# Fase 1 — Expresiones regulares de los tokens variables

**Tarea Jira:** ER-2 — ER de identificadores, literales, blancos y comentarios
**Responsable:** Daniel Josué Narváez Hincapié
**Insumos:** catálogo de tokens (LEX-1), alfabeto Σ (LEX-2) y ER de tokens fijos (ER-1)

---

## Convención

- Se usan solo los operadores permitidos en el curso: unión con coma (`a,b`), concatenación por yuxtaposición o paréntesis (`ab`, `(a)(b)`), cerradura de Kleene `( )*` y cerradura positiva `( )+`.
- Los símbolos de Σ que coinciden con metasímbolos se escriben entre comillas simples: `'('`, `')'`, `'*'`, `'+'` (ver `alfabeto.md`).
- `.`, `"`, `#` y `_` no son metasímbolos en esta notación; dentro de una ER representan el propio símbolo de Σ.
- `␣` denota el espacio, `\t` la tabulación, `\n` el salto de línea y `\r` el retorno de carro.
- ε denota la cadena vacía. Es una ER primitiva básica, no un operador (ver `er.md`, sección 3).
- Un token variable tiene infinitos lexemas posibles, por eso su ER usa cerraduras. Los tokens fijos (un solo lexema) están en `er_tokens_fijos.md`.

## 1. Expresiones auxiliares

Para no repetir uniones largas, se nombran estas ER. Cada nombre abrevia la unión escrita completa a su derecha, y su lenguaje es el conjunto del mismo nombre en `alfabeto.md`.

| Nombre | ER | Lenguaje |
| --- | --- | --- |
| L | a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,p,q,r,s,t,u,v,w,x,y,z | Las 26 letras minúsculas |
| D | 0,1,2,3,4,5,6,7,8,9 | Los 10 dígitos |
| C | L,D,_,␣ | Contenido permitido en una cadena (38 símbolos) |
| K | L,D,'+',-,'*',/,<,>,=,!,'(',')',;,.,",#,_,␣,\t | Contenido permitido en un comentario: todo Σ excepto `\n` y `\r` (53 símbolos) |

Cuando un nombre aparece dentro de otra ER, se reemplaza por su unión entre paréntesis. Por ejemplo, `(L)(L,D,_)*` equivale a escribir las 26 letras en el primer paréntesis y las 26 letras, los 10 dígitos y el guion bajo en el segundo.

## 2. Expresiones regulares

| Código | Token | ER | Descripción |
| --- | --- | --- | --- |
| 20 | ID | (L)(L,D,_)* | Una letra seguida de cero o más letras, dígitos o guiones bajos |
| 21 | ENTERO | (D)+ | Uno o más dígitos |
| 22 | DECIMAL | (D)+.(D)+ | Uno o más dígitos, un punto y uno o más dígitos |
| 23 | CADENA | "(C)*" | Comilla, cero o más símbolos de C, comilla |
| 90 | COMENTARIO | #(K)* | Numeral seguido de cero o más símbolos de K |
| 91 | BLANCO | (␣,\t,\n,\r)+ | Uno o más espacios, tabulaciones, saltos de línea o retornos de carro |

**Números factorizados.** ENTERO y DECIMAL comparten el prefijo `(D)+`. Factorizando, la unión de ambos es:

NUM = (D)+(ε, .(D)+)

La rama `ε` corresponde a ENTERO y la rama `.(D)+` a DECIMAL. En el AFD esto produce un estado de aceptación después de los dígitos (ENTERO), y un estado de **no** aceptación después del punto, hasta que llega otro dígito (DECIMAL).

**Fin de los tokens variables.** Ninguna ER marca explícitamente dónde termina el lexema. El final lo determina la regla del lexema más largo (catálogo, Regla 1): el analizador avanza mientras exista transición y se detiene en el primer símbolo que no puede continuar. Por ejemplo, el comentario termina al llegar `\n` o `\r` porque esos son los únicos símbolos que no están en K.

## 3. Cadenas aceptadas y rechazadas

Una cadena **rechazada** es una cadena que no pertenece al lenguaje de la ER. Algunas pueden partirse en varios tokens válidos (por ejemplo `2kilos` = ENTERO + ID), pero ninguna de ellas es, completa, un lexema de ese token.

### ID = (L)(L,D,_)*

| Cadena | Resultado | Justificación |
| --- | --- | --- |
| `kilos` | Aceptada | `k` ∈ L; `ilos` ∈ (L,D,_)* |
| `lote_norte` | Aceptada | `l` ∈ L; `ote_norte` está formada por letras y un `_` |
| `promedio_2lotes` | Aceptada | Empieza con letra; luego letras, `_` y el dígito `2` |
| `2kilos` | Rechazada | El primer símbolo debe pertenecer a L y `2` ∈ D |
| `_lote` | Rechazada | El primer símbolo debe pertenecer a L y `_` ∉ L |
| `kilos-norte` | Rechazada | `-` no pertenece a (L,D,_) |

