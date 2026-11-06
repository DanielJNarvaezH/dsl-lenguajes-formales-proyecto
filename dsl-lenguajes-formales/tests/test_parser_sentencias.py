"""Pruebas de las funciones de programa y sentencias del parser (PAR-3).

Ejecutar desde la raíz del repositorio:

    python -m unittest tests.test_parser_sentencias -v

Usan un analizador LL(1) con pila igual al de referencia de PAR-2, pero con
la gramática completa, y los árboles armados a mano de PAR-1. De las pruebas
de PAR-1 y PAR-2 se importan los módulos, no sus clases, para que unittest no
vuelva a ejecutar aquí las pruebas de esos archivos.
"""

import itertools
import random
import unittest
from pathlib import Path

from src.lexer.lexer import AnalizadorLexico, Token
from src.parser.parser import ErrorSintactico, Parser, TablaLL1
from tests import test_arbol as par1
from tests import test_parser_expresiones as par2

RAIZ = Path(__file__).resolve().parent.parent
EJEMPLOS = RAIZ / "ejemplos"

# Lado derecho de cada regla de programa y sentencias (factorizacion.md,
# sección 6). Junto con las de expresiones de PAR-2 forman la gramática completa.
# Solo lo usan estas pruebas, no el parser.
GRAMATICA = dict(par2.GRAMATICA)
GRAMATICA.update({
    "P1": ["INICIO", "<sentencias>", "FIN"],
    "R1": ["<sentencia>", "<sentencias>"], "R2": [],
    "P4": ["<declaracion>"], "P5": ["<asignacion>"], "P6": ["<salida>"],
    "P7": ["<condicional>"], "P8": ["<ciclo>"],
    "D1": ["DATO", "ID", "ASIGNACION", "<expresion>", "PUNTO_COMA"],
    "A1": ["ID", "ASIGNACION", "<expresion>", "PUNTO_COMA"],
    "M1": ["MOSTRAR", "PAR_ABRE", "<argumento>", "PAR_CIERRA", "PUNTO_COMA"],
    "M2": ["<expresion>"], "M3": ["CADENA"],
    "F4": ["SI", "PAR_ABRE", "<expresion>", "PAR_CIERRA", "ENTONCES",
           "<sentencias>", "<condicional_prima>"],
    "F5": ["FIN"], "F6": ["SINO", "<sentencias>", "FIN"],
    "L1": ["MIENTRAS", "PAR_ABRE", "<expresion>", "PAR_CIERRA", "HACER", "<sentencias>", "FIN"],
})

NO_TERMINALES_SENTENCIAS = [
    "<programa>", "<sentencias>", "<sentencia>", "<declaracion>", "<asignacion>",
    "<salida>", "<argumento>", "<condicional>", "<condicional_prima>", "<ciclo>"]


def referencia_ll1(tabla, tokens):
    """Analizador LL(1) con pila sobre la gramática completa, desde <programa>.

    Es el mismo algoritmo que par2.referencia_ll1 (trazas de la sección 11 de
    GIC-6). Devuelve (reglas aplicadas, índice del token con error o None).
    """
    pila = ["EOF", "<programa>"]
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


def analizar(texto):
    return Parser(AnalizadorLexico().analizar(texto)).analizar()


def nodos(raiz, simbolo):
    """Nodos con ese símbolo, en preorden."""
    return [n for n in raiz.recorrer() if n.simbolo == simbolo]


class PruebaFunciones(unittest.TestCase):

    def test_una_funcion_por_no_terminal_con_su_regla(self):
        tabla = TablaLL1()
        for no_terminal in NO_TERMINALES_SENTENCIAS:
            with self.subTest(no_terminal=no_terminal):
                funcion = getattr(Parser, no_terminal.strip("<>"))
                reglas = {r for (nt, _), r in tabla.celdas.items() if nt == no_terminal}
                for regla in reglas:
                    self.assertIn(regla, funcion.__doc__)

    def test_todos_los_no_terminales_tienen_funcion(self):
        # Con PAR-2 y PAR-3, los 23 no terminales de la tabla tienen su función.
        for no_terminal in TablaLL1().no_terminales:
            with self.subTest(no_terminal=no_terminal):
                self.assertTrue(callable(getattr(Parser, no_terminal.strip("<>"), None)))

    def test_la_gramatica_de_las_pruebas_cubre_la_tabla(self):
        self.assertEqual(set(GRAMATICA), set(TablaLL1().celdas.values()))


