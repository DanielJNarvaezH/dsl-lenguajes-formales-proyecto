# Fase 1 — Justificación de los estados de aceptación y rechazo

**Tarea Jira:** AFD-6 — Justificación de estados de aceptación y rechazo
**Responsable:** Daniel Josué Narváez Hincapié
**Insumos:** AFD global (`afd_global.md`), matriz de transiciones (`matriz_transiciones.md`) y grafo (`afd/afd3_global.drawio`)

---

## 1. Observación sobre el estado de rechazo

Por indicación de la profesora, el AFD **no usa estado sumidero**. La función de transición δ es parcial: una celda vacía en la matriz significa que δ(q, a) no está definida.

Una cadena se **rechaza** en dos casos:

1. **Falta de transición:** llega un símbolo a para el cual δ(q, a) está vacía, y desde el inicio del lexema no se visitó ningún estado de aceptación.
2. **Fin en estado de no aceptación:** la cadena termina en un estado q ∉ F.

Este AFD parcial es equivalente al AFD completo que se obtendría agregando un estado q∅ de no aceptación, con todas las celdas vacías dirigidas hacia él y un lazo con los 55 símbolos de Σ. Ambos reconocen el mismo lenguaje: el sumidero solo daría nombre a un rechazo que ya ocurre.

## 2. Celda vacía: fin de token o rechazo

En un analizador léxico, una celda vacía no siempre significa error. Depende de si el estado actual es de aceptación:

| Situación | Significado | Acción del analizador |
| --- | --- | --- |
| δ(q, a) vacía y **q ∈ F** | El lexema terminó: lo leído es un token completo y `a` pertenece al siguiente | Emite el token de q y vuelve a q0 desde `a` |
| δ(q, a) vacía, q ∉ F, pero **antes se visitó un estado de aceptación** | Lo leído después de ese estado no forma un token | Retrocede al último estado de aceptación, emite su token y continúa desde el símbolo siguiente |
| δ(q, a) vacía, q ∉ F y **no se visitó ningún estado de aceptación** | Ningún prefijo de lo leído es un token | **Error léxico** en el primer símbolo del lexema |

Ejemplo de cada caso:
- `si(`: δ(q15, `'('`) está vacía y q15 ∈ F, así que se emite SI.
- `12.x`: se llega a q66 ∉ F, pero se visitó q65, así que se emite ENTERO `12` y el punto queda en error.
- `!x`: q59 ∉ F y no hubo aceptación, así que hay error léxico en `!`.

## 3. Estados de aceptación: por qué aceptan y qué token devuelven

**Criterio general:** un estado q pertenece a F si y solo si toda cadena que lleva de q0 a q es un lexema completo de algún token. El token que devuelve es el de la ER cuyo lenguaje contiene esa cadena; si hay dos, se aplica la prioridad de palabra reservada sobre identificador (catálogo, Regla 2).

### 3.1 Caminos de las palabras reservadas (q1–q48)

En cada camino, el último estado devuelve la palabra reservada y los anteriores devuelven ID. Lo leído en un estado intermedio es una cadena de letras que empieza por letra, así que pertenece a L((L)(L,D,_)*). Como no es una palabra reservada completa, el token es ID.

| Camino | Estados y cadena leída | Token |
| --- | --- | --- |
| INICIO | q1 `i`, q2 `in`, q3 `ini`, q4 `inic`, q5 `inici` | ID |
| | q6 `inicio` | INICIO |
| FIN | q7 `f`, q8 `fi` | ID |
| | q9 `fin` | FIN |
| DATO | q10 `d`, q11 `da`, q12 `dat` | ID |
| | q13 `dato` | DATO |
| SI / SINO | q14 `s`, q16 `sin` | ID |
| | q15 `si` | SI |
| | q17 `sino` | SINO |
| ENTONCES | q18 `e`, q19 `en`, q20 `ent`, q21 `ento`, q22 `enton`, q23 `entonc`, q24 `entonce` | ID |
| | q25 `entonces` | ENTONCES |
| MIENTRAS | q26 `m`, q27 `mi`, q28 `mie`, q29 `mien`, q30 `mient`, q31 `mientr`, q32 `mientra` | ID |
| | q33 `mientras` | MIENTRAS |
| MOSTRAR | q34 `mo`, q35 `mos`, q36 `most`, q37 `mostr`, q38 `mostra` | ID |
| | q39 `mostrar` | MOSTRAR |
| HACER | q40 `h`, q41 `ha`, q42 `hac`, q43 `hace` | ID |
| | q44 `hacer` | HACER |
| Y | q45 `y` | Y |
| O | q46 `o` | O |
| NO | q47 `n` | ID |
| | q48 `no` | NO |

**Casos que merecen atención:**
- **q15 (SI)** es de aceptación aunque tiene una transición de salida (con `n` hacia q16). Aceptar no significa que el camino termine: si después de `si` llega `no`, el lexema más largo es `sino`; si llega cualquier otro símbolo que no sea letra, dígito ni `_`, el token es SI.
- **q45 (Y) y q46 (O)** son palabras reservadas de una sola letra. Por eso no puede existir una variable llamada `y` ni `o`.
- **Los estados finales de palabras reservadas** (q6, q9, q13…) siguen teniendo transiciones con L, D y `_` hacia q64. Por eso `datos` o `finca` son ID: el lexema más largo ya no es la palabra reservada.

