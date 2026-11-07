# Fase 3 — Analizador sintáctico descendente recursivo

Este documento describe `src/parser/parser.py`. Lo completan tres tareas:

| Sección | Tarea | Responsable |
|---|---|---|
| 1 a 7 | PAR-2 — Base común del parser y funciones de expresiones | Daniel Josué Narváez Hincapié |
| 8 a 10 | PAR-3 — Funciones de sentencias y programa | Juan Diego García Albarracín |
| 11 a 14 | PAR-4 — Manejo de errores sintácticos | Daniel Josué Narváez Hincapié |

**Insumos:** gramática final (`docs/fase2/factorizacion.md`, sección 6), tabla LL(1) (`src/parser/tabla_ll1.csv` y `docs/fase2/primero_siguiente_ll1.md`, GIC-6), `src/parser/arbol.py` y `docs/fase3/arbol.md` (PAR-1)
**Archivos de PAR-2:** `src/parser/parser.py` (base común y expresiones) y `tests/test_parser_expresiones.py`
**Archivos de PAR-3:** `src/parser/parser.py` (sección «Programa y sentencias (PAR-3)») y `tests/test_parser_sentencias.py`
**Archivos de PAR-4:** `src/parser/parser.py` (base común y una línea en cada función), `src/parser/siguiente.csv`, `tests/test_errores_sintacticos.py`, `tests/errores/sintactico1_expresiones.cft`, `sintactico2_sentencias.cft` y `sintactico3_bloques.cft`, y `docs/fase3/diagramas/par4_modo_panico.drawio`

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
| `_error(esperados, contexto)` | En PAR-2 lanzaba `ErrorSintactico`. Desde PAR-4 registra el error en `errores` y el análisis se recupera (sección 11); con `detener_en_error=True` lo sigue lanzando |
| `analizar()` | Analiza un programa completo: `programa()` y después `verificar_fin()`. Desde PAR-3 analiza cualquier archivo `.cft` |
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

Desde PAR-4, estos mismos errores se registran y el análisis continúa (sección 11). Las pruebas de esta sección usan `detener_en_error=True`, que conserva el comportamiento de PAR-2.

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

Resultado: **21 pruebas, todas correctas.**

## 8. Funciones de programa y sentencias (PAR-3)

Están al final de la clase `Parser`, en la sección «Programa y sentencias (PAR-3)», con la misma forma de las de expresiones (sección 1): predecir, crear el nodo, recorrer el lado derecho y devolver el nodo. Encima de cada función está su regla BNF como comentario, y la misma regla está en su docstring.

| Función | Reglas | Lado derecho que escribe |
|---|---|---|
| `programa` | P1 | `emparejar("INICIO")`, `sentencias()`, `emparejar("FIN")` |
| `sentencias` | R1, R2 | R1: `sentencia()`, `sentencias()` · R2: ε |
| `sentencia` | P4 a P8 | P4: `declaracion()` · P5: `asignacion()` · P6: `salida()` · P7: `condicional()` · P8: `ciclo()` |
| `declaracion` | D1 | `emparejar("DATO")`, `emparejar("ID")`, `emparejar("ASIGNACION")`, `expresion()`, `emparejar("PUNTO_COMA")` |
| `asignacion` | A1 | `emparejar("ID")`, `emparejar("ASIGNACION")`, `expresion()`, `emparejar("PUNTO_COMA")` |
| `salida` | M1 | `emparejar("MOSTRAR")`, `emparejar("PAR_ABRE")`, `argumento()`, `emparejar("PAR_CIERRA")`, `emparejar("PUNTO_COMA")` |
| `argumento` | M2, M3 | M2: `expresion()` · M3: `emparejar("CADENA")` |
| `condicional` | F4 | `emparejar("SI")`, `emparejar("PAR_ABRE")`, `expresion()`, `emparejar("PAR_CIERRA")`, `emparejar("ENTONCES")`, `sentencias()`, `condicional_prima()` |
| `condicional_prima` | F5, F6 | F5: `emparejar("FIN")` · F6: `emparejar("SINO")`, `sentencias()`, `emparejar("FIN")` |
| `ciclo` | L1 | `emparejar("MIENTRAS")`, `emparejar("PAR_ABRE")`, `expresion()`, `emparejar("PAR_CIERRA")`, `emparejar("HACER")`, `sentencias()`, `emparejar("FIN")` |