class PruebaProgramasDeEjemplo(unittest.TestCase):
    """Los tres programas de ejemplos/ con el analizador completo."""

    REGLAS = {"ejemplo1_produccion.cft": 174,
              "ejemplo2_clasificacion.cft": 134,
              "ejemplo3_secado.cft": 165}

    def test_arbol_completo(self):
        lexer, tabla = AnalizadorLexico(), TablaLL1()
        for nombre, cantidad in self.REGLAS.items():
            with self.subTest(programa=nombre):
                tokens = lexer.analizar_archivo(EJEMPLOS / nombre)
                raiz = Parser(tokens, tabla).analizar()
                self.assertEqual(raiz.simbolo, "<programa>")
                self.assertEqual(raiz.frontera(), tokens[:-1])           # todo menos EOF
                reglas, error = referencia_ll1(tabla, tokens)
                self.assertIsNone(error)
                self.assertEqual(raiz.derivacion_izquierda(), reglas)
                self.assertEqual(len(reglas), cantidad)
                for nodo in raiz.recorrer():
                    if nodo.es_no_terminal:
                        esperado = GRAMATICA[nodo.regla] or ["ε"]
                        self.assertEqual([h.simbolo for h in nodo.hijos], esperado, nodo)

    def test_estructura_del_secado(self):
        raiz = analizar((EJEMPLOS / "ejemplo3_secado.cft").read_text(encoding="utf-8"))
        sentencias = [n.hijos[0].simbolo for n in nodos(raiz, "<sentencia>")]
        self.assertEqual(sentencias, ["<declaracion>", "<declaracion>", "<ciclo>", "<asignacion>",
                                      "<condicional>", "<salida>", "<asignacion>", "<salida>"])
        # Cuerpo del mientras: se recorre la cadena de <sentencias> (R1 … R2)
        # que es el sexto hijo de L1.
        ciclo = nodos(raiz, "<ciclo>")[0]
        cuerpo, lista = [], ciclo.hijos[5]
        while lista.regla == "R1":
            cuerpo.append(lista.hijos[0].hijos[0].simbolo)
            lista = lista.hijos[1]
        self.assertEqual(cuerpo, ["<asignacion>", "<condicional>", "<asignacion>"])


class PruebaArbolesDePar1(unittest.TestCase):
    """El parser construye exactamente los árboles armados regla por regla en PAR-1."""

    def test_mismos_arboles(self):
        lexer = AnalizadorLexico()
        for texto, espec in [("inicio x = 1; fin", par1.ASIGNACION),
                             ('inicio si (a > 0) entonces mostrar("ok"); sino fin fin', par1.CONDICIONAL)]:
            with self.subTest(programa=texto):
                tokens = lexer.analizar(texto)
                self.assertEqual(Parser(tokens).analizar(), par1.construir(espec, iter(tokens)))


