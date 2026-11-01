# Fase 2 — Conjuntos PRIMERO y SIGUIENTE y tabla LL(1)

**Tarea Jira:** GIC-6 — Conjuntos PRIMERO y SIGUIENTE y tabla LL(1)
**Responsable:** Juan Diego García Albarracín
**Insumos:** `factorizacion.md` (GIC-5, gramática factorizada de la sección 6), `recursividad.md` (GIC-4) y `ambiguedad.md` (GIC-3)
**Archivo asociado:** `src/parser/tabla_ll1.csv` (tabla LL(1) completa)
**Se complementa con:** DOC-3 (documento de la Fase 2) y PAR-2 a PAR-4 (analizador sintáctico de la Fase 3)

---

## 1. Qué se construye y para qué

Después de GIC-4 y GIC-5, la gramática de Cafetal no tiene recursividad por la izquierda y está factorizada. Falta comprobar que es **LL(1)**: que un analizador que lee la entrada de izquierda a derecha (la primera L), construye una derivación más a la izquierda (la segunda L) y mira **un solo token** por adelantado (el 1) puede elegir siempre la regla correcta sin retroceder (Aho et al., 2006).

Para eso se calculan dos conjuntos por cada no terminal:

- **PRIMERO(α):** los tokens con que puede empezar una cadena derivada desde α. Si α puede derivar la cadena vacía, también contiene ε.
- **SIGUIENTE(A):** los tokens que pueden aparecer inmediatamente después de A en alguna forma sentencial derivada desde `<programa>`. Incluye `EOF` si A puede quedar al final del programa.

Con ellos se construye la **tabla de análisis predictivo** M[A, t]: la regla que el analizador aplica cuando el no terminal A está en la cima de la pila y el siguiente token es t. Si ninguna celda tiene dos reglas, la gramática es LL(1), y toda gramática LL(1) es **no ambigua** (sección 10). Esa tabla es el argumento formal que cierra la Fase 2.

## 2. Notación

- La notación BNF es la misma de GIC-1 a GIC-5: no terminales en minúsculas entre `< >`, terminales con el nombre del token del catálogo en MAYÚSCULAS, `::=`, `|` y ε.
- Los conjuntos se escriben **por extensión con { }**, como en la Fase 1: PRIMERO(`<factor>`) = {PAR_ABRE, ID, ENTERO, DECIMAL}. Cafetal no usa llaves, así que no chocan con ningún símbolo del lenguaje.
- **ε dentro de un conjunto PRIMERO** no es un token: indica que la cadena puede derivar la cadena vacía. Nunca aparece en un conjunto SIGUIENTE ni en la tabla.
- **`EOF`** es el marcador de fin de entrada que agrega el analizador léxico (código 99, Fase 1). Cumple el papel del símbolo $ de la bibliografía.
- Las reglas se citan con las etiquetas de GIC-2, GIC-4 y GIC-5 (P, D, E, R, A, M, F y L).

## 3. Gramática de partida

Es la gramática factorizada de la sección 6 de `factorizacion.md` (GIC-5), sin cambios:

```
P1   <programa> ::= INICIO <sentencias> FIN
R1   <sentencias> ::= <sentencia> <sentencias>
R2   <sentencias> ::= ε
P4   <sentencia> ::= <declaracion>
P5   <sentencia> ::= <asignacion>
P6   <sentencia> ::= <salida>
P7   <sentencia> ::= <condicional>
P8   <sentencia> ::= <ciclo>
D1   <declaracion> ::= DATO ID ASIGNACION <expresion> PUNTO_COMA
R3   <expresion> ::= <conjuncion> <expresion_prima>
R4   <expresion_prima> ::= O <conjuncion> <expresion_prima>
R5   <expresion_prima> ::= ε
R6   <conjuncion> ::= <negacion> <conjuncion_prima>
R7   <conjuncion_prima> ::= Y <negacion> <conjuncion_prima>
R8   <conjuncion_prima> ::= ε
E5   <negacion> ::= NO <negacion>
E6   <negacion> ::= <comparacion>
F1   <comparacion> ::= <suma> <comparacion_prima>
F2   <comparacion_prima> ::= <op_rel> <suma>
F3   <comparacion_prima> ::= ε
E9   <op_rel> ::= MENOR
E10  <op_rel> ::= MAYOR
E11  <op_rel> ::= MENOR_IGUAL
E12  <op_rel> ::= MAYOR_IGUAL
E13  <op_rel> ::= IGUAL
E14  <op_rel> ::= DIFERENTE
R9   <suma> ::= <termino> <suma_prima>
R10  <suma_prima> ::= SUMA <termino> <suma_prima>
R11  <suma_prima> ::= RESTA <termino> <suma_prima>
R12  <suma_prima> ::= ε
R13  <termino> ::= <factor> <termino_prima>
R14  <termino_prima> ::= MULT <factor> <termino_prima>
R15  <termino_prima> ::= DIV <factor> <termino_prima>
R16  <termino_prima> ::= ε
E21  <factor> ::= PAR_ABRE <expresion> PAR_CIERRA
E22  <factor> ::= ID
E23  <factor> ::= ENTERO
E24  <factor> ::= DECIMAL
A1   <asignacion> ::= ID ASIGNACION <expresion> PUNTO_COMA
M1   <salida> ::= MOSTRAR PAR_ABRE <argumento> PAR_CIERRA PUNTO_COMA
M2   <argumento> ::= <expresion>
M3   <argumento> ::= CADENA
F4   <condicional> ::= SI PAR_ABRE <expresion> PAR_CIERRA ENTONCES <sentencias> <condicional_prima>
F5   <condicional_prima> ::= FIN
F6   <condicional_prima> ::= SINO <sentencias> FIN
L1   <ciclo> ::= MIENTRAS PAR_ABRE <expresion> PAR_CIERRA HACER <sentencias> FIN
```

## 4. No terminales anulables

Un no terminal es **anulable** si deriva ε. Se necesita saberlo antes de calcular PRIMERO, porque si el primer símbolo de una regla es anulable, el segundo también puede aportar el primer token.

Son anulables exactamente los seis no terminales que tienen una regla ε:

| No terminal | Regla ε |
|---|---|
| `<sentencias>` | R2 |
| `<expresion_prima>` | R5 |
| `<conjuncion_prima>` | R8 |
| `<comparacion_prima>` | F3 |
| `<suma_prima>` | R12 |
| `<termino_prima>` | R16 |

Ningún otro no terminal es anulable: todas las demás reglas contienen al menos un terminal o empiezan con un no terminal que termina generando un `<factor>`, y `<factor>` siempre produce un token.

## 5. Conjuntos PRIMERO

### 5.1 Reglas de cálculo

1. Si t es un terminal, PRIMERO(t) = {t}.
2. Si A ::= ε es una regla, ε ∈ PRIMERO(A).
3. Para una cadena X₁ X₂ … Xₙ:
   - se agrega PRIMERO(X₁) sin ε;
   - si X₁ es anulable, se agrega también PRIMERO(X₂) sin ε, y así sucesivamente mientras los símbolos anteriores sean anulables;
   - si **todos** los Xᵢ son anulables, se agrega ε.
