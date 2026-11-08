"""Punto de entrada del analizador de Cafetal (PAR-5).

Recibe la ruta de un archivo .cft, ejecuta el analizador léxico (LXR-1 y LXR-2)
y el sintáctico (PAR-2 a PAR-4), y muestra el árbol de derivación (ARB-1) o el
listado de errores, como pide el enunciado de la Fase 3.

Uso, desde la carpeta del proyecto:

    python main.py ejemplos/ejemplo3_secado.cft
    python main.py ejemplos/ejemplo3_secado.cft --tokens --derivacion
    python main.py ejemplos/ejemplo3_secado.cft --salida arbol.txt
    python main.py tests/errores/lexico1_fuera_del_alfabeto.cft

No hay rutas fijas: el archivo .cft y las rutas de salida se reciben como
argumentos, y las tablas tabla_afd.csv y tabla_ll1.csv las buscan el lexer y
el parser junto a su propio código.

Salida:

* stdout: solo lo pedido (la lista de tokens, el árbol y la derivación), para
  poder redirigirlo a un archivo;
* stderr: los errores y los avisos;
* código de salida: 0 sin errores, 1 con errores léxicos o sintácticos y 2 si
  el archivo no se pudo leer o los argumentos no son válidos.
"""

import argparse
import sys
from pathlib import Path

from src.lexer.lexer import AnalizadorLexico
from src.lexer.tokens import EOF
from src.parser.parser import Parser
from src.parser.visualizacion import (exportar_derivacion, exportar_dot, exportar_imagen,
                                      exportar_texto, imprimir_arbol, texto_derivacion)

SIN_ERRORES = 0
CON_ERRORES = 1
ERROR_DE_ENTRADA = 2


def crear_parser_argumentos():
    argumentos = argparse.ArgumentParser(
        prog="python main.py",
        description="Analizador léxico y sintáctico de Cafetal: muestra el árbol de "
                    "derivación de un programa .cft o el listado de sus errores.")
    argumentos.add_argument("archivo", help="ruta del programa fuente .cft")
    argumentos.add_argument("--tokens", action="store_true",
                            help="mostrar la lista de tokens antes del árbol")
    argumentos.add_argument("--derivacion", action="store_true",
                            help="mostrar también la derivación más a la izquierda")
    argumentos.add_argument("--posiciones", action="store_true",
                            help="mostrar la línea y la columna de cada token en el árbol")
    argumentos.add_argument("--ascii", action="store_true",
                            help="dibujar las ramas del árbol solo con caracteres ASCII")
    argumentos.add_argument("--salida", metavar="RUTA",
                            help="guardar el árbol en este archivo de texto (UTF-8)")
    argumentos.add_argument("--salida-derivacion", metavar="RUTA",
                            help="guardar la derivación en este archivo de texto (UTF-8)")
    argumentos.add_argument("--dot", metavar="RUTA",
                            help="guardar el árbol en formato DOT de Graphviz")
    argumentos.add_argument("--png", metavar="RUTA",
                            help="dibujar el árbol como imagen PNG (requiere Graphviz)")
    return argumentos


def usar_utf8():
    """Escribe stdout y stderr en UTF-8.

    En Windows, si la salida se redirige a un archivo, Python usa cp1252, que
    no tiene ε ni las ramas del árbol (├──), y la escritura falla. Los flujos
    que no se pueden reconfigurar (por ejemplo, en las pruebas) se dejan igual.
    """
    for flujo in (sys.stdout, sys.stderr):
        if hasattr(flujo, "reconfigure"):
            flujo.reconfigure(encoding="utf-8")


def leer_tokens(lexer, ruta):
    """Tokens del archivo, o None si no se pudo leer (el motivo va a stderr).

    La carpeta se revisa antes de abrir, porque en Windows abrir una carpeta
    lanza PermissionError y no IsADirectoryError.
    """
    if Path(ruta).is_dir():
        print(f"No se pudo leer el archivo {ruta!r}: es una carpeta, no un archivo.", file=sys.stderr)
        return None
    try:
        return lexer.analizar_archivo(ruta)
    except FileNotFoundError:
        motivo = "no existe"
    except PermissionError:
        motivo = "no se tiene permiso para leerlo"
    except UnicodeDecodeError:
        motivo = "no está guardado en UTF-8"
    print(f"No se pudo leer el archivo {ruta!r}: {motivo}.", file=sys.stderr)
    return None