### 3.2 Operadores, asignación y delimitadores (q49–q63)

| Estado | Cadena leída | Token | Por qué acepta |
| --- | --- | --- | --- |
| q49 | `+` | SUMA | Es exactamente el lexema de la ER `'+'` |
| q50 | `-` | RESTA | Lexema de `-` |
| q51 | `*` | MULT | Lexema de `'*'` |
| q52 | `/` | DIV | Lexema de `/` |
| q53 | `<` | MENOR | Lexema de `<`; acepta aunque pueda continuar con `=` (rama ε de `<(ε,=)`) |
| q54 | `<=` | MENOR_IGUAL | Lexema de `<=` (rama `=` de `<(ε,=)`) |
| q55 | `>` | MAYOR | Rama ε de `>(ε,=)` |
| q56 | `>=` | MAYOR_IGUAL | Rama `=` de `>(ε,=)` |
| q57 | `=` | ASIGNACION | Rama ε de `=(ε,=)` |
| q58 | `==` | IGUAL | Rama `=` de `=(ε,=)` |
| q60 | `!=` | DIFERENTE | Lexema completo de `!=` |
| q61 | `(` | PAR_ABRE | Lexema de `'('` |
| q62 | `)` | PAR_CIERRA | Lexema de `')'` |
| q63 | `;` | PUNTO_COMA | Lexema de `;` |

### 3.3 Identificadores y tokens variables (q64–q71)

| Estado | Ejemplos de cadena leída | Token | Por qué acepta |
| --- | --- | --- | --- |
| q64 | `a`, `kilos`, `lote_2`, `datos` | ID | Se leyó una letra inicial y cero o más letras, dígitos o `_`: cumple `(L)(L,D,_)*` y no es una palabra reservada completa |
| q65 | `5`, `320` | ENTERO | Se leyó al menos un dígito: cumple `(D)+` |
| q67 | `11.5`, `0.25` | DECIMAL | Hay al menos un dígito a cada lado del punto: cumple `(D)+.(D)+` |
| q69 | `"secar"`, `""` | CADENA | Se cerró la comilla: cumple `"(C)*"` |
| q70 | `#`, `# total = 5;` | COMENTARIO | Tras `#`, cero o más símbolos de K: cumple `#(K)*` |
| q71 | `␣`, `\r\n` | BLANCO | Al menos un blanco: cumple `(␣,\t,\n,\r)+` |

## 4. Estados de no aceptación: por qué rechazan

| Estado | Cadena leída | Qué le falta | Única forma de continuar (celdas no vacías) | Con cualquier otro símbolo |
| --- | --- | --- | --- | --- |
| q0 | Nada (ε) | Al menos un símbolo: ninguna ER genera la cadena vacía | Todo Σ excepto `_` y `.` | `_` o `.` al inicio: error léxico |
| q59 | `!` | El `=` de `!=`; `!` no es un token por sí solo | `=` → q60 | Error léxico en `!` |
| q66 | Dígitos y `.` | Un dígito después del punto, que exige el segundo `(D)+` | D → q67 | Retrocede a q65 (ENTERO) y el `.` queda en error |
| q68 | `"` y contenido | La comilla de cierre | C → q68, `"` → q69 | Error léxico en la `"` inicial (cadena sin cerrar) |

En q59, q66 y q68 la cadena leída es un **prefijo propio** de un token: le falta algo para pertenecer al lenguaje de su ER. Por eso no pueden aceptar. Si el analizador acabara ahí, estaría entregando un token incompleto.

Los símbolos que no pertenecen a Σ (mayúsculas, tildes, `ñ`, `,`, `:`) no tienen columna en la matriz. Desde cualquier estado su celda está vacía, y desde q0 producen error léxico.

## 5. Trazas a mano sobre la matriz

Cada paso indica la celda consultada en `matriz_transiciones.md`. La **Parte A** contiene las columnas de letras (`a`, `c`, `d`, `e`, `f`, `h`, `i`, `m`, `n`, `o`, `r`, `s`, `t`, `y`, L₁), D y `_`. La **Parte B** contiene `.`, `"`, `#`, ␣, \t, \n/\r, operadores y delimitadores, además de la columna Token.

### Traza 1 (aceptada): `sino`

| Paso | Estado | Símbolo | Celda de la matriz | Nuevo estado | ¿Acepta? |
| --- | --- | --- | --- | --- | --- |
| 1 | q0 | `s` | Parte A, fila q0, columna `s` | q14 | Sí (ID) |
| 2 | q14 | `i` | Parte A, fila q14, columna `i` | q15 | Sí (SI) |
| 3 | q15 | `n` | Parte A, fila q15, columna `n` | q16 | Sí (ID) |
| 4 | q16 | `o` | Parte A, fila q16, columna `o` | q17 | Sí (SINO) |

