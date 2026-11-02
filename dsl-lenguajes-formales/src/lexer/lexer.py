"""Analizador léxico de Cafetal dirigido por la matriz de transiciones (LXR-1 y LXR-2).

El analizador no contiene reglas propias para reconocer tokens: carga la
matriz del AFD de la Fase 1 (tabla_afd.csv) y la recorre símbolo por símbolo.
Cada decisión sale de la tabla:

* qué estado sigue después de leer un símbolo (celda de la matriz);
* si el estado es de aceptación y qué token devuelve (columna "token");
* cuándo se rechaza (celda vacía: δ(q, a) no está definida; el AFD no tiene
  estado sumidero, por indicación de la profesora).

Reglas de reconocimiento (Fase 1, documento_fase1.md):

1. Lexema más largo: se avanza mientras exista transición y se recuerda el
   último estado de aceptación visitado. Al detenerse, se retrocede a ese
   estado y se emite su token.
2. Prioridad de palabra reservada sobre ID: ya está dentro del AFD (por
   ejemplo, q15 devuelve SI y q64 devuelve ID), así que no se consulta
   ninguna lista de palabras reservadas.
3. Descarte: COMENTARIO y BLANCO se reconocen, pero no se entregan.

Errores léxicos (LXR-2): cuando ningún prefijo desde la posición actual forma
un token (tercer caso de la Tabla 17 de la Fase 1), se registra el error con
su símbolo, línea y columna, y el análisis continúa desde el símbolo
siguiente. Así se listan todos los errores del archivo en una sola pasada.

No se usa el módulo re ni comparaciones con lexemas o nombres de tokens.

Uso desde la terminal, en la raíz del repositorio:

    python -m src.lexer.lexer ejemplos/ejemplo3_secado.cft
    python -m src.lexer.lexer ejemplos/ejemplo3_secado.cft --todos
"""

import argparse
import csv
import sys
from dataclasses import dataclass
from pathlib import Path

from .tokens import CODIGOS, DESCARTABLES, EOF

# Ruta de la matriz: junto a este archivo, sin rutas fijas del equipo.
RUTA_TABLA = Path(__file__).with_name("tabla_afd.csv")

# En la cabecera del CSV, los blancos tienen un nombre en lugar del carácter.
NOMBRES_BLANCOS = {"ESP": " ", "TAB": "\t", "LF": "\n", "CR": "\r"}


class ErrorTabla(Exception):
    """La matriz de transiciones no tiene el formato esperado."""


class ErrorLexico(Exception):
    """Ningún prefijo del texto, desde la posición actual, forma un token.

    Corresponde al tercer caso de la Tabla 17 de la Fase 1: δ(q, a) vacía,
    q ∉ F y no se visitó ningún estado de aceptación. El error se reporta en
    el primer símbolo del lexema.

    * simbolo: primer símbolo del lexema, donde se reporta el error;
    * linea y columna: posición de ese símbolo (desde 1);
    * leido: lo que el AFD alcanzó a recorrer antes de quedarse sin transición;
    * en_alfabeto: si el símbolo pertenece a Σ.
    """

    def __init__(self, simbolo, linea, columna, leido, en_alfabeto):
        self.simbolo = simbolo
        self.linea = linea
        self.columna = columna
        self.leido = leido
        self.en_alfabeto = en_alfabeto
        super().__init__(self.mensaje())

    def mensaje(self):
        if not self.en_alfabeto:
            motivo = "no pertenece al alfabeto Σ"
        elif len(self.leido) > 1:
            motivo = f"{self.leido!r} no forma ningún token"
        else:
            motivo = "no forma ningún token"
        return (f"Error léxico en la línea {self.linea}, columna {self.columna}, "
                f"símbolo {self.simbolo!r}: {motivo}.")


@dataclass(frozen=True)
class Token:
    """Contrato entre el analizador léxico y el sintáctico."""

    tipo: str
    lexema: str
    linea: int
    columna: int

    @property
    def codigo(self):
        return CODIGOS[self.tipo]

    def __str__(self):
        return f"{self.linea}:{self.columna} {self.tipo}({self.codigo}) {self.lexema!r}"