def imprimir_tokens(tokens):
    """Tabla de tokens que recibe el parser (sin COMENTARIO ni BLANCO)."""
    print(f"{'Línea':>5} {'Col':>4}  {'Token':<12} {'Cód':>3}  Lexema")
    for token in tokens:
        print(f"{token.linea:>5} {token.columna:>4}  {token.tipo:<12} {token.codigo:>3}  {token.lexema!r}")
    print(f"\n{len(tokens) - 1} tokens, más {EOF}.\n")


def cantidad(n, singular, plural):
    return f"{n} {singular if n == 1 else plural}"


def reportar_errores(lexicos, sintacticos):
    """Lista los errores léxicos y después los sintácticos, cada grupo en orden."""
    for errores, singular, plural in [(lexicos, "error léxico", "errores léxicos"),
                                      (sintacticos, "error sintáctico", "errores sintácticos")]:
        if errores:
            print(f"{cantidad(len(errores), singular, plural)}:", file=sys.stderr)
            for error in errores:
                print(f"  {error}", file=sys.stderr)
    total = len(lexicos) + len(sintacticos)
    print(f"\n{cantidad(total, 'error', 'errores')} en total; no se muestra el árbol de derivación.",
          file=sys.stderr)


def guardar_salidas(raiz, args):
    """Guarda los archivos pedidos. La imagen es opcional: si Graphviz no está, solo avisa."""
    if args.salida:
        exportar_texto(raiz, args.salida, args.ascii, args.posiciones)
        print(f"Árbol guardado en {args.salida}.", file=sys.stderr)
    if args.salida_derivacion:
        exportar_derivacion(raiz, args.salida_derivacion)
        print(f"Derivación guardada en {args.salida_derivacion}.", file=sys.stderr)
    if args.dot:
        exportar_dot(raiz, args.dot)
        print(f"Árbol en formato DOT guardado en {args.dot}.", file=sys.stderr)
    if args.png:
        try:
            exportar_imagen(raiz, args.png)
            print(f"Imagen del árbol guardada en {args.png}.", file=sys.stderr)
        except RuntimeError as error:
            print(f"Aviso: {error}", file=sys.stderr)


def main(argv=None):
    usar_utf8()
    args = crear_parser_argumentos().parse_args(argv)

    # 1. Análisis léxico (LXR-1 y LXR-2): siempre entrega una lista válida de
    #    tokens, y los errores quedan aparte en lexer.errores.
    lexer = AnalizadorLexico()
    tokens = leer_tokens(lexer, args.archivo)
    if tokens is None:
        return ERROR_DE_ENTRADA
    if args.tokens:
        imprimir_tokens(tokens)

    # 2. Análisis sintáctico (PAR-2 a PAR-4): se hace aunque haya errores
    #    léxicos, para reportar en una sola ejecución todos los problemas del
    #    archivo. Con recuperación en modo pánico, analizar() siempre devuelve
    #    un árbol, y los errores quedan en parser.errores.
    parser = Parser(tokens)
    raiz = parser.analizar()

    # 3. El árbol o el listado de errores: con errores, el árbol está
    #    incompleto, así que solo se muestran los errores.
    if lexer.errores or parser.errores:
        reportar_errores(lexer.errores, parser.errores)
        return CON_ERRORES

    imprimir_arbol(raiz, args.ascii, args.posiciones)
    if args.derivacion:
        print()
        print(texto_derivacion(raiz), end="")
    guardar_salidas(raiz, args)
    print(f"\nAnálisis correcto: {cantidad(len(tokens) - 1, 'token', 'tokens')} y "
          f"{cantidad(len(raiz.derivacion_izquierda()), 'regla aplicada', 'reglas aplicadas')}.",
          file=sys.stderr)
    return SIN_ERRORES


if __name__ == "__main__":
    sys.exit(main())
