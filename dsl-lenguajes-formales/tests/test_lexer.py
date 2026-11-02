"""Pruebas del analizador léxico dirigido por la matriz del AFD (LXR-1).

Ejecutar desde la raíz del repositorio:

    python -m unittest tests.test_lexer -v
"""

import ast
import unittest
from pathlib import Path

from src.lexer.lexer import AnalizadorLexico, ErrorLexico, TablaAFD
from src.lexer.tokens import CODIGOS

RAIZ = Path(__file__).resolve().parent.parent
EJEMPLOS = RAIZ / "ejemplos"


class PruebaTabla(unittest.TestCase):
    """La matriz cargada coincide con el AFD de la Fase 1."""

    @classmethod
    def setUpClass(cls):
        cls.tabla = TablaAFD()

    def test_dimensiones(self):
        self.assertEqual(len(self.tabla.delta), 72)          # q0–q71
        self.assertEqual(len(self.tabla.alfabeto), 55)       # |Σ| = 55
        self.assertEqual(self.tabla.estado_inicial, "q0")

    def test_estados_de_aceptacion(self):
        self.assertEqual(len(self.tabla.aceptacion), 68)
        no_aceptan = set(self.tabla.delta) - set(self.tabla.aceptacion)
        self.assertEqual(no_aceptan, {"q0", "q59", "q66", "q68"})

    def test_transiciones(self):
        self.assertEqual(self.tabla.total_transiciones, 1997)


class PruebaReconocimiento(unittest.TestCase):

    def setUp(self):
        self.lexer = AnalizadorLexico()

    def tipos(self, texto):
        return [t.tipo for t in self.lexer.analizar(texto)][:-1]   # sin EOF

    # Trazas 1 a 3 de la Fase 1
    def test_traza_sino(self):
        self.assertEqual(self.tipos("sino"), ["SINO"])

    def test_traza_id_con_digito_y_guion(self):
        self.assertEqual(self.tipos("lote_2"), ["ID"])

    def test_traza_decimal(self):
        self.assertEqual(self.tipos("11.5"), ["DECIMAL"])

    # Regla 1: lexema más largo
    def test_lexema_mas_largo(self):
        self.assertEqual(self.tipos("<= >= == != < > ="),
                         ["MENOR_IGUAL", "MAYOR_IGUAL", "IGUAL", "DIFERENTE",
                          "MENOR", "MAYOR", "ASIGNACION"])
        self.assertEqual(self.tipos("finca"), ["ID"])

    def test_sin_espacios(self):
        self.assertEqual(self.tipos("si(x<=2)"),
                         ["SI", "PAR_ABRE", "ID", "MENOR_IGUAL", "ENTERO", "PAR_CIERRA"])
        self.assertEqual(self.tipos("kilos-norte"), ["ID", "RESTA", "ID"])

    # Regla 2: palabra reservada sobre ID
    def test_palabras_reservadas(self):
        texto = "inicio fin dato si entonces sino mientras hacer mostrar y o no"
        self.assertEqual(self.tipos(texto),
                         ["INICIO", "FIN", "DATO", "SI", "ENTONCES", "SINO",
                          "MIENTRAS", "HACER", "MOSTRAR", "Y", "O", "NO"])

    def test_prefijos_y_extensiones_son_id(self):
        for texto in ["dat", "mos", "n", "datos", "siembra", "dato_1", "entonces2", "yo", "nos"]:
            with self.subTest(texto=texto):
                self.assertEqual(self.tipos(texto), ["ID"])

    # Regla 3: descarte
    def test_comentario_y_blancos_se_descartan(self):
        tokens = self.lexer.analizar("# total = kilos * 2;\n  x")
        self.assertEqual([t.tipo for t in tokens], ["ID", "EOF"])

    def test_descartables_si_se_piden(self):
        tipos = [t.tipo for t in self.lexer.analizar("# c\nx", incluir_descartables=True)]
        self.assertEqual(tipos, ["COMENTARIO", "BLANCO", "ID", "EOF"])

    def test_cadena(self):
        tokens = self.lexer.analizar('mostrar("secar de nuevo");')
        self.assertEqual(tokens[2].tipo, "CADENA")
        self.assertEqual(tokens[2].lexema, '"secar de nuevo"')


class PruebaPosiciones(unittest.TestCase):

    def setUp(self):
        self.lexer = AnalizadorLexico()

    def test_linea_y_columna(self):
        tokens = self.lexer.analizar("inicio\n  dato x = 1;\nfin")
        posiciones = [(t.tipo, t.linea, t.columna) for t in tokens]
        self.assertEqual(posiciones, [
            ("INICIO", 1, 1), ("DATO", 2, 3), ("ID", 2, 8), ("ASIGNACION", 2, 10),
            ("ENTERO", 2, 12), ("PUNTO_COMA", 2, 13), ("FIN", 3, 1), ("EOF", 3, 4)])

    def test_fin_de_linea_windows(self):
        tokens = self.lexer.analizar("a\r\nb\rc")
        self.assertEqual([(t.linea, t.columna) for t in tokens[:3]], [(1, 1), (2, 1), (3, 1)])

    def test_eof(self):
        tokens = self.lexer.analizar("")
        self.assertEqual([(t.tipo, t.codigo) for t in tokens], [("EOF", 99)])


