# Fase 2: Estructura sintáctica del lenguaje de dominio específico Cafetal

**Proyecto:** Diseño, auditoría e ingeniería inversa de un mini-lenguaje de programación de dominio específico (DSL) en Python
**Curso:** Teoría de Lenguajes Formales, Universidad del Quindío, 2026-2
**Docente:** Ana María Tamayo Ocampo
**Integrantes:** Daniel Josué Narváez Hincapié (código 1090273355) y Juan Diego García Albarracín (código 1090273470)
**Tarea Jira:** DOC-3 — Documento de la Fase 2

---

## Introducción

Este documento presenta la estructura sintáctica de Cafetal, el lenguaje de dominio específico diseñado por el equipo para registrar y calcular la producción de una finca cafetera. La Fase 2 exige definir la gramática independiente del contexto (GIC) del lenguaje en formato Backus-Naur (BNF) y demostrar matemáticamente la eliminación de la recursividad por la izquierda y la factorización, para garantizar una gramática no ambigua.

El documento sigue el **orden de las transformaciones** que llevaron de la gramática inicial a la gramática final que usa el analizador sintáctico de la Fase 3:

1. **Gramática inicial** (sección 2): la BNF del programa, las sentencias y las expresiones, escrita de la forma más natural.
2. **Ambigüedad y estratificación** (sección 3): se demuestra que una gramática ingenua de expresiones es ambigua y se justifica la estratificación por niveles de precedencia que tiene la gramática inicial; se muestra también cómo el delimitador `fin` elimina el sino colgante.
3. **Eliminación de la recursividad por la izquierda** (sección 4).
4. **Factorización por la izquierda** (sección 5).
5. **Conjuntos PRIMERO y SIGUIENTE y tabla LL(1)** (sección 6): una tabla sin celdas con dos reglas es el argumento formal de que la gramática final no es ambigua.
6. **Gramática final** (sección 7), con la correspondencia de cada regla con su origen.

Cada transformación se demuestra paso a paso y se verifica que no cambia el lenguaje. Las derivaciones completas de los programas de ejemplo y las tablas de verificación están en los apéndices. Los documentos fuente de cada tarea, los diagramas editables y el código están en el repositorio del proyecto (Narváez Hincapié y García Albarracín, 2026); el Apéndice C indica dónde está cada uno.

## 1. Notación

### 1.1 Notación BNF

**Tabla 1**

*Notación BNF usada en todo el documento*

| Elemento | Notación | Ejemplo |
|---|---|---|
| No terminal | Nombre en minúsculas entre `< >` | `<expresion>` |
| Terminal | Nombre del token del catálogo de la Fase 1, en MAYÚSCULAS | `DATO`, `ID`, `SUMA` |
| Definición | `::=` | `<factor> ::= ID` |
| Alternativa | `\|` | `<op_rel> ::= MENOR \| MAYOR` |
| Cadena vacía | ε | `<sentencias> ::= ε` |

Los terminales son los **tokens** que entrega el analizador léxico de la Fase 1, no los caracteres de Σ. Por eso se escriben con su nombre del catálogo (`SUMA`, `PAR_ABRE`) y no con su lexema (`+`, `(`): así ningún símbolo del lenguaje se confunde con los metasímbolos de la BNF. COMENTARIO y BLANCO no aparecen en la gramática, porque el analizador léxico los descarta. `EOF` (código 99) marca el fin de la entrada.

**Tabla 2**

*Terminales de la gramática y sus lexemas*

| Terminal | Lexema | Terminal | Lexema |
|---|---|---|---|
| INICIO | `inicio` | SUMA | `+` |
| FIN | `fin` | RESTA | `-` |
| DATO | `dato` | MULT | `*` |
| SI | `si` | DIV | `/` |
| ENTONCES | `entonces` | MENOR | `<` |
| SINO | `sino` | MAYOR | `>` |
| MIENTRAS | `mientras` | MENOR_IGUAL | `<=` |
| HACER | `hacer` | MAYOR_IGUAL | `>=` |
| MOSTRAR | `mostrar` | IGUAL | `==` |
| Y, O, NO | `y`, `o`, `no` | DIFERENTE | `!=` |
| ID | identificador | ASIGNACION | `=` |
| ENTERO | número entero | PAR_ABRE, PAR_CIERRA | `(`, `)` |
| DECIMAL | número decimal | PUNTO_COMA | `;` |
| CADENA | cadena entre comillas | EOF | fin de la entrada |

### 1.2 Lenguajes con expresiones regulares primitivas

Para comparar lo que genera un no terminal antes y después de una transformación, se escribe ese conjunto de formas con los mismos operadores primitivos de la Fase 1: unión con coma (`a,b`), concatenación por yuxtaposición o con paréntesis (`ab`, `(a)(b)`) y cerradura de Kleene `( )*`. ε es una expresión regular primitiva, no un operador. Aquí los símbolos no son caracteres de Σ sino símbolos de la gramática; ningún nombre de token contiene coma ni paréntesis, así que no chocan con los metasímbolos.

### 1.3 Numeración de las reglas

Cada alternativa de la gramática tiene una etiqueta, que se conserva en todas las secciones y en el código del analizador:

**Tabla 3**

*Etiquetas de las reglas*

| Etiquetas | Origen | Contenido |
|---|---|---|
| P1–P8 | Gramática inicial | Programa, lista de sentencias y tipos de sentencia |
| D1 | Gramática inicial | Declaración |
| E1–E24 | Gramática inicial | Expresiones |
| A1, M1–M3, C1, C2, L1 | Gramática inicial | Asignación, salida, condicional y ciclo |
| R1–R16 | Eliminación de la recursividad (sección 4) | Reglas que reemplazan a las recursivas por la izquierda |
| F1–F6 | Factorización (sección 5) | Reglas que reemplazan a las que tenían prefijo común |

En las derivaciones, el lexema de ID, ENTERO y DECIMAL se indica entre ⟨ ⟩, por ejemplo ID⟨kilos⟩.

## 2. Gramática inicial

La gramática inicial se escribió de la forma más natural, sin pensar todavía en el analizador: las listas y los operadores asociativos por la izquierda usan recursividad por la izquierda, y el condicional con y sin `sino` son dos reglas separadas. Las secciones 4 y 5 la transforman para el analizador descendente.

### 2.1 Programa y sentencias

```
P1   <programa>    ::= INICIO <sentencias> FIN
P2   <sentencias>  ::= <sentencias> <sentencia>
P3   <sentencias>  ::= ε
P4   <sentencia>   ::= <declaracion>
P5   <sentencia>   ::= <asignacion>
P6   <sentencia>   ::= <salida>
P7   <sentencia>   ::= <condicional>
P8   <sentencia>   ::= <ciclo>
D1   <declaracion> ::= DATO ID ASIGNACION <expresion> PUNTO_COMA
A1   <asignacion>  ::= ID ASIGNACION <expresion> PUNTO_COMA
M1   <salida>      ::= MOSTRAR PAR_ABRE <argumento> PAR_CIERRA PUNTO_COMA
M2   <argumento>   ::= <expresion>
M3   <argumento>   ::= CADENA
C1   <condicional> ::= SI PAR_ABRE <expresion> PAR_CIERRA ENTONCES <sentencias> FIN
C2   <condicional> ::= SI PAR_ABRE <expresion> PAR_CIERRA ENTONCES <sentencias> SINO <sentencias> FIN
L1   <ciclo>       ::= MIENTRAS PAR_ABRE <expresion> PAR_CIERRA HACER <sentencias> FIN
```

- `<programa>` es el **símbolo inicial**. `<sentencias>` genera una secuencia de cero o más sentencias.
- **Declaración y asignación.** La declaración empieza con DATO y la asignación con ID, así que nunca se confunden. Que una variable no pueda llamarse como una palabra reservada se resuelve sin reglas adicionales: en `dato si = 3;` el lexema `si` llega como el token SI, y D1 exige ID después de DATO.
- **Salida.** `mostrar` recibe una `<expresion>` o una CADENA. Se necesita la alternativa CADENA porque las cadenas no forman parte de las expresiones: `"kilos" + 1` no es una expresión válida.
- **Lectura.** Cafetal no tiene instrucción de lectura: la especificación solo define la salida con `mostrar`, y los datos se escriben en el programa con `dato`.
- **Bloques.** Los bloques de `si` y `mientras` usan `<sentencias>`, así que pueden estar vacíos o contener cualquier sentencia, incluidos otros `si` y `mientras`. Todo bloque termina con su propio `fin`, lo que elimina el sino colgante (sección 3.5).
- **Paréntesis de las sentencias.** La condición de `si` y `mientras` y el argumento de `mostrar` van entre paréntesis propios de la sentencia, distintos de los de `<factor>`: en `si ((a + b) > 2)` el primer `(` es de la sentencia y el segundo del factor.

### 2.2 Expresiones con niveles de precedencia

Las condiciones de `si` y `mientras` y las expresiones aritméticas comparten **una sola jerarquía de expresiones**: los operadores lógicos y relacionales son los niveles de menor precedencia. Así, `no (humedad > 20)` y `(lote_norte + lote_sur) / 2` se describen con las mismas reglas.

```
E1   <expresion>   ::= <expresion> O <conjuncion>
E2   <expresion>   ::= <conjuncion>
E3   <conjuncion>  ::= <conjuncion> Y <negacion>
E4   <conjuncion>  ::= <negacion>
E5   <negacion>    ::= NO <negacion>
E6   <negacion>    ::= <comparacion>
E7   <comparacion> ::= <suma> <op_rel> <suma>
E8   <comparacion> ::= <suma>
E9   <op_rel>      ::= MENOR
E10  <op_rel>      ::= MAYOR
E11  <op_rel>      ::= MENOR_IGUAL
E12  <op_rel>      ::= MAYOR_IGUAL
E13  <op_rel>      ::= IGUAL
E14  <op_rel>      ::= DIFERENTE
E15  <suma>        ::= <suma> SUMA <termino>
E16  <suma>        ::= <suma> RESTA <termino>
E17  <suma>        ::= <termino>
E18  <termino>     ::= <termino> MULT <factor>
E19  <termino>     ::= <termino> DIV <factor>
E20  <termino>     ::= <factor>
E21  <factor>      ::= PAR_ABRE <expresion> PAR_CIERRA
E22  <factor>      ::= ID
E23  <factor>      ::= ENTERO
E24  <factor>      ::= DECIMAL
```

Cada nivel de precedencia es un no terminal. Un operador de menor precedencia aparece más arriba en la gramática, cerca de `<expresion>`, y uno de mayor precedencia más abajo, cerca de `<factor>`. Como cada nivel solo puede contener expresiones del nivel inmediatamente inferior, los operadores de mayor precedencia quedan siempre más profundos en el árbol y se evalúan primero.

**Tabla 4**

*Niveles de precedencia de las expresiones*

| Nivel (de menor a mayor precedencia) | No terminal | Operadores | Asociatividad |
|---|---|---|---|
| 1 | `<expresion>` | `o` | Izquierda |
| 2 | `<conjuncion>` | `y` | Izquierda |
| 3 | `<negacion>` | `no` (prefijo) | Unario |
| 4 | `<comparacion>` | `< > <= >= == !=` | No asociativo |
| 5 | `<suma>` | `+ -` | Izquierda |
| 6 | `<termino>` | `* /` | Izquierda |
| 7 | `<factor>` | `( )`, operandos | — |

- **Asociatividad por la izquierda** (`o`, `y`, `+ -`, `* /`): la regla es recursiva por la izquierda, como `<suma> ::= <suma> RESTA <termino>`. En `10 - 4 - 2`, el `<suma>` de la izquierda tiene que generar `10 - 4`, de modo que la expresión se agrupa como `(10 - 4) - 2`.
- **Comparación no asociativa:** `<comparacion>` no es recursiva; a cada lado del relacional solo cabe una `<suma>`. Por eso `a < b < c` no es derivable, como exige la especificación.
- **Negación unaria:** `<negacion> ::= NO <negacion>` es recursiva por la derecha, porque `no` es prefijo: `no no x` se lee `no (no x)`.

### 2.3 Gramática inicial completa

G = (N, T, P, S), donde N tiene 17 no terminales (`<programa>`, `<sentencias>`, `<sentencia>`, `<declaracion>`, `<asignacion>`, `<salida>`, `<argumento>`, `<condicional>`, `<ciclo>`, `<expresion>`, `<conjuncion>`, `<negacion>`, `<comparacion>`, `<op_rel>`, `<suma>`, `<termino>` y `<factor>`), T son los 30 tokens del catálogo que llegan al analizador sintáctico más `EOF`, P son las 40 reglas de las secciones 2.1 y 2.2, y S = `<programa>`.

### 2.4 Ejemplos de derivación

Derivación más a la izquierda de `kilos + 25 * 2` (tokens ID SUMA ENTERO MULT ENTERO):

```
      <expresion>
⇒ E2  <conjuncion>
⇒ E4  <negacion>
⇒ E6  <comparacion>
⇒ E8  <suma>
⇒ E15 <suma> SUMA <termino>
⇒ E17 <termino> SUMA <termino>
⇒ E20 <factor> SUMA <termino>
⇒ E22 ID SUMA <termino>
⇒ E18 ID SUMA <termino> MULT <factor>
⇒ E20 ID SUMA <factor> MULT <factor>
⇒ E23 ID SUMA ENTERO MULT <factor>
⇒ E23 ID SUMA ENTERO MULT ENTERO
```

**Figura 1**

*Árbol de derivación de kilos + 25 \* 2 en la gramática inicial*

![Árbol de derivación de kilos + 25 * 2](arboles/img/gic1_arboles_expresiones-Aritmetica.drawio.png)

*Nota.* La multiplicación queda dentro del `<termino>` derecho, más abajo que la suma, así que `25 * 2` se agrupa primero. Fuente editable: `arboles/gic1_arboles_expresiones.drawio`, página Aritmetica.

El segundo ejemplo es la condición del programa de secado, `dia == 5 o no (humedad > 20)`. El `o` aparece en el primer paso (E1) porque es el operador de menor precedencia; la comparación `humedad > 20` queda dentro de un `<factor>` entre paréntesis (E21), debajo del `no` (E5). Su derivación paso a paso está en el Apéndice A.4.

**Figura 2**

*Árbol de derivación de dia == 5 o no (humedad > 20)*

![Árbol de derivación de la condición del secado](arboles/img/gic1_arboles_expresiones-Condicion.drawio.png)

*Nota.* Fuente editable: `arboles/gic1_arboles_expresiones.drawio`, página Condicion.

### 2.5 Verificación de la gramática inicial

Los tres programas de ejemplo se convirtieron en tokens con el AFD de la Fase 1 y se derivaron desde `<programa>`. Un analizador general, que no supone nada sobre la forma de la gramática, contó sus árboles de derivación:

**Tabla 5**

*Derivación de los programas de ejemplo con la gramática inicial*

| Programa | Tokens | Sentencias | Árboles de derivación | Resultado |
|---|---|---|---|---|
| `ejemplo1_produccion.cft` | 66 | 10 | 1 | Derivable |
| `ejemplo2_clasificacion.cft` | 62 | 9 | 1 | Derivable |
| `ejemplo3_secado.cft` | 57 | 8 | 1 | Derivable |

Las derivaciones más a la izquierda completas están en el Apéndice A. La Figura 3 muestra el árbol del programa de secado, con las expresiones abreviadas.

**Figura 3**

*Árbol de derivación de ejemplo3_secado.cft*

![Árbol de derivación de ejemplo3_secado.cft](arboles/img/gic2_arboles_sentencias-Secado.drawio.png)

*Nota.* Las expresiones aparecen abreviadas (⇒*) con los tokens que generan. La imagen está a resolución completa y se puede ampliar en el documento digital. Fuente editable: `arboles/gic2_arboles_sentencias.drawio`, página Secado.

La gramática también rechaza las entradas que la especificación prohíbe:

**Tabla 6**

*Entradas rechazadas por la gramática inicial*

