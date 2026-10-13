# Fase 1 — AFD parciales de los tokens variables

**Tarea Jira:** AFD-2 — AFD parciales de tokens variables
**Responsable:** Daniel Josué Narváez Hincapié
**Insumo:** ER de los tokens variables (`er_tokens_variables.md`, ER-2)
**Grafos:** `afd/afd2_tokens_variables.drawio` (una página por AFD) y sus imágenes en `afd/img/`

---

## 1. Convención

- Los estados se nombran q0, q1, q2…; q0 es siempre el estado inicial.
- En los grafos, el doble círculo marca un estado de aceptación y debajo se indica el token que reconoce.
- **No se usa estado sumidero**, por indicación de la profesora. La función de transición δ es parcial: una celda vacía (—) significa que no existe transición para ese par (estado, símbolo).
- Una cadena se **rechaza** en dos casos: (a) llega un símbolo sin transición desde el estado actual, o (b) la cadena termina en un estado que no es de aceptación.
- Para no escribir 55 columnas, las tablas agrupan los símbolos por los conjuntos de ER-2: L (26 letras), D (10 dígitos), C = L,D,_,␣ (contenido de cadena), K = Σ excepto \n y \r (contenido de comentario) y B = ␣,\t,\n,\r (blancos). Una transición con el nombre de un conjunto significa una transición con **cada** símbolo de ese conjunto. Los símbolos de Σ que no aparecen como columna no tienen transición.
- Cada AFD parcial se define como M = (Q, Σ, δ, q0, F), con Σ el alfabeto completo de `alfabeto.md`.

## 2. Cómo se traducen los operadores de la ER al grafo

| Operador en la ER | Traducción en el grafo | Dónde se ve |
| --- | --- | --- |
| Concatenación `ab` | Estados en serie: a lleva a un estado y b sale de ese estado | `"` seguido de `(C)*` en CADENA |
| Unión `a,b` | Varias transiciones que salen del mismo estado | Desde q1 en NUM: con D vuelve a q1, con `.` va a q2 |
| Cerradura de Kleene `(X)*` | **Lazo con X sobre el estado actual**, sin crear estado nuevo. Como admite cero repeticiones, se puede salir del estado sin haber usado el lazo | `(L,D,_)*` en ID, `(C)*` en CADENA, `(K)*` en COMENTARIO |
| Cerradura positiva `(X)+` | **Transición con X hacia un estado nuevo y lazo con X sobre ese estado nuevo**, porque `(X)+ = X(X)*`: la primera repetición es obligatoria y las demás son opcionales | `(D)+` en NUM, `(B)+` en BLANCO |

Que el estado con el lazo sea o no de aceptación no depende del `*` o el `+`, sino de **lo que sigue en la ER**. En ID y COMENTARIO, `(X)*` está al final de la ER, así que el estado del lazo es de aceptación. En CADENA, después de `(C)*` todavía falta la comilla de cierre, así que el estado del lazo (q1) **no** es de aceptación.

## 3. AFD de ID

**ER:** `(L)(L,D,_)*`

M_ID = ({q0, q1}, Σ, δ, q0, {q1})

| Estado | L | D | _ |
| --- | --- | --- | --- |
| → q0 | q1 | — | — |
| \* q1 | q1 | q1 | q1 |

(→ estado inicial, \* estado de aceptación)

**Construcción:** `(L)` es una transición obligatoria de q0 a q1. `(L,D,_)*` es un lazo en q1 con las 37 letras, dígitos y guion bajo.

**Estados:**
- q0 no es de aceptación: la cadena vacía no es un identificador.
- q1 es de aceptación (ID): ya se leyó la letra inicial obligatoria, y la cerradura `*` admite que la cadena termine ahí.

**Trazas:**

| Cadena | Recorrido | Resultado |
| --- | --- | --- |
| `lote_2` | q0 →l→ q1 →o→ q1 →t→ q1 →e→ q1 →_→ q1 →2→ q1 | Aceptada: termina en q1 ∈ F |
| `2kilos` | q0 →2→ (sin transición) | Rechazada: D no tiene transición desde q0 |
| `_lote` | q0 →_→ (sin transición) | Rechazada: `_` no tiene transición desde q0 |

## 4. AFD de ENTERO y DECIMAL

**ER:** `NUM = (D)+(ε, .(D)+)`, que es la unión factorizada de `ENTERO = (D)+` y `DECIMAL = (D)+.(D)+`.

M_NUM = ({q0, q1, q2, q3}, Σ, δ, q0, {q1, q3})

| Estado | D | . |
| --- | --- | --- |
| → q0 | q1 | — |
| \* q1 | q1 | q2 |
| q2 | q3 | — |
| \* q3 | q3 | — |

**Construcción:**
- El primer `(D)+` es la transición q0 →D→ q1 más el lazo D en q1.
- La unión `(ε, .(D)+)` sale de q1. La rama ε significa quedarse en q1, que por eso es de aceptación. La rama `.(D)+` es q1 →.→ q2 y luego un segundo `(D)+`: q2 →D→ q3 con lazo D en q3.

**Estados:**
- q1 es de aceptación (ENTERO): se leyó al menos un dígito.
- q2 **no** es de aceptación: se leyó el punto, pero `(D)+` exige al menos un dígito después de él.
- q3 es de aceptación (DECIMAL): ya hay dígitos a ambos lados del punto.
- q0 no es de aceptación: la cadena vacía no es un número.

**Trazas:**

