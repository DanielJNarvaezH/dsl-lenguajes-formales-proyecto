# Fase 2 — Eliminación de la recursividad por la izquierda

**Tarea Jira:** GIC-4 — Eliminación de recursividad por la izquierda
**Responsable:** Juan Diego García Albarracín
**Insumos:** `gramatica_programa_expresiones.md` (GIC-1), `gramatica_sentencias.md` (GIC-2) y el documento de GIC-3 (demostración de ambigüedad y estratificación)
**Se complementa con:** GIC-5 (factorización por la izquierda) y GIC-6 (PRIMERO, SIGUIENTE y tabla LL(1))

---

## 1. Qué es la recursividad por la izquierda y por qué se elimina

Un no terminal A es **recursivo por la izquierda** si existe una derivación A ⇒⁺ A γ, es decir, si A puede volver a aparecer como **primer** símbolo de lo que él mismo genera (Aho et al., 2006). Hay dos casos:

- **Directa:** existe una regla de la forma `A ::= A α`.
- **Indirecta:** A llega a sí mismo pasando por otros no terminales, por ejemplo `A ::= B α` y `B ::= A β`.

La gramática de GIC-1 tiene recursividad directa a propósito: en GIC-3 se usó para fijar la asociatividad por la izquierda de `o`, `y`, `+ -` y `* /`. Pero la Fase 3 usa un **analizador descendente recursivo**, con una función por no terminal, y ese tipo de analizador no puede trabajar con una gramática recursiva por la izquierda, por dos razones:

1. **No termina.** La función de `<suma>`, al aplicar E15 (`<suma> ::= <suma> SUMA <termino>`), tendría que llamarse a sí misma antes de consumir ningún token. Esa llamada vuelve a hacer lo mismo, y así indefinidamente. Se comprobó con un analizador descendente ingenuo, que prueba todas las alternativas de cada no terminal: sobre la gramática de GIC-1 + GIC-2 entra en recursión infinita incluso con la entrada `ID` (sección 8).
2. **No puede elegir regla mirando el siguiente token.** Las tres alternativas de `<suma>` (E15, E16 y E17) empiezan con los mismos tokens, porque las tres empiezan generando un `<termino>`: PAR_ABRE, ID, ENTERO o DECIMAL. Para derivar `10 - 4 - 2`, el analizador tendría que decidir desde el primer token, ENTERO⟨10⟩, que debe aplicar E16 **dos veces**, y eso depende de cuántos RESTA hay más adelante.

Este documento elimina la recursividad por la izquierda con la transformación

```
A ::= A α | β      ⇒      A ::= β A'
                          A' ::= α A' | ε
```

aplicada paso a paso a cada regla recursiva, y demuestra que la transformación **no cambia el lenguaje**.

## 2. Notación

- Se usa la misma notación BNF de GIC-1 y GIC-2: no terminales en minúsculas entre `< >`, terminales con el nombre del token del catálogo en MAYÚSCULAS, `::=`, `|` y ε. En las derivaciones, el lexema de ID, ENTERO y DECIMAL se indica entre ⟨ ⟩.
- **El no terminal nuevo A'.** En la fórmula del método se escribe A', como en la bibliografía. En la gramática de Cafetal se escribe agregando `_prima` al nombre: el A' de `<suma>` es `<suma_prima>`. Así se conserva la convención de GIC-1 (solo minúsculas y guion bajo), y el nombre sirve directamente como nombre de la función de Python del analizador de la Fase 3 (`suma_prima`). El apóstrofo no es válido en un identificador de Python.
- **Lenguajes con expresiones regulares primitivas.** Para comparar lo que genera un no terminal antes y después de la transformación, se escribe ese conjunto de formas con los mismos operadores primitivos que en la Fase 1: unión con coma (`a,b`), concatenación por yuxtaposición o con paréntesis (`ab`, `(a)(b)`) y cerradura de Kleene `( )*`. ε es una expresión regular primitiva, no un operador. Aquí los símbolos no son caracteres de Σ sino símbolos de la gramática (tokens y no terminales). Ningún nombre de token contiene coma ni paréntesis, así que no chocan con los metasímbolos.
- **Numeración de las reglas.** Las reglas que no cambian conservan su etiqueta de GIC-2 (P, D, E, A, M, C, L). Las reglas que produce esta tarea se numeran R1 a R16.

## 3. Detección de la recursividad por la izquierda

