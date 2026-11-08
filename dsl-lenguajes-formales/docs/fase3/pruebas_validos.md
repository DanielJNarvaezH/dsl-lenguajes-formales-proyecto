# Fase 3 — Suite de programas válidos

**Tarea Jira:** TST-1 — Suite de programas válidos
**Responsable:** Juan Diego García Albarracín
**Insumos:** gramática final (`docs/fase2/factorizacion.md`, sección 6), tabla LL(1) (`src/parser/tabla_ll1.csv`, GIC-6), `main.py` (PAR-5) y el formato de árbol de ARB-1 (`docs/fase3/visualizacion.md`)
**Archivos:** `tests/validos/` (6 programas `.cft` y su árbol esperado `.txt`), `tests/test_validos.py`
**Se complementa con:** TST-2 (programas con errores y ejecución de toda la suite)

---

## 1. Qué contiene

`tests/validos/` tiene 6 programas válidos de Cafetal, cada uno con su árbol de derivación esperado:

| # | Programa | Qué prueba | Tokens | Reglas aplicadas | Reglas distintas |
|---|---|---|---|---|---|
| 1 | `valido1_produccion_lotes` | Declaraciones, aritmética con los cuatro operadores, paréntesis, decimales y `mostrar` de cadena y de expresión | 77 | 199 | 28 |
| 2 | `valido2_precio_venta` | `si` con y sin `sino`, `y`, los relacionales `<=`, `>=`, `!=` y `==`, y asignaciones | 83 | 211 | 37 |
| 3 | `valido3_secado_marquesina` | `mientras` con un `si … sino … fin` y un `si … fin` adentro, `o`, `no` con paréntesis | 77 | 223 | 38 |
| 4 | `valido4_clasificacion_anidada` | Condicionales anidados con las dos lecturas del sino colgante: el `sino` del `si` interno y el del externo | 77 | 162 | 29 |
| 5 | `valido5_precedencia` | Expresiones con todos los niveles de precedencia en una sola línea, `no no` y paréntesis que cambian la agrupación | 100 | 313 | 37 |
| 6 | `valido6_bloques_vacios` | Bloques vacíos: `si` con `sino` vacíos, `mientras` vacío y `si` vacío; `mostrar` de una expresión con paréntesis | 43 | 120 | 33 |

Los tokens no incluyen comentarios, blancos ni EOF. Las reglas aplicadas son los no terminales del árbol, que es el largo de la derivación más a la izquierda.

Todos los programas tienen sentido en el dominio de Cafetal (producción por lote, precio de venta, secado en marquesina, clasificación del grano), para que sirvan también como ejemplos en la sustentación. Solo `valido5_precedencia` usa variables de una letra, porque su objetivo es mostrar la agrupación de las expresiones.

### 1.1 Árbol esperado

Cada `valido*.cft` tiene un `valido*.txt` con el mismo nombre. Contiene el árbol en el formato de ARB-1: una línea por nodo en preorden, la regla de cada no terminal entre corchetes, el lexema de cada terminal entre comillas y ε en las reglas vacías. Es el mismo formato de la sección 5 de `arbol.md` y el que muestra `main.py`, así que el árbol esperado se puede abrir y revisar a mano.

## 2. Cobertura de la gramática

La gramática final tiene 46 reglas. **Las 46 aparecen en la suite, y cada una aparece en al menos dos programas.** La tabla dice en cuáles:

