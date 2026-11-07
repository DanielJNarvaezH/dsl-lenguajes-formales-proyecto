"""Pruebas de la base común del parser y de las funciones de expresiones (PAR-2).

Ejecutar desde la raíz del repositorio:

    python -m unittest tests.test_parser_expresiones -v

Las expresiones se analizan con Parser.analizar_fragmento("<expresion>", ...):
una expresión siempre va seguida de PUNTO_COMA o PAR_CIERRA (SIGUIENTE de
<expresion> en GIC-6), así que se prueba como "expresión ;".
"""

import ast
import itertools
import unittest
from pathlib import Path

from src.lexer.lexer import AnalizadorLexico, Token
from src.parser.arbol import Nodo
from src.parser.parser import ErrorSintactico, Parser, TablaLL1

RAIZ = Path(__file__).resolve().parent.parent
EJEMPLOS = RAIZ / "ejemplos"

# Lado derecho de cada regla de expresiones (factorizacion.md, sección 6).
# Solo lo usa el analizador de referencia de estas pruebas, no el parser.
GRAMATICA = {
    "R3": ["<conjuncion>", "<expresion_prima>"],
    "R4": ["O", "<conjuncion>", "<expresion_prima>"], "R5": [],
    "R6": ["<negacion>", "<conjuncion_prima>"],
    "R7": ["Y", "<negacion>", "<conjuncion_prima>"], "R8": [],
    "E5": ["NO", "<negacion>"], "E6": ["<comparacion>"],
    "F1": ["<suma>", "<comparacion_prima>"],
    "F2": ["<op_rel>", "<suma>"], "F3": [],
    "E9": ["MENOR"], "E10": ["MAYOR"], "E11": ["MENOR_IGUAL"],
    "E12": ["MAYOR_IGUAL"], "E13": ["IGUAL"], "E14": ["DIFERENTE"],
    "R9": ["<termino>", "<suma_prima>"],
    "R10": ["SUMA", "<termino>", "<suma_prima>"],
    "R11": ["RESTA", "<termino>", "<suma_prima>"], "R12": [],
    "R13": ["<factor>", "<termino_prima>"],
    "R14": ["MULT", "<factor>", "<termino_prima>"],
    "R15": ["DIV", "<factor>", "<termino_prima>"], "R16": [],
    "E21": ["PAR_ABRE", "<expresion>", "PAR_CIERRA"],
    "E22": ["ID"], "E23": ["ENTERO"], "E24": ["DECIMAL"],
}

NO_TERMINALES_EXPRESIONES = [
    "<expresion>", "<expresion_prima>", "<conjuncion>", "<conjuncion_prima>",
    "<negacion>", "<comparacion>", "<comparacion_prima>", "<op_rel>",
    "<suma>", "<suma_prima>", "<termino>", "<termino_prima>", "<factor>"]


def referencia_ll1(tabla, tokens, inicial, seguido_de):
    """Analizador LL(1) con pila (como las trazas de la sección 11 de GIC-6).

    Devuelve (reglas aplicadas, índice del token con error o None).
    """
    pila = ["EOF"] + list(reversed(seguido_de)) + [inicial]
    i, reglas = 0, []
    while pila:
        cima = pila.pop()
        tipo = tokens[i].tipo
        if cima.startswith("<"):
            regla = tabla.regla(cima, tipo)
            if regla is None:
                return reglas, i
            reglas.append(regla)
            pila.extend(reversed(GRAMATICA[regla]))
        elif cima == tipo:
            i += 1
        else:
            return reglas, i
    return reglas, None


def tokens_de(tipos):
    """Tokens artificiales en una sola línea, para las pruebas exhaustivas."""
    return [Token(t, t.lower(), 1, i + 1) for i, t in enumerate(tipos)] + \
           [Token("EOF", "", 1, len(tipos) + 1)]