Algunas observaciones:

- **Entrada/salida.** La tarea habla de entrada/salida, pero Cafetal solo tiene `mostrar`: GIC-2 (sección 1) ya documentó que no hay instrucción de lectura, porque los datos se escriben en el programa con `dato`. Por eso la única sentencia de este grupo es `salida`.
- **`sentencia` elige entre cinco reglas con la etiqueta.** Las cinco tienen la misma forma (un solo no terminal), pero cada una llama a una función distinta, así que se usa una cadena `if regla == "P4" … elif …` en vez de un diccionario: se lee igual que las reglas P4 a P8 de la BNF.
- **`condicional_prima` termina siempre con FIN.** F5 y F6 terminan en FIN, así que el `emparejar("FIN")` va después del `if`, para las dos reglas. Es la forma que mostraba la sección 4.
- **`sentencias` aplica R2 con FIN o SINO.** Es su SIGUIENTE (GIC-6, sección 6.4). Cuando aparece un SINO que no corresponde a ningún `si`, `sentencias` aplica R2 igual, y el error aparece un paso después, al emparejar el FIN que se esperaba (sección 9.3).
- **El sino colgante no necesita ninguna regla especial.** Cada `si` cierra con su propio `fin` dentro de F5 o F6, así que la función no tiene que decidir a qué `si` pertenece un `sino`: lo decide la tabla, como se demostró en GIC-3 (sección 6.3) y GIC-5 (sección 5.1).

Con estas funciones, los 23 no terminales de la tabla tienen su función, y `Parser(tokens).analizar()` analiza un archivo completo:

```python
from src.lexer.lexer import AnalizadorLexico
from src.parser.parser import Parser

tokens = AnalizadorLexico().analizar_archivo("ejemplos/ejemplo3_secado.cft")
arbol = Parser(tokens).analizar()
print(arbol.derivacion_izquierda())
```

El punto de entrada por línea de comandos, que une lexer, parser y salida, es de PAR-5.

## 9. Comportamiento con programas completos

### 9.1 Programas de ejemplo

Los tres programas de `ejemplos/` se analizan sin errores. La frontera de cada árbol es la lista de tokens sin EOF, y la cantidad de reglas aplicadas coincide con las trazas del analizador LL(1) con pila de GIC-6 (sección 12 de `primero_siguiente_ll1.md`: los pasos totales menos los emparejamientos de tokens y el paso de aceptación; por ejemplo, 241 − 66 − 1 = 174):

| Programa | Tokens | Reglas aplicadas |
|---|---|---|
| `ejemplo1_produccion.cft` | 66 | 174 |
| `ejemplo2_clasificacion.cft` | 62 | 134 |
| `ejemplo3_secado.cft` | 57 | 165 |

En `ejemplo3_secado.cft`, las ocho sentencias quedan en este orden de preorden: dos declaraciones, el ciclo y, dentro de él, la asignación, el condicional (con su `mostrar`) y la otra asignación, y al final el `mostrar` del programa.

### 9.2 Ejemplo: `si (a) entonces x = 1; sino x = 2; fin`

| Paso | Función | Token actual | M[A, token] | Qué hace |
|---|---|---|---|---|
| 1 | `sentencia` | SI | P7 | Llama a `condicional` |
| 2 | `condicional` | SI | F4 | Empareja SI y PAR_ABRE, llama a `expresion()` (R3 … R5 con `a`), empareja PAR_CIERRA y ENTONCES |
| 3 | `sentencias` | ID `x` | R1 | `sentencia()` → P5 → `asignacion()` (A1: `x = 1;`) |
| 4 | `sentencias` | SINO | R2 | ε: SINO ∈ SIGUIENTE(`<sentencias>`) |
| 5 | `condicional_prima` | SINO | F6 | Empareja SINO, llama a `sentencias()` |
| 6 | `sentencias` | ID `x` | R1 | `x = 2;` |
| 7 | `sentencias` | FIN | R2 | ε |
| 8 | `condicional_prima` | — | — | Empareja FIN |

F6 se elige recién en el paso 5, cuando llega SINO, y no al comienzo del condicional: eso es lo que permitió la factorización de GIC-5.

### 9.3 Errores en sentencias

Hasta PAR-4, el primer error detiene el análisis (sección 5). Estos son los casos que verifican las pruebas:

| Entrada | Dónde se detecta | Esperados |
|---|---|---|
| archivo vacío | `predecir("<programa>")` con EOF | INICIO |
| `inicio x = 1;` (falta el `fin`) | `predecir("<sentencias>")` con EOF | La fila de `<sentencias>`: FIN, DATO, SI, SINO, MIENTRAS, MOSTRAR e ID |
| `inicio x = 1 fin` (falta el `;`) | `predecir("<termino_prima>")` con FIN: FIN no puede seguir a una expresión | La fila de `<termino_prima>` |
| `inicio dato si = 3; fin` | `emparejar("ID")` con SI (GIC-1, sección 3) | ID |
| `inicio sino fin` | `emparejar("FIN")` de P1, después de que `sentencias` aplicó R2 con SINO | FIN |
| `inicio mientras (a) entonces fin fin` | `emparejar("HACER")` con ENTONCES | HACER |
| `inicio mostrar(); fin` | `predecir("<argumento>")` con PAR_CIERRA | La fila de `<argumento>` |
| `inicio fin fin` | `verificar_fin()` | el fin del archivo |
| `inicio si (a) entonces si (b) entonces x = 1; sino x = 2; fin fin` (falta un `fin`) | El primer FIN cierra el `si` interno (F6) y el segundo, el externo (F5); el programa queda sin su `fin` y el error aparece en `predecir("<sentencias>")` con EOF | La fila de `<sentencias>` |

Por ejemplo, para `inicio`, `  mientras (a) entonces fin` y `fin` en tres líneas:

```
Error sintáctico en la línea 2, columna 16: se esperaba HACER y se encontró 'entonces' (ENTONCES).
```

### 9.4 Límite de anidamiento de las sentencias

`<sentencias>` es recursiva por la derecha (R1), así que cada sentencia de una lista agrega una llamada de Python, y cada bloque anidado (`si` o `mientras`) agrega unas tres (`sentencias`, `sentencia` y `condicional` o `ciclo`). Con el límite de recursión por defecto (1 000), se midió que el parser analiza unas **980 sentencias seguidas** y unos **320 bloques anidados**. Igual que en la sección 6, los programas de Cafetal quedan muy por debajo, y las pruebas verifican 500 sentencias seguidas y 100 bloques anidados.

## 10. Pruebas de PAR-3

```
python -m unittest tests.test_parser_sentencias -v
```

| Grupo | Qué comprueba |
|---|---|
| Funciones | Una función por cada uno de los 10 no terminales de programa y sentencias, con todas sus reglas en el docstring; con PAR-2, los 23 no terminales de la tabla tienen función |
| Programas de ejemplo | Los tres programas: la frontera es la entrada sin EOF, las reglas coinciden con el analizador LL(1) con pila (174, 134 y 165) y cada nodo tiene exactamente los hijos de su regla; estructura de las sentencias del secado y del cuerpo de su ciclo |
| Árboles de PAR-1 | El parser construye exactamente los dos árboles que PAR-1 armó regla por regla (`inicio x = 1; fin` y un `si … sino … fin`) |
| Sentencias | Programa vacío; las cinco reglas de `<sentencia>`; `mostrar` con cadena y con expresión; bloques vacíos con y sin `sino`; las dos lecturas del sino colgante y el texto al que le falta un `fin`; anidamiento de `mientras` y `si`; 500 sentencias y 100 bloques anidados |
| Referencia LL(1) | El mismo algoritmo con pila de PAR-2, con la gramática completa: todos los programas `inicio w fin` con w de hasta 4 tokens de un alfabeto de 12 (22 621 programas) y 300 programas generados al azar desde `<programa>` con 2 variantes de un token cambiado cada uno. El parser acepta y rechaza exactamente lo mismo, aplica las mismas reglas en el mismo orden y, cuando rechaza, se detiene en el mismo token |
| Errores | Los casos de la sección 9.3: contexto, esperados (fila de la tabla), posición y mensaje |

La prueba de restricciones de PAR-2 (sección 7) también cubre estas funciones: revisa toda la clase `Parser`, y todas las comparaciones de PAR-3 son con etiquetas de regla.

Resultado: **24 pruebas, todas correctas.** Con las de LXR-1, LXR-2, PAR-1 y PAR-2, la suite tiene 99 pruebas y todas pasan:

```
python -m unittest tests.test_lexer tests.test_errores_lexicos tests.test_arbol tests.test_parser_expresiones tests.test_parser_sentencias -v
```

## 11. Manejo de errores sintácticos (PAR-4)

### 11.1 Qué cambia

Hasta PAR-3, el primer error sintáctico detenía el análisis. Con PAR-4, el parser **registra cada error, se recupera en modo pánico y sigue analizando**, de modo que en una sola pasada lista varios errores, en el orden del texto:

```python
parser = Parser(tokens)
arbol = parser.analizar()
for error in parser.errores:
    print(error)
```

Cada error es un `ErrorSintactico`, el mismo de PAR-2: el token esperado (o la lista de esperados) frente al encontrado, con su línea y su columna. Con `Parser(tokens, detener_en_error=True)` se conserva el comportamiento de PAR-2 y PAR-3, igual que `detener_en_error` en el analizador léxico (LXR-2).

`analizar()` siempre devuelve un árbol. Si `errores` no está vacío, el árbol está incompleto: tiene nodos de regla `ERROR`, que son no terminales que no se pudieron derivar, y hojas de lexema vacío, que son terminales que faltaban. Mostrar el árbol solo cuando no hay errores, o el listado de errores en caso contrario, es decisión de `main.py` (PAR-5); el enunciado pide «el árbol de derivación sintáctica o el listado de errores».

### 11.2 Datos que usa la recuperación

| Dato | Origen |
|---|---|
| SIGUIENTE(A) de cada no terminal | `src/parser/siguiente.csv`, copiado de la sección 6.4 de `primero_siguiente_ll1.md` (GIC-6). Las pruebas lo vuelven a calcular desde la gramática y comprueban que coincide |
| Con qué tokens puede empezar A | La fila de A en la tabla LL(1): si M[A, t] tiene regla, A puede continuar con t |
| `ANCLAJE` = {DATO, SI, MIENTRAS, MOSTRAR, SINO, FIN} | Las palabras que empiezan una sentencia o terminan un bloque (sección 11.3) |

### 11.3 Recuperación en `predecir`: modo pánico con SIGUIENTE

Cuando la celda M[A, t] está vacía:

1. Se registra el error: se esperaba cualquiera de la fila de A y se encontró t.
2. **Se descartan tokens** mientras el token actual no sea EOF, A no pueda empezar con él y no esté en SIGUIENTE(A) ∪ ANCLAJE.
3. Si ahora A puede empezar con el token, M[A, t] tiene regla y A se deriva normalmente.
4. Si no, el token está en SIGUIENTE(A) o es de anclaje: **A se omite**. Su función devuelve `omitido(A)`, un nodo con regla `ERROR` y sin hijos, y la función que la llamó sigue con ese mismo token, que es justamente uno que puede venir después de A.

Para el paso 4, cada una de las 23 funciones empieza ahora así:

```python
regla = self.predecir("<factor>")
if regla is None:                       # PAR-4: no se pudo derivar
    return self.omitido("<factor>")
nodo = Nodo.no_terminal("<factor>", regla)
```

Es el único cambio en las funciones de PAR-2 y PAR-3: el resto de cada función no cambia.

**Por qué el anclaje.** Con SIGUIENTE(A) solo, un error dentro de una expresión puede descartar la sentencia siguiente. Por ejemplo, en `x = 1` seguido de `fin`, SIGUIENTE(`<termino_prima>`) no contiene FIN, así que el `fin` se descartaría y el análisis llegaría al final del archivo con errores falsos. Aho et al. (2006, sección 4.4.5) recomiendan agregar al conjunto de sincronización de una construcción los símbolos que empiezan las construcciones de nivel superior. En Cafetal son las palabras que empiezan una sentencia y las que terminan un bloque. Todas están en la fila de `<sentencias>`, así que siempre hay una función abierta que puede usarlas. ID no se incluye porque también aparece dentro de las expresiones, y ENTONCES y HACER tampoco, porque solo los usa la cabecera de un bloque: fuera de ella, el parser quedaría detenido en el mismo token.

**Ejemplo:** `inicio x = a < b < c; z = 2; fin`.