| Regla | No terminal | Programas |
|---|---|---|
| P1 | `<programa>` | 1, 2, 3, 4, 5, 6 |
| R1 | `<sentencias>` | 1, 2, 3, 4, 5, 6 |
| R2 | `<sentencias>` | 1, 2, 3, 4, 5, 6 |
| P4 | `<sentencia>` | 1, 2, 3, 4, 5, 6 |
| P5 | `<sentencia>` | 2, 3 |
| P6 | `<sentencia>` | 1, 2, 3, 4, 5, 6 |
| P7 | `<sentencia>` | 2, 3, 4, 6 |
| P8 | `<sentencia>` | 3, 6 |
| D1 | `<declaracion>` | 1, 2, 3, 4, 5, 6 |
| R3 | `<expresion>` | 1, 2, 3, 4, 5, 6 |
| R4 | `<expresion_prima>` | 3, 5 |
| R5 | `<expresion_prima>` | 1, 2, 3, 4, 5, 6 |
| R6 | `<conjuncion>` | 1, 2, 3, 4, 5, 6 |
| R7 | `<conjuncion_prima>` | 2, 5 |
| R8 | `<conjuncion_prima>` | 1, 2, 3, 4, 5, 6 |
| E5 | `<negacion>` | 3, 5 |
| E6 | `<negacion>` | 1, 2, 3, 4, 5, 6 |
| F1 | `<comparacion>` | 1, 2, 3, 4, 5, 6 |
| F2 | `<comparacion_prima>` | 2, 3, 4, 5, 6 |
| F3 | `<comparacion_prima>` | 1, 2, 3, 4, 5, 6 |
| E9 | `<op_rel>` (MENOR) | 4, 5 |
| E10 | `<op_rel>` (MAYOR) | 3, 4, 5, 6 |
| E11 | `<op_rel>` (MENOR_IGUAL) | 2, 5 |
| E12 | `<op_rel>` (MAYOR_IGUAL) | 2, 5 |
| E13 | `<op_rel>` (IGUAL) | 2, 3, 5, 6 |
| E14 | `<op_rel>` (DIFERENTE) | 2, 5 |
| R9 | `<suma>` | 1, 2, 3, 4, 5, 6 |
| R10 | `<suma_prima>` (SUMA) | 1, 3, 5, 6 |
| R11 | `<suma_prima>` (RESTA) | 1, 2, 3, 5 |
| R12 | `<suma_prima>` (ε) | 1, 2, 3, 4, 5, 6 |
| R13 | `<termino>` | 1, 2, 3, 4, 5, 6 |
| R14 | `<termino_prima>` (MULT) | 1, 2, 5, 6 |
| R15 | `<termino_prima>` (DIV) | 1, 5 |
| R16 | `<termino_prima>` (ε) | 1, 2, 3, 4, 5, 6 |
| E21 | `<factor>` (paréntesis) | 1, 3, 5, 6 |
| E22 | `<factor>` (ID) | 1, 2, 3, 4, 5, 6 |
| E23 | `<factor>` (ENTERO) | 1, 2, 3, 4, 5, 6 |
| E24 | `<factor>` (DECIMAL) | 1, 2, 4, 5 |
| A1 | `<asignacion>` | 2, 3 |
| M1 | `<salida>` | 1, 2, 3, 4, 5, 6 |
| M2 | `<argumento>` (expresión) | 1, 2, 3, 5, 6 |
| M3 | `<argumento>` (CADENA) | 1, 2, 3, 4 |
| F4 | `<condicional>` | 2, 3, 4, 6 |
| F5 | `<condicional_prima>` (FIN) | 2, 3, 4, 6 |
| F6 | `<condicional_prima>` (SINO) | 2, 3, 4, 6 |
| L1 | `<ciclo>` | 3, 6 |

La prueba `test_todas_las_reglas_al_menos_una_vez` calcula esta cobertura a partir de los árboles esperados y, si falta alguna regla, dice cuál.

## 3. Precedencia y asociatividad

`valido5_precedencia.cft` tiene, en la declaración de `listo`, una expresión que usa todos los niveles de precedencia de Cafetal: `o`, `y`, `no`, un relacional, `+ -`, `* /` y paréntesis.

```
dato listo = a + b * c - (a - b) / 2 > c o no a < b y c != 0;
```

### 3.1 Agrupación hecha a mano

Aplicando la precedencia de la especificación (de menor a mayor: `o`, `y`, `no`, relacionales, `+ -`, `* /`, paréntesis) y la asociatividad por la izquierda, la expresión se agrupa así, con un paréntesis por operación:

```
((((a + (b * c)) - ((a - b) / 2)) > c) o ((no (a < b)) y (c != 0)))
```

Paso a paso:

1. El operador de menor precedencia es el `o`, así que queda en la raíz: a la izquierda `a + b * c - (a - b) / 2 > c` y a la derecha `no a < b y c != 0`.
2. En la izquierda, el `>` separa `a + b * c - (a - b) / 2` de `c`.
3. En `a + b * c - (a - b) / 2`, `*` y `/` van primero: `b * c` y `(a - b) / 2`. Después `+` y `-`, por la izquierda: `(a + (b * c)) - ((a - b) / 2)`.
4. En la derecha, `y` es el de menor precedencia: `no a < b` y `c != 0`.
5. `no` tiene menos precedencia que los relacionales, así que se aplica a la comparación completa: `no (a < b)`.

### 3.2 Comprobación en el árbol esperado

En `valido5_precedencia.txt`, el `<expresion>` de `listo` tiene exactamente esa forma:

| Operador | Dónde queda en el árbol |
|---|---|
| `o` | En el `<expresion_prima>` [R4] hijo directo del `<expresion>`: es la raíz de la expresión |
| `y` | En el `<conjuncion_prima>` [R7] de la `<conjuncion>` que está a la derecha del `o` |
| `no` | En la `<negacion>` [E5] de esa conjunción, con la comparación `a < b` dentro: no alcanza a `c != 0` |
| `>` | En el `<comparacion_prima>` [F2] de la `<conjuncion>` izquierda, por encima de todos los `+ - * /` |
| `+`, `-` | En la cadena de `<suma_prima>` (R10 y después R11), en el orden del texto |
| `*` | En el `<termino_prima>` [R14] del `<termino>` que sigue al `+`: más abajo que el `+` |
| `/` | En el `<termino_prima>` [R15] del `<termino>` que sigue al `-`, cuyo `<factor>` es el paréntesis (E21) |