| Entrada | Motivo |
|---|---|
| `dato x = 1 < 2 < 3;` | La comparación no es asociativa: después de `1 < 2` se espera PUNTO_COMA y llega MENOR |
| `dato x = (1 + ;` | Después de SUMA se espera un `<factor>` y llega PUNTO_COMA |
| `dato si = 3;` | Después de DATO se espera ID y llega SI |

## 3. Ambigüedad y estratificación por precedencia

Una GIC es **ambigua** si existe al menos una cadena con dos árboles de derivación distintos o, lo que es equivalente, con dos derivaciones más a la izquierda distintas (Hopcroft et al., 2007). Para probar que una gramática **es** ambigua basta una cadena con dos árboles; para probar que **no** lo es, hace falta un argumento que valga para todas las cadenas. Esta sección hace las dos cosas: prueba que una gramática ingenua de las expresiones de Cafetal es ambigua, la transforma en la gramática estratificada de la sección 2.2 y demuestra que esta asigna a cada cadena un único árbol. Después hace lo mismo con el condicional.

### 3.1 La gramática ingenua G0

La forma más directa de escribir las expresiones es poner todos los operadores en un único no terminal `<E>`:

```
N1   <E> ::= <E> SUMA <E>
N2   <E> ::= <E> RESTA <E>
N3   <E> ::= <E> MULT <E>
N4   <E> ::= <E> DIV <E>
N5   <E> ::= PAR_ABRE <E> PAR_CIERRA
N6   <E> ::= ID
N7   <E> ::= ENTERO
N8   <E> ::= DECIMAL
N9   <E> ::= <E> O <E>
N10  <E> ::= <E> Y <E>
N11  <E> ::= NO <E>
N12  <E> ::= <E> <op_rel> <E>
N13  <op_rel> ::= MENOR | MAYOR | MENOR_IGUAL | MAYOR_IGUAL | IGUAL | DIFERENTE
```

G0 dice **qué** operadores existen, pero no **en qué orden** se aplican. Las reglas binarias tienen la forma `<E> ::= <E> op <E>`, con `<E>` a ambos lados del operador: cuando una cadena tiene dos operadores, cualquiera de los dos puede quedar en la raíz del árbol.

### 3.2 Demostraciones de ambigüedad de G0

**Precedencia: `kilos + 25 * 2`.** Tokens: ID⟨kilos⟩ SUMA ENTERO⟨25⟩ MULT ENTERO⟨2⟩. Dos derivaciones más a la izquierda distintas:

```
Derivación 1 (N1 en la raíz)
      <E>
⇒ N1  <E> SUMA <E>
⇒ N6  ID⟨kilos⟩ SUMA <E>
⇒ N3  ID⟨kilos⟩ SUMA <E> MULT <E>
⇒ N7  ID⟨kilos⟩ SUMA ENTERO⟨25⟩ MULT <E>
⇒ N7  ID⟨kilos⟩ SUMA ENTERO⟨25⟩ MULT ENTERO⟨2⟩

Derivación 2 (N3 en la raíz)
      <E>
⇒ N3  <E> MULT <E>
⇒ N1  <E> SUMA <E> MULT <E>
⇒ N6  ID⟨kilos⟩ SUMA <E> MULT <E>
⇒ N7  ID⟨kilos⟩ SUMA ENTERO⟨25⟩ MULT <E>
⇒ N7  ID⟨kilos⟩ SUMA ENTERO⟨25⟩ MULT ENTERO⟨2⟩
```

Las dos llegan a la misma cadena y difieren desde el primer paso, así que producen árboles distintos. La diferencia no es solo de forma: con `kilos = 100`, el árbol 1 calcula `kilos + (25 * 2) = 150` y el árbol 2 calcula `(kilos + 25) * 2 = 250`.

**Figura 4**

*Dos árboles de kilos + 25 \* 2 en la gramática ingenua G0*

![Dos árboles de kilos + 25 * 2 en G0](arboles/img/gic3_ambiguedad-Precedencia.drawio.png)

*Nota.* Solo el árbol 1 respeta la precedencia de Cafetal, en la que `*` va antes que `+`. Fuente editable: `arboles/gic3_ambiguedad.drawio`, página Precedencia.

**Asociatividad: `10 - 4 - 2`.** Tokens: ENTERO⟨10⟩ RESTA ENTERO⟨4⟩ RESTA ENTERO⟨2⟩. Los dos operadores son el mismo, así que el problema no es de precedencia sino de agrupación:

```
Derivación 1: (10 - 4) - 2
      <E>
⇒ N2  <E> RESTA <E>
⇒ N2  <E> RESTA <E> RESTA <E>
⇒ N7  ENTERO⟨10⟩ RESTA <E> RESTA <E>
⇒ N7  ENTERO⟨10⟩ RESTA ENTERO⟨4⟩ RESTA <E>
⇒ N7  ENTERO⟨10⟩ RESTA ENTERO⟨4⟩ RESTA ENTERO⟨2⟩

Derivación 2: 10 - (4 - 2)
      <E>
⇒ N2  <E> RESTA <E>
⇒ N7  ENTERO⟨10⟩ RESTA <E>
⇒ N2  ENTERO⟨10⟩ RESTA <E> RESTA <E>
⇒ N7  ENTERO⟨10⟩ RESTA ENTERO⟨4⟩ RESTA <E>
⇒ N7  ENTERO⟨10⟩ RESTA ENTERO⟨4⟩ RESTA ENTERO⟨2⟩
```

**Figura 5**

*Dos árboles de 10 - 4 - 2 en G0*

![Dos árboles de 10 - 4 - 2 en G0](arboles/img/gic3_ambiguedad-Asociatividad.drawio.png)

*Nota.* El árbol 1 vale `(10 - 4) - 2 = 4` y el árbol 2 vale `10 - (4 - 2) = 8`. Cafetal, como la aritmética usual, agrupa por la izquierda. Fuente editable: `arboles/gic3_ambiguedad.drawio`, página Asociatividad.

**Operadores lógicos: `a o b y c`.** Es el mismo problema de la precedencia, en los niveles lógicos: una derivación pone N9 (`o`) en la raíz y agrupa `a o (b y c)`; la otra pone N10 (`y`) en la raíz y agrupa `(a o b) y c`.

**Figura 6**

*Dos árboles de a o b y c en G0*

![Dos árboles de a o b y c en G0](arboles/img/gic3_ambiguedad-Logicos.drawio.png)

*Nota.* Con `a` y `b` verdaderos y `c` falso, el árbol 1 da verdadero y el árbol 2 da falso. En Cafetal `y` tiene mayor precedencia que `o`, así que el correcto es el árbol 1. Fuente editable: `arboles/gic3_ambiguedad.drawio`, página Logicos.

G0 tiene otros dos defectos: `no a y b` tiene dos árboles, `(no a) y b` y `no (a y b)`, y `a < b < c` tiene dos árboles aunque, según la especificación, **no debería ser válida**. G0 no solo es ambigua: además genera cadenas que el lenguaje debe rechazar.

En G0, una expresión con n operadores binarios seguidos y sin paréntesis tiene tantos árboles como formas de colocar los paréntesis, que es el número de Catalan Cₙ (1, 2, 5, 14, …). Se contaron los árboles con un analizador general por programación dinámica:

**Tabla 7**

*Número de árboles de derivación en la gramática ingenua G0 y en la estratificada G1*

| Expresión | Árboles en G0 | Árboles en G1 |
|---|---|---|
| `kilos + 25 * 2` | 2 | 1 |
| `10 - 4 - 2` | 2 | 1 |
| `a o b y c` | 2 | 1 |
| `no a y b` | 2 | 1 |
| `a + b * c - d` | 5 | 1 |
| `a + b + c + d + e` | 14 | 1 |
| `dia == 5 o no (humedad > 20)` | 2 | 1 |
| `(a + b) * c` | 1 | 1 |
| `a < b < c` | 2 | 0 (rechazada) |

Los paréntesis explícitos sí quitan la ambigüedad en G0, como muestra `(a + b) * c`, pero no se puede exigir que el programador escriba todos los paréntesis: la gramática tiene que resolver por sí sola los casos sin paréntesis.

### 3.3 Estratificación: de G0 a G1

La ambigüedad de G0 viene de que el mismo no terminal está a ambos lados de cada operador. La solución es **estratificar** la gramática:

1. **Un no terminal por nivel de precedencia**, y cada operador se introduce solo en su nivel.
2. **Cada nivel solo usa el nivel inmediatamente inferior como operando**, así que un operador de mayor precedencia nunca puede quedar por encima de uno de menor precedencia.
3. **La forma de la regla fija la asociatividad**: la recursión va solo hacia el lado por el que se agrupa.
4. **Los paréntesis vuelven al nivel superior**: `<factor>` es el único que reinicia la jerarquía con `PAR_ABRE <expresion> PAR_CIERRA`.

Cada nivel sigue uno de tres patrones, donde A es el no terminal del nivel y B el del nivel siguiente:

**Tabla 8**

*Patrones de regla de la estratificación*

| Patrón | Niveles | Efecto |
|---|---|---|
| `A ::= A op B \| B` | `o`, `y`, `+ -`, `* /` | Asociativo por la izquierda: a la derecha del operador solo cabe un B, que no contiene `op` sin paréntesis, así que `a op b op c` se agrupa `(a op b) op c` |
| `A ::= op A \| B` | `no` | Prefijo unario que se puede repetir: `no no x` es `no (no x)` |
| `A ::= B op B \| B` | relacionales | No asociativo: a cada lado solo cabe un B, así que `a < b < c` no es derivable |

La transformación se hizo en cinco pasos:

1. **Aritmética.** N1–N4 se reemplazan por `<suma>` (`+ -`, nivel 5) y `<termino>` (`* /`, nivel 6), y los operandos y paréntesis pasan a `<factor>`. Es la gramática clásica de expresiones E–T–F (Aho et al., 2006).
2. **Relacionales.** N12 se reemplaza por `<comparacion> ::= <suma> <op_rel> <suma> | <suma>`.
3. **Negación.** N11 se reemplaza por `<negacion> ::= NO <negacion> | <comparacion>`.
4. **Conjunción y disyunción.** N10 y N9 se reemplazan por `<conjuncion> ::= <conjuncion> Y <negacion> | <negacion>` y `<expresion> ::= <expresion> O <conjuncion> | <conjuncion>`.
5. **Paréntesis.** Como `<expresion>` es ahora el nivel más alto, la regla de paréntesis pasa a contener una expresión completa: `<factor> ::= PAR_ABRE <expresion> PAR_CIERRA`.

El resultado, G1, es exactamente la jerarquía de expresiones E1–E24 de la sección 2.2:

**Tabla 9**

*Correspondencia entre las reglas de G0 y las de G1*

| Regla de G0 | Reglas de G1 que la reemplazan |
|---|---|
| N9 (`o`) | E1, E2 |
| N10 (`y`) | E3, E4 |
| N11 (`no`) | E5, E6 |
| N12, N13 (relacionales) | E7, E8, E9–E14 |
| N1, N2 (`+ -`) | E15, E16, E17 |
| N3, N4 (`* /`) | E18, E19, E20 |
| N5 (paréntesis) | E21 |
| N6, N7, N8 (operandos) | E22, E23, E24 |

G1 no genera el mismo lenguaje que G0, sino uno más pequeño: L(G1) ⊂ L(G0). G0 acepta además cadenas como `a < b < c`, que la especificación prohíbe. La estratificación quita la ambigüedad y, a la vez, deja el lenguaje exactamente como lo pide la especificación.

**Figura 7**

*Árboles únicos de 10 - 4 - 2 y a o b y c en G1*

![Árboles únicos en G1](arboles/img/gic3_ambiguedad-Estratificada.drawio.png)

*Nota.* En `10 - 4 - 2`, la recursión izquierda de E16 obliga a que el `<suma>` izquierdo genere `10 - 4`. En `a o b y c`, el O solo puede aparecer en E1, en la raíz, y el Y queda dentro de la `<conjuncion>` derecha. Fuente editable: `arboles/gic3_ambiguedad.drawio`, página Estratificada.

### 3.4 Por qué G1 no es ambigua

Un token está **a nivel cero** si no está encerrado entre un PAR_ABRE y su PAR_CIERRA correspondiente.

**Lema 1.** Una cadena derivada desde cada no terminal solo puede tener a nivel cero los operadores de su nivel y de los niveles de mayor precedencia. Por ejemplo, `<termino>` solo puede tener MULT y DIV a nivel cero, y `<suma>` no puede tener relacionales, NO, Y ni O.

*Prueba.* Cada operador aparece en una sola familia de reglas (SUMA solo en E15, Y solo en E3, etc.), y desde un nivel solo se baja a niveles de mayor precedencia. La única forma de volver a un nivel superior es E21, que encierra la `<expresion>` entre paréntesis, fuera del nivel cero. ∎

**Proposición.** Para todo no terminal A de G1 y toda cadena w, existe a lo sumo un árbol de derivación con raíz A y frontera w.

*Prueba.* Por inducción sobre la longitud de w y, para la misma longitud, sobre el nivel de A. En cada caso la primera regla y la forma de partir w quedan determinadas por w:

- **`<expresion>`**: si w no tiene O a nivel cero, solo aplica E2. Si lo tiene, solo aplica E1, y como la `<conjuncion>` derecha no puede tener O a nivel cero (Lema 1), el O de la regla es **el último O a nivel cero de w**. La partición es única.
- **`<conjuncion>`, `<suma>` y `<termino>`**: igual, con el último Y, el último SUMA o RESTA y el último MULT o DIV a nivel cero.
- **`<negacion>`**: si w empieza con NO, aplica E5, porque una `<comparacion>` no puede empezar con NO; si no, E6.
- **`<comparacion>`**: con cero relacionales a nivel cero aplica E8; con uno, E7 parte w en ese relacional; con dos o más, ninguna regla aplica y w no tiene árbol. Así se rechaza `a < b < c`.
- **`<factor>`**: el primer token decide (PAR_ABRE, ID, ENTERO o DECIMAL).

En ningún caso hay dos reglas posibles ni dos formas de partir la cadena, así que el árbol es único. ∎

La prueba muestra además **por qué** el árbol es el correcto: en cada nivel, la raíz es el operador de menor precedencia y, entre varios iguales, el último. Eso es exactamente evaluar primero los de mayor precedencia y agrupar por la izquierda.

### 3.5 El sino colgante

Si el condicional no tuviera un delimitador de cierre y cada rama fuera una sola sentencia, se escribiría así:

```
S1   <sentencia>   ::= <condicional>
S2   <sentencia>   ::= <asignacion>
K1   <condicional> ::= SI PAR_ABRE <expresion> PAR_CIERRA ENTONCES <sentencia>
K2   <condicional> ::= SI PAR_ABRE <expresion> PAR_CIERRA ENTONCES <sentencia> SINO <sentencia>
```

Para `si (a) entonces si (b) entonces x = 1; sino x = 2;`, una derivación aplica K1 al `si` externo y K2 al interno (el `sino` es del `si` interno), y otra aplica K2 al externo y K1 al interno (el `sino` es del externo). Las derivaciones difieren en el segundo paso, así que esta gramática es ambigua.

**Figura 8**

*Gramática sin delimitador de cierre: primer árbol, el sino es del si interno*

![Sino colgante, árbol 1](arboles/img/gic3_ambiguedad-SinoIngenua-a.png)

*Nota.* Fuente editable: `arboles/gic3_ambiguedad.drawio`, página SinoIngenua (árbol izquierdo).

**Figura 9**

*Gramática sin delimitador de cierre: segundo árbol, el sino es del si externo*

![Sino colgante, árbol 2](arboles/img/gic3_ambiguedad-SinoIngenua-b.png)

*Nota.* Con `a` falso, el primer árbol no ejecuta nada y el segundo ejecuta `x = 2`. Fuente editable: `arboles/gic3_ambiguedad.drawio`, página SinoIngenua (árbol derecho).