| Cadena | Recorrido | Resultado |
| --- | --- | --- |
| `320` | q0 →3→ q1 →2→ q1 →0→ q1 | Aceptada como ENTERO |
| `11.5` | q0 →1→ q1 →1→ q1 →.→ q2 →5→ q3 | Aceptada como DECIMAL |
| `12.` | q0 →1→ q1 →2→ q1 →.→ q2 | Rechazada: termina en q2 ∉ F |
| `.5` | q0 →.→ (sin transición) | Rechazada: `.` no tiene transición desde q0 |

Con la regla del lexema más largo, ante `12.` el analizador léxico retrocede al último estado de aceptación visitado (q1): emite ENTERO `12`, y el punto queda como error léxico.

## 5. AFD de CADENA

**ER:** `"(C)*"`

M_CAD = ({q0, q1, q2}, Σ, δ, q0, {q2})

| Estado | " | C |
| --- | --- | --- |
| → q0 | q1 | — |
| q1 | q2 | q1 |
| \* q2 | — | — |

**Construcción:** la comilla inicial es q0 →"→ q1. `(C)*` es un lazo con C en q1. La comilla final es q1 →"→ q2.

**Estados:**
- q1 **no** es de aceptación: la cadena está abierta y falta la comilla de cierre. Es el caso en que el lazo de un `*` queda sobre un estado de no aceptación, porque en la ER todavía sigue un símbolo obligatorio.
- q2 es de aceptación (CADENA): la cadena se cerró. No tiene transiciones de salida, así que el lexema termina obligatoriamente en la comilla de cierre.

**Trazas:**

| Cadena | Recorrido | Resultado |
| --- | --- | --- |
| `"lote_2"` | q0 →"→ q1 →l,o,t,e,_,2→ q1 →"→ q2 | Aceptada |
| `""` | q0 →"→ q1 →"→ q2 | Aceptada (cero repeticiones del lazo) |
| `"secar` | q0 →"→ q1 →s,e,c,a,r→ q1 | Rechazada: termina en q1 ∉ F |
| `"kilos;"` | q0 →"→ q1 →k,i,l,o,s→ q1 →;→ (sin transición) | Rechazada: `;` ∉ C |

## 6. AFD de COMENTARIO

**ER:** `#(K)*`

M_COM = ({q0, q1}, Σ, δ, q0, {q1})

| Estado | # | K |
| --- | --- | --- |
| → q0 | q1 | — |
| \* q1 | q1 | q1 |

El símbolo `#` también pertenece a K, por eso en q1 aparece en ambas columnas con el mismo destino. En la tabla global (AFD-3) las columnas se reorganizarán en grupos disjuntos.

**Construcción:** `#` es la transición q0 →#→ q1. `(K)*` es un lazo con K en q1.

**Estados:**
- q1 es de aceptación (COMENTARIO): tras el `#`, cualquier cantidad de símbolos de K, incluso cero, forma un comentario válido.
- Desde q1 solo `\n` y `\r` no tienen transición. Por eso el comentario termina justo al final de la línea, sin necesidad de una transición explícita de cierre.

**Trazas:**

| Cadena | Recorrido | Resultado |
| --- | --- | --- |
| `# total = 5;` | q0 →#→ q1 →(␣,t,o,t,a,l,␣,=,␣,5,;)→ q1 | Aceptada |
| `#` | q0 →#→ q1 | Aceptada (cero repeticiones) |
| `simula` | q0 →s→ (sin transición) | Rechazada: falta el `#` inicial |

## 7. AFD de BLANCO

**ER:** `(␣,\t,\n,\r)+`, es decir `(B)+`

M_BLA = ({q0, q1}, Σ, δ, q0, {q1})

| Estado | B |
| --- | --- |
| → q0 | q1 |
| \* q1 | q1 |

**Construcción:** es el patrón de `(X)+`: la primera repetición es la transición q0 →B→ q1 y las siguientes son el lazo B en q1.

**Estados:** q1 es de aceptación (BLANCO); q0 no lo es, porque `+` exige al menos un blanco.

**Trazas:**

| Cadena | Recorrido | Resultado |
| --- | --- | --- |
| `\r\n` | q0 →\r→ q1 →\n→ q1 | Aceptada |
| `␣a` | q0 →␣→ q1 →a→ (sin transición) | Rechazada |
| ε | Se queda en q0 | Rechazada: q0 ∉ F |

## 8. Resumen

| AFD | Estados | Aceptación | No aceptación | Lazos |
| --- | --- | --- | --- | --- |
| ID | 2 | q1 (ID) | q0 | q1 con L, D, _ |
| NUM | 4 | q1 (ENTERO), q3 (DECIMAL) | q0, q2 | q1 y q3 con D |
| CADENA | 3 | q2 (CADENA) | q0, q1 | q1 con C |
| COMENTARIO | 2 | q1 (COMENTARIO) | q0 | q1 con K |
| BLANCO | 2 | q1 (BLANCO) | q0 | q1 con B |

## 9. Insumos para AFD-3 (AFD global)

- Al unir los AFD parciales, todos los q0 se funden en un único estado inicial y los demás estados se renumeran.
- El AFD de ID se solapa con los AFD de palabras reservadas de AFD-1: ambos empiezan con una letra. En el AFD global, los estados que aceptan una palabra reservada deben tener también transiciones hacia el camino de ID con letras, dígitos y `_` (catálogo, Regla 2).
- Las columnas de la matriz global deben formar una partición de Σ en grupos disjuntos. Por ejemplo, `#` irá en su propia columna y no dentro de K.
