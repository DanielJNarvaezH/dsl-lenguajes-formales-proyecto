"""Suite de programas válidos (TST-1).

Ejecutar desde la raíz del repositorio:

    python -m unittest tests.test_validos -v

tests/validos/ tiene 6 programas válidos (.cft) y el árbol esperado de cada uno
(.txt, en el formato de ARB-1). Las pruebas comprueban dos cosas:

1. El parser produce exactamente el árbol esperado (prueba de regresión).
2. El árbol esperado es correcto por sí mismo, sin usar el parser: se lee desde
   el .txt y se valida contra la gramática, contra un analizador LL(1) con
   pila independiente y contra la agrupación de las expresiones escrita a mano.
   Así la prueba no es circular: un árbol esperado equivocado no pasa aunque el
   parser produzca el mismo.

Si la gramática cambia, los árboles esperados se regeneran con main.py:

    python main.py tests/validos/valido1_produccion_lotes.cft --salida tests/validos/valido1_produccion_lotes.txt
"""

import ast
import unittest
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from src.lexer.lexer import AnalizadorLexico
from src.parser.parser import Parser, TablaLL1
from src.parser.visualizacion import texto_arbol

RAIZ = Path(__file__).resolve().parent.parent
VALIDOS = RAIZ / "tests" / "validos"

PROGRAMAS = ["valido1_produccion_lotes", "valido2_precio_venta", "valido3_secado_marquesina",
             "valido4_clasificacion_anidada", "valido5_precedencia", "valido6_bloques_vacios"]

# Gramática final (factorizacion.md, sección 6): lado derecho de cada regla.
# Se escribe aquí, a mano, para validar los árboles sin depender del parser.
GRAMATICA = {
    "P1": ["INICIO", "<sentencias>", "FIN"],
    "R1": ["<sentencia>", "<sentencias>"], "R2": [],
    "P4": ["<declaracion>"], "P5": ["<asignacion>"], "P6": ["<salida>"],
    "P7": ["<condicional>"], "P8": ["<ciclo>"],
    "D1": ["DATO", "ID", "ASIGNACION", "<expresion>", "PUNTO_COMA"],
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
    "A1": ["ID", "ASIGNACION", "<expresion>", "PUNTO_COMA"],
    "M1": ["MOSTRAR", "PAR_ABRE", "<argumento>", "PAR_CIERRA", "PUNTO_COMA"],
    "M2": ["<expresion>"], "M3": ["CADENA"],
    "F4": ["SI", "PAR_ABRE", "<expresion>", "PAR_CIERRA", "ENTONCES",
           "<sentencias>", "<condicional_prima>"],
    "F5": ["FIN"], "F6": ["SINO", "<sentencias>", "FIN"],
    "L1": ["MIENTRAS", "PAR_ABRE", "<expresion>", "PAR_CIERRA", "HACER", "<sentencias>", "FIN"],
}

# Lado izquierdo de cada regla: el no terminal al que pertenece.
NO_TERMINAL = {
    "P1": "<programa>", "R1": "<sentencias>", "R2": "<sentencias>",
    **{r: "<sentencia>" for r in ["P4", "P5", "P6", "P7", "P8"]},
    "D1": "<declaracion>", "R3": "<expresion>", "R4": "<expresion_prima>", "R5": "<expresion_prima>",
    "R6": "<conjuncion>", "R7": "<conjuncion_prima>", "R8": "<conjuncion_prima>",
    "E5": "<negacion>", "E6": "<negacion>", "F1": "<comparacion>",
    "F2": "<comparacion_prima>", "F3": "<comparacion_prima>",
    **{r: "<op_rel>" for r in ["E9", "E10", "E11", "E12", "E13", "E14"]},
    "R9": "<suma>", "R10": "<suma_prima>", "R11": "<suma_prima>", "R12": "<suma_prima>",
    "R13": "<termino>", "R14": "<termino_prima>", "R15": "<termino_prima>", "R16": "<termino_prima>",
    **{r: "<factor>" for r in ["E21", "E22", "E23", "E24"]},
    "A1": "<asignacion>", "M1": "<salida>", "M2": "<argumento>", "M3": "<argumento>",
    "F4": "<condicional>", "F5": "<condicional_prima>", "F6": "<condicional_prima>", "L1": "<ciclo>",
}


# ----------------------------------------------------------------------
# Lectura del árbol esperado desde el .txt, sin usar el parser
# ----------------------------------------------------------------------

@dataclass
class NodoTexto:
    simbolo: str
    regla: Optional[str] = None
    lexema: Optional[str] = None
    hijos: List["NodoTexto"] = field(default_factory=list)


