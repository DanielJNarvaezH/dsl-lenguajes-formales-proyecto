"""Pruebas del punto de entrada main.py (PAR-5).

Ejecutar desde la raíz del repositorio:

    python -m unittest tests.test_main -v

La mayoría llama a main() en el mismo proceso. Las de PruebaEjecucionReal
ejecutan "python main.py" como lo haría un usuario: desde otra carpeta y con
la salida redirigida.
"""

import ast
import io
import os
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from main import main
from src.lexer.lexer import AnalizadorLexico
from src.parser.parser import Parser
from src.parser.visualizacion import a_dot, graphviz_disponible, texto_arbol, texto_derivacion

RAIZ = Path(__file__).resolve().parent.parent
EJEMPLOS = RAIZ / "ejemplos"
ERRORES = RAIZ / "tests" / "errores"
MAIN = RAIZ / "main.py"


def ejecutar(*argumentos):
    """Llama a main() y devuelve (código, stdout, stderr)."""
    salida, errores = io.StringIO(), io.StringIO()
    with redirect_stdout(salida), redirect_stderr(errores):
        codigo = main([str(a) for a in argumentos])
    return codigo, salida.getvalue(), errores.getvalue()


def arbol_de(ruta):
    return Parser(AnalizadorLexico().analizar_archivo(ruta)).analizar()


class PruebaProgramaValido(unittest.TestCase):

    def test_muestra_el_arbol_de_cada_ejemplo(self):
        resumen = {"ejemplo1_produccion.cft": "66 tokens y 174 reglas aplicadas",
                   "ejemplo2_clasificacion.cft": "62 tokens y 134 reglas aplicadas",
                   "ejemplo3_secado.cft": "57 tokens y 165 reglas aplicadas"}
        for nombre, texto in resumen.items():
            with self.subTest(programa=nombre):
                codigo, salida, errores = ejecutar(EJEMPLOS / nombre)
                self.assertEqual(codigo, 0)
                self.assertEqual(salida, texto_arbol(arbol_de(EJEMPLOS / nombre)))
                self.assertIn(f"Análisis correcto: {texto}.", errores)

    def test_tokens(self):
        codigo, salida, _ = ejecutar(EJEMPLOS / "ejemplo3_secado.cft", "--tokens")
        self.assertEqual(codigo, 0)
        self.assertTrue(salida.startswith("Línea  Col  Token"))
        self.assertIn("57 tokens, más EOF.", salida)
        self.assertIn("<programa> [P1]", salida)                 # y después el árbol

    def test_derivacion(self):
        ruta = EJEMPLOS / "ejemplo1_produccion.cft"
        _, salida, _ = ejecutar(ruta, "--derivacion")
        self.assertTrue(salida.endswith(texto_derivacion(arbol_de(ruta))))

    def test_formato_del_arbol(self):
        ruta = EJEMPLOS / "ejemplo2_clasificacion.cft"
        _, salida, _ = ejecutar(ruta, "--ascii", "--posiciones")
        self.assertEqual(salida, texto_arbol(arbol_de(ruta), ascii=True, posiciones=True))

    def test_archivos_de_salida(self):
        ruta = EJEMPLOS / "ejemplo3_secado.cft"
        raiz = arbol_de(ruta)
        with tempfile.TemporaryDirectory() as carpeta:
            carpeta = Path(carpeta)
            codigo, _, _ = ejecutar(ruta, "--salida", carpeta / "arbol.txt",
                                    "--salida-derivacion", carpeta / "derivacion.txt",
                                    "--dot", carpeta / "arbol.dot")
            self.assertEqual(codigo, 0)
            self.assertEqual((carpeta / "arbol.txt").read_text(encoding="utf-8"), texto_arbol(raiz))
            self.assertEqual((carpeta / "derivacion.txt").read_text(encoding="utf-8"),
                             texto_derivacion(raiz))
            self.assertEqual((carpeta / "arbol.dot").read_text(encoding="utf-8"), a_dot(raiz))

    def test_imagen(self):
        with tempfile.TemporaryDirectory() as carpeta:
            ruta = Path(carpeta) / "arbol.png"
            codigo, _, errores = ejecutar(EJEMPLOS / "ejemplo3_secado.cft", "--png", ruta)
            self.assertEqual(codigo, 0)                          # la imagen es opcional
            if graphviz_disponible():
                self.assertEqual(ruta.read_bytes()[:8], b"\x89PNG\r\n\x1a\n")
            else:
                self.assertIn("Aviso: Graphviz no está instalado", errores)


class PruebaErrores(unittest.TestCase):

    def escribir(self, carpeta, texto):
        ruta = Path(carpeta) / "programa.cft"
        ruta.write_text(texto, encoding="utf-8")
        return ruta

    def test_errores_lexicos(self):
        ruta = ERRORES / "lexico2_simbolos_sin_token.cft"
        lexer = AnalizadorLexico()
        lexer.analizar_archivo(ruta)
        codigo, salida, errores = ejecutar(ruta)
        self.assertEqual((codigo, salida), (1, ""))               # sin árbol
        self.assertIn("5 errores léxicos:", errores)
        for error in lexer.errores:
            self.assertIn(f"  {error}\n", errores)
        self.assertIn("no se muestra el árbol de derivación", errores)

    def test_los_lexicos_van_antes_que_los_sintacticos(self):
        # lexico1: dato año = 2026; deja ID a y O o, que también es error sintáctico.
        _, _, errores = ejecutar(ERRORES / "lexico1_fuera_del_alfabeto.cft")
        self.assertIn("errores léxicos:", errores)
        self.assertIn("sintáctico", errores)
        self.assertLess(errores.index("errores léxicos:"), errores.index("Error sintáctico"))

    def test_errores_sintacticos(self):
        with tempfile.TemporaryDirectory() as carpeta:
            ruta = self.escribir(carpeta, "inicio\n  mientras (a) entonces fin\nfin\n")
            codigo, salida, errores = ejecutar(ruta, "--salida", Path(carpeta) / "arbol.txt")
            self.assertEqual((codigo, salida), (1, ""))
            self.assertIn("Error sintáctico en la línea 2, columna 16: se esperaba HACER "
                          "y se encontró 'entonces' (ENTONCES).", errores)
            self.assertNotIn("léxico", errores)
            self.assertFalse((Path(carpeta) / "arbol.txt").exists())   # con errores no se guarda

    def test_archivo_vacio(self):
        with tempfile.TemporaryDirectory() as carpeta:
            codigo, _, errores = ejecutar(self.escribir(carpeta, ""))
            self.assertEqual(codigo, 1)
            self.assertIn("se esperaba INICIO", errores)

    def test_tokens_aunque_haya_errores(self):
        _, salida, _ = ejecutar(ERRORES / "lexico3_cadenas_y_comentarios.cft", "--tokens")
        self.assertTrue(salida.startswith("Línea  Col  Token"))
        self.assertNotIn("<programa>", salida)