class PruebaErrores(unittest.TestCase):
    """Comportamiento de LXR-1: el primer error detiene el análisis.

    Desde LXR-2 el analizador continúa por defecto; estas pruebas usan
    detener_en_error=True. El modo que continúa se prueba en
    tests/test_errores_lexicos.py.
    """

    def setUp(self):
        self.lexer = AnalizadorLexico(detener_en_error=True)

    def error(self, texto):
        with self.assertRaises(ErrorLexico) as contexto:
            self.lexer.analizar(texto)
        return contexto.exception

    def test_traza_exclamacion_sola(self):            # Traza 4 de la Fase 1
        error = self.error("!x")
        self.assertEqual((error.simbolo, error.linea, error.columna), ("!", 1, 1))

    def test_traza_cadena_sin_cerrar(self):           # Traza 5 de la Fase 1
        error = self.error('x = "secar\n')
        self.assertEqual((error.simbolo, error.columna, error.leido), ('"', 5, '"secar'))

    def test_simbolo_fuera_del_alfabeto(self):
        error = self.error("dato Kilos = 1;")
        self.assertEqual((error.simbolo, error.columna, error.en_alfabeto), ("K", 6, False))

    def test_retroceso_al_ultimo_estado_de_aceptacion(self):
        # 12.x: llega a q66 (no acepta), retrocede a q65 y emite ENTERO 12;
        # después el punto solo no forma ningún token.
        generador = self.lexer.tokens("12.x")
        primero = next(generador)
        self.assertEqual((primero.tipo, primero.lexema), ("ENTERO", "12"))
        with self.assertRaises(ErrorLexico) as contexto:
            next(generador)
        self.assertEqual((contexto.exception.simbolo, contexto.exception.columna), (".", 3))


class PruebaProgramasDeEjemplo(unittest.TestCase):
    """Tabla 20 de la Fase 1: 0 errores y 66, 62 y 57 tokens."""

    ESPERADO = {"ejemplo1_produccion.cft": 66,
                "ejemplo2_clasificacion.cft": 62,
                "ejemplo3_secado.cft": 57}

    def setUp(self):
        self.lexer = AnalizadorLexico()

    def test_cantidad_de_tokens(self):
        for nombre, cantidad in self.ESPERADO.items():
            with self.subTest(programa=nombre):
                tokens = self.lexer.analizar_archivo(EJEMPLOS / nombre)
                self.assertEqual(len(tokens) - 1, cantidad)
                self.assertEqual(tokens[-1].tipo, "EOF")

    def test_aparecen_las_32_categorias(self):
        vistas = set()
        for nombre in self.ESPERADO:
            vistas |= {t.tipo for t in self.lexer.analizar_archivo(EJEMPLOS / nombre, True)}
        self.assertEqual(vistas - {"EOF"}, set(CODIGOS) - {"EOF"})

    def test_linea_7_del_secado(self):
        tokens = self.lexer.analizar_archivo(EJEMPLOS / "ejemplo3_secado.cft")
        linea7 = [t.tipo for t in tokens if t.linea == 7]
        self.assertEqual(linea7, ["SI", "PAR_ABRE", "ID", "IGUAL", "ENTERO", "O", "NO",
                                  "PAR_ABRE", "ID", "MAYOR", "ENTERO", "PAR_CIERRA",
                                  "PAR_CIERRA", "ENTONCES"])


class PruebaRestricciones(unittest.TestCase):
    """El código del analizador cumple las restricciones de la tarea."""

    def test_no_importa_re(self):
        for archivo in ["lexer.py", "tokens.py"]:
            arbol = ast.parse((RAIZ / "src" / "lexer" / archivo).read_text(encoding="utf-8"))
            modulos = {alias.name for nodo in ast.walk(arbol) if isinstance(nodo, ast.Import)
                       for alias in nodo.names}
            modulos |= {nodo.module for nodo in ast.walk(arbol) if isinstance(nodo, ast.ImportFrom)}
            with self.subTest(archivo=archivo):
                self.assertNotIn("re", modulos)

    def test_no_compara_con_lexemas_ni_tokens(self):
        # Ningún literal de lexema o nombre de token aparece en una comparación.
        codigo = (RAIZ / "src" / "lexer" / "lexer.py").read_text(encoding="utf-8")
        arbol = ast.parse(codigo)
        prohibidos = set(CODIGOS) | {"inicio", "fin", "dato", "si", "entonces", "sino",
                                     "mientras", "hacer", "mostrar", "y", "o", "no"}
        for nodo in ast.walk(arbol):
            if isinstance(nodo, ast.Compare):
                for parte in [nodo.left, *nodo.comparators]:
                    if isinstance(parte, ast.Constant):
                        self.assertNotIn(parte.value, prohibidos)


if __name__ == "__main__":
    unittest.main()
