"""Pruebas del manejo de errores sintácticos en modo pánico (PAR-4).

El parser registra cada error con el token esperado y el encontrado, su línea
y su columna, se sincroniza con el conjunto SIGUIENTE y continúa, para listar
varios errores en una sola pasada.

Ejecutar desde la raíz del repositorio:

    python -m unittest tests.test_errores_sintacticos -v
"""

import csv
import itertools
import random
import unittest
from pathlib import Path

from src.lexer.lexer import AnalizadorLexico, Token
from src.parser.parser import (ANCLAJE, REGLA_ERROR, ErrorSintactico, Parser, TablaLL1,
                               cargar_siguiente)
from tests import test_parser_expresiones as par2
from tests import test_parser_sentencias as par3

RAIZ = Path(__file__).resolve().parent.parent
EJEMPLOS = RAIZ / "ejemplos"
ERRORES = RAIZ / "tests" / "errores"


def analizar(texto):
    """Analiza con recuperación; devuelve (árbol, errores)."""
    parser = Parser(AnalizadorLexico().analizar(texto))
    return parser.analizar(), parser.errores


def resumen(errores):
    """(tipo encontrado, línea, columna) de cada error, en orden."""
    return [(e.encontrado.tipo, e.linea, e.columna) for e in errores]


def siguiente_calculado():
    """SIGUIENTE de cada no terminal, calculado desde la gramática de las pruebas.

    Algoritmo de punto fijo de GIC-6 (sección 6), independiente de siguiente.csv.
    """
    gramatica = par3.GRAMATICA
    tabla = TablaLL1()
    lado_izquierdo = {regla: nt for (nt, _), regla in tabla.celdas.items()}
    no_terminales = set(lado_izquierdo.values())
    anulables, primero = set(), {nt: set() for nt in no_terminales}
    cambio = True
    while cambio:
        cambio = False
        for regla, lado in gramatica.items():
            a = lado_izquierdo[regla]
            for simbolo in lado:
                nuevos = primero[simbolo] if simbolo in no_terminales else {simbolo}
                if not nuevos <= primero[a]:
                    primero[a] |= nuevos
                    cambio = True
                if simbolo not in anulables:
                    break
            else:
                if a not in anulables:
                    anulables.add(a)
                    cambio = True
    siguiente = {nt: set() for nt in no_terminales}
    siguiente["<programa>"].add("EOF")
    cambio = True
    while cambio:
        cambio = False
        for regla, lado in gramatica.items():
            a = lado_izquierdo[regla]
            for i, simbolo in enumerate(lado):
                if simbolo not in no_terminales:
                    continue
                nuevos, resto_anulable = set(), True
                for despues in lado[i + 1:]:
                    nuevos |= primero[despues] if despues in no_terminales else {despues}
                    if despues not in anulables:
                        resto_anulable = False
                        break
                if resto_anulable:
                    nuevos |= siguiente[a]
                if not nuevos <= siguiente[simbolo]:
                    siguiente[simbolo] |= nuevos
                    cambio = True
    return siguiente


class PruebaSiguiente(unittest.TestCase):

    def test_siguiente_csv_coincide_con_gic6(self):
        cargado = cargar_siguiente()
        calculado = siguiente_calculado()
        self.assertEqual(set(cargado), set(TablaLL1().no_terminales))
        for no_terminal, conjunto in calculado.items():
            with self.subTest(no_terminal=no_terminal):
                self.assertEqual(set(cargado[no_terminal]), conjunto)

    def test_anclaje(self):
        # Palabras que empiezan una sentencia o terminan un bloque: todas están
        # en la fila de <sentencias>, así que siempre hay quien las use.
        self.assertTrue(ANCLAJE <= set(TablaLL1().esperados("<sentencias>")))
        self.assertNotIn("ID", ANCLAJE)