### ENTERO = (D)+

| Cadena | Resultado | Justificación |
| --- | --- | --- |
| `5` | Aceptada | Una repetición de D |
| `320` | Aceptada | Tres repeticiones de D |
| `150000` | Aceptada | Seis repeticiones de D |
| ε (cadena vacía) | Rechazada | `( )+` exige al menos un dígito |
| `12a` | Rechazada | `a` ∉ D |
| `2.5` | Rechazada | `.` ∉ D (es un DECIMAL) |

### DECIMAL = (D)+.(D)+

| Cadena | Resultado | Justificación |
| --- | --- | --- |
| `11.5` | Aceptada | `11` ∈ (D)+, punto, `5` ∈ (D)+ |
| `275.5` | Aceptada | `275` ∈ (D)+, punto, `5` ∈ (D)+ |
| `0.25` | Aceptada | `0` ∈ (D)+, punto, `25` ∈ (D)+ |
| `12.` | Rechazada | Falta al menos un dígito después del punto |
| `.5` | Rechazada | Falta al menos un dígito antes del punto |
| `1.2.3` | Rechazada | La ER admite un único punto |

### CADENA = "(C)*"

| Cadena | Resultado | Justificación |
| --- | --- | --- |
| `"secar de nuevo"` | Aceptada | Letras y espacios ∈ C, entre comillas |
| `"lote_2"` | Aceptada | Letras, `_` y dígito ∈ C, entre comillas |
| `""` | Aceptada | (C)* admite cero repeticiones |
| `"secar de nuevo` | Rechazada | Falta la comilla de cierre |
| `"kilos;"` | Rechazada | `;` ∉ C |
| `"linea1\nlinea2"` (con salto real) | Rechazada | `\n` ∉ C: una cadena no puede ocupar dos líneas |

### COMENTARIO = #(K)*

| Cadena | Resultado | Justificación |
| --- | --- | --- |
| `# simula los dias de secado` | Aceptada | `#` seguido de letras y espacios ∈ K |
| `# total = kilos * 2;` | Aceptada | `=`, `'*'` y `;` ∈ K: el comentario no se corta |
| `#` | Aceptada | (K)* admite cero repeticiones |
| `simula los dias` | Rechazada | Falta el `#` inicial |
| `# dos\nlineas` (con salto real) | Rechazada | `\n` ∉ K: el comentario termina en el salto de línea |
| `# Revisar` | Rechazada | `R` ∉ Σ, por lo tanto ∉ K |

### BLANCO = (␣,\t,\n,\r)+

| Cadena | Resultado | Justificación |
| --- | --- | --- |
| `␣` | Aceptada | Una repetición |
| `\r\n` | Aceptada | Fin de línea de Windows: dos símbolos de la unión |
| `\t␣␣` | Aceptada | Tres símbolos de la unión |
| ε (cadena vacía) | Rechazada | `( )+` exige al menos un símbolo |
| `␣a` | Rechazada | `a` no pertenece a la unión |
| `_` | Rechazada | El guion bajo no es un blanco |

## 4. Relación con las palabras reservadas

Las 12 palabras reservadas de `er_tokens_fijos.md` también pertenecen al lenguaje de ID: por ejemplo, `mientras` ∈ L((L)(L,D,_)*). Las dos ER se solapan a propósito, y la ambigüedad se resuelve con la Regla 2 del catálogo: si el lexema más largo es **exactamente** una palabra reservada, se clasifica como palabra reservada. En otro caso, es ID.

| Lexema | ¿∈ L(ID)? | ¿Es palabra reservada? | Token |
| --- | --- | --- | --- |
| `si` | Sí | Sí | SI |
| `sino` | Sí | Sí | SINO |
| `siembra` | Sí | No | ID |
| `fin` | Sí | Sí | FIN |
| `finca` | Sí | No | ID |
| `o` | Sí | Sí | O |

## 5. Verificación con los programas de ejemplo

Todos los lexemas variables de los 3 programas de `ejemplos/` pertenecen al lenguaje de su ER:

| Token | Lexemas de los ejemplos |
| --- | --- |
| ID | `lote_norte`, `lote_sur`, `total_kilos`, `promedio_2lotes`, `precio_kilo`, `ingreso`, `humedad`, `defectos`, `dia` |
| ENTERO | `0`, `1`, `2`, `4`, `5`, `6`, `10`, `12`, `20`, `45`, `320`, `12500`, `150000` |
| DECIMAL | `275.5`, `11.5` |
| CADENA | `"kilos cosechados"`, `"cafe tipo exportacion"`, `"revisar el secador"`, entre otras |
| COMENTARIO | `# calcula la produccion total de dos lotes`, `# pierde 6 puntos por dia`, entre otros |
| BLANCO | Espacios de indentación y finales de línea `\r\n` |