class PruebaTabla(unittest.TestCase):

    def test_dimensiones(self):
        tabla = TablaLL1()
        self.assertEqual(len(tabla.no_terminales), 23)
        self.assertEqual(len(tabla.terminales), 31)       # 30 tokens + EOF
        self.assertEqual(len(tabla.celdas), 106)

    def test_esperados_en_orden_de_columnas(self):
        tabla = TablaLL1()
        self.assertEqual(tabla.esperados("<factor>"), ["ID", "ENTERO", "DECIMAL", "PAR_ABRE"])


class PruebaFunciones(unittest.TestCase):
    """Una función por no terminal de expresiones, con su regla BNF escrita encima."""

    def test_una_funcion_por_no_terminal(self):
        tabla = TablaLL1()
        for no_terminal in NO_TERMINALES_EXPRESIONES:
            with self.subTest(no_terminal=no_terminal):
                funcion = getattr(Parser, no_terminal.strip("<>"))
                reglas = {r for (nt, _), r in tabla.celdas.items() if nt == no_terminal}
                for regla in reglas:
                    self.assertIn(regla, funcion.__doc__)


class PruebaArboles(unittest.TestCase):

    def setUp(self):
        self.lexer = AnalizadorLexico()

    def arbol(self, texto):
        tokens = self.lexer.analizar(texto + ";")
        return tokens, Parser(tokens).analizar_fragmento("<expresion>", "PUNTO_COMA")

    def test_frontera_es_la_expresion(self):
        for texto in ["kilos + 25 * 2", "10 - 4 - 2", "a o b y c",
                      "dia == 5 o no (humedad > 20)", "no no (x)", "11.5 / 2 >= promedio_2lotes"]:
            with self.subTest(expresion=texto):
                tokens, raiz = self.arbol(texto)
                self.assertEqual(raiz.frontera(), tokens[:-2])     # sin ; ni EOF

    def test_un_solo_factor(self):
        # Mismo orden que el ejemplo de la sección 5 de arbol.md (PAR-1).
        _, raiz = self.arbol("1")
        self.assertEqual(raiz.derivacion_izquierda(),
                         ["R3", "R6", "E6", "F1", "R9", "R13", "E23", "R16", "R12", "F3", "R8", "R5"])

    def test_precedencia_mult_debajo_de_suma(self):
        # kilos + 25 * 2: el MULT queda dentro del <termino> que sigue al SUMA.
        _, raiz = self.arbol("kilos + 25 * 2")
        suma = raiz.hijos[0].hijos[0].hijos[0].hijos[0]            # <suma>
        suma_prima = suma.hijos[1]
        self.assertEqual((suma_prima.regla, suma_prima.hijos[0].simbolo), ("R10", "SUMA"))
        termino = suma_prima.hijos[1]
        self.assertEqual(termino.hijos[1].regla, "R14")            # <termino_prima> con MULT

    def test_asociatividad_en_la_cadena_prima(self):
        # 10 - 4 - 2: los operadores quedan en la cadena de <suma_prima>, en el
        # orden del texto (sección 7.2 de recursividad.md).
        _, raiz = self.arbol("10 - 4 - 2")
        suma = raiz.hijos[0].hijos[0].hijos[0].hijos[0]
        cadena, nodo = [], suma.hijos[1]
        while nodo.regla != "R12":
            cadena.append((nodo.hijos[0].simbolo, nodo.hijos[1].frontera()[0].lexema))
            nodo = nodo.hijos[2]
        self.assertEqual(cadena, [("RESTA", "4"), ("RESTA", "2")])

    def test_y_debajo_de_o(self):
        _, raiz = self.arbol("a o b y c")
        expresion_prima = raiz.hijos[1]
        self.assertEqual(expresion_prima.regla, "R4")
        self.assertIn("R7", expresion_prima.derivacion_izquierda())   # el y está dentro
        self.assertNotIn("R7", raiz.hijos[0].derivacion_izquierda())  # no en la izquierda

    def test_parentesis_vuelven_a_expresion(self):
        _, raiz = self.arbol("(a o b) y c")
        self.assertIn("R4", raiz.hijos[0].derivacion_izquierda())    # el o queda dentro del ( )
        self.assertEqual(raiz.hijos[1].regla, "R5")

    def test_expresiones_largas_y_anidadas(self):
        # 300 operadores seguidos y 50 niveles de paréntesis (sección 6 de parser.md).
        tokens, raiz = self.arbol("a" + " + a" * 300)
        self.assertEqual(len(raiz.frontera()), 601)
        tokens, raiz = self.arbol("(" * 50 + "a" + ")" * 50)
        self.assertEqual(raiz.derivacion_izquierda().count("E21"), 50)

    def test_cada_nodo_tiene_los_hijos_de_su_regla(self):
        _, raiz = self.arbol("dia == 5 o no (humedad > 20) y x != 2.5 * (k - 1)")
        for nodo in raiz.recorrer():
            if nodo.es_no_terminal:
                esperado = GRAMATICA[nodo.regla] or ["ε"]
                self.assertEqual([h.simbolo for h in nodo.hijos], esperado, nodo)