4. PRIMERO(A) es la unión de PRIMERO del lado derecho de todas las reglas de A.

### 5.2 Cálculo

Se calcula de abajo hacia arriba, empezando por los no terminales cuyas reglas empiezan con un terminal. Así, cuando se necesita PRIMERO de un no terminal, ya está calculado.

| No terminal | Cálculo | PRIMERO |
|---|---|---|
| `<factor>` | E21–E24 empiezan con un terminal | {PAR_ABRE, ID, ENTERO, DECIMAL} |
| `<termino_prima>` | R14, R15 empiezan con MULT y DIV; R16 es ε | {MULT, DIV, ε} |
| `<termino>` | R13: PRIMERO(`<factor>`); `<factor>` no es anulable | {PAR_ABRE, ID, ENTERO, DECIMAL} |
| `<suma_prima>` | R10, R11 empiezan con SUMA y RESTA; R12 es ε | {SUMA, RESTA, ε} |
| `<suma>` | R9: PRIMERO(`<termino>`); `<termino>` no es anulable | {PAR_ABRE, ID, ENTERO, DECIMAL} |
| `<op_rel>` | E9–E14, un relacional cada una | {MENOR, MAYOR, MENOR_IGUAL, MAYOR_IGUAL, IGUAL, DIFERENTE} |
| `<comparacion_prima>` | F2: PRIMERO(`<op_rel>`); F3 es ε | {MENOR, MAYOR, MENOR_IGUAL, MAYOR_IGUAL, IGUAL, DIFERENTE, ε} |
| `<comparacion>` | F1: PRIMERO(`<suma>`); `<suma>` no es anulable | {PAR_ABRE, ID, ENTERO, DECIMAL} |
| `<negacion>` | E5: {NO}; E6: PRIMERO(`<comparacion>`) | {NO, PAR_ABRE, ID, ENTERO, DECIMAL} |
| `<conjuncion_prima>` | R7 empieza con Y; R8 es ε | {Y, ε} |
| `<conjuncion>` | R6: PRIMERO(`<negacion>`); `<negacion>` no es anulable | {NO, PAR_ABRE, ID, ENTERO, DECIMAL} |
| `<expresion_prima>` | R4 empieza con O; R5 es ε | {O, ε} |
| `<expresion>` | R3: PRIMERO(`<conjuncion>`); `<conjuncion>` no es anulable | {NO, PAR_ABRE, ID, ENTERO, DECIMAL} |
| `<argumento>` | M2: PRIMERO(`<expresion>`); M3: {CADENA} | {NO, PAR_ABRE, ID, ENTERO, DECIMAL, CADENA} |
| `<declaracion>` | D1 empieza con DATO | {DATO} |
| `<asignacion>` | A1 empieza con ID | {ID} |
| `<salida>` | M1 empieza con MOSTRAR | {MOSTRAR} |
| `<condicional>` | F4 empieza con SI | {SI} |
| `<condicional_prima>` | F5 empieza con FIN; F6 con SINO | {FIN, SINO} |
| `<ciclo>` | L1 empieza con MIENTRAS | {MIENTRAS} |
| `<sentencia>` | P4–P8: unión de PRIMERO de las cinco sentencias | {DATO, ID, MOSTRAR, SI, MIENTRAS} |
| `<sentencias>` | R1: PRIMERO(`<sentencia>`); R2 es ε | {DATO, ID, MOSTRAR, SI, MIENTRAS, ε} |
| `<programa>` | P1 empieza con INICIO | {INICIO} |

En las reglas que empiezan con un no terminal (R3, R6, R9, R13, F1, R1), ese primer no terminal **no es anulable**, así que el segundo símbolo nunca aporta a PRIMERO. Por eso ninguna de esas reglas necesitó el paso 3 más allá de X₁.

## 6. Conjuntos SIGUIENTE

### 6.1 Reglas de cálculo

1. `EOF` ∈ SIGUIENTE(`<programa>`), porque el programa termina con el fin de la entrada.
2. Para cada regla A ::= α B β, donde B es un no terminal:
   - todo PRIMERO(β), sin ε, se agrega a SIGUIENTE(B): lo que empieza β viene justo después de B;
   - si β es ε o es anulable, todo SIGUIENTE(A) se agrega a SIGUIENTE(B): cuando β desaparece, lo que sigue a A sigue también a B.
3. Se repiten las reglas hasta que ningún conjunto cambie.

### 6.2 Aportes de cada aparición de un no terminal

Cada fila es una aparición de un no terminal B en el lado derecho de una regla. La columna β es lo que va después de B en esa regla.

