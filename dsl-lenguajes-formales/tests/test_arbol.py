"""Pruebas del árbol de derivación y del contrato entre lexer y parser (PAR-1).

Ejecutar desde la raíz del repositorio:

    python -m unittest tests.test_arbol -v
"""

import ast
import unittest
from pathlib import Path

from src.lexer.lexer import AnalizadorLexico, Token
from src.parser.arbol import EPSILON, ErrorContrato, Nodo, verificar_contrato

RAIZ = Path(__file__).resolve().parent.parent
EJEMPLOS = RAIZ / "ejemplos"
ERRORES = RAIZ / "tests" / "errores"


def construir(espec, tokens):
    """Arma un árbol a partir de una especificación anidada, consumiendo tokens en orden.

    * ("<no_terminal>", "REGLA", [hijos]) es un no terminal;
    * "ε" es una hoja vacía;
    * cualquier otro texto es un terminal: se empareja con el siguiente token.
    """
    if isinstance(espec, tuple):
        simbolo, regla, hijos = espec
        nodo = Nodo.no_terminal(simbolo, regla)
        for hijo in hijos:
            nodo.agregar(construir(hijo, tokens))
        return nodo
    if espec == EPSILON:
        return Nodo.vacio()
    token = next(tokens)
    assert token.tipo == espec, f"se esperaba {espec} y llegó {token.tipo}"
    return Nodo.terminal(token)


def vacio(simbolo, regla):
    return (simbolo, regla, [EPSILON])


def suma(regla_factor, terminal):
    """<suma> que deriva un solo factor (ID, ENTERO o DECIMAL)."""
    return ("<suma>", "R9", [
        ("<termino>", "R13", [("<factor>", regla_factor, [terminal]),
                              vacio("<termino_prima>", "R16")]),
        vacio("<suma_prima>", "R12")])


def expresion(comparacion):
    """<expresion> sin O, Y ni NO, a partir de una <comparacion>."""
    return ("<expresion>", "R3", [
        ("<conjuncion>", "R6", [("<negacion>", "E6", [comparacion]),
                                vacio("<conjuncion_prima>", "R8")]),
        vacio("<expresion_prima>", "R5")])


# inicio x = 1; fin
ASIGNACION = ("<programa>", "P1", [
    "INICIO",
    ("<sentencias>", "R1", [
        ("<sentencia>", "P5", [
            ("<asignacion>", "A1", [
                "ID", "ASIGNACION",
                expresion(("<comparacion>", "F1", [suma("E23", "ENTERO"),
                                                   vacio("<comparacion_prima>", "F3")])),
                "PUNTO_COMA"])]),
        vacio("<sentencias>", "R2")]),
    "FIN"])

# inicio si (a > 0) entonces mostrar("ok"); sino fin fin
CONDICIONAL = ("<programa>", "P1", [
    "INICIO",
    ("<sentencias>", "R1", [
        ("<sentencia>", "P7", [
            ("<condicional>", "F4", [
                "SI", "PAR_ABRE",
                expresion(("<comparacion>", "F1", [
                    suma("E22", "ID"),
                    ("<comparacion_prima>", "F2", [("<op_rel>", "E10", ["MAYOR"]),
                                                   suma("E23", "ENTERO")])])),
                "PAR_CIERRA", "ENTONCES",
                ("<sentencias>", "R1", [
                    ("<sentencia>", "P6", [
                        ("<salida>", "M1", ["MOSTRAR", "PAR_ABRE",
                                            ("<argumento>", "M3", ["CADENA"]),
                                            "PAR_CIERRA", "PUNTO_COMA"])]),
                    vacio("<sentencias>", "R2")]),
                ("<condicional_prima>", "F6", ["SINO", vacio("<sentencias>", "R2"), "FIN"])])]),
        vacio("<sentencias>", "R2")]),
    "FIN"])