class PruebaReferenciaLL1(unittest.TestCase):
    """Las funciones del parser aplican las mismas reglas que el analizador LL(1) con pila."""

    TIPOS = ["ID", "ENTERO", "SUMA", "MULT", "O", "Y", "NO", "MENOR", "PAR_ABRE", "PAR_CIERRA"]

    def comparar(self, tokens, seguido_de):
        tabla = TablaLL1()
        reglas_ref, error_ref = referencia_ll1(tabla, tokens, "<expresion>", seguido_de)
        try:
            raiz = Parser(tokens, tabla, detener_en_error=True).analizar_fragmento("<expresion>", *seguido_de)
        except ErrorSintactico as error:
            self.assertEqual(tokens.index(error.encontrado), error_ref, tokens)
            return False
        self.assertIsNone(error_ref, tokens)
        self.assertEqual(raiz.derivacion_izquierda(), reglas_ref)
        return True

    def test_todas_las_cadenas_de_hasta_4_tokens(self):
        aceptadas = total = 0
        for n in range(5):
            for tipos in itertools.product(self.TIPOS, repeat=n):
                total += 1
                aceptadas += self.comparar(tokens_de(list(tipos) + ["PUNTO_COMA"]), ["PUNTO_COMA"])
        self.assertEqual(total, 11111)
        self.assertGreater(aceptadas, 0)

    def test_expresiones_de_los_programas_de_ejemplo(self):
        # Lado derecho de cada asignación y declaración (hasta el ;) y condición
        # de cada si y mientras (hasta el ) que precede a entonces o hacer).
        lexer = AnalizadorLexico()
        cantidad = 0
        for archivo in sorted(EJEMPLOS.glob("*.cft")):
            tipos = [t.tipo for t in lexer.analizar_archivo(archivo)]
            for i, tipo in enumerate(tipos):
                if tipo == "ASIGNACION":
                    fin = tipos.index("PUNTO_COMA", i)
                    segmento, cierre = tipos[i + 1:fin], "PUNTO_COMA"
                elif tipo in ("SI", "MIENTRAS"):
                    fin = next(j for j in range(i, len(tipos)) if tipos[j] in ("ENTONCES", "HACER"))
                    segmento, cierre = tipos[i + 2:fin - 1], "PAR_CIERRA"
                else:
                    continue
                with self.subTest(archivo=archivo.name, posicion=i):
                    self.assertTrue(self.comparar(tokens_de(segmento + [cierre]), [cierre]))
                cantidad += 1
        self.assertEqual(cantidad, 17)


