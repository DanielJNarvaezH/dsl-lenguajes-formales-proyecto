# Fase 3 — Programas con errores y pruebas automatizadas

**Tarea Jira:** TST-2 — Programas con errores y pruebas automatizadas
**Responsable:** Daniel Josué Narváez Hincapié
**Insumos:** los programas con errores de LXR-2 (`docs/fase3/errores_lexicos.md`, sección 6) y de PAR-4 (`docs/fase3/parser.md`, sección 12.2), `main.py` (PAR-5) y la suite de programas válidos (TST-1, `docs/fase3/pruebas_validos.md`)
**Archivos:** `tests/errores/` (6 programas `.cft` y su salida esperada `.txt`), `tests/test_errores.py` y `ejecutar_pruebas.py` (en la raíz del proyecto)
**Se complementa con:** TST-1 (programas válidos), DOC-4 (guía de ejecución del README) y CIE-2 (pruebas en máquina limpia)

---

## 1. Qué contiene

La tarea pide seis programas con errores léxicos y sintácticos y un script que ejecute toda la suite y compare con lo esperado.

| Parte | Dónde |
|---|---|
| 6 programas con errores, cada uno con su salida esperada | `tests/errores/`: un `.cft` y un `.txt` con el mismo nombre |
| Pruebas que comparan la salida de `main.py` con la esperada y validan lo esperado sin usar el analizador | `tests/test_errores.py` |
| Script que ejecuta toda la suite y resume el resultado | `ejecutar_pruebas.py` |

Los seis programas ya existían: los tres léxicos se escribieron en LXR-2 y los tres sintácticos en PAR-4. Hasta ahora cada prueba revisaba solo su parte: los errores léxicos con el lexer y los sintácticos con el parser. TST-2 los prueba de punta a punta, como los ve un usuario: con `main.py`, que analiza también sintácticamente los programas con errores léxicos (sección 3.1 de `main.md`).

| # | Programa | Qué prueba | Errores léxicos | Errores sintácticos | Total |
|---|---|---|---|---|---|
| 1 | `lexico1_fuera_del_alfabeto` | Símbolos que no pertenecen a Σ: mayúscula, ñ, coma y llaves | 5 | 2 | 7 |
| 2 | `lexico2_simbolos_sin_token` | Símbolos de Σ que no forman token: `_` inicial, `.` sin dígitos, `!` solo | 5 | 1 | 6 |
| 3 | `lexico3_cadenas_y_comentarios` | Cadena sin cerrar, cadena con símbolo fuera de C, comentario cortado por una mayúscula, `@` | 6 | 5 | 11 |
| 4 | `sintactico1_expresiones` | Operando que falta, dos operadores seguidos, relacionales encadenados, `;` que falta | 0 | 4 | 4 |
| 5 | `sintactico2_sentencias` | Palabra reservada como variable, `=` que falta, `entonces` en lugar de `hacer`, `mostrar()` vacío, `sino` sin `si` | 0 | 5 | 5 |
| 6 | `sintactico3_bloques` | `si` sin paréntesis, bloque `si … sino` sin su `fin` | 0 | 3 | 3 |

Con los seis programas válidos de TST-1, la suite tiene 12 programas de prueba con el mismo formato: un `.cft` y su salida esperada.

## 2. Salida esperada

Cada `.txt` contiene exactamente lo que `main.py` escribe en la salida de error para ese programa: los errores léxicos, después los sintácticos y la línea final con el total. La salida estándar queda vacía, porque con errores no se muestra el árbol. Por ejemplo, `sintactico2_sentencias.txt`:

```
5 errores sintácticos:
  Error sintáctico en la línea 3, columna 10: se esperaba ID y se encontró 'si' (SI).
  Error sintáctico en la línea 4, columna 13: se esperaba ASIGNACION y se encontró '12' (ENTERO).
  Error sintáctico en la línea 5, columna 29: se esperaba HACER y se encontró 'entonces' (ENTONCES).
  Error sintáctico en la línea 8, columna 13: se esperaba NO, ID, ENTERO, DECIMAL, CADENA o PAR_ABRE y se encontró ')' (PAR_CIERRA).
  Error sintáctico en la línea 9, columna 5: se esperaba FIN y se encontró 'sino' (SINO).

5 errores en total; no se muestra el árbol de derivación.
```

