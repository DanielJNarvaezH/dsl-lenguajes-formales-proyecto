# Fase 1 — AFD global del analizador léxico de Cafetal

**Tarea Jira:** AFD-3 — Unificación en el AFD global del analizador léxico
**Responsable:** Daniel Josué Narváez Hincapié
**Insumos:** AFD parciales de tokens fijos (`afd_tokens_fijos.md`, AFD-1) y de tokens variables (`afd_tokens_variables.md`, AFD-2)
**Grafo:** `afd/afd3_global.drawio` y su imagen en `afd/img/`

---

## 1. Convención y observación sobre el estado de rechazo

- Los estados se nombran q0, q1, q2…; q0 es el único estado inicial.
- δ es una **función parcial**: una celda vacía (—) significa que no existe transición para ese par (estado, símbolo).

> **Observación (indicación de la profesora).** El AFD global no incluye estado sumidero ni estado ∅. Como las expresiones regulares están bien definidas, no es necesario: una cadena se rechaza cuando llega un símbolo sin transición desde el estado actual o cuando termina en un estado que no es de aceptación. Este AFD parcial es equivalente al AFD completo que se obtendría agregando un estado de no aceptación q∅, con todas las transiciones faltantes dirigidas hacia él y un lazo con todos los símbolos de Σ; ambos reconocen el mismo lenguaje.

## 2. Método de unificación

**Paso 1: unión de los AFD parciales.** Se toman los 8 AFD parciales:
- los 3 de AFD-1: palabras reservadas, operadores y delimitadores;
- los 5 de AFD-2: ID, NUM, CADENA, COMENTARIO y BLANCO.

Sus estados iniciales se funden en un único q0. El resultado es un **autómata no determinista**, porque desde algunos estados un mismo símbolo lleva a dos destinos. Por ejemplo, desde q0 la letra `i` lleva tanto al camino de INICIO como al estado de ID.

**Paso 2: construcción de subconjuntos.** Como en la conversión AFN → AFD de clase, cada estado del AFD global representa el conjunto de estados parciales en los que podría estar el autómata. Por ejemplo, después de leer `i` el autómata está a la vez en "segundo estado de INICIO" y en "estado de ID". Ese par se convierte en un solo estado del AFD global, q1.

**Resultado:** las únicas colisiones aparecen con **letras**, entre el AFD de palabras reservadas y el de ID. Todos los demás AFD parciales empiezan con símbolos distintos (dígitos, `"`, `#`, blancos, operadores y delimitadores), así que se unen sin conflicto.

## 3. Numeración de los estados

Los estados q0–q63 conservan la numeración de AFD-1, para que los grafos de Diego sigan siendo válidos. Los estados de AFD-2 se renumeran a continuación:

| AFD parcial (AFD-2) | Estado parcial | Estado global | Token que acepta |
| --- | --- | --- | --- |
| ID | q1 | q64 | ID |
| NUM | q1 | q65 | ENTERO |
| NUM | q2 | q66 | (no acepta: punto sin dígitos después) |
| NUM | q3 | q67 | DECIMAL |
| CADENA | q1 | q68 | (no acepta: cadena abierta) |
| CADENA | q2 | q69 | CADENA |
| COMENTARIO | q1 | q70 | COMENTARIO |
| BLANCO | q1 | q71 | BLANCO |

El estado q0 de cada AFD parcial pasa a ser el q0 global.

## 4. Definición formal

M = (Q, Σ, δ, q0, F)

- **Q** = {q0, q1, …, q71}, |Q| = 72
- **Σ** = alfabeto de `alfabeto.md`, |Σ| = 55
- **q0** = estado inicial único
- **δ** = función parcial definida en la sección 5
- **F** = Q − {q0, q59, q66, q68}, |F| = 68

