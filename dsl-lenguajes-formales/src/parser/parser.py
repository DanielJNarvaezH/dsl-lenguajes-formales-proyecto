"""Analizador sintáctico descendente recursivo de Cafetal (PAR-2 y PAR-3).

Hay una función por cada no terminal de la gramática final de la Fase 2
(docs/fase2/factorizacion.md, sección 6). Cada función:

1. consulta la tabla LL(1) (tabla_ll1.csv, GIC-6) con su no terminal y el
   token actual para saber qué regla aplicar;
2. crea su nodo con Nodo.no_terminal(simbolo, regla) (PAR-1, sección 5.1 de
   docs/fase3/arbol.md);
3. agrega un hijo por cada símbolo del lado derecho de esa regla, en orden:
   los terminales con emparejar(TIPO), los no terminales llamando a su
   función y la cadena vacía con Nodo.vacio();
4. devuelve el nodo.

Encima de cada función está, como comentario, la regla BNF que implementa.

La tabla decide qué regla se aplica; el código de cada función solo escribe el
lado derecho de las reglas de su no terminal. Si la tabla no tiene regla para
el par (no terminal, token actual), o el token no es el terminal que la regla
pide, hay un error sintáctico.

Este archivo tiene tres partes:

* base común (PAR-2): TablaLL1, ErrorSintactico y la clase Parser con el
  token actual, predecir, emparejar y el manejo de errores;
* funciones de expresiones (PAR-2);
* funciones de programa y sentencias (PAR-3).
"""

import csv
from pathlib import Path

from ..lexer.tokens import EOF
from .arbol import Nodo

# Ruta de la tabla: junto a este archivo, sin rutas fijas del equipo.
RUTA_TABLA_LL1 = Path(__file__).with_name("tabla_ll1.csv")


class ErrorTablaLL1(Exception):
    """La tabla LL(1) no tiene el formato esperado."""


class ErrorSintactico(Exception):
    """El token actual no puede seguir en ese punto del programa.

    * encontrado: el Token donde se detectó el error;
    * esperados: los terminales que sí podían aparecer, en el orden de la tabla;
    * contexto: el no terminal que se estaba analizando, o el terminal que se
      intentaba emparejar.
    """

    def __init__(self, encontrado, esperados, contexto):
        self.encontrado = encontrado
        self.esperados = list(esperados)
        self.contexto = contexto
        self.linea = encontrado.linea
        self.columna = encontrado.columna
        super().__init__(self.mensaje())

    def mensaje(self):
        if self.encontrado.tipo == EOF:
            hallado = "el fin del archivo"
        else:
            hallado = f"{self.encontrado.lexema!r} ({self.encontrado.tipo})"
        return (f"Error sintáctico en la línea {self.linea}, columna {self.columna}: "
                f"se esperaba {_enumerar(self.esperados)} y se encontró {hallado}.")


def _enumerar(nombres):
    """A, B o C. EOF se escribe como «el fin del archivo»."""
    nombres = ["el fin del archivo" if n == EOF else n for n in nombres]
    if len(nombres) == 1:
        return nombres[0]
    return ", ".join(nombres[:-1]) + " o " + nombres[-1]


