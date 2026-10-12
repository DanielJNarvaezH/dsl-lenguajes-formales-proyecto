# Fase 1 — Expresiones regulares de los tokens fijos

## Convención
- Unión: coma (a,b). Concatenación: yuxtaposición o paréntesis (ab, (a)(b)).
- ε denota la cadena vacía.
- Los símbolos de Σ que coinciden con metasímbolos se escriben entre comillas
  simples: '(' ')' '*' '+' (ver alfabeto.md).
- Cada token fijo tiene un único lexema, por lo que su ER usa solo concatenación
  y su lenguaje es un conjunto unitario. La unión se usa para agrupar tokens de
  una categoría y para factorizar prefijos comunes.

## 1. Palabras reservadas

| Token | ER | Lenguaje |
|---|---|---|
| INICIO | inicio | {inicio} |
| FIN | fin | {fin} |
| DATO | dato | {dato} |
| SI | si | {si} |
| ENTONCES | entonces | {entonces} |
| SINO | sino | {sino} |
| MIENTRAS | mientras | {mientras} |
| HACER | hacer | {hacer} |
| MOSTRAR | mostrar | {mostrar} |
| Y | y | {y} |
| O | o | {o} |
| NO | no | {no} |

ER de la categoría (unión de las 12):
PR = inicio, fin, dato, si, entonces, sino, mientras, hacer, mostrar, y, o, no

ER factorizada por prefijos comunes:
PR = inicio, fin, dato, s i(ε, no), entonces, m(ientras, ostrar), hacer, y, o, no

- si / sino: comparten el prefijo "si". Después de leer "si", si sigue "no"
  el lexema es SINO; si no, es SI.
- mientras / mostrar: comparten el prefijo "m" y se separan en el segundo símbolo
  (i u o).

## 2. Operadores aritméticos

| Token | ER | Lenguaje |
|---|---|---|
| MAS | '+' | {+} |
| MENOS | - | {-} |
| POR | '*' | {*} |
| DIV | / | {/} |

OP_ARIT = '+', -, '*', /

## 3. Operadores relacionales y asignación

| Token | ER | Lenguaje |
|---|---|---|
| MENOR | < | {<} |
| MENOR_IGUAL | <= | {<=} |
| MAYOR | > | {>} |
| MAYOR_IGUAL | >= | {>=} |
| IGUAL | == | {==} |
| DIFERENTE | != | {!=} |
| ASIG | = | {=} |

ER factorizadas por prefijo común:

| Prefijo | ER factorizada | Lenguaje | Token según la rama |
|---|---|---|---|
| < | <(ε, =) | {<, <=} | ε → MENOR, = → MENOR_IGUAL |
| > | >(ε, =) | {>, >=} | ε → MAYOR, = → MAYOR_IGUAL |
| = | =(ε, =) | {=, ==} | ε → ASIG, = → IGUAL |
| ! | != | {!=} | solo DIFERENTE |

Observación: "!" pertenece a Σ, pero "!" solo NO es un token. En el AFD, el
estado alcanzado después de leer "!" es de no aceptación; si el siguiente
símbolo no es "=", se produce un error léxico.

## 4. Delimitadores

| Token | ER | Lenguaje |
|---|---|---|
| PAR_ABRE | '(' | {(} |
| PAR_CIERRA | ')' | {)} |
| PUNTO_COMA | ; | {;} |

DELIM = '(', ')', ;

Los símbolos . " # no son tokens por sí solos: forman parte de los números
decimales, las cadenas y los comentarios (ver ER-2).

## 5. Resolución de prefijos comunes

1. **Factorización en la ER**: un prefijo común se escribe una sola vez y la
   unión se aplica a lo que sigue, por ejemplo <(ε, =). Esto corresponde en el
   AFD a un único estado tras leer "<", que es de aceptación (MENOR) y además
   tiene una transición con "=" hacia otro estado de aceptación (MENOR_IGUAL).
2. **Coincidencia más larga**: el analizador léxico avanza mientras exista
   transición y emite el token del último estado de aceptación alcanzado.
    - "<=" → MENOR_IGUAL (no MENOR + ASIG)
    - "==" → IGUAL (no ASIG + ASIG)
    - "sino" → SINO (no SI + NO)
    - "< =" → MENOR, ASIG (el espacio corta el lexema)
3. **Palabras reservadas e identificadores**: toda palabra reservada también
   cumple la forma de un identificador. Se aplica la coincidencia más larga y,
   si el lexema completo es exactamente una palabra reservada, gana la palabra
   reservada: "si" → SI, pero "sinos" o "si2" → ID. La ER de identificadores
   se define en ER-2.