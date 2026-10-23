# Fase 2 — BNF de programa, declaraciones y expresiones

**Tarea Jira:** GIC-1 — BNF de programa, declaraciones y expresiones
**Responsable:** Daniel Josué Narváez Hincapié
**Insumos:** catálogo de tokens (`docs/fase1/catalogo_tokens.md`, LEX-1) y especificación informal (`docs/fase1/especificacion_informal.md`, DSL-2)
**Se complementa con:** `gramatica_sentencias.md` (GIC-2: asignación, salida, condicional y ciclo)

---

## 1. Convención de notación BNF

| Elemento | Notación | Ejemplo |
| --- | --- | --- |
| No terminal | Nombre en minúsculas entre `< >` | `<expresion>` |
| Terminal | Nombre del token del catálogo, en MAYÚSCULAS | `DATO`, `ID`, `SUMA` |
| Definición | `::=` | `<factor> ::= ID` |
| Alternativa | `\|` | `<op_rel> ::= MENOR \| MAYOR` |
| Cadena vacía | ε | `<sentencias> ::= ε` |

Los terminales son los **tokens** que entrega el analizador léxico, no los caracteres de Σ. Por eso se escriben con su nombre del catálogo (`SUMA`, `PAR_ABRE`) y no con su lexema (`+`, `(`). Así, ningún símbolo del lenguaje se confunde con los metasímbolos de la BNF.

Para leer las reglas más fácil, esta es la equivalencia entre los terminales que se usan aquí y sus lexemas:

| Terminal | Lexema | Terminal | Lexema |
| --- | --- | --- | --- |
| INICIO | `inicio` | SUMA | `+` |
| FIN | `fin` | RESTA | `-` |
| DATO | `dato` | MULT | `*` |
| O | `o` | DIV | `/` |
| Y | `y` | MENOR | `<` |
| NO | `no` | MAYOR | `>` |
| ID | identificador | MENOR_IGUAL | `<=` |
| ENTERO | número entero | MAYOR_IGUAL | `>=` |
| DECIMAL | número decimal | IGUAL | `==` |
| ASIGNACION | `=` | DIFERENTE | `!=` |
| PUNTO_COMA | `;` | PAR_ABRE, PAR_CIERRA | `(`, `)` |

COMENTARIO y BLANCO no aparecen en la gramática, porque el analizador léxico los descarta.

## 2. Estructura general del programa

```
<programa>    ::= INICIO <sentencias> FIN

<sentencias>  ::= <sentencias> <sentencia>
               |  ε

<sentencia>   ::= <declaracion>
               |  <asignacion>
               |  <salida>
               |  <condicional>
               |  <ciclo>
```

- `<programa>` es el **símbolo inicial** de la gramática.
- `<sentencias>` genera una secuencia de cero o más sentencias. Es recursiva por la izquierda: así se escribe de forma natural una lista que crece hacia la derecha.
- `<asignacion>`, `<salida>`, `<condicional>` y `<ciclo>` se definen en GIC-2. Los bloques de `si` y `mientras` vuelven a usar `<sentencias>`, y por eso pueden anidarse.

## 3. Declaración

```
<declaracion> ::= DATO ID ASIGNACION <expresion> PUNTO_COMA
```

Ejemplo: `dato kilos = 250;` produce la secuencia de tokens DATO ID ASIGNACION ENTERO PUNTO_COMA.

Que una variable no pueda llamarse como una palabra reservada se resuelve aquí sin reglas adicionales. En `dato si = 3;` el lexema `si` llega como el token SI, y la regla exige ID después de DATO, así que la declaración se rechaza.

## 4. Expresiones con niveles de precedencia

En Cafetal, las condiciones de `si` y `mientras` y las expresiones aritméticas comparten **una sola jerarquía de expresiones**. Los operadores lógicos y relacionales son simplemente los niveles de menor precedencia. Así, `no (humedad > 20)` y `(lote_norte + lote_sur) / 2` se describen con las mismas reglas, y el paréntesis queda en un único lugar de la gramática.

```
<expresion>   ::= <expresion> O <conjuncion>
               |  <conjuncion>

<conjuncion>  ::= <conjuncion> Y <negacion>
               |  <negacion>

<negacion>    ::= NO <negacion>
               |  <comparacion>

<comparacion> ::= <suma> <op_rel> <suma>
               |  <suma>

<op_rel>      ::= MENOR | MAYOR | MENOR_IGUAL | MAYOR_IGUAL | IGUAL | DIFERENTE

<suma>        ::= <suma> SUMA <termino>
               |  <suma> RESTA <termino>
               |  <termino>

<termino>     ::= <termino> MULT <factor>
               |  <termino> DIV <factor>
               |  <factor>

<factor>      ::= PAR_ABRE <expresion> PAR_CIERRA
               |  ID
               |  ENTERO
               |  DECIMAL
```

### 4.1 Cómo la gramática fija la precedencia

Cada nivel de precedencia es un no terminal. Un operador de menor precedencia aparece **más arriba** en la gramática, cerca de `<expresion>`, y uno de mayor precedencia aparece **más abajo**, cerca de `<factor>`. Como cada nivel solo puede contener expresiones del nivel inmediatamente inferior, los operadores de mayor precedencia quedan siempre más profundos en el árbol de derivación y se evalúan primero.

