"""Pruebas de la visualización del árbol de derivación (ARB-1).

Ejecutar desde la raíz del repositorio:

    python -m unittest tests.test_visualizacion -v

La verificación principal compara la salida con lo hecho a mano en el proyecto:
el árbol de la sección 5 de arbol.md (PAR-1), la traza de la sección 11.1 de
primero_siguiente_ll1.md (GIC-6), la derivación a mano de la sección 4 de
visualizacion.md y el árbol de 10 - 4 - 2 dibujado en draw.io en GIC-4.
"""

import ast
import io
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from src.lexer.lexer import AnalizadorLexico
from src.parser.arbol import Nodo
from src.parser.parser import Parser
from src.parser.visualizacion import (a_dot, derivacion, exportar_dot, exportar_imagen,
                                      exportar_texto, graphviz_disponible, lineas_arbol, main,
                                      texto_arbol, texto_derivacion)

RAIZ = Path(__file__).resolve().parent.parent
EJEMPLOS = RAIZ / "ejemplos"
ERRORES = RAIZ / "tests" / "errores"


def arbol(texto):
    parser = Parser(AnalizadorLexico().analizar(texto))
    raiz = parser.analizar()
    return raiz, parser.errores


# Árbol de la sección 5 de docs/fase3/arbol.md (PAR-1), copiado tal cual.
ARBOL_MD = """\
<programa> [P1]
├── INICIO 'inicio'
├── <sentencias> [R1]
│   ├── <sentencia> [P5]
│   │   └── <asignacion> [A1]
│   │       ├── ID 'x'
│   │       ├── ASIGNACION '='
│   │       ├── <expresion> [R3]
│   │       │   ├── <conjuncion> [R6]
│   │       │   │   ├── <negacion> [E6]
│   │       │   │   │   └── <comparacion> [F1]
│   │       │   │   │       ├── <suma> [R9]
│   │       │   │   │       │   ├── <termino> [R13]
│   │       │   │   │       │   │   ├── <factor> [E23]
│   │       │   │   │       │   │   │   └── ENTERO '1'
│   │       │   │   │       │   │   └── <termino_prima> [R16]
│   │       │   │   │       │   │       └── ε
│   │       │   │   │       │   └── <suma_prima> [R12]
│   │       │   │   │       │       └── ε
│   │       │   │   │       └── <comparacion_prima> [F3]
│   │       │   │   │           └── ε
│   │       │   │   └── <conjuncion_prima> [R8]
│   │       │   │       └── ε
│   │       │   └── <expresion_prima> [R5]
│   │       │       └── ε
│   │       └── PUNTO_COMA ';'
│   └── <sentencias> [R2]
│       └── ε
└── FIN 'fin'
"""

# Reglas de la traza a mano de la sección 11.1 de primero_siguiente_ll1.md
# (GIC-6) para inicio x = a - 1; fin, en el orden de la columna Acción.
REGLAS_TRAZA_GIC6 = ["P1", "R1", "P5", "A1", "R3", "R6", "E6", "F1", "R9", "R13", "E22",
                     "R16", "R11", "R13", "E23", "R16", "R12", "F3", "R8", "R5", "R2"]