| Estados de aceptación | Cantidad | Token |
| --- | --- | --- |
| q6, q9, q13, q15, q17, q25, q33, q39, q44, q45, q46, q48 | 12 | La palabra reservada que terminan (INICIO, FIN, DATO, SI, SINO, ENTONCES, MIENTRAS, MOSTRAR, HACER, Y, O, NO) |
| q1–q5, q7, q8, q10–q12, q14, q16, q18–q24, q26–q32, q34–q38, q40–q43, q47 | 36 | ID (prefijos de palabras reservadas, ver sección 7) |
| q49–q58, q60–q63 | 14 | Operadores, asignación y delimitadores, según AFD-1 |
| q64 | 1 | ID |
| q65, q67 | 2 | ENTERO, DECIMAL |
| q69 | 1 | CADENA |
| q70 | 1 | COMENTARIO |
| q71 | 1 | BLANCO |

| Estados de no aceptación | Motivo |
| --- | --- |
| q0 | La cadena vacía no es un token |
| q59 | Se leyó `!`, que solo es válido seguido de `=` |
| q66 | Se leyó un número y un punto; DECIMAL exige un dígito después |
| q68 | Se abrió una cadena y falta la comilla de cierre |

## 5. Función de transición

Abreviaturas: L = letras minúsculas, D = dígitos, B = {␣, \t, \n, \r}, C = L ∪ D ∪ {_, ␣}, K = Σ − {\n, \r}. "Resto de L ∪ D ∪ {_}" significa todas las letras, dígitos y el guion bajo que no aparecen en otra transición del mismo estado.

### 5.1 Desde el estado inicial q0

| Símbolo | Destino | Símbolo | Destino |
| --- | --- | --- | --- |
| `i` | q1 | D | q65 |
| `f` | q7 | `"` | q68 |
| `d` | q10 | `#` | q70 |
| `s` | q14 | B | q71 |
| `e` | q18 | `'+'` | q49 |
| `m` | q26 | `-` | q50 |
| `h` | q40 | `'*'` | q51 |
| `y` | q45 | `/` | q52 |
| `o` | q46 | `<` | q53 |
| `n` | q47 | `>` | q55 |
| Las otras 16 letras | q64 | `=` | q57 |
| | | `!` | q59 |
| | | `'('`, `')'`, `;` | q61, q62, q63 |

Desde q0 no hay transición con `_` ni con `.`: un identificador no puede empezar con guion bajo y un número no puede empezar con punto.

### 5.2 Camino de las palabras reservadas

Cada estado tiene la transición que continúa la palabra reservada. **Todo el resto de L ∪ D ∪ {_} va a q64 (ID)**, y los demás símbolos no tienen transición.

| Estado | Continúa con | Estado | Continúa con |
| --- | --- | --- | --- |
| q1 | `n` → q2 | q24 | `s` → q25 |
| q2 | `i` → q3 | q25 | (ninguna) |
| q3 | `c` → q4 | q26 | `i` → q27, `o` → q34 |
| q4 | `i` → q5 | q27 | `e` → q28 |
| q5 | `o` → q6 | q28 | `n` → q29 |
| q6 | (ninguna) | q29 | `t` → q30 |
| q7 | `i` → q8 | q30 | `r` → q31 |
| q8 | `n` → q9 | q31 | `a` → q32 |
| q9 | (ninguna) | q32 | `s` → q33 |
| q10 | `a` → q11 | q33 | (ninguna) |
| q11 | `t` → q12 | q34 | `s` → q35 |
| q12 | `o` → q13 | q35 | `t` → q36 |
| q13 | (ninguna) | q36 | `r` → q37 |
| q14 | `i` → q15 | q37 | `a` → q38 |
| q15 | `n` → q16 | q38 | `r` → q39 |
| q16 | `o` → q17 | q39 | (ninguna) |
| q17 | (ninguna) | q40 | `a` → q41 |
| q18 | `n` → q19 | q41 | `c` → q42 |
| q19 | `t` → q20 | q42 | `e` → q43 |
| q20 | `o` → q21 | q43 | `r` → q44 |
| q21 | `n` → q22 | q44 | (ninguna) |
| q22 | `c` → q23 | q45, q46 | (ninguna) |
| q23 | `e` → q24 | q47 | `o` → q48 |
| | | q48 | (ninguna) |

