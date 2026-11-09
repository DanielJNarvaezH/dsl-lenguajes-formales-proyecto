"""Programas con errores: salida esperada de main.py (TST-2).

Ejecutar desde la raíz del repositorio:

    python -m unittest tests.test_errores -v

tests/errores/ tiene 6 programas con errores (.cft): 3 con errores léxicos
(LXR-2) y 3 con errores sintácticos (PAR-4). Junto a cada uno está su salida
esperada (.txt): el listado de errores que muestra main.py, tal cual.

Como en TST-1, las pruebas comprueban dos cosas:

1. main.py produce exactamente la salida esperada (prueba de regresión).
2. La salida esperada es correcta por sí misma, sin usar el analizador: cada
   error está en la línea y la columna donde el archivo fuente tiene el símbolo
   reportado, los totales cuadran y la lista de errores coincide con la escrita
   a mano en la sección 3 de docs/fase3/pruebas_errores.md.

Si cambia el formato de los mensajes, las salidas esperadas se regeneran con:

    python -m tests.test_errores --regenerar
"""

import ast
import io
import subprocess
import sys
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from main import main

RAIZ = Path(__file__).resolve().parent.parent
ERRORES = RAIZ / "tests" / "errores"

PROGRAMAS = ["lexico1_fuera_del_alfabeto", "lexico2_simbolos_sin_token",
             "lexico3_cadenas_y_comentarios", "sintactico1_expresiones",
             "sintactico2_sentencias", "sintactico3_bloques"]

# Errores de cada programa, escritos a mano (sección 3 de pruebas_errores.md):
# (clase, línea, columna, texto encontrado). Clase L es léxico y S sintáctico;
# el texto es el símbolo del error léxico o el lexema del token del sintáctico
# (None si es el fin del archivo).
ESPERADOS_A_MANO = {
    "lexico1_fuera_del_alfabeto": [
        ("L", 3, 10, "K"), ("L", 4, 11, "ñ"), ("L", 5, 22, ","), ("L", 6, 32, "{"), ("L", 8, 5, "}"),
        ("S", 4, 12, "o"), ("S", 5, 23, "5")],
    "lexico2_simbolos_sin_token": [
        ("L", 3, 10, "_"), ("L", 4, 19, "."), ("L", 5, 20, "."), ("L", 6, 9, "!"), ("L", 9, 15, "."),
        ("S", 9, 16, "x")],
    "lexico3_cadenas_y_comentarios": [
        ("L", 4, 13, '"'), ("L", 5, 7, "R"), ("L", 6, 13, '"'), ("L", 6, 18, ":"), ("L", 6, 25, '"'),
        ("L", 7, 21, "@"),
        ("S", 4, 20, "de"), ("S", 5, 15, "el"), ("S", 5, 18, "secador"), ("S", 6, 20, "norte"),
        ("S", 8, 1, "fin")],
    "sintactico1_expresiones": [
        ("S", 4, 28, ";"), ("S", 5, 26, "*"), ("S", 6, 20, "<"), ("S", 10, 5, "mostrar")],
    "sintactico2_sentencias": [
        ("S", 3, 10, "si"), ("S", 4, 13, "12"), ("S", 5, 29, "entonces"), ("S", 8, 13, ")"),
        ("S", 9, 5, "sino")],
    "sintactico3_bloques": [
        ("S", 4, 8, "dia"), ("S", 4, 17, "entonces"), ("S", 15, 1, None)],
}


def ejecutar_main(ruta):
    """main.py sobre el archivo: (código, stdout, stderr)."""
    salida, errores = io.StringIO(), io.StringIO()
    with redirect_stdout(salida), redirect_stderr(errores):
        codigo = main([str(ruta)])
    return codigo, salida.getvalue(), errores.getvalue()


def esperado(nombre):
    return (ERRORES / f"{nombre}.txt").read_text(encoding="utf-8")


def numero_tras(texto, prefijo):
    """El número entero que sigue a prefijo en texto."""
    resto = texto[texto.index(prefijo) + len(prefijo):]
    digitos = ""
    for caracter in resto:
        if not caracter.isdigit():
            break
        digitos += caracter
    return int(digitos)


def leer_errores(texto):
    """Lee el listado de errores (.txt) sin usar el analizador.

    Devuelve una lista de (clase, línea, columna, texto encontrado) y el total
    que declara la última línea.
    """
    errores, total = [], None
    for linea in texto.splitlines():
        linea = linea.strip()
        if linea.startswith("Error léxico"):
            # ... símbolo 'x': ...  (el símbolo es un solo carácter, escrito con repr)
            inicio = linea.index("símbolo ") + len("símbolo ")
            simbolo = ast.literal_eval(linea[inicio:inicio + 3])
            errores.append(("L", numero_tras(linea, "línea "), numero_tras(linea, "columna "), simbolo))
        elif linea.startswith("Error sintáctico"):
            encontrado = linea[linea.index("se encontró ") + len("se encontró "):]
            if encontrado.startswith("el fin del archivo"):
                lexema = None
            else:
                lexema = ast.literal_eval(encontrado.rsplit(" (", 1)[0])
            errores.append(("S", numero_tras(linea, "línea "), numero_tras(linea, "columna "), lexema))
        elif "en total" in linea:
            total = numero_tras(linea, "")
    return errores, total