class TablaLL1:
    """Tabla de análisis predictivo de GIC-6: M[no terminal, terminal] = etiqueta de la regla."""

    def __init__(self, ruta=RUTA_TABLA_LL1):
        self.ruta = Path(ruta)
        self.celdas = {}        # (no terminal, terminal) -> regla
        self.terminales = []    # en el orden de las columnas
        self.no_terminales = []
        self._cargar()

    def _cargar(self):
        with open(self.ruta, encoding="utf-8", newline="") as archivo:
            filas = list(csv.reader(archivo))
        if len(filas) < 2 or filas[0][0] != "no_terminal":
            raise ErrorTablaLL1(f"{self.ruta}: la cabecera debe empezar con 'no_terminal'")
        self.terminales = filas[0][1:]
        for fila in filas[1:]:
            if len(fila) != len(filas[0]):
                raise ErrorTablaLL1(f"{self.ruta}: la fila de {fila[0]!r} no tiene {len(filas[0])} columnas")
            no_terminal = fila[0]
            self.no_terminales.append(no_terminal)
            for terminal, regla in zip(self.terminales, fila[1:]):
                if regla:
                    self.celdas[(no_terminal, terminal)] = regla

    def regla(self, no_terminal, terminal):
        """M[no terminal, terminal], o None si la celda está vacía (error)."""
        return self.celdas.get((no_terminal, terminal))

    def esperados(self, no_terminal):
        """Terminales con celda no vacía en la fila del no terminal, en orden de columnas."""
        return [t for t in self.terminales if (no_terminal, t) in self.celdas]


