# Sustentación — Banco de preguntas y ejercicios de ingeniería inversa

**Tarea Jira:** SUS-1 — Banco de preguntas y ejercicios de ingeniería inversa
**Responsable:** Juan Diego García Albarracín
**Insumos:** documento de la Fase 1, `docs/fase2/documento_fase2.md` (DOC-3), `docs/fase3/` (LXR-1 a PAR-5, ARB-1) y el código de `src/`
**Se complementa con:** SUS-2 (simulacro de sustentación cruzada) y CIE-3 (guía de estudio)

---

## 1. Cómo usar este banco

La sustentación vale el 40 % de la nota y es **individual**: la rúbrica pide modificar la gramática o mapear errores en el autómata en vivo, con dominio conceptual, y penaliza a quien "solo explica las líneas que él/ella programó". Por eso cada uno debe poder responder todas las preguntas, no solo las de sus tareas.

- **Sección 2:** 15 preguntas (3 de expresiones regulares, 4 de AFD, 5 de gramática y 3 de código). Cada una tiene una respuesta modelo, dónde está en los documentos y una pregunta de seguimiento, que es la que suele hacer la profesora después de la primera respuesta.
- **Sección 3:** 4 ejercicios en vivo, con todos los pasos. Los cuatro **se ejecutaron sobre una copia del proyecto**: los números, las celdas y las salidas que aparecen aquí son los reales.
- **Para SUS-2:** en el simulacro, cada uno responde las preguntas y hace los ejercicios de las partes que hizo el otro. Las preguntas que cuesten se registran en Jira como tareas de repaso.

**Para practicar los ejercicios sin dañar el repositorio**, desde `dsl-lenguajes-formales`:

```
git switch -c practica/sus1
  (hacer los cambios del ejercicio y correr las pruebas)
git restore .
git switch main
git branch -D practica/sus1
```

## 2. Preguntas

### 2.1 Expresiones regulares

**Pregunta 1. ¿Qué es el alfabeto Σ de Cafetal, cuántos símbolos tiene y por qué `<=` no pertenece a Σ?**

*Respuesta.* Σ es el conjunto de caracteres individuales que pueden aparecer en un programa: Σ = L ∪ D ∪ O ∪ P ∪ B, con 26 letras minúsculas, 10 dígitos, 8 operadores (`'+'`, `-`, `'*'`, `/`, `<`, `>`, `=`, `!`), 7 de puntuación (`'('`, `')'`, `;`, `.`, `"`, `#`, `_`) y 4 blancos (espacio, `\t`, `\n`, `\r`). Los subconjuntos son disjuntos, así que |Σ| = 26 + 10 + 8 + 7 + 4 = 55. `<=` no está en Σ porque no es un carácter: es una cadena de longitud 2 de Σ\*, que el AFD reconoce como el token MENOR_IGUAL. Hay tres niveles distintos: el alfabeto (caracteres), los tokens (cadenas de Σ\* descritas por ER) y la gramática (terminales, que son los tokens, y no terminales).

*Dónde:* Fase 1, secciones "Alfabeto Σ" y "Separación entre alfabeto, léxico y gramática" (Tabla 4).

*Seguimiento:* ¿qué pasa con una `K` o una `ñ` en un programa? Respuesta: no pertenecen a Σ, no tienen columna en la matriz, así que desde q0 no hay transición y se produce un error léxico (LXR-2 lo reporta con línea y columna y sigue).

**Pregunta 2. Escriba la expresión regular de DECIMAL con la notación del curso y explique cada operador.**

*Respuesta.* `(D)+.(D)+`, donde D = `(0,1,2,3,4,5,6,7,8,9)` es la unión de los diez dígitos con coma. `(D)+` es la cerradura positiva, la única operación no primitiva permitida, que equivale a `(D)(D)*`: uno o más dígitos. El punto se concatena por yuxtaposición. En notación solo primitiva: `(D)(D)*.(D)(D)*`. Rechaza `12.` y `.5`, porque falta al menos un dígito a un lado del punto, y `1.2.3`, porque tiene un solo punto. Junto con ENTERO se factoriza por el prefijo común: `(D)+(ε,.(D)+)`.

*Dónde:* Fase 1, Tabla 6, Tabla 7 y Tabla 8.

*Seguimiento:* ¿cómo cambiaría la ER para aceptar `12.`? Respuesta: `(D)+.(D)*`. Es el ejercicio 1 de la sección 3.

**Pregunta 3. ¿Por qué en las expresiones regulares `'('`, `')'`, `'*'` y `'+'` van entre comillas simples, y qué es ε?**

