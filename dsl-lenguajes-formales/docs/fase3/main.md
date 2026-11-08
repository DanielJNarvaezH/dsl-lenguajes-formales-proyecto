# Fase 3 — Punto de entrada por línea de comandos

**Tarea Jira:** PAR-5 — Punto de entrada por línea de comandos
**Responsable:** Juan Diego García Albarracín
**Insumos:** `src/lexer/lexer.py` (LXR-1 y LXR-2), `src/parser/parser.py` (PAR-2 a PAR-4), `src/parser/visualizacion.py` (ARB-1) y sus documentos en `docs/fase3/`
**Archivos:** `main.py` (en la raíz del proyecto) y `tests/test_main.py`
**Se complementa con:** TST-1 y TST-2 (suites de programas válidos y con errores), DOC-4 (guía de ejecución del README) y CIE-2 (pruebas en máquina limpia)

---

## 1. Qué hace

`main.py` es el punto de entrada del proyecto. Recibe la ruta de un programa Cafetal y hace lo que pide el enunciado de la Fase 3: tomar un archivo de texto con código del mini-lenguaje y generar **el árbol de derivación sintáctica o el listado de errores**.

```
archivo .cft ──► analizador léxico ──► tokens ──► analizador sintáctico ──► árbol
                   (LXR-1, LXR-2)                    (PAR-2 a PAR-4)          │
                        │                                  │                  ▼
                        └── errores léxicos ──┬── errores sintácticos   sin errores: árbol (ARB-1)
                                              ▼
                                    con errores: listado de errores
```

No tiene lógica de análisis propia: une las piezas que ya existen. El lexer decide con `tabla_afd.csv`, el parser con `tabla_ll1.csv` y el árbol se muestra con las funciones de ARB-1. Así, cada parte se prueba en su propio módulo y `main.py` solo se encarga de recibir los argumentos, ordenar la ejecución y mostrar el resultado.

## 2. Uso

Desde la carpeta del proyecto (`dsl-lenguajes-formales`), con Python 3 y sin librerías externas:

```
python main.py ejemplos/ejemplo3_secado.cft
python main.py ejemplos/ejemplo3_secado.cft --tokens --derivacion
python main.py ejemplos/ejemplo3_secado.cft --salida arbol.txt --dot arbol.dot
python main.py tests/errores/lexico1_fuera_del_alfabeto.cft
python main.py --help
```

| Argumento | Efecto |
|---|---|
| `archivo` (obligatorio) | Ruta del programa `.cft`, relativa a la carpeta actual o absoluta |
| `--tokens` | Muestra la lista de tokens (línea, columna, token, código y lexema) antes del árbol |
| `--derivacion` | Muestra también la derivación más a la izquierda (ARB-1, sección 3) |
| `--posiciones` | Agrega línea:columna a cada terminal del árbol |
| `--ascii` | Dibuja las ramas del árbol solo con caracteres ASCII |
| `--salida RUTA` | Guarda el árbol en un archivo de texto UTF-8 |
| `--salida-derivacion RUTA` | Guarda la derivación en un archivo de texto UTF-8 |
| `--dot RUTA` | Guarda el árbol en formato DOT de Graphviz |
| `--png RUTA` | Dibuja el árbol como imagen PNG; requiere Graphviz, que es opcional (ARB-1, sección 5) |

Las opciones de visualización tienen los mismos nombres que en `python -m src.parser.visualizacion` (ARB-1). Esa línea de comandos queda como herramienta para ver árboles; `main.py` es el punto de entrada oficial.

### 2.1 Sin rutas fijas

La rúbrica sanciona como hardcodeo las rutas fijas. En `main.py`:

- el programa `.cft` y todos los archivos de salida se reciben como argumentos, y ningún argumento tiene una ruta por defecto;
- las tablas `tabla_afd.csv` y `tabla_ll1.csv` no se nombran en `main.py`: las buscan el lexer y el parser junto a su propio código (`Path(__file__)`), sin depender de la carpeta desde donde se ejecuta.