class PruebaSentencias(unittest.TestCase):

    def test_programa_vacio(self):
        raiz = analizar("inicio fin")
        self.assertEqual(raiz.derivacion_izquierda(), ["P1", "R2"])

    def test_cada_sentencia_usa_su_regla(self):
        raiz = analizar('inicio dato a = 1; a = 2; mostrar(a); si (a) entonces fin '
                        'mientras (a) hacer fin fin')
        reglas = [n.regla for n in nodos(raiz, "<sentencia>")]
        self.assertEqual(reglas, ["P4", "P5", "P6", "P7", "P8"])

    def test_argumento_cadena_o_expresion(self):
        raiz = analizar('inicio mostrar("kilos"); mostrar(a + 1); fin')
        self.assertEqual([n.regla for n in nodos(raiz, "<argumento>")], ["M3", "M2"])

    def test_bloques_vacios(self):
        for texto, reglas in [("inicio si (a) entonces fin fin", ["F5"]),
                              ("inicio si (a) entonces sino fin fin", ["F6"]),
                              ("inicio mientras (a) hacer fin fin", [])]:
            with self.subTest(programa=texto):
                raiz = analizar(texto)
                self.assertEqual([n.regla for n in nodos(raiz, "<condicional_prima>")], reglas)

    def test_sino_colgante(self):
        # GIC-3, sección 6.2: cada texto con fin tiene una sola lectura.
        interno = analizar("inicio si (a) entonces si (b) entonces x = 1; sino x = 2; fin fin fin")
        externo = analizar("inicio si (a) entonces si (b) entonces x = 1; fin sino x = 2; fin fin")
        # Preorden: el primer <condicional_prima> que aparece es el del si interno.
        self.assertEqual([n.regla for n in nodos(interno, "<condicional_prima>")], ["F6", "F5"])
        self.assertEqual([n.regla for n in nodos(externo, "<condicional_prima>")], ["F5", "F6"])
        with self.assertRaises(ErrorSintactico):                # falta un fin
            analizar("inicio si (a) entonces si (b) entonces x = 1; sino x = 2; fin fin")

    def test_anidamiento(self):
        raiz = analizar("inicio mientras (a) hacer si (b) entonces mientras (c) hacer "
                        "x = 1; fin sino y_ = 2; fin fin fin")
        self.assertEqual([n.simbolo for n in raiz.recorrer() if n.simbolo in ("<ciclo>", "<condicional>")],
                         ["<ciclo>", "<condicional>", "<ciclo>"])

    def test_programas_largos_y_profundos(self):
        # Sección 9.4 de parser.md: unas 980 sentencias seguidas y 320 bloques
        # anidados con el límite de recursión por defecto.
        raiz = analizar("inicio " + "x = 1; " * 500 + "fin")
        self.assertEqual(len(nodos(raiz, "<sentencia>")), 500)
        raiz = analizar("inicio " + "si (a) entonces " * 100 + "fin " * 100 + "fin")
        self.assertEqual(len(nodos(raiz, "<condicional>")), 100)


class PruebaReferenciaLL1(unittest.TestCase):
    """Las funciones aplican las mismas reglas que el analizador LL(1) con pila."""

    TIPOS = ["DATO", "ID", "ASIGNACION", "ENTERO", "PUNTO_COMA", "SI", "PAR_ABRE",
             "PAR_CIERRA", "ENTONCES", "SINO", "FIN", "MOSTRAR"]

    def comparar(self, tokens, tabla):
        reglas_ref, error_ref = referencia_ll1(tabla, tokens)
        try:
            raiz = Parser(tokens, tabla).analizar()
        except ErrorSintactico as error:
            self.assertEqual(tokens.index(error.encontrado), error_ref, tokens)
            return False
        self.assertIsNone(error_ref, tokens)
        self.assertEqual(raiz.derivacion_izquierda(), reglas_ref)
        return True

    def test_todos_los_programas_de_hasta_4_tokens_entre_inicio_y_fin(self):
        tabla = TablaLL1()
        aceptados = total = 0
        for n in range(5):
            for tipos in itertools.product(self.TIPOS, repeat=n):
                total += 1
                aceptados += self.comparar(par2.tokens_de(["INICIO", *tipos, "FIN"]), tabla)
        self.assertEqual(total, 22621)
        self.assertGreater(aceptados, 0)

    def test_programas_generados_al_azar(self):
        # Programas derivados al azar desde <programa> y variantes con un token
        # cambiado, para probar programas largos y anidados.
        tabla, azar = TablaLL1(), random.Random(2026)
        reglas_de = {}
        for (nt, _), regla in tabla.celdas.items():
            reglas_de.setdefault(nt, set()).add(regla)
        reglas_de = {nt: sorted(r) for nt, r in reglas_de.items()}

        def generar(simbolo, profundidad):
            if not simbolo.startswith("<"):
                return [simbolo]
            opciones = reglas_de[simbolo]
            if profundidad > 6:
                # Para terminar: una regla que no se llame a sí misma, con la
                # menor cantidad de no terminales.
                no_recursivas = [r for r in opciones if simbolo not in GRAMATICA[r]]
                opciones = [min(no_recursivas, key=lambda r: sum(s.startswith("<") for s in GRAMATICA[r]))]
            salida = []
            for s in GRAMATICA[azar.choice(opciones)]:
                salida += generar(s, profundidad + 1)
            return salida

        terminales = sorted({s for lado in GRAMATICA.values() for s in lado if not s.startswith("<")})
        aceptados = rechazados = 0
        for _ in range(300):
            tipos = generar("<programa>", 0)
            self.assertTrue(self.comparar(par2.tokens_de(tipos), tabla))
            aceptados += 1
            for _ in range(2):
                variante = list(tipos)
                variante[azar.randrange(len(variante))] = azar.choice(terminales)
                if not self.comparar(par2.tokens_de(variante), tabla):
                    rechazados += 1
        self.assertGreater(rechazados, 0)