*Respuesta.* En la notación del curso, los paréntesis, el asterisco, el más y la coma son **metasímbolos**: agrupan, indican cerradura o unión. Como en Cafetal también son símbolos del lenguaje, se escriben entre comillas cuando son terminales: `'+'` es el token SUMA y `(a)+` es la cerradura positiva. Cafetal no usa coma ni llaves, así que esos no chocan. ε es la cadena vacía: no es un operador, sino una de las expresiones regulares primitivas, junto con ∅ y cada símbolo de Σ.

*Dónde:* Fase 1, "Convención de notación" y "Uso de ε".

*Seguimiento:* ¿por qué `%` no necesitaría comillas si se agregara? Respuesta: porque no es un metasímbolo de la notación (ejercicio 2).

### 2.2 Autómata finito determinista

**Pregunta 4. ¿Cómo se pasa de una expresión regular al grafo del AFD?**

*Respuesta.* La concatenación `ab` se convierte en estados en serie; la unión `a,b`, en varias transiciones que salen del mismo estado; la cerradura `(X)*`, en un lazo con X sobre el estado actual; y la cerradura positiva `(X)+`, en una transición con X a un estado nuevo más un lazo con X sobre él, porque `(X)+ = (X)(X)*`. Que el estado del lazo sea de aceptación no depende del operador, sino de lo que sigue en la ER: en ID el lazo está al final, así que q64 acepta; en CADENA todavía falta la comilla de cierre, así que q68 no acepta.

*Dónde:* Fase 1, Tabla 9.

*Seguimiento:* dibuje en el tablero el AFD de `(D)+(ε,.(D)+)` (estados q65, q66 y q67 del AFD global).

**Pregunta 5. ¿Cómo se obtuvo el AFD global y por qué los estados intermedios de las palabras reservadas aceptan ID?**

*Respuesta.* Se unieron los estados iniciales de los 8 AFD parciales en un único q0. El resultado era no determinista solo con las letras: desde q0, la `i` llevaba tanto al camino de `inicio` como al estado de ID. Se aplicó la construcción de subconjuntos (AFN a AFD). Cada estado del camino de una palabra reservada representa a la vez "voy leyendo la palabra" y "voy leyendo un identificador", así que acepta ID, y toda letra, dígito o `_` que no continúe la palabra lleva a q64. Por eso `dat` (q12), `datos` (q64) y `entonces2` son ID, y `dato` (q13) es DATO. La prioridad de la palabra reservada sobre el ID queda dentro del AFD, no en el código.

*Dónde:* Fase 1, "Unificación en el AFD global" y Tabla 11.

*Seguimiento:* ¿cuántos estados, de aceptación y transiciones tiene? Respuesta: 72 estados (q0–q71), 68 de aceptación (no aceptan q0, q59, q66 y q68) y 1 997 transiciones de 3 960 celdas.

**Pregunta 6. El AFD no tiene estado sumidero. ¿Por qué sigue siendo correcto y cómo se decide si una celda vacía es un error?**

*Respuesta.* La función δ es parcial: una celda vacía significa que δ(q, a) no está definida, es decir, rechazo. Es equivalente al AFD completo que se obtiene agregando un estado q∅ de no aceptación, con todas las celdas vacías dirigidas a él y un lazo con los 55 símbolos: los dos reconocen el mismo lenguaje. En el analizador léxico, una celda vacía tiene tres casos (Tabla 17 de la Fase 1):

- q ∈ F: el lexema terminó; se emite el token de q y se sigue desde a (`si(` emite SI).
- q ∉ F, pero antes se visitó un estado de aceptación: se retrocede a ese estado (`12.x` llega a q66, retrocede a q65 y emite ENTERO `12`).
- q ∉ F y no hubo aceptación: error léxico en el primer símbolo del lexema (`!x`, error en `!`).

*Dónde:* Fase 1, "Rechazo sin estado sumidero"; `docs/fase3/errores_lexicos.md`, sección 2.

*Seguimiento:* después de un error, ¿desde dónde sigue el análisis? Respuesta: desde el símbolo siguiente (LXR-2). Saltar hasta otro punto, por ejemplo hasta el fin de línea en una cadena sin cerrar, exigiría que el código supiera que q68 "significa" cadena abierta, y eso sería una regla escrita a mano fuera de la tabla.

**Pregunta 7. Haga la traza de `sino` y de `si(` sobre la matriz.**