Por eso el programa funciona desde cualquier carpeta, por ejemplo `python C:\...\dsl-lenguajes-formales\main.py C:\...\ejemplos\ejemplo3_secado.cft`. Una prueba lo ejecuta desde una carpeta temporal y otra revisa el código fuente para comprobar que no haya rutas fijas (sección 6).

## 3. Funcionamiento

| Paso | Qué hace | Pieza que usa |
|---|---|---|
| 1 | Lee los argumentos con `argparse` | — |
| 2 | Analiza el archivo léxicamente. Si no se puede leer, termina con código 2 (sección 4.3) | `AnalizadorLexico.analizar_archivo` |
| 3 | Si se pidió `--tokens`, muestra la lista de tokens | — |
| 4 | Analiza sintácticamente la lista de tokens | `Parser(tokens).analizar()` |
| 5 | Si hubo errores léxicos o sintácticos, los lista y termina con código 1 | `lexer.errores`, `parser.errores` |
| 6 | Si no hubo errores, muestra el árbol, la derivación si se pidió, guarda los archivos pedidos y termina con código 0 | `imprimir_arbol`, `texto_derivacion`, `exportar_*` |

### 3.1 Por qué se analiza sintácticamente aunque haya errores léxicos

El lexer siempre entrega una lista válida de tokens (contrato de PAR-1, garantía 5): los símbolos con error simplemente no están. Por eso el parser puede trabajar igual, y se reportan en una sola ejecución todos los problemas del archivo, léxicos y sintácticos.

Tiene un costo: un símbolo que falta puede producir un error sintáctico que en realidad es consecuencia del léxico. Por ejemplo, en `dato año = 2026;` el lexer reporta la `ñ`, y el parser recibe `dato a o = 2026;`, que tampoco es sintácticamente válido. Para que se note el origen, **los errores léxicos se listan primero**, y cada grupo va en el orden del archivo. La alternativa, detenerse después de los errores léxicos, ocultaría los errores sintácticos reales del resto del archivo.

### 3.2 Árbol o errores

Si hubo algún error, se muestra solo el listado de errores, no el árbol: con errores, el árbol que devuelve el parser en modo pánico (PAR-4) está incompleto. Es el mismo criterio de la línea de comandos de ARB-1. Con errores tampoco se guardan los archivos de `--salida`, `--dot` ni los demás.

## 4. Salida

### 4.1 Dónde se escribe cada cosa

| Flujo | Contenido |
|---|---|
| Salida estándar (stdout) | Solo lo pedido: la lista de tokens, el árbol y la derivación |
| Salida de error (stderr) | Los errores, los avisos y el resumen final |

Así, `python main.py ejemplos/ejemplo3_secado.cft > arbol.txt` deja en el archivo solo el árbol, y los mensajes siguen apareciendo en la consola.

### 4.2 Programa sin errores

```
<programa> [P1]
├── INICIO 'inicio'
├── <sentencias> [R1]
│   ├── <sentencia> [P4]
…
└── FIN 'fin'

Análisis correcto: 57 tokens y 165 reglas aplicadas.
```

### 4.3 Programa con errores

Para `tests/errores/lexico2_simbolos_sin_token.cft`:

```
5 errores léxicos:
  Error léxico en la línea 3, columna 10, símbolo '_': no forma ningún token.
  Error léxico en la línea 4, columna 19, símbolo '.': no forma ningún token.
  Error léxico en la línea 5, columna 20, símbolo '.': no forma ningún token.
  Error léxico en la línea 6, columna 9, símbolo '!': no forma ningún token.
  Error léxico en la línea 9, columna 15, símbolo '.': no forma ningún token.
1 error sintáctico:
  Error sintáctico en la línea 9, columna 16: se esperaba Y, O, SUMA, RESTA, MULT, DIV, MENOR, MAYOR, MENOR_IGUAL, MAYOR_IGUAL, IGUAL, DIFERENTE, PAR_CIERRA o PUNTO_COMA y se encontró 'x' (ID).

6 errores en total; no se muestra el árbol de derivación.
```