| Nivel (de menor a mayor precedencia) | No terminal | Operadores | Asociatividad |
| --- | --- | --- | --- |
| 1 | `<expresion>` | `o` | Izquierda |
| 2 | `<conjuncion>` | `y` | Izquierda |
| 3 | `<negacion>` | `no` (prefijo) | Unario |
| 4 | `<comparacion>` | `< > <= >= == !=` | No asociativo |
| 5 | `<suma>` | `+ -` | Izquierda |
| 6 | `<termino>` | `* /` | Izquierda |
| 7 | `<factor>` | `( )`, operandos | — |

Este orden coincide con el de la especificación informal: `( )`, luego `* /`, `+ -`, relacionales, `no`, `y` y `o`.

### 4.2 Cómo la gramática fija la asociatividad

- **Asociatividad por la izquierda (`o`, `y`, `+ -`, `* /`).** La regla es recursiva por la izquierda, por ejemplo `<suma> ::= <suma> RESTA <termino>`. En `10 - 4 - 2`, el `<suma>` de la izquierda tiene que generar `10 - 4`, de modo que la expresión se agrupa como `(10 - 4) - 2 = 4` y no como `10 - (4 - 2) = 8`.
- **Comparación no asociativa.** `<comparacion>` no es recursiva: a cada lado del operador relacional solo puede ir una `<suma>`. Por eso `a < b < c` **no** es derivable, como exige la especificación. Para comparar resultados de comparaciones hay que usar `y` u `o`: `a < b y b < c`.
- **Negación unaria.** `<negacion> ::= NO <negacion>` es recursiva por la derecha, porque `no` es un operador prefijo: `no no x` se lee como `no (no x)`.

### 4.3 Ejemplo de derivación

Derivación por la izquierda de `kilos + 25 * 2` (tokens: ID SUMA ENTERO MULT ENTERO):

```
<expresion>
⇒ <conjuncion>
⇒ <negacion>
⇒ <comparacion>
⇒ <suma>
⇒ <suma> SUMA <termino>
⇒ <termino> SUMA <termino>
⇒ <factor> SUMA <termino>
⇒ ID SUMA <termino>
⇒ ID SUMA <termino> MULT <factor>
⇒ ID SUMA <factor> MULT <factor>
⇒ ID SUMA ENTERO MULT <factor>
⇒ ID SUMA ENTERO MULT ENTERO
```

Árbol de derivación (a partir de `<suma>`):

```
                <suma>
         ┌────────┼─────────────┐
       <suma>    SUMA        <termino>
         │                ┌─────┼──────┐
     <termino>        <termino> MULT  <factor>
         │                │              │
      <factor>         <factor>       ENTERO (2)
         │                │
      ID (kilos)      ENTERO (25)
```

La multiplicación queda dentro del `<termino>` derecho, más abajo que la suma, así que `25 * 2` se agrupa primero. En el programa de secado, `kilos + 25 * 2` vale `kilos + 50`, nunca `(kilos + 25) * 2`.

Un segundo ejemplo, con operadores lógicos, es la condición del programa de secado: `dia == 5 o no (humedad > 20)`. La derivación empieza por `<expresion> ⇒ <expresion> O <conjuncion>`:
- el lado izquierdo deriva la comparación `dia == 5`;
- el lado derecho deriva `NO <negacion>`, y la `<negacion>` llega hasta `<factor> ⇒ PAR_ABRE <expresion> PAR_CIERRA`, que contiene la comparación `humedad > 20`.

## 5. Gramática formal

G = (N, T, P, S), donde:

- **N** (no terminales de esta parte) = {`<programa>`, `<sentencias>`, `<sentencia>`, `<declaracion>`, `<expresion>`, `<conjuncion>`, `<negacion>`, `<comparacion>`, `<op_rel>`, `<suma>`, `<termino>`, `<factor>`}, a los que GIC-2 suma `<asignacion>`, `<salida>`, `<condicional>` y `<ciclo>`.
- **T** (terminales) = los 30 tokens del catálogo que se entregan al analizador sintáctico, más `EOF` como marcador de fin.
- **P** = las producciones de las secciones 2 a 4, junto con las de GIC-2.
- **S** = `<programa>`.

## 6. Verificación

Se derivaron con esta gramática, junto con las reglas de sentencias de GIC-2, los 3 programas de `ejemplos/`. Los tres son derivables desde `<programa>`. También se comprobó que la gramática rechaza:

| Entrada | Resultado | Motivo |
| --- | --- | --- |
| `dato x = 1 < 2 < 3;` | Rechazada | La comparación no es asociativa: después de `1 < 2` se espera PUNTO_COMA y llega MENOR |
| `dato x = (1 + ;` | Rechazada | Después de SUMA se espera un `<factor>` y llega PUNTO_COMA |
| `dato si = 3;` | Rechazada | Después de DATO se espera ID y llega SI |

## 7. Pendientes para las siguientes tareas de la Fase 2

Esta es la gramática **inicial**: no es ambigua, porque la precedencia y la asociatividad están fijadas por niveles, pero todavía no está lista para un analizador descendente.

| Tarea | Qué queda por hacer sobre esta gramática |
| --- | --- |
| GIC-3 (Daniel) | Mostrar la gramática ingenua `E → E + E \| E * E \| (E) \| id`, probar que es ambigua con dos árboles para una misma cadena y justificar la estratificación de la sección 4 |
| GIC-4 (Diego) | Eliminar la recursividad por la izquierda de `<sentencias>`, `<expresion>`, `<conjuncion>`, `<suma>` y `<termino>` |
| GIC-5 (Daniel) | Factorizar `<comparacion>`, cuyas dos alternativas empiezan con `<suma>`, y el condicional con y sin `sino` de GIC-2 |
| GIC-6 (Diego) | Calcular PRIMERO y SIGUIENTE y construir la tabla LL(1) de la gramática final |