class PruebaRecuperacion(unittest.TestCase):
    """Cada caso tiene un solo error real y se reporta un solo error."""

    CASOS = {
        # Falta el ; antes de fin: se detecta en el fin (sincroniza con FIN)
        "inicio x = 1 fin": [("FIN", 1, 14)],
        # Palabra reservada como variable: falta ID, se supone insertado y SI sobra
        "inicio dato si = 3; fin": [("SI", 1, 13)],
        # sino sin si: sobra un token, se descarta
        "inicio sino fin": [("SINO", 1, 8)],
        # Palabra del bloque equivocada: falta HACER, el cuerpo se analiza igual
        "inicio mientras (a) entonces x = 1; fin fin": [("ENTONCES", 1, 21)],
        # Falta el ) del condicional
        "inicio si (a entonces x = 1; fin fin": [("ENTONCES", 1, 14)],
        # Relacionales encadenados: se descarta hasta el ;
        "inicio x = a < b < c; z = 2; fin": [("MENOR", 1, 18)],
        # Falta un operando
        "inicio x = (a + ; z = 1; fin": [("PUNTO_COMA", 1, 17)],
        # Operando de más
        "inicio x = a b c; fin": [("ID", 1, 14)],
        # Doble =
        "inicio x = = 2; fin": [("ASIGNACION", 1, 12)],
        # Falta el =
        "inicio x 1; fin": [("ENTERO", 1, 10)],
        # Cadena en una expresión: CADENA solo puede ser todo el argumento
        'inicio mostrar("a" + 1); fin': [("SUMA", 1, 20)],
        # Sobra texto después del programa
        "inicio fin fin": [("FIN", 1, 12)],
        # Falta el fin del programa
        "inicio x = 1;": [("EOF", 1, 14)],
        # Archivo vacío
        "": [("EOF", 1, 1)],
    }

    def test_un_error_por_caso(self):
        for texto, esperado in self.CASOS.items():
            with self.subTest(programa=texto):
                _, errores = analizar(texto)
                self.assertEqual(resumen(errores), esperado)

    def test_varios_errores_en_un_programa(self):
        _, errores = analizar("inicio\n  x = 1\n  z = 2;\n  mostrar(;\n  dato = 4;\nfin")
        self.assertEqual(resumen(errores), [("ID", 3, 3), ("PUNTO_COMA", 4, 11),
                                            ("ASIGNACION", 5, 8)])

    def test_dos_errores_seguidos_en_la_cabecera(self):
        # Sin paréntesis: falta el ( y, más adelante, el ).
        _, errores = analizar("inicio si a > 1 entonces x = 1; fin fin")
        self.assertEqual(resumen(errores), [("ID", 1, 11), ("ENTONCES", 1, 17)])
        self.assertEqual([e.esperados for e in errores][0], ["PAR_ABRE"])

    def test_esperado_frente_a_encontrado(self):
        _, errores = analizar("inicio\n  mientras (a) entonces fin\nfin")
        error = errores[0]
        self.assertEqual((error.esperados, error.encontrado.lexema, error.linea, error.columna),
                         (["HACER"], "entonces", 2, 16))
        self.assertEqual(str(error), "Error sintáctico en la línea 2, columna 16: se esperaba "
                                     "HACER y se encontró 'entonces' (ENTONCES).")

    def test_arbol_con_errores(self):
        # El árbol se construye igual, con nodos ERROR (no terminales omitidos)
        # y hojas de lexema vacío (terminales que faltaban).
        raiz, errores = analizar("inicio x = (a + ; fin")
        self.assertEqual(len(errores), 1)
        self.assertEqual(raiz.simbolo, "<programa>")
        omitidos = [n.simbolo for n in raiz.recorrer() if n.regla == REGLA_ERROR]
        self.assertIn("<termino>", omitidos)
        insertados = [n.simbolo for n in raiz.recorrer() if n.es_terminal and n.token.lexema == ""]
        self.assertEqual(insertados, ["PAR_CIERRA"])

    def test_modo_que_se_detiene(self):
        tokens = AnalizadorLexico().analizar("inicio x = 1 fin z = ; fin")
        with self.assertRaises(ErrorSintactico):
            Parser(tokens, detener_en_error=True).analizar()