Lenguajes como C o Java resuelven este caso con una regla externa a la gramática ("el `else` pertenece al `if` más cercano"). Cafetal lo resuelve **dentro** de la gramática: todo condicional y todo ciclo termina con `fin` (reglas C1, C2 y L1). Con `fin`, las dos lecturas ya no son dos árboles de la misma cadena, sino **dos cadenas distintas**, y el programador escribe la que quiere:

**Tabla 10**

*El sino colgante en Cafetal*

| Texto | Significado | Árboles |
|---|---|---|
| `si (a) entonces si (b) entonces x = 1; sino x = 2; fin fin` | El `sino` es del `si` interno | 1 |
| `si (a) entonces si (b) entonces x = 1; fin sino x = 2; fin` | El `sino` es del `si` externo | 1 |
| `si (a) entonces si (b) entonces x = 1; sino x = 2; fin` | Falta un `fin` | 0 (rechazada) |

**Figura 10**

*Árbol del sino del si interno, con fin*

![Sino del si interno](arboles/img/gic2_arboles_sentencias-SinoColgante-a.png)

*Nota.* Fuente editable: `arboles/gic2_arboles_sentencias.drawio`, página SinoColgante (árbol izquierdo).

**Figura 11**

*Árbol del sino del si externo, con fin*

![Sino del si externo](arboles/img/gic2_arboles_sentencias-SinoColgante-b.png)

*Nota.* En cada caso el `sino` queda bajo un único `<condicional>`: el que cierra su propio `fin`. Fuente editable: `arboles/gic2_arboles_sentencias.drawio`, página SinoColgante (árbol derecho).

**Lema 2 (emparejamiento).** En toda cadena derivada desde `<sentencias>`, si cada SI y cada MIENTRAS se lee como un paréntesis que abre y cada FIN como uno que cierra, los tokens quedan balanceados, y cada SI o MIENTRAS tiene un único FIN correspondiente.

*Prueba.* C1, C2 y L1 producen exactamente un SI o MIENTRAS al comienzo y un FIN al final, y entre ellos solo hay `<sentencias>`, balanceadas por inducción. Las demás sentencias no contienen SI, MIENTRAS ni FIN. Una secuencia balanceada tiene un emparejamiento único, como una secuencia de paréntesis. ∎

Con el Lema 2, cada decisión queda determinada por la cadena: un condicional o ciclo termina en el FIN que corresponde a su SI o MIENTRAS; se usa C2 si y solo si hay un SINO al nivel del bloque (no dentro de otro par SI…FIN), y hay a lo sumo uno; y la declaración, la asignación y la salida terminan en su primer PUNTO_COMA, porque las expresiones no contienen PUNTO_COMA. Por lo tanto, cada programa de Cafetal tiene a lo sumo un árbol de derivación.

C1 y C2 todavía comparten el prefijo `SI PAR_ABRE <expresion> PAR_CIERRA ENTONCES <sentencias>`. Eso no es ambigüedad, sino un problema de **determinismo**: un analizador descendente no puede elegir entre C1 y C2 mirando solo el primer token. Se resuelve con la factorización de la sección 5.

### 3.6 Resumen

**Tabla 11**

*Fuentes de ambigüedad y su solución en Cafetal*

| Fuente de ambigüedad | Ejemplo | Árboles en la gramática ingenua | Solución | Árboles en Cafetal |
|---|---|---|---|---|
| Precedencia | `kilos + 25 * 2` | 2 | Un no terminal por nivel (`<suma>`, `<termino>`) | 1 |
| Asociatividad | `10 - 4 - 2` | 2 | Recursión solo por la izquierda (E16) | 1 |
| Operadores lógicos | `a o b y c` | 2 | Niveles `<expresion>`, `<conjuncion>`, `<negacion>` | 1 |
| Relacionales encadenados | `a < b < c` | 2 | `<comparacion>` no asociativa (E7) | 0 (rechazada) |
| Sino colgante | `si (a) entonces si (b) entonces x = 1; sino x = 2;` | 2 | Delimitador de cierre `fin` (C1, C2, L1) | 1 por cada texto con `fin` |

## 4. Eliminación de la recursividad por la izquierda

Un no terminal A es **recursivo por la izquierda** si existe una derivación A ⇒⁺ A γ, es decir, si A puede volver a aparecer como primer símbolo de lo que él mismo genera. Es **directa** si hay una regla `A ::= A α` e **indirecta** si A llega a sí mismo pasando por otros no terminales (Aho et al., 2006).

La gramática inicial tiene recursividad directa a propósito: fija la asociatividad por la izquierda de `o`, `y`, `+ -` y `* /`. Pero la Fase 3 usa un **analizador descendente recursivo**, con una función por no terminal, que no puede trabajar con ella por dos razones:

1. **No termina.** La función de `<suma>`, al aplicar E15, tendría que llamarse a sí misma antes de consumir ningún token, indefinidamente. Se comprobó con un analizador descendente ingenuo: sobre la gramática inicial entra en recursión infinita incluso con la entrada `ID`.
2. **No puede elegir regla mirando el siguiente token.** E15, E16 y E17 empiezan generando un `<termino>`, así que las tres empiezan con los mismos tokens. Para derivar `10 - 4 - 2`, el analizador tendría que decidir desde el primer token que debe aplicar E16 **dos veces**, y eso depende de cuántos RESTA hay más adelante.

### 4.1 Detección

**Recursividad directa.** De las 40 reglas, siete tienen la forma `A ::= A α`, en cinco no terminales: P2 (`<sentencias>`), E1 (`<expresion>`), E3 (`<conjuncion>`), E15 y E16 (`<suma>`), y E18 y E19 (`<termino>`). Hay otras reglas recursivas, pero no por la izquierda: E5 (`NO <negacion>`) es recursiva por la derecha, E21 tiene `<expresion>` después de PAR_ABRE, y C1, C2 y L1 tienen `<sentencias>` después de terminales.

**Recursividad indirecta.** Hay que ver qué no terminales pueden quedar de primeros en el lado derecho de cada regla, teniendo en cuenta los **anulables** (los que derivan ε): si una regla empieza con un anulable, el símbolo siguiente también puede quedar de primero. En la gramática inicial el único anulable es `<sentencias>` (P3).

**Tabla 12**

*No terminales que pueden quedar de primeros en la gramática inicial*

| No terminal | Pueden quedar de primeros |
|---|---|
| `<programa>`, `<declaracion>`, `<asignacion>`, `<salida>`, `<condicional>`, `<ciclo>`, `<factor>`, `<op_rel>` | Ninguno: todas sus reglas empiezan con un terminal |
| `<sentencias>` | `<sentencias>` (P2) y, como es anulable, `<sentencia>` (P2) |
| `<sentencia>` | `<declaracion>`, `<asignacion>`, `<salida>`, `<condicional>`, `<ciclo>` |
| `<argumento>` | `<expresion>` (M2) |
| `<expresion>` | `<expresion>` (E1), `<conjuncion>` (E2) |
| `<conjuncion>` | `<conjuncion>` (E3), `<negacion>` (E4) |
| `<negacion>` | `<comparacion>` (E6) |
| `<comparacion>` | `<suma>` (E7, E8) |
| `<suma>` | `<suma>` (E15, E16), `<termino>` (E17) |
| `<termino>` | `<termino>` (E18, E19), `<factor>` (E20) |

Si se quitan las flechas de cada no terminal hacia sí mismo, quedan dos cadenas que **nunca vuelven atrás**:

```
<sentencias> → <sentencia> → <declaracion> | <asignacion> | <salida> | <condicional> | <ciclo>
<argumento> → <expresion> → <conjuncion> → <negacion> → <comparacion> → <suma> → <termino> → <factor>
```

El único camino de `<factor>` a `<expresion>` es E21, y ahí `<expresion>` va después de PAR_ABRE. Por lo tanto **no hay recursividad indirecta**.

### 4.2 Método

```
A ::= A α | β      ⇒      A  ::= β A'
                          A' ::= α A' | ε
```

donde A' es un no terminal nuevo. En la gramática se escribe agregando `_prima` al nombre (el A' de `<suma>` es `<suma_prima>`): así se conserva la convención de minúsculas y guion bajo, y el nombre sirve directamente como nombre de la función de Python del analizador. El método exige que ningún α sea ε, que ningún β empiece con A y que no haya recursividad indirecta; las siete reglas lo cumplen.

**La transformación conserva el lenguaje.** Antes, cada vez que se aplica `A ::= A α` aparece un α más a la derecha, y la derivación termina con `A ::= β`:

```
A ⇒ A α ⇒ A α α ⇒ … ⇒ A α α … α ⇒ β α α … α      (k veces α, k ≥ 0)
```

Las formas son **(β)(α)\***. Después, A' genera cero o más α y termina con ε, es decir (α)\*; como `A ::= β A'` es la única regla de A, A genera **(β)(α)\***. Los dos conjuntos son iguales. ∎

Lo que cambia es el orden: la regla original agrega los α de derecha a izquierda, y la nueva de izquierda a derecha, en el mismo orden en que el analizador lee los tokens.

**Varias alternativas recursivas.** En `A ::= A α₁ | A α₂ | β`, como la concatenación se distribuye sobre la unión, `A α₁ , A α₂` es `A (α₁,α₂)`: es la forma básica con α = (α₁,α₂). Al aplicarla y volver a distribuir queda `A' ::= α₁ A' | α₂ A' | ε`, y A genera (β)(α₁,α₂)\* antes y después.

**Caso β = ε.** En `<sentencias>`, la alternativa no recursiva es ε. La fórmula da `A ::= ε A'`, que es `A ::= A'` porque ε es el neutro de la concatenación. Como es la única regla de A, A y A' generan lo mismo, (α)\*, y se renombra A' como A: `A ::= α A | ε`. Así el nombre `<sentencias>` se conserva y P1, C1, C2 y L1 no cambian.

### 4.3 Aplicación

**Tabla 13**

*Eliminación de la recursividad por la izquierda, regla por regla*

| No terminal | Reglas originales | α | β | Reglas nuevas | Lenguaje (igual antes y después) |
|---|---|---|---|---|---|
| `<sentencias>` | P2, P3 | `<sentencia>` | ε | R1, R2 | (`<sentencia>`)\* |
| `<expresion>` | E1, E2 | O `<conjuncion>` | `<conjuncion>` | R3, R4, R5 | (`<conjuncion>`)(O `<conjuncion>`)\* |
| `<conjuncion>` | E3, E4 | Y `<negacion>` | `<negacion>` | R6, R7, R8 | (`<negacion>`)(Y `<negacion>`)\* |
| `<suma>` | E15, E16, E17 | (SUMA `<termino>`, RESTA `<termino>`) | `<termino>` | R9 a R12 | (`<termino>`)(SUMA `<termino>`, RESTA `<termino>`)\* |
| `<termino>` | E18, E19, E20 | (MULT `<factor>`, DIV `<factor>`) | `<factor>` | R13 a R16 | (`<factor>`)(MULT `<factor>`, DIV `<factor>`)\* |

Por ejemplo, para `<suma>` la sustitución en la fórmula es:

```
A  ::= β A'     ⇒   <suma>       ::= <termino> <suma_prima>
A' ::= α A'     ⇒   <suma_prima> ::= (SUMA <termino>, RESTA <termino>) <suma_prima>
                ⇒   <suma_prima> ::= SUMA <termino> <suma_prima>        (distribución)
                    <suma_prima> ::= RESTA <termino> <suma_prima>
A' ::= ε        ⇒   <suma_prima> ::= ε
```

Las 16 reglas resultantes son:

```
R1   <sentencias>       ::= <sentencia> <sentencias>
R2   <sentencias>       ::= ε
R3   <expresion>        ::= <conjuncion> <expresion_prima>
R4   <expresion_prima>  ::= O <conjuncion> <expresion_prima>
R5   <expresion_prima>  ::= ε
R6   <conjuncion>       ::= <negacion> <conjuncion_prima>
R7   <conjuncion_prima> ::= Y <negacion> <conjuncion_prima>
R8   <conjuncion_prima> ::= ε
R9   <suma>             ::= <termino> <suma_prima>
R10  <suma_prima>       ::= SUMA <termino> <suma_prima>
R11  <suma_prima>       ::= RESTA <termino> <suma_prima>
R12  <suma_prima>       ::= ε
R13  <termino>          ::= <factor> <termino_prima>
R14  <termino_prima>    ::= MULT <factor> <termino_prima>
R15  <termino_prima>    ::= DIV <factor> <termino_prima>
R16  <termino_prima>    ::= ε
```

Se eliminan 12 reglas (P2, P3, E1–E4, E15–E20) y se agregan estas 16: la gramática pasa de 40 a 44 reglas y de 17 a 21 no terminales.

**Comprobación.** En la gramática nueva hay cinco anulables (`<sentencias>` y los cuatro `_prima`), pero ninguno está al comienzo de una regla seguido de otro no terminal: R1, R3, R6, R9 y R13 empiezan con un no terminal no anulable. Las dos cadenas de la sección 4.1 quedan igual, sin las flechas de cada no terminal hacia sí mismo: **no queda recursividad por la izquierda, ni directa ni indirecta.**

### 4.4 Efecto sobre la derivación y el árbol

Con la gramática inicial, la derivación más a la izquierda de `10 - 4 - 2` desde `<suma>` empieza con E16 y otra vez E16, **antes de ver ningún token**. Con la gramática nueva, cada regla se elige cuando llega el token que la justifica: R11 cuando el siguiente token es RESTA, y R16 o R12 cuando ya no viene un operador de su nivel. Esa es la propiedad que necesita el analizador descendente.

**Figura 12**

*Árbol de 10 - 4 - 2 desde <suma>, antes y después de eliminar la recursividad*

![Árbol de 10 - 4 - 2 antes y después](arboles/img/gic4_recursividad.drawio.png)

*Nota.* Fuente editable: `arboles/gic4_recursividad.drawio`, página Comparacion.

- **La precedencia no cambia.** Cada operador sigue apareciendo solo en las reglas de su nivel (O en R4, Y en R7, SUMA y RESTA en R10 y R11, MULT y DIV en R14 y R15), y el único regreso al nivel superior sigue siendo E21.
- **La asociatividad ya no se ve en la forma del árbol.** El árbol nuevo se inclina hacia la derecha, y los operandos y operadores quedan en la cadena de `<suma_prima>` en el orden del texto. La agrupación por la izquierda se recupera recorriendo esa cadena de izquierda a derecha. La transformación no cambia qué cadenas son válidas.

La transformación se verificó con un analizador general (Earley) sobre todas las cadenas cortas y sobre miles de programas generados al azar: las dos gramáticas aceptan exactamente las mismas cadenas (Apéndice B.1).

## 5. Factorización por la izquierda

Después de eliminar la recursividad, la gramática todavía no basta para un analizador **predictivo**, que debe elegir una regla de A mirando solo el siguiente token y sin retroceder. Eso falla cuando dos reglas de A empiezan igual: mientras se lee el prefijo común, las dos reglas siguen siendo posibles. La **factorización por la izquierda** saca el prefijo común α a una sola regla y deja la decisión para el momento en que aparece la diferencia (Aho et al., 2006):

```
A ::= α β₁ | α β₂      ⇒      A  ::= α A'
                              A' ::= β₁ | β₂
```

donde α ≠ ε es el **prefijo común más largo** de las dos alternativas, y β₁ o β₂ pueden ser ε. Si se sacara un prefijo más corto, las reglas de A' seguirían empezando igual y habría que factorizar otra vez.

**La transformación conserva el lenguaje.** Antes, A genera α β₁ , α β₂. Después, A genera (α)(β₁,β₂). Como la concatenación se distribuye sobre la unión, (α)(β₁,β₂) = α β₁ , α β₂. ∎

La factorización **no quita ambigüedad**: la sección 3 ya demostró que la gramática no es ambigua. Lo que resuelve es un problema de **determinismo**.

### 5.1 Detección

Hay que factorizar un no terminal cuando dos de sus alternativas pueden empezar con el mismo token, ya sea porque empiezan con el mismo símbolo (prefijo explícito) o porque símbolos distintos pueden generar el mismo primer token (prefijo oculto). Se revisaron los 12 no terminales con más de una alternativa:

**Tabla 14**

*Búsqueda de prefijos comunes en la gramática sin recursividad*

| No terminal | Tokens con que puede empezar cada alternativa | ¿Prefijo común? |
|---|---|---|
| `<sentencias>` | R1: DATO, ID, MOSTRAR, SI, MIENTRAS · R2: ε | No |
| `<sentencia>` | P4: DATO · P5: ID · P6: MOSTRAR · P7: SI · P8: MIENTRAS | No |
| `<expresion_prima>` | R4: O · R5: ε | No |
| `<conjuncion_prima>` | R7: Y · R8: ε | No |
| `<negacion>` | E5: NO · E6: PAR_ABRE, ID, ENTERO, DECIMAL | No |
| **`<comparacion>`** | **E7 y E8: PAR_ABRE, ID, ENTERO, DECIMAL** | **Sí: `<suma>`** |
| `<op_rel>` | Un relacional distinto en cada regla | No |
| `<suma_prima>` | R10: SUMA · R11: RESTA · R12: ε | No |
| `<termino_prima>` | R14: MULT · R15: DIV · R16: ε | No |
| `<factor>` | PAR_ABRE · ID · ENTERO · DECIMAL | No |
| `<argumento>` | M2: NO, PAR_ABRE, ID, ENTERO, DECIMAL · M3: CADENA | No |
| **`<condicional>`** | **C1 y C2: SI** | **Sí: `SI PAR_ABRE <expresion> PAR_CIERRA ENTONCES <sentencias>`** |

Hay exactamente **dos** reglas con prefijo común. Las alternativas ε no tienen prefijo, así que no entran en un conflicto de factorización: cuándo se aplican se decide con SIGUIENTE (sección 6). El ejemplo típico de factorización, una sentencia que empieza con ID y puede ser asignación o llamada a procedimiento, no se presenta en Cafetal: no hay procedimientos y `mostrar` es una palabra reservada.

### 5.2 Condicional (C1 y C2)

Comparando las dos alternativas símbolo por símbolo, coinciden en las posiciones 1 a 6 (SI, PAR_ABRE, `<expresion>`, PAR_CIERRA, ENTONCES, `<sentencias>`) y difieren en la 7 (FIN frente a SINO). Por lo tanto:

**Tabla 15**

*Factorización del condicional*

| Símbolo de la fórmula | Valor |
|---|---|
| A | `<condicional>` |
| α | SI PAR_ABRE `<expresion>` PAR_CIERRA ENTONCES `<sentencias>` |
| β₁ | FIN |
| β₂ | SINO `<sentencias>` FIN |
| A' | `<condicional_prima>` |

```
F4   <condicional>       ::= SI PAR_ABRE <expresion> PAR_CIERRA ENTONCES <sentencias> <condicional_prima>
F5   <condicional_prima> ::= FIN
F6   <condicional_prima> ::= SINO <sentencias> FIN
```

Antes había que elegir entre C1 y C2 al leer SI, sin saber si más adelante vendría un `sino`. Ahora F4 se aplica siempre al leer SI, y la elección entre F5 y F6 se hace al terminar el bloque, mirando un solo token: FIN o SINO. El sino colgante sigue resuelto: cada condicional sigue cerrando con su propio FIN, ahora dentro de F5 o F6, así que el Lema 2 se mantiene.

**Figura 13**

*Árbol de si (a) entonces x = 1; sino x = 2; fin antes de factorizar (C2)*

![Condicional antes de factorizar](arboles/img/gic5_factorizacion-Condicional-a.png)

*Nota.* Los seis primeros hijos son el prefijo común α. Fuente editable: `arboles/gic5_factorizacion.drawio`, página Condicional (árbol izquierdo).

**Figura 14**

*El mismo condicional después de factorizar (F4 y F6)*

![Condicional después de factorizar](arboles/img/gic5_factorizacion-Condicional-b.png)

*Nota.* SINO y FIN quedan bajo `<condicional_prima>`: se decide al llegar a ese token. Fuente editable: `arboles/gic5_factorizacion.drawio`, página Condicional (árbol derecho).

### 5.3 Comparación (E7 y E8)

E7 es `<suma> <op_rel> <suma>` y E8 es `<suma>`: el prefijo común más largo es `<suma>`, y después de él E8 ya no tiene nada, así que β₂ = ε.

```
F1   <comparacion>       ::= <suma> <comparacion_prima>
F2   <comparacion_prima> ::= <op_rel> <suma>
F3   <comparacion_prima> ::= ε
```

El lenguaje antes es `<suma>` `<op_rel>` `<suma>` , `<suma>`, y después (`<suma>`)(`<op_rel>` `<suma>` , ε): son iguales por la distribución y porque ε es el neutro de la concatenación. Ahora F1 se aplica siempre, y después de leer la primera `<suma>` el siguiente token decide: si es un relacional se aplica F2, si no, F3. Los relacionales siguen siendo no asociativos: `<comparacion_prima>` no es recursiva, así que `a < b < c` sigue sin ser derivable.

**Figura 15**

*Árboles desde <comparacion>, antes y después de factorizar*

![Comparación antes y después de factorizar](arboles/img/gic5_factorizacion-Comparacion.drawio.png)

*Nota.* Después de factorizar, el `<op_rel>` o su ausencia (ε) se decide cuando ya se leyó la primera `<suma>`. Fuente editable: `arboles/gic5_factorizacion.drawio`, página Comparacion.

### 5.4 Resultado

Se eliminan 4 reglas (E7, E8, C1, C2) y se agregan 6 (F1–F6): la gramática pasa de 44 a 46 reglas y de 21 a 23 no terminales. Ningún no terminal tiene ya dos alternativas que empiecen con el mismo token, y no se introdujo recursividad por la izquierda: F1 empieza con `<suma>`, F2 con `<op_rel>` y F4 con SI. La gramática factorizada es la **gramática final** (sección 7). La verificación de la transformación está en el Apéndice B.2.

## 6. Conjuntos PRIMERO y SIGUIENTE y tabla LL(1)

Falta comprobar que la gramática factorizada es **LL(1)**: que un analizador que lee la entrada de izquierda a derecha (la primera L), construye una derivación más a la izquierda (la segunda L) y mira **un solo token** por adelantado (el 1) puede elegir siempre la regla correcta sin retroceder (Aho et al., 2006). Para eso se calculan dos conjuntos por cada no terminal:

- **PRIMERO(α):** los tokens con que puede empezar una cadena derivada desde α. Si α puede derivar la cadena vacía, también contiene ε, que no es un token: indica que α es anulable.
- **SIGUIENTE(A):** los tokens que pueden aparecer inmediatamente después de A en alguna forma sentencial derivada desde `<programa>`. Incluye `EOF` si A puede quedar al final del programa.

Con ellos se construye la **tabla de análisis predictivo** M[A, t]: la regla que el analizador aplica cuando A está en la cima de la pila y el siguiente token es t. Si ninguna celda tiene dos reglas, la gramática es LL(1), y toda gramática LL(1) es **no ambigua** (sección 6.7). Los conjuntos se escriben por extensión con { }, como en la Fase 1; Cafetal no usa llaves, así que no chocan con ningún símbolo del lenguaje. Los cálculos se hacen sobre la gramática final de la sección 7.

### 6.1 No terminales anulables

Un no terminal es **anulable** si deriva ε. Se necesita saberlo antes de calcular PRIMERO, porque si el primer símbolo de una regla es anulable, el segundo también puede aportar el primer token.

Son anulables exactamente los seis no terminales que tienen una regla ε:

**Tabla 16**

*No terminales anulables*

| No terminal | Regla ε |
|---|---|
| `<sentencias>` | R2 |
| `<expresion_prima>` | R5 |
| `<conjuncion_prima>` | R8 |
| `<comparacion_prima>` | F3 |
| `<suma_prima>` | R12 |
| `<termino_prima>` | R16 |

Ningún otro no terminal es anulable: todas las demás reglas contienen al menos un terminal o empiezan con un no terminal que termina generando un `<factor>`, y `<factor>` siempre produce un token.

### 6.2 Conjuntos PRIMERO

#### 6.2.1 Reglas de cálculo

1. Si t es un terminal, PRIMERO(t) = {t}.
2. Si A ::= ε es una regla, ε ∈ PRIMERO(A).
3. Para una cadena X₁ X₂ … Xₙ:
   - se agrega PRIMERO(X₁) sin ε;
   - si X₁ es anulable, se agrega también PRIMERO(X₂) sin ε, y así sucesivamente mientras los símbolos anteriores sean anulables;
   - si **todos** los Xᵢ son anulables, se agrega ε.
4. PRIMERO(A) es la unión de PRIMERO del lado derecho de todas las reglas de A.

#### 6.2.2 Cálculo

Se calcula de abajo hacia arriba, empezando por los no terminales cuyas reglas empiezan con un terminal. Así, cuando se necesita PRIMERO de un no terminal, ya está calculado.

**Tabla 17**

*Cálculo de los conjuntos PRIMERO*

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

### 6.3 Conjuntos SIGUIENTE

#### 6.3.1 Reglas de cálculo

1. `EOF` ∈ SIGUIENTE(`<programa>`), porque el programa termina con el fin de la entrada.
2. Para cada regla A ::= α B β, donde B es un no terminal:
   - todo PRIMERO(β), sin ε, se agrega a SIGUIENTE(B): lo que empieza β viene justo después de B;
   - si β es ε o es anulable, todo SIGUIENTE(A) se agrega a SIGUIENTE(B): cuando β desaparece, lo que sigue a A sigue también a B.
3. Se repiten las reglas hasta que ningún conjunto cambie.

#### 6.3.2 Aportes de cada aparición de un no terminal

Cada fila es una aparición de un no terminal B en el lado derecho de una regla. La columna β es lo que va después de B en esa regla.

**Tabla 18**

*Aportes de cada aparición de un no terminal al conjunto SIGUIENTE*

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

#### 6.3.3 Resolución

Las inclusiones de la última columna siempre van de un no terminal "de arriba" hacia uno "de abajo" en la gramática, y las únicas que van de un conjunto a sí mismo no aportan nada. Por eso basta con resolverlas en orden, de `<programa>` hacia `<factor>`, y una segunda pasada completa no agrega ningún token: se llega al punto fijo de la regla 3 de la sección 6.3.1.

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

#### 6.3.4 Resultado

**Tabla 19**

*Conjuntos PRIMERO y SIGUIENTE de los 23 no terminales*

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

Los conjuntos SIGUIENTE de las expresiones crecen hacia abajo en la jerarquía. Es la estratificación de la sección 3.3 vista desde otro ángulo: después de un `<factor>` puede venir cualquier operador de un nivel igual o inferior, mientras que después de una `<expresion>` completa solo puede venir el cierre de la sentencia o del paréntesis.

### 6.4 Conjunto de predicción de cada regla

El **conjunto de predicción** de una regla A ::= α son los tokens con los que el analizador debe elegirla:

- PRED(A ::= α) = PRIMERO(α) sin ε, si α no es anulable;
- PRED(A ::= α) = (PRIMERO(α) sin ε) ∪ SIGUIENTE(A), si α es anulable. En Cafetal, esto solo pasa con las reglas ε.

**Tabla 20**

*Conjunto de predicción de cada regla*

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

### 6.5 Tabla de análisis predictivo LL(1)

Para cada regla A ::= α y cada token t ∈ PRED(A ::= α), se escribe la etiqueta de la regla en la celda M[A, t]. Una celda vacía significa **error sintáctico**: con A en la cima de la pila, el token t no puede aparecer.

El resultado tiene **106 celdas llenas** de las 23 × 31 = 713 posibles, y **ninguna celda tiene dos reglas**.

Las columnas ENTONCES, HACER, ASIGNACION y EOF no tienen ninguna celda llena. Esos tokens nunca deciden una regla: solo aparecen en medio o al final de un lado derecho, donde el analizador ya sabe qué regla está aplicando y solo los empareja. `EOF` se empareja al final, cuando la pila queda vacía (sección 6.8).

Para que quepa en la página, la tabla se presenta en cinco partes de hasta seis columnas, con las filas que tienen al menos una celda llena en esas columnas; las cinco suman las 106 celdas. La tabla completa está en `src/parser/tabla_ll1.csv`, que es la que usa el analizador de la Fase 3.

**Tabla 21**

*Tabla de análisis predictivo LL(1), parte 1: programa y sentencias*

| No terminal | INICIO | FIN | SINO | DATO | ID | SI |
|---|---|---|---|---|---|---|
| `<programa>` | P1 |  |  |  |  |  |
| `<sentencias>` |  | R2 | R2 | R1 | R1 | R1 |
| `<sentencia>` |  |  |  | P4 | P5 | P7 |
| `<declaracion>` |  |  |  | D1 |  |  |
| `<expresion>` |  |  |  |  | R3 |  |
| `<conjuncion>` |  |  |  |  | R6 |  |
| `<negacion>` |  |  |  |  | E6 |  |
| `<comparacion>` |  |  |  |  | F1 |  |
| `<suma>` |  |  |  |  | R9 |  |
| `<termino>` |  |  |  |  | R13 |  |
| `<factor>` |  |  |  |  | E22 |  |
| `<asignacion>` |  |  |  |  | A1 |  |
| `<argumento>` |  |  |  |  | M2 |  |
| `<condicional>` |  |  |  |  |  | F4 |
| `<condicional_prima>` |  | F5 | F6 |  |  |  |

**Tabla 22**

*Tabla de análisis predictivo LL(1), parte 2: sentencias, cadena y operadores lógicos*

| No terminal | MIENTRAS | MOSTRAR | CADENA | NO | Y | O |
|---|---|---|---|---|---|---|
| `<sentencias>` | R1 | R1 |  |  |  |  |
| `<sentencia>` | P8 | P6 |  |  |  |  |
| `<expresion>` |  |  |  | R3 |  |  |
| `<expresion_prima>` |  |  |  |  |  | R4 |
| `<conjuncion>` |  |  |  | R6 |  |  |
| `<conjuncion_prima>` |  |  |  |  | R7 | R8 |
| `<negacion>` |  |  |  | E5 |  |  |
| `<comparacion_prima>` |  |  |  |  | F3 | F3 |
| `<suma_prima>` |  |  |  |  | R12 | R12 |
| `<termino_prima>` |  |  |  |  | R16 | R16 |
| `<salida>` |  | M1 |  |  |  |  |
| `<argumento>` |  |  | M3 | M2 |  |  |
| `<ciclo>` | L1 |  |  |  |  |  |

**Tabla 23**

*Tabla de análisis predictivo LL(1), parte 3: delimitadores y literales*

| No terminal | PAR_ABRE | PAR_CIERRA | PUNTO_COMA | ENTERO | DECIMAL |
|---|---|---|---|---|---|
| `<expresion>` | R3 |  |  | R3 | R3 |
| `<expresion_prima>` |  | R5 | R5 |  |  |
| `<conjuncion>` | R6 |  |  | R6 | R6 |
| `<conjuncion_prima>` |  | R8 | R8 |  |  |
| `<negacion>` | E6 |  |  | E6 | E6 |
| `<comparacion>` | F1 |  |  | F1 | F1 |
| `<comparacion_prima>` |  | F3 | F3 |  |  |
| `<suma>` | R9 |  |  | R9 | R9 |
| `<suma_prima>` |  | R12 | R12 |  |  |
| `<termino>` | R13 |  |  | R13 | R13 |
| `<termino_prima>` |  | R16 | R16 |  |  |
| `<factor>` | E21 |  |  | E23 | E24 |
| `<argumento>` | M2 |  |  | M2 | M2 |

**Tabla 24**

*Tabla de análisis predictivo LL(1), parte 4: operadores aritméticos y MENOR*