### 3.1 Recursividad directa

Se revisaron las 40 reglas de la gramática completa de GIC-2 (sección 3 de `gramatica_sentencias.md`). Tienen la forma `A ::= A α` siete reglas, de cinco no terminales:

| Regla | No terminal | Forma |
|---|---|---|
| P2 | `<sentencias>` | `<sentencias> ::= <sentencias> <sentencia>` |
| E1 | `<expresion>` | `<expresion> ::= <expresion> O <conjuncion>` |
| E3 | `<conjuncion>` | `<conjuncion> ::= <conjuncion> Y <negacion>` |
| E15 | `<suma>` | `<suma> ::= <suma> SUMA <termino>` |
| E16 | `<suma>` | `<suma> ::= <suma> RESTA <termino>` |
| E18 | `<termino>` | `<termino> ::= <termino> MULT <factor>` |
| E19 | `<termino>` | `<termino> ::= <termino> DIV <factor>` |

Hay otras reglas recursivas, pero **no por la izquierda**, y no se modifican:

| Regla | Por qué no es recursiva por la izquierda |
|---|---|
| E5 `<negacion> ::= NO <negacion>` | La recursión está a la derecha: antes de `<negacion>` va el terminal NO |
| E21 `<factor> ::= PAR_ABRE <expresion> PAR_CIERRA` | `<expresion>` vuelve a aparecer, pero después del terminal PAR_ABRE |
| C1, C2 y L1 | `<sentencias>` aparece después de SI … ENTONCES o MIENTRAS … HACER |

Ninguna regla de GIC-2 es recursiva por la izquierda, como ya se indicaba en la sección 5 de ese documento.

### 3.2 Recursividad indirecta

Para descartar la recursividad indirecta hay que ver qué no terminales pueden quedar **de primeros** en el lado derecho de cada regla. Hay que tener en cuenta los no terminales **anulables**, los que pueden derivar ε: si una regla empieza con un anulable, el símbolo que sigue también puede quedar de primero.

En la gramática de GIC-1 + GIC-2 el único no terminal anulable es `<sentencias>` (P3). Ningún no terminal de expresiones es anulable, porque todas sus reglas terminan generando al menos un `<factor>`, que siempre produce un token.

| No terminal | No terminales que pueden quedar de primeros en sus reglas |
|---|---|
| `<programa>` | ninguno (P1 empieza con INICIO) |
| `<sentencias>` | `<sentencias>` (P2) y, como `<sentencias>` es anulable, `<sentencia>` (P2) |
| `<sentencia>` | `<declaracion>`, `<asignacion>`, `<salida>`, `<condicional>`, `<ciclo>` |
| `<declaracion>`, `<asignacion>`, `<salida>`, `<condicional>`, `<ciclo>` | ninguno (empiezan con DATO, ID, MOSTRAR, SI y MIENTRAS) |
| `<argumento>` | `<expresion>` (M2) |
| `<expresion>` | `<expresion>` (E1), `<conjuncion>` (E2) |
| `<conjuncion>` | `<conjuncion>` (E3), `<negacion>` (E4) |
| `<negacion>` | `<comparacion>` (E6); E5 empieza con NO |
| `<comparacion>` | `<suma>` (E7, E8) |
| `<suma>` | `<suma>` (E15, E16), `<termino>` (E17) |
| `<termino>` | `<termino>` (E18, E19), `<factor>` (E20) |
| `<factor>`, `<op_rel>` | ninguno (todas sus reglas empiezan con un terminal) |

Si se quitan los casos en que un no terminal se apunta a sí mismo, que son la recursividad directa de 3.1, lo que queda son dos cadenas que **nunca vuelven atrás**:

```
<sentencias> → <sentencia> → <declaracion> | <asignacion> | <salida> | <condicional> | <ciclo>
<argumento> → <expresion> → <conjuncion> → <negacion> → <comparacion> → <suma> → <termino> → <factor>
```

Las dos terminan en no terminales cuyas reglas empiezan con un terminal. El único camino de regreso de `<factor>` a `<expresion>` es E21, y ahí `<expresion>` va después de PAR_ABRE, así que no queda de primera. Por lo tanto, **no hay recursividad indirecta**: basta con eliminar la recursividad directa de las siete reglas de 3.1.

### 3.3 Condiciones para aplicar el método

La transformación de la sección 4 exige tres condiciones, y las siete reglas las cumplen:

| Condición | Por qué se exige | Comprobación en Cafetal |
|---|---|---|
| Ningún α es ε | Una regla `A ::= A` no genera nada nuevo y haría que A' derivara ε de infinitas formas | Todos los α empiezan con un terminal (O, Y, SUMA, RESTA, MULT, DIV) o con `<sentencia>`, que no es anulable |
| Ningún β empieza con A | Si no, la regla `A ::= β A'` seguiría siendo recursiva por la izquierda | Los β son ε, `<conjuncion>`, `<negacion>`, `<termino>` y `<factor>` |
| No hay recursividad indirecta | El método solo elimina la recursividad directa | Demostrado en 3.2 |

## 4. Método

### 4.1 Regla básica

Si las reglas de A son

```
A ::= A α
A ::= β
```

donde α y β son cadenas de símbolos de la gramática y β no empieza con A, se reemplazan por

```
A  ::= β A'
A' ::= α A'
A' ::= ε
```

donde A' es un no terminal nuevo.

### 4.2 Por qué la transformación conserva el lenguaje

Se compara lo que genera A usando solo sus propias reglas.

**Antes.** Cada vez que se aplica `A ::= A α`, la A de la izquierda se reemplaza por `A α`, y así aparece un α más a la derecha. La derivación termina cuando se aplica `A ::= β`:

```
A ⇒ A α ⇒ A α α ⇒ … ⇒ A α α … α ⇒ β α α … α      (k veces α, k ≥ 0)
```

Las formas que se obtienen son β seguida de cero o más α: **(β)(α)\***.

**Después.** A' genera cero o más α: cada `A' ::= α A'` agrega un α y deja A' a la derecha, y `A' ::= ε` termina.

```
A' ⇒ α A' ⇒ α α A' ⇒ … ⇒ α α … α A' ⇒ α α … α      (k veces α, k ≥ 0)
```

Así, A' genera (α)\*, y como `A ::= β A'` es la única regla de A, A genera **(β)(α)\***.

Los dos conjuntos son iguales, así que la gramática transformada genera exactamente el mismo lenguaje. ∎

Lo que cambia es el **orden** en que se construye la cadena: la regla original agrega los α de derecha a izquierda (el último α es el primero que aparece en la derivación) y la nueva los agrega de izquierda a derecha, en el mismo orden en que el analizador lee los tokens. Por eso la nueva forma sirve para un analizador descendente. El efecto sobre la forma del árbol se analiza en la sección 7.

### 4.3 Varias alternativas recursivas

`<suma>` y `<termino>` tienen dos alternativas recursivas cada una:

```
A ::= A α₁ | A α₂ | β
```

No hace falta una fórmula nueva. Como la concatenación se distribuye sobre la unión, `A α₁ , A α₂` es lo mismo que `A (α₁,α₂)`, así que las reglas tienen la forma básica con **α = (α₁,α₂)**. Se aplica la regla de 4.1:

```
A  ::= β A'
A' ::= (α₁,α₂) A' | ε
```

Y se vuelve a distribuir la concatenación sobre la unión, `(α₁,α₂) A' = α₁ A' , α₂ A'`, para que cada alternativa quede en su propia regla:

```
A  ::= β A'
A' ::= α₁ A' | α₂ A' | ε
```

Por 4.2, A genera **(β)(α₁,α₂)\*** antes y después. Solo se usaron unión, concatenación y cerradura de Kleene.

### 4.4 Caso β = ε

En `<sentencias>`, la alternativa no recursiva es ε. Al aplicar 4.1 con β = ε:

```
A  ::= ε A'
A' ::= α A' | ε
```

ε es el elemento neutro de la concatenación (ε A' = A'), así que la primera regla queda `A ::= A'`. Como esa es la **única** regla de A, A y A' generan exactamente lo mismo, (α)\*, y se puede reemplazar A' por A en todas partes (renombrar):

```
A ::= α A | ε
```

Esta simplificación no cambia el lenguaje y tiene una ventaja práctica: el nombre `<sentencias>` se conserva, así que P1, C1, C2 y L1, que lo usan, no cambian. Se comprobó además que las dos versiones, con y sin simplificar, aceptan exactamente las mismas cadenas (sección 8).

## 5. Aplicación paso a paso

### 5.1 `<sentencias>` (P2 y P3)

**Regla original:**

