# \# dsl-lenguajes-formales

# 

# Diseño, auditoría e ingeniería inversa de un mini-lenguaje de programación de dominio específico (DSL) en Python.

# Proyecto final de Teoría de Lenguajes Formales — Universidad del Quindío, 2026-2.

# 

# \## Integrantes

# \- Daniel Josué Narváez Hincapié

# \- Juan Diego García Albarracín

# 

# \## Fases

# 1\. \*\*Formalismo léxico:\*\* alfabeto Σ, expresiones regulares primitivas por token, AFD y matriz de transiciones.

# 2\. \*\*Estructura sintáctica:\*\* GIC en BNF, eliminación de recursividad por la izquierda y factorización.

# 3\. \*\*Implementación:\*\* analizador léxico y sintáctico en Python que genera el árbol de derivación o el listado de errores.

# 

# \## Estructura

# | Carpeta | Contenido |

# | --- | --- |

# | `docs/fase1`, `docs/fase2`, `docs/fase3` | Documentos de cada fase |

# | `src/lexer` | Analizador léxico dirigido por la matriz del AFD |

# | `src/parser` | Analizador sintáctico y árbol de derivación |

# | `tests/validos`, `tests/errores` | Programas de prueba |

# | `ejemplos` | Programas de ejemplo escritos en el DSL |

# 

# \## Configuración del entorno

# ```bash

# python -m venv .venv

# .\\.venv\\Scripts\\Activate.ps1      # Windows (PowerShell)

# pip install -r requirements.txt

# ```

# 

# \## Restricciones del proyecto

# \- Expresiones regulares solo con unión (`,`), concatenación, cerradura de Kleene `( )\*` y cerradura positiva `( )+`.

# \- Sin librerías generadoras de parsers ni el módulo `re`: el lexer y el parser se implementan desde cero.