| No terminal | SUMA | RESTA | MULT | DIV | MENOR |
|---|---|---|---|---|---|
| `<comparacion_prima>` |  |  |  |  | F2 |
| `<op_rel>` |  |  |  |  | E9 |
| `<suma_prima>` | R10 | R11 |  |  | R12 |
| `<termino_prima>` | R16 | R16 | R14 | R15 | R16 |

**Tabla 25**

*Tabla de análisis predictivo LL(1), parte 5: demás relacionales*

| No terminal | MAYOR | MENOR_IGUAL | MAYOR_IGUAL | IGUAL | DIFERENTE |
|---|---|---|---|---|---|
| `<comparacion_prima>` | F2 | F2 | F2 | F2 | F2 |
| `<op_rel>` | E10 | E11 | E12 | E13 | E14 |
| `<suma_prima>` | R12 | R12 | R12 | R12 | R12 |
| `<termino_prima>` | R16 | R16 | R16 | R16 | R16 |

### 6.6 Condición LL(1)

Una gramática es LL(1) si y solo si, para todo no terminal A con dos alternativas distintas A ::= α | β (Aho et al., 2006):

1. PRIMERO(α) y PRIMERO(β) no tienen tokens en común;
2. a lo sumo una de las dos deriva ε;
3. si β deriva ε, PRIMERO(α) no tiene tokens en común con SIGUIENTE(A).

Las tres condiciones juntas equivalen a que los conjuntos de predicción de las alternativas de A sean **disjuntos dos a dos**, es decir, a que ninguna celda M[A, t] tenga dos reglas. Se revisan los 12 no terminales con más de una alternativa (los otros 11 tienen una sola regla y no pueden tener conflicto):

**Tabla 26**

*Condición LL(1) en los no terminales con varias alternativas*

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

#### 6.6.1 Por qué no hay conflictos: cada decisión de diseño elimina uno

Los casos más delicados son las reglas ε, que se eligen con SIGUIENTE. Cada uno queda libre de conflicto gracias a una decisión de las tareas anteriores:

**Tabla 27**

*Decisiones de diseño que evitan los conflictos de las reglas ε*

| Regla ε | Conflicto que podría tener | Por qué no ocurre | Decisión que lo evita |
|---|---|---|---|
| R2 (`<sentencias>`) | Con R1, si una lista pudiera ir seguida de algo que también empieza una sentencia | SIGUIENTE(`<sentencias>`) = {FIN, SINO}, y ninguna sentencia empieza con FIN ni SINO | Todo bloque cierra con `fin` (sección 3.5) |
| R12 (`<suma_prima>`) | Con R10 y R11, si SUMA o RESTA pudieran seguir a una `<suma>` completa | SUMA y RESTA solo aparecen dentro de `<suma_prima>`; una `<suma>` completa solo va seguida de relacionales, Y, O o cierres | Estratificación por niveles (sección 3.3) |
| R16 (`<termino_prima>`) | Con R14 y R15, si MULT o DIV pudieran seguir a un `<termino>` completo | Igual que el anterior, un nivel más abajo | Estratificación por niveles (sección 3.3) |
| F3 (`<comparacion_prima>`) | Con F2, si un relacional pudiera seguir a una comparación completa | SIGUIENTE(`<comparacion_prima>`) = {Y, O, PAR_CIERRA, PUNTO_COMA}: no contiene relacionales | Relacionales no asociativos (secciones 2.2 y 3.3) |
| R5 y R8 | Con R4 y R7 | O e Y no están en los SIGUIENTE de su propio nivel | Estratificación por niveles (sección 3.3) |

La fila de F3 explica cómo se rechaza `a < b < c`: después de `a < b`, `<comparacion_prima>` ya se usó, y el segundo MENOR llega cuando en la cima está `<conjuncion_prima>`. La celda M[`<conjuncion_prima>`, MENOR] está vacía, así que el analizador reporta el error justo en el segundo relacional.

### 6.7 Por qué la tabla LL(1) demuestra que la gramática no es ambigua

**Proposición.** Si la tabla LL(1) de una gramática G no tiene celdas con dos reglas, ninguna cadena tiene dos árboles de derivación en G.

*Prueba.* Dos árboles distintos de la misma cadena w corresponden a dos derivaciones más a la izquierda distintas (Hopcroft et al., 2007). Se supone que existen y se busca una contradicción.

Las dos derivaciones parten de `<programa>`, y mientras apliquen las mismas reglas producen las mismas formas sentenciales. Sea x A γ la primera forma sentencial en que difieren, donde x es la parte ya formada solo por tokens, A es el no terminal más a la izquierda y γ el resto. Una derivación aplica A ::= α₁ y la otra A ::= α₂, con α₁ ≠ α₂. Como las dos llegan a w, la cadena w empieza con x. Sea t el token de w que viene justo después de x, o `EOF` si x ya es toda la cadena.

En la derivación que usa A ::= α₁, la forma x α₁ γ termina generando w, así que α₁ γ genera lo que sigue a x, que empieza con t. Hay dos casos:

- si α₁ genera al menos un token, t es el primero de ellos y t ∈ PRIMERO(α₁);
- si α₁ genera ε, t es el primer token que genera γ, o es `EOF`. Como x A γ se deriva desde `<programa>`, ese token aparece justo después de A en una forma sentencial, así que t ∈ SIGUIENTE(A).

En los dos casos t ∈ PRED(A ::= α₁), es decir, M[A, t] contiene α₁. Con el mismo argumento, M[A, t] contiene α₂. La celda M[A, t] tendría entonces dos reglas, lo que contradice la hipótesis. ∎

Como la tabla de la sección 6.5 no tiene celdas con dos reglas, **la gramática final de Cafetal no es ambigua**. Esto confirma, para la gramática que usará el analizador, las demostraciones de la sección 3, hechas sobre la gramática estratificada.

La prueba muestra algo más: el árbol se puede construir **eligiendo cada regla con un solo token**, y eso es exactamente lo que hace el analizador de la Fase 3.

### 6.8 Funcionamiento del analizador predictivo

El analizador predictivo guarda en una **pila** los símbolos que faltan por derivar. Empieza con `<programa>` sobre `EOF` y repite:

- si la cima es un terminal igual al token actual, los **empareja**: saca la cima y avanza al siguiente token;
- si la cima es un no terminal A, consulta M[A, t] con el token actual t: si la celda tiene una regla, saca A y apila su lado derecho, con el primer símbolo en la cima; si está vacía, reporta un **error sintáctico**;
- si la cima es `EOF` y el token actual también, **acepta**.

#### 6.8.1 Traza de una entrada válida

Entrada: `inicio x = a - 1; fin`. Tokens: INICIO ID ASIGNACION ID RESTA ENTERO PUNTO_COMA FIN EOF. En la columna Pila, la cima está a la izquierda.

**Tabla 28**

*Traza del analizador predictivo para inicio x = a - 1; fin*

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

#### 6.8.2 Traza de una entrada con error

Entrada: `inicio x = a - ; fin`. Los pasos 1 a 18 son iguales a los de 11.1. En el paso 19 el token actual es PUNTO_COMA, donde debía venir el operando de la resta:

**Tabla 29**

*Traza del analizador predictivo para inicio x = a - ; fin*

| Paso | Pila | Entrada | Acción |
|---|---|---|---|
| 19 | `<termino>` `<suma_prima>` `<comparacion_prima>` … | PUNTO_COMA FIN EOF | Error: M[`<termino>`, PUNTO_COMA] está vacía |

La celda vacía indica qué se esperaba: los tokens con celda llena en la fila de `<termino>`, que son PRIMERO(`<termino>`) = {PAR_ABRE, ID, ENTERO, DECIMAL}. El analizador de la Fase 3 arma su mensaje de error con esa fila y con la línea y columna del token.
## 7. Gramática final

Esta es la gramática que implementa el analizador sintáctico descendente recursivo de la Fase 3: una función de Python por cada no terminal, que elige su regla con la tabla LL(1) de la sección 6.5.

```
P1   <programa>          ::= INICIO <sentencias> FIN
R1   <sentencias>        ::= <sentencia> <sentencias>
R2   <sentencias>        ::= ε
P4   <sentencia>         ::= <declaracion>
P5   <sentencia>         ::= <asignacion>
P6   <sentencia>         ::= <salida>
P7   <sentencia>         ::= <condicional>
P8   <sentencia>         ::= <ciclo>
D1   <declaracion>       ::= DATO ID ASIGNACION <expresion> PUNTO_COMA
R3   <expresion>         ::= <conjuncion> <expresion_prima>
R4   <expresion_prima>   ::= O <conjuncion> <expresion_prima>
R5   <expresion_prima>   ::= ε
R6   <conjuncion>        ::= <negacion> <conjuncion_prima>
R7   <conjuncion_prima>  ::= Y <negacion> <conjuncion_prima>
R8   <conjuncion_prima>  ::= ε
E5   <negacion>          ::= NO <negacion>
E6   <negacion>          ::= <comparacion>
F1   <comparacion>       ::= <suma> <comparacion_prima>
F2   <comparacion_prima> ::= <op_rel> <suma>
F3   <comparacion_prima> ::= ε
E9   <op_rel>            ::= MENOR
E10  <op_rel>            ::= MAYOR
E11  <op_rel>            ::= MENOR_IGUAL
E12  <op_rel>            ::= MAYOR_IGUAL
E13  <op_rel>            ::= IGUAL
E14  <op_rel>            ::= DIFERENTE
R9   <suma>              ::= <termino> <suma_prima>
R10  <suma_prima>        ::= SUMA <termino> <suma_prima>
R11  <suma_prima>        ::= RESTA <termino> <suma_prima>
R12  <suma_prima>        ::= ε
R13  <termino>           ::= <factor> <termino_prima>
R14  <termino_prima>     ::= MULT <factor> <termino_prima>
R15  <termino_prima>     ::= DIV <factor> <termino_prima>
R16  <termino_prima>     ::= ε
E21  <factor>            ::= PAR_ABRE <expresion> PAR_CIERRA
E22  <factor>            ::= ID
E23  <factor>            ::= ENTERO
E24  <factor>            ::= DECIMAL
A1   <asignacion>        ::= ID ASIGNACION <expresion> PUNTO_COMA
M1   <salida>            ::= MOSTRAR PAR_ABRE <argumento> PAR_CIERRA PUNTO_COMA
M2   <argumento>         ::= <expresion>
M3   <argumento>         ::= CADENA
F4   <condicional>       ::= SI PAR_ABRE <expresion> PAR_CIERRA ENTONCES <sentencias> <condicional_prima>
F5   <condicional_prima> ::= FIN
F6   <condicional_prima> ::= SINO <sentencias> FIN
L1   <ciclo>             ::= MIENTRAS PAR_ABRE <expresion> PAR_CIERRA HACER <sentencias> FIN
```

G = (N, T, P, S), donde:

- **N** = {`<programa>`, `<sentencias>`, `<sentencia>`, `<declaracion>`, `<expresion>`, `<expresion_prima>`, `<conjuncion>`, `<conjuncion_prima>`, `<negacion>`, `<comparacion>`, `<comparacion_prima>`, `<op_rel>`, `<suma>`, `<suma_prima>`, `<termino>`, `<termino_prima>`, `<factor>`, `<asignacion>`, `<salida>`, `<argumento>`, `<condicional>`, `<condicional_prima>`, `<ciclo>`}, |N| = 23.
- **T** = los 30 tokens del catálogo que llegan al analizador sintáctico, más `EOF`.
- **P** = las 46 reglas anteriores.
- **S** = `<programa>`.

La gramática final es no ambigua (secciones 3.4, 3.5 y 6.7), no tiene recursividad por la izquierda (sección 4.3), está factorizada (sección 5.4) y es LL(1) (sección 6.6).

### 7.1 Origen de cada regla

**Tabla 30**

*Correspondencia entre la gramática inicial y la gramática final*

| Reglas de la gramática inicial | Transformación | Reglas de la gramática final |
|---|---|---|
| P1, P4–P8, D1, A1, M1–M3, L1 | Ninguna | Las mismas |
| E5, E6, E9–E14, E21–E24 | Ninguna | Las mismas |
| P2, P3 | Eliminación de la recursividad (β = ε, simplificada) | R1, R2 |
| E1, E2 | Eliminación de la recursividad | R3, R4, R5 |
| E3, E4 | Eliminación de la recursividad | R6, R7, R8 |
| E15, E16, E17 | Eliminación de la recursividad (dos α) | R9, R10, R11, R12 |
| E18, E19, E20 | Eliminación de la recursividad (dos α) | R13, R14, R15, R16 |
| E7, E8 | Factorización (β₂ = ε) | F1, F2, F3 |
| C1, C2 | Factorización | F4, F5, F6 |

**Tabla 31**

*Evolución de la gramática*

| Etapa | Reglas | No terminales | Recursiva por la izquierda | Prefijos comunes | Conflictos LL(1) |
|---|---|---|---|---|---|
| Gramática ingenua de expresiones G0 (sección 3.1) | 13 | 2 | Sí | Sí | — (ambigua) |
| Gramática inicial (sección 2) | 40 | 17 | Sí (7 reglas) | Sí (2 no terminales) | Sí |
| Sin recursividad por la izquierda (sección 4) | 44 | 21 | No | Sí (2 no terminales) | Sí |
| Factorizada: gramática final (sección 5) | 46 | 23 | No | No | No (sección 6) |

## Conclusiones

La gramática inicial de Cafetal describe el lenguaje de la especificación con una sola jerarquía de expresiones, en la que los operadores lógicos y relacionales son los niveles de menor precedencia, y con bloques que siempre cierran con `fin`.

La ambigüedad se controló desde el diseño. La gramática ingenua de expresiones es ambigua en la precedencia, la asociatividad y los operadores lógicos, y además acepta comparaciones encadenadas que la especificación prohíbe. La estratificación por niveles asigna un único árbol a cada cadena, como se demostró con el Lema 1 y la proposición de la sección 3.4, y el delimitador `fin` elimina el sino colgante dentro de la propia gramática.

La eliminación de la recursividad por la izquierda y la factorización transformaron la gramática para un analizador descendente sin cambiar el lenguaje: en los dos casos se demostró que el no terminal genera el mismo conjunto de formas antes y después, escrito con las operaciones primitivas de las expresiones regulares del curso, (β)(α)\* en la primera y (α)(β₁,β₂) en la segunda.

La tabla de análisis predictivo de la gramática final tiene 106 celdas llenas y ninguna con dos reglas: la gramática es LL(1) y, por la proposición de la sección 6.7, no es ambigua. Cada posible conflicto de las reglas ε queda evitado por una decisión de diseño de las etapas anteriores. La tabla, exportada en `src/parser/tabla_ll1.csv`, es la que usa el analizador sintáctico de la Fase 3 para decidir, sin reglas escritas a mano en el código.

## Referencias

Aho, A. V., Lam, M. S., Sethi, R. y Ullman, J. D. (2006). *Compilers: Principles, techniques, and tools* (2.ª ed.). Addison-Wesley.

Hopcroft, J. E., Motwani, R. y Ullman, J. D. (2007). *Introduction to automata theory, languages, and computation* (3.ª ed.). Addison-Wesley.

Narváez Hincapié, D. J. y García Albarracín, J. D. (2026). *dsl-lenguajes-formales-proyecto* [Software]. GitHub. https://github.com/DanielJNarvaezH/dsl-lenguajes-formales-proyecto

## Apéndice A. Derivaciones de los programas de ejemplo

Son derivaciones más a la izquierda con la gramática inicial (sección 2). En cada línea se reemplaza el no terminal que está más a la izquierda, y al inicio de la línea aparece la regla aplicada. Como `<sentencias>` es recursiva por la izquierda (P2), la derivación primero despliega la lista completa y después deriva cada sentencia en orden. Para que las líneas se puedan leer:

- cuando una sentencia queda completa, sus tokens se reemplazan por **wₖ** (línea "=");
- cada expresión se deriva en un solo paso **⇒\***, con la lista de reglas aplicadas entre corchetes; las condiciones de `si` y `mientras` se abrevian después como **cₖ**;
- al final de cada derivación están los tokens de cada wₖ y cₖ.