def leer_arbol(texto):
    """Reconstruye el árbol a partir de las líneas con sangría.

    La profundidad de cada línea es la columna donde empieza su etiqueta,
    dividida entre 4 (cada nivel ocupa 4 caracteres de ramas o espacios).
    """
    pila = []
    raiz = None
    for linea in texto.splitlines():
        inicio = len(linea) - len(linea.lstrip(" │├└─"))
        profundidad, etiqueta = inicio // 4, linea[inicio:]
        if etiqueta.startswith("<"):
            simbolo, regla = etiqueta[:-1].split(" [")
            nodo = NodoTexto(simbolo, regla=regla)
        elif etiqueta == "ε":
            nodo = NodoTexto("ε")
        else:
            tipo, lexema = etiqueta.split(" ", 1)
            nodo = NodoTexto(tipo, lexema=ast.literal_eval(lexema))
        del pila[profundidad:]
        if pila:
            pila[-1].hijos.append(nodo)
        else:
            raiz = nodo
        pila.append(nodo)
    return raiz


def preorden(nodo):
    pendientes = [nodo]
    while pendientes:
        actual = pendientes.pop()
        yield actual
        pendientes.extend(reversed(actual.hijos))


def referencia_ll1(tabla, tipos):
    """Analizador LL(1) con pila (sección 11 de GIC-6). Devuelve las reglas o None si rechaza."""
    pila, i, reglas = ["EOF", "<programa>"], 0, []
    tipos = list(tipos) + ["EOF"]
    while pila:
        cima = pila.pop()
        if cima.startswith("<"):
            regla = tabla.regla(cima, tipos[i])
            if regla is None:
                return None
            reglas.append(regla)
            pila.extend(reversed(GRAMATICA[regla]))
        elif cima == tipos[i]:
            i += 1
        else:
            return None
    return reglas


# ----------------------------------------------------------------------
# Agrupación de una expresión, a partir del árbol
# ----------------------------------------------------------------------

OPERADOR = {"O": "o", "Y": "y", "SUMA": "+", "RESTA": "-", "MULT": "*", "DIV": "/",
            "MENOR": "<", "MAYOR": ">", "MENOR_IGUAL": "<=", "MAYOR_IGUAL": ">=",
            "IGUAL": "==", "DIFERENTE": "!="}


def agrupar(nodo):
    """La expresión con un paréntesis por cada operación, según el árbol.

    Las cadenas _prima se recorren de izquierda a derecha y cada operador se
    agrupa con lo acumulado a su izquierda: así se lee la asociatividad por la
    izquierda en el árbol de GIC-4 (sección 7.2 de recursividad.md).
    """
    s = nodo.simbolo
    if s == "<factor>":
        if nodo.regla == "E21":
            return agrupar(nodo.hijos[1])                  # el paréntesis del texto
        return nodo.hijos[0].lexema
    if s == "<negacion>":
        if nodo.regla == "E5":
            return f"(no {agrupar(nodo.hijos[1])})"
        return agrupar(nodo.hijos[0])
    if s == "<comparacion>":
        izquierda, resto = agrupar(nodo.hijos[0]), nodo.hijos[1]
        if resto.regla == "F2":
            operador = OPERADOR[resto.hijos[0].hijos[0].simbolo]
            return f"({izquierda} {operador} {agrupar(resto.hijos[1])})"
        return izquierda
    # <expresion>, <conjuncion>, <suma> y <termino>: primero y luego la cadena _prima.
    acumulado, resto = agrupar(nodo.hijos[0]), nodo.hijos[1]
    while resto.hijos[0].simbolo != "ε":
        acumulado = f"({acumulado} {OPERADOR[resto.hijos[0].simbolo]} {agrupar(resto.hijos[1])})"
        resto = resto.hijos[2]
    return acumulado


def expresion_de(raiz, variable):
    """El nodo <expresion> de la declaración «dato variable = …;»."""
    for nodo in preorden(raiz):
        if nodo.simbolo == "<declaracion>" and nodo.hijos[1].lexema == variable:
            return nodo.hijos[3]
    raise KeyError(variable)


def esperado(nombre):
    return (VALIDOS / f"{nombre}.txt").read_text(encoding="utf-8")


# ----------------------------------------------------------------------
# Pruebas
# ----------------------------------------------------------------------

class PruebaParser(unittest.TestCase):
    """El parser produce exactamente el árbol esperado, sin errores."""

    def test_archivos(self):
        self.assertEqual(sorted(p.stem for p in VALIDOS.glob("*.cft")), PROGRAMAS)
        self.assertEqual(sorted(p.stem for p in VALIDOS.glob("*.txt")), PROGRAMAS)

    def test_arbol_igual_al_esperado(self):
        for nombre in PROGRAMAS:
            with self.subTest(programa=nombre):
                lexer = AnalizadorLexico()
                parser = Parser(lexer.analizar_archivo(VALIDOS / f"{nombre}.cft"))
                raiz = parser.analizar()
                self.assertEqual(lexer.errores, [])
                self.assertEqual(parser.errores, [])
                self.assertEqual(texto_arbol(raiz), esperado(nombre))