# Derivación más a la izquierda de inicio x = a - 1; fin, hecha a mano
# (sección 4 de docs/fase3/visualizacion.md).
_C = "<comparacion_prima> <conjuncion_prima> <expresion_prima> PUNTO_COMA <sentencias> FIN"
DERIVACION_A_MANO = [
    (None, "<programa>"),
    ("P1", "INICIO <sentencias> FIN"),
    ("R1", "INICIO <sentencia> <sentencias> FIN"),
    ("P5", "INICIO <asignacion> <sentencias> FIN"),
    ("A1", "INICIO ID⟨x⟩ ASIGNACION <expresion> PUNTO_COMA <sentencias> FIN"),
    ("R3", "INICIO ID⟨x⟩ ASIGNACION <conjuncion> <expresion_prima> PUNTO_COMA <sentencias> FIN"),
    ("R6", "INICIO ID⟨x⟩ ASIGNACION <negacion> <conjuncion_prima> <expresion_prima> PUNTO_COMA <sentencias> FIN"),
    ("E6", "INICIO ID⟨x⟩ ASIGNACION <comparacion> <conjuncion_prima> <expresion_prima> PUNTO_COMA <sentencias> FIN"),
    ("F1", "INICIO ID⟨x⟩ ASIGNACION <suma> " + _C),
    ("R9", "INICIO ID⟨x⟩ ASIGNACION <termino> <suma_prima> " + _C),
    ("R13", "INICIO ID⟨x⟩ ASIGNACION <factor> <termino_prima> <suma_prima> " + _C),
    ("E22", "INICIO ID⟨x⟩ ASIGNACION ID⟨a⟩ <termino_prima> <suma_prima> " + _C),
    ("R16", "INICIO ID⟨x⟩ ASIGNACION ID⟨a⟩ <suma_prima> " + _C),
    ("R11", "INICIO ID⟨x⟩ ASIGNACION ID⟨a⟩ RESTA <termino> <suma_prima> " + _C),
    ("R13", "INICIO ID⟨x⟩ ASIGNACION ID⟨a⟩ RESTA <factor> <termino_prima> <suma_prima> " + _C),
    ("E23", "INICIO ID⟨x⟩ ASIGNACION ID⟨a⟩ RESTA ENTERO⟨1⟩ <termino_prima> <suma_prima> " + _C),
    ("R16", "INICIO ID⟨x⟩ ASIGNACION ID⟨a⟩ RESTA ENTERO⟨1⟩ <suma_prima> " + _C),
    ("R12", "INICIO ID⟨x⟩ ASIGNACION ID⟨a⟩ RESTA ENTERO⟨1⟩ " + _C),
    ("F3", "INICIO ID⟨x⟩ ASIGNACION ID⟨a⟩ RESTA ENTERO⟨1⟩ <conjuncion_prima> <expresion_prima> PUNTO_COMA <sentencias> FIN"),
    ("R8", "INICIO ID⟨x⟩ ASIGNACION ID⟨a⟩ RESTA ENTERO⟨1⟩ <expresion_prima> PUNTO_COMA <sentencias> FIN"),
    ("R5", "INICIO ID⟨x⟩ ASIGNACION ID⟨a⟩ RESTA ENTERO⟨1⟩ PUNTO_COMA <sentencias> FIN"),
    ("R2", "INICIO ID⟨x⟩ ASIGNACION ID⟨a⟩ RESTA ENTERO⟨1⟩ PUNTO_COMA FIN"),
]

# Árbol de 10 - 4 - 2 desde <suma>, dibujado en draw.io en GIC-4
# (docs/fase2/arboles/gic4_recursividad.drawio, página Comparacion, árbol derecho).
SUMA_GIC4 = """\
<suma> [R9]
├── <termino> [R13]
│   ├── <factor> [E23]
│   │   └── ENTERO '10'
│   └── <termino_prima> [R16]
│       └── ε
└── <suma_prima> [R11]
    ├── RESTA '-'
    ├── <termino> [R13]
    │   ├── <factor> [E23]
    │   │   └── ENTERO '4'
    │   └── <termino_prima> [R16]
    │       └── ε
    └── <suma_prima> [R11]
        ├── RESTA '-'
        ├── <termino> [R13]
        │   ├── <factor> [E23]
        │   │   └── ENTERO '2'
        │   └── <termino_prima> [R16]
        │       └── ε
        └── <suma_prima> [R12]
            └── ε
"""