*Respuesta.* `sino`: q0 →s→ q14 →i→ q15 (acepta SI) →n→ q16 →o→ q17. Termina en q17 ∈ F: SINO. En q15 ya se había aceptado SI, pero por la regla del **lexema más largo** se sigue mientras haya transición. `si(`: q0 →s→ q14 →i→ q15; δ(q15, `(`) está vacía y q15 ∈ F, así que se emite SI y se empieza de nuevo en q0 con `(`, que lleva a q61 (PAR_ABRE).

*Dónde:* Fase 1, Traza 1 y Tablas 13 a 16.

*Seguimiento:* traza de `siembra`. Respuesta: q14, q15, y con `e` va a q64 (ID); el resto de letras se queda en q64: ID.

### 2.3 Gramática

**Pregunta 8. Demuestre que la gramática `E → E + E | E * E | id` es ambigua.**

*Respuesta.* Basta una cadena con dos árboles de derivación, o con dos derivaciones más a la izquierda distintas. Para `id + id * id`: una derivación empieza con `E ⇒ E + E` (la suma queda en la raíz y agrupa `id + (id * id)`), y la otra con `E ⇒ E * E` (agrupa `(id + id) * id`). Las dos llegan a la misma cadena y difieren desde el primer paso. La diferencia cambia el resultado: con `kilos = 100`, `kilos + 25 * 2` vale 150 o 250 según el árbol.

*Dónde:* `documento_fase2.md`, sección 3.2.

*Seguimiento:* ¿cuántos árboles tiene `a + b + c + d + e` en esa gramática? Respuesta: 14, el número de Catalan C₄ (sección 3.2, Tabla 7).

**Pregunta 9. ¿Cómo fija la gramática de Cafetal la precedencia y la asociatividad? ¿Por qué `a < b < c` no es válida?**

*Respuesta.* Hay un no terminal por nivel de precedencia (`<expresion>` para `o`, `<conjuncion>` para `y`, `<negacion>` para `no`, `<comparacion>` para los relacionales, `<suma>` para `+ -`, `<termino>` para `* /` y `<factor>` para los paréntesis y operandos), y cada nivel solo usa el siguiente como operando. Así, un operador de mayor precedencia siempre queda más abajo en el árbol. La asociatividad la fija la forma de la regla: `<suma> ::= <suma> RESTA <termino>` agrupa por la izquierda. `<comparacion> ::= <suma> <op_rel> <suma>` no es recursiva: a cada lado del relacional solo cabe una `<suma>`, que no contiene relacionales sin paréntesis, así que `a < b < c` no es derivable.

*Dónde:* `documento_fase2.md`, secciones 2.2, 3.3 y 3.4.

*Seguimiento:* ¿cómo se demuestra que la gramática estratificada no es ambigua? Respuesta: con el Lema 1 (cada no terminal solo tiene a nivel cero los operadores de su nivel o mayores) y la proposición de la sección 3.4: el operador de la raíz siempre es el último de menor precedencia a nivel cero, así que la partición es única.

**Pregunta 10. Elimine la recursividad por la izquierda de `<suma>` y demuestre que no cambia el lenguaje.**

*Respuesta.* Con la fórmula `A ::= A α | β ⇒ A ::= β A'`, `A' ::= α A' | ε`, donde α = `(SUMA <termino>, RESTA <termino>)` y β = `<termino>`:

```
R9   <suma>       ::= <termino> <suma_prima>
R10  <suma_prima> ::= SUMA <termino> <suma_prima>
R11  <suma_prima> ::= RESTA <termino> <suma_prima>
R12  <suma_prima> ::= ε
```

Antes, cada aplicación de la regla recursiva agrega un α a la derecha y se termina con β: las formas son (β)(α)\*. Después, `<suma_prima>` genera (α)\*, y `<suma>` genera (β)(α)\*. Son el mismo conjunto. Se usan dos α porque la concatenación se distribuye sobre la unión: `A α₁ , A α₂ = A (α₁,α₂)`.

*Dónde:* `documento_fase2.md`, secciones 4.2 y 4.3.

*Seguimiento:* ¿por qué hay que eliminarla? Respuesta: la función de `<suma>` se llamaría a sí misma sin consumir tokens (recursión infinita), y además no podría elegir regla con un solo token. ¿Y se pierde la asociatividad por la izquierda? Respuesta: el árbol se inclina a la derecha, pero los operadores quedan en la cadena de `<suma_prima>` en el orden del texto; la agrupación por la izquierda se recupera recorriéndola de izquierda a derecha.

**Pregunta 11. ¿Por qué se factorizó el condicional? ¿La factorización quita ambigüedad?**