| Regla | B | β (lo que sigue a B) | PRIMERO(β) sin ε, que va a SIGUIENTE(B) | Inclusión, si β es anulable |
|---|---|---|---|---|
| P1 | `<sentencias>` | FIN | FIN | — |
| R1 | `<sentencia>` | `<sentencias>` | DATO, ID, MOSTRAR, SI, MIENTRAS | SIGUIENTE(`<sentencias>`) ⊆ SIGUIENTE(`<sentencia>`) |
| R1 | `<sentencias>` | ε | — | SIGUIENTE(`<sentencias>`) ⊆ SIGUIENTE(`<sentencias>`) (no aporta) |
| P4 | `<declaracion>` | ε | — | SIGUIENTE(`<sentencia>`) ⊆ SIGUIENTE(`<declaracion>`) |
| P5 | `<asignacion>` | ε | — | SIGUIENTE(`<sentencia>`) ⊆ SIGUIENTE(`<asignacion>`) |
| P6 | `<salida>` | ε | — | SIGUIENTE(`<sentencia>`) ⊆ SIGUIENTE(`<salida>`) |
| P7 | `<condicional>` | ε | — | SIGUIENTE(`<sentencia>`) ⊆ SIGUIENTE(`<condicional>`) |
| P8 | `<ciclo>` | ε | — | SIGUIENTE(`<sentencia>`) ⊆ SIGUIENTE(`<ciclo>`) |
| D1 | `<expresion>` | PUNTO_COMA | PUNTO_COMA | — |
| R3 | `<conjuncion>` | `<expresion_prima>` | O | SIGUIENTE(`<expresion>`) ⊆ SIGUIENTE(`<conjuncion>`) |
| R3 | `<expresion_prima>` | ε | — | SIGUIENTE(`<expresion>`) ⊆ SIGUIENTE(`<expresion_prima>`) |
| R4 | `<conjuncion>` | `<expresion_prima>` | O | SIGUIENTE(`<expresion_prima>`) ⊆ SIGUIENTE(`<conjuncion>`) |
| R4 | `<expresion_prima>` | ε | — | (no aporta: es el mismo conjunto) |
| R6 | `<negacion>` | `<conjuncion_prima>` | Y | SIGUIENTE(`<conjuncion>`) ⊆ SIGUIENTE(`<negacion>`) |
| R6 | `<conjuncion_prima>` | ε | — | SIGUIENTE(`<conjuncion>`) ⊆ SIGUIENTE(`<conjuncion_prima>`) |
| R7 | `<negacion>` | `<conjuncion_prima>` | Y | SIGUIENTE(`<conjuncion_prima>`) ⊆ SIGUIENTE(`<negacion>`) |
| R7 | `<conjuncion_prima>` | ε | — | (no aporta: es el mismo conjunto) |
| E5 | `<negacion>` | ε | — | (no aporta: es el mismo conjunto) |
| E6 | `<comparacion>` | ε | — | SIGUIENTE(`<negacion>`) ⊆ SIGUIENTE(`<comparacion>`) |
| F1 | `<suma>` | `<comparacion_prima>` | MENOR, MAYOR, MENOR_IGUAL, MAYOR_IGUAL, IGUAL, DIFERENTE | SIGUIENTE(`<comparacion>`) ⊆ SIGUIENTE(`<suma>`) |
| F1 | `<comparacion_prima>` | ε | — | SIGUIENTE(`<comparacion>`) ⊆ SIGUIENTE(`<comparacion_prima>`) |
| F2 | `<op_rel>` | `<suma>` | PAR_ABRE, ID, ENTERO, DECIMAL | — |
| F2 | `<suma>` | ε | — | SIGUIENTE(`<comparacion_prima>`) ⊆ SIGUIENTE(`<suma>`) |
| R9 | `<termino>` | `<suma_prima>` | SUMA, RESTA | SIGUIENTE(`<suma>`) ⊆ SIGUIENTE(`<termino>`) |
| R9 | `<suma_prima>` | ε | — | SIGUIENTE(`<suma>`) ⊆ SIGUIENTE(`<suma_prima>`) |
| R10, R11 | `<termino>` | `<suma_prima>` | SUMA, RESTA | SIGUIENTE(`<suma_prima>`) ⊆ SIGUIENTE(`<termino>`) |
| R10, R11 | `<suma_prima>` | ε | — | (no aporta: es el mismo conjunto) |
| R13 | `<factor>` | `<termino_prima>` | MULT, DIV | SIGUIENTE(`<termino>`) ⊆ SIGUIENTE(`<factor>`) |
| R13 | `<termino_prima>` | ε | — | SIGUIENTE(`<termino>`) ⊆ SIGUIENTE(`<termino_prima>`) |
| R14, R15 | `<factor>` | `<termino_prima>` | MULT, DIV | SIGUIENTE(`<termino_prima>`) ⊆ SIGUIENTE(`<factor>`) |
| R14, R15 | `<termino_prima>` | ε | — | (no aporta: es el mismo conjunto) |
| E21 | `<expresion>` | PAR_CIERRA | PAR_CIERRA | — |
| A1 | `<expresion>` | PUNTO_COMA | PUNTO_COMA | — |
| M1 | `<argumento>` | PAR_CIERRA PUNTO_COMA | PAR_CIERRA | — |
| M2 | `<expresion>` | ε | — | SIGUIENTE(`<argumento>`) ⊆ SIGUIENTE(`<expresion>`) |
| F4 | `<expresion>` | PAR_CIERRA ENTONCES … | PAR_CIERRA | — |
| F4 | `<sentencias>` | `<condicional_prima>` | FIN, SINO | — (`<condicional_prima>` no es anulable) |
| F4 | `<condicional_prima>` | ε | — | SIGUIENTE(`<condicional>`) ⊆ SIGUIENTE(`<condicional_prima>`) |
| F6 | `<sentencias>` | FIN | FIN | — |
| L1 | `<expresion>` | PAR_CIERRA HACER … | PAR_CIERRA | — |
| L1 | `<sentencias>` | FIN | FIN | — |

### 6.3 Resolución

Las inclusiones de la última columna siempre van de un no terminal "de arriba" hacia uno "de abajo" en la gramática, y las únicas que van de un conjunto a sí mismo no aportan nada. Por eso basta con resolverlas en orden, de `<programa>` hacia `<factor>`, y una segunda pasada completa no agrega ningún token: se llega al punto fijo de la regla 3.

1. **SIGUIENTE(`<programa>`)** = {EOF}, por la regla 1. `<programa>` no aparece en ningún lado derecho.
2. **SIGUIENTE(`<sentencias>`)** = {FIN} (P1, F6, L1) ∪ {FIN, SINO} (F4) = **{FIN, SINO}**.
3. **SIGUIENTE(`<sentencia>`)** = {DATO, ID, MOSTRAR, SI, MIENTRAS} (R1) ∪ SIGUIENTE(`<sentencias>`) = **{FIN, SINO, DATO, ID, MOSTRAR, SI, MIENTRAS}**.
4. **`<declaracion>`, `<asignacion>`, `<salida>`, `<condicional>` y `<ciclo>`** reciben SIGUIENTE(`<sentencia>`) completo (P4–P8), y no aparecen en ningún otro lugar.
5. **SIGUIENTE(`<condicional_prima>`)** = SIGUIENTE(`<condicional>`) (F4) = el mismo conjunto de 7 tokens.
6. **SIGUIENTE(`<argumento>`)** = **{PAR_CIERRA}** (M1).
7. **SIGUIENTE(`<expresion>`)** = {PUNTO_COMA} (D1, A1) ∪ {PAR_CIERRA} (E21, F4, L1) ∪ SIGUIENTE(`<argumento>`) (M2) = **{PAR_CIERRA, PUNTO_COMA}**.
8. **SIGUIENTE(`<expresion_prima>`)** = SIGUIENTE(`<expresion>`) (R3) = **{PAR_CIERRA, PUNTO_COMA}**.
9. **SIGUIENTE(`<conjuncion>`)** = {O} (R3, R4) ∪ SIGUIENTE(`<expresion>`) ∪ SIGUIENTE(`<expresion_prima>`) = **{O, PAR_CIERRA, PUNTO_COMA}**.
10. **SIGUIENTE(`<conjuncion_prima>`)** = SIGUIENTE(`<conjuncion>`) (R6) = **{O, PAR_CIERRA, PUNTO_COMA}**.
11. **SIGUIENTE(`<negacion>`)** = {Y} (R6, R7) ∪ SIGUIENTE(`<conjuncion>`) ∪ SIGUIENTE(`<conjuncion_prima>`) = **{Y, O, PAR_CIERRA, PUNTO_COMA}**.
12. **SIGUIENTE(`<comparacion>`)** = SIGUIENTE(`<negacion>`) (E6) = **{Y, O, PAR_CIERRA, PUNTO_COMA}**.
13. **SIGUIENTE(`<comparacion_prima>`)** = SIGUIENTE(`<comparacion>`) (F1) = **{Y, O, PAR_CIERRA, PUNTO_COMA}**.
14. **SIGUIENTE(`<op_rel>`)** = PRIMERO(`<suma>`) (F2) = **{PAR_ABRE, ID, ENTERO, DECIMAL}**.
15. **SIGUIENTE(`<suma>`)** = {6 relacionales} (F1) ∪ SIGUIENTE(`<comparacion>`) ∪ SIGUIENTE(`<comparacion_prima>`) = **{MENOR, MAYOR, MENOR_IGUAL, MAYOR_IGUAL, IGUAL, DIFERENTE, Y, O, PAR_CIERRA, PUNTO_COMA}**.
16. **SIGUIENTE(`<suma_prima>`)** = SIGUIENTE(`<suma>`) (R9): los mismos 10 tokens.
17. **SIGUIENTE(`<termino>`)** = {SUMA, RESTA} (R9, R10, R11) ∪ SIGUIENTE(`<suma>`) ∪ SIGUIENTE(`<suma_prima>`): 12 tokens.
18. **SIGUIENTE(`<termino_prima>`)** = SIGUIENTE(`<termino>`) (R13): los mismos 12 tokens.
19. **SIGUIENTE(`<factor>`)** = {MULT, DIV} (R13, R14, R15) ∪ SIGUIENTE(`<termino>`) ∪ SIGUIENTE(`<termino_prima>`): 14 tokens.