El error sintáctico es consecuencia del último error léxico (sección 3.1): en la línea 9, `3.x` pierde el punto, y el parser recibe `3 x`, dos operandos seguidos. Los mensajes son los de `ErrorLexico` (LXR-2) y `ErrorSintactico` (PAR-2 y PAR-4), sin cambios.

### 4.4 Códigos de salida

| Código | Significado |
|---|---|
| 0 | Análisis correcto: se mostró el árbol |
| 1 | El programa tiene errores léxicos o sintácticos: se mostró el listado |
| 2 | No se pudo analizar: el archivo no existe, es una carpeta, no se puede leer o no está en UTF-8, o los argumentos no son válidos (este último caso lo maneja `argparse`) |

En PowerShell, el código de la última ejecución se ve con `$LASTEXITCODE`.

### 4.5 Caracteres especiales en Windows

El árbol usa `ε` y las ramas `├──`, `└──` y `│`. En la consola se ven bien, pero cuando la salida se redirige a un archivo en Windows, Python usa por defecto la codificación cp1252, que no tiene esos caracteres, y la escritura falla con `UnicodeEncodeError`. Por eso `main.py` configura stdout y stderr en UTF-8 al empezar (`usar_utf8`). Una prueba lo verifica ejecutando `main.py` con la salida en cp1252, como la de Windows (sección 6).

Si en alguna consola las ramas se ven como símbolos raros, se puede usar `--ascii`, o ejecutar antes `chcp 65001` (ARB-1, sección 2).

## 5. Estructura de `main.py`

| Función | Qué hace |
|---|---|
| `crear_parser_argumentos` | Define los argumentos con `argparse` |
| `usar_utf8` | Configura stdout y stderr en UTF-8 (sección 4.5) |
| `leer_tokens` | Ejecuta el lexer sobre el archivo y traduce los problemas de lectura a un mensaje claro (sección 4.4). Revisa primero si la ruta es una carpeta, porque en Windows abrir una carpeta lanza `PermissionError` y no `IsADirectoryError` |
| `imprimir_tokens` | Tabla de tokens de `--tokens` |
| `reportar_errores` | Lista los errores léxicos y después los sintácticos |
| `guardar_salidas` | Guarda los archivos pedidos. Si se pide `--png` y Graphviz no está instalado, solo muestra un aviso: la imagen es opcional y no cambia el resultado del análisis |
| `main` | Ordena los pasos de la sección 3 y devuelve el código de salida |

## 6. Pruebas

```
python -m unittest tests.test_main -v
```

| Grupo | Qué comprueba |
|---|---|
| Programa válido | Los tres programas de `ejemplos/`: código 0, la salida es exactamente el árbol de ARB-1 y el resumen tiene los tokens y las reglas correctas (57 y 165 en el secado); `--tokens`, `--derivacion`, `--ascii` y `--posiciones`; `--salida`, `--salida-derivacion` y `--dot` guardan exactamente lo que producen las funciones de ARB-1; `--png` con y sin Graphviz |
| Errores | Errores léxicos: código 1, salida vacía y los 5 errores de LXR-2; los léxicos van antes que los sintácticos; un error sintáctico con su mensaje exacto; con errores no se guarda el árbol; archivo vacío; `--tokens` funciona aunque haya errores |
| Entrada | Archivo inexistente, carpeta, archivo en Latin-1 y sin argumentos: código 2 |
| Ejecución real | `python main.py` desde una carpeta temporal con rutas absolutas, y con la salida en cp1252 como en Windows: `ε` y `├──` se escriben bien |
| Restricciones | `main.py` no importa `re`; ningún texto fijo del código tiene separadores de ruta, ninguna función que abre o escribe archivos recibe una ruta fija y ningún argumento tiene una ruta por defecto |

Resultado: **19 pruebas, todas correctas.** La suite completa del proyecto:

```
python -m unittest discover -s tests -t . -v
```
