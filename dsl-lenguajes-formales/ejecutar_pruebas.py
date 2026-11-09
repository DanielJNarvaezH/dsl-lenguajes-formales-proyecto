"""Ejecuta la suite de pruebas del proyecto y muestra un resumen por módulo (TST-2).

Uso, desde la carpeta del proyecto:

    python ejecutar_pruebas.py                 # toda la suite
    python ejecutar_pruebas.py -v              # con el nombre de cada prueba
    python ejecutar_pruebas.py lexer parser_expresiones   # solo algunos módulos

Un módulo se puede nombrar completo (tests.test_lexer) o corto (lexer).
Termina con código 0 si todas las pruebas pasan y con 1 si alguna falla.

Es lo mismo que «python -m unittest discover -s tests -t .», más el resumen.
Solo usa la biblioteca estándar (unittest).
"""

import argparse
import importlib.util
import sys
import time
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent

# Qué prueba cada módulo, para el resumen. Un módulo nuevo que no esté aquí
# aparece igual, con su nombre.
DESCRIPCION = {
    "tests.test_lexer": "Analizador léxico (LXR-1)",
    "tests.test_errores_lexicos": "Errores léxicos (LXR-2)",
    "tests.test_arbol": "Árbol de derivación y contrato (PAR-1)",
    "tests.test_parser_expresiones": "Parser: expresiones (PAR-2)",
    "tests.test_parser_sentencias": "Parser: programa y sentencias (PAR-3)",
    "tests.test_errores_sintacticos": "Errores sintácticos (PAR-4)",
    "tests.test_visualizacion": "Visualización del árbol (ARB-1)",
    "tests.test_main": "Punto de entrada main.py (PAR-5)",
    "tests.test_validos": "Programas válidos (TST-1)",
    "tests.test_errores": "Programas con errores (TST-2)",
    "tests.test_documentacion": "Coherencia de la documentación (DOC-4)",
}


class ResultadoPorModulo(unittest.TextTestResult):
    """Resultado de unittest que además cuenta las pruebas de cada módulo."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.por_modulo = {}

    def _contador(self, prueba):
        modulo = type(prueba).__module__
        return self.por_modulo.setdefault(modulo, {"pruebas": 0, "fallas": 0, "omitidas": 0})

    def startTest(self, prueba):
        super().startTest(prueba)
        self._contador(prueba)["pruebas"] += 1

    def addFailure(self, prueba, error):
        super().addFailure(prueba, error)
        self._contador(prueba)["fallas"] += 1

    def addError(self, prueba, error):
        super().addError(prueba, error)
        self._contador(prueba)["fallas"] += 1

    def addSubTest(self, prueba, subprueba, error):
        super().addSubTest(prueba, subprueba, error)
        if error is not None:
            self._contador(prueba)["fallas"] += 1

    def addSkip(self, prueba, motivo):
        super().addSkip(prueba, motivo)
        self._contador(prueba)["omitidas"] += 1


def nombre_completo(modulo):
    """lexer -> tests.test_lexer; un nombre completo se deja igual."""
    return modulo if modulo.startswith("tests.") else f"tests.test_{modulo}"


def cargar(modulos):
    cargador = unittest.TestLoader()
    if not modulos:
        return cargador.discover(start_dir=str(RAIZ / "tests"), top_level_dir=str(RAIZ))
    return cargador.loadTestsFromNames([nombre_completo(m) for m in modulos])


def imprimir_resumen(resultado, segundos):
    print("\nResumen por módulo")
    print(f"{'Módulo':<32} {'Qué prueba':<40} {'Pruebas':>7} {'Fallas':>6} {'Omitidas':>8}")
    for modulo in sorted(resultado.por_modulo):
        c = resultado.por_modulo[modulo]
        print(f"{modulo:<32} {DESCRIPCION.get(modulo, ''):<40} "
              f"{c['pruebas']:>7} {c['fallas']:>6} {c['omitidas']:>8}")
    total = resultado.testsRun
    fallas = len(resultado.failures) + len(resultado.errors)
    print(f"\n{total} pruebas en {segundos:.1f} s: {total - fallas - len(resultado.skipped)} correctas, "
          f"{fallas} con fallas y {len(resultado.skipped)} omitidas.")
    if resultado.wasSuccessful():
        print("Todas las pruebas pasaron.")
    else:
        print("Hay pruebas con fallas: el detalle está arriba.")


def main(argv=None):
    for flujo in (sys.stdout, sys.stderr):
        if hasattr(flujo, "reconfigure"):
            flujo.reconfigure(encoding="utf-8")
    argumentos = argparse.ArgumentParser(
        prog="python ejecutar_pruebas.py",
        description="Ejecuta la suite de pruebas de Cafetal y muestra un resumen por módulo.")
    argumentos.add_argument("modulos", nargs="*",
                            help="módulos a ejecutar, por ejemplo lexer o tests.test_lexer (por defecto, todos)")
    argumentos.add_argument("-v", "--detalle", action="store_true",
                            help="mostrar el nombre y el resultado de cada prueba")
    args = argumentos.parse_args(argv)

    # Para que «from src…» y «from main…» funcionen desde cualquier carpeta.
    sys.path.insert(0, str(RAIZ))
    faltantes = [m for m in args.modulos if importlib.util.find_spec(nombre_completo(m)) is None]
    if faltantes:
        print(f"No existe el módulo de pruebas: {', '.join(nombre_completo(m) for m in faltantes)}.",
              file=sys.stderr)
        return 2
    suite = cargar(args.modulos)

    ejecutor = unittest.TextTestRunner(resultclass=ResultadoPorModulo,
                                       verbosity=2 if args.detalle else 1, stream=sys.stdout)
    inicio = time.perf_counter()
    resultado = ejecutor.run(suite)
    imprimir_resumen(resultado, time.perf_counter() - inicio)
    return 0 if resultado.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main())
