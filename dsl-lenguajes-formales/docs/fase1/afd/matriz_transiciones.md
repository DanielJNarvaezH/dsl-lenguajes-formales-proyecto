# Fase 1 — Matriz de transiciones δ del AFD de Cafetal

AFD M = (Q, Σ, δ, q0, F), con Q = {q0, …, q71} (|Q| = 72), Σ de `alfabeto.md` (|Σ| = 55),
estado inicial q0 y |F| = 68. La matriz corresponde exactamente al grafo `afd_global.drawio`.

## Observación: sin estado sumidero

Por indicación de la profesora **no se usa estado sumidero**. δ es una función parcial:
las celdas vacías indican que δ(q, a) no está definida y significan **rechazo**.
De las 72 × 55 = 3960 celdas posibles, 1997 tienen transición.

## Convenciones de la tabla

- **→** marca el estado inicial; **\*** marca los estados de aceptación (el token aparece en la última columna de la parte B).
- Los estados intermedios de palabras reservadas (q1–q48 sin palabra completa) aceptan ID.
- `'+'`, `'*'`, `'('` y `')'` van entre comillas simples porque coinciden con metasímbolos de las ER.

## Agrupación de columnas

Se agrupan en una sola columna los símbolos que tienen **la misma transición en todos los estados**.
Cada grupo es la unión que lo define:

| Columna | Símbolos (unión) | Motivo |
|---|---|---|
| a, c, d, e, f, h, i, m, n, o, r, s, t, y | una columna por letra | aparecen en alguna palabra reservada, por lo que se comportan distinto según el estado |
| L₁ | b, g, j, k, l, p, q, u, v, w, x, z | L − {a, c, d, e, f, h, i, m, n, o, r, s, t, y}: no aparecen en ninguna palabra reservada; siempre llevan a ID, cadena o comentario |
| D | 0, 1, 2, 3, 4, 5, 6, 7, 8, 9 | todos los dígitos se comportan igual |
| \n, \r | \n, \r | ambos solo forman BLANCO y cierran comentarios |
| resto | una columna por símbolo | cada uno tiene un comportamiento propio |

En total: 34 columnas que cubren los 55 símbolos de Σ.

Subconjuntos usados en la definición: L = {a, …, z}, D = {0, …, 9}, C = L ∪ D ∪ {_, ␣}, K = Σ − {\n, \r}.

## Parte A — letras, dígitos y guion bajo