class PruebaTexto(unittest.TestCase):

    def test_coincide_con_el_arbol_de_arbol_md(self):
        raiz, _ = arbol("inicio x = 1; fin")
        self.assertEqual(texto_arbol(raiz), ARBOL_MD)

    def test_coincide_con_el_arbol_dibujado_en_gic4(self):
        raiz, _ = arbol("inicio x = 10 - 4 - 2; fin")
        suma = next(n for n in raiz.recorrer() if n.simbolo == "<suma>")
        self.assertEqual(texto_arbol(suma), SUMA_GIC4)

    def test_una_linea_por_nodo_y_sangria_por_profundidad(self):
        raiz, _ = arbol((EJEMPLOS / "ejemplo3_secado.cft").read_text(encoding="utf-8"))
        lineas = lineas_arbol(raiz, ascii=True)
        self.assertEqual(len(lineas), len(list(raiz.recorrer())))
        # Con ramas ASCII, cada nivel ocupa 4 caracteres antes de la etiqueta.
        pendientes, profundidades = [(raiz, 0)], []
        while pendientes:
            nodo, nivel = pendientes.pop()
            profundidades.append(nivel)
            pendientes.extend((h, nivel + 1) for h in reversed(nodo.hijos))
        for linea, nivel in zip(lineas, profundidades):
            # La etiqueta empieza en la columna 4 × nivel, justo después de su rama.
            self.assertNotEqual(linea[4 * nivel], " ", linea)
            if nivel:
                self.assertIn(linea[4 * nivel - 4:4 * nivel], ("|-- ", "`-- "), linea)

    def test_ascii(self):
        raiz, _ = arbol('inicio mostrar("hola"); fin')
        texto = texto_arbol(raiz, ascii=True)
        for caracter in "├└│─":
            self.assertNotIn(caracter, texto)
        self.assertIn("`-- FIN 'fin'", texto)
        self.assertIn("CADENA '\"hola\"'", texto)

    def test_posiciones(self):
        raiz, _ = arbol("inicio\n  x = 1;\nfin")
        texto = texto_arbol(raiz, posiciones=True)
        self.assertIn("ID 'x' 2:3", texto)
        self.assertIn("FIN 'fin' 3:1", texto)

    def test_arbol_con_errores(self):
        raiz, errores = arbol("inicio x = (a + ; fin")
        self.assertEqual(len(errores), 1)
        texto = texto_arbol(raiz)
        self.assertIn("<termino> [ERROR]", texto)
        self.assertIn("PAR_CIERRA (faltante)", texto)

    def test_arbol_muy_profundo(self):
        raiz = actual = Nodo.no_terminal("<sentencias>", "R1")
        for _ in range(5000):
            actual = actual.agregar(Nodo.no_terminal("<sentencias>", "R1"))
        actual.agregar(Nodo.vacio())
        self.assertEqual(len(lineas_arbol(raiz)), 5002)
        self.assertEqual(len(derivacion(raiz)), 5002)

    def test_exportar_texto(self):
        raiz, _ = arbol("inicio x = 1; fin")
        with tempfile.TemporaryDirectory() as carpeta:
            ruta = Path(carpeta) / "arbol.txt"
            exportar_texto(raiz, ruta)
            self.assertEqual(ruta.read_text(encoding="utf-8"), ARBOL_MD)


class PruebaDerivacion(unittest.TestCase):

    def setUp(self):
        self.raiz, _ = arbol("inicio x = a - 1; fin")

    def test_reglas_de_la_traza_de_gic6(self):
        self.assertEqual([regla for regla, _ in derivacion(self.raiz)[1:]], REGLAS_TRAZA_GIC6)

    def test_coincide_con_la_derivacion_a_mano(self):
        self.assertEqual(derivacion(self.raiz), DERIVACION_A_MANO)

    def test_texto(self):
        lineas = texto_derivacion(self.raiz).splitlines()
        self.assertEqual(len(lineas), 22)
        self.assertEqual(lineas[0].strip(), "<programa>")
        self.assertTrue(lineas[1].startswith("⇒ P1"))
        self.assertTrue(lineas[-1].endswith("ENTERO⟨1⟩ PUNTO_COMA FIN"))

    def test_programas_de_ejemplo(self):
        # Una forma por regla y la última es el programa, en el orden del texto.
        lexer = AnalizadorLexico()
        for archivo in sorted(EJEMPLOS.glob("*.cft")):
            with self.subTest(programa=archivo.name):
                tokens = lexer.analizar_archivo(archivo)
                raiz = Parser(tokens).analizar()
                pasos = derivacion(raiz)
                self.assertEqual([r for r, _ in pasos[1:]], raiz.derivacion_izquierda())
                # La última forma sentencial es el programa: sus tokens, sin EOF.
                esperado = " ".join(f"{t.tipo}⟨{t.lexema}⟩" if t.tipo in ("ID", "ENTERO", "DECIMAL", "CADENA")
                                    else t.tipo for t in tokens[:-1])
                self.assertEqual(pasos[-1][1], esperado)


