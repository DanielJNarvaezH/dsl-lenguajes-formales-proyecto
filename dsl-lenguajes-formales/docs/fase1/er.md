# Fase 1 — Auditoría de las expresiones regulares

**Tarea Jira:** ER-3 — Auditoría de las ER
**Responsable:** Daniel Josué Narváez Hincapié
**Fecha:** 12 de octubre de 2026
**Documentos auditados:** `er_tokens_fijos.md` (ER-1), `er_tokens_variables.md` (ER-2), con referencia a `alfabeto.md` (LEX-2) y `catalogo_tokens.md` (LEX-1)

---

## 1. Propósito

Verificar que todas las expresiones regulares de Cafetal cumplen la notación exigida en el curso y que, en conjunto, reconocen todos los tokens de los programas de ejemplo. Este documento registra el resultado, las correcciones aplicadas y la tabla consolidada de las ER que se usará en el documento final de la Fase 1.

## 2. Criterios y resultados

| # | Criterio | Resultado | Evidencia |
| --- | --- | --- | --- |
| C1 | Solo se usan unión (coma), concatenación (yuxtaposición o paréntesis), `( )*` y `( )+` | Cumple | No aparecen `?`, `{n,m}`, rangos `[a-z]`, clases `\d`, `\w` ni `|` en ninguna ER |
| C2 | Los símbolos de Σ que coinciden con metasímbolos van entre comillas simples | Cumple | `'+'`, `'*'`, `'('` y `')'` aparecen siempre entre comillas cuando son símbolos del lenguaje; los paréntesis sin comillas solo agrupan |
| C3 | Las abreviaturas (L, D, C, K) se definen como uniones explícitas | Cumple | Las cuatro están escritas por extensión en `er_tokens_variables.md`, sección 1 |
| C4 | Cada token del catálogo tiene su ER | Cumple | 26 tokens fijos en ER-1 y 6 tokens variables en ER-2: 32 de 32 |
| C5 | Los nombres de los tokens coinciden con el catálogo | Cumple (tras corrección) | ER-1 usaba `MAS`, `MENOS`, `POR` y `ASIG`; se corrigieron (ver registro de cambios) |
| C6 | Las ER cubren todos los lexemas de los 3 programas de ejemplo | Cumple | Se recorrieron los 3 archivos aplicando la regla del lexema más largo: todos los lexemas pertenecen a alguna ER y aparecen las 32 categorías (sección 5) |
| C7 | Las cadenas aceptadas y rechazadas de ER-2 son correctas | Cumple | Las 36 cadenas de las tablas de ER-2 se verificaron contra su ER: las 18 aceptadas pertenecen al lenguaje y las 18 rechazadas no |
| C8 | Todo símbolo usado en las ER pertenece a Σ | Cumple | Los 55 símbolos de `alfabeto.md` cubren todos los símbolos de las ER; ε no es un símbolo de Σ (sección 3) |
| C9 | Todo símbolo especial usado en las ER está definido en la convención | Cumple (tras corrección) | ER-2 usaba ε sin definirlo en su convención; se agregó |

## 3. Uso de ε (cadena vacía)

Las ER factorizadas usan ε: `si(ε, no)`, `<(ε, =)`, `>(ε, =)`, `=(ε, =)` y `NUM = (D)+(ε, .(D)+)`.

ε **no es un operador**: es una de las ER primitivas básicas, junto con ∅ y cada símbolo de Σ. Los operadores siguen siendo únicamente la unión, la concatenación y las cerraduras. Por eso su uso cumple el criterio C1.

Además, cada ER con ε tiene una equivalente sin ε, obtenida al distribuir la concatenación sobre la unión:

| ER factorizada | Equivalente sin ε | Lenguaje |
| --- | --- | --- |
| si(ε, no) | si, sino | {si, sino} |
| <(ε, =) | <, <= | {<, <=} |
| >(ε, =) | >, >= | {>, >=} |
| =(ε, =) | =, == | {=, ==} |
| (D)+(ε, .(D)+) | (D)+, (D)+.(D)+ | ENTERO ∪ DECIMAL |

Se conserva la forma factorizada porque muestra directamente el prefijo común, que en el AFD se convierte en un único camino compartido con un estado de aceptación intermedio.

## 4. Tabla consolidada de las ER

Abreviaturas (definidas en `er_tokens_variables.md`): L = a,b,…,z (26 letras); D = 0,1,…,9; C = L,D,_,␣; K = todos los símbolos de Σ excepto `\n` y `\r`.