```
P2   <sentencias> ::= <sentencias> <sentencia>
P3   <sentencias> ::= ε
```

**Identificación de α y β:**

| Símbolo de la fórmula | Valor |
|---|---|
| A | `<sentencias>` |
| α | `<sentencia>` |
| β | ε |
| A' | `<sentencias_prima>` |

**Sustitución en la fórmula** (4.1):

```
<sentencias>       ::= ε <sentencias_prima>
<sentencias_prima> ::= <sentencia> <sentencias_prima>
<sentencias_prima> ::= ε
```

**Simplificación** (4.4): ε `<sentencias_prima>` = `<sentencias_prima>`, y como esa es la única regla de `<sentencias>`, se renombra `<sentencias_prima>` como `<sentencias>`.

**Regla resultante:**

```
R1   <sentencias> ::= <sentencia> <sentencias>
R2   <sentencias> ::= ε
```

**Lenguaje:** antes (ε)(`<sentencia>`)\* = (`<sentencia>`)\*; después (`<sentencia>`)\*. Una lista de cero o más sentencias, igual que antes. La lista ahora es recursiva por la derecha: la primera sentencia queda arriba en el árbol y el resto de la lista debajo de ella.

### 5.2 `<expresion>` (E1 y E2)

**Regla original:**

```
E1   <expresion> ::= <expresion> O <conjuncion>
E2   <expresion> ::= <conjuncion>
```

**Identificación de α y β:**

| Símbolo de la fórmula | Valor |
|---|---|
| A | `<expresion>` |
| α | O `<conjuncion>` |
| β | `<conjuncion>` |
| A' | `<expresion_prima>` |

**Sustitución en la fórmula:**

```
A  ::= β A'          ⇒   <expresion>       ::= <conjuncion> <expresion_prima>
A' ::= α A'          ⇒   <expresion_prima> ::= O <conjuncion> <expresion_prima>
A' ::= ε             ⇒   <expresion_prima> ::= ε
```

**Regla resultante:**

```
R3   <expresion>       ::= <conjuncion> <expresion_prima>
R4   <expresion_prima> ::= O <conjuncion> <expresion_prima>
R5   <expresion_prima> ::= ε
```

**Lenguaje:** antes y después, (`<conjuncion>`)(O `<conjuncion>`)\*: una o más conjunciones separadas por O.

### 5.3 `<conjuncion>` (E3 y E4)

**Regla original:**

```
E3   <conjuncion> ::= <conjuncion> Y <negacion>
E4   <conjuncion> ::= <negacion>
```

**Identificación de α y β:**

| Símbolo de la fórmula | Valor |
|---|---|
| A | `<conjuncion>` |
| α | Y `<negacion>` |
| β | `<negacion>` |
| A' | `<conjuncion_prima>` |

**Sustitución en la fórmula:**

```
A  ::= β A'          ⇒   <conjuncion>       ::= <negacion> <conjuncion_prima>
A' ::= α A'          ⇒   <conjuncion_prima> ::= Y <negacion> <conjuncion_prima>
A' ::= ε             ⇒   <conjuncion_prima> ::= ε
```

**Regla resultante:**

```
R6   <conjuncion>       ::= <negacion> <conjuncion_prima>
R7   <conjuncion_prima> ::= Y <negacion> <conjuncion_prima>
R8   <conjuncion_prima> ::= ε
```

**Lenguaje:** antes y después, (`<negacion>`)(Y `<negacion>`)\*.

### 5.4 `<suma>` (E15, E16 y E17)

**Regla original:**

```
E15  <suma> ::= <suma> SUMA <termino>
E16  <suma> ::= <suma> RESTA <termino>
E17  <suma> ::= <termino>
```

**Identificación de α y β** (dos alternativas recursivas, sección 4.3):

| Símbolo de la fórmula | Valor |
|---|---|
| A | `<suma>` |
| α₁ | SUMA `<termino>` |
| α₂ | RESTA `<termino>` |
| α = (α₁,α₂) | (SUMA `<termino>`, RESTA `<termino>`) |
| β | `<termino>` |
| A' | `<suma_prima>` |

**Sustitución en la fórmula:**

```
A  ::= β A'          ⇒   <suma>       ::= <termino> <suma_prima>
A' ::= α A'          ⇒   <suma_prima> ::= (SUMA <termino>, RESTA <termino>) <suma_prima>
                     ⇒   <suma_prima> ::= SUMA <termino> <suma_prima>       (distribución)
                         <suma_prima> ::= RESTA <termino> <suma_prima>
A' ::= ε             ⇒   <suma_prima> ::= ε
```

