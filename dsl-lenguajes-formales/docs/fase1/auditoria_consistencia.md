# Fase 1 — Auditoría de consistencia: ER, AFD y matriz

**Tarea Jira:** DOC-2 — Auditoría de consistencia ER, AFD y matriz
**Responsable:** Juan Diego García Albarracín
**Documento auditado:** `Fase1_Cafetal.docx` (versión APA 7 para la entrega ENT-1)
**Referencia verificada:** `src/lexer/tabla_afd.csv` y `afd/afd3_global.drawio` (cruzados en AFD-4: 0 diferencias)

## 1. Objetivo

La rúbrica califica como **insuficiente** el modelamiento léxico cuando "el autómata no coincide con las expresiones regulares". Esta auditoría comprueba, antes de exportar el documento final, que:

1. cada expresión regular (ER) corresponde exactamente a los caminos del AFD que terminan en el estado de aceptación de su token;
2. la matriz de transiciones del documento coincide celda a celda con la matriz verificada;
3. el grafo del documento coincide con la matriz;
4. las cifras, trazas y programas citados en el texto son coherentes con lo anterior.

## 2. Método

Las comprobaciones se hicieron por programa, leyendo directamente el contenido del `.docx` (tablas, texto e imágenes), para evitar errores de revisión manual.

| Comprobación | Cómo se hizo |
|---|---|
| ER ↔ AFD | Cada ER de la tabla de tokens se convirtió en un autómata (construcción de Thompson y de subconjuntos, con la notación del curso: coma = unión, yuxtaposición = concatenación, `( )*`, `( )+`, comillas simples para `'(' ')' '*' '+'`). Luego se comparó su lenguaje con el conjunto de cadenas que el AFD global lleva desde q0 hasta un estado de aceptación de ese token, recorriendo el producto de ambos autómatas. Si los lenguajes difieren, el recorrido entrega una cadena de contraejemplo. |
| Expresiones auxiliares | Se comprobó que L, D, C y K, escritas como uniones, generan exactamente los conjuntos definidos en el alfabeto. |
| ER factorizadas | Se comparó cada ER factorizada con su equivalente sin ε. |
| Matriz | Se leyeron las 4 tablas de la matriz (72 filas × 34 columnas) y se comparó cada celda, la marca de cada estado (→, *) y la columna Token con la matriz verificada. |
| Agrupación de columnas | Se comprobó que todos los símbolos de L₁, D y {\n, \r} tienen la misma transición en los 72 estados. |
| Grafo | Se revisó la imagen del grafo incrustada en el documento contra la matriz, buscando flechas faltantes o etiquetas incorrectas. |
| Texto | Se verificaron las cifras citadas, cada transición escrita en las trazas, y los programas del Apéndice A (contenido y conteo de tokens con el AFD). |

## 3. Resultados

### 3.1 Expresiones regulares contra el AFD

| Token | ER | Resultado |
|---|---|---|
| INICIO, FIN, DATO, SI, ENTONCES, SINO, MIENTRAS, HACER, MOSTRAR, Y, O, NO | Concatenación del lexema | Coinciden (12 de 12) |
| ID | (L)(L,D,_)* | Coincide, excepto las 12 palabras reservadas, que el AFD clasifica como su palabra reservada por la regla de prioridad |
| ENTERO | (D)+ | Coincide |
| DECIMAL | (D)+.(D)+ | Coincide |
| CADENA | "(C)*" | Coincide |
| SUMA, RESTA, MULT, DIV | '+', -, '*', / | Coinciden |
| MENOR, MAYOR, MENOR_IGUAL, MAYOR_IGUAL, IGUAL, DIFERENTE, ASIGNACION | <, >, <=, >=, ==, !=, = | Coinciden |
| PAR_ABRE, PAR_CIERRA, PUNTO_COMA | '(', ')', ; | Coinciden |
| COMENTARIO | #(K)* | Coincide |
| BLANCO | (␣,\t,\n,\r)+ | Coincide |

**Resultado: 32 de 32 tokens coinciden.** Ningún recorrido produjo un contraejemplo.