*Respuesta.* C1 y C2 empezaban con el mismo prefijo `SI PAR_ABRE <expresion> PAR_CIERRA ENTONCES <sentencias>`; al leer SI, el analizador no podía saber si más adelante vendría un `sino`. Con `A ::= α β₁ | α β₂ ⇒ A ::= α A'`, `A' ::= β₁ | β₂` queda F4 para el prefijo, y la elección entre F5 (FIN) y F6 (SINO) se hace al terminar el bloque, con un solo token. **No quita ambigüedad:** la gramática ya no era ambigua (el `fin` resuelve el sino colgante); lo que resuelve es un problema de **determinismo**. El lenguaje no cambia: (α)(β₁,β₂) = α β₁ , α β₂ por la distribución.

*Dónde:* `documento_fase2.md`, sección 5.

*Seguimiento:* ¿cómo resuelve Cafetal el sino colgante? Respuesta: dentro de la gramática, con el delimitador `fin`: las dos lecturas son dos textos distintos (`… sino … fin fin` o `… fin sino … fin`), cada uno con un solo árbol (sección 3.5, Lema 2).

**Pregunta 12. ¿Qué son PRIMERO y SIGUIENTE, y por qué una tabla LL(1) sin conflictos demuestra que la gramática no es ambigua?**

*Respuesta.* PRIMERO(α) son los tokens con que puede empezar lo que deriva α; SIGUIENTE(A), los que pueden venir justo después de A. La regla A ::= α va en la celda M[A, t] para cada t de PRIMERO(α) y, si α deriva ε, también para cada t de SIGUIENTE(A). Ejemplo: SIGUIENTE(`<sentencias>`) = {FIN, SINO}, así que R2 (`<sentencias> ::= ε`) se aplica con FIN o SINO, y no choca con R1 porque ninguna sentencia empieza con FIN ni SINO. Si dos derivaciones más a la izquierda de la misma cadena difirieran, en el primer paso distinto las dos reglas estarían en la misma celda M[A, t], con t el siguiente token; como ninguna celda tiene dos reglas, eso es imposible. La tabla de Cafetal tiene 106 celdas llenas y ninguna con dos reglas.

*Dónde:* `documento_fase2.md`, secciones 6.3, 6.5 y 6.7.

*Seguimiento:* ¿por qué `a < b < c` se rechaza justo en el segundo `<`? Respuesta: después de `a < b`, `<comparacion_prima>` ya se usó, y en la cima queda `<conjuncion_prima>`; la celda M[`<conjuncion_prima>`, MENOR] está vacía (sección 6.6.1).

### 2.4 Código

**Pregunta 13. ¿Cómo reconoce los tokens el analizador léxico sin el módulo `re` y sin un `if` por token?**

*Respuesta.* `lexer.py` carga `tabla_afd.csv` (la matriz de la Fase 1) y la recorre: desde q0, avanza con δ(q, a) mientras la celda no esté vacía, recuerda el último estado de aceptación y, cuando ya no puede avanzar, retrocede a ese estado y emite su token (columna `token` del CSV). Toda decisión sale de la tabla: ni siquiera la prioridad de palabras reservadas está en el código. Una prueba revisa el código fuente y falla si importa `re` o si compara con un nombre de token o un lexema. Si se cambia el lenguaje, se cambia la matriz y el código no cambia (ejercicios 1 y 2).

*Dónde:* `docs/fase3/lexer.md`, secciones 1 y 3.

*Seguimiento:* ¿cómo se cuentan la línea y la columna? Respuesta: desde 1; cada carácter avanza una columna, y `\n`, `\r` o la pareja `\r\n` pasan a la línea siguiente.

**Pregunta 14. ¿Cómo decide el analizador sintáctico qué regla aplicar?**

*Respuesta.* Es descendente recursivo: una función de Python por no terminal, con el mismo nombre sin `< >`. Cada función hace siempre lo mismo: `predecir` consulta la tabla LL(1) (`tabla_ll1.csv`) con su no terminal y el token actual; crea su nodo con la regla obtenida; recorre el lado derecho de la regla (los terminales con `emparejar`, los no terminales llamando a su función y ε con `Nodo.vacio()`); y devuelve el nodo. Ninguna función pregunta por el tipo del token: solo compara la etiqueta de regla que devolvió la tabla, y una prueba lo verifica sobre el código. Encima de cada función está, como comentario, la regla BNF que implementa.

*Dónde:* `docs/fase3/parser.md`, secciones 1, 3 y 8.

*Seguimiento:* muestre en el código la función de `<condicional_prima>` y explique por qué el `emparejar("FIN")` está fuera del `if` (F5 y F6 terminan con FIN).