### 6.4 Resultado

| No terminal | PRIMERO | SIGUIENTE |
|---|---|---|
| `<programa>` | {INICIO} | {EOF} |
| `<sentencias>` | {DATO, ID, MOSTRAR, SI, MIENTRAS, ε} | {FIN, SINO} |
| `<sentencia>` | {DATO, ID, MOSTRAR, SI, MIENTRAS} | {FIN, SINO, DATO, ID, MOSTRAR, SI, MIENTRAS} |
| `<declaracion>` | {DATO} | {FIN, SINO, DATO, ID, MOSTRAR, SI, MIENTRAS} |
| `<asignacion>` | {ID} | {FIN, SINO, DATO, ID, MOSTRAR, SI, MIENTRAS} |
| `<salida>` | {MOSTRAR} | {FIN, SINO, DATO, ID, MOSTRAR, SI, MIENTRAS} |
| `<argumento>` | {NO, PAR_ABRE, ID, ENTERO, DECIMAL, CADENA} | {PAR_CIERRA} |
| `<condicional>` | {SI} | {FIN, SINO, DATO, ID, MOSTRAR, SI, MIENTRAS} |
| `<condicional_prima>` | {FIN, SINO} | {FIN, SINO, DATO, ID, MOSTRAR, SI, MIENTRAS} |
| `<ciclo>` | {MIENTRAS} | {FIN, SINO, DATO, ID, MOSTRAR, SI, MIENTRAS} |
| `<expresion>` | {NO, PAR_ABRE, ID, ENTERO, DECIMAL} | {PAR_CIERRA, PUNTO_COMA} |
| `<expresion_prima>` | {O, ε} | {PAR_CIERRA, PUNTO_COMA} |
| `<conjuncion>` | {NO, PAR_ABRE, ID, ENTERO, DECIMAL} | {O, PAR_CIERRA, PUNTO_COMA} |
| `<conjuncion_prima>` | {Y, ε} | {O, PAR_CIERRA, PUNTO_COMA} |
| `<negacion>` | {NO, PAR_ABRE, ID, ENTERO, DECIMAL} | {Y, O, PAR_CIERRA, PUNTO_COMA} |
| `<comparacion>` | {PAR_ABRE, ID, ENTERO, DECIMAL} | {Y, O, PAR_CIERRA, PUNTO_COMA} |
| `<comparacion_prima>` | {MENOR, MAYOR, MENOR_IGUAL, MAYOR_IGUAL, IGUAL, DIFERENTE, ε} | {Y, O, PAR_CIERRA, PUNTO_COMA} |
| `<op_rel>` | {MENOR, MAYOR, MENOR_IGUAL, MAYOR_IGUAL, IGUAL, DIFERENTE} | {PAR_ABRE, ID, ENTERO, DECIMAL} |
| `<suma>` | {PAR_ABRE, ID, ENTERO, DECIMAL} | {MENOR, MAYOR, MENOR_IGUAL, MAYOR_IGUAL, IGUAL, DIFERENTE, Y, O, PAR_CIERRA, PUNTO_COMA} |
| `<suma_prima>` | {SUMA, RESTA, ε} | {MENOR, MAYOR, MENOR_IGUAL, MAYOR_IGUAL, IGUAL, DIFERENTE, Y, O, PAR_CIERRA, PUNTO_COMA} |
| `<termino>` | {PAR_ABRE, ID, ENTERO, DECIMAL} | {SUMA, RESTA, MENOR, MAYOR, MENOR_IGUAL, MAYOR_IGUAL, IGUAL, DIFERENTE, Y, O, PAR_CIERRA, PUNTO_COMA} |
| `<termino_prima>` | {MULT, DIV, ε} | {SUMA, RESTA, MENOR, MAYOR, MENOR_IGUAL, MAYOR_IGUAL, IGUAL, DIFERENTE, Y, O, PAR_CIERRA, PUNTO_COMA} |
| `<factor>` | {PAR_ABRE, ID, ENTERO, DECIMAL} | {MULT, DIV, SUMA, RESTA, MENOR, MAYOR, MENOR_IGUAL, MAYOR_IGUAL, IGUAL, DIFERENTE, Y, O, PAR_CIERRA, PUNTO_COMA} |

Los conjuntos SIGUIENTE de las expresiones crecen hacia abajo en la jerarquía. Es la estratificación de GIC-3 vista desde otro ángulo: después de un `<factor>` puede venir cualquier operador de un nivel igual o inferior, mientras que después de una `<expresion>` completa solo puede venir el cierre de la sentencia o del paréntesis.

## 7. Conjunto de predicción de cada regla

El **conjunto de predicción** de una regla A ::= α son los tokens con los que el analizador debe elegirla:

- PRED(A ::= α) = PRIMERO(α) sin ε, si α no es anulable;
- PRED(A ::= α) = (PRIMERO(α) sin ε) ∪ SIGUIENTE(A), si α es anulable. En Cafetal, esto solo pasa con las reglas ε.