class PruebaNodo(unittest.TestCase):

    def setUp(self):
        self.token = Token("ID", "kilos", 3, 5)

    def test_tres_tipos_de_nodo(self):
        no_terminal = Nodo.no_terminal("<factor>", "E22")
        terminal = Nodo.terminal(self.token)
        vacio_ = Nodo.vacio()
        self.assertEqual((no_terminal.es_no_terminal, no_terminal.es_terminal, no_terminal.es_vacio),
                         (True, False, False))
        self.assertEqual((terminal.es_no_terminal, terminal.es_terminal, terminal.es_vacio),
                         (False, True, False))
        self.assertEqual((vacio_.es_no_terminal, vacio_.es_terminal, vacio_.es_vacio),
                         (False, False, True))
        self.assertEqual((terminal.simbolo, terminal.token), ("ID", self.token))
        self.assertEqual(vacio_.simbolo, "ε")

    def test_agregar_devuelve_el_hijo_en_orden(self):
        padre = Nodo.no_terminal("<factor>", "E22")
        hijo = padre.agregar(Nodo.terminal(self.token))
        self.assertIs(padre.hijos[0], hijo)

    def test_validaciones(self):
        with self.assertRaises(ValueError):
            Nodo.no_terminal("suma", "R9")                      # sin < >
        with self.assertRaises(ValueError):
            Nodo.no_terminal("<suma>", "")                      # sin regla
        with self.assertRaises(TypeError):
            Nodo.terminal("ID")                                 # no es un Token
        with self.assertRaises(ValueError):
            Nodo.terminal(Token("EOF", "", 1, 1))               # EOF no va en el árbol
        with self.assertRaises(ValueError):
            Nodo.terminal(self.token).agregar(Nodo.vacio())     # una hoja no tiene hijos
        with self.assertRaises(ValueError):
            Nodo.vacio().agregar(Nodo.vacio())

    def test_representacion(self):
        nodo = Nodo.no_terminal("<factor>", "E22")
        nodo.agregar(Nodo.terminal(self.token))
        self.assertEqual(repr(nodo), "Nodo(<factor> E22, 1 hijos)")
        self.assertEqual(repr(nodo.hijos[0]), "Nodo(ID 'kilos' 3:5)")
        self.assertEqual(repr(Nodo.vacio()), "Nodo(ε)")


class PruebaArbolCompleto(unittest.TestCase):
    """Árboles de dos programas, armados regla por regla con la gramática final."""

    def setUp(self):
        self.lexer = AnalizadorLexico()

    def arbol(self, texto, espec):
        tokens = self.lexer.analizar(texto)
        return tokens, construir(espec, iter(tokens))

    def test_frontera_es_el_programa_sin_eof(self):
        for texto, espec in [("inicio x = 1; fin", ASIGNACION),
                             ('inicio si (a > 0) entonces mostrar("ok"); sino fin fin', CONDICIONAL)]:
            with self.subTest(programa=texto):
                tokens, raiz = self.arbol(texto, espec)
                self.assertEqual(raiz.frontera(), tokens[:-1])

    def test_derivacion_izquierda(self):
        # Mismo orden en que el analizador LL(1) de GIC-6 aplica las reglas.
        _, raiz = self.arbol("inicio x = 1; fin", ASIGNACION)
        self.assertEqual(raiz.derivacion_izquierda(),
                         ["P1", "R1", "P5", "A1", "R3", "R6", "E6", "F1", "R9", "R13",
                          "E23", "R16", "R12", "F3", "R8", "R5", "R2"])
        _, raiz = self.arbol('inicio si (a > 0) entonces mostrar("ok"); sino fin fin', CONDICIONAL)
        self.assertEqual(raiz.derivacion_izquierda(),
                         ["P1", "R1", "P7", "F4", "R3", "R6", "E6", "F1", "R9", "R13", "E22",
                          "R16", "R12", "F2", "E10", "R9", "R13", "E23", "R16", "R12", "R8",
                          "R5", "R1", "P6", "M1", "M3", "R2", "F6", "R2", "R2"])

    def test_hojas_incluyen_epsilon(self):
        _, raiz = self.arbol("inicio x = 1; fin", ASIGNACION)
        simbolos = [hoja.simbolo for hoja in raiz.hojas()]
        self.assertEqual(simbolos, ["INICIO", "ID", "ASIGNACION", "ENTERO", "ε", "ε", "ε", "ε",
                                    "ε", "PUNTO_COMA", "ε", "FIN"])

    def test_cada_epsilon_es_hijo_unico_de_una_regla_epsilon(self):
        _, raiz = self.arbol('inicio si (a > 0) entonces mostrar("ok"); sino fin fin', CONDICIONAL)
        for nodo in raiz.recorrer():
            if any(hijo.es_vacio for hijo in nodo.hijos):
                self.assertEqual(len(nodo.hijos), 1)
                self.assertIn(nodo.regla, {"R2", "R5", "R8", "F3", "R12", "R16"})

    def test_posicion(self):
        _, raiz = self.arbol("inicio\n  x = 1;\nfin", ASIGNACION)
        sentencia = raiz.hijos[1].hijos[0]
        self.assertEqual(raiz.posicion, (1, 1))
        self.assertEqual(sentencia.posicion, (2, 3))
        self.assertIsNone(raiz.hijos[1].hijos[1].posicion)      # <sentencias> ::= ε

    def test_igualdad_estructural(self):
        _, a = self.arbol("inicio x = 1; fin", ASIGNACION)
        _, b = self.arbol("inicio x = 1; fin", ASIGNACION)
        _, c = self.arbol("inicio z = 1; fin", ASIGNACION)
        self.assertEqual(a, b)
        self.assertNotEqual(a, c)                                # cambia el lexema de ID

    def test_arbol_profundo_sin_limite_de_recursion(self):
        def profundo(hoja):
            raiz = Nodo.no_terminal("<sentencias>", "R1")
            actual = raiz
            for _ in range(5000):
                actual = actual.agregar(Nodo.no_terminal("<sentencias>", "R1"))
            actual.agregar(hoja)
            return raiz
        raiz = profundo(Nodo.vacio())
        self.assertEqual(len(raiz.derivacion_izquierda()), 5001)
        # La igualdad también es iterativa: compara 5 000 niveles sin RecursionError.
        self.assertEqual(raiz, profundo(Nodo.vacio()))
        self.assertNotEqual(raiz, profundo(Nodo.terminal(Token("ID", "x", 1, 1))))