| Otras comprobaciones | Resultado |
|---|---|
| C = L ∪ D ∪ {_, ␣} (38 símbolos) | Correcto |
| K = Σ − {\n, \r} (53 símbolos) | Correcto |
| `inicio, …, si(ε,no), …, m(ientras,ostrar), …` = las 12 palabras sin ε | Equivalentes |
| `<(ε,=)`, `>(ε,=)`, `=(ε,=)` = `<,<=`, `>,>=`, `=,==` | Equivalentes |
| `(D)+(ε,.(D)+)` = `(D)+, (D)+.(D)+` | Equivalentes |

### 3.2 Matriz de transiciones

| Comprobación | Resultado |
|---|---|
| Celdas comparadas (72 estados × 34 columnas) | 2 448 |
| Celdas distintas de la matriz verificada | **0** |
| Estados en orden q0–q71, con → en q0 y * en los 68 estados de F | Correcto |
| Columna Token (68 estados de aceptación, nombres del catálogo) | Correcta |
| Agrupación de columnas L₁, D y {\n, \r} | Consistente en los 72 estados |

### 3.3 Grafo contra la matriz

El grafo editable del repositorio (`afd/afd3_global.drawio`) ya se había cruzado con la matriz en AFD-4, con 0 diferencias. Sin embargo, **la imagen incrustada en el Word no coincidía**:

| Transición en la matriz | En la imagen del Word |
|---|---|
| δ(q65, .) = q66 | Aparecía la etiqueta `.`, pero sin flecha |
| δ(q66, D) = q67 | Aparecía la etiqueta `D`, pero sin flecha |
| δ(q57, =) = q58 | Aparecía la etiqueta `=`, pero sin flecha |

La imagen del Word era una copia de baja resolución (1 244 × 2 047 px) tomada de un PDF, y al reducirla se perdieron esas líneas horizontales delgadas. Leído al pie de la letra con la convención "toda transición no dibujada significa rechazo", el grafo rechazaba `11.5` y `==`, que la matriz acepta.

### 3.4 Coherencia del texto

| Comprobación | Resultado |
|---|---|
| \|Σ\| = 55, \|Q\| = 72, \|F\| = 68, 34 columnas, 3 960 celdas, 1 997 transiciones, 1 738 retornos a ID, 32 categorías | Coherentes en todo el documento |
| Nombres de token antiguos (MAS, MENOS, POR, ASIG) | No aparecen |
| Transiciones escritas en las trazas | Todas existen en la matriz |
| Programas del Apéndice A | Idénticos a los de `ejemplos/` |
| Análisis léxico de los 3 programas | 0 errores; 66, 62 y 57 tokens, como dice la tabla de resultados |
| Citas y referencias | Las 3 referencias se citan en el texto y las 3 citas tienen su referencia |

## 4. Correcciones registradas

| # | Hallazgo | Corrección | Estado |
|---|---|---|---|
| 1 | La imagen del grafo global en el Word había perdido 3 flechas (sección 3.3) | Se reemplazó por el PNG original de alta resolución (3 116 × 5 128 px) de `afd/img/afd_global.drawio.png`, el mismo que se verificó en AFD-4. Se comprobó que las 3 flechas se ven en el documento | Corregido |
| 2 | El índice del Word tiene los números de página escritos a mano | Revisarlos en Word justo antes de exportar, o reemplazarlo por una tabla de contenido automática (Referencias → Tabla de contenido) y actualizarla. No se pudo comprobar aquí porque la paginación depende del programa con que se abra el archivo | Pendiente antes de exportar |

**Observación sin corrección.** Las figuras de los AFD parciales (Figuras 1 a 8) conservan el texto "inicio" en la flecha inicial, que en el grafo global se retiró porque coincide con una palabra reservada. No afecta la consistencia, porque son las figuras de la etapa de construcción; se deja registrado por si se pregunta en la sustentación.

## 5. Conclusión

Las 32 expresiones regulares corresponden exactamente a los caminos del AFD, y la matriz del documento coincide celda a celda con la matriz verificada (2 448 celdas, 0 diferencias). La única inconsistencia era de la imagen del grafo en el Word, no del autómata, y quedó corregida. Con la revisión del índice, el documento queda listo para exportar a PDF y entregar.