| Regla | No terminal | Lado derecho α | PRIMERO(α) | PRED |
|---|---|---|---|---|
| P1 | `<programa>` | INICIO `<sentencias>` FIN | {INICIO} | {INICIO} |
| R1 | `<sentencias>` | `<sentencia>` `<sentencias>` | {DATO, ID, MOSTRAR, SI, MIENTRAS} | {DATO, ID, MOSTRAR, SI, MIENTRAS} |
| R2 | `<sentencias>` | ε | {ε} | SIGUIENTE = {FIN, SINO} |
| P4 | `<sentencia>` | `<declaracion>` | {DATO} | {DATO} |
| P5 | `<sentencia>` | `<asignacion>` | {ID} | {ID} |
| P6 | `<sentencia>` | `<salida>` | {MOSTRAR} | {MOSTRAR} |
| P7 | `<sentencia>` | `<condicional>` | {SI} | {SI} |
| P8 | `<sentencia>` | `<ciclo>` | {MIENTRAS} | {MIENTRAS} |
| D1 | `<declaracion>` | DATO ID ASIGNACION `<expresion>` PUNTO_COMA | {DATO} | {DATO} |
| R3 | `<expresion>` | `<conjuncion>` `<expresion_prima>` | {NO, PAR_ABRE, ID, ENTERO, DECIMAL} | {NO, PAR_ABRE, ID, ENTERO, DECIMAL} |
| R4 | `<expresion_prima>` | O `<conjuncion>` `<expresion_prima>` | {O} | {O} |
| R5 | `<expresion_prima>` | ε | {ε} | SIGUIENTE = {PAR_CIERRA, PUNTO_COMA} |
| R6 | `<conjuncion>` | `<negacion>` `<conjuncion_prima>` | {NO, PAR_ABRE, ID, ENTERO, DECIMAL} | {NO, PAR_ABRE, ID, ENTERO, DECIMAL} |
| R7 | `<conjuncion_prima>` | Y `<negacion>` `<conjuncion_prima>` | {Y} | {Y} |
| R8 | `<conjuncion_prima>` | ε | {ε} | SIGUIENTE = {O, PAR_CIERRA, PUNTO_COMA} |
| E5 | `<negacion>` | NO `<negacion>` | {NO} | {NO} |
| E6 | `<negacion>` | `<comparacion>` | {PAR_ABRE, ID, ENTERO, DECIMAL} | {PAR_ABRE, ID, ENTERO, DECIMAL} |
| F1 | `<comparacion>` | `<suma>` `<comparacion_prima>` | {PAR_ABRE, ID, ENTERO, DECIMAL} | {PAR_ABRE, ID, ENTERO, DECIMAL} |
| F2 | `<comparacion_prima>` | `<op_rel>` `<suma>` | {MENOR, MAYOR, MENOR_IGUAL, MAYOR_IGUAL, IGUAL, DIFERENTE} | {MENOR, MAYOR, MENOR_IGUAL, MAYOR_IGUAL, IGUAL, DIFERENTE} |
| F3 | `<comparacion_prima>` | ε | {ε} | SIGUIENTE = {Y, O, PAR_CIERRA, PUNTO_COMA} |
| E9–E14 | `<op_rel>` | un relacional | {ese relacional} | {ese relacional} |
| R9 | `<suma>` | `<termino>` `<suma_prima>` | {PAR_ABRE, ID, ENTERO, DECIMAL} | {PAR_ABRE, ID, ENTERO, DECIMAL} |
| R10 | `<suma_prima>` | SUMA `<termino>` `<suma_prima>` | {SUMA} | {SUMA} |
| R11 | `<suma_prima>` | RESTA `<termino>` `<suma_prima>` | {RESTA} | {RESTA} |
| R12 | `<suma_prima>` | ε | {ε} | SIGUIENTE = {MENOR, MAYOR, MENOR_IGUAL, MAYOR_IGUAL, IGUAL, DIFERENTE, Y, O, PAR_CIERRA, PUNTO_COMA} |
| R13 | `<termino>` | `<factor>` `<termino_prima>` | {PAR_ABRE, ID, ENTERO, DECIMAL} | {PAR_ABRE, ID, ENTERO, DECIMAL} |
| R14 | `<termino_prima>` | MULT `<factor>` `<termino_prima>` | {MULT} | {MULT} |
| R15 | `<termino_prima>` | DIV `<factor>` `<termino_prima>` | {DIV} | {DIV} |
| R16 | `<termino_prima>` | ε | {ε} | SIGUIENTE = {SUMA, RESTA, MENOR, MAYOR, MENOR_IGUAL, MAYOR_IGUAL, IGUAL, DIFERENTE, Y, O, PAR_CIERRA, PUNTO_COMA} |
| E21 | `<factor>` | PAR_ABRE `<expresion>` PAR_CIERRA | {PAR_ABRE} | {PAR_ABRE} |
| E22 | `<factor>` | ID | {ID} | {ID} |
| E23 | `<factor>` | ENTERO | {ENTERO} | {ENTERO} |
| E24 | `<factor>` | DECIMAL | {DECIMAL} | {DECIMAL} |
| A1 | `<asignacion>` | ID ASIGNACION `<expresion>` PUNTO_COMA | {ID} | {ID} |
| M1 | `<salida>` | MOSTRAR PAR_ABRE `<argumento>` PAR_CIERRA PUNTO_COMA | {MOSTRAR} | {MOSTRAR} |
| M2 | `<argumento>` | `<expresion>` | {NO, PAR_ABRE, ID, ENTERO, DECIMAL} | {NO, PAR_ABRE, ID, ENTERO, DECIMAL} |
| M3 | `<argumento>` | CADENA | {CADENA} | {CADENA} |
| F4 | `<condicional>` | SI PAR_ABRE `<expresion>` PAR_CIERRA ENTONCES `<sentencias>` `<condicional_prima>` | {SI} | {SI} |
| F5 | `<condicional_prima>` | FIN | {FIN} | {FIN} |
| F6 | `<condicional_prima>` | SINO `<sentencias>` FIN | {SINO} | {SINO} |
| L1 | `<ciclo>` | MIENTRAS PAR_ABRE `<expresion>` PAR_CIERRA HACER `<sentencias>` FIN | {MIENTRAS} | {MIENTRAS} |

## 8. Tabla de análisis predictivo LL(1)

### 8.1 Construcción

Para cada regla A ::= α y cada token t ∈ PRED(A ::= α), se escribe la etiqueta de la regla en la celda M[A, t]. Una celda vacía significa **error sintáctico**: con A en la cima de la pila, el token t no puede aparecer.

El resultado tiene **106 celdas llenas** de las 23 × 31 = 713 posibles, y **ninguna celda tiene dos reglas**.

Las columnas ENTONCES, HACER, ASIGNACION y EOF no tienen ninguna celda llena. Esos tokens nunca deciden una regla: solo aparecen en medio o al final de un lado derecho, donde el analizador ya sabe qué regla está aplicando y solo los empareja. `EOF` se empareja al final, cuando la pila queda vacía (sección 11).

Para que quepa en la página, la tabla se presenta en tres partes, con las filas que tienen al menos una celda llena en esas columnas. La tabla completa está en `src/parser/tabla_ll1.csv`.

**Parte 1: tokens de programa y sentencias**

| No terminal | INICIO | FIN | SINO | DATO | ID | SI | MIENTRAS | MOSTRAR | CADENA |
|---|---|---|---|---|---|---|---|---|---|
| `<programa>` | P1 |  |  |  |  |  |  |  |  |
| `<sentencias>` |  | R2 | R2 | R1 | R1 | R1 | R1 | R1 |  |
| `<sentencia>` |  |  |  | P4 | P5 | P7 | P8 | P6 |  |
| `<declaracion>` |  |  |  | D1 |  |  |  |  |  |
| `<expresion>` |  |  |  |  | R3 |  |  |  |  |
| `<conjuncion>` |  |  |  |  | R6 |  |  |  |  |
| `<negacion>` |  |  |  |  | E6 |  |  |  |  |
| `<comparacion>` |  |  |  |  | F1 |  |  |  |  |
| `<suma>` |  |  |  |  | R9 |  |  |  |  |
| `<termino>` |  |  |  |  | R13 |  |  |  |  |
| `<factor>` |  |  |  |  | E22 |  |  |  |  |
| `<asignacion>` |  |  |  |  | A1 |  |  |  |  |
| `<salida>` |  |  |  |  |  |  |  | M1 |  |
| `<argumento>` |  |  |  |  | M2 |  |  |  | M3 |
| `<condicional>` |  |  |  |  |  | F4 |  |  |  |
| `<condicional_prima>` |  | F5 | F6 |  |  |  |  |  |  |
| `<ciclo>` |  |  |  |  |  |  | L1 |  |  |