**Pregunta 15. ¿Qué hace el programa con un archivo que tiene errores?**

*Respuesta.* `main.py` recibe la ruta del archivo con `argparse` (sin rutas fijas) y:

1. Ejecuta el lexer, que no se detiene en el primer error: registra cada error léxico con símbolo, línea y columna y sigue desde el símbolo siguiente (LXR-2).
2. Ejecuta el parser aunque haya errores léxicos, porque el lexer siempre entrega una lista válida de tokens. El parser se recupera de cada error sintáctico en modo pánico, sincronizándose con los conjuntos SIGUIENTE (PAR-4), para listar varios errores.
3. Si hubo algún error, muestra los léxicos y después los sintácticos, sin el árbol, y termina con código 1. Si no hubo errores, muestra el árbol de derivación (ARB-1) y termina con código 0.

*Dónde:* `docs/fase3/errores_lexicos.md`, `docs/fase3/parser.md` (sección de PAR-4) y `docs/fase3/main.md`.

*Seguimiento:* ¿por qué los errores léxicos se listan primero? Respuesta: un símbolo con error falta en la lista de tokens y puede causar un error sintáctico que en realidad es consecuencia del léxico; listándolos primero se ve el origen.

## 3. Ejercicios en vivo

Los cuatro ejercicios recorren el camino completo de un cambio: expresión regular → AFD → matriz → CSV → código, y BNF → PRIMERO/SIGUIENTE → tabla LL(1) → función del parser. Los ejercicios 1 y 2 son del lexer ("modificar un token y rastrearlo en la matriz"), y los ejercicios 3 y 4, de la gramática ("agregar una regla a la BNF y actualizar su función"). El ejercicio 4 usa el token del ejercicio 2.

Se ejecutaron sobre una copia del proyecto: los conteos, las trazas y las salidas son los reales. En cada uno se indica qué pruebas del repositorio dejarían de pasar, porque verifican el estado actual del lenguaje: actualizarlas es parte del cambio.

### 3.1 Ejercicio 1 — Aceptar `12.` como número decimal

**Enunciado.** Hoy `12.` no es un token: se emite ENTERO `12` y el punto queda como error léxico. Se pide que `12.` sea un DECIMAL.

**Paso 1, expresión regular.** DECIMAL pasa de `(D)+.(D)+` a `(D)+.(D)*`: después del punto, cero o más dígitos. La factorizada de los números pasa de `(D)+(ε,.(D)+)` a `(D)+(ε,.(D)*)`.

**Paso 2, AFD.** No hay estados ni transiciones nuevos. Lo que cambia es que **q66 pasa a ser de aceptación** y devuelve DECIMAL: con `(D)*`, la cadena "dígitos y punto" ya es un lexema completo. En el grafo, q66 pasa a tener doble círculo con la etiqueta DECIMAL. F pasa de 68 a 69 estados; las transiciones siguen siendo 1 997.

**Paso 3, matriz.** Una sola celda: en la Tabla 16 de la Fase 1, fila q66, columna Token, de vacío a DECIMAL, y la fila se marca con `*`. En `src/lexer/tabla_afd.csv`, la última columna de la fila `q66` pasa de vacía a `DECIMAL`.

**Paso 4, código.** Ninguno: el lexer lee la tabla.

**Comprobación.**

| Entrada | Antes | Después |
|---|---|---|
| `x = 12.;` | ID, ASIGNACION, ENTERO `12`, PUNTO_COMA y error léxico en `.` (columna 7) | ID, ASIGNACION, DECIMAL `12.`, PUNTO_COMA, sin errores |
| `12.x` | ENTERO `12`, error en `.`, ID `x` | DECIMAL `12.`, ID `x` |
| `1.5` | DECIMAL `1.5` | DECIMAL `1.5` (igual) |

Traza de `12.` después del cambio: q0 →1→ q65 →2→ q65 →.→ q66, y se acaba el texto (o llega `;`, que no tiene transición desde q66). Ahora q66 ∈ F, así que se emite DECIMAL `12.` sin retroceder. Antes, q66 ∉ F obligaba a retroceder a q65.

**Qué hay que actualizar además.** En la Fase 1: la ER de la Tabla 6, la factorizada de la Tabla 7, el ejemplo `12.` de la Tabla 8, F y la Tabla 11, las Tablas 16, 18 y 19 (q66 deja de ser de no aceptación). Pruebas que cambian: en `test_lexer.py`, `test_estados_de_aceptacion` (68 → 69, y q66 sale del conjunto que no acepta) y `test_retroceso_al_ultimo_estado_de_aceptacion` (`12.x` ya no tiene error); en `test_errores_lexicos.py`, los errores esperados de `lexico2_simbolos_sin_token.cft` (desaparecen los de `12.` y `3.x`) y `test_retroceso_y_error`.

