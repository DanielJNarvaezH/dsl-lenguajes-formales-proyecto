# Fase 1 — Definición formal del alfabeto Σ de Cafetal

## Convención de notación
- En las ER del curso, ( ) * + y la coma son metasímbolos (agrupación/concatenación,
  cerradura de Kleene, cerradura positiva y unión). Cuando estos caracteres son
  **símbolos del lenguaje Cafetal**, se escriben entre comillas simples:
  '(' ')' '*' '+'. Esta convención se usa desde Σ y en todas las fases.
- Cafetal no usa llaves { } ni coma, por lo que no chocan con la notación de conjuntos.
- ␣ denota el espacio en blanco; \t la tabulación; \n el salto de línea;
  \r el retorno de carro (presente en archivos guardados en Windows).

## Subconjuntos auxiliares

**Letras (minúsculas):**
L = {a, b, c, d, e, f, g, h, i, j, k, l, m, n, o, p, q, r, s, t, u, v, w, x, y, z}
|L| = 26

**Dígitos:**
D = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9}
|D| = 10

**Símbolos de operadores:**
O = {'+', -, '*', /, <, >, =, !}
|O| = 8

**Símbolos de puntuación:**
P = {'(', ')', ;, ., ", #, _}
|P| = 7

**Símbolos blancos (separadores):**
B = {␣, \t, \n, \r}
|B| = 4

## Alfabeto

Σ = L ∪ D ∪ O ∪ P ∪ B

Como los subconjuntos son disjuntos dos a dos:
|Σ| = 26 + 10 + 8 + 7 + 4 = 55

Σ por extensión:
Σ = {a, b, c, d, e, f, g, h, i, j, k, l, m, n, o, p, q, r, s, t, u, v, w, x, y, z,
     0, 1, 2, 3, 4, 5, 6, 7, 8, 9,
     '+', -, '*', /, <, >, =, !,
     '(', ')', ;, ., ", #, _,
     ␣, \t, \n, \r}

## Subconjunto auxiliar para cadenas y comentarios

El contenido de una cadena y de un comentario está restringido a:
C = L ∪ D ∪ {_, ␣}      |C| = 38

C ⊂ Σ. Las comillas " no pertenecen a C (delimitan la cadena) y \n no pertenece
a C (termina el comentario).

## Función de cada símbolo

| Símbolo | Uso en Cafetal |
|---|---|
| L | identificadores, palabras reservadas, contenido de cadenas y comentarios |
| D | números, identificadores (después de la primera letra), cadenas y comentarios |
| '+' - '*' / | operadores aritméticos |
| < > = ! | relacionales (solos o combinados: <= >= == !=) y asignación (=) |
| '(' ')' | agrupación de expresiones y condiciones, argumento de mostrar |
| ; | fin de sentencia |
| . | punto decimal |
| " | delimitador de cadenas |
| # | inicio de comentario |
| _ | identificadores, cadenas y comentarios |
| B | separadores; \n además cierra un comentario |

## Símbolos que NO pertenecen a Σ

Mayúsculas (A–Z), vocales con tilde, ñ, dos puntos, coma, llaves, corchetes,
apóstrofo y cualquier otro carácter. Si un archivo .cft contiene un símbolo x ∉ Σ,
el analizador léxico lo reporta como **error léxico** (el AFD pasa al estado de rechazo).

## Separación alfabeto / léxico / gramática

- Σ contiene **solo caracteres individuales**.
- Los tokens (palabras reservadas como `mientras`, operadores compuestos como `<=`,
  identificadores, números y cadenas) son **cadenas de Σ\*** y se definen con
  expresiones regulares en LEX-3.
- Los no terminales de la GIC (por ejemplo `<expresion>`) no son símbolos de Σ;
  la gramática trabaja sobre los tokens, no sobre los caracteres.