class Parser:
    """Analizador sintáctico descendente recursivo, dirigido por la tabla LL(1).

    Recibe la lista de tokens del analizador léxico (contrato de PAR-1) y
    construye el árbol de derivación.
    """

    def __init__(self, tokens, tabla=None):
        self.tokens = list(tokens)
        self.tabla = tabla if tabla is not None else TablaLL1()
        self.posicion = 0

    # ------------------------------------------------------------------
    # Base común (PAR-2)
    # ------------------------------------------------------------------

    @property
    def actual(self):
        """Token actual (el siguiente sin consumir). El último siempre es EOF."""
        return self.tokens[self.posicion]

    def predecir(self, no_terminal):
        """Regla que la tabla LL(1) indica para el no terminal y el token actual."""
        regla = self.tabla.regla(no_terminal, self.actual.tipo)
        if regla is None:
            self._error(self.tabla.esperados(no_terminal), no_terminal)
        return regla

    def emparejar(self, tipo):
        """Consume el token actual si es del terminal que pide la regla y devuelve su hoja."""
        token = self.actual
        if token.tipo != tipo:
            self._error([tipo], tipo)
        self.posicion += 1
        return Nodo.terminal(token)

    def verificar_fin(self):
        """Después del símbolo inicial solo puede quedar EOF."""
        if self.actual.tipo != EOF:
            self._error([EOF], EOF)

    def _error(self, esperados, contexto):
        """Error sintáctico en el token actual.

        En PAR-2 el análisis se detiene en el primer error. PAR-4 reemplaza
        este método por la recuperación en modo pánico con SIGUIENTE.
        """
        raise ErrorSintactico(self.actual, esperados, contexto)

    def analizar(self):
        """Analiza un programa completo: <programa> seguido de EOF (requiere PAR-3)."""
        raiz = self.programa()
        self.verificar_fin()
        return raiz

    def analizar_fragmento(self, no_terminal, *seguido_de):
        """Analiza solo un no terminal, seguido de los terminales indicados y de EOF.

        Sirve para probar partes de la gramática. Por ejemplo, una expresión
        siempre va seguida de PAR_CIERRA o PUNTO_COMA (SIGUIENTE(<expresion>)),
        así que se prueba con analizar_fragmento("<expresion>", "PUNTO_COMA")
        sobre el texto "expresión ;".
        """
        raiz = getattr(self, no_terminal.strip("<>"))()
        for tipo in seguido_de:
            self.emparejar(tipo)
        self.verificar_fin()
        return raiz

    # ------------------------------------------------------------------
    # Expresiones (PAR-2)
    # Gramática sin recursividad por la izquierda (GIC-4) y factorizada (GIC-5).
    # ------------------------------------------------------------------

    # R3   <expresion> ::= <conjuncion> <expresion_prima>
    def expresion(self):
        """R3: <expresion> ::= <conjuncion> <expresion_prima>"""
        nodo = Nodo.no_terminal("<expresion>", self.predecir("<expresion>"))
        nodo.agregar(self.conjuncion())
        nodo.agregar(self.expresion_prima())
        return nodo

    # R4   <expresion_prima> ::= O <conjuncion> <expresion_prima>
    # R5   <expresion_prima> ::= ε
    def expresion_prima(self):
        """R4: <expresion_prima> ::= O <conjuncion> <expresion_prima> | R5: ε"""
        regla = self.predecir("<expresion_prima>")
        nodo = Nodo.no_terminal("<expresion_prima>", regla)
        if regla == "R4":
            nodo.agregar(self.emparejar("O"))
            nodo.agregar(self.conjuncion())
            nodo.agregar(self.expresion_prima())
        else:                                   # R5
            nodo.agregar(Nodo.vacio())
        return nodo

    # R6   <conjuncion> ::= <negacion> <conjuncion_prima>
    def conjuncion(self):
        """R6: <conjuncion> ::= <negacion> <conjuncion_prima>"""
        nodo = Nodo.no_terminal("<conjuncion>", self.predecir("<conjuncion>"))
        nodo.agregar(self.negacion())
        nodo.agregar(self.conjuncion_prima())
        return nodo

    # R7   <conjuncion_prima> ::= Y <negacion> <conjuncion_prima>
    # R8   <conjuncion_prima> ::= ε
    def conjuncion_prima(self):
        """R7: <conjuncion_prima> ::= Y <negacion> <conjuncion_prima> | R8: ε"""
        regla = self.predecir("<conjuncion_prima>")
        nodo = Nodo.no_terminal("<conjuncion_prima>", regla)
        if regla == "R7":
            nodo.agregar(self.emparejar("Y"))
            nodo.agregar(self.negacion())
            nodo.agregar(self.conjuncion_prima())
        else:                                   # R8
            nodo.agregar(Nodo.vacio())
        return nodo

    # E5   <negacion> ::= NO <negacion>
    # E6   <negacion> ::= <comparacion>
    def negacion(self):
        """E5: <negacion> ::= NO <negacion> | E6: <comparacion>"""
        regla = self.predecir("<negacion>")
        nodo = Nodo.no_terminal("<negacion>", regla)
        if regla == "E5":
            nodo.agregar(self.emparejar("NO"))
            nodo.agregar(self.negacion())
        else:                                   # E6
            nodo.agregar(self.comparacion())
        return nodo

    # F1   <comparacion> ::= <suma> <comparacion_prima>
    def comparacion(self):
        """F1: <comparacion> ::= <suma> <comparacion_prima>"""
        nodo = Nodo.no_terminal("<comparacion>", self.predecir("<comparacion>"))
        nodo.agregar(self.suma())
        nodo.agregar(self.comparacion_prima())
        return nodo

    # F2   <comparacion_prima> ::= <op_rel> <suma>
    # F3   <comparacion_prima> ::= ε
    def comparacion_prima(self):
        """F2: <comparacion_prima> ::= <op_rel> <suma> | F3: ε"""
        regla = self.predecir("<comparacion_prima>")
        nodo = Nodo.no_terminal("<comparacion_prima>", regla)
        if regla == "F2":
            nodo.agregar(self.op_rel())
            nodo.agregar(self.suma())
        else:                                   # F3
            nodo.agregar(Nodo.vacio())
        return nodo

    # E9   <op_rel> ::= MENOR          E12  <op_rel> ::= MAYOR_IGUAL
    # E10  <op_rel> ::= MAYOR          E13  <op_rel> ::= IGUAL
    # E11  <op_rel> ::= MENOR_IGUAL    E14  <op_rel> ::= DIFERENTE
    TERMINAL_OP_REL = {"E9": "MENOR", "E10": "MAYOR", "E11": "MENOR_IGUAL",
                       "E12": "MAYOR_IGUAL", "E13": "IGUAL", "E14": "DIFERENTE"}

    def op_rel(self):
        """E9: <op_rel> ::= MENOR | E10: MAYOR | E11: MENOR_IGUAL | E12: MAYOR_IGUAL | E13: IGUAL | E14: DIFERENTE"""
        regla = self.predecir("<op_rel>")
        nodo = Nodo.no_terminal("<op_rel>", regla)
        nodo.agregar(self.emparejar(self.TERMINAL_OP_REL[regla]))
        return nodo

    # R9   <suma> ::= <termino> <suma_prima>
    def suma(self):
        """R9: <suma> ::= <termino> <suma_prima>"""
        nodo = Nodo.no_terminal("<suma>", self.predecir("<suma>"))
        nodo.agregar(self.termino())
        nodo.agregar(self.suma_prima())
        return nodo

    # R10  <suma_prima> ::= SUMA <termino> <suma_prima>
    # R11  <suma_prima> ::= RESTA <termino> <suma_prima>
    # R12  <suma_prima> ::= ε
    OPERADOR_SUMA = {"R10": "SUMA", "R11": "RESTA"}

    def suma_prima(self):
        """R10: <suma_prima> ::= SUMA <termino> <suma_prima> | R11: RESTA <termino> <suma_prima> | R12: ε"""
        regla = self.predecir("<suma_prima>")
        nodo = Nodo.no_terminal("<suma_prima>", regla)
        if regla in self.OPERADOR_SUMA:         # R10 o R11
            nodo.agregar(self.emparejar(self.OPERADOR_SUMA[regla]))
            nodo.agregar(self.termino())
            nodo.agregar(self.suma_prima())
        else:                                   # R12
            nodo.agregar(Nodo.vacio())
        return nodo

    # R13  <termino> ::= <factor> <termino_prima>
    def termino(self):
        """R13: <termino> ::= <factor> <termino_prima>"""
        nodo = Nodo.no_terminal("<termino>", self.predecir("<termino>"))
        nodo.agregar(self.factor())
        nodo.agregar(self.termino_prima())
        return nodo

    # R14  <termino_prima> ::= MULT <factor> <termino_prima>
    # R15  <termino_prima> ::= DIV <factor> <termino_prima>
    # R16  <termino_prima> ::= ε
    OPERADOR_TERMINO = {"R14": "MULT", "R15": "DIV"}

    def termino_prima(self):
        """R14: <termino_prima> ::= MULT <factor> <termino_prima> | R15: DIV <factor> <termino_prima> | R16: ε"""
        regla = self.predecir("<termino_prima>")
        nodo = Nodo.no_terminal("<termino_prima>", regla)
        if regla in self.OPERADOR_TERMINO:      # R14 o R15
            nodo.agregar(self.emparejar(self.OPERADOR_TERMINO[regla]))
            nodo.agregar(self.factor())
            nodo.agregar(self.termino_prima())
        else:                                   # R16
            nodo.agregar(Nodo.vacio())
        return nodo

    # E21  <factor> ::= PAR_ABRE <expresion> PAR_CIERRA
    # E22  <factor> ::= ID
    # E23  <factor> ::= ENTERO
    # E24  <factor> ::= DECIMAL
    OPERANDO = {"E22": "ID", "E23": "ENTERO", "E24": "DECIMAL"}

    def factor(self):
        """E21: <factor> ::= PAR_ABRE <expresion> PAR_CIERRA | E22: ID | E23: ENTERO | E24: DECIMAL"""
        regla = self.predecir("<factor>")
        nodo = Nodo.no_terminal("<factor>", regla)
        if regla == "E21":
            nodo.agregar(self.emparejar("PAR_ABRE"))
            nodo.agregar(self.expresion())
            nodo.agregar(self.emparejar("PAR_CIERRA"))
        else:                                   # E22, E23 o E24
            nodo.agregar(self.emparejar(self.OPERANDO[regla]))
        return nodo

    # ------------------------------------------------------------------
    # Programa y sentencias (PAR-3)
    # ------------------------------------------------------------------
