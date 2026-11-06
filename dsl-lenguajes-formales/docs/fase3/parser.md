# Fase 3 — Analizador sintáctico descendente recursivo

Este documento describe `src/parser/parser.py`. Lo completan tres tareas:

| Sección | Tarea | Responsable |
|---|---|---|
| 1 a 7 | PAR-2 — Base común del parser y funciones de expresiones | Daniel Josué Narváez Hincapié |
| (pendiente) | PAR-3 — Funciones de sentencias y programa | Juan Diego García Albarracín |
| (pendiente) | PAR-4 — Manejo de errores sintácticos | Daniel Josué Narváez Hincapié |

**Insumos:** gramática final (`docs/fase2/factorizacion.md`, sección 6), tabla LL(1) (`src/parser/tabla_ll1.csv` y `docs/fase2/primero_siguiente_ll1.md`, GIC-6), `src/parser/arbol.py` y `docs/fase3/arbol.md` (PAR-1)
**Archivos de PAR-2:** `src/parser/parser.py` (base común y expresiones) y `tests/test_parser_expresiones.py`

---

## 1. Idea

El parser es **descendente recursivo**: tiene una función de Python por cada no terminal de la gramática final, con el mismo nombre sin `< >` (`<suma_prima>` → `suma_prima`). La función de un no terminal A hace siempre lo mismo:

1. **Predice:** consulta la tabla LL(1) con A y el token actual, M[A, token], para saber qué regla aplicar. Si la celda está vacía, hay un error sintáctico.
2. **Crea su nodo** con `Nodo.no_terminal("<A>", regla)`, como indica la sección 5.1 de `arbol.md`.
3. **Recorre el lado derecho de la regla, en orden:** cada terminal se empareja con `emparejar(TIPO)`, cada no terminal se deriva llamando a su función y la regla ε agrega `Nodo.vacio()`.
4. **Devuelve el nodo.**

Así, **la tabla decide qué regla se aplica y el código solo escribe el lado derecho de cada regla.** Ninguna función pregunta por el tipo del token actual: las únicas comparaciones de las funciones son con la etiqueta de regla que devolvió la tabla (`if regla == "R4"`). Una prueba lo verifica sobre el código fuente (sección 7).

## 2. Base común

Estas piezas las usan tanto las funciones de expresiones (PAR-2) como las de sentencias (PAR-3).

| Pieza | Qué hace |
|---|---|
| `TablaLL1` | Carga `tabla_ll1.csv` (junto a `parser.py`, sin rutas fijas). `regla(A, t)` devuelve M[A, t] o `None` si la celda está vacía, y `esperados(A)` devuelve los terminales con celda llena en la fila de A, en el orden de las columnas |
| `Parser(tokens)` | Recibe la lista de tokens del lexer, según el contrato de PAR-1 |
| `actual` | El token actual, el siguiente sin consumir. Siempre existe, porque la lista termina en EOF |
| `predecir(A)` | M[A, actual.tipo]. Si la celda está vacía, llama a `_error` con la fila de A como esperados |
| `emparejar(TIPO)` | Si el token actual es de ese tipo, lo consume y devuelve su hoja (`Nodo.terminal`). Si no, llama a `_error` con `[TIPO]` |
| `verificar_fin()` | Comprueba que después del símbolo inicial solo quede EOF |
| `_error(esperados, contexto)` | Lanza `ErrorSintactico`. Es el único punto de manejo de errores: PAR-4 lo reemplaza por la recuperación en modo pánico |
| `analizar()` | Analiza un programa completo: `programa()` y después `verificar_fin()`. Funciona cuando PAR-3 agregue `programa()` |
| `analizar_fragmento(A, *seguido_de)` | Analiza solo el no terminal A, seguido de los terminales indicados y de EOF. Sirve para probar partes de la gramática |

`ErrorSintactico` tiene el token `encontrado`, su `linea` y `columna`, la lista de `esperados` y el `contexto` (el no terminal o el terminal que se estaba analizando). Su mensaje sigue el formato de los errores léxicos de LXR-2:

```
Error sintáctico en la línea 1, columna 7: se esperaba Y, O, PAR_CIERRA o PUNTO_COMA y se encontró '<' (MENOR).
```

### 2.1 Por qué se consulta la tabla también en los no terminales de una sola regla

`<expresion>`, `<conjuncion>`, `<comparacion>`, `<suma>` y `<termino>` tienen una sola regla, y la función podría aplicarla sin preguntar. Se consulta la tabla igual por dos razones. Primero, todas las funciones quedan con la misma forma: predecir, crear el nodo y recorrer el lado derecho. Segundo, el error se detecta **lo antes posible**: en `(a + ;`, el `;` se rechaza en `<termino>`, cuando se esperaba ID, ENTERO, DECIMAL o PAR_ABRE, y no varios pasos después en `<factor>`.

### 2.2 Por qué una expresión se prueba seguida de `;`