La cadena termina en q17 ∈ F. Columna Token de la fila q17: **SINO**. En el paso 2 ya se había aceptado SI, pero la regla del lexema más largo continúa mientras haya transición, y por eso el token final es SINO y no SI seguido de NO.

### Traza 2 (aceptada): `lote_2`

| Paso | Estado | Símbolo | Celda de la matriz | Nuevo estado | ¿Acepta? |
| --- | --- | --- | --- | --- | --- |
| 1 | q0 | `l` | Parte A, fila q0, columna L₁ | q64 | Sí (ID) |
| 2 | q64 | `o` | Parte A, fila q64, columna `o` | q64 | Sí (ID) |
| 3 | q64 | `t` | Parte A, fila q64, columna `t` | q64 | Sí (ID) |
| 4 | q64 | `e` | Parte A, fila q64, columna `e` | q64 | Sí (ID) |
| 5 | q64 | `_` | Parte A, fila q64, columna `_` | q64 | Sí (ID) |
| 6 | q64 | `2` | Parte A, fila q64, columna D | q64 | Sí (ID) |

La cadena termina en q64 ∈ F. Columna Token de la fila q64: **ID**. Los pasos 2 a 6 recorren el lazo de q64, que corresponde a `(L,D,_)*`.

### Traza 3 (aceptada): `11.5`

| Paso | Estado | Símbolo | Celda de la matriz | Nuevo estado | ¿Acepta? |
| --- | --- | --- | --- | --- | --- |
| 1 | q0 | `1` | Parte A, fila q0, columna D | q65 | Sí (ENTERO) |
| 2 | q65 | `1` | Parte A, fila q65, columna D | q65 | Sí (ENTERO) |
| 3 | q65 | `.` | Parte B, fila q65, columna `.` | q66 | **No** |
| 4 | q66 | `5` | Parte A, fila q66, columna D | q67 | Sí (DECIMAL) |

La cadena termina en q67 ∈ F. Columna Token de la fila q67: **DECIMAL**. En el paso 3 el autómata pasa por q66, que no acepta, pero la cadena no termina ahí: el dígito siguiente lo lleva de nuevo a un estado de aceptación.

### Traza 4 (rechazada): `!x`

| Paso | Estado | Símbolo | Celda de la matriz | Nuevo estado | ¿Acepta? |
| --- | --- | --- | --- | --- | --- |
| 1 | q0 | `!` | Parte B, fila q0, columna `!` | q59 | **No** |
| 2 | q59 | `x` | Parte A, fila q59, columna L₁ | **vacía** | — |

La celda δ(q59, `x`) está vacía, q59 ∉ F y durante el lexema no se visitó ningún estado de aceptación. Resultado: **error léxico en `!`**. El analizador lo reporta con su línea y columna y continúa desde `x`, que se reconoce como ID. Para negar, Cafetal usa la palabra reservada `no`; el `!` solo es válido como parte de `!=`.

### Traza 5 (rechazada): `"secar` seguido de salto de línea

| Paso | Estado | Símbolo | Celda de la matriz | Nuevo estado | ¿Acepta? |
| --- | --- | --- | --- | --- | --- |
| 1 | q0 | `"` | Parte B, fila q0, columna `"` | q68 | **No** |
| 2 | q68 | `s` | Parte A, fila q68, columna `s` | q68 | No |
| 3 | q68 | `e` | Parte A, fila q68, columna `e` | q68 | No |
| 4 | q68 | `c` | Parte A, fila q68, columna `c` | q68 | No |
| 5 | q68 | `a` | Parte A, fila q68, columna `a` | q68 | No |
| 6 | q68 | `r` | Parte A, fila q68, columna `r` | q68 | No |
| 7 | q68 | `\n` | Parte B, fila q68, columna \n/\r | **vacía** | — |

La celda δ(q68, `\n`) está vacía, porque una cadena no puede ocupar dos líneas. Además, q68 ∉ F y no se visitó ningún estado de aceptación desde la comilla. Resultado: **error léxico en `"`** (cadena sin cerrar). El analizador continúa desde `s` y reconoce `secar` como ID.

## 6. Resumen

| Grupo | Estados | Acepta | Token |
| --- | --- | --- | --- |
| Palabra reservada completa | q6, q9, q13, q15, q17, q25, q33, q39, q44, q45, q46, q48 | Sí | La palabra reservada |
| Prefijo de palabra reservada | q1–q5, q7, q8, q10–q12, q14, q16, q18–q24, q26–q32, q34–q38, q40–q43, q47 | Sí | ID |
| Operadores y delimitadores | q49–q58, q60–q63 | Sí | Su operador o delimitador |
| Tokens variables | q64, q65, q67, q69, q70, q71 | Sí | ID, ENTERO, DECIMAL, CADENA, COMENTARIO, BLANCO |
| Inicio | q0 | No | — |
| Prefijos incompletos | q59, q66, q68 | No | — |

Total: 68 estados de aceptación y 4 de no aceptación, como define F en `afd_global.md` y la matriz.