| Paso | Qué pasa |
|---|---|
| 1 | Después de `a < b`, `conjuncion_prima` recibe el segundo `<`: M[`<conjuncion_prima>`, MENOR] está vacía. Error: se esperaba Y, O, PAR_CIERRA o PUNTO_COMA |
| 2 | Se descartan `<` y `c`; el `;` está en SIGUIENTE(`<conjuncion_prima>`) |
| 3 | M[`<conjuncion_prima>`, PUNTO_COMA] = R8: se aplica ε y el análisis sigue |
| 4 | `asignacion` empareja el `;` y la sentencia `z = 2;` se analiza normalmente |

Resultado: un solo error, en la línea 1, columna 18.

### 11.4 Recuperación en `emparejar`: token que falta o que sobra

Cuando la regla pide el terminal T y el token actual t es otro:

1. Se registra el error: se esperaba T y se encontró t.
2. **Si el token siguiente es T, t sobra:** se descarta y se empareja T.
3. **Si no, T falta:** se supone insertado. `emparejar` devuelve una hoja de T con lexema vacío y no consume t, que queda para el resto de la regla.

| Entrada | Caso | Qué hace |
|---|---|---|
| `inicio sino fin` | SINO sobra antes del FIN del programa | Descarta SINO y empareja FIN |
| `inicio x 1; fin` | Falta el `=` | Supone el `=` y sigue con `1;` |
| `inicio dato si = 3; fin` | Falta el ID (SI no puede ser variable) | Supone el ID; luego, al emparejar el `=`, ve que SI sobra y lo descarta. Se reporta un solo error |

Estas dos acciones (insertar o borrar un token) son la recuperación a nivel de frase que describen Aho et al. (2006, sección 4.4.5) para un terminal en la cima de la pila del analizador predictivo.

### 11.5 Errores en cascada

Después de un error, varias funciones pueden encontrar tokens inesperados por el mismo error mientras el parser se recupera. Por eso, **después de un error no se registra otro hasta que se empareje correctamente algún token.** Por ejemplo, en `mostrar(;` seguido de `dato = 4;` en la línea siguiente, el error real es el `;` sin argumento. Después, `salida` no encuentra el `)` ni el `;`, pero esos avisos se suprimen porque son consecuencia del primero. El siguiente error, `dato = 4` sin identificador, sí se registra, porque antes se emparejó DATO.

### 11.6 Por qué la recuperación siempre termina

Cada error termina en una de cuatro acciones: descartar tokens (paso 2 de 11.3), omitir un no terminal (paso 4), descartar un token sobrante o suponer uno faltante (11.4). Las acciones que no consumen tokens, omitir y suponer, avanzan en la regla que se está analizando, y una regla tiene un lado derecho finito. Toda recursión, directa (`sentencias`, `negacion` y las cuatro `_prima`) o indirecta (`factor` → `expresion`, y `condicional` o `ciclo` → `sentencias`), pasa por una regla que la tabla eligió con el token actual, y el primer terminal de esa regla es justamente ese token: se empareja y se consume antes de volver a llamar. Así, cada vuelta consume al menos un token. Por eso el análisis siempre llega al final del archivo. Las pruebas lo comprueban con miles de programas inválidos (sección 13).

## 12. Ejemplos

### 12.1 Un error real, un error reportado

| Entrada | Error reportado |
|---|---|
| `inicio x = 1 fin` | Columna 14, `fin`: falta el `;` (sincroniza con FIN, de anclaje) |
| `inicio mientras (a) entonces x = 1; fin fin` | Columna 21: se esperaba HACER y se encontró `entonces`. El cuerpo del ciclo se analiza igual |
| `inicio si (a entonces x = 1; fin fin` | Columna 14, `entonces`: falta el `)` |
| `inicio x = (a + ; z = 1; fin` | Columna 17, `;`: falta un operando |
| `inicio x = a b c; fin` | Columna 14, `b`: operando de más |
| `inicio mostrar("a" + 1); fin` | Columna 20, `+`: una CADENA solo puede ser todo el argumento de `mostrar` |
| `inicio x = 1;` | Columna 14: falta el `fin` del programa |

### 12.2 Programas con varios errores

Los tres archivos nuevos de `tests/errores/` no tienen errores léxicos y sí varios errores sintácticos, en líneas distintas. Junto con los tres de LXR-2, completan los seis programas con errores que pide TST-2.