class PruebaArchivos(unittest.TestCase):

    def test_un_txt_por_programa(self):
        self.assertEqual(sorted(p.stem for p in ERRORES.glob("*.cft")), PROGRAMAS)
        self.assertEqual(sorted(p.stem for p in ERRORES.glob("*.txt")), PROGRAMAS)

    def test_hay_de_los_dos_tipos(self):
        # 3 programas con errores léxicos y 3 solo con errores sintácticos.
        lexicos = [n for n in PROGRAMAS if any(c == "L" for c, *_ in ESPERADOS_A_MANO[n])]
        solo_sintacticos = [n for n in PROGRAMAS if all(c == "S" for c, *_ in ESPERADOS_A_MANO[n])]
        self.assertEqual((len(lexicos), len(solo_sintacticos)), (3, 3))


class PruebaMain(unittest.TestCase):
    """main.py produce exactamente la salida esperada: errores, sin árbol."""

    def test_salida_igual_a_la_esperada(self):
        for nombre in PROGRAMAS:
            with self.subTest(programa=nombre):
                codigo, salida, errores = ejecutar_main(ERRORES / f"{nombre}.cft")
                self.assertEqual(codigo, 1)
                self.assertEqual(salida, "")                    # no se muestra el árbol
                self.assertEqual(errores, esperado(nombre))


class PruebaSalidaEsperada(unittest.TestCase):
    """Cada salida esperada es correcta por sí misma (sin usar el analizador)."""

    def test_coincide_con_la_lista_a_mano(self):
        for nombre in PROGRAMAS:
            with self.subTest(programa=nombre):
                errores, _ = leer_errores(esperado(nombre))
                self.assertEqual(errores, ESPERADOS_A_MANO[nombre])

    def test_cada_error_apunta_a_su_simbolo_en_el_fuente(self):
        for nombre in PROGRAMAS:
            with self.subTest(programa=nombre):
                lineas = (ERRORES / f"{nombre}.cft").read_text(encoding="utf-8").splitlines()
                for clase, linea, columna, texto in leer_errores(esperado(nombre))[0]:
                    if texto is None:                           # fin del archivo
                        self.assertEqual(linea, len(lineas) + 1)
                        self.assertEqual(columna, 1)
                    else:
                        fuente = lineas[linea - 1]
                        self.assertEqual(fuente[columna - 1:columna - 1 + len(texto)], texto,
                                         f"{clase} {linea}:{columna} en {fuente!r}")

    def test_totales_y_orden(self):
        for nombre in PROGRAMAS:
            with self.subTest(programa=nombre):
                texto = esperado(nombre)
                errores, total = leer_errores(texto)
                self.assertEqual(total, len(errores))
                lexicos = [e for e in errores if e[0] == "L"]
                sintacticos = [e for e in errores if e[0] == "S"]
                # Primero los léxicos y después los sintácticos, cada grupo en orden.
                self.assertEqual(errores, lexicos + sintacticos)
                self.assertEqual(lexicos, sorted(lexicos, key=lambda e: e[1:3]))
                self.assertEqual(sintacticos, sorted(sintacticos, key=lambda e: e[1:3]))
                for grupo, nombre_grupo in [(lexicos, "léxico"), (sintacticos, "sintáctico")]:
                    if grupo:
                        self.assertIn(f"{len(grupo)} error", texto)
                        self.assertIn(nombre_grupo, texto)
                self.assertTrue(texto.endswith("no se muestra el árbol de derivación.\n"))


class PruebaEjecutarPruebas(unittest.TestCase):
    """El script ejecutar_pruebas.py corre módulos de la suite y resume el resultado."""

    def correr(self, *argumentos):
        return subprocess.run([sys.executable, str(RAIZ / "ejecutar_pruebas.py"), *argumentos],
                              capture_output=True, cwd=RAIZ)

    def test_un_modulo(self):
        resultado = self.correr("arbol")
        salida = resultado.stdout.decode("utf-8")
        self.assertEqual(resultado.returncode, 0, resultado.stderr.decode("utf-8", "replace"))
        self.assertIn("tests.test_arbol", salida)
        self.assertIn("Todas las pruebas pasaron", salida)

    def test_modulo_inexistente(self):
        resultado = self.correr("no_existe")
        self.assertNotEqual(resultado.returncode, 0)


def regenerar():
    """Vuelve a escribir los .txt con la salida actual de main.py (UTF-8, saltos \\n)."""
    for nombre in PROGRAMAS:
        _, _, errores = ejecutar_main(ERRORES / f"{nombre}.cft")
        with open(ERRORES / f"{nombre}.txt", "w", encoding="utf-8", newline="\n") as archivo:
            archivo.write(errores)
        print(f"Regenerado tests/errores/{nombre}.txt")


if __name__ == "__main__":
    if "--regenerar" in sys.argv:
        regenerar()
    else:
        unittest.main()