class PruebaArbolEsperado(unittest.TestCase):
    """Cada árbol esperado es correcto por sí mismo (sin usar el parser)."""

    def test_cada_nodo_sigue_su_regla(self):
        for nombre in PROGRAMAS:
            with self.subTest(programa=nombre):
                raiz = leer_arbol(esperado(nombre))
                self.assertEqual((raiz.simbolo, raiz.regla), ("<programa>", "P1"))
                for nodo in preorden(raiz):
                    if nodo.regla is not None:
                        self.assertEqual(nodo.simbolo, NO_TERMINAL[nodo.regla], nodo.simbolo)
                        lado_derecho = GRAMATICA[nodo.regla] or ["ε"]
                        self.assertEqual([h.simbolo for h in nodo.hijos], lado_derecho,
                                         f"{nodo.simbolo} [{nodo.regla}]")
                    else:
                        self.assertEqual(nodo.hijos, [])

    def test_las_hojas_son_el_programa(self):
        lexer = AnalizadorLexico()
        for nombre in PROGRAMAS:
            with self.subTest(programa=nombre):
                tokens = lexer.analizar_archivo(VALIDOS / f"{nombre}.cft")[:-1]   # sin EOF
                hojas = [n for n in preorden(leer_arbol(esperado(nombre))) if n.lexema is not None]
                self.assertEqual([(h.simbolo, h.lexema) for h in hojas],
                                 [(t.tipo, t.lexema) for t in tokens])

    def test_reglas_iguales_al_analizador_ll1(self):
        # El orden de las reglas en el árbol (preorden) es la derivación más a
        # la izquierda; debe coincidir con la que aplica el analizador con pila.
        lexer, tabla = AnalizadorLexico(), TablaLL1()
        for nombre in PROGRAMAS:
            with self.subTest(programa=nombre):
                tipos = [t.tipo for t in lexer.analizar_archivo(VALIDOS / f"{nombre}.cft")[:-1]]
                reglas = [n.regla for n in preorden(leer_arbol(esperado(nombre))) if n.regla]
                self.assertEqual(reglas, referencia_ll1(tabla, tipos))


class PruebaCobertura(unittest.TestCase):

    def test_todas_las_reglas_al_menos_una_vez(self):
        usadas = set()
        for nombre in PROGRAMAS:
            usadas |= {n.regla for n in preorden(leer_arbol(esperado(nombre))) if n.regla}
        reglas = set(TablaLL1().celdas.values())
        self.assertEqual(len(reglas), 46)
        self.assertEqual(reglas - usadas, set(), "reglas sin usar")
        self.assertEqual(set(GRAMATICA), reglas)

    def test_cada_programa_aporta_reglas(self):
        # Ningún programa sobra: cada uno usa al menos 28 reglas distintas.
        for nombre in PROGRAMAS:
            with self.subTest(programa=nombre):
                reglas = {n.regla for n in preorden(leer_arbol(esperado(nombre))) if n.regla}
                self.assertGreaterEqual(len(reglas), 28)


class PruebaPrecedencia(unittest.TestCase):
    """La agrupación de las expresiones, escrita a mano, coincide con el árbol esperado."""

    CASOS = {
        ("valido5_precedencia", "listo"):
            "((((a + (b * c)) - ((a - b) / 2)) > c) o ((no (a < b)) y (c != 0)))",
        ("valido5_precedencia", "doble"):
            "(no (no (a == 4)))",
        ("valido5_precedencia", "mixto"):
            "(((((a + b) * (c - 1)) / 3) >= 12) y ((b <= a) o (a == c)))",
        ("valido1_produccion_lotes", "total"):
            "((lote_a + lote_b) + lote_c)",
        ("valido1_produccion_lotes", "ajuste"):
            "((((lote_a - lote_b) * 2) + (lote_c / 4)) - 0.75)",
    }

    def test_agrupacion(self):
        for (nombre, variable), agrupacion in self.CASOS.items():
            with self.subTest(programa=nombre, variable=variable):
                raiz = leer_arbol(esperado(nombre))
                self.assertEqual(agrupar(expresion_de(raiz, variable)), agrupacion)

    def test_listo_usa_todos_los_niveles(self):
        # o, y, no, relacionales, + -, * / y paréntesis en una sola expresión.
        raiz = leer_arbol(esperado("valido5_precedencia"))
        reglas = {n.regla for n in preorden(expresion_de(raiz, "listo")) if n.regla}
        for regla in ["R4", "R7", "E5", "F2", "R10", "R11", "R14", "R15", "E21"]:
            self.assertIn(regla, reglas)


if __name__ == "__main__":
    unittest.main()