**Regla resultante:**

```
R9   <suma>       ::= <termino> <suma_prima>
R10  <suma_prima> ::= SUMA <termino> <suma_prima>
R11  <suma_prima> ::= RESTA <termino> <suma_prima>
R12  <suma_prima> ::= ε
```

**Lenguaje:** antes y después, (`<termino>`)(SUMA `<termino>`, RESTA `<termino>`)\*: uno o más términos separados por SUMA o RESTA, en cualquier combinación.

### 5.5 `<termino>` (E18, E19 y E20)

**Regla original:**

```
E18  <termino> ::= <termino> MULT <factor>
E19  <termino> ::= <termino> DIV <factor>
E20  <termino> ::= <factor>
```

**Identificación de α y β:**

| Símbolo de la fórmula | Valor |
|---|---|
| A | `<termino>` |
| α₁ | MULT `<factor>` |
| α₂ | DIV `<factor>` |
| α = (α₁,α₂) | (MULT `<factor>`, DIV `<factor>`) |
| β | `<factor>` |
| A' | `<termino_prima>` |

**Sustitución en la fórmula:**

```
A  ::= β A'          ⇒   <termino>       ::= <factor> <termino_prima>
A' ::= α A'          ⇒   <termino_prima> ::= (MULT <factor>, DIV <factor>) <termino_prima>
                     ⇒   <termino_prima> ::= MULT <factor> <termino_prima>      (distribución)
                         <termino_prima> ::= DIV <factor> <termino_prima>
A' ::= ε             ⇒   <termino_prima> ::= ε
```

**Regla resultante:**

```
R13  <termino>       ::= <factor> <termino_prima>
R14  <termino_prima> ::= MULT <factor> <termino_prima>
R15  <termino_prima> ::= DIV <factor> <termino_prima>
R16  <termino_prima> ::= ε
```

**Lenguaje:** antes y después, (`<factor>`)(MULT `<factor>`, DIV `<factor>`)\*.

### 5.6 Resumen

| No terminal | Reglas originales | α | β | Reglas nuevas | Lenguaje (igual antes y después) |
|---|---|---|---|---|---|
| `<sentencias>` | P2, P3 | `<sentencia>` | ε | R1, R2 | (`<sentencia>`)\* |
| `<expresion>` | E1, E2 | O `<conjuncion>` | `<conjuncion>` | R3, R4, R5 | (`<conjuncion>`)(O `<conjuncion>`)\* |
| `<conjuncion>` | E3, E4 | Y `<negacion>` | `<negacion>` | R6, R7, R8 | (`<negacion>`)(Y `<negacion>`)\* |
| `<suma>` | E15, E16, E17 | (SUMA `<termino>`, RESTA `<termino>`) | `<termino>` | R9, R10, R11, R12 | (`<termino>`)(SUMA `<termino>`, RESTA `<termino>`)\* |
| `<termino>` | E18, E19, E20 | (MULT `<factor>`, DIV `<factor>`) | `<factor>` | R13, R14, R15, R16 | (`<factor>`)(MULT `<factor>`, DIV `<factor>`)\* |

## 6. Gramática sin recursividad por la izquierda