Si cambia el formato de los mensajes, los `.txt` se regeneran con:

```
python -m tests.test_errores --regenerar
```

El comando los escribe en UTF-8, con saltos de línea `\n`. No conviene generarlos redirigiendo la salida de `main.py` en PowerShell (`2> archivo.txt`), porque PowerShell 5 guarda el archivo en UTF-16. Después de regenerar, las pruebas de la sección 4 tienen que seguir pasando.

## 3. Errores esperados, escritos a mano

Los errores léxicos y los sintácticos de los programas 4 a 6 se explican en sus documentos (sección 6 de `errores_lexicos.md` y sección 12.2 de `parser.md`). Lo nuevo de TST-2 son los **errores sintácticos de los programas léxicos**: el lexer entrega los tokens sin los símbolos con error, y el parser analiza lo que queda. Cada uno se dedujo a mano quitando del texto los símbolos con error léxico.

### 3.1 `lexico1_fuera_del_alfabeto`

| Línea | Texto | Lo que recibe el parser | Error sintáctico |
|---|---|---|---|
| 3 | `dato Kilos = 250;` | `dato ilos = 250;` | Ninguno: `ilos` es un ID válido |
| 4 | `dato año = 2026;` | `dato a o = 2026;`: la `o` es la palabra reservada O | Columna 12, `o`: se esperaba ASIGNACION |
| 5 | `dato humedad = 11,5;` | `dato humedad = 11 5;` | Columna 23, `5`: dos operandos seguidos |
| 6 y 8 | `… entonces {` y `}` | Sin las llaves, el `si … fin` queda bien formado | Ninguno |

### 3.2 `lexico2_simbolos_sin_token`

| Línea | Texto | Lo que recibe el parser | Error sintáctico |
|---|---|---|---|
| 3 | `dato _lote = 5;` | `dato lote = 5;` | Ninguno |
| 4 | `dato precio = .5;` | `dato precio = 5;` | Ninguno |
| 5 | `dato total = 12.;` | `dato total = 12;` | Ninguno |
| 6 | `si (!(total > 3)) entonces` | `si ((total > 3)) entonces`: paréntesis de más, pero válidos | Ninguno |
| 9 | `dato x = 3.x;` | `dato x = 3 x;` | Columna 16, `x`: dos operandos seguidos |

Este programa muestra que un error léxico no siempre produce un error sintáctico: en cuatro de las cinco líneas, lo que queda sigue siendo un programa válido.

### 3.3 `lexico3_cadenas_y_comentarios`

| Línea | Texto | Lo que recibe el parser | Error sintáctico |
|---|---|---|---|
| 4 | `mostrar("secar de nuevo);` | `mostrar(secar de nuevo);`: sin la comilla, las palabras son ID | Columna 20, `de`: después de `secar` se esperaba un operador o el `)`. La recuperación descarta hasta el `)` |
| 5 | `# Revisar el secador` | El comentario `# ` termina en la `R`; queda `evisar el secador` | Columna 15, `el`: `evisar` empieza una asignación y falta el `=`. Columna 18, `secador`: después de `el` falta un operador |
| 6 | `mostrar("lote: norte");` | `mostrar(lote norte);` | Columna 20, `norte`: dos operandos seguidos |
| 7 y 8 | `dias = dias - 1 @` y `fin` | `dias = dias - 1` sin `;`, y después `fin` | Línea 8, columna 1, `fin`: falta el `;`, y se detecta en el token siguiente |

En la línea 5 hay dos errores sintácticos porque, entre ellos, el parser empareja `el` correctamente. Según la sección 11.5 de `parser.md`, después de un emparejamiento correcto se vuelven a registrar errores.

### 3.4 Lista completa

`ESPERADOS_A_MANO`, en `tests/test_errores.py`, tiene los 36 errores de los seis programas como (clase, línea, columna, texto encontrado), copiados de las tablas anteriores y de los documentos de LXR-2 y PAR-4.

## 4. Cómo se verifica que la salida esperada es correcta

Igual que en TST-1, si la salida esperada se generara con `main.py` y después se comprobara `main.py` contra ella, la prueba sería circular. Por eso hay dos partes:

**1. Regresión (`PruebaMain`).** Para cada programa, `main.py` termina con código 1, no escribe nada en la salida estándar (no hay árbol) y su salida de error es idéntica, carácter por carácter, al `.txt`.