"(ninguna)" significa que la palabra reservada ya está completa: cualquier letra, dígito o `_` adicional lleva a q64.

### 5.3 Identificadores, números, cadenas, comentarios y blancos

| Estado | Transiciones |
| --- | --- |
| q64 (ID) | L, D, `_` → q64 |
| q65 (ENTERO) | D → q65; `.` → q66 |
| q66 | D → q67 |
| q67 (DECIMAL) | D → q67 |
| q68 | C → q68; `"` → q69 |
| q69 (CADENA) | (ninguna) |
| q70 (COMENTARIO) | K → q70 |
| q71 (BLANCO) | B → q71 |

### 5.4 Operadores y delimitadores

| Estado | Transiciones |
| --- | --- |
| q53 (MENOR) | `=` → q54 |
| q55 (MAYOR) | `=` → q56 |
| q57 (ASIGNACION) | `=` → q58 |
| q59 | `=` → q60 |
| q49–q52, q54, q56, q58, q60–q63 | (ninguna) |

## 6. Verificación del determinismo

Un autómata es determinista si, para cada estado y cada símbolo, existe **a lo sumo una** transición.

1. **Las colisiones de la unión quedaron resueltas.** Las únicas colisiones estaban en las letras desde q0 y desde los estados de palabras reservadas, porque el camino de la palabra reservada y el de ID competían por la misma letra. La construcción de subconjuntos dejó una sola transición por letra: la que continúa la palabra reservada, o q64 si la letra no la continúa.
2. **Los demás AFD parciales no se solapan.** Desde q0 empiezan con símbolos distintos entre sí: D, `"`, `#`, B, operadores y delimitadores. Dentro de cada AFD parcial ya había una sola transición por símbolo.
3. **Partición de Σ en columnas.** Agrupando los símbolos que se comportan igual en los 72 estados, Σ queda dividido en **34 clases disjuntas**, y en cada estado cada clase tiene a lo sumo un destino:

| Tipo | Clases | Símbolos |
| --- | --- | --- |
| Letras que aparecen en palabras reservadas | 14 | `a`, `c`, `d`, `e`, `f`, `h`, `i`, `m`, `n`, `o`, `r`, `s`, `t`, `y` (una clase cada una) |
| Letras que no aparecen en ninguna palabra reservada | 1 | `b`, `g`, `j`, `k`, `l`, `p`, `q`, `u`, `v`, `w`, `x`, `z` |
| Dígitos | 1 | `0`–`9` |
| Guion bajo | 1 | `_` |
| Operadores y delimitadores | 11 | `+`, `-`, `*`, `/`, `<`, `>`, `=`, `!`, `(`, `)`, `;` (una clase cada uno) |
| Punto, comilla y numeral | 3 | `.`, `"`, `#` |
| Blancos | 3 | `␣`, `\t`, y la clase {`\n`, `\r`} |

Total: 14 + 1 + 1 + 1 + 11 + 3 + 3 = 34 clases, que cubren los 55 símbolos de Σ.

Los blancos no forman una sola clase porque se comportan distinto en otros estados: `␣` pertenece al contenido de una cadena (C), `\t` no; y `\n`, `\r` terminan un comentario, mientras `␣` y `\t` no.

## 7. Cómo se distingue una palabra reservada de un identificador

Cada estado del camino de una palabra reservada es el resultado de la construcción de subconjuntos: representa a la vez "voy leyendo la palabra reservada" y "voy leyendo un identificador". Por eso su clasificación sigue tres reglas:

1. **Estado que completa una palabra reservada** (por ejemplo q13 tras `dato`): acepta la **palabra reservada**. El lexema también pertenece al lenguaje de ID, pero la palabra reservada tiene prioridad (catálogo, Regla 2).
2. **Estado intermedio** (por ejemplo q12 tras `dat`): acepta **ID**, porque `dat` es un identificador válido y no es una palabra reservada completa.
3. **Cualquier letra, dígito o `_` que no continúe la palabra reservada** lleva a q64, el estado de ID.