Se eliminan 12 reglas (P2, P3, E1–E4, E15–E20) y se agregan 16 (R1–R16). La gramática pasa de 40 a 44 reglas y de 17 a 21 no terminales, con los cuatro nuevos: `<expresion_prima>`, `<conjuncion_prima>`, `<suma_prima>` y `<termino_prima>`.

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
E7   <comparacion> ::= <suma> <op_rel> <suma>
E8   <comparacion> ::= <suma>
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
C1   <condicional> ::= SI PAR_ABRE <expresion> PAR_CIERRA ENTONCES <sentencias> FIN
C2   <condicional> ::= SI PAR_ABRE <expresion> PAR_CIERRA ENTONCES <sentencias> SINO <sentencias> FIN
L1   <ciclo> ::= MIENTRAS PAR_ABRE <expresion> PAR_CIERRA HACER <sentencias> FIN
```

G2 = (N, T, P, S), donde:

- **N** = {`<programa>`, `<sentencias>`, `<sentencia>`, `<declaracion>`, `<expresion>`, `<expresion_prima>`, `<conjuncion>`, `<conjuncion_prima>`, `<negacion>`, `<comparacion>`, `<op_rel>`, `<suma>`, `<suma_prima>`, `<termino>`, `<termino_prima>`, `<factor>`, `<asignacion>`, `<salida>`, `<argumento>`, `<condicional>`, `<ciclo>`}, |N| = 21.
- **T** = los 30 tokens del catálogo que llegan al analizador sintáctico, más `EOF`. No cambia.
- **P** = las 44 reglas anteriores.
- **S** = `<programa>`. No cambia.

### 6.1 Correspondencia con la gramática anterior

| Reglas de GIC-1 + GIC-2 | Reglas de esta gramática |
|---|---|
| P1, P4–P8, D1, E5–E14, E21–E24, A1, M1–M3, C1, C2, L1 | Las mismas, sin cambios (28 reglas) |
| P2, P3 | R1, R2 |
| E1, E2 | R3, R4, R5 |
| E3, E4 | R6, R7, R8 |
| E15, E16, E17 | R9, R10, R11, R12 |
| E18, E19, E20 | R13, R14, R15, R16 |

### 6.2 Comprobación de que no queda recursividad por la izquierda

Ahora hay cinco no terminales anulables: `<sentencias>` (R2), `<expresion_prima>` (R5), `<conjuncion_prima>` (R8), `<suma_prima>` (R12) y `<termino_prima>` (R16). Se repite el análisis de 3.2:

| No terminal | No terminales que pueden quedar de primeros |
|---|---|
| `<sentencias>` | `<sentencia>` (R1) |
| `<expresion>` | `<conjuncion>` (R3) |
| `<conjuncion>` | `<negacion>` (R6) |
| `<suma>` | `<termino>` (R9) |
| `<termino>` | `<factor>` (R13) |
| `<expresion_prima>`, `<conjuncion_prima>`, `<suma_prima>`, `<termino_prima>` | ninguno: empiezan con O, Y, SUMA, RESTA, MULT o DIV, o son ε |
| Los demás | igual que en 3.2 |

- Ninguna regla tiene la forma `A ::= A α`: ya no hay recursividad directa.
- Los anulables nunca están al comienzo de una regla seguidos de otro no terminal: en R1, R3, R6, R9 y R13 el primer símbolo (`<sentencia>`, `<conjuncion>`, `<negacion>`, `<termino>`, `<factor>`) no es anulable, y en E7 tampoco lo es `<suma>`. Por eso los anulables nuevos no crean caminos nuevos.
- Las cadenas de 3.2 quedan igual, sin la flecha de cada no terminal hacia sí mismo, y siguen terminando en terminales:

```
<sentencias> → <sentencia> → <declaracion> | <asignacion> | <salida> | <condicional> | <ciclo>
<argumento> → <expresion> → <conjuncion> → <negacion> → <comparacion> → <suma> → <termino> → <factor>
```

Ningún no terminal puede llegar a sí mismo como primer símbolo: **la gramática no tiene recursividad por la izquierda, ni directa ni indirecta**.

## 7. Efecto sobre la derivación y el árbol

### 7.1 Derivación de `10 - 4 - 2`

Tokens: ENTERO⟨10⟩ RESTA ENTERO⟨4⟩ RESTA ENTERO⟨2⟩. Derivación más a la izquierda desde `<suma>` en las dos gramáticas.

**Con la gramática de GIC-1 (recursiva por la izquierda):**

```
      <suma>
⇒ E16 <suma> RESTA <termino>
⇒ E16 <suma> RESTA <termino> RESTA <termino>
⇒ E17 <termino> RESTA <termino> RESTA <termino>
⇒ E20 <factor> RESTA <termino> RESTA <termino>
⇒ E23 ENTERO⟨10⟩ RESTA <termino> RESTA <termino>
⇒ E20 ENTERO⟨10⟩ RESTA <factor> RESTA <termino>
⇒ E23 ENTERO⟨10⟩ RESTA ENTERO⟨4⟩ RESTA <termino>
⇒ E20 ENTERO⟨10⟩ RESTA ENTERO⟨4⟩ RESTA <factor>
⇒ E23 ENTERO⟨10⟩ RESTA ENTERO⟨4⟩ RESTA ENTERO⟨2⟩
```

**Con la gramática sin recursividad por la izquierda:**

```
      <suma>