### Palabras reservadas

| Código | Token | ER |
| --- | --- | --- |
| 1 | INICIO | inicio |
| 2 | FIN | fin |
| 3 | DATO | dato |
| 4 | SI | si |
| 5 | ENTONCES | entonces |
| 6 | SINO | sino |
| 7 | MIENTRAS | mientras |
| 8 | HACER | hacer |
| 9 | MOSTRAR | mostrar |
| 10 | Y | y |
| 11 | O | o |
| 12 | NO | no |

### Identificadores y literales

| Código | Token | ER |
| --- | --- | --- |
| 20 | ID | (L)(L,D,_)* |
| 21 | ENTERO | (D)+ |
| 22 | DECIMAL | (D)+.(D)+ |
| 23 | CADENA | "(C)*" |

### Operadores, asignación y delimitadores

| Código | Token | ER |
| --- | --- | --- |
| 30 | SUMA | '+' |
| 31 | RESTA | - |
| 32 | MULT | '*' |
| 33 | DIV | / |
| 40 | MENOR | < |
| 41 | MAYOR | > |
| 42 | MENOR_IGUAL | <= |
| 43 | MAYOR_IGUAL | >= |
| 44 | IGUAL | == |
| 45 | DIFERENTE | != |
| 50 | ASIGNACION | = |
| 60 | PAR_ABRE | '(' |
| 61 | PAR_CIERRA | ')' |
| 62 | PUNTO_COMA | ; |

### Categorías descartables

| Código | Categoría | ER |
| --- | --- | --- |
| 90 | COMENTARIO | #(K)* |
| 91 | BLANCO | (␣,\t,\n,\r)+ |

## 5. Cobertura de los programas de ejemplo

Los 3 programas se recorrieron de principio a fin aplicando el lexema más largo y la prioridad de palabra reservada sobre identificador. No quedó ningún símbolo sin reconocer, y las 32 categorías aparecen al menos una vez:

| Programa | Categorías que aparecen por primera vez |
| --- | --- |
| `ejemplo1_produccion.cft` | INICIO, FIN, DATO, MOSTRAR, ID, ENTERO, DECIMAL, CADENA, SUMA, RESTA, MULT, DIV, ASIGNACION, PAR_ABRE, PAR_CIERRA, PUNTO_COMA, COMENTARIO, BLANCO |
| `ejemplo2_clasificacion.cft` | SI, ENTONCES, SINO, Y, MENOR, MENOR_IGUAL, MAYOR_IGUAL, DIFERENTE |
| `ejemplo3_secado.cft` | MIENTRAS, HACER, O, NO, MAYOR, IGUAL |

Total: 18 + 8 + 6 = 32 categorías.

## 6. Registro de cambios

| # | Tarea | Documento | Cambio | Motivo |
| --- | --- | --- | --- | --- |
| 1 | LEX-1 | Ejemplos y especificación | Cadenas y comentarios en minúscula, sin `:` | Mantener el contenido dentro de Σ |
| 2 | ER-2 | Catálogo, especificación, propuesta | Los comentarios admiten cualquier símbolo de Σ excepto `\n` y `\r` | Un `=` o `;` dentro de un comentario lo cortaba y generaba tokens ocultos |
| 3 | LEX-2 | `alfabeto.md` | Se agrega K = Σ − {\n, \r}; se corrige la referencia a ER-1 y ER-2; el error léxico se describe como ausencia de transición | Coherencia con ER-2 y con la indicación de la profesora de no usar estado sumidero |
| 4 | ER-1 | `er_tokens_fijos.md` | `MAS`, `MENOS`, `POR`, `ASIG` → `SUMA`, `RESTA`, `MULT`, `ASIGNACION`; `s i(ε, no)` → `si(ε, no)` | Criterio C5 y error tipográfico |
| 5 | ER-3 | `er_tokens_variables.md` | Se agrega la definición de ε a la convención | Criterio C9: ER-2 usaba ε sin definirlo |

## 7. Conclusión

Las 32 expresiones regulares de Cafetal usan únicamente unión, concatenación, cerradura de Kleene y cerradura positiva, con los metasímbolos del lenguaje entre comillas simples. Cubren todos los lexemas de los 3 programas de ejemplo y son consistentes con el catálogo de tokens y con el alfabeto Σ. Quedan listas para construir los AFD parciales (AFD-1 y AFD-2).