| Estado | `a` | `c` | `d` | `e` | `f` | `h` | `i` | `m` | `n` | `o` | `r` | `s` | `t` | `y` | L₁ | D | `_` |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| →q0 | q64 | q64 | q10 | q18 | q7 | q40 | q1 | q26 | q47 | q46 | q64 | q14 | q64 | q45 | q64 | q65 |  |
| \*q1 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q2 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 |
| \*q2 | q64 | q64 | q64 | q64 | q64 | q64 | q3 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 |
| \*q3 | q64 | q4 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 |
| \*q4 | q64 | q64 | q64 | q64 | q64 | q64 | q5 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 |
| \*q5 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q6 | q64 | q64 | q64 | q64 | q64 | q64 | q64 |
| \*q6 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 |
| \*q7 | q64 | q64 | q64 | q64 | q64 | q64 | q8 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 |
| \*q8 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q9 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 |
| \*q9 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 |
| \*q10 | q11 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 |
| \*q11 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q12 | q64 | q64 | q64 | q64 |
| \*q12 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q13 | q64 | q64 | q64 | q64 | q64 | q64 | q64 |
| \*q13 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 |
| \*q14 | q64 | q64 | q64 | q64 | q64 | q64 | q15 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 |
| \*q15 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q16 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 |
| \*q16 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q17 | q64 | q64 | q64 | q64 | q64 | q64 | q64 |
| \*q17 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 |
| \*q18 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q19 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 |
| \*q19 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q20 | q64 | q64 | q64 | q64 |
| \*q20 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q21 | q64 | q64 | q64 | q64 | q64 | q64 | q64 |
| \*q21 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q22 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 |
| \*q22 | q64 | q23 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 |
| \*q23 | q64 | q64 | q64 | q24 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 |
| \*q24 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q25 | q64 | q64 | q64 | q64 | q64 |
| \*q25 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 |
| \*q26 | q64 | q64 | q64 | q64 | q64 | q64 | q27 | q64 | q64 | q34 | q64 | q64 | q64 | q64 | q64 | q64 | q64 |
| \*q27 | q64 | q64 | q64 | q28 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 |
| \*q28 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q29 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 |
| \*q29 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q30 | q64 | q64 | q64 | q64 |
| \*q30 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q31 | q64 | q64 | q64 | q64 | q64 | q64 |
| \*q31 | q32 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 |
| \*q32 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q33 | q64 | q64 | q64 | q64 | q64 |
| \*q33 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 |
| \*q34 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q35 | q64 | q64 | q64 | q64 | q64 |
| \*q35 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q36 | q64 | q64 | q64 | q64 |
| \*q36 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q37 | q64 | q64 | q64 | q64 | q64 | q64 |
| \*q37 | q38 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 |
| \*q38 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q39 | q64 | q64 | q64 | q64 | q64 | q64 |
| \*q39 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 |
| \*q40 | q41 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 |
| \*q41 | q64 | q42 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 |
| \*q42 | q64 | q64 | q64 | q43 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 |
| \*q43 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q44 | q64 | q64 | q64 | q64 | q64 | q64 |
| \*q44 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 |
| \*q45 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 |
| \*q46 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 |
| \*q47 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q48 | q64 | q64 | q64 | q64 | q64 | q64 | q64 |
| \*q48 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 |
| \*q49 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| \*q50 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| \*q51 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| \*q52 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| \*q53 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| \*q54 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| \*q55 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| \*q56 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| \*q57 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| \*q58 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| q59 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| \*q60 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| \*q61 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| \*q62 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| \*q63 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| \*q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 | q64 |
| \*q65 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | q65 |  |
| q66 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | q67 |  |
| \*q67 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | q67 |  |
| q68 | q68 | q68 | q68 | q68 | q68 | q68 | q68 | q68 | q68 | q68 | q68 | q68 | q68 | q68 | q68 | q68 | q68 |
| \*q69 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| \*q70 | q70 | q70 | q70 | q70 | q70 | q70 | q70 | q70 | q70 | q70 | q70 | q70 | q70 | q70 | q70 | q70 | q70 |
| \*q71 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

## Parte B — demás símbolos