Junto con la regla del lexema más largo, esto produce:

| Entrada | Recorrido | Token |
| --- | --- | --- |
| `dato` | q0 → q10 → q11 → q12 → q13 | DATO |
| `datos` | … → q13 →s→ q64 | ID |
| `dat` | q0 → q10 → q11 → q12 | ID |
| `si` | q0 → q14 → q15 | SI |
| `sino` | … → q15 → q16 → q17 | SINO |
| `sinos` | … → q17 →s→ q64 | ID |
| `mos` | q0 → q26 → q34 → q35 | ID |
| `o` | q0 → q46 | O |
| `oro` | q0 → q46 →r→ q64 →o→ q64 | ID |
| `finca` | q0 → q7 → q8 → q9 →c→ q64 →a→ q64 | ID |
| `entonces2` | … → q25 →2→ q64 | ID |

Así, una variable nunca puede llamarse como una palabra reservada: `dato si = 3;` produce DATO, **SI**, ASIGNACION…, y el analizador sintáctico rechaza la declaración porque esperaba un ID.

## 8. Lexema más largo y retroceso

El analizador léxico avanza mientras exista transición y recuerda el **último estado de aceptación** visitado. Cuando no puede avanzar, emite el token de ese estado y vuelve a q0 desde el símbolo siguiente al lexema emitido. Si no visitó ningún estado de aceptación, reporta un error léxico en el primer símbolo.

| Entrada | Recorrido | Resultado |
| --- | --- | --- |
| `<=` | q0 → q53 → q54 | MENOR_IGUAL |
| `< =` | q0 → q53; `␣` no tiene transición | MENOR; luego BLANCO y ASIGNACION |
| `11.5` | q0 → q65 → q65 → q66 → q67 | DECIMAL |
| `12.` | q0 → q65 → q65 → q66; termina en q66 ∉ F | Retrocede a q65: ENTERO `12`; el `.` queda como error léxico |
| `!␣` | q0 → q59; `␣` no tiene transición | q59 ∉ F y no hubo aceptación: error léxico en `!` |
| `"secar` | q0 → q68 → q68…; termina en q68 ∉ F | Error léxico en `"`; luego se reconoce `secar` como ID |
| `# total = 5;` + salto de línea | q0 → q70 → … → q70; `\n` no tiene transición | COMENTARIO hasta antes del salto de línea |

## 9. Verificación con los programas de ejemplo

Se recorrieron los 3 programas de `ejemplos/` con el AFD global y la regla del lexema más largo. No se produjo **ningún error léxico**, y cada lexema se clasificó igual que en el catálogo de tokens:

| Programa | Errores léxicos | Tokens entregados al parser (sin blancos ni comentarios) |
| --- | --- | --- |
| `ejemplo1_produccion.cft` | 0 | 66 |
| `ejemplo2_clasificacion.cft` | 0 | 62 |
| `ejemplo3_secado.cft` | 0 | 57 |

## 10. Insumos para las siguientes tareas

- **AFD-4 (grafo vectorizado):** el grafo del AFD global está en `afd/afd3_global.drawio`. Dibujar las transiciones de cada estado de palabra reservada hacia q64 daría 1 754 flechas, así que el grafo dibuja los caminos completos de todos los tokens, la transición q0 → q64 con las 16 letras que no inician palabra reservada, y una nota visible que explica los retornos a q64. AFD-4 consiste en revisar ese grafo contra la matriz, ajustar la presentación y exportar la imagen final.
- **AFD-5 (matriz de transiciones):** 72 filas (q0–q71) y 34 columnas (las clases de la sección 6). Cada celda se llena con las transiciones de la sección 5, y las celdas sin transición quedan con —.
- **AFD-6 (justificación):** los estados de aceptación y no aceptación con su motivo están en la sección 4, y las trazas en las secciones 7 y 8.
- **LXR-1 (lexer en Python):** el algoritmo de la sección 8, recorriendo la matriz de AFD-5.