**Parte 2: operadores lógicos, delimitadores y literales**

| No terminal | NO | Y | O | PAR_ABRE | PAR_CIERRA | PUNTO_COMA | ENTERO | DECIMAL |
|---|---|---|---|---|---|---|---|---|
| `<expresion>` | R3 |  |  | R3 |  |  | R3 | R3 |
| `<expresion_prima>` |  |  | R4 |  | R5 | R5 |  |  |
| `<conjuncion>` | R6 |  |  | R6 |  |  | R6 | R6 |
| `<conjuncion_prima>` |  | R7 | R8 |  | R8 | R8 |  |  |
| `<negacion>` | E5 |  |  | E6 |  |  | E6 | E6 |
| `<comparacion>` |  |  |  | F1 |  |  | F1 | F1 |
| `<comparacion_prima>` |  | F3 | F3 |  | F3 | F3 |  |  |
| `<suma>` |  |  |  | R9 |  |  | R9 | R9 |
| `<suma_prima>` |  | R12 | R12 |  | R12 | R12 |  |  |
| `<termino>` |  |  |  | R13 |  |  | R13 | R13 |
| `<termino_prima>` |  | R16 | R16 |  | R16 | R16 |  |  |
| `<factor>` |  |  |  | E21 |  |  | E23 | E24 |
| `<argumento>` | M2 |  |  | M2 |  |  | M2 | M2 |

**Parte 3: operadores aritméticos y relacionales**

| No terminal | SUMA | RESTA | MULT | DIV | MENOR | MAYOR | MENOR_IGUAL | MAYOR_IGUAL | IGUAL | DIFERENTE |
|---|---|---|---|---|---|---|---|---|---|---|
| `<comparacion_prima>` |  |  |  |  | F2 | F2 | F2 | F2 | F2 | F2 |
| `<op_rel>` |  |  |  |  | E9 | E10 | E11 | E12 | E13 | E14 |
| `<suma_prima>` | R10 | R11 |  |  | R12 | R12 | R12 | R12 | R12 | R12 |
| `<termino_prima>` | R16 | R16 | R14 | R15 | R16 | R16 | R16 | R16 | R16 | R16 |

Las tres partes suman 29 + 47 + 30 = 106 celdas.

### 8.2 Formato de `tabla_ll1.csv`

- Codificación UTF-8, separada por comas, igual que `src/lexer/tabla_afd.csv`.
- Primera fila: `no_terminal` y los 31 terminales en el orden de código del catálogo (INICIO … PUNTO_COMA) y `EOF` al final.
- Una fila por no terminal, con su nombre entre `< >`, en el orden de la sección 3.
- Cada celda contiene la etiqueta de la regla (P1, R10, F2…) o queda vacía (error). El lado derecho de cada etiqueta está en la sección 3.

## 9. Condición LL(1)

Una gramática es LL(1) si y solo si, para todo no terminal A con dos alternativas distintas A ::= α | β (Aho et al., 2006):

1. PRIMERO(α) y PRIMERO(β) no tienen tokens en común;
2. a lo sumo una de las dos deriva ε;
3. si β deriva ε, PRIMERO(α) no tiene tokens en común con SIGUIENTE(A).

Las tres condiciones juntas equivalen a que los conjuntos de predicción de las alternativas de A sean **disjuntos dos a dos**, es decir, a que ninguna celda M[A, t] tenga dos reglas. Se revisan los 12 no terminales con más de una alternativa (los otros 11 tienen una sola regla y no pueden tener conflicto):

| No terminal | Conjuntos de predicción de sus alternativas | ¿Disjuntos? |
|---|---|---|
| `<sentencias>` | R1 {DATO, ID, MOSTRAR, SI, MIENTRAS} · R2 {FIN, SINO} | Sí |
| `<sentencia>` | P4 {DATO} · P5 {ID} · P6 {MOSTRAR} · P7 {SI} · P8 {MIENTRAS} | Sí |
| `<expresion_prima>` | R4 {O} · R5 {PAR_CIERRA, PUNTO_COMA} | Sí |
| `<conjuncion_prima>` | R7 {Y} · R8 {O, PAR_CIERRA, PUNTO_COMA} | Sí |
| `<negacion>` | E5 {NO} · E6 {PAR_ABRE, ID, ENTERO, DECIMAL} | Sí |
| `<comparacion_prima>` | F2 {MENOR, MAYOR, MENOR_IGUAL, MAYOR_IGUAL, IGUAL, DIFERENTE} · F3 {Y, O, PAR_CIERRA, PUNTO_COMA} | Sí |
| `<op_rel>` | E9–E14, un relacional distinto cada una | Sí |
| `<suma_prima>` | R10 {SUMA} · R11 {RESTA} · R12 {MENOR, MAYOR, MENOR_IGUAL, MAYOR_IGUAL, IGUAL, DIFERENTE, Y, O, PAR_CIERRA, PUNTO_COMA} | Sí |
| `<termino_prima>` | R14 {MULT} · R15 {DIV} · R16 {SUMA, RESTA, MENOR, MAYOR, MENOR_IGUAL, MAYOR_IGUAL, IGUAL, DIFERENTE, Y, O, PAR_CIERRA, PUNTO_COMA} | Sí |
| `<factor>` | E21 {PAR_ABRE} · E22 {ID} · E23 {ENTERO} · E24 {DECIMAL} | Sí |
| `<argumento>` | M2 {NO, PAR_ABRE, ID, ENTERO, DECIMAL} · M3 {CADENA} | Sí |
| `<condicional_prima>` | F5 {FIN} · F6 {SINO} | Sí |

Además, cada no terminal tiene a lo sumo una alternativa ε, así que la condición 2 también se cumple. **La gramática es LL(1).**

### 9.1 Por qué no hay conflictos: cada decisión de diseño elimina uno

Los casos más delicados son las reglas ε, que se eligen con SIGUIENTE. Cada uno queda libre de conflicto gracias a una decisión de las tareas anteriores:

| Regla ε | Conflicto que podría tener | Por qué no ocurre | Decisión que lo evita |
|---|---|---|---|
| R2 (`<sentencias>`) | Con R1, si una lista pudiera ir seguida de algo que también empieza una sentencia | SIGUIENTE(`<sentencias>`) = {FIN, SINO}, y ninguna sentencia empieza con FIN ni SINO | Todo bloque cierra con `fin` (DSL-2, GIC-3) |
| R12 (`<suma_prima>`) | Con R10 y R11, si SUMA o RESTA pudieran seguir a una `<suma>` completa | SUMA y RESTA solo aparecen dentro de `<suma_prima>`; una `<suma>` completa solo va seguida de relacionales, Y, O o cierres | Estratificación por niveles (GIC-3) |
| R16 (`<termino_prima>`) | Con R14 y R15, si MULT o DIV pudieran seguir a un `<termino>` completo | Igual que el anterior, un nivel más abajo | Estratificación por niveles (GIC-3) |
| F3 (`<comparacion_prima>`) | Con F2, si un relacional pudiera seguir a una comparación completa | SIGUIENTE(`<comparacion_prima>`) = {Y, O, PAR_CIERRA, PUNTO_COMA}: no contiene relacionales | Relacionales no asociativos (GIC-1, GIC-3) |
| R5 y R8 | Con R4 y R7 | O e Y no están en los SIGUIENTE de su propio nivel | Estratificación por niveles (GIC-3) |