SIGUIENTE(`<expresion>`) = {PAR_CIERRA, PUNTO_COMA} (GIC-6). En Cafetal una expresión nunca aparece sola al final del archivo: siempre la sigue un `;` o un `)`. Por eso la tabla no tiene celdas con EOF en las filas de expresiones, y una expresión suelta seguida de EOF daría error en la primera regla ε. Las pruebas analizan `expresión ;` con `analizar_fragmento("<expresion>", "PUNTO_COMA")`, que es el mismo contexto en que aparecen en las asignaciones y declaraciones.

## 3. Funciones de expresiones

Siguen la gramática sin recursividad por la izquierda de GIC-4, factorizada en GIC-5. Encima de cada función está su regla BNF como comentario, y la misma regla está en su docstring.

| Función | Reglas | Lado derecho que escribe |
|---|---|---|
| `expresion` | R3 | `conjuncion()`, `expresion_prima()` |
| `expresion_prima` | R4, R5 | R4: `emparejar("O")`, `conjuncion()`, `expresion_prima()` · R5: ε |
| `conjuncion` | R6 | `negacion()`, `conjuncion_prima()` |
| `conjuncion_prima` | R7, R8 | R7: `emparejar("Y")`, `negacion()`, `conjuncion_prima()` · R8: ε |
| `negacion` | E5, E6 | E5: `emparejar("NO")`, `negacion()` · E6: `comparacion()` |
| `comparacion` | F1 | `suma()`, `comparacion_prima()` |
| `comparacion_prima` | F2, F3 | F2: `op_rel()`, `suma()` · F3: ε |
| `op_rel` | E9 a E14 | El relacional de la regla (MENOR, MAYOR, MENOR_IGUAL, MAYOR_IGUAL, IGUAL o DIFERENTE) |
| `suma` | R9 | `termino()`, `suma_prima()` |
| `suma_prima` | R10, R11, R12 | R10/R11: `emparejar("SUMA")` o `emparejar("RESTA")`, `termino()`, `suma_prima()` · R12: ε |
| `termino` | R13 | `factor()`, `termino_prima()` |
| `termino_prima` | R14, R15, R16 | R14/R15: `emparejar("MULT")` o `emparejar("DIV")`, `factor()`, `termino_prima()` · R16: ε |
| `factor` | E21 a E24 | E21: `emparejar("PAR_ABRE")`, `expresion()`, `emparejar("PAR_CIERRA")` · E22–E24: `emparejar` de ID, ENTERO o DECIMAL |

En `op_rel`, `suma_prima`, `termino_prima` y `factor`, varias reglas tienen la misma forma y solo cambia el terminal. El terminal de cada regla está en un diccionario de la clase (`TERMINAL_OP_REL`, `OPERADOR_SUMA`, `OPERADOR_TERMINO`, `OPERANDO`), que es una copia literal de las reglas E9–E14, R10–R11, R14–R15 y E22–E24: la regla sigue saliendo de la tabla, y el diccionario solo dice qué terminal pide.

### 3.1 Ejemplo: `kilos + 25 * 2;`

| Paso | Función | Token actual | M[A, token] | Qué hace |
|---|---|---|---|---|
| 1 | `expresion` | ID `kilos` | R3 | Llama a `conjuncion` |
| 2–4 | `conjuncion`, `negacion`, `comparacion` | ID | R6, E6, F1 | Bajan hasta `suma` |
| 5 | `suma` | ID | R9 | Llama a `termino` |
| 6 | `termino` | ID | R13 | Llama a `factor` |
| 7 | `factor` | ID | E22 | `emparejar("ID")` |
| 8 | `termino_prima` | SUMA | R16 | ε: no hay `*` ni `/` |
| 9 | `suma_prima` | SUMA | R10 | `emparejar("SUMA")`, `termino()`, `suma_prima()` |
| 10–11 | `termino`, `factor` | ENTERO `25` | R13, E23 | `emparejar("ENTERO")` |
| 12 | `termino_prima` | MULT | R14 | `emparejar("MULT")`, `factor()` (E23, `2`), `termino_prima()` |
| 13 | `termino_prima` | PUNTO_COMA | R16 | ε |
| 14 | `suma_prima` | PUNTO_COMA | R12 | ε |
| 15–17 | `comparacion_prima`, `conjuncion_prima`, `expresion_prima` | PUNTO_COMA | F3, R8, R5 | ε |

Las reglas en ese orden, R3 R6 E6 F1 R9 R13 E22 R16 R10 R13 E23 R14 E23 R16 R12 F3 R8 R5, son la derivación más a la izquierda que devuelve `derivacion_izquierda()`. El MULT queda dentro del `<termino>` que sigue al SUMA, es decir, más abajo en el árbol: `25 * 2` se agrupa primero, como exige la precedencia.

## 4. Cómo agregar las funciones de sentencias (PAR-3)

Las funciones de PAR-3 van al final de la clase `Parser`, en la sección marcada «Programa y sentencias (PAR-3)», con la misma forma. Por ejemplo, para la regla de una sola alternativa A1:

```python
# A1   <asignacion> ::= ID ASIGNACION <expresion> PUNTO_COMA
def asignacion(self):
    """A1: <asignacion> ::= ID ASIGNACION <expresion> PUNTO_COMA"""
    nodo = Nodo.no_terminal("<asignacion>", self.predecir("<asignacion>"))
    nodo.agregar(self.emparejar("ID"))
    nodo.agregar(self.emparejar("ASIGNACION"))
    nodo.agregar(self.expresion())
    nodo.agregar(self.emparejar("PUNTO_COMA"))
    return nodo
```

Y para un no terminal con varias reglas, se compara la etiqueta que devolvió `predecir`, nunca el tipo del token:

```python
# F5   <condicional_prima> ::= FIN
# F6   <condicional_prima> ::= SINO <sentencias> FIN
def condicional_prima(self):
    """F5: <condicional_prima> ::= FIN | F6: SINO <sentencias> FIN"""
    regla = self.predecir("<condicional_prima>")
    nodo = Nodo.no_terminal("<condicional_prima>", regla)
    if regla == "F6":
        nodo.agregar(self.emparejar("SINO"))
        nodo.agregar(self.sentencias())
    nodo.agregar(self.emparejar("FIN"))
    return nodo
```

Con `programa()` definido, `Parser(tokens).analizar()` ya analiza un archivo completo.

## 5. Errores en PAR-2

En esta tarea, el primer error sintáctico detiene el análisis con `ErrorSintactico`. Hay dos lugares donde se detecta:

| Dónde | Cuándo | Esperados |
|---|---|---|
| `predecir(A)` | La celda M[A, token] está vacía | La fila de A en la tabla: los terminales con los que A puede empezar y, si A tiene regla ε, también su SIGUIENTE |
| `emparejar(TIPO)` | El token no es el terminal que pide la regla | Solo `TIPO` |

Ejemplos:

| Entrada | Error | Esperados |
|---|---|---|
| `a < b < c;` | Segundo `<`, columna 7, en `<conjuncion_prima>`: después de `a < b` ya no cabe otro relacional (GIC-6, sección 9.1) | Y, O, PAR_CIERRA, PUNTO_COMA |
| `(a + ;` | `;` en `<termino>` | ID, ENTERO, DECIMAL, PAR_ABRE |
| `(a;` | `;` al emparejar el `)` de E21 | PAR_CIERRA |
| `a; b` | `b` después del `;` | el fin del archivo |

PAR-4 reemplaza `_error` por la recuperación en modo pánico: registrar el error, descartar tokens hasta uno del conjunto SIGUIENTE del no terminal y continuar, para listar varios errores.

## 6. Límite de anidamiento

Como cada no terminal es una función, la profundidad de llamadas de Python crece con el anidamiento de la expresión. Cada nivel de paréntesis usa unas siete llamadas (de `expresion` a `factor`), así que con el límite de recursión de Python por defecto (1 000) se pueden anidar alrededor de 140 paréntesis. Una cadena de operadores sin paréntesis, como `a + a + … + a`, agrega una llamada por operador en `suma_prima`, y funciona con más de 900 operadores. Los programas de Cafetal quedan muy por debajo de esos valores, y las pruebas verifican 300 operadores seguidos y 50 niveles de paréntesis.

## 7. Pruebas

```
python -m unittest tests.test_parser_expresiones -v
```

| Grupo | Qué comprueba |
|---|---|
| Tabla | 23 no terminales, 31 terminales (30 tokens y EOF) y 106 celdas, como en GIC-6; `esperados` en el orden de las columnas |
| Funciones | Hay una función por cada uno de los 13 no terminales de expresiones, y el docstring de cada una nombra todas sus reglas de la tabla |
| Árboles | La frontera es la expresión; el árbol de `1` coincide con el ejemplo de `arbol.md`; el MULT queda debajo del SUMA, los operadores de `10 - 4 - 2` quedan en la cadena de `<suma_prima>` en el orden del texto (como en la sección 7.2 de `recursividad.md`), el `y` queda debajo del `o` y los paréntesis vuelven a `<expresion>`; cada nodo tiene exactamente los hijos de su regla; 300 operadores y 50 paréntesis anidados |
| Referencia LL(1) | Un analizador con pila, independiente del parser, como el de las trazas de GIC-6, sobre todas las cadenas de hasta 4 tokens de un alfabeto de 10 (11 111 cadenas) y las 17 expresiones de los programas de ejemplo: el parser acepta y rechaza exactamente las mismas, aplica las mismas reglas en el mismo orden y, cuando rechaza, se detiene en el mismo token |
| Errores | Los cuatro casos de la sección 5: posición, contexto, esperados (que son la fila de la tabla) y mensaje |
| Restricciones | `parser.py` no importa `re`, y dentro de la clase `Parser` toda comparación con texto fijo es con una etiqueta de regla de la tabla |

Resultado: **21 pruebas, todas correctas.** Con las de LXR-1, LXR-2 y PAR-1, la suite tiene 75 pruebas y todas pasan:

```
python -m unittest tests.test_lexer tests.test_errores_lexicos tests.test_arbol tests.test_parser_expresiones -v
```