class PruebaErrores(unittest.TestCase):
    """Comportamiento de PAR-2: el primer error detiene el análisis.

    Desde PAR-4 el parser se recupera por defecto; estas pruebas usan
    detener_en_error=True. La recuperación se prueba en
    tests/test_errores_sintacticos.py.
    """

    def setUp(self):
        self.lexer = AnalizadorLexico()

    def error(self, texto):
        with self.assertRaises(ErrorSintactico) as contexto:
            Parser(self.lexer.analizar(texto), detener_en_error=True).analizar_fragmento(
                "<expresion>", "PUNTO_COMA")
        return contexto.exception

    def test_relacionales_encadenados(self):
        # a < b < c: el segundo < llega cuando se analiza <conjuncion_prima> (GIC-6, 9.1).
        error = self.error("a < b < c;")
        self.assertEqual((error.encontrado.tipo, error.columna, error.contexto),
                         ("MENOR", 7, "<conjuncion_prima>"))
        self.assertEqual(error.esperados, ["Y", "O", "PAR_CIERRA", "PUNTO_COMA"])

    def test_falta_operando(self):
        # Cada función consulta la tabla al entrar, así que el error se detecta
        # en <termino>, el primer no terminal que no puede empezar con ;.
        error = self.error("(a + ;")
        self.assertEqual((error.encontrado.tipo, error.contexto), ("PUNTO_COMA", "<termino>"))
        self.assertEqual(error.esperados, ["ID", "ENTERO", "DECIMAL", "PAR_ABRE"])

    def test_falta_parentesis_de_cierre(self):
        error = self.error("(a;")
        self.assertEqual((error.esperados, error.columna), (["PAR_CIERRA"], 3))

    def test_esperados_son_la_fila_de_la_tabla(self):
        error = self.error("a b;")
        self.assertEqual(error.esperados, TablaLL1().esperados("<termino_prima>"))

    def test_mensaje(self):
        self.assertEqual(str(self.error("(a;")),
                         "Error sintáctico en la línea 1, columna 3: se esperaba PAR_CIERRA "
                         "y se encontró ';' (PUNTO_COMA).")
        error = self.error("a")                                  # falta el ;
        self.assertIn("se encontró el fin del archivo", str(error))

    def test_sobra_texto_al_final(self):
        with self.assertRaises(ErrorSintactico) as contexto:
            Parser(self.lexer.analizar("a; b"), detener_en_error=True).analizar_fragmento(
                "<expresion>", "PUNTO_COMA")
        self.assertEqual(contexto.exception.esperados, ["EOF"])
        self.assertIn("se esperaba el fin del archivo", str(contexto.exception))


class PruebaRestricciones(unittest.TestCase):

    def setUp(self):
        self.codigo = (RAIZ / "src" / "parser" / "parser.py").read_text(encoding="utf-8")
        self.arbol = ast.parse(self.codigo)

    def test_no_importa_re(self):
        modulos = {alias.name for nodo in ast.walk(self.arbol) if isinstance(nodo, ast.Import)
                   for alias in nodo.names}
        modulos |= {nodo.module for nodo in ast.walk(self.arbol) if isinstance(nodo, ast.ImportFrom)}
        self.assertNotIn("re", modulos)

    def test_las_decisiones_comparan_reglas_de_la_tabla(self):
        # Las comparaciones con texto fijo solo usan etiquetas de reglas, que
        # vienen de la tabla LL(1); nunca se pregunta directamente por un token.
        reglas = set(TablaLL1().celdas.values())
        clase = next(n for n in self.arbol.body if isinstance(n, ast.ClassDef) and n.name == "Parser")
        for nodo in ast.walk(clase):
            if isinstance(nodo, ast.Compare):
                for parte in [nodo.left, *nodo.comparators]:
                    if isinstance(parte, ast.Constant) and isinstance(parte.value, str):
                        self.assertIn(parte.value, reglas, ast.unparse(nodo))


if __name__ == "__main__":
    unittest.main()
