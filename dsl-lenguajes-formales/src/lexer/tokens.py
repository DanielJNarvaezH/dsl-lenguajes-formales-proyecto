"""Catálogo de tokens de Cafetal (docs/fase1/catalogo_tokens.md).

Este módulo solo contiene datos: el código de cada categoría léxica y las
categorías que se descartan. El analizador léxico no decide nada con estos
datos; quien decide qué token es cada lexema es el AFD (tabla_afd.csv).
"""

# Código de cada categoría léxica, igual que en el catálogo de la Fase 1.
CODIGOS = {
    "INICIO": 1, "FIN": 2, "DATO": 3, "SI": 4, "ENTONCES": 5, "SINO": 6,
    "MIENTRAS": 7, "HACER": 8, "MOSTRAR": 9, "Y": 10, "O": 11, "NO": 12,
    "ID": 20, "ENTERO": 21, "DECIMAL": 22, "CADENA": 23,
    "SUMA": 30, "RESTA": 31, "MULT": 32, "DIV": 33,
    "MENOR": 40, "MAYOR": 41, "MENOR_IGUAL": 42, "MAYOR_IGUAL": 43,
    "IGUAL": 44, "DIFERENTE": 45,
    "ASIGNACION": 50, "PAR_ABRE": 60, "PAR_CIERRA": 61, "PUNTO_COMA": 62,
    "COMENTARIO": 90, "BLANCO": 91,
    "EOF": 99,
}

# Categorías que se reconocen para avanzar en el texto, pero no se entregan
# al analizador sintáctico (regla 3 de reconocimiento, Fase 1).
DESCARTABLES = frozenset({"COMENTARIO", "BLANCO"})

# Marcador de fin de archivo que se agrega al final de la lista de tokens.
EOF = "EOF"