class PruebaArchivosConErrores(unittest.TestCase):
    """Los 3 programas con errores sintácticos de tests/errores (sin errores léxicos)."""

    ESPERADO = {
        "sintactico1_expresiones.cft": [
            ("PUNTO_COMA", 4, 28), ("MULT", 5, 26), ("MENOR", 6, 20), ("MOSTRAR", 10, 5)],
        "sintactico2_sentencias.cft": [
            ("SI", 3, 10), ("ENTERO", 4, 13), ("ENTONCES", 5, 29), ("PAR_CIERRA", 8, 13),
            ("SINO", 9, 5)],
        "sintactico3_bloques.cft": [
            ("ID", 4, 8), ("ENTONCES", 4, 17), ("EOF", 15, 1)],
    }

    def test_errores_esperados(self):
        for nombre, esperado in self.ESPERADO.items():
            with self.subTest(archivo=nombre):
                lexer = AnalizadorLexico()
                parser = Parser(lexer.analizar_archivo(ERRORES / nombre))
                parser.analizar()
                self.assertEqual(lexer.errores, [])
                self.assertEqual(resumen(parser.errores), esperado)


class PruebaSinErrores(unittest.TestCase):

    def test_programas_de_ejemplo(self):
        lexer = AnalizadorLexico()
        for archivo in sorted(EJEMPLOS.glob("*.cft")):
            with self.subTest(programa=archivo.name):
                tokens = lexer.analizar_archivo(archivo)
                parser = Parser(tokens)
                raiz = parser.analizar()
                self.assertEqual(parser.errores, [])
                self.assertEqual(raiz, Parser(tokens, detener_en_error=True).analizar())


class PruebaPropiedades(unittest.TestCase):
    """Con cualquier entrada, la recuperación termina y es coherente con PAR-2 y PAR-3.

    * el análisis siempre llega al final, sin excepciones;
    * hay errores si y solo si el modo que se detiene encuentra un error;
    * el primer error es el mismo que en el modo que se detiene;
    * los errores están en el orden del texto, cada uno en un token distinto.
    """

    TIPOS = ["DATO", "ID", "ASIGNACION", "ENTERO", "PUNTO_COMA", "SI", "PAR_ABRE",
             "PAR_CIERRA", "ENTONCES", "SINO", "FIN", "MOSTRAR", "MIENTRAS", "HACER",
             "SUMA", "MENOR"]

    def comprobar(self, tipos, tabla, siguiente):
        tokens = par2.tokens_de(tipos)
        try:
            Parser(tokens, tabla, siguiente, detener_en_error=True).analizar()
            primero = None
        except ErrorSintactico as error:
            primero = tokens.index(error.encontrado)
        parser = Parser(tokens, tabla, siguiente)
        parser.analizar()
        indices = [tokens.index(e.encontrado) for e in parser.errores]
        self.assertEqual(bool(indices), primero is not None, tipos)
        if indices:
            self.assertEqual(indices[0], primero, tipos)
            self.assertEqual(indices, sorted(set(indices)), tipos)
        return len(indices)

    def test_todos_los_programas_de_hasta_3_tokens(self):
        tabla, siguiente = TablaLL1(), cargar_siguiente()
        total = 0
        for n in range(4):
            for tipos in itertools.product(self.TIPOS, repeat=n):
                self.comprobar(["INICIO", *tipos, "FIN"], tabla, siguiente)
                total += 1
        self.assertEqual(total, 4369)

    def test_programas_al_azar_con_varios_errores(self):
        tabla, siguiente, azar = TablaLL1(), cargar_siguiente(), random.Random(2026)
        lexer = AnalizadorLexico()
        validos = [[t.tipo for t in lexer.analizar_archivo(a)][:-1] for a in sorted(EJEMPLOS.glob("*.cft"))]
        terminales = sorted({s for lado in par3.GRAMATICA.values() for s in lado if not s.startswith("<")})
        varios = 0
        for _ in range(300):
            tipos = list(azar.choice(validos))
            for _ in range(azar.randint(1, 4)):          # de 1 a 4 tokens cambiados
                tipos[azar.randrange(len(tipos))] = azar.choice(terminales)
            varios += self.comprobar(tipos, tabla, siguiente) > 1
        self.assertGreater(varios, 0)                    # hubo programas con varios errores


if __name__ == "__main__":
    unittest.main()
