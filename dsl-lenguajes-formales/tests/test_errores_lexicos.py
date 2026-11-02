"""Pruebas del manejo de errores léxicos (LXR-2).

El analizador registra cada error con su símbolo, línea y columna, y continúa
con el símbolo siguiente para listar todos los errores del archivo.

Ejecutar desde la raíz del repositorio:

    python -m unittest tests.test_errores_lexicos -v
"""

import io
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from src.lexer.lexer import AnalizadorLexico, ErrorLexico, main

RAIZ = Path(__file__).resolve().parent.parent
EJEMPLOS = RAIZ / "ejemplos"
ERRORES = RAIZ / "tests" / "errores"


def resumen(errores):
    """(símbolo, línea, columna) de cada error, en orden."""
    return [(e.simbolo, e.linea, e.columna) for e in errores]


class PruebaContinuar(unittest.TestCase):
    """Después de un error, el análisis sigue y se listan todos."""

    def setUp(self):
        self.lexer = AnalizadorLexico()

    def test_varios_errores_en_una_linea(self):
        tokens = self.lexer.analizar("dato Kilos = 2,5;")
        self.assertEqual(resumen(self.lexer.errores), [("K", 1, 6), (",", 1, 15)])
        self.assertEqual([t.tipo for t in tokens],
                         ["DATO", "ID", "ASIGNACION", "ENTERO", "ENTERO", "PUNTO_COMA", "EOF"])

    def test_errores_en_varias_lineas(self):
        self.lexer.analizar("x = 1;\n  y = @;\n\n_z = 2;")
        self.assertEqual(resumen(self.lexer.errores), [("@", 2, 7), ("_", 4, 1)])

    def test_fin_de_linea_windows(self):
        self.lexer.analizar("a\r\nB\r\nc = !;")
        self.assertEqual(resumen(self.lexer.errores), [("B", 2, 1), ("!", 3, 5)])

    def test_simbolos_seguidos_fuera_del_alfabeto(self):
        # Un error por símbolo: cada uno tiene su propia posición.
        self.lexer.analizar("CAFE")
        self.assertEqual(resumen(self.lexer.errores),
                         [("C", 1, 1), ("A", 1, 2), ("F", 1, 3), ("E", 1, 4)])

    def test_los_tokens_siguientes_conservan_su_posicion(self):
        tokens = self.lexer.analizar("dato año = 1;")
        posiciones = [(t.tipo, t.lexema, t.columna) for t in tokens[:-1]]
        self.assertEqual(posiciones, [("DATO", "dato", 1), ("ID", "a", 6), ("O", "o", 8),
                                      ("ASIGNACION", "=", 10), ("ENTERO", "1", 12),
                                      ("PUNTO_COMA", ";", 13)])

    def test_retroceso_y_error(self):
        # 12.x: ENTERO 12 por retroceso, error en el punto y después ID x.
        tokens = self.lexer.analizar("12.x")
        self.assertEqual([(t.tipo, t.lexema) for t in tokens[:-1]], [("ENTERO", "12"), ("ID", "x")])
        self.assertEqual(resumen(self.lexer.errores), [(".", 1, 3)])

    def test_cadena_sin_cerrar(self):
        # Traza 5 de la Fase 1: el error queda en la comilla inicial.
        tokens = self.lexer.analizar('x = "secar\ny = 1;')
        error = self.lexer.errores[0]
        self.assertEqual((error.simbolo, error.linea, error.columna, error.leido),
                         ('"', 1, 5, '"secar'))
        self.assertEqual(len(self.lexer.errores), 1)
        self.assertEqual(tokens[-5].linea, 2)          # la línea 2 se analiza normalmente

    def test_los_errores_se_reinician_en_cada_analisis(self):
        self.lexer.analizar("!")
        self.lexer.analizar("x = 1;")
        self.assertEqual(self.lexer.errores, [])

    def test_mensaje(self):
        self.lexer.analizar('K !\n"ab')
        mensajes = [str(e) for e in self.lexer.errores]
        self.assertEqual(mensajes, [
            "Error léxico en la línea 1, columna 1, símbolo 'K': no pertenece al alfabeto Σ.",
            "Error léxico en la línea 1, columna 3, símbolo '!': no forma ningún token.",
            "Error léxico en la línea 2, columna 1, símbolo '\"': '\"ab' no forma ningún token."])

    def test_modo_que_se_detiene(self):
        lexer = AnalizadorLexico(detener_en_error=True)
        with self.assertRaises(ErrorLexico):
            lexer.analizar("x = 1; !")


class PruebaArchivosConErrores(unittest.TestCase):
    """Los 3 archivos de tests/errores: todos los errores, en orden."""

    ESPERADO = {
        "lexico1_fuera_del_alfabeto.cft": [
            ("K", 3, 10), ("ñ", 4, 11), (",", 5, 22), ("{", 6, 32), ("}", 8, 5)],
        "lexico2_simbolos_sin_token.cft": [
            ("_", 3, 10), (".", 4, 19), (".", 5, 20), ("!", 6, 9), (".", 9, 15)],
        "lexico3_cadenas_y_comentarios.cft": [
            ('"', 4, 13), ("R", 5, 7), ('"', 6, 13), (":", 6, 18), ('"', 6, 25), ("@", 7, 21)],
    }

    def setUp(self):
        self.lexer = AnalizadorLexico()

    def test_errores_esperados(self):
        for nombre, esperado in self.ESPERADO.items():
            with self.subTest(archivo=nombre):
                tokens = self.lexer.analizar_archivo(ERRORES / nombre)
                self.assertEqual(resumen(self.lexer.errores), esperado)
                self.assertEqual(tokens[-1].tipo, "EOF")       # el análisis llega al final

    def test_linea_de_comandos(self):
        salida, errores = io.StringIO(), io.StringIO()
        with redirect_stdout(salida), redirect_stderr(errores):
            codigo = main([str(ERRORES / "lexico2_simbolos_sin_token.cft")])
        self.assertEqual(codigo, 1)
        self.assertIn("5 errores léxicos:", errores.getvalue())
        self.assertIn("línea 6, columna 9, símbolo '!'", errores.getvalue())


class PruebaSinErrores(unittest.TestCase):
    """Los programas de ejemplo siguen sin errores léxicos."""

    def test_programas_de_ejemplo(self):
        lexer = AnalizadorLexico()
        for nombre in ["ejemplo1_produccion.cft", "ejemplo2_clasificacion.cft",
                       "ejemplo3_secado.cft"]:
            with self.subTest(programa=nombre):
                lexer.analizar_archivo(EJEMPLOS / nombre)
                self.assertEqual(lexer.errores, [])

    def test_linea_de_comandos_sin_errores(self):
        salida = io.StringIO()
        with redirect_stdout(salida):
            codigo = main([str(EJEMPLOS / "ejemplo3_secado.cft")])
        self.assertEqual(codigo, 0)
        self.assertIn("Sin errores léxicos.", salida.getvalue())


if __name__ == "__main__":
    unittest.main()