El Apéndice A.4 muestra una condición derivada paso a paso, sin abreviar.

### A.1 ejemplo1_produccion.cft

```
# calcula la produccion total de dos lotes
inicio
    dato lote_norte = 320;
    dato lote_sur = 275.5;
    dato precio_kilo = 12500;
    dato total_kilos = lote_norte + lote_sur;
    dato ingreso = total_kilos * precio_kilo - 150000 / 2;
    dato promedio_2lotes = (lote_norte + lote_sur) / 2;
    mostrar("kilos cosechados");
    mostrar(total_kilos);
    mostrar(ingreso);
    mostrar(promedio_2lotes);
fin
```

```
      <programa>
⇒ P1  INICIO <sentencias> FIN
⇒ P2  INICIO <sentencias> <sentencia> FIN
⇒ P2  INICIO <sentencias> <sentencia> <sentencia> FIN
⇒ P2  INICIO <sentencias> <sentencia> <sentencia> <sentencia> FIN
⇒ P2  INICIO <sentencias> <sentencia> <sentencia> <sentencia> <sentencia> FIN
⇒ P2  INICIO <sentencias> <sentencia> <sentencia> <sentencia> <sentencia> <sentencia> FIN
⇒ P2  INICIO <sentencias> <sentencia> <sentencia> <sentencia> <sentencia> <sentencia> <sentencia> FIN
⇒ P2  INICIO <sentencias> <sentencia> <sentencia> <sentencia> <sentencia> <sentencia> <sentencia> <sentencia> FIN
⇒ P2  INICIO <sentencias> <sentencia> <sentencia> <sentencia> <sentencia> <sentencia> <sentencia> <sentencia> <sentencia> FIN
⇒ P2  INICIO <sentencias> <sentencia> <sentencia> <sentencia> <sentencia> <sentencia> <sentencia> <sentencia> <sentencia> <sentencia> FIN
⇒ P2  INICIO <sentencias> <sentencia> <sentencia> <sentencia> <sentencia> <sentencia> <sentencia> <sentencia> <sentencia> <sentencia> <sentencia> FIN
⇒ P3  INICIO <sentencia> <sentencia> <sentencia> <sentencia> <sentencia> <sentencia> <sentencia> <sentencia> <sentencia> <sentencia> FIN
⇒ P4  INICIO <declaracion> <sentencia> <sentencia> <sentencia> <sentencia> <sentencia> <sentencia> <sentencia> <sentencia> <sentencia> FIN
⇒ D1  INICIO DATO ID⟨lote_norte⟩ ASIGNACION <expresion> PUNTO_COMA <sentencia> <sentencia> <sentencia> <sentencia> <sentencia> <sentencia> <sentencia> <sentencia> <sentencia> FIN
⇒*    INICIO DATO ID⟨lote_norte⟩ ASIGNACION ENTERO⟨320⟩ PUNTO_COMA <sentencia> <sentencia> <sentencia> <sentencia> <sentencia> <sentencia> <sentencia> <sentencia> <sentencia> FIN   [E2 E4 E6 E8 E17 E20 E23]
=     INICIO w1 <sentencia> <sentencia> <sentencia> <sentencia> <sentencia> <sentencia> <sentencia> <sentencia> <sentencia> FIN
⇒ P4  INICIO w1 <declaracion> <sentencia> <sentencia> <sentencia> <sentencia> <sentencia> <sentencia> <sentencia> <sentencia> FIN
⇒ D1  INICIO w1 DATO ID⟨lote_sur⟩ ASIGNACION <expresion> PUNTO_COMA <sentencia> <sentencia> <sentencia> <sentencia> <sentencia> <sentencia> <sentencia> <sentencia> FIN
⇒*    INICIO w1 DATO ID⟨lote_sur⟩ ASIGNACION DECIMAL⟨275.5⟩ PUNTO_COMA <sentencia> <sentencia> <sentencia> <sentencia> <sentencia> <sentencia> <sentencia> <sentencia> FIN   [E2 E4 E6 E8 E17 E20 E24]
=     INICIO w1 w2 <sentencia> <sentencia> <sentencia> <sentencia> <sentencia> <sentencia> <sentencia> <sentencia> FIN
⇒ P4  INICIO w1 w2 <declaracion> <sentencia> <sentencia> <sentencia> <sentencia> <sentencia> <sentencia> <sentencia> FIN
⇒ D1  INICIO w1 w2 DATO ID⟨precio_kilo⟩ ASIGNACION <expresion> PUNTO_COMA <sentencia> <sentencia> <sentencia> <sentencia> <sentencia> <sentencia> <sentencia> FIN
⇒*    INICIO w1 w2 DATO ID⟨precio_kilo⟩ ASIGNACION ENTERO⟨12500⟩ PUNTO_COMA <sentencia> <sentencia> <sentencia> <sentencia> <sentencia> <sentencia> <sentencia> FIN   [E2 E4 E6 E8 E17 E20 E23]
=     INICIO w1 w2 w3 <sentencia> <sentencia> <sentencia> <sentencia> <sentencia> <sentencia> <sentencia> FIN
⇒ P4  INICIO w1 w2 w3 <declaracion> <sentencia> <sentencia> <sentencia> <sentencia> <sentencia> <sentencia> FIN
⇒ D1  INICIO w1 w2 w3 DATO ID⟨total_kilos⟩ ASIGNACION <expresion> PUNTO_COMA <sentencia> <sentencia> <sentencia> <sentencia> <sentencia> <sentencia> FIN
⇒*    INICIO w1 w2 w3 DATO ID⟨total_kilos⟩ ASIGNACION ID⟨lote_norte⟩ SUMA ID⟨lote_sur⟩ PUNTO_COMA <sentencia> <sentencia> <sentencia> <sentencia> <sentencia> <sentencia> FIN   [E2 E4 E6 E8 E15 E17 E20 E22 E20 E22]
=     INICIO w1 w2 w3 w4 <sentencia> <sentencia> <sentencia> <sentencia> <sentencia> <sentencia> FIN
⇒ P4  INICIO w1 w2 w3 w4 <declaracion> <sentencia> <sentencia> <sentencia> <sentencia> <sentencia> FIN
⇒ D1  INICIO w1 w2 w3 w4 DATO ID⟨ingreso⟩ ASIGNACION <expresion> PUNTO_COMA <sentencia> <sentencia> <sentencia> <sentencia> <sentencia> FIN
⇒*    INICIO w1 w2 w3 w4 DATO ID⟨ingreso⟩ ASIGNACION ID⟨total_kilos⟩ MULT ID⟨precio_kilo⟩ RESTA ENTERO⟨150000⟩ DIV ENTERO⟨2⟩ PUNTO_COMA <sentencia> <sentencia> <sentencia> <sentencia> <sentencia> FIN   [E2 E4 E6 E8 E16 E17 E18 E20 E22 E22 E19 E20 E23 E23]
=     INICIO w1 w2 w3 w4 w5 <sentencia> <sentencia> <sentencia> <sentencia> <sentencia> FIN
⇒ P4  INICIO w1 w2 w3 w4 w5 <declaracion> <sentencia> <sentencia> <sentencia> <sentencia> FIN
⇒ D1  INICIO w1 w2 w3 w4 w5 DATO ID⟨promedio_2lotes⟩ ASIGNACION <expresion> PUNTO_COMA <sentencia> <sentencia> <sentencia> <sentencia> FIN
⇒*    INICIO w1 w2 w3 w4 w5 DATO ID⟨promedio_2lotes⟩ ASIGNACION PAR_ABRE ID⟨lote_norte⟩ SUMA ID⟨lote_sur⟩ PAR_CIERRA DIV ENTERO⟨2⟩ PUNTO_COMA <sentencia> <sentencia> <sentencia> <sentencia> FIN   [E2 E4 E6 E8 E17 E19 E20 E21 E2 E4 E6 E8 E15 E17 E20 E22 E20 E22 E23]
=     INICIO w1 w2 w3 w4 w5 w6 <sentencia> <sentencia> <sentencia> <sentencia> FIN
⇒ P6  INICIO w1 w2 w3 w4 w5 w6 <salida> <sentencia> <sentencia> <sentencia> FIN
⇒ M1  INICIO w1 w2 w3 w4 w5 w6 MOSTRAR PAR_ABRE <argumento> PAR_CIERRA PUNTO_COMA <sentencia> <sentencia> <sentencia> FIN
⇒ M3  INICIO w1 w2 w3 w4 w5 w6 MOSTRAR PAR_ABRE CADENA⟨"kilos cosechados"⟩ PAR_CIERRA PUNTO_COMA <sentencia> <sentencia> <sentencia> FIN
=     INICIO w1 w2 w3 w4 w5 w6 w7 <sentencia> <sentencia> <sentencia> FIN
⇒ P6  INICIO w1 w2 w3 w4 w5 w6 w7 <salida> <sentencia> <sentencia> FIN
⇒ M1  INICIO w1 w2 w3 w4 w5 w6 w7 MOSTRAR PAR_ABRE <argumento> PAR_CIERRA PUNTO_COMA <sentencia> <sentencia> FIN
⇒ M2  INICIO w1 w2 w3 w4 w5 w6 w7 MOSTRAR PAR_ABRE <expresion> PAR_CIERRA PUNTO_COMA <sentencia> <sentencia> FIN
⇒*    INICIO w1 w2 w3 w4 w5 w6 w7 MOSTRAR PAR_ABRE ID⟨total_kilos⟩ PAR_CIERRA PUNTO_COMA <sentencia> <sentencia> FIN   [E2 E4 E6 E8 E17 E20 E22]
=     INICIO w1 w2 w3 w4 w5 w6 w7 w8 <sentencia> <sentencia> FIN
⇒ P6  INICIO w1 w2 w3 w4 w5 w6 w7 w8 <salida> <sentencia> FIN
⇒ M1  INICIO w1 w2 w3 w4 w5 w6 w7 w8 MOSTRAR PAR_ABRE <argumento> PAR_CIERRA PUNTO_COMA <sentencia> FIN
⇒ M2  INICIO w1 w2 w3 w4 w5 w6 w7 w8 MOSTRAR PAR_ABRE <expresion> PAR_CIERRA PUNTO_COMA <sentencia> FIN
⇒*    INICIO w1 w2 w3 w4 w5 w6 w7 w8 MOSTRAR PAR_ABRE ID⟨ingreso⟩ PAR_CIERRA PUNTO_COMA <sentencia> FIN   [E2 E4 E6 E8 E17 E20 E22]
=     INICIO w1 w2 w3 w4 w5 w6 w7 w8 w9 <sentencia> FIN
⇒ P6  INICIO w1 w2 w3 w4 w5 w6 w7 w8 w9 <salida> FIN
⇒ M1  INICIO w1 w2 w3 w4 w5 w6 w7 w8 w9 MOSTRAR PAR_ABRE <argumento> PAR_CIERRA PUNTO_COMA FIN
⇒ M2  INICIO w1 w2 w3 w4 w5 w6 w7 w8 w9 MOSTRAR PAR_ABRE <expresion> PAR_CIERRA PUNTO_COMA FIN
⇒*    INICIO w1 w2 w3 w4 w5 w6 w7 w8 w9 MOSTRAR PAR_ABRE ID⟨promedio_2lotes⟩ PAR_CIERRA PUNTO_COMA FIN   [E2 E4 E6 E8 E17 E20 E22]
=     INICIO w1 w2 w3 w4 w5 w6 w7 w8 w9 w10 FIN

w1 = DATO ID⟨lote_norte⟩ ASIGNACION ENTERO⟨320⟩ PUNTO_COMA
w2 = DATO ID⟨lote_sur⟩ ASIGNACION DECIMAL⟨275.5⟩ PUNTO_COMA
w3 = DATO ID⟨precio_kilo⟩ ASIGNACION ENTERO⟨12500⟩ PUNTO_COMA
w4 = DATO ID⟨total_kilos⟩ ASIGNACION ID⟨lote_norte⟩ SUMA ID⟨lote_sur⟩ PUNTO_COMA
w5 = DATO ID⟨ingreso⟩ ASIGNACION ID⟨total_kilos⟩ MULT ID⟨precio_kilo⟩ RESTA ENTERO⟨150000⟩ DIV ENTERO⟨2⟩ PUNTO_COMA
w6 = DATO ID⟨promedio_2lotes⟩ ASIGNACION PAR_ABRE ID⟨lote_norte⟩ SUMA ID⟨lote_sur⟩ PAR_CIERRA DIV ENTERO⟨2⟩ PUNTO_COMA
w7 = MOSTRAR PAR_ABRE CADENA⟨"kilos cosechados"⟩ PAR_CIERRA PUNTO_COMA
w8 = MOSTRAR PAR_ABRE ID⟨total_kilos⟩ PAR_CIERRA PUNTO_COMA
w9 = MOSTRAR PAR_ABRE ID⟨ingreso⟩ PAR_CIERRA PUNTO_COMA
w10 = MOSTRAR PAR_ABRE ID⟨promedio_2lotes⟩ PAR_CIERRA PUNTO_COMA
```

### A.2 ejemplo2_clasificacion.cft

```
# clasifica el cafe segun humedad y defectos
inicio
    dato humedad = 11.5;
    dato defectos = 4;
    si (humedad >= 10 y humedad <= 12) entonces
        si (defectos < 5) entonces
            mostrar("cafe tipo exportacion");
        sino
            mostrar("cafe para consumo interno");
        fin
    sino
        mostrar("secar de nuevo");
    fin
    si (defectos != 0) entonces
        mostrar("hay granos defectuosos");
    fin
fin
```