**Preguntas probables.** ¿Y si se pidiera aceptar `.5`? Entonces hace falta una transición nueva δ(q0, `.`) hacia un estado nuevo que espere dígitos, y la ER sería `(D)+.(D)*, .(D)+`. ¿Por qué no cambió ninguna transición? Porque `(D)*` y `(D)+` producen el mismo lazo sobre q67; lo único que cambia es si el estado anterior al lazo ya es un lexema completo (pregunta 4).

### 3.2 Ejercicio 2 — Agregar el operador módulo `%`

**Enunciado.** Agregar el token MOD, con lexema `%`, por ejemplo para `resto = kilos % 50;`.

**Paso 1, alfabeto.** `%` se agrega a O: |O| = 9 y |Σ| = 56. Como K = Σ − {\n, \r}, K también crece (de 53 a 54), así que los comentarios podrán contener `%`. C, el contenido de las cadenas, no cambia: es un conjunto definido aparte.

**Paso 2, expresión regular y catálogo.** MOD = `%`, sin comillas, porque `%` no es un metasímbolo. Código del catálogo: 34, a continuación de DIV (33).

**Paso 3, AFD.** Un estado nuevo, **q72**, de aceptación, que devuelve MOD, y dos transiciones:

- δ(q0, `%`) = q72;
- δ(q70, `%`) = q70: el lazo del comentario es con K, y K ahora incluye `%`.

Q pasa a 73 estados, F a 69 y las transiciones de 1 997 a 1 999.

**Paso 4, matriz y CSV.** Una columna nueva `%` (en el CSV, en la cabecera; su posición no importa, porque el lexer lee los símbolos de la cabecera), con q72 en la fila q0 y q70 en la fila q70, y una fila nueva `q72` con todas las celdas vacías y el token `MOD`.

**Paso 5, código.** En `src/lexer/tokens.py`, agregar `"MOD": 34` al diccionario CODIGOS. `lexer.py` no cambia. Si se olvida este paso, el lexer no arranca: al cargar la tabla, `TablaAFD` valida que todo token esté en el catálogo y lanza `ErrorTabla: el token 'MOD' no está en el catálogo`.

**Comprobación.**

| Entrada | Antes | Después |
|---|---|---|
| `resto = kilos % 50;` | Error léxico: `%` no pertenece al alfabeto Σ | ID, ASIGNACION, ID, MOD, ENTERO, PUNTO_COMA |
| `a%2` | ID, error en `%`, ENTERO | ID, MOD, ENTERO |
| `# 10 % de humedad` | Error: el comentario se corta en `%` | Un solo COMENTARIO (se descarta) |
| `"cien %"` | Errores | Sigue con errores: `%` no está en C |

Traza de `kilos % 50`: `kilos` llega a q64 (ID); δ(q64, espacio) está vacía y q64 ∈ F, así que se emite ID; el espacio va a q71 (BLANCO); `%` va de q0 a q72, y δ(q72, espacio) está vacía con q72 ∈ F: MOD; `50` va a q65: ENTERO.

**Error típico.** Si se olvida δ(q70, `%`), `# 10 % de humedad` se reconoce como COMENTARIO `# 10 ` y después llegan al parser MOD, ID, ID, que dan un error sintáctico en un comentario. Es un buen ejemplo de por qué un cambio en Σ obliga a revisar K.

**Qué hay que actualizar además.** En la Fase 1: Σ, O, K, la tabla de tokens, el grafo y la matriz. Pruebas que cambian: en `test_lexer.py`, `test_dimensiones` (72 → 73 estados, 55 → 56 símbolos), `test_estados_de_aceptacion` (68 → 69), `test_transiciones` (1 997 → 1 999) y `test_aparecen_las_32_categorias` (MOD no aparece en los programas de ejemplo). Con el AFD nuevo, MOD llega al parser, pero la gramática todavía no lo acepta: eso es el ejercicio 4.

### 3.3 Ejercicio 3 — Declaración sin valor inicial: `dato x;`

**Enunciado.** Permitir declarar una variable sin asignarle un valor, como `dato humedad;`.

**Paso 1, regla BNF.** La regla natural es `<declaracion> ::= DATO ID PUNTO_COMA`. Pero comparte el prefijo `DATO ID` con D1, así que la gramática dejaría de ser LL(1): al leer DATO no se podría elegir. Hay que **factorizar** (sección 5 de la Fase 2), con α = DATO ID, β₁ = ASIGNACION `<expresion>` PUNTO_COMA y β₂ = PUNTO_COMA:

```
D1   <declaracion>       ::= DATO ID <declaracion_prima>
D2   <declaracion_prima> ::= ASIGNACION <expresion> PUNTO_COMA
D3   <declaracion_prima> ::= PUNTO_COMA
```

El lenguaje de `<declaracion>` es (DATO ID)(ASIGNACION `<expresion>` PUNTO_COMA , PUNTO_COMA): la declaración de antes o la nueva.

**Paso 2, PRIMERO y SIGUIENTE.** PRIMERO(`<declaracion_prima>`) = {ASIGNACION, PUNTO_COMA}. SIGUIENTE(`<declaracion_prima>`) = SIGUIENTE(`<declaracion>`) = {FIN, SINO, DATO, ID, MOSTRAR, SI, MIENTRAS}. SIGUIENTE(`<expresion>`) no cambia: el PUNTO_COMA que antes aportaba D1 ahora lo aporta D2.

**Paso 3, tabla LL(1).** Una fila nueva, `<declaracion_prima>`, con dos celdas: M[`<declaracion_prima>`, ASIGNACION] = D2 y M[`<declaracion_prima>`, PUNTO_COMA] = D3. La celda M[`<declaracion>`, DATO] sigue siendo D1, aunque D1 tiene otro lado derecho. Las dos alternativas tienen conjuntos de predicción disjuntos, así que la gramática sigue siendo LL(1). En `src/parser/tabla_ll1.csv`: agregar la fila `<declaracion_prima>` con D2 en la columna ASIGNACION y D3 en la columna PUNTO_COMA.

**Paso 4, funciones del parser.** En `src/parser/parser.py` se modifica `declaracion` y se agrega `declaracion_prima`, con el mismo patrón de `condicional_prima`:

```python
# D1   <declaracion> ::= DATO ID <declaracion_prima>
def declaracion(self):
    """D1: <declaracion> ::= DATO ID <declaracion_prima>"""
    nodo = Nodo.no_terminal("<declaracion>", self.predecir("<declaracion>"))
    nodo.agregar(self.emparejar("DATO"))
    nodo.agregar(self.emparejar("ID"))
    nodo.agregar(self.declaracion_prima())
    return nodo

# D2   <declaracion_prima> ::= ASIGNACION <expresion> PUNTO_COMA
# D3   <declaracion_prima> ::= PUNTO_COMA
def declaracion_prima(self):
    """D2: <declaracion_prima> ::= ASIGNACION <expresion> PUNTO_COMA | D3: PUNTO_COMA"""
    regla = self.predecir("<declaracion_prima>")
    nodo = Nodo.no_terminal("<declaracion_prima>", regla)
    if regla == "D2":
        nodo.agregar(self.emparejar("ASIGNACION"))
        nodo.agregar(self.expresion())
    nodo.agregar(self.emparejar("PUNTO_COMA"))     # D2 y D3 terminan con PUNTO_COMA
    return nodo
```

Si la recuperación de errores de PAR-4 lee los conjuntos SIGUIENTE de un archivo, hay que agregar en él la fila de `<declaracion_prima>` con los 7 tokens del paso 2.

**Comprobación.**

| Entrada | Resultado |
|---|---|
| `inicio dato x; fin` | Correcto. Reglas: P1, R1, P4, D1, D3, R2 |
| `inicio dato x = 1; fin` | Correcto. Reglas: P1, R1, P4, D1, D2, R3 … R5, R2 |
| `inicio dato x 1; fin` | Error en la columna 15: se esperaba ASIGNACION o PUNTO_COMA y se encontró `1` (ENTERO) |
| `inicio dato x = ; fin` | Error en la columna 17: se esperaba NO, ID, ENTERO, DECIMAL o PAR_ABRE y se encontró `;` |

El mensaje del tercer caso sale directamente de la fila nueva de la tabla: los esperados son las celdas llenas de `<declaracion_prima>`.

**Qué hay que actualizar además.** En la Fase 2: la gramática final, PRIMERO, SIGUIENTE, la tabla de predicción y la tabla LL(1). Pruebas que cambian: cada declaración tiene ahora un nodo más (`<declaracion_prima>`), así que las cantidades de reglas de los ejemplos pasan de 174, 134 y 165 a 180, 136 y 167 (`test_parser_sentencias.py`); en `test_parser_expresiones.py`, `test_dimensiones` (23 → 24 no terminales y 106 → 108 celdas); el diccionario GRAMATICA de las pruebas de PAR-3 y TST-1; y los árboles esperados de TST-1, que se regeneran con `main.py --salida` (sección 5 de `pruebas_validos.md`).