La fila de F3 explica cómo se rechaza `a < b < c`: después de `a < b`, `<comparacion_prima>` ya se usó, y el segundo MENOR llega cuando en la cima está `<conjuncion_prima>`. La celda M[`<conjuncion_prima>`, MENOR] está vacía, así que el analizador reporta el error justo en el segundo relacional.

## 10. Por qué la tabla LL(1) demuestra que la gramática no es ambigua

**Proposición.** Si la tabla LL(1) de una gramática G no tiene celdas con dos reglas, ninguna cadena tiene dos árboles de derivación en G.

*Prueba.* Dos árboles distintos de la misma cadena w corresponden a dos derivaciones más a la izquierda distintas (Hopcroft et al., 2007). Se supone que existen y se busca una contradicción.

Las dos derivaciones parten de `<programa>`, y mientras apliquen las mismas reglas producen las mismas formas sentenciales. Sea x A γ la primera forma sentencial en que difieren, donde x es la parte ya formada solo por tokens, A es el no terminal más a la izquierda y γ el resto. Una derivación aplica A ::= α₁ y la otra A ::= α₂, con α₁ ≠ α₂. Como las dos llegan a w, la cadena w empieza con x. Sea t el token de w que viene justo después de x, o `EOF` si x ya es toda la cadena.

En la derivación que usa A ::= α₁, la forma x α₁ γ termina generando w, así que α₁ γ genera lo que sigue a x, que empieza con t. Hay dos casos:

- si α₁ genera al menos un token, t es el primero de ellos y t ∈ PRIMERO(α₁);
- si α₁ genera ε, t es el primer token que genera γ, o es `EOF`. Como x A γ se deriva desde `<programa>`, ese token aparece justo después de A en una forma sentencial, así que t ∈ SIGUIENTE(A).

En los dos casos t ∈ PRED(A ::= α₁), es decir, M[A, t] contiene α₁. Con el mismo argumento, M[A, t] contiene α₂. La celda M[A, t] tendría entonces dos reglas, lo que contradice la hipótesis. ∎

Como la tabla de la sección 8 no tiene celdas con dos reglas, **la gramática final de Cafetal no es ambigua**. Esto confirma, para la gramática que usará el analizador, las demostraciones de GIC-3 hechas sobre la gramática estratificada.

La prueba muestra algo más: el árbol se puede construir **eligiendo cada regla con un solo token**, y eso es exactamente lo que hace el analizador de la Fase 3.

## 11. Funcionamiento del analizador predictivo

El analizador predictivo guarda en una **pila** los símbolos que faltan por derivar. Empieza con `<programa>` sobre `EOF` y repite:

- si la cima es un terminal igual al token actual, los **empareja**: saca la cima y avanza al siguiente token;
- si la cima es un no terminal A, consulta M[A, t] con el token actual t: si la celda tiene una regla, saca A y apila su lado derecho, con el primer símbolo en la cima; si está vacía, reporta un **error sintáctico**;
- si la cima es `EOF` y el token actual también, **acepta**.

### 11.1 Traza de una entrada válida

Entrada: `inicio x = a - 1; fin`. Tokens: INICIO ID ASIGNACION ID RESTA ENTERO PUNTO_COMA FIN EOF. En la columna Pila, la cima está a la izquierda.

| Paso | Pila | Entrada | Acción |
|---|---|---|---|
| 1 | `<programa>` EOF | INICIO ID ASIGNACION ID RESTA ENTERO PUNTO_COMA FIN EOF | P1: `<programa>` ::= INICIO `<sentencias>` FIN |
| 2 | INICIO `<sentencias>` FIN EOF | INICIO ID ASIGNACION ID RESTA ENTERO PUNTO_COMA FIN EOF | Emparejar INICIO |
| 3 | `<sentencias>` FIN EOF | ID ASIGNACION ID RESTA ENTERO PUNTO_COMA FIN EOF | R1: `<sentencias>` ::= `<sentencia>` `<sentencias>` |
| 4 | `<sentencia>` `<sentencias>` FIN EOF | ID ASIGNACION ID RESTA ENTERO PUNTO_COMA FIN EOF | P5: `<sentencia>` ::= `<asignacion>` |
| 5 | `<asignacion>` `<sentencias>` FIN EOF | ID ASIGNACION ID RESTA ENTERO PUNTO_COMA FIN EOF | A1: `<asignacion>` ::= ID ASIGNACION `<expresion>` PUNTO_COMA |
| 6 | ID ASIGNACION `<expresion>` PUNTO_COMA `<sentencias>` FIN EOF | ID ASIGNACION ID RESTA ENTERO PUNTO_COMA FIN EOF | Emparejar ID |
| 7 | ASIGNACION `<expresion>` PUNTO_COMA `<sentencias>` FIN EOF | ASIGNACION ID RESTA ENTERO PUNTO_COMA FIN EOF | Emparejar ASIGNACION |
| 8 | `<expresion>` PUNTO_COMA `<sentencias>` FIN EOF | ID RESTA ENTERO PUNTO_COMA FIN EOF | R3: `<expresion>` ::= `<conjuncion>` `<expresion_prima>` |
| 9 | `<conjuncion>` `<expresion_prima>` PUNTO_COMA … | ID RESTA ENTERO PUNTO_COMA FIN EOF | R6: `<conjuncion>` ::= `<negacion>` `<conjuncion_prima>` |
| 10 | `<negacion>` `<conjuncion_prima>` `<expresion_prima>` PUNTO_COMA … | ID RESTA ENTERO PUNTO_COMA FIN EOF | E6: `<negacion>` ::= `<comparacion>` |
| 11 | `<comparacion>` `<conjuncion_prima>` `<expresion_prima>` PUNTO_COMA … | ID RESTA ENTERO PUNTO_COMA FIN EOF | F1: `<comparacion>` ::= `<suma>` `<comparacion_prima>` |
| 12 | `<suma>` `<comparacion_prima>` `<conjuncion_prima>` `<expresion_prima>` PUNTO_COMA … | ID RESTA ENTERO PUNTO_COMA FIN EOF | R9: `<suma>` ::= `<termino>` `<suma_prima>` |
| 13 | `<termino>` `<suma_prima>` `<comparacion_prima>` … | ID RESTA ENTERO PUNTO_COMA FIN EOF | R13: `<termino>` ::= `<factor>` `<termino_prima>` |
| 14 | `<factor>` `<termino_prima>` `<suma_prima>` … | ID RESTA ENTERO PUNTO_COMA FIN EOF | E22: `<factor>` ::= ID |
| 15 | ID `<termino_prima>` `<suma_prima>` … | ID RESTA ENTERO PUNTO_COMA FIN EOF | Emparejar ID |
| 16 | `<termino_prima>` `<suma_prima>` … | RESTA ENTERO PUNTO_COMA FIN EOF | R16: `<termino_prima>` ::= ε (RESTA ∈ SIGUIENTE) |
| 17 | `<suma_prima>` `<comparacion_prima>` … | RESTA ENTERO PUNTO_COMA FIN EOF | R11: `<suma_prima>` ::= RESTA `<termino>` `<suma_prima>` |
| 18 | RESTA `<termino>` `<suma_prima>` … | RESTA ENTERO PUNTO_COMA FIN EOF | Emparejar RESTA |
| 19 | `<termino>` `<suma_prima>` … | ENTERO PUNTO_COMA FIN EOF | R13: `<termino>` ::= `<factor>` `<termino_prima>` |
| 20 | `<factor>` `<termino_prima>` `<suma_prima>` … | ENTERO PUNTO_COMA FIN EOF | E23: `<factor>` ::= ENTERO |
| 21 | ENTERO `<termino_prima>` `<suma_prima>` … | ENTERO PUNTO_COMA FIN EOF | Emparejar ENTERO |
| 22 | `<termino_prima>` `<suma_prima>` `<comparacion_prima>` `<conjuncion_prima>` `<expresion_prima>` PUNTO_COMA `<sentencias>` FIN EOF | PUNTO_COMA FIN EOF | R16: `<termino_prima>` ::= ε |
| 23 | `<suma_prima>` `<comparacion_prima>` `<conjuncion_prima>` `<expresion_prima>` PUNTO_COMA `<sentencias>` FIN EOF | PUNTO_COMA FIN EOF | R12: `<suma_prima>` ::= ε |
| 24 | `<comparacion_prima>` `<conjuncion_prima>` `<expresion_prima>` PUNTO_COMA `<sentencias>` FIN EOF | PUNTO_COMA FIN EOF | F3: `<comparacion_prima>` ::= ε |
| 25 | `<conjuncion_prima>` `<expresion_prima>` PUNTO_COMA `<sentencias>` FIN EOF | PUNTO_COMA FIN EOF | R8: `<conjuncion_prima>` ::= ε |
| 26 | `<expresion_prima>` PUNTO_COMA `<sentencias>` FIN EOF | PUNTO_COMA FIN EOF | R5: `<expresion_prima>` ::= ε |
| 27 | PUNTO_COMA `<sentencias>` FIN EOF | PUNTO_COMA FIN EOF | Emparejar PUNTO_COMA |
| 28 | `<sentencias>` FIN EOF | FIN EOF | R2: `<sentencias>` ::= ε (FIN ∈ SIGUIENTE) |
| 29 | FIN EOF | FIN EOF | Emparejar FIN |
| 30 | EOF | EOF | Aceptar |