```
      <programa>
⇒ P1  INICIO <sentencias> FIN
⇒ P2  INICIO <sentencias> <sentencia> FIN
⇒ P2  INICIO <sentencias> <sentencia> <sentencia> FIN
⇒ P2  INICIO <sentencias> <sentencia> <sentencia> <sentencia> FIN
⇒ P2  INICIO <sentencias> <sentencia> <sentencia> <sentencia> <sentencia> FIN
⇒ P3  INICIO <sentencia> <sentencia> <sentencia> <sentencia> FIN
⇒ P4  INICIO <declaracion> <sentencia> <sentencia> <sentencia> FIN
⇒ D1  INICIO DATO ID⟨humedad⟩ ASIGNACION <expresion> PUNTO_COMA <sentencia> <sentencia> <sentencia> FIN
⇒*    INICIO DATO ID⟨humedad⟩ ASIGNACION DECIMAL⟨11.5⟩ PUNTO_COMA <sentencia> <sentencia> <sentencia> FIN   [E2 E4 E6 E8 E17 E20 E24]
=     INICIO w1 <sentencia> <sentencia> <sentencia> FIN
⇒ P4  INICIO w1 <declaracion> <sentencia> <sentencia> FIN
⇒ D1  INICIO w1 DATO ID⟨defectos⟩ ASIGNACION <expresion> PUNTO_COMA <sentencia> <sentencia> FIN
⇒*    INICIO w1 DATO ID⟨defectos⟩ ASIGNACION ENTERO⟨4⟩ PUNTO_COMA <sentencia> <sentencia> FIN   [E2 E4 E6 E8 E17 E20 E23]
=     INICIO w1 w2 <sentencia> <sentencia> FIN
⇒ P7  INICIO w1 w2 <condicional> <sentencia> FIN
⇒ C2  INICIO w1 w2 SI PAR_ABRE <expresion> PAR_CIERRA ENTONCES <sentencias> SINO <sentencias> FIN <sentencia> FIN
⇒*    INICIO w1 w2 SI PAR_ABRE ID⟨humedad⟩ MAYOR_IGUAL ENTERO⟨10⟩ Y ID⟨humedad⟩ MENOR_IGUAL ENTERO⟨12⟩ PAR_CIERRA ENTONCES <sentencias> SINO <sentencias> FIN <sentencia> FIN   [E2 E3 E4 E6 E7 E17 E20 E22 E12 E17 E20 E23 E6 E7 E17 E20 E22 E11 E17 E20 E23]
⇒ P2  INICIO w1 w2 SI PAR_ABRE c1 PAR_CIERRA ENTONCES <sentencias> <sentencia> SINO <sentencias> FIN <sentencia> FIN
⇒ P3  INICIO w1 w2 SI PAR_ABRE c1 PAR_CIERRA ENTONCES <sentencia> SINO <sentencias> FIN <sentencia> FIN
⇒ P7  INICIO w1 w2 SI PAR_ABRE c1 PAR_CIERRA ENTONCES <condicional> SINO <sentencias> FIN <sentencia> FIN
⇒ C2  INICIO w1 w2 SI PAR_ABRE c1 PAR_CIERRA ENTONCES SI PAR_ABRE <expresion> PAR_CIERRA ENTONCES <sentencias> SINO <sentencias> FIN SINO <sentencias> FIN <sentencia> FIN
⇒*    INICIO w1 w2 SI PAR_ABRE c1 PAR_CIERRA ENTONCES SI PAR_ABRE ID⟨defectos⟩ MENOR ENTERO⟨5⟩ PAR_CIERRA ENTONCES <sentencias> SINO <sentencias> FIN SINO <sentencias> FIN <sentencia> FIN   [E2 E4 E6 E7 E17 E20 E22 E9 E17 E20 E23]
⇒ P2  INICIO w1 w2 SI PAR_ABRE c1 PAR_CIERRA ENTONCES SI PAR_ABRE c2 PAR_CIERRA ENTONCES <sentencias> <sentencia> SINO <sentencias> FIN SINO <sentencias> FIN <sentencia> FIN
⇒ P3  INICIO w1 w2 SI PAR_ABRE c1 PAR_CIERRA ENTONCES SI PAR_ABRE c2 PAR_CIERRA ENTONCES <sentencia> SINO <sentencias> FIN SINO <sentencias> FIN <sentencia> FIN
⇒ P6  INICIO w1 w2 SI PAR_ABRE c1 PAR_CIERRA ENTONCES SI PAR_ABRE c2 PAR_CIERRA ENTONCES <salida> SINO <sentencias> FIN SINO <sentencias> FIN <sentencia> FIN
⇒ M1  INICIO w1 w2 SI PAR_ABRE c1 PAR_CIERRA ENTONCES SI PAR_ABRE c2 PAR_CIERRA ENTONCES MOSTRAR PAR_ABRE <argumento> PAR_CIERRA PUNTO_COMA SINO <sentencias> FIN SINO <sentencias> FIN <sentencia> FIN
⇒ M3  INICIO w1 w2 SI PAR_ABRE c1 PAR_CIERRA ENTONCES SI PAR_ABRE c2 PAR_CIERRA ENTONCES MOSTRAR PAR_ABRE CADENA⟨"cafe tipo exportacion"⟩ PAR_CIERRA PUNTO_COMA SINO <sentencias> FIN SINO <sentencias> FIN <sentencia> FIN
=     INICIO w1 w2 SI PAR_ABRE c1 PAR_CIERRA ENTONCES SI PAR_ABRE c2 PAR_CIERRA ENTONCES w3 SINO <sentencias> FIN SINO <sentencias> FIN <sentencia> FIN
⇒ P2  INICIO w1 w2 SI PAR_ABRE c1 PAR_CIERRA ENTONCES SI PAR_ABRE c2 PAR_CIERRA ENTONCES w3 SINO <sentencias> <sentencia> FIN SINO <sentencias> FIN <sentencia> FIN
⇒ P3  INICIO w1 w2 SI PAR_ABRE c1 PAR_CIERRA ENTONCES SI PAR_ABRE c2 PAR_CIERRA ENTONCES w3 SINO <sentencia> FIN SINO <sentencias> FIN <sentencia> FIN
⇒ P6  INICIO w1 w2 SI PAR_ABRE c1 PAR_CIERRA ENTONCES SI PAR_ABRE c2 PAR_CIERRA ENTONCES w3 SINO <salida> FIN SINO <sentencias> FIN <sentencia> FIN
⇒ M1  INICIO w1 w2 SI PAR_ABRE c1 PAR_CIERRA ENTONCES SI PAR_ABRE c2 PAR_CIERRA ENTONCES w3 SINO MOSTRAR PAR_ABRE <argumento> PAR_CIERRA PUNTO_COMA FIN SINO <sentencias> FIN <sentencia> FIN
⇒ M3  INICIO w1 w2 SI PAR_ABRE c1 PAR_CIERRA ENTONCES SI PAR_ABRE c2 PAR_CIERRA ENTONCES w3 SINO MOSTRAR PAR_ABRE CADENA⟨"cafe para consumo interno"⟩ PAR_CIERRA PUNTO_COMA FIN SINO <sentencias> FIN <sentencia> FIN
=     INICIO w1 w2 SI PAR_ABRE c1 PAR_CIERRA ENTONCES SI PAR_ABRE c2 PAR_CIERRA ENTONCES w3 SINO w4 FIN SINO <sentencias> FIN <sentencia> FIN
=     INICIO w1 w2 SI PAR_ABRE c1 PAR_CIERRA ENTONCES w5 SINO <sentencias> FIN <sentencia> FIN
⇒ P2  INICIO w1 w2 SI PAR_ABRE c1 PAR_CIERRA ENTONCES w5 SINO <sentencias> <sentencia> FIN <sentencia> FIN
⇒ P3  INICIO w1 w2 SI PAR_ABRE c1 PAR_CIERRA ENTONCES w5 SINO <sentencia> FIN <sentencia> FIN
⇒ P6  INICIO w1 w2 SI PAR_ABRE c1 PAR_CIERRA ENTONCES w5 SINO <salida> FIN <sentencia> FIN
⇒ M1  INICIO w1 w2 SI PAR_ABRE c1 PAR_CIERRA ENTONCES w5 SINO MOSTRAR PAR_ABRE <argumento> PAR_CIERRA PUNTO_COMA FIN <sentencia> FIN
⇒ M3  INICIO w1 w2 SI PAR_ABRE c1 PAR_CIERRA ENTONCES w5 SINO MOSTRAR PAR_ABRE CADENA⟨"secar de nuevo"⟩ PAR_CIERRA PUNTO_COMA FIN <sentencia> FIN
=     INICIO w1 w2 SI PAR_ABRE c1 PAR_CIERRA ENTONCES w5 SINO w6 FIN <sentencia> FIN
=     INICIO w1 w2 w7 <sentencia> FIN
⇒ P7  INICIO w1 w2 w7 <condicional> FIN
⇒ C1  INICIO w1 w2 w7 SI PAR_ABRE <expresion> PAR_CIERRA ENTONCES <sentencias> FIN FIN
⇒*    INICIO w1 w2 w7 SI PAR_ABRE ID⟨defectos⟩ DIFERENTE ENTERO⟨0⟩ PAR_CIERRA ENTONCES <sentencias> FIN FIN   [E2 E4 E6 E7 E17 E20 E22 E14 E17 E20 E23]
⇒ P2  INICIO w1 w2 w7 SI PAR_ABRE c3 PAR_CIERRA ENTONCES <sentencias> <sentencia> FIN FIN
⇒ P3  INICIO w1 w2 w7 SI PAR_ABRE c3 PAR_CIERRA ENTONCES <sentencia> FIN FIN
⇒ P6  INICIO w1 w2 w7 SI PAR_ABRE c3 PAR_CIERRA ENTONCES <salida> FIN FIN
⇒ M1  INICIO w1 w2 w7 SI PAR_ABRE c3 PAR_CIERRA ENTONCES MOSTRAR PAR_ABRE <argumento> PAR_CIERRA PUNTO_COMA FIN FIN
⇒ M3  INICIO w1 w2 w7 SI PAR_ABRE c3 PAR_CIERRA ENTONCES MOSTRAR PAR_ABRE CADENA⟨"hay granos defectuosos"⟩ PAR_CIERRA PUNTO_COMA FIN FIN
=     INICIO w1 w2 w7 SI PAR_ABRE c3 PAR_CIERRA ENTONCES w8 FIN FIN
=     INICIO w1 w2 w7 w9 FIN

w1 = DATO ID⟨humedad⟩ ASIGNACION DECIMAL⟨11.5⟩ PUNTO_COMA
w2 = DATO ID⟨defectos⟩ ASIGNACION ENTERO⟨4⟩ PUNTO_COMA
w3 = MOSTRAR PAR_ABRE CADENA⟨"cafe tipo exportacion"⟩ PAR_CIERRA PUNTO_COMA
w4 = MOSTRAR PAR_ABRE CADENA⟨"cafe para consumo interno"⟩ PAR_CIERRA PUNTO_COMA
w5 = SI PAR_ABRE c2 PAR_CIERRA ENTONCES w3 SINO w4 FIN
w6 = MOSTRAR PAR_ABRE CADENA⟨"secar de nuevo"⟩ PAR_CIERRA PUNTO_COMA
w7 = SI PAR_ABRE c1 PAR_CIERRA ENTONCES w5 SINO w6 FIN
w8 = MOSTRAR PAR_ABRE CADENA⟨"hay granos defectuosos"⟩ PAR_CIERRA PUNTO_COMA
w9 = SI PAR_ABRE c3 PAR_CIERRA ENTONCES w8 FIN
c1 = ID⟨humedad⟩ MAYOR_IGUAL ENTERO⟨10⟩ Y ID⟨humedad⟩ MENOR_IGUAL ENTERO⟨12⟩      (humedad >= 10 y humedad <= 12)
c2 = ID⟨defectos⟩ MENOR ENTERO⟨5⟩      (defectos < 5)
c3 = ID⟨defectos⟩ DIFERENTE ENTERO⟨0⟩      (defectos != 0)
```

### A.3 ejemplo3_secado.cft

```
# simula los dias de secado del grano
inicio
    dato dia = 1;
    dato humedad = 45;
    mientras (humedad > 12) hacer
        humedad = humedad - 6;   # pierde 6 puntos por dia
        si (dia == 5 o no (humedad > 20)) entonces
            mostrar("revisar el secador");
        fin
        dia = dia + 1;
    fin
    mostrar(dia);
fin
```

```
      <programa>
⇒ P1  INICIO <sentencias> FIN
⇒ P2  INICIO <sentencias> <sentencia> FIN
⇒ P2  INICIO <sentencias> <sentencia> <sentencia> FIN
⇒ P2  INICIO <sentencias> <sentencia> <sentencia> <sentencia> FIN
⇒ P2  INICIO <sentencias> <sentencia> <sentencia> <sentencia> <sentencia> FIN
⇒ P3  INICIO <sentencia> <sentencia> <sentencia> <sentencia> FIN
⇒ P4  INICIO <declaracion> <sentencia> <sentencia> <sentencia> FIN
⇒ D1  INICIO DATO ID⟨dia⟩ ASIGNACION <expresion> PUNTO_COMA <sentencia> <sentencia> <sentencia> FIN
⇒*    INICIO DATO ID⟨dia⟩ ASIGNACION ENTERO⟨1⟩ PUNTO_COMA <sentencia> <sentencia> <sentencia> FIN   [E2 E4 E6 E8 E17 E20 E23]
=     INICIO w1 <sentencia> <sentencia> <sentencia> FIN
⇒ P4  INICIO w1 <declaracion> <sentencia> <sentencia> FIN
⇒ D1  INICIO w1 DATO ID⟨humedad⟩ ASIGNACION <expresion> PUNTO_COMA <sentencia> <sentencia> FIN
⇒*    INICIO w1 DATO ID⟨humedad⟩ ASIGNACION ENTERO⟨45⟩ PUNTO_COMA <sentencia> <sentencia> FIN   [E2 E4 E6 E8 E17 E20 E23]
=     INICIO w1 w2 <sentencia> <sentencia> FIN
⇒ P8  INICIO w1 w2 <ciclo> <sentencia> FIN
⇒ L1  INICIO w1 w2 MIENTRAS PAR_ABRE <expresion> PAR_CIERRA HACER <sentencias> FIN <sentencia> FIN
⇒*    INICIO w1 w2 MIENTRAS PAR_ABRE ID⟨humedad⟩ MAYOR ENTERO⟨12⟩ PAR_CIERRA HACER <sentencias> FIN <sentencia> FIN   [E2 E4 E6 E7 E17 E20 E22 E10 E17 E20 E23]
⇒ P2  INICIO w1 w2 MIENTRAS PAR_ABRE c1 PAR_CIERRA HACER <sentencias> <sentencia> FIN <sentencia> FIN
⇒ P2  INICIO w1 w2 MIENTRAS PAR_ABRE c1 PAR_CIERRA HACER <sentencias> <sentencia> <sentencia> FIN <sentencia> FIN
⇒ P2  INICIO w1 w2 MIENTRAS PAR_ABRE c1 PAR_CIERRA HACER <sentencias> <sentencia> <sentencia> <sentencia> FIN <sentencia> FIN
⇒ P3  INICIO w1 w2 MIENTRAS PAR_ABRE c1 PAR_CIERRA HACER <sentencia> <sentencia> <sentencia> FIN <sentencia> FIN
⇒ P5  INICIO w1 w2 MIENTRAS PAR_ABRE c1 PAR_CIERRA HACER <asignacion> <sentencia> <sentencia> FIN <sentencia> FIN
⇒ A1  INICIO w1 w2 MIENTRAS PAR_ABRE c1 PAR_CIERRA HACER ID⟨humedad⟩ ASIGNACION <expresion> PUNTO_COMA <sentencia> <sentencia> FIN <sentencia> FIN
⇒*    INICIO w1 w2 MIENTRAS PAR_ABRE c1 PAR_CIERRA HACER ID⟨humedad⟩ ASIGNACION ID⟨humedad⟩ RESTA ENTERO⟨6⟩ PUNTO_COMA <sentencia> <sentencia> FIN <sentencia> FIN   [E2 E4 E6 E8 E16 E17 E20 E22 E20 E23]
=     INICIO w1 w2 MIENTRAS PAR_ABRE c1 PAR_CIERRA HACER w3 <sentencia> <sentencia> FIN <sentencia> FIN
⇒ P7  INICIO w1 w2 MIENTRAS PAR_ABRE c1 PAR_CIERRA HACER w3 <condicional> <sentencia> FIN <sentencia> FIN
⇒ C1  INICIO w1 w2 MIENTRAS PAR_ABRE c1 PAR_CIERRA HACER w3 SI PAR_ABRE <expresion> PAR_CIERRA ENTONCES <sentencias> FIN <sentencia> FIN <sentencia> FIN
⇒*    INICIO w1 w2 MIENTRAS PAR_ABRE c1 PAR_CIERRA HACER w3 SI PAR_ABRE ID⟨dia⟩ IGUAL ENTERO⟨5⟩ O NO PAR_ABRE ID⟨humedad⟩ MAYOR ENTERO⟨20⟩ PAR_CIERRA PAR_CIERRA ENTONCES <sentencias> FIN <sentencia> FIN <sentencia> FIN   [E1 E2 E4 E6 E7 E17 E20 E22 E13 E17 E20 E23 E4 E5 E6 E8 E17 E20 E21 E2 E4 E6 E7 E17 E20 E22 E10 E17 E20 E23]
⇒ P2  INICIO w1 w2 MIENTRAS PAR_ABRE c1 PAR_CIERRA HACER w3 SI PAR_ABRE c2 PAR_CIERRA ENTONCES <sentencias> <sentencia> FIN <sentencia> FIN <sentencia> FIN
⇒ P3  INICIO w1 w2 MIENTRAS PAR_ABRE c1 PAR_CIERRA HACER w3 SI PAR_ABRE c2 PAR_CIERRA ENTONCES <sentencia> FIN <sentencia> FIN <sentencia> FIN
⇒ P6  INICIO w1 w2 MIENTRAS PAR_ABRE c1 PAR_CIERRA HACER w3 SI PAR_ABRE c2 PAR_CIERRA ENTONCES <salida> FIN <sentencia> FIN <sentencia> FIN
⇒ M1  INICIO w1 w2 MIENTRAS PAR_ABRE c1 PAR_CIERRA HACER w3 SI PAR_ABRE c2 PAR_CIERRA ENTONCES MOSTRAR PAR_ABRE <argumento> PAR_CIERRA PUNTO_COMA FIN <sentencia> FIN <sentencia> FIN
⇒ M3  INICIO w1 w2 MIENTRAS PAR_ABRE c1 PAR_CIERRA HACER w3 SI PAR_ABRE c2 PAR_CIERRA ENTONCES MOSTRAR PAR_ABRE CADENA⟨"revisar el secador"⟩ PAR_CIERRA PUNTO_COMA FIN <sentencia> FIN <sentencia> FIN
=     INICIO w1 w2 MIENTRAS PAR_ABRE c1 PAR_CIERRA HACER w3 SI PAR_ABRE c2 PAR_CIERRA ENTONCES w4 FIN <sentencia> FIN <sentencia> FIN
=     INICIO w1 w2 MIENTRAS PAR_ABRE c1 PAR_CIERRA HACER w3 w5 <sentencia> FIN <sentencia> FIN
⇒ P5  INICIO w1 w2 MIENTRAS PAR_ABRE c1 PAR_CIERRA HACER w3 w5 <asignacion> FIN <sentencia> FIN
⇒ A1  INICIO w1 w2 MIENTRAS PAR_ABRE c1 PAR_CIERRA HACER w3 w5 ID⟨dia⟩ ASIGNACION <expresion> PUNTO_COMA FIN <sentencia> FIN
⇒*    INICIO w1 w2 MIENTRAS PAR_ABRE c1 PAR_CIERRA HACER w3 w5 ID⟨dia⟩ ASIGNACION ID⟨dia⟩ SUMA ENTERO⟨1⟩ PUNTO_COMA FIN <sentencia> FIN   [E2 E4 E6 E8 E15 E17 E20 E22 E20 E23]
=     INICIO w1 w2 MIENTRAS PAR_ABRE c1 PAR_CIERRA HACER w3 w5 w6 FIN <sentencia> FIN
=     INICIO w1 w2 w7 <sentencia> FIN
⇒ P6  INICIO w1 w2 w7 <salida> FIN
⇒ M1  INICIO w1 w2 w7 MOSTRAR PAR_ABRE <argumento> PAR_CIERRA PUNTO_COMA FIN
⇒ M2  INICIO w1 w2 w7 MOSTRAR PAR_ABRE <expresion> PAR_CIERRA PUNTO_COMA FIN
⇒*    INICIO w1 w2 w7 MOSTRAR PAR_ABRE ID⟨dia⟩ PAR_CIERRA PUNTO_COMA FIN   [E2 E4 E6 E8 E17 E20 E22]
=     INICIO w1 w2 w7 w8 FIN

w1 = DATO ID⟨dia⟩ ASIGNACION ENTERO⟨1⟩ PUNTO_COMA
w2 = DATO ID⟨humedad⟩ ASIGNACION ENTERO⟨45⟩ PUNTO_COMA
w3 = ID⟨humedad⟩ ASIGNACION ID⟨humedad⟩ RESTA ENTERO⟨6⟩ PUNTO_COMA
w4 = MOSTRAR PAR_ABRE CADENA⟨"revisar el secador"⟩ PAR_CIERRA PUNTO_COMA
w5 = SI PAR_ABRE c2 PAR_CIERRA ENTONCES w4 FIN
w6 = ID⟨dia⟩ ASIGNACION ID⟨dia⟩ SUMA ENTERO⟨1⟩ PUNTO_COMA
w7 = MIENTRAS PAR_ABRE c1 PAR_CIERRA HACER w3 w5 w6 FIN
w8 = MOSTRAR PAR_ABRE ID⟨dia⟩ PAR_CIERRA PUNTO_COMA
c1 = ID⟨humedad⟩ MAYOR ENTERO⟨12⟩      (humedad > 12)
c2 = ID⟨dia⟩ IGUAL ENTERO⟨5⟩ O NO PAR_ABRE ID⟨humedad⟩ MAYOR ENTERO⟨20⟩ PAR_CIERRA      (dia == 5 o no ( humedad > 20 ))
```