### 3.4 Ejercicio 4 — El operador `%` en las expresiones

**Enunciado.** Con el token MOD del ejercicio 2, permitir `%` en las expresiones, con la misma precedencia y asociatividad de `*` y `/`.

**Paso 1, regla BNF.** En la gramática inicial sería una tercera alternativa recursiva de `<termino>`: `<termino> ::= <termino> MOD <factor>`. Al eliminar la recursividad por la izquierda, es un tercer α en la fórmula, α₃ = MOD `<factor>` (sección 4.2 de la Fase 2), y produce una regla nueva de `<termino_prima>`:

```
R17  <termino_prima> ::= MOD <factor> <termino_prima>
```

El lenguaje de `<termino>` pasa a ser (`<factor>`)(MULT `<factor>`, DIV `<factor>`, MOD `<factor>`)\*.

**Paso 2, PRIMERO y SIGUIENTE.** MOD entra en PRIMERO(`<termino_prima>`) y en SIGUIENTE(`<factor>`). Nada más cambia, porque `<factor>` no tiene regla ε.

**Paso 3, tabla LL(1).** Una columna nueva, MOD, con una sola celda: M[`<termino_prima>`, MOD] = R17. No hay conflicto con R16 (ε), porque MOD no está en SIGUIENTE(`<termino_prima>`). En `src/parser/tabla_ll1.csv`: agregar la columna `MOD` (después de DIV) con R17 en la fila `<termino_prima>`.

**Paso 4, función del parser.** **Una línea.** `termino_prima` ya trata MULT y DIV con el diccionario OPERADOR_TERMINO, que dice qué terminal pide cada regla; basta agregar R17:

```python
# R17  <termino_prima> ::= MOD <factor> <termino_prima>
OPERADOR_TERMINO = {"R14": "MULT", "R15": "DIV", "R17": "MOD"}
```

Además se agrega R17 al comentario y al docstring de la función: la prueba de PAR-2 exige que el docstring nombre todas las reglas de la tabla. El cuerpo de la función no cambia, porque la tabla decide la regla y el diccionario solo dice qué terminal emparejar. Es la mejor demostración de que el parser está dirigido por la tabla.

**Comprobación.** `inicio r = a % 2 * b; fin` es correcto, con las reglas P1, R1, P5, A1, R3, R6, E6, F1, R9, R13, E22, **R17**, E23, R14, E22, R16, R12, F3, R8, R5, R2. El `%` y el `*` quedan en la misma cadena de `<termino_prima>`, en el orden del texto, así que se agrupa `(a % 2) * b`, por la izquierda. `inicio r = a % ; fin` da error: después de MOD se espera ID, ENTERO, DECIMAL o PAR_ABRE.

**Verificación de los ejercicios 3 y 4 juntos.** Con los dos cambios, la gramática tiene 49 reglas y la tabla 109 celdas. Se recalcularon PRIMERO, SIGUIENTE y la tabla con el mismo procedimiento de la sección 6 de la Fase 2: **0 conflictos**, así que la gramática sigue siendo LL(1) y no ambigua.

**Qué hay que actualizar además.** En la Fase 2: la regla nueva en las secciones 4 y 7, PRIMERO, SIGUIENTE, la tabla de predicción y la tabla LL(1). Pruebas que cambian: en `test_parser_expresiones.py`, `test_dimensiones` (31 → 32 terminales y una celda más).

## 4. Resumen de los ejercicios

| Ejercicio | Expresión regular o BNF | AFD o tabla LL(1) | Código |
|---|---|---|---|
| 1. `12.` como DECIMAL | `(D)+.(D)*` | q66 pasa a ser de aceptación (una celda) | Ninguno |
| 2. Token `%` | MOD = `%`; `%` ∈ O y en K | Estado q72, columna `%`, δ(q0, `%`) y δ(q70, `%`) | `"MOD": 34` en `tokens.py` |
| 3. `dato x;` | Factorización: D1, D2, D3 | Fila `<declaracion_prima>` (dos celdas) | `declaracion` y `declaracion_prima` |
| 4. `%` en expresiones | R17, tercer α de `<termino>` | Columna MOD (una celda) | Una entrada en OPERADOR_TERMINO |

En los cuatro casos, el lexer y el parser cambian poco o nada, porque las decisiones están en las tablas: esa es la respuesta corta a cualquier pregunta sobre hardcodeo.