class PruebaEntrada(unittest.TestCase):

    def test_archivo_inexistente(self):
        codigo, _, errores = ejecutar(RAIZ / "no_existe.cft")
        self.assertEqual(codigo, 2)
        self.assertIn("no existe", errores)

    def test_carpeta(self):
        codigo, _, errores = ejecutar(EJEMPLOS)
        self.assertEqual(codigo, 2)
        self.assertIn("es una carpeta", errores)

    def test_archivo_que_no_es_utf8(self):
        with tempfile.TemporaryDirectory() as carpeta:
            ruta = Path(carpeta) / "latin1.cft"
            ruta.write_bytes("inicio mostrar(\"café\"); fin".encode("latin-1"))
            codigo, _, errores = ejecutar(ruta)
            self.assertEqual(codigo, 2)
            self.assertIn("no está guardado en UTF-8", errores)

    def test_sin_argumentos(self):
        with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as salida:
            main([])
        self.assertEqual(salida.exception.code, 2)


class PruebaEjecucionReal(unittest.TestCase):
    """python main.py, como lo ejecuta un usuario."""

    def correr(self, *argumentos, carpeta, entorno=None):
        return subprocess.run([sys.executable, str(MAIN), *map(str, argumentos)],
                              cwd=carpeta, capture_output=True,
                              env={**os.environ, **(entorno or {})})

    def test_desde_otra_carpeta(self):
        # Sin rutas fijas: funciona desde cualquier carpeta con rutas absolutas.
        with tempfile.TemporaryDirectory() as carpeta:
            resultado = self.correr(EJEMPLOS / "ejemplo3_secado.cft", carpeta=carpeta)
            self.assertEqual(resultado.returncode, 0, resultado.stderr.decode("utf-8", "replace"))
            self.assertTrue(resultado.stdout.decode("utf-8").startswith("<programa> [P1]"))

    def test_salida_redirigida_con_codificacion_de_windows(self):
        # Simula la salida redirigida en Windows (cp1252), que no tiene ε ni ├──.
        resultado = self.correr(EJEMPLOS / "ejemplo3_secado.cft", carpeta=RAIZ,
                                entorno={"PYTHONIOENCODING": "cp1252"})
        self.assertEqual(resultado.returncode, 0, resultado.stderr.decode("utf-8", "replace"))
        texto = resultado.stdout.decode("utf-8")
        self.assertIn("ε", texto)
        self.assertIn("├──", texto)


class PruebaRestricciones(unittest.TestCase):

    def setUp(self):
        self.arbol = ast.parse(MAIN.read_text(encoding="utf-8"))

    def test_no_importa_re(self):
        modulos = {alias.name for nodo in ast.walk(self.arbol) if isinstance(nodo, ast.Import)
                   for alias in nodo.names}
        modulos |= {nodo.module for nodo in ast.walk(self.arbol) if isinstance(nodo, ast.ImportFrom)}
        self.assertNotIn("re", modulos)

    def test_sin_rutas_fijas(self):
        # 1. Fuera de los docstrings, ningún texto fijo tiene separadores de ruta.
        docstrings = {id(nodo.body[0].value) for nodo in ast.walk(self.arbol)
                      if isinstance(nodo, (ast.Module, ast.FunctionDef)) and nodo.body
                      and isinstance(nodo.body[0], ast.Expr)
                      and isinstance(nodo.body[0].value, ast.Constant)}
        for nodo in ast.walk(self.arbol):
            if isinstance(nodo, ast.Constant) and isinstance(nodo.value, str) and id(nodo) not in docstrings:
                self.assertNotIn("/", nodo.value)
                self.assertNotIn("\\", nodo.value)
        # 2. Las funciones que abren o escriben archivos nunca reciben un texto
        #    fijo: la ruta siempre viene de los argumentos de la línea de comandos.
        lectoras = {"open", "Path", "analizar_archivo", "exportar_texto", "exportar_derivacion",
                    "exportar_dot", "exportar_imagen"}
        for nodo in ast.walk(self.arbol):
            if isinstance(nodo, ast.Call):
                nombre = getattr(nodo.func, "id", getattr(nodo.func, "attr", None))
                if nombre in lectoras:
                    for argumento in nodo.args:
                        self.assertFalse(isinstance(argumento, ast.Constant), ast.unparse(nodo))
                # 3. Ningún argumento de la línea de comandos tiene una ruta por defecto.
                if nombre == "add_argument":
                    self.assertNotIn("default", [k.arg for k in nodo.keywords], ast.unparse(nodo))

if __name__ == "__main__":
    unittest.main()
