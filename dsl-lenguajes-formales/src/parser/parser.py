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

Errores sintácticos (PAR-4): cada error se registra con el token esperado y el
encontrado, su línea y su columna, y el análisis continúa en modo pánico:

* en predecir(A), se descartan tokens hasta uno con el que A pueda empezar o
  uno de SIGUIENTE(A) (más las palabras reservadas de anclaje). Si A puede
  empezar, se deriva normalmente; si no, A se omite y su función devuelve un
  nodo de error, para que quien la llamó siga con ese token;
* en emparejar(T), si el token sobra (el siguiente sí es T) se descarta; si
  no, se supone que T faltaba y se sigue como si estuviera.

Así se listan varios errores en una sola pasada. Con detener_en_error=True el
primer error detiene el análisis, como en PAR-2 y PAR-3.

Este archivo tiene tres partes:

* base común (PAR-2): TablaLL1, ErrorSintactico y la clase Parser con el
  token actual, predecir, emparejar y el manejo de errores (PAR-4);
* funciones de expresiones (PAR-2);
* funciones de programa y sentencias (PAR-3).
"""

import csv
from pathlib import Path

from ..lexer.lexer import Token
from ..lexer.tokens import EOF
from .arbol import Nodo

# Rutas de los datos de GIC-6: junto a este archivo, sin rutas fijas del equipo.
RUTA_TABLA_LL1 = Path(__file__).with_name("tabla_ll1.csv")
RUTA_SIGUIENTE = Path(__file__).with_name("siguiente.csv")

# Etiqueta del nodo de un no terminal que no se pudo derivar (PAR-4).
REGLA_ERROR = "ERROR"

# Anclaje del modo pánico (PAR-4): además de SIGUIENTE(A), la búsqueda de un
# token de sincronización se detiene en las palabras reservadas que empiezan
# una sentencia (DATO, SI, MIENTRAS, MOSTRAR) o terminan un bloque (SINO, FIN),
# aunque no estén en SIGUIENTE(A). Es la recomendación de Aho et al. (2006,
# sección 4.4.5) de agregar al conjunto de sincronización de una construcción
# los símbolos que empiezan las construcciones de nivel superior: si el error
# está dentro de una expresión, el análisis se retoma en la sentencia siguiente
# en lugar de descartarla. Siempre hay una <sentencias> abierta que puede usar
# esos tokens. ID no se incluye porque también aparece dentro de las
# expresiones, ni ENTONCES y HACER, porque solo los usa la cabecera de un
# bloque y fuera de ella dejarían al parser detenido en el mismo token.
ANCLAJE = frozenset({"DATO", "SI", "MIENTRAS", "MOSTRAR", "SINO", "FIN"})


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


def cargar_siguiente(ruta=RUTA_SIGUIENTE):
    """Conjuntos SIGUIENTE de GIC-6 (sección 6.4): {no terminal: frozenset de terminales}."""
    with open(ruta, encoding="utf-8", newline="") as archivo:
        filas = list(csv.reader(archivo))
    if not filas or filas[0] != ["no_terminal", "siguiente"]:
        raise ErrorTablaLL1(f"{ruta}: la cabecera debe ser 'no_terminal,siguiente'")
    return {no_terminal: frozenset(terminales.split()) for no_terminal, terminales in filas[1:]}


class Parser:
    """Analizador sintáctico descendente recursivo, dirigido por la tabla LL(1).

    Recibe la lista de tokens del analizador léxico (contrato de PAR-1) y
    construye el árbol de derivación.
    """

    def __init__(self, tokens, tabla=None, siguiente=None, detener_en_error=False):
        self.tokens = list(tokens)
        self.tabla = tabla if tabla is not None else TablaLL1()
        self.siguiente = siguiente if siguiente is not None else cargar_siguiente()
        self.detener_en_error = detener_en_error
        self.posicion = 0
        self.errores = []                 # ErrorSintactico, en el orden del texto
        self._recuperando = False         # True desde un error hasta el siguiente emparejamiento

    # ------------------------------------------------------------------
    # Base común (PAR-2)
    # ------------------------------------------------------------------

    @property
    def actual(self):
        """Token actual (el siguiente sin consumir). El último siempre es EOF."""
        return self.tokens[self.posicion]

    def predecir(self, no_terminal):
        """Regla que la tabla LL(1) indica para el no terminal y el token actual.

        Si la celda está vacía, registra el error y se sincroniza (PAR-4).
        Devuelve None si el no terminal debe omitirse: en ese caso su función
        devuelve self.omitido(no_terminal).
        """
        regla = self.tabla.regla(no_terminal, self.actual.tipo)
        if regla is None:
            self._error(self.tabla.esperados(no_terminal), no_terminal)
            regla = self._sincronizar(no_terminal)
        return regla

    def _sincronizar(self, no_terminal):
        """Modo pánico: descarta tokens hasta uno de sincronización.

        Se detiene en un token con el que el no terminal puede empezar (la
        tabla tiene regla), en uno de SIGUIENTE(no terminal), en una palabra de ANCLAJE
        o en EOF. Devuelve la regla si el no terminal puede continuar, o None
        si hay que omitirlo.
        """
        parada = self.siguiente[no_terminal] | ANCLAJE
        while (self.actual.tipo != EOF
               and self.tabla.regla(no_terminal, self.actual.tipo) is None
               and self.actual.tipo not in parada):
            self.posicion += 1
        return self.tabla.regla(no_terminal, self.actual.tipo)

    def omitido(self, no_terminal):
        """Nodo de un no terminal que no se pudo derivar: regla ERROR y sin hijos."""
        return Nodo.no_terminal(no_terminal, REGLA_ERROR)

    def emparejar(self, tipo):
        """Consume el token actual si es del terminal que pide la regla y devuelve su hoja.

        Si no lo es, registra el error y se recupera (PAR-4): si el token
        actual sobra porque el siguiente sí es el esperado, lo descarta y
        empareja el siguiente; si no, supone que el terminal faltaba y sigue sin
        consumir nada, con una hoja de lexema vacío en lugar del token.
        """
        token = self.actual
        if token.tipo == tipo:
            self.posicion += 1
            self._recuperando = False
            return Nodo.terminal(token)
        self._error([tipo], tipo)
        if token.tipo != EOF and self.tokens[self.posicion + 1].tipo == tipo:
            self.posicion += 2                    # token sobrante: se descarta
            self._recuperando = False
            return Nodo.terminal(self.tokens[self.posicion - 1])
        return Nodo.terminal(Token(tipo, "", token.linea, token.columna))   # token faltante

    def verificar_fin(self):
        """Después del símbolo inicial solo puede quedar EOF. Lo que sobra se ignora."""
        if self.actual.tipo != EOF:
            self._error([EOF], EOF)
            self.posicion = len(self.tokens) - 1

    def _error(self, esperados, contexto):
        """Registra un error sintáctico en el token actual (PAR-4).

        Después de un error no se registra otro hasta que se empareje
        correctamente algún token: mientras el parser se recupera, las funciones
        que encuentran tokens inesperados lo hacen por el mismo error, y esos
        avisos en cascada no aportan información (Aho et al., 2006, sección
        4.4.5). Con detener_en_error=True lanza el error, como en PAR-2 y PAR-3.
        """
        error = ErrorSintactico(self.actual, esperados, contexto)
        if self.detener_en_error:
            raise error
        if not self._recuperando:
            self.errores.append(error)
            self._recuperando = True

    def analizar(self):
        """Analiza un programa completo: <programa> seguido de EOF.

        Devuelve el árbol. Si hubo errores (self.errores no está vacío), el
        árbol está incompleto: tiene nodos ERROR y hojas de lexema vacío.
        """
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
        regla = self.predecir("<expresion>")
        if regla is None:                       # PAR-4: no se pudo derivar
            return self.omitido("<expresion>")
        nodo = Nodo.no_terminal("<expresion>", regla)
        nodo.agregar(self.conjuncion())
        nodo.agregar(self.expresion_prima())
        return nodo

    # R4   <expresion_prima> ::= O <conjuncion> <expresion_prima>
    # R5   <expresion_prima> ::= ε
    def expresion_prima(self):
        """R4: <expresion_prima> ::= O <conjuncion> <expresion_prima> | R5: ε"""
        regla = self.predecir("<expresion_prima>")
        if regla is None:                       # PAR-4: no se pudo derivar
            return self.omitido("<expresion_prima>")
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
        regla = self.predecir("<conjuncion>")
        if regla is None:                       # PAR-4: no se pudo derivar
            return self.omitido("<conjuncion>")
        nodo = Nodo.no_terminal("<conjuncion>", regla)
        nodo.agregar(self.negacion())
        nodo.agregar(self.conjuncion_prima())
        return nodo

    # R7   <conjuncion_prima> ::= Y <negacion> <conjuncion_prima>
    # R8   <conjuncion_prima> ::= ε
    def conjuncion_prima(self):
        """R7: <conjuncion_prima> ::= Y <negacion> <conjuncion_prima> | R8: ε"""
        regla = self.predecir("<conjuncion_prima>")
        if regla is None:                       # PAR-4: no se pudo derivar
            return self.omitido("<conjuncion_prima>")
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
        if regla is None:                       # PAR-4: no se pudo derivar
            return self.omitido("<negacion>")
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
        regla = self.predecir("<comparacion>")
        if regla is None:                       # PAR-4: no se pudo derivar
            return self.omitido("<comparacion>")
        nodo = Nodo.no_terminal("<comparacion>", regla)
        nodo.agregar(self.suma())
        nodo.agregar(self.comparacion_prima())
        return nodo

    # F2   <comparacion_prima> ::= <op_rel> <suma>
    # F3   <comparacion_prima> ::= ε
    def comparacion_prima(self):
        """F2: <comparacion_prima> ::= <op_rel> <suma> | F3: ε"""
        regla = self.predecir("<comparacion_prima>")
        if regla is None:                       # PAR-4: no se pudo derivar
            return self.omitido("<comparacion_prima>")
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
        if regla is None:                       # PAR-4: no se pudo derivar
            return self.omitido("<op_rel>")
        nodo = Nodo.no_terminal("<op_rel>", regla)
        nodo.agregar(self.emparejar(self.TERMINAL_OP_REL[regla]))
        return nodo

    # R9   <suma> ::= <termino> <suma_prima>
    def suma(self):
        """R9: <suma> ::= <termino> <suma_prima>"""
        regla = self.predecir("<suma>")
        if regla is None:                       # PAR-4: no se pudo derivar
            return self.omitido("<suma>")
        nodo = Nodo.no_terminal("<suma>", regla)
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
        if regla is None:                       # PAR-4: no se pudo derivar
            return self.omitido("<suma_prima>")
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
        regla = self.predecir("<termino>")
        if regla is None:                       # PAR-4: no se pudo derivar
            return self.omitido("<termino>")
        nodo = Nodo.no_terminal("<termino>", regla)
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
        if regla is None:                       # PAR-4: no se pudo derivar
            return self.omitido("<termino_prima>")
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
        if regla is None:                       # PAR-4: no se pudo derivar
            return self.omitido("<factor>")
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
    # Cafetal no tiene instrucción de lectura: la única sentencia de
    # entrada/salida es mostrar (GIC-2, sección 1).

    # P1   <programa> ::= INICIO <sentencias> FIN
    def programa(self):
        """P1: <programa> ::= INICIO <sentencias> FIN"""
        regla = self.predecir("<programa>")
        if regla is None:                       # PAR-4: no se pudo derivar
            return self.omitido("<programa>")
        nodo = Nodo.no_terminal("<programa>", regla)
        nodo.agregar(self.emparejar("INICIO"))
        nodo.agregar(self.sentencias())
        nodo.agregar(self.emparejar("FIN"))
        return nodo

    # R1   <sentencias> ::= <sentencia> <sentencias>
    # R2   <sentencias> ::= ε
    def sentencias(self):
        """R1: <sentencias> ::= <sentencia> <sentencias> | R2: ε"""
        regla = self.predecir("<sentencias>")
        if regla is None:                       # PAR-4: no se pudo derivar
            return self.omitido("<sentencias>")
        nodo = Nodo.no_terminal("<sentencias>", regla)
        if regla == "R1":
            nodo.agregar(self.sentencia())
            nodo.agregar(self.sentencias())
        else:                                   # R2: llegó FIN o SINO
            nodo.agregar(Nodo.vacio())
        return nodo

    # P4   <sentencia> ::= <declaracion>
    # P5   <sentencia> ::= <asignacion>
    # P6   <sentencia> ::= <salida>
    # P7   <sentencia> ::= <condicional>
    # P8   <sentencia> ::= <ciclo>
    def sentencia(self):
        """P4: <sentencia> ::= <declaracion> | P5: <asignacion> | P6: <salida> | P7: <condicional> | P8: <ciclo>"""
        regla = self.predecir("<sentencia>")
        if regla is None:                       # PAR-4: no se pudo derivar
            return self.omitido("<sentencia>")
        nodo = Nodo.no_terminal("<sentencia>", regla)
        if regla == "P4":
            nodo.agregar(self.declaracion())
        elif regla == "P5":
            nodo.agregar(self.asignacion())
        elif regla == "P6":
            nodo.agregar(self.salida())
        elif regla == "P7":
            nodo.agregar(self.condicional())
        else:                                   # P8
            nodo.agregar(self.ciclo())
        return nodo

    # D1   <declaracion> ::= DATO ID ASIGNACION <expresion> PUNTO_COMA
    def declaracion(self):
        """D1: <declaracion> ::= DATO ID ASIGNACION <expresion> PUNTO_COMA"""
        regla = self.predecir("<declaracion>")
        if regla is None:                       # PAR-4: no se pudo derivar
            return self.omitido("<declaracion>")
        nodo = Nodo.no_terminal("<declaracion>", regla)
        nodo.agregar(self.emparejar("DATO"))
        nodo.agregar(self.emparejar("ID"))
        nodo.agregar(self.emparejar("ASIGNACION"))
        nodo.agregar(self.expresion())
        nodo.agregar(self.emparejar("PUNTO_COMA"))
        return nodo

    # A1   <asignacion> ::= ID ASIGNACION <expresion> PUNTO_COMA
    def asignacion(self):
        """A1: <asignacion> ::= ID ASIGNACION <expresion> PUNTO_COMA"""
        regla = self.predecir("<asignacion>")
        if regla is None:                       # PAR-4: no se pudo derivar
            return self.omitido("<asignacion>")
        nodo = Nodo.no_terminal("<asignacion>", regla)
        nodo.agregar(self.emparejar("ID"))
        nodo.agregar(self.emparejar("ASIGNACION"))
        nodo.agregar(self.expresion())
        nodo.agregar(self.emparejar("PUNTO_COMA"))
        return nodo

    # M1   <salida> ::= MOSTRAR PAR_ABRE <argumento> PAR_CIERRA PUNTO_COMA
    def salida(self):
        """M1: <salida> ::= MOSTRAR PAR_ABRE <argumento> PAR_CIERRA PUNTO_COMA"""
        regla = self.predecir("<salida>")
        if regla is None:                       # PAR-4: no se pudo derivar
            return self.omitido("<salida>")
        nodo = Nodo.no_terminal("<salida>", regla)
        nodo.agregar(self.emparejar("MOSTRAR"))
        nodo.agregar(self.emparejar("PAR_ABRE"))
        nodo.agregar(self.argumento())
        nodo.agregar(self.emparejar("PAR_CIERRA"))
        nodo.agregar(self.emparejar("PUNTO_COMA"))
        return nodo

    # M2   <argumento> ::= <expresion>
    # M3   <argumento> ::= CADENA
    def argumento(self):
        """M2: <argumento> ::= <expresion> | M3: CADENA"""
        regla = self.predecir("<argumento>")
        if regla is None:                       # PAR-4: no se pudo derivar
            return self.omitido("<argumento>")
        nodo = Nodo.no_terminal("<argumento>", regla)
        if regla == "M3":
            nodo.agregar(self.emparejar("CADENA"))
        else:                                   # M2
            nodo.agregar(self.expresion())
        return nodo

    # F4   <condicional> ::= SI PAR_ABRE <expresion> PAR_CIERRA ENTONCES <sentencias> <condicional_prima>
    def condicional(self):
        """F4: <condicional> ::= SI PAR_ABRE <expresion> PAR_CIERRA ENTONCES <sentencias> <condicional_prima>"""
        regla = self.predecir("<condicional>")
        if regla is None:                       # PAR-4: no se pudo derivar
            return self.omitido("<condicional>")
        nodo = Nodo.no_terminal("<condicional>", regla)
        nodo.agregar(self.emparejar("SI"))
        nodo.agregar(self.emparejar("PAR_ABRE"))
        nodo.agregar(self.expresion())
        nodo.agregar(self.emparejar("PAR_CIERRA"))
        nodo.agregar(self.emparejar("ENTONCES"))
        nodo.agregar(self.sentencias())
        nodo.agregar(self.condicional_prima())
        return nodo

    # F5   <condicional_prima> ::= FIN
    # F6   <condicional_prima> ::= SINO <sentencias> FIN
    def condicional_prima(self):
        """F5: <condicional_prima> ::= FIN | F6: SINO <sentencias> FIN"""
        regla = self.predecir("<condicional_prima>")
        if regla is None:                       # PAR-4: no se pudo derivar
            return self.omitido("<condicional_prima>")
        nodo = Nodo.no_terminal("<condicional_prima>", regla)
        if regla == "F6":
            nodo.agregar(self.emparejar("SINO"))
            nodo.agregar(self.sentencias())
        nodo.agregar(self.emparejar("FIN"))     # F5 y F6 terminan con FIN
        return nodo

    # L1   <ciclo> ::= MIENTRAS PAR_ABRE <expresion> PAR_CIERRA HACER <sentencias> FIN
    def ciclo(self):
        """L1: <ciclo> ::= MIENTRAS PAR_ABRE <expresion> PAR_CIERRA HACER <sentencias> FIN"""
        regla = self.predecir("<ciclo>")
        if regla is None:                       # PAR-4: no se pudo derivar
            return self.omitido("<ciclo>")
        nodo = Nodo.no_terminal("<ciclo>", regla)
        nodo.agregar(self.emparejar("MIENTRAS"))
        nodo.agregar(self.emparejar("PAR_ABRE"))
        nodo.agregar(self.expresion())
        nodo.agregar(self.emparejar("PAR_CIERRA"))
        nodo.agregar(self.emparejar("HACER"))
        nodo.agregar(self.sentencias())
        nodo.agregar(self.emparejar("FIN"))
        return nodo