| Estado | `.` | `"` | `#` | ␣ | \t | \n, \r | `'+'` | `-` | `'*'` | `/` | `<` | `>` | `=` | `!` | `'('` | `')'` | `;` | Token |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| →q0 |  | q68 | q70 | q71 | q71 | q71 | q49 | q50 | q51 | q52 | q53 | q55 | q57 | q59 | q61 | q62 | q63 |  |
| \*q1 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | ID |
| \*q2 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | ID |
| \*q3 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | ID |
| \*q4 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | ID |
| \*q5 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | ID |
| \*q6 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | INICIO |
| \*q7 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | ID |
| \*q8 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | ID |
| \*q9 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | FIN |
| \*q10 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | ID |
| \*q11 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | ID |
| \*q12 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | ID |
| \*q13 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | DATO |
| \*q14 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | ID |
| \*q15 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | SI |
| \*q16 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | ID |
| \*q17 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | SINO |
| \*q18 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | ID |
| \*q19 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | ID |
| \*q20 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | ID |
| \*q21 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | ID |
| \*q22 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | ID |
| \*q23 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | ID |
| \*q24 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | ID |
| \*q25 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | ENTONCES |
| \*q26 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | ID |
| \*q27 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | ID |
| \*q28 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | ID |
| \*q29 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | ID |
| \*q30 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | ID |
| \*q31 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | ID |
| \*q32 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | ID |
| \*q33 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | MIENTRAS |
| \*q34 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | ID |
| \*q35 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | ID |
| \*q36 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | ID |
| \*q37 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | ID |
| \*q38 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | ID |
| \*q39 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | MOSTRAR |
| \*q40 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | ID |
| \*q41 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | ID |
| \*q42 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | ID |
| \*q43 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | ID |
| \*q44 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | HACER |
| \*q45 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | Y |
| \*q46 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | O |
| \*q47 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | ID |
| \*q48 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | NO |
| \*q49 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | MAS |
| \*q50 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | MENOS |
| \*q51 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | POR |
| \*q52 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | DIV |
| \*q53 |  |  |  |  |  |  |  |  |  |  |  |  | q54 |  |  |  |  | MENOR |
| \*q54 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | MENOR_IGUAL |
| \*q55 |  |  |  |  |  |  |  |  |  |  |  |  | q56 |  |  |  |  | MAYOR |
| \*q56 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | MAYOR_IGUAL |
| \*q57 |  |  |  |  |  |  |  |  |  |  |  |  | q58 |  |  |  |  | ASIG |
| \*q58 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | IGUAL |
| q59 |  |  |  |  |  |  |  |  |  |  |  |  | q60 |  |  |  |  |  |
| \*q60 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | DIFERENTE |
| \*q61 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | PAR_ABRE |
| \*q62 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | PAR_CIERRA |
| \*q63 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | PUNTO_COMA |
| \*q64 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | ID |
| \*q65 | q66 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | ENTERO |
| q66 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| \*q67 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | DECIMAL |
| q68 |  | q69 |  | q68 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| \*q69 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | CADENA |
| \*q70 | q70 | q70 | q70 | q70 | q70 |  | q70 | q70 | q70 | q70 | q70 | q70 | q70 | q70 | q70 | q70 | q70 | COMENTARIO |
| \*q71 |  |  |  | q71 | q71 | q71 |  |  |  |  |  |  |  |  |  |  |  | BLANCO |

## Conjunto de aceptación

F = {q1, q2, q3, q4, q5, q6, q7, q8, q9, q10, q11, q12, q13, q14, q15, q16, q17, q18, q19, q20, q21, q22, q23, q24, q25, q26, q27, q28, q29, q30, q31, q32, q33, q34, q35, q36, q37, q38, q39, q40, q41, q42, q43, q44, q45, q46, q47, q48, q49, q50, q51, q52, q53, q54, q55, q56, q57, q58, q60, q61, q62, q63, q64, q65, q67, q69, q70, q71}

Estados de no aceptación: q0 (inicial), q59 (leyó `!`), q66 (leyó `.` sin dígitos después), q68 (cadena sin cerrar).

## Justificación de aceptación y rechazo

- Un estado está en F si y solo si la cadena leída desde q0 es un lexema completo de algún token.
- Si δ(q, a) está vacía y q ∈ F, el token termina en q (coincidencia más larga) y el analizador vuelve a q0 con el símbolo a.
- Si δ(q, a) está vacía y q ∉ F, se produce un error léxico. Ejemplos: `!␣` (q59), `12.␣` (q66), `"abc` + salto de línea (q68).
- Todo símbolo que no pertenece a Σ (mayúsculas, tildes, ñ, `:`, `,`, …) no tiene columna; en q0 produce error léxico.

## Archivo CSV

La tabla completa, sin agrupar (72 filas × 55 símbolos), está en `src/lexer/tabla_afd.csv`:
- Columna `estado`, luego una columna por símbolo de Σ y al final `token` (vacía si el estado no es de aceptación).
- Los blancos se nombran `ESP` (espacio), `TAB`, `LF` (\n) y `CR` (\r).
- Celda vacía = sin transición = rechazo.
- Codificación UTF-8, separador coma (la coma no pertenece a Σ, así que no hay ambigüedad).
