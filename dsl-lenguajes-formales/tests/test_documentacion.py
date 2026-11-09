"""Coherencia del documento de la Fase 3 con el código (DOC-4).

Ejecutar desde la raíz del repositorio:

    python -m unittest tests.test_documentacion -v

Comprueba que docs/fase3/documento_fase3.md no quede desactualizado:

* la tabla regla BNF ↔ función de Python (sección 4.2) tiene exactamente las
  46 reglas de la tabla LL(1), con su producción y la función que la
  implementa en Parser;
* los archivos del proyecto que el documento nombra existen.
"""

import unittest
from pathlib import Path

from src.parser.parser import Parser, TablaLL1
from tests.test_validos import GRAMATICA, NO_TERMINAL

RAIZ = Path(__file__).resolve().parent.parent
DOCUMENTO = RAIZ / "docs" / "fase3" / "documento_fase3.md"


def tabla_reglas(texto):
    """Filas de la tabla de la sección 4.2: {regla: (producción, función)}."""
    seccion = texto[texto.index("### 4.2"):texto.index("### 4.3")]
    filas = {}
    for linea in seccion.splitlines():
        celdas = [c.strip() for c in linea.strip().strip("|").split("|")]
        if len(celdas) == 3 and celdas[2].startswith("`"):
            filas[celdas[0]] = (celdas[1].strip("`"), celdas[2].strip("`"))
    return filas


def rutas_nombradas(texto):
    """Textos entre comillas invertidas que parecen archivos del proyecto."""
    rutas = set()
    partes = texto.split("`")
    for i in range(1, len(partes), 2):
        candidato = partes[i]
        nombre = candidato.rsplit("/", 1)[-1]
        if (" " not in candidato and "." in nombre[1:]
                and candidato.endswith((".py", ".csv", ".cft", ".md", ".drawio"))):
            rutas.add(candidato)
    return rutas


class PruebaTablaReglas(unittest.TestCase):

    def setUp(self):
        self.filas = tabla_reglas(DOCUMENTO.read_text(encoding="utf-8"))

    def test_estan_las_46_reglas(self):
        self.assertEqual(set(self.filas), set(TablaLL1().celdas.values()))
        self.assertEqual(len(self.filas), 46)

    def test_produccion_correcta(self):
        for regla, (produccion, _) in self.filas.items():
            with self.subTest(regla=regla):
                lado = " ".join(GRAMATICA[regla]) or "ε"
                self.assertEqual(produccion, f"{NO_TERMINAL[regla]} ::= {lado}")

    def test_cada_regla_tiene_su_funcion(self):
        for regla, (produccion, funcion) in self.filas.items():
            with self.subTest(regla=regla):
                self.assertEqual(funcion, NO_TERMINAL[regla].strip("<>"))
                metodo = getattr(Parser, funcion, None)
                self.assertTrue(callable(metodo), funcion)
                self.assertIn(regla, metodo.__doc__)


class PruebaArchivosNombrados(unittest.TestCase):

    def test_existen(self):
        # Una ruta puede estar escrita desde la raíz del proyecto o solo con
        # el nombre del archivo, junto a los documentos o a las tablas.
        bases = [RAIZ, RAIZ / "docs" / "fase3", RAIZ / "docs" / "fase2",
                 RAIZ / "src" / "lexer", RAIZ / "src" / "parser"]
        faltantes = [ruta for ruta in rutas_nombradas(DOCUMENTO.read_text(encoding="utf-8"))
                     if not any((base / ruta).exists() for base in bases)]
        self.assertEqual(faltantes, [])


if __name__ == "__main__":
    unittest.main()