class TablaAFD:
    """Matriz de transiciones del AFD global de Cafetal (72 estados × 55 símbolos)."""

    def __init__(self, ruta=RUTA_TABLA):
        self.ruta = Path(ruta)
        self.delta = {}        # estado -> {símbolo: estado siguiente}
        self.aceptacion = {}   # estado de aceptación -> token que devuelve
        self.alfabeto = set()
        self.estado_inicial = None
        self._cargar()

    def _cargar(self):
        with open(self.ruta, encoding="utf-8", newline="") as archivo:
            filas = list(csv.reader(archivo))
        if len(filas) < 2:
            raise ErrorTabla(f"{self.ruta}: la tabla está vacía")
        cabecera = filas[0]
        if cabecera[0] != "estado" or cabecera[-1] != "token":
            raise ErrorTabla(f"{self.ruta}: la cabecera debe empezar con 'estado' y terminar con 'token'")
        simbolos = [NOMBRES_BLANCOS.get(nombre, nombre) for nombre in cabecera[1:-1]]
        self.alfabeto = set(simbolos)

        for fila in filas[1:]:
            if len(fila) != len(cabecera):
                raise ErrorTabla(f"{self.ruta}: la fila de {fila[0]!r} no tiene {len(cabecera)} columnas")
            estado, celdas, token = fila[0], fila[1:-1], fila[-1]
            # Solo se guardan las celdas no vacías: una celda vacía es rechazo.
            self.delta[estado] = {s: destino for s, destino in zip(simbolos, celdas) if destino}
            if token:
                self.aceptacion[estado] = token
        self.estado_inicial = filas[1][0]

        for estado, salidas in self.delta.items():
            for destino in salidas.values():
                if destino not in self.delta:
                    raise ErrorTabla(f"{self.ruta}: {estado} lleva a {destino!r}, que no es un estado")
        for token in self.aceptacion.values():
            if token not in CODIGOS:
                raise ErrorTabla(f"{self.ruta}: el token {token!r} no está en el catálogo")

    def transicion(self, estado, simbolo):
        """δ(estado, símbolo), o None si la celda está vacía."""
        return self.delta[estado].get(simbolo)

    def token_de(self, estado):
        """Token que devuelve el estado, o None si no es de aceptación."""
        return self.aceptacion.get(estado)

    @property
    def total_transiciones(self):
        return sum(len(salidas) for salidas in self.delta.values())


