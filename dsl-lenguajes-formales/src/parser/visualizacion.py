"""Visualización del árbol de derivación de Cafetal (ARB-1).

Tres salidas a partir de un árbol de Nodo (PAR-1):

* texto con sangría, para la consola o para un archivo de texto;
* la derivación más a la izquierda, forma sentencial por forma sentencial,
  para compararla con una derivación hecha a mano;
* el árbol en lenguaje DOT de Graphviz y, si Graphviz está instalado, una
  imagen PNG (opcional).

Todos los recorridos son iterativos, como recorrer() de PAR-1, para no depender
del límite de recursión de Python en programas largos.

Uso desde la terminal, en la raíz del repositorio:

    python -m src.parser.visualizacion ejemplos/ejemplo3_secado.cft
    python -m src.parser.visualizacion ejemplos/ejemplo3_secado.cft --salida arbol.txt
    python -m src.parser.visualizacion ejemplos/ejemplo3_secado.cft --derivacion
    python -m src.parser.visualizacion ejemplos/ejemplo3_secado.cft --salida-derivacion derivacion.txt
    python -m src.parser.visualizacion ejemplos/ejemplo3_secado.cft --dot arbol.dot --png arbol.png
"""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

from .arbol import EPSILON
from .parser import REGLA_ERROR, Parser
from ..lexer.lexer import AnalizadorLexico

# Ramas del árbol en texto: con caracteres de recuadro o solo ASCII.
RAMAS_UNICODE = {"medio": "├── ", "ultimo": "└── ", "linea": "│   ", "vacio": "    "}
RAMAS_ASCII = {"medio": "|-- ", "ultimo": "`-- ", "linea": "|   ", "vacio": "    "}

# Tokens cuyo lexema varía; en la derivación se escribe entre ⟨ ⟩, como en la Fase 2.
CON_LEXEMA = frozenset({"ID", "ENTERO", "DECIMAL", "CADENA"})


# ----------------------------------------------------------------------
# Etiquetas
# ----------------------------------------------------------------------

def etiqueta(nodo, posiciones=False):
    """Texto de un nodo en una línea.

    * no terminal: su símbolo y la regla aplicada, <suma> [R9];
    * terminal: su tipo y su lexema, ID 'kilos' (con posiciones=True, también
      la línea y la columna);
    * vacío: ε.

    Si el análisis tuvo errores (PAR-4), un no terminal omitido se muestra con
    [ERROR] y un terminal que faltaba, con (faltante).
    """
    if nodo.es_no_terminal:
        return f"{nodo.simbolo} [{nodo.regla}]"
    if nodo.es_vacio:
        return EPSILON
    token = nodo.token
    if not token.lexema:
        return f"{nodo.simbolo} (faltante)"
    texto = f"{nodo.simbolo} {token.lexema!r}"
    return f"{texto} {token.linea}:{token.columna}" if posiciones else texto


def simbolo_derivacion(nodo):
    """Símbolo de un nodo en una forma sentencial: ID⟨kilos⟩, SUMA o <termino>."""
    if nodo.es_terminal and nodo.simbolo in CON_LEXEMA:
        return f"{nodo.simbolo}⟨{nodo.token.lexema}⟩"
    return nodo.simbolo


# ----------------------------------------------------------------------
# Árbol con sangría
# ----------------------------------------------------------------------

def lineas_arbol(raiz, ascii=False, posiciones=False):
    """Líneas del árbol con sangría, en preorden: la raíz y luego cada hijo."""
    ramas = RAMAS_ASCII if ascii else RAMAS_UNICODE
    lineas = [etiqueta(raiz, posiciones)]
    # Cada pendiente: (nodo, prefijo de sus antepasados, ¿es el último hijo?)
    pendientes = [(hijo, "", i == len(raiz.hijos) - 1)
                  for i, hijo in reversed(list(enumerate(raiz.hijos)))]
    while pendientes:
        nodo, prefijo, ultimo = pendientes.pop()
        lineas.append(prefijo + ramas["ultimo" if ultimo else "medio"] + etiqueta(nodo, posiciones))
        prefijo_hijos = prefijo + ramas["vacio" if ultimo else "linea"]
        for i in reversed(range(len(nodo.hijos))):
            pendientes.append((nodo.hijos[i], prefijo_hijos, i == len(nodo.hijos) - 1))
    return lineas