| Archivo | Línea | Columna | Encontrado | Error |
|---|---|---|---|---|
| `sintactico1_expresiones.cft` | 4 | 28 | `;` | `(kilos + ;`: falta un operando |
| | 5 | 26 | `*` | `kilos * * 2`: dos operadores seguidos |
| | 6 | 20 | `<` | `kilos < 10 < 20`: relacionales encadenados |
| | 10 | 5 | `mostrar` | Falta el `;` al final de la línea 9: se detecta en el primer token de la línea 10 |
| `sintactico2_sentencias.cft` | 3 | 10 | `si` | `dato si = 3;`: palabra reservada como variable |
| | 4 | 13 | `12` | `humedad 12;`: falta el `=` |
| | 5 | 29 | `entonces` | `mientras (…) entonces`: se esperaba HACER |
| | 8 | 13 | `)` | `mostrar();`: falta el argumento |
| | 9 | 5 | `sino` | `sino` sin `si` |
| `sintactico3_bloques.cft` | 4 | 8 | `dia` | `si dia == 1 entonces`: falta el `(` |
| | 4 | 17 | `entonces` | … y también el `)` |
| | 15 | 1 | fin del archivo | El `si … sino` de la línea 7 no tiene su `fin`: el último `fin` lo cierra y el programa queda sin el suyo |

Por ejemplo, para `sintactico2_sentencias.cft`:

```
Error sintáctico en la línea 3, columna 10: se esperaba ID y se encontró 'si' (SI).
Error sintáctico en la línea 4, columna 13: se esperaba ASIGNACION y se encontró '12' (ENTERO).
Error sintáctico en la línea 5, columna 29: se esperaba HACER y se encontró 'entonces' (ENTONCES).
Error sintáctico en la línea 8, columna 13: se esperaba NO, ID, ENTERO, DECIMAL, CADENA o PAR_ABRE y se encontró ')' (PAR_CIERRA).
Error sintáctico en la línea 9, columna 5: se esperaba FIN y se encontró 'sino' (SINO).
```

### 12.3 Limitaciones

El modo pánico es una heurística: garantiza que el análisis termina y que el primer error es exacto, pero no siempre adivina la intención del programador.

- **Un error puede ocultar una sentencia.** En `x = 1` seguido de `z = 2;` en la línea siguiente, falta el `;` de la primera línea, y la recuperación descarta `z = 2` hasta el `;`. Se reporta un solo error, en `z`, pero `z = 2` no se analiza por separado.
- **Un error puede producir otro real.** En `si dia == 1 entonces`, faltan los dos paréntesis, y se reportan los dos.
- **Un `sino` o un `fin` de más en el nivel del programa termina el análisis.** El `fin` que sobra cierra el programa, y lo que queda después solo produce el error «se esperaba el fin del archivo».

## 13. Pruebas de PAR-4

```
python -m unittest tests.test_errores_sintacticos -v
```

| Grupo | Qué comprueba |
|---|---|
| SIGUIENTE | `siguiente.csv` coincide con SIGUIENTE calculado desde la gramática con el algoritmo de punto fijo de GIC-6; el anclaje está contenido en la fila de `<sentencias>` y no incluye ID |
| Recuperación | 14 entradas con un error real cada una producen exactamente un error, con su token, línea y columna; un programa con tres errores en líneas distintas; la cabecera sin paréntesis; el texto del mensaje (esperado frente a encontrado); el árbol con nodos ERROR y hojas insertadas; el modo `detener_en_error` |
| Archivos con errores | Los tres archivos de la sección 12.2 producen exactamente esos errores, en orden y sin errores léxicos |
| Sin errores | Los tres programas de `ejemplos/` no tienen errores, y el árbol es igual al del modo que se detiene |
| Propiedades | Todos los programas `inicio w fin` con w de hasta 3 tokens de un alfabeto de 16 (4 369 programas) y 300 variantes de los programas de ejemplo con 1 a 4 tokens cambiados. En todos, el análisis llega al final; hay errores si y solo si el modo que se detiene encuentra uno; el primer error es el mismo; y los errores están en el orden del texto, cada uno en un token distinto. Al menos una variante tiene varios errores |

Las pruebas de PAR-2 y PAR-3 que esperan que el primer error detenga el análisis ahora crean el parser con `detener_en_error=True`. Es el único cambio en esos archivos, como hizo LXR-2 con las de LXR-1.

Resultado: **12 pruebas, todas correctas.** Con las anteriores, la suite tiene 111 pruebas y todas pasan:

```
python -m unittest discover -s tests -t . -v
```