class AnalizadorLexico:
    """Recorre el texto con el AFD y entrega la secuencia de tokens.

    Los errores léxicos de la última llamada quedan en self.errores, en el
    orden en que aparecen en el texto. Con detener_en_error=True se vuelve al
    comportamiento de LXR-1: el primer error lanza ErrorLexico.
    """

    def __init__(self, tabla=None, detener_en_error=False):
        self.tabla = tabla if tabla is not None else TablaAFD()
        self.detener_en_error = detener_en_error
        self.errores = []

    def tokens(self, texto, incluir_descartables=False):
        """Genera los tokens del texto, terminando con EOF.

        Con incluir_descartables=True también entrega COMENTARIO y BLANCO.
        Los símbolos con error léxico no producen token: se registran en
        self.errores y el análisis sigue con el símbolo siguiente.
        """
        self.errores = []
        posicion, linea, columna = 0, 1, 1
        while posicion < len(texto):
            fin, tipo, leido_hasta = self._lexema_mas_largo(texto, posicion)
            if tipo is None:
                fin = self._manejar_error(texto, posicion, leido_hasta, linea, columna)
                linea, columna = _avanzar(texto[posicion:fin], linea, columna)
                posicion = fin
                continue
            lexema = texto[posicion:fin]
            if incluir_descartables or tipo not in DESCARTABLES:
                yield Token(tipo, lexema, linea, columna)
            linea, columna = _avanzar(lexema, linea, columna)
            posicion = fin
        yield Token(EOF, "", linea, columna)

    def analizar(self, texto, incluir_descartables=False):
        """Lista completa de tokens del texto. Los errores quedan en self.errores."""
        return list(self.tokens(texto, incluir_descartables))

    def analizar_archivo(self, ruta, incluir_descartables=False):
        """Lista de tokens de un archivo .cft (UTF-8)."""
        with open(ruta, encoding="utf-8-sig", newline="") as archivo:
            return self.analizar(archivo.read(), incluir_descartables)

    def _lexema_mas_largo(self, texto, inicio):
        """Recorre el AFD desde q0 a partir de texto[inicio].

        Devuelve (fin, tipo, leido_hasta):
        * fin y tipo: fin del lexema y token del último estado de aceptación
          visitado (tipo es None si no se visitó ninguno);
        * leido_hasta: posición donde el AFD se detuvo, para los mensajes de error.
        """
        estado = self.tabla.estado_inicial
        posicion = inicio
        ultimo_fin, ultimo_tipo = inicio, None
        while posicion < len(texto):
            siguiente = self.tabla.transicion(estado, texto[posicion])
            if siguiente is None:            # celda vacía: el AFD ya no avanza
                break
            estado = siguiente
            posicion += 1
            tipo = self.tabla.token_de(estado)
            if tipo is not None:             # estado de aceptación: se recuerda
                ultimo_fin, ultimo_tipo = posicion, tipo
        return ultimo_fin, ultimo_tipo, posicion

    def _manejar_error(self, texto, inicio, leido_hasta, linea, columna):
        """Registra el error léxico en el primer símbolo del lexema (LXR-2).

        Devuelve la posición desde donde continúa el análisis: el símbolo
        siguiente al del error. No se salta nada más, porque el analizador no
        sabe qué "significa" cada estado del AFD (por ejemplo, que q68 es una
        cadena abierta): saltar hasta otro punto sería una regla propia fuera
        de la tabla. Con detener_en_error=True lanza el error, como en LXR-1.
        """
        simbolo = texto[inicio]
        leido = texto[inicio:max(leido_hasta, inicio + 1)]
        error = ErrorLexico(simbolo, linea, columna, leido, simbolo in self.tabla.alfabeto)
        if self.detener_en_error:
            raise error
        self.errores.append(error)
        return inicio + 1


def _avanzar(lexema, linea, columna):
    """Línea y columna después de un lexema. \\r\\n cuenta como un solo salto."""
    anterior = ""
    for caracter in lexema:
        if caracter == "\n" and anterior == "\r":
            pass                              # ya se contó en el \r
        elif caracter in "\r\n":
            linea, columna = linea + 1, 1
        else:
            columna += 1
        anterior = caracter
    return linea, columna


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="python -m src.lexer.lexer",
        description="Analizador léxico de Cafetal dirigido por la matriz del AFD.")
    parser.add_argument("archivo", help="archivo fuente .cft")
    parser.add_argument("--todos", action="store_true",
                        help="mostrar también COMENTARIO y BLANCO")
    parser.add_argument("--tabla", default=str(RUTA_TABLA),
                        help="ruta de la matriz de transiciones (por defecto, tabla_afd.csv)")
    args = parser.parse_args(argv)

    analizador = AnalizadorLexico(TablaAFD(args.tabla))
    try:
        tokens = analizador.analizar_archivo(args.archivo, args.todos)
    except FileNotFoundError:
        print(f"No se encontró el archivo {args.archivo!r}.", file=sys.stderr)
        return 2

    print(f"{'Línea':>5} {'Col':>4}  {'Token':<12} {'Cód':>3}  Lexema")
    for token in tokens:
        print(f"{token.linea:>5} {token.columna:>4}  {token.tipo:<12} {token.codigo:>3}  {token.lexema!r}")
    entregados = sum(1 for t in tokens if t.tipo not in DESCARTABLES and t.tipo != EOF)
    print(f"\n{entregados} tokens para el analizador sintáctico, más EOF.")

    if analizador.errores:
        print(f"\n{len(analizador.errores)} errores léxicos:", file=sys.stderr)
        for error in analizador.errores:
            print(f"  {error}", file=sys.stderr)
        return 1
    print("Sin errores léxicos.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