⇒ R9  <termino> <suma_prima>
⇒ R13 <factor> <termino_prima> <suma_prima>
⇒ E23 ENTERO⟨10⟩ <termino_prima> <suma_prima>
⇒ R16 ENTERO⟨10⟩ <suma_prima>
⇒ R11 ENTERO⟨10⟩ RESTA <termino> <suma_prima>
⇒ R13 ENTERO⟨10⟩ RESTA <factor> <termino_prima> <suma_prima>
⇒ E23 ENTERO⟨10⟩ RESTA ENTERO⟨4⟩ <termino_prima> <suma_prima>
⇒ R16 ENTERO⟨10⟩ RESTA ENTERO⟨4⟩ <suma_prima>
⇒ R11 ENTERO⟨10⟩ RESTA ENTERO⟨4⟩ RESTA <termino> <suma_prima>
⇒ R13 ENTERO⟨10⟩ RESTA ENTERO⟨4⟩ RESTA <factor> <termino_prima> <suma_prima>
⇒ E23 ENTERO⟨10⟩ RESTA ENTERO⟨4⟩ RESTA ENTERO⟨2⟩ <termino_prima> <suma_prima>
⇒ R16 ENTERO⟨10⟩ RESTA ENTERO⟨4⟩ RESTA ENTERO⟨2⟩ <suma_prima>
⇒ R12 ENTERO⟨10⟩ RESTA ENTERO⟨4⟩ RESTA ENTERO⟨2⟩
```

En la primera derivación, las dos primeras reglas (E16, E16) se eligen **antes de ver ningún token**: hay que saber de antemano que vienen dos RESTA. En la segunda, cada regla se elige cuando llega el token que la justifica: R11 cuando el siguiente token es RESTA, y R16 y R12 cuando ya no viene un operador de su nivel. Esa es la propiedad que necesita el analizador descendente. Cómo se elige exactamente entre las alternativas se formaliza con PRIMERO y SIGUIENTE en GIC-6.

### 7.2 Forma del árbol

En los árboles, `A ── B` indica que B es el único hijo de A.

**Con la gramática de GIC-1:**

```
<suma>
├── <suma>
│   ├── <suma> ── <termino> ── <factor> ── ENTERO⟨10⟩
│   ├── RESTA
│   └── <termino> ── <factor> ── ENTERO⟨4⟩
├── RESTA
└── <termino> ── <factor> ── ENTERO⟨2⟩
```

**Con la gramática sin recursividad por la izquierda:**

```
<suma>
├── <termino>
│   ├── <factor> ── ENTERO⟨10⟩
│   └── <termino_prima> ── ε
└── <suma_prima>
    ├── RESTA
    ├── <termino>
    │   ├── <factor> ── ENTERO⟨4⟩
    │   └── <termino_prima> ── ε
    └── <suma_prima>
        ├── RESTA
        ├── <termino>
        │   ├── <factor> ── ENTERO⟨2⟩
        │   └── <termino_prima> ── ε
        └── <suma_prima> ── ε