**2. Corrección de la salida esperada, sin usar el analizador (`PruebaSalidaEsperada`).** El `.txt` se lee como texto (`leer_errores`) y se valida contra fuentes independientes:

| Prueba | Contra qué se compara |
|---|---|
| `test_coincide_con_la_lista_a_mano` | La lista escrita a mano de la sección 3: mismos errores, misma clase, línea, columna y texto, en el mismo orden |
| `test_cada_error_apunta_a_su_simbolo_en_el_fuente` | El archivo `.cft`: en la línea y la columna de cada error está exactamente el símbolo o el lexema reportado. El fin del archivo se reporta en la línea siguiente a la última, columna 1 |
| `test_totales_y_orden` | El propio texto: el total de la última línea es la cantidad de errores; los léxicos van antes que los sintácticos y cada grupo está en el orden del archivo |

Para confirmar que la parte 2 no depende del analizador, se cambió a propósito una columna de `sintactico2_sentencias.txt` (13 por 14). Las pruebas de la parte 2 lo detectaron dos veces, contra la lista a mano y contra el archivo fuente, sin ejecutar `main.py`.

## 5. `ejecutar_pruebas.py`: toda la suite con un comando

Desde la carpeta del proyecto:

```
python ejecutar_pruebas.py                    # toda la suite
python ejecutar_pruebas.py -v                 # con el nombre de cada prueba
python ejecutar_pruebas.py lexer errores      # solo algunos módulos
```

Un módulo se puede nombrar completo (`tests.test_lexer`) o corto (`lexer`). El script usa solo `unittest`: descubre las pruebas de `tests/` igual que `python -m unittest discover -s tests -t .` y, al final, muestra un resumen por módulo con lo que prueba cada uno:

```
Resumen por módulo
Módulo                           Qué prueba                               Pruebas Fallas Omitidas
tests.test_arbol                 Árbol de derivación y contrato (PAR-1)        15      0        0
tests.test_errores               Programas con errores (TST-2)                  8      0        0
tests.test_errores_lexicos       Errores léxicos (LXR-2)                       14      0        0
tests.test_errores_sintacticos   Errores sintácticos (PAR-4)                   12      0        0
tests.test_lexer                 Analizador léxico (LXR-1)                     25      0        0
tests.test_main                  Punto de entrada main.py (PAR-5)              19      0        0
tests.test_parser_expresiones    Parser: expresiones (PAR-2)                   21      0        0
tests.test_parser_sentencias     Parser: programa y sentencias (PAR-3)         24      0        0
tests.test_validos               Programas válidos (TST-1)                      9      0        0
tests.test_visualizacion         Visualización del árbol (ARB-1)               19      0        0

166 pruebas en 4.6 s: 166 correctas, 0 con fallas y 0 omitidas.
Todas las pruebas pasaron.
```

| Código de salida | Significado |
|---|---|
| 0 | Todas las pruebas pasaron |
| 1 | Alguna prueba falló; el detalle está antes del resumen |
| 2 | Se nombró un módulo de pruebas que no existe |

La columna «Fallas» cuenta cada falla, incluidas las de las subpruebas: una prueba que revisa seis programas y falla en dos suma 2. Si Graphviz no está instalado, las pruebas de la imagen aparecen como omitidas y el resultado sigue siendo correcto. El script agrega la carpeta del proyecto a la ruta de importación, así que funciona desde cualquier carpeta: `python C:\...\dsl-lenguajes-formales\ejecutar_pruebas.py`.

## 6. Pruebas

```
python -m unittest tests.test_errores -v
```

| Grupo | Qué comprueba |
|---|---|
| Archivos | Están los 6 `.cft` con sus 6 `.txt`; 3 programas tienen errores léxicos y 3 solo sintácticos |
| `main.py` | Para cada programa: código 1, sin árbol y la salida de error idéntica a la esperada |
| Salida esperada | Sin usar el analizador: coincide con la lista a mano, cada error apunta a su símbolo en el fuente y los totales y el orden cuadran |
| `ejecutar_pruebas.py` | Ejecuta un módulo y resume el resultado; un módulo inexistente termina con error |

Resultado: **8 pruebas, todas correctas.** Con ellas, la suite completa tiene **166 pruebas**:

```
python ejecutar_pruebas.py
```
