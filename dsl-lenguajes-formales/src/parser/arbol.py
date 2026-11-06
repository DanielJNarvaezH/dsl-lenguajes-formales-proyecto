"""Árbol de derivación de Cafetal y contrato entre el analizador léxico y el sintáctico (PAR-1).

Contrato entre el lexer y el parser
-----------------------------------
El analizador sintáctico recibe la lista de objetos Token que produce
AnalizadorLexico (src/lexer/lexer.py). Cada Token tiene:

* tipo: nombre del token del catálogo (INICIO, ID, SUMA…). Es exactamente el
  nombre del terminal en la BNF de la Fase 2, así que el parser decide solo
  con este campo;
* lexema: el texto reconocido, que se guarda en las hojas del árbol;
* linea y columna: posición del primer carácter, desde 1, para los mensajes
  de error;
* codigo (propiedad): el código numérico del catálogo.

El analizador léxico garantiza, y verificar_contrato comprueba, que:

1. todo tipo pertenece al catálogo (tokens.py);
2. no hay COMENTARIO ni BLANCO: se descartan antes de llegar al parser;
3. la lista termina con EOF, que aparece una sola vez;
4. los tokens están en el orden del texto (línea y columna crecientes);
5. los errores léxicos no están en la lista: quedan en AnalizadorLexico.errores.

El parser, por su parte, no modifica los tokens (Token es inmutable): solo los
lee en orden y los empareja con los terminales de la gramática.

Árbol de derivación
-------------------
Cada nodo es de uno de tres tipos:

* no terminal: símbolo de la BNF entre < > (por ejemplo <suma_prima>), con la
  etiqueta de la regla que se le aplicó (R10, F2…) y sus hijos en el orden del
  lado derecho de esa regla;
* terminal: hoja con el Token emparejado; su símbolo es el tipo del token;
* vacío: hoja ε, hijo único de un no terminal al que se le aplicó una regla ε.

EOF no forma parte del árbol: la gramática no lo genera, solo marca el fin.
Imprimir o exportar el árbol corresponde a ARB-1.
"""

from dataclasses import dataclass, field
from typing import Iterator, List, Optional, Tuple

from ..lexer.lexer import Token
from ..lexer.tokens import CODIGOS, DESCARTABLES, EOF

# Símbolo de la hoja que representa la cadena vacía.
EPSILON = "ε"


class ErrorContrato(Exception):
    """La lista de tokens no cumple el contrato entre el lexer y el parser."""


def verificar_contrato(tokens):
    """Comprueba las garantías 1 a 4 del contrato. Lanza ErrorContrato si falla alguna."""
    if not tokens:
        raise ErrorContrato("la lista de tokens está vacía: debe terminar con EOF")
    anterior = None
    for i, token in enumerate(tokens):
        if not isinstance(token, Token):
            raise ErrorContrato(f"el elemento {i} no es un Token: {token!r}")
        if token.tipo not in CODIGOS:
            raise ErrorContrato(f"el token {i} tiene un tipo fuera del catálogo: {token.tipo!r}")
        if token.tipo in DESCARTABLES:
            raise ErrorContrato(f"el token {i} es {token.tipo}, que el lexer debe descartar")
        es_ultimo = i == len(tokens) - 1
        if (token.tipo == EOF) != es_ultimo:
            raise ErrorContrato("EOF debe aparecer una sola vez, como último token")
        posicion = (token.linea, token.columna)
        if anterior is not None and posicion <= anterior:
            raise ErrorContrato(f"el token {i} ({token}) no está después del anterior")
        anterior = posicion