```

- **La precedencia no cambia.** Los niveles son los mismos de GIC-1 y GIC-3: cada operador sigue apareciendo solo en las reglas de su nivel (O en R4, Y en R7, SUMA y RESTA en R10 y R11, MULT y DIV en R14 y R15), y el único camino de regreso al nivel superior sigue siendo E21, con paréntesis. En `kilos + 25 * 2`, el MULT sigue quedando dentro de un `<termino>`, más abajo que el SUMA.
- **La asociatividad ya no se ve en la forma del árbol.** En GIC-1 la agrupación `(10 - 4) - 2` se lee directamente: el primer RESTA queda más abajo. En la gramática nueva, el árbol se inclina hacia la derecha, y los operandos y operadores quedan en una cadena de `<suma_prima>` en el mismo orden en que aparecen en el texto. La agrupación por la izquierda se recupera recorriendo esa cadena de izquierda a derecha. Como ya lo indica la sección 8 del documento de GIC-3, la forma en que el analizador de la Fase 3 refleje esa agrupación se define en la Fase 3; la transformación no cambia qué cadenas son válidas.

## 8. Verificación

Además de la demostración de 4.2, se verificó la transformación con dos analizadores escritos para esta tarea: un analizador general (algoritmo de Earley), que acepta cualquier gramática independiente del contexto, incluidas las recursivas por la izquierda, y un analizador descendente ingenuo que prueba todas las alternativas de cada no terminal y cuenta los árboles.

| Prueba | Resultado |
|---|---|
| Analizador descendente ingenuo sobre GIC-1 + GIC-2, entrada `ID` desde `<expresion>` | Recursión infinita: no termina |
| Analizador descendente ingenuo sobre la gramática de la sección 6 | Termina en todas las pruebas de esta tabla |
| Todas las cadenas de hasta 5 tokens desde `<expresion>`, sobre ID, SUMA, RESTA, MULT, DIV, O, Y, NO, MENOR, PAR_ABRE y PAR_CIERRA | 177 156 cadenas, 108 aceptadas, **0 diferencias** entre las dos gramáticas |
| Todas las cadenas de hasta 6 tokens desde `<expresion>`, sobre ID, SUMA, MULT, O, Y, NO, PAR_ABRE y PAR_CIERRA | 299 593 cadenas, 138 aceptadas, **0 diferencias** |
| Todas las cadenas de hasta 5 tokens desde `<sentencias>`, sobre 10 tokens de sentencias | 111 111 cadenas, **0 diferencias**; también 0 diferencias entre la versión simplificada (R1, R2) y la versión sin simplificar de 5.1 |
| 2 996 programas generados al azar desde `<programa>` (hasta 79 tokens), más 2 variantes de cada uno con un token cambiado | 8 988 entradas, 3 287 aceptadas y 5 701 rechazadas, **0 diferencias** |

Las pruebas acotadas no reemplazan la demostración de 4.2, que vale para cadenas de cualquier longitud; la complementan comprobando que las reglas se escribieron sin errores.

**Programas de ejemplo.** Los tres programas de `ejemplos/` siguen siendo derivables y tienen exactamente un árbol de derivación en la gramática nueva:

| Programa | Tokens | Árboles en la gramática de la sección 6 |
|---|---|---|
| `ejemplo1_produccion.cft` | 66 | 1 |
| `ejemplo2_clasificacion.cft` | 62 | 1 |
| `ejemplo3_secado.cft` | 57 | 1 |

**Cadenas de GIC-3.** Las cadenas usadas para demostrar la ambigüedad de la gramática ingenua conservan en la gramática nueva el mismo número de árboles que tenían en G1:

| Entrada | Árboles |
|---|---|
| `kilos + 25 * 2` | 1 |
| `10 - 4 - 2` | 1 |
| `a o b y c` | 1 |
| `no a y b` | 1 |
| `a + b * c - d` | 1 |
| `a + b + c + d + e` | 1 |
| `dia == 5 o no (humedad > 20)` | 1 |
| `a < b < c` | 0 (rechazada) |
| `inicio si (a) entonces si (b) entonces x = 1; sino x = 2; fin fin fin` | 1 |
| `inicio si (a) entonces si (b) entonces x = 1; fin sino x = 2; fin fin` | 1 |
| `inicio si (a) entonces si (b) entonces x = 1; sino x = 2; fin fin` | 0 (rechazada: falta un `fin`) |
| `inicio fin` | 1 |

## 9. Pendientes para las siguientes tareas

| Tarea | Qué queda por hacer sobre la gramática de la sección 6 |
|---|---|
| GIC-5 (Daniel) | Factorizar `<comparacion>` (E7 y E8 empiezan con `<suma>`) y el condicional (C1 y C2 comparten el prefijo `SI PAR_ABRE <expresion> PAR_CIERRA ENTONCES <sentencias>`). Esta tarea no los modifica |
| GIC-6 (Diego) | Calcular PRIMERO y SIGUIENTE sobre la gramática que resulte de GIC-5. Las reglas ε nuevas (R2, R5, R8, R12 y R16) son las que necesitan SIGUIENTE para decidir cuándo se aplican |
| PAR-2 y PAR-3 (Fase 3) | Una función por no terminal, incluidas `expresion_prima`, `conjuncion_prima`, `suma_prima` y `termino_prima`, y decidir cómo se refleja en el árbol la agrupación por la izquierda (sección 7.2) |

## Referencias

Aho, A. V., Lam, M. S., Sethi, R. y Ullman, J. D. (2006). *Compilers: Principles, techniques, and tools* (2.ª ed.). Addison-Wesley.

Hopcroft, J. E., Motwani, R. y Ullman, J. D. (2007). *Introduction to automata theory, languages, and computation* (3.ª ed.). Addison-Wesley.