class PruebaContrato(unittest.TestCase):
    """El lexer cumple el contrato y verificar_contrato detecta cada incumplimiento."""

    def setUp(self):
        self.lexer = AnalizadorLexico()

    def test_el_lexer_cumple_el_contrato(self):
        archivos = sorted(EJEMPLOS.glob("*.cft")) + sorted(ERRORES.glob("*.cft"))
        self.assertGreaterEqual(len(archivos), 6)
        for archivo in archivos:
            with self.subTest(archivo=archivo.name):
                verificar_contrato(self.lexer.analizar_archivo(archivo))
        verificar_contrato(self.lexer.analizar(""))              # archivo vacío: solo EOF

    def test_incumplimientos(self):
        buenos = self.lexer.analizar("x = 1;")
        casos = {
            "lista vacía": [],
            "sin EOF": buenos[:-1],
            "EOF en medio": [buenos[-1]] + buenos,
            "tipo fuera del catálogo": [Token("NUMERO", "1", 1, 1)] + buenos[-1:],
            "token descartable": [Token("BLANCO", " ", 1, 1)] + buenos[-1:],
            "orden alterado": [buenos[1], buenos[0]] + buenos[2:],
            "no es un Token": ["ID"] + buenos[-1:],
        }
        for nombre, tokens in casos.items():
            with self.subTest(caso=nombre):
                with self.assertRaises(ErrorContrato):
                    verificar_contrato(tokens)

    def test_con_errores_lexicos_la_lista_sigue_cumpliendo(self):
        tokens = self.lexer.analizar("dato Kilos = 2,5;")
        verificar_contrato(tokens)
        self.assertEqual(len(self.lexer.errores), 2)


class PruebaRestricciones(unittest.TestCase):

    def test_no_importa_re(self):
        arbol = ast.parse((RAIZ / "src" / "parser" / "arbol.py").read_text(encoding="utf-8"))
        modulos = {alias.name for nodo in ast.walk(arbol) if isinstance(nodo, ast.Import)
                   for alias in nodo.names}
        modulos |= {nodo.module for nodo in ast.walk(arbol) if isinstance(nodo, ast.ImportFrom)}
        self.assertNotIn("re", modulos)


if __name__ == "__main__":
    unittest.main()