@dataclass(eq=False)
class Nodo:
    """Nodo del árbol de derivación.

    Se crea con Nodo.no_terminal, Nodo.terminal o Nodo.vacio. Dos árboles son
    iguales (==) si tienen los mismos símbolos, reglas, tokens e hijos. La
    comparación es iterativa, como recorrer, para no depender del límite de
    recursión de Python.
    """

    simbolo: str
    regla: Optional[str] = None
    token: Optional[Token] = None
    hijos: List["Nodo"] = field(default_factory=list)

    # Construcción

    @classmethod
    def no_terminal(cls, simbolo, regla):
        """Nodo de un no terminal (<...>) al que se le aplicó la regla indicada."""
        if not (len(simbolo) > 2 and simbolo.startswith("<") and simbolo.endswith(">")):
            raise ValueError(f"un no terminal se escribe entre < >: {simbolo!r}")
        if not regla:
            raise ValueError(f"falta la etiqueta de la regla aplicada a {simbolo}")
        return cls(simbolo, regla)

    @classmethod
    def terminal(cls, token):
        """Hoja con el token emparejado. Su símbolo es el tipo del token."""
        if not isinstance(token, Token):
            raise TypeError(f"se esperaba un Token: {token!r}")
        if token.tipo == EOF:
            raise ValueError("EOF no forma parte del árbol de derivación")
        return cls(token.tipo, token=token)

    @classmethod
    def vacio(cls):
        """Hoja ε, para las reglas que derivan la cadena vacía."""
        return cls(EPSILON)

    def agregar(self, hijo):
        """Agrega un hijo al final y lo devuelve. Solo los no terminales tienen hijos."""
        if not self.es_no_terminal:
            raise ValueError(f"{self!r} es una hoja: no puede tener hijos")
        if not isinstance(hijo, Nodo):
            raise TypeError(f"se esperaba un Nodo: {hijo!r}")
        self.hijos.append(hijo)
        return hijo

    # Tipo de nodo

    @property
    def es_no_terminal(self):
        return self.regla is not None

    @property
    def es_terminal(self):
        return self.token is not None

    @property
    def es_vacio(self):
        return self.regla is None and self.token is None

    @property
    def es_hoja(self):
        return not self.hijos

    # Consultas

    def recorrer(self) -> Iterator["Nodo"]:
        """Todos los nodos en preorden: el nodo y luego cada hijo, de izquierda a derecha.

        Es iterativo para no depender del límite de recursión de Python en
        programas largos.
        """
        pendientes = [self]
        while pendientes:
            nodo = pendientes.pop()
            yield nodo
            pendientes.extend(reversed(nodo.hijos))

    def hojas(self) -> List["Nodo"]:
        """Las hojas de izquierda a derecha, incluidas las ε."""
        return [nodo for nodo in self.recorrer() if nodo.es_hoja]

    def frontera(self) -> List[Token]:
        """Los tokens de las hojas, de izquierda a derecha.

        En un árbol completo desde <programa>, es la lista de tokens del
        programa sin EOF: la cadena que el árbol deriva.
        """
        return [nodo.token for nodo in self.recorrer() if nodo.es_terminal]

    def derivacion_izquierda(self) -> List[str]:
        """Las reglas aplicadas, en preorden.

        Ese orden es el de la derivación más a la izquierda, y el mismo en que
        un analizador descendente aplica las reglas (sección 11 de GIC-6).
        """
        return [nodo.regla for nodo in self.recorrer() if nodo.es_no_terminal]

    @property
    def posicion(self) -> Optional[Tuple[int, int]]:
        """(línea, columna) del primer token del subárbol, o None si no tiene tokens."""
        for nodo in self.recorrer():
            if nodo.es_terminal:
                return nodo.token.linea, nodo.token.columna
        return None

    def __eq__(self, otro):
        """Igualdad estructural, comparando los dos árboles nodo por nodo en preorden."""
        if not isinstance(otro, Nodo):
            return NotImplemented
        pendientes = [(self, otro)]
        while pendientes:
            a, b = pendientes.pop()
            if (a.simbolo, a.regla, a.token, len(a.hijos)) != (b.simbolo, b.regla, b.token, len(b.hijos)):
                return False
            pendientes.extend(zip(a.hijos, b.hijos))
        return True

    def __repr__(self):
        if self.es_terminal:
            return f"Nodo({self.simbolo} {self.token.lexema!r} {self.token.linea}:{self.token.columna})"
        if self.es_vacio:
            return f"Nodo({EPSILON})"
        return f"Nodo({self.simbolo} {self.regla}, {len(self.hijos)} hijos)"