Los "…" abrevian el fondo de la pila, que no cambia en esos pasos y se ve completo en los pasos 8 y 22. Las reglas aplicadas, en orden (P1, R1, P5, A1, R3, …, R2), son exactamente la derivación más a la izquierda de la entrada, y por eso definen su árbol. Los pasos 22 a 26 muestran el efecto de PUNTO_COMA: está en el SIGUIENTE de los cinco no terminales `_prima` pendientes, así que el analizador los cierra todos con su regla ε.

### 11.2 Traza de una entrada con error

Entrada: `inicio x = a - ; fin`. Los pasos 1 a 18 son iguales a los de 11.1. En el paso 19 el token actual es PUNTO_COMA, donde debía venir el operando de la resta:

| Paso | Pila | Entrada | Acción |
|---|---|---|---|
| 19 | `<termino>` `<suma_prima>` `<comparacion_prima>` … | PUNTO_COMA FIN EOF | Error: M[`<termino>`, PUNTO_COMA] está vacía |

La celda vacía indica qué se esperaba: los tokens con celda llena en la fila de `<termino>`, que son PRIMERO(`<termino>`) = {PAR_ABRE, ID, ENTERO, DECIMAL}. El mensaje de error de PAR-4 puede armarse con esa fila y con la línea y columna del token.

## 12. Verificación

Los conjuntos y la tabla se calcularon a mano, en el orden de las secciones 5 y 6, y se verificaron con un programa que aplica las reglas de 5.1 y 6.1 hasta el punto fijo. Después, la tabla se probó con un analizador predictivo que solo consulta la tabla (sección 11), comparado con el analizador general usado en GIC-4, que acepta cualquier gramática independiente del contexto y cuenta los árboles.

| Prueba | Resultado |
|---|---|
| PRIMERO, SIGUIENTE y anulables calculados por el programa frente a los de las secciones 4 a 6 | Coinciden en los 23 no terminales |
| Celdas de la tabla | 106 llenas, **0 con dos reglas** |
| Todos los programas `inicio x = w; fin` con w de hasta 5 tokens sobre ID, SUMA, MULT, O, Y, NO, MENOR, IGUAL, PAR_ABRE y PAR_CIERRA | 111 111 entradas, 86 aceptadas, **0 diferencias** entre el analizador predictivo y el general |
| 2 000 programas generados al azar desde `<programa>` (hasta 86 tokens), más 2 variantes de cada uno con un token cambiado | 6 000 entradas, 2 230 aceptadas y 3 770 rechazadas, **0 diferencias** y ninguna entrada con más de un árbol |

**Programas de ejemplo.** El analizador predictivo acepta los tres programas de `ejemplos/`, y el analizador general confirma que cada uno tiene un único árbol:

| Programa | Tokens | Pasos del analizador predictivo | Árboles |
|---|---|---|---|
| `ejemplo1_produccion.cft` | 66 | 241 | 1 |
| `ejemplo2_clasificacion.cft` | 62 | 197 | 1 |
| `ejemplo3_secado.cft` | 57 | 223 | 1 |

## 13. Pendientes para las siguientes tareas

| Tarea | Qué toma de este documento |
|---|---|
| DOC-3 (Diego) | Este documento cierra la Fase 2: la tabla sin conflictos es la conclusión de la cadena GIC-1 → GIC-3 → GIC-4 → GIC-5 → GIC-6 |
| PAR-2 y PAR-3 (Fase 3) | Una función por no terminal. Cada función elige su regla con la fila de la tabla (o con los conjuntos de predicción de la sección 7) mirando el token actual, sin retroceder. Las funciones de los no terminales con una sola regla no necesitan elegir |
| PAR-4 (Fase 3) | La recuperación en modo pánico se sincroniza con SIGUIENTE (sección 6.4): ante un error en A, se descartan tokens hasta encontrar uno de SIGUIENTE(A) |

## Referencias

Aho, A. V., Lam, M. S., Sethi, R. y Ullman, J. D. (2006). *Compilers: Principles, techniques, and tools* (2.ª ed.). Addison-Wesley.

Hopcroft, J. E., Motwani, R. y Ullman, J. D. (2007). *Introduction to automata theory, languages, and computation* (3.ª ed.). Addison-Wesley.