class PruebaErrores(unittest.TestCase):

    def error(self, texto):
        with self.assertRaises(ErrorSintactico) as contexto:
            analizar(texto)
        return contexto.exception

    def test_archivo_vacio(self):
        error = self.error("")
        self.assertEqual((error.contexto, error.esperados), ("<programa>", ["INICIO"]))

    def test_falta_fin_del_programa(self):
        error = self.error("inicio\n  x = 1;\n")
        self.assertEqual((error.encontrado.tipo, error.contexto), ("EOF", "<sentencias>"))
        self.assertEqual(error.esperados, TablaLL1().esperados("<sentencias>"))
        self.assertIn("se encontró el fin del archivo", str(error))

    def test_falta_punto_y_coma(self):
        # FIN no puede seguir a una expresión: el error se detecta dentro de
        # ella, en el primer no terminal cuya fila no tiene FIN.
        error = self.error("inicio\n  x = 1\nfin")
        self.assertEqual((error.encontrado.tipo, error.linea, error.columna), ("FIN", 3, 1))
        self.assertEqual(error.contexto, "<termino_prima>")

    def test_palabra_reservada_como_variable(self):
        # GIC-1, sección 3: después de DATO se espera ID y llega SI.
        error = self.error("inicio dato si = 3; fin")
        self.assertEqual((error.esperados, error.encontrado.tipo, error.columna), (["ID"], "SI", 13))

    def test_sino_sin_si(self):
        # SINO está en SIGUIENTE(<sentencias>), así que R2 se aplica; el error
        # aparece al emparejar el FIN del programa.
        error = self.error("inicio sino fin")
        self.assertEqual((error.esperados, error.encontrado.tipo), (["FIN"], "SINO"))

    def test_palabra_del_bloque_equivocada(self):
        error = self.error("inicio mientras (a) entonces fin fin")
        self.assertEqual((error.esperados, error.encontrado.tipo), (["HACER"], "ENTONCES"))

    def test_mostrar_sin_argumento(self):
        error = self.error("inicio mostrar(); fin")
        self.assertEqual((error.contexto, error.encontrado.tipo), ("<argumento>", "PAR_CIERRA"))
        self.assertEqual(error.esperados, TablaLL1().esperados("<argumento>"))

    def test_sobra_texto_despues_del_programa(self):
        error = self.error("inicio fin fin")
        self.assertEqual((error.esperados, error.columna), (["EOF"], 12))

    def test_mensaje(self):
        self.assertEqual(str(self.error("inicio\n  mientras (a) entonces fin\nfin")),
                         "Error sintáctico en la línea 2, columna 16: se esperaba HACER "
                         "y se encontró 'entonces' (ENTONCES).")


if __name__ == "__main__":
    unittest.main()