def texto_arbol(raiz, ascii=False, posiciones=False):
    """El árbol completo como texto, una línea por nodo."""
    return "\n".join(lineas_arbol(raiz, ascii, posiciones)) + "\n"


def imprimir_arbol(raiz, ascii=False, posiciones=False, salida=None):
    """Imprime el árbol en la consola (o en el flujo indicado)."""
    salida = salida if salida is not None else sys.stdout
    salida.write(texto_arbol(raiz, ascii, posiciones))


def exportar_texto(raiz, ruta, ascii=False, posiciones=False):
    """Guarda el árbol con sangría en un archivo de texto UTF-8."""
    Path(ruta).write_text(texto_arbol(raiz, ascii, posiciones), encoding="utf-8")


# ----------------------------------------------------------------------
# Derivación más a la izquierda
# ----------------------------------------------------------------------

def derivacion(raiz):
    """Derivación más a la izquierda que representa el árbol.

    Devuelve una lista de pasos (regla, forma sentencial). El primero es
    (None, "<programa>") y cada paso siguiente reemplaza el no terminal de más
    a la izquierda por los hijos de su nodo; una hoja ε no deja nada.
    """
    forma = [raiz]
    pasos = [(None, simbolo_derivacion(raiz))]
    inicio = 0
    while True:
        # Antes de inicio solo hay terminales: la derivación es más a la izquierda.
        while inicio < len(forma) and not forma[inicio].es_no_terminal:
            inicio += 1
        if inicio == len(forma):
            return pasos
        nodo = forma[inicio]
        hijos = [h for h in nodo.hijos if not h.es_vacio]
        forma[inicio:inicio + 1] = hijos
        texto = " ".join(simbolo_derivacion(n) for n in forma) or EPSILON
        pasos.append((nodo.regla, texto))


def exportar_derivacion(raiz, ruta):
    """Guarda la derivación más a la izquierda en un archivo de texto UTF-8."""
    Path(ruta).write_text(texto_derivacion(raiz), encoding="utf-8")


def texto_derivacion(raiz):
    """La derivación como texto: una forma sentencial por línea, con la regla aplicada."""
    pasos = derivacion(raiz)
    ancho = max(len(regla or "") for regla, _ in pasos)
    lineas = []
    for regla, forma in pasos:
        marca = f"⇒ {regla:<{ancho}}" if regla else " " * (ancho + 2)
        lineas.append(f"{marca}  {forma}")
    return "\n".join(lineas) + "\n"


# ----------------------------------------------------------------------
# Graphviz (opcional)
# ----------------------------------------------------------------------

def _texto_dot(texto):
    """Texto entre comillas para DOT."""
    return '"' + texto.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n") + '"'


def a_dot(raiz):
    """El árbol en lenguaje DOT de Graphviz.

    No terminales en rectángulos redondeados, terminales en elipses con el
    lexema debajo, ε como texto y los nodos ERROR con borde punteado. Es el
    mismo código visual de los árboles de la Fase 2 en draw.io.
    """
    lineas = ["digraph arbol {",
              '  graph [ordering=out, nodesep=0.25, ranksep=0.45];',
              '  node [fontname="Arial", fontsize=11];',
              "  edge [arrowhead=none];"]
    ids = {}
    for nodo in raiz.recorrer():
        ident = f"n{len(ids)}"
        ids[id(nodo)] = ident
        if nodo.es_no_terminal:
            estilo = "rounded,dashed" if nodo.regla == REGLA_ERROR else "rounded"
            texto = f"{nodo.simbolo}\n{nodo.regla}"
            atributos = f"shape=box, style={_texto_dot(estilo)}"
        elif nodo.es_vacio:
            texto, atributos = EPSILON, "shape=plaintext"
        else:
            lexema = nodo.token.lexema or "(faltante)"
            texto = nodo.simbolo if nodo.token.lexema == nodo.simbolo.lower() else f"{nodo.simbolo}\n{lexema}"
            atributos = "shape=ellipse"
        lineas.append(f"  {ident} [label={_texto_dot(texto)}, {atributos}];")
    for nodo in raiz.recorrer():
        for hijo in nodo.hijos:
            lineas.append(f"  {ids[id(nodo)]} -> {ids[id(hijo)]};")
    lineas.append("}")
    return "\n".join(lineas) + "\n"