class PruebaGraphviz(unittest.TestCase):

    def setUp(self):
        self.raiz, _ = arbol('inicio si (a > 0) entonces mostrar("ok"); fin fin')

    def test_dot(self):
        dot = a_dot(self.raiz)
        nodos = len(list(self.raiz.recorrer()))
        self.assertTrue(dot.startswith("digraph arbol {"))
        self.assertEqual(dot.count(" -> "), nodos - 1)
        self.assertEqual(sum(1 for l in dot.splitlines() if "[label=" in l), nodos)
        self.assertIn('\\"ok\\"', dot)                     # comillas de la cadena escapadas

    def test_exportar_dot(self):
        with tempfile.TemporaryDirectory() as carpeta:
            ruta = Path(carpeta) / "arbol.dot"
            exportar_dot(self.raiz, ruta)
            self.assertEqual(ruta.read_text(encoding="utf-8"), a_dot(self.raiz))

    @unittest.skipUnless(graphviz_disponible(), "Graphviz no está instalado (opcional)")
    def test_imagen(self):
        with tempfile.TemporaryDirectory() as carpeta:
            ruta = Path(carpeta) / "arbol.png"
            exportar_imagen(self.raiz, ruta)
            self.assertEqual(ruta.read_bytes()[:8], b"\x89PNG\r\n\x1a\n")


class PruebaLineaDeComandos(unittest.TestCase):

    def ejecutar(self, *argumentos):
        salida, errores = io.StringIO(), io.StringIO()
        with redirect_stdout(salida), redirect_stderr(errores):
            codigo = main(list(argumentos))
        return codigo, salida.getvalue(), errores.getvalue()

    def test_programa_valido(self):
        with tempfile.TemporaryDirectory() as carpeta:
            ruta = Path(carpeta) / "secado.txt"
            ruta_derivacion = Path(carpeta) / "derivacion.txt"
            codigo, salida, _ = self.ejecutar(str(EJEMPLOS / "ejemplo3_secado.cft"),
                                              "--salida", str(ruta), "--derivacion",
                                              "--salida-derivacion", str(ruta_derivacion))
            self.assertEqual(codigo, 0)
            self.assertTrue(ruta_derivacion.read_text(encoding="utf-8").startswith(" " * 7 + "<programa>"))
            self.assertTrue(salida.startswith("<programa> [P1]\n"))
            self.assertIn("⇒ P1", salida)
            self.assertTrue(ruta.read_text(encoding="utf-8").startswith("<programa> [P1]\n"))

    def test_con_errores_no_muestra_el_arbol(self):
        codigo, salida, errores = self.ejecutar(str(ERRORES / "sintactico2_sentencias.cft"))
        self.assertEqual(codigo, 1)
        self.assertEqual(salida, "")
        self.assertIn("5 errores; no se muestra el árbol", errores)

    def test_archivo_inexistente(self):
        codigo, _, errores = self.ejecutar("no_existe.cft")
        self.assertEqual(codigo, 2)


class PruebaRestricciones(unittest.TestCase):

    def test_no_importa_re(self):
        arbol_ = ast.parse((RAIZ / "src" / "parser" / "visualizacion.py").read_text(encoding="utf-8"))
        modulos = {alias.name for nodo in ast.walk(arbol_) if isinstance(nodo, ast.Import)
                   for alias in nodo.names}
        modulos |= {nodo.module for nodo in ast.walk(arbol_) if isinstance(nodo, ast.ImportFrom)}
        self.assertNotIn("re", modulos)


if __name__ == "__main__":
    unittest.main()