### A.4 Derivación completa de una condición

Condición del `si` de `ejemplo3_secado.cft`: `dia == 5 o no (humedad > 20)`.

```
      <expresion>
⇒ E1  <expresion> O <conjuncion>
⇒ E2  <conjuncion> O <conjuncion>
⇒ E4  <negacion> O <conjuncion>
⇒ E6  <comparacion> O <conjuncion>
⇒ E7  <suma> <op_rel> <suma> O <conjuncion>
⇒ E17 <termino> <op_rel> <suma> O <conjuncion>
⇒ E20 <factor> <op_rel> <suma> O <conjuncion>
⇒ E22 ID⟨dia⟩ <op_rel> <suma> O <conjuncion>
⇒ E13 ID⟨dia⟩ IGUAL <suma> O <conjuncion>
⇒ E17 ID⟨dia⟩ IGUAL <termino> O <conjuncion>
⇒ E20 ID⟨dia⟩ IGUAL <factor> O <conjuncion>
⇒ E23 ID⟨dia⟩ IGUAL ENTERO⟨5⟩ O <conjuncion>
⇒ E4  ID⟨dia⟩ IGUAL ENTERO⟨5⟩ O <negacion>
⇒ E5  ID⟨dia⟩ IGUAL ENTERO⟨5⟩ O NO <negacion>
⇒ E6  ID⟨dia⟩ IGUAL ENTERO⟨5⟩ O NO <comparacion>
⇒ E8  ID⟨dia⟩ IGUAL ENTERO⟨5⟩ O NO <suma>
⇒ E17 ID⟨dia⟩ IGUAL ENTERO⟨5⟩ O NO <termino>
⇒ E20 ID⟨dia⟩ IGUAL ENTERO⟨5⟩ O NO <factor>
⇒ E21 ID⟨dia⟩ IGUAL ENTERO⟨5⟩ O NO PAR_ABRE <expresion> PAR_CIERRA
⇒ E2  ID⟨dia⟩ IGUAL ENTERO⟨5⟩ O NO PAR_ABRE <conjuncion> PAR_CIERRA
⇒ E4  ID⟨dia⟩ IGUAL ENTERO⟨5⟩ O NO PAR_ABRE <negacion> PAR_CIERRA
⇒ E6  ID⟨dia⟩ IGUAL ENTERO⟨5⟩ O NO PAR_ABRE <comparacion> PAR_CIERRA
⇒ E7  ID⟨dia⟩ IGUAL ENTERO⟨5⟩ O NO PAR_ABRE <suma> <op_rel> <suma> PAR_CIERRA
⇒ E17 ID⟨dia⟩ IGUAL ENTERO⟨5⟩ O NO PAR_ABRE <termino> <op_rel> <suma> PAR_CIERRA
⇒ E20 ID⟨dia⟩ IGUAL ENTERO⟨5⟩ O NO PAR_ABRE <factor> <op_rel> <suma> PAR_CIERRA
⇒ E22 ID⟨dia⟩ IGUAL ENTERO⟨5⟩ O NO PAR_ABRE ID⟨humedad⟩ <op_rel> <suma> PAR_CIERRA
⇒ E10 ID⟨dia⟩ IGUAL ENTERO⟨5⟩ O NO PAR_ABRE ID⟨humedad⟩ MAYOR <suma> PAR_CIERRA
⇒ E17 ID⟨dia⟩ IGUAL ENTERO⟨5⟩ O NO PAR_ABRE ID⟨humedad⟩ MAYOR <termino> PAR_CIERRA
⇒ E20 ID⟨dia⟩ IGUAL ENTERO⟨5⟩ O NO PAR_ABRE ID⟨humedad⟩ MAYOR <factor> PAR_CIERRA
⇒ E23 ID⟨dia⟩ IGUAL ENTERO⟨5⟩ O NO PAR_ABRE ID⟨humedad⟩ MAYOR ENTERO⟨20⟩ PAR_CIERRA
```

## Apéndice B. Verificación de las transformaciones

Las demostraciones de las secciones 3 a 6 valen para cadenas de cualquier longitud. Además, cada transformación se verificó con programas, para comprobar que las reglas se escribieron sin errores. Las pruebas acotadas no reemplazan las demostraciones: las complementan.

### B.1 Eliminación de la recursividad por la izquierda

Además de la demostración de la sección 4.2, se verificó la transformación con dos analizadores escritos para esta tarea: un analizador general (algoritmo de Earley), que acepta cualquier gramática independiente del contexto, incluidas las recursivas por la izquierda, y un analizador descendente ingenuo que prueba todas las alternativas de cada no terminal y cuenta los árboles.

**Tabla 32**

*Verificación de la eliminación de la recursividad por la izquierda*

| Prueba | Resultado |
|---|---|
| Analizador descendente ingenuo sobre la gramática inicial, entrada `ID` desde `<expresion>` | Recursión infinita: no termina |
| Analizador descendente ingenuo sobre la gramática sin recursividad (sección 4.3) | Termina en todas las pruebas de esta tabla |
| Todas las cadenas de hasta 5 tokens desde `<expresion>`, sobre ID, SUMA, RESTA, MULT, DIV, O, Y, NO, MENOR, PAR_ABRE y PAR_CIERRA | 177 156 cadenas, 108 aceptadas, **0 diferencias** entre las dos gramáticas |
| Todas las cadenas de hasta 6 tokens desde `<expresion>`, sobre ID, SUMA, MULT, O, Y, NO, PAR_ABRE y PAR_CIERRA | 299 593 cadenas, 138 aceptadas, **0 diferencias** |
| Todas las cadenas de hasta 5 tokens desde `<sentencias>`, sobre 10 tokens de sentencias | 111 111 cadenas, **0 diferencias**; también 0 diferencias entre la versión simplificada (R1, R2) y la versión sin simplificar de 5.1 |
| 2 996 programas generados al azar desde `<programa>` (hasta 79 tokens), más 2 variantes de cada uno con un token cambiado | 8 988 entradas, 3 287 aceptadas y 5 701 rechazadas, **0 diferencias** |

Las pruebas acotadas no reemplazan la demostración de la sección 4.2, que vale para cadenas de cualquier longitud; la complementan comprobando que las reglas se escribieron sin errores.

**Programas de ejemplo.** Los tres programas de `ejemplos/` siguen siendo derivables y tienen exactamente un árbol de derivación en la gramática nueva:

**Tabla 33**

*Programas de ejemplo en la gramática sin recursividad por la izquierda*

| Programa | Tokens | Árboles en la gramática sin recursividad |
|---|---|---|
| `ejemplo1_produccion.cft` | 66 | 1 |
| `ejemplo2_clasificacion.cft` | 62 | 1 |
| `ejemplo3_secado.cft` | 57 | 1 |

**Cadenas de la sección 3.** Las cadenas usadas para demostrar la ambigüedad de la gramática ingenua conservan en la gramática sin recursividad el mismo número de árboles que tenían en G1:

**Tabla 34**

*Cadenas de la sección 3 en la gramática sin recursividad por la izquierda*

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

### B.2 Factorización por la izquierda

Se compararon la gramática sin recursividad por la izquierda (sección 4.3) y la factorizada (sección 7) con un analizador general por programación dinámica, que cuenta los árboles de una cadena en cualquier gramática independiente del contexto.

**Tabla 35**

*Verificación de la factorización por la izquierda*

| Prueba | Resultado |
|---|---|
| Búsqueda automática de alternativas de un mismo no terminal que puedan empezar con el mismo token | Gramática sin recursividad: 2 conflictos, `<comparacion>` (PAR_ABRE, ID, ENTERO, DECIMAL) y `<condicional>` (SI). Gramática factorizada: **0 conflictos** |
| Todas las cadenas de hasta 5 tokens desde `<expresion>`, sobre ID, SUMA, MULT, O, Y, NO, MENOR, IGUAL, PAR_ABRE y PAR_CIERRA | 111 111 cadenas, 86 aceptadas, **0 diferencias** entre las dos gramáticas y ninguna con más de un árbol |
| 1 000 programas generados al azar desde `<programa>` (hasta 67 tokens), más 2 variantes de cada uno con un token cambiado | 3 000 entradas, 1 118 aceptadas y 1 882 rechazadas, **0 diferencias** y ninguna con más de un árbol |

Los tres programas de ejemplo siguen siendo derivables con un único árbol (66, 62 y 57 tokens). Las cadenas de la sección 3 conservan su número de árboles; además, `inicio si (a) entonces fin fin` y `inicio si (a) entonces sino fin fin`, con bloques vacíos, tienen un árbol en las dos gramáticas.

### B.3 Conjuntos PRIMERO y SIGUIENTE y tabla LL(1)

Los conjuntos y la tabla se calcularon a mano, en el orden de las secciones 6.2 y 6.3, y se verificaron con un programa que aplica las reglas de las secciones 6.2.1 y 6.3.1 hasta el punto fijo. Después, la tabla se probó con un analizador predictivo que solo consulta la tabla (sección 6.8), comparado con el analizador general usado en el Apéndice B.1, que acepta cualquier gramática independiente del contexto y cuenta los árboles.

**Tabla 36**

*Verificación de la tabla LL(1)*

| Prueba | Resultado |
|---|---|
| PRIMERO, SIGUIENTE y anulables calculados por el programa frente a los de las secciones 6.1 a 6.3 | Coinciden en los 23 no terminales |
| Celdas de la tabla | 106 llenas, **0 con dos reglas** |
| Todos los programas `inicio x = w; fin` con w de hasta 5 tokens sobre ID, SUMA, MULT, O, Y, NO, MENOR, IGUAL, PAR_ABRE y PAR_CIERRA | 111 111 entradas, 86 aceptadas, **0 diferencias** entre el analizador predictivo y el general |
| 2 000 programas generados al azar desde `<programa>` (hasta 86 tokens), más 2 variantes de cada uno con un token cambiado | 6 000 entradas, 2 230 aceptadas y 3 770 rechazadas, **0 diferencias** y ninguna entrada con más de un árbol |

**Programas de ejemplo.** El analizador predictivo acepta los tres programas de `ejemplos/`, y el analizador general confirma que cada uno tiene un único árbol:

**Tabla 37**

*Programas de ejemplo con el analizador predictivo*

| Programa | Tokens | Pasos del analizador predictivo | Árboles |
|---|---|---|---|
| `ejemplo1_produccion.cft` | 66 | 241 | 1 |
| `ejemplo2_clasificacion.cft` | 62 | 197 | 1 |
| `ejemplo3_secado.cft` | 57 | 223 | 1 |

## Apéndice C. Documentos fuente en el repositorio

El repositorio público del proyecto se encuentra en https://github.com/DanielJNarvaezH/dsl-lenguajes-formales-proyecto. Los documentos de esta fase están en la carpeta `docs/fase2/`, los diagramas editables de los árboles en `docs/fase2/arboles/` y sus imágenes en `docs/fase2/arboles/img/`.

**Tabla 38**

*Documentos fuente de la Fase 2 en el repositorio*

| Tema | Documento en `docs/fase2/` | Diagramas en `docs/fase2/arboles/` | Tarea |
|---|---|---|---|
| Programa, declaración y expresiones | `gramatica_programa_expresiones.md` | `gic1_arboles_expresiones.drawio` | GIC-1 |
| Sentencias de control y salida | `gramatica_sentencias.md` | `gic2_arboles_sentencias.drawio` | GIC-2 |
| Ambigüedad y estratificación | `ambiguedad.md` | `gic3_ambiguedad.drawio` | GIC-3 |
| Eliminación de la recursividad por la izquierda | `recursividad.md` | `gic4_recursividad.drawio` | GIC-4 |
| Factorización por la izquierda | `factorizacion.md` | `gic5_factorizacion.drawio` | GIC-5 |
| PRIMERO, SIGUIENTE y tabla LL(1) | `primero_siguiente_ll1.md` y `src/parser/tabla_ll1.csv` | — | GIC-6 |
| Este documento | `documento_fase2.md` | — | DOC-3 |