def exportar_dot(raiz, ruta):
    """Guarda el árbol en un archivo .dot (UTF-8)."""
    Path(ruta).write_text(a_dot(raiz), encoding="utf-8")


def graphviz_disponible():
    """True si el programa dot de Graphviz está instalado y en el PATH."""
    return shutil.which("dot") is not None


def exportar_imagen(raiz, ruta, formato="png"):
    """Dibuja el árbol con Graphviz (dot) y lo guarda como imagen.

    Graphviz es opcional: si no está instalado, lanza RuntimeError con la
    indicación de usar el archivo .dot.
    """
    if not graphviz_disponible():
        raise RuntimeError("Graphviz no está instalado: no se encontró el programa 'dot'. "
                           "Use exportar_dot y abra el .dot en un visor de Graphviz.")
    subprocess.run(["dot", f"-T{formato}", "-o", str(ruta)],
                   input=a_dot(raiz).encode("utf-8"), check=True)


# ----------------------------------------------------------------------
# Línea de comandos
# ----------------------------------------------------------------------

def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="python -m src.parser.visualizacion",
        description="Muestra el árbol de derivación de un programa Cafetal (ARB-1).")
    parser.add_argument("archivo", help="archivo fuente .cft")
    parser.add_argument("--salida", help="guardar el árbol con sangría en este archivo de texto")
    parser.add_argument("--derivacion", action="store_true",
                        help="mostrar también la derivación más a la izquierda")
    parser.add_argument("--salida-derivacion",
                        help="guardar la derivación más a la izquierda en este archivo de texto")
    parser.add_argument("--posiciones", action="store_true",
                        help="mostrar la línea y la columna de cada token")
    parser.add_argument("--ascii", action="store_true",
                        help="dibujar las ramas solo con caracteres ASCII")
    parser.add_argument("--dot", help="guardar el árbol en formato DOT de Graphviz")
    parser.add_argument("--png", help="dibujar el árbol como imagen PNG (requiere Graphviz)")
    args = parser.parse_args(argv)

    lexer = AnalizadorLexico()
    try:
        tokens = lexer.analizar_archivo(args.archivo)
    except FileNotFoundError:
        print(f"No se encontró el archivo {args.archivo!r}.", file=sys.stderr)
        return 2
    analizador = Parser(tokens)
    raiz = analizador.analizar()
    errores = lexer.errores + analizador.errores
    if errores:
        # El enunciado pide el árbol o el listado de errores: con errores, el
        # árbol está incompleto (PAR-4) y no se muestra.
        print(f"{len(errores)} errores; no se muestra el árbol:", file=sys.stderr)
        for error in errores:
            print(f"  {error}", file=sys.stderr)
        return 1

    imprimir_arbol(raiz, args.ascii, args.posiciones)
    if args.derivacion:
        print()
        print(texto_derivacion(raiz), end="")
    if args.salida:
        exportar_texto(raiz, args.salida, args.ascii, args.posiciones)
        print(f"\nÁrbol guardado en {args.salida}.")
    if args.salida_derivacion:
        exportar_derivacion(raiz, args.salida_derivacion)
        print(f"Derivación guardada en {args.salida_derivacion}.")
    if args.dot:
        exportar_dot(raiz, args.dot)
        print(f"Árbol en formato DOT guardado en {args.dot}.")
    if args.png:
        try:
            exportar_imagen(raiz, args.png)
            print(f"Imagen del árbol guardada en {args.png}.")
        except RuntimeError as error:
            print(error, file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