La función `agrupar` de las pruebas lee el árbol esperado de esa forma: recorre cada cadena `_prima` de izquierda a derecha y agrupa cada operador con lo acumulado a su izquierda (sección 7.2 de `recursividad.md`). El resultado se compara con la agrupación escrita a mano en la sección 3.1. Se hace lo mismo con otras cuatro expresiones:

| Programa | Variable | Agrupación escrita a mano |
|---|---|---|
| `valido5_precedencia` | `doble` | `(no (no (a == 4)))` |
| `valido5_precedencia` | `mixto` | `(((((a + b) * (c - 1)) / 3) >= 12) y ((b <= a) o (a == c)))` |
| `valido1_produccion_lotes` | `total` | `((lote_a + lote_b) + lote_c)` |
| `valido1_produccion_lotes` | `ajuste` | `((((lote_a - lote_b) * 2) + (lote_c / 4)) - 0.75)` |

En `mixto`, los paréntesis del texto cambian la agrupación: `b <= a o a == c` queda dentro del `y`, aunque `o` tenga menos precedencia. En `total` y `ajuste` se ve la asociatividad por la izquierda.

## 4. Cómo se verifica que el árbol esperado es correcto

Si el árbol esperado se generara con el parser y después se comprobara el parser contra él, la prueba sería circular: un error del parser quedaría guardado como "esperado". Por eso las pruebas tienen dos partes:

**1. Regresión (`PruebaParser`).** El parser, sobre cada `.cft`, no reporta errores léxicos ni sintácticos, y produce un árbol idéntico, carácter por carácter, al `.txt`.

**2. Corrección del árbol esperado, sin usar el parser.** El `.txt` se vuelve a leer como árbol a partir de su sangría (`leer_arbol`), y ese árbol se valida contra fuentes independientes:

| Prueba | Contra qué se compara |
|---|---|
| `test_cada_nodo_sigue_su_regla` | La BNF, escrita a mano en la prueba: cada no terminal es el lado izquierdo de su regla y sus hijos son exactamente el lado derecho, o ε |
| `test_las_hojas_son_el_programa` | Los tokens del lexer: las hojas, de izquierda a derecha, son el programa |
| `test_reglas_iguales_al_analizador_ll1` | Un analizador LL(1) con pila, como el de las trazas de GIC-6 (sección 11), que solo usa la tabla y la BNF: las reglas del árbol en preorden son exactamente las que aplica |
| `PruebaPrecedencia` | La agrupación escrita a mano de la sección 3 |

Para confirmar que estas pruebas no dependen del parser, se alteró a propósito `valido5_precedencia.txt` de tres formas: una regla cambiada (R10 por R11), dos hojas cambiadas (`*` por `/`) y una hoja ε borrada. Las pruebas de la parte 2 detectaron las tres alteraciones sin ejecutar el parser.

## 5. Regenerar los árboles esperados

Si la gramática o el formato del árbol cambian, los `.txt` se regeneran con `main.py`, desde la carpeta del proyecto:

```
python main.py tests/validos/valido1_produccion_lotes.cft --salida tests/validos/valido1_produccion_lotes.txt
```

Y lo mismo para los otros cinco. Después de regenerar, las pruebas de la parte 2 de la sección 4 tienen que seguir pasando: son las que garantizan que el árbol nuevo es correcto y no solo igual a lo que produce el parser.

Para agregar un programa a la suite, se guarda el `.cft` en `tests/validos/`, se genera su `.txt` con el comando anterior y se agrega su nombre a la lista `PROGRAMAS` de `tests/test_validos.py`.

## 6. Pruebas

```
python -m unittest tests.test_validos -v
```

| Grupo | Qué comprueba |
|---|---|
| Parser | Están los 6 `.cft` con sus 6 `.txt`; el parser los analiza sin errores y produce exactamente el árbol esperado |
| Árbol esperado | Sin usar el parser: cada nodo sigue su regla de la BNF, las hojas son el programa y el orden de las reglas coincide con el analizador LL(1) con pila |
| Cobertura | Las 46 reglas de la tabla aparecen al menos una vez, la BNF de la prueba coincide con la tabla y cada programa usa al menos 28 reglas distintas |
| Precedencia | La agrupación de cinco expresiones coincide con la escrita a mano, y `listo` usa todos los niveles de precedencia |

Resultado: **9 pruebas, todas correctas.** La suite completa del proyecto:

```
python -m unittest discover -s tests -t . -v
```

## 7. Relación con TST-2

TST-2 agrega los programas con errores y un script que ejecuta toda la suite. Para mantener un solo formato, los programas con errores pueden seguir la misma idea: cada `.cft` en `tests/errores/` con un archivo de salida esperada que el script compare, y en esta carpeta, el árbol esperado en el formato de ARB-1.
