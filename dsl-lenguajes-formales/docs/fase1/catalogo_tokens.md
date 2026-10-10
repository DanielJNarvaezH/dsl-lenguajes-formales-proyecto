# Catálogo de tokens de Cafetal

**Tarea Jira:** LEX-1 — Catálogo de tokens
**Responsable:** Daniel Josué Narváez Hincapié
**Fase:** 1 — Formalismo léxico
**Insumos:** propuesta del DSL (DSL-1) y especificación informal con programas de ejemplo (DSL-2)

---

## 1. Resumen

El analizador léxico de Cafetal reconoce **32 categorías léxicas**:

- **30 tokens** que se entregan al analizador sintáctico.
- **2 categorías descartables** (comentarios y blancos), que solo separan tokens.

Además, el analizador sintáctico recibe un marcador artificial de fin de archivo, `EOF`, que no proviene del texto fuente.

Las expresiones regulares de cada token se definen en las tareas ER-1 (tokens fijos) y ER-2 (tokens variables). El alfabeto Σ se define formalmente en LEX-2. Este catálogo fija **qué** se reconoce y **con qué código**; aquí los patrones se describen en palabras.

## 2. Conjuntos de caracteres de referencia

Estos nombres se usan en la columna "Lexema o patrón" y se formalizan en LEX-2.

| Nombre | Caracteres |
| --- | --- |
| Letra | Las 26 letras minúsculas de la `a` a la `z` (sin tildes ni `ñ`) |
| Dígito | Del `0` al `9` |
| Texto | Letra, dígito, guion bajo `_` o espacio |

## 3. Catálogo

### 3.1 Palabras reservadas (12)

| Código | Token | Lexema | Uso |
| --- | --- | --- | --- |
| 1 | INICIO | `inicio` | Abre el programa |
| 2 | FIN | `fin` | Cierra el programa y cada bloque `si` o `mientras` |
| 3 | DATO | `dato` | Declaración de variable |
| 4 | SI | `si` | Condicional |
| 5 | ENTONCES | `entonces` | Inicio del bloque verdadero del condicional |
| 6 | SINO | `sino` | Alternativa del condicional |
| 7 | MIENTRAS | `mientras` | Ciclo |
| 8 | HACER | `hacer` | Inicio del cuerpo del ciclo |
| 9 | MOSTRAR | `mostrar` | Salida |
| 10 | Y | `y` | Conjunción lógica |
| 11 | O | `o` | Disyunción lógica |
| 12 | NO | `no` | Negación lógica |

### 3.2 Identificadores y literales (4)

| Código | Token | Lexema o patrón | Ejemplos válidos | Ejemplos inválidos |
| --- | --- | --- | --- | --- |
| 20 | ID | Una letra seguida de cero o más letras, dígitos o guiones bajos | `kilos`, `lote_norte`, `promedio_2lotes` | `_kilos`, `Kilos` |
| 21 | ENTERO | Uno o más dígitos | `1`, `320`, `150000` | `-5` (son dos tokens: RESTA y ENTERO) |
| 22 | DECIMAL | Uno o más dígitos, un punto y uno o más dígitos | `11.5`, `275.5` | `12.`, `.5` |
| 23 | CADENA | Comilla doble, cero o más caracteres de Texto y comilla doble | `"secar de nuevo"`, `""` | `"Cafe"`, `"a:b"`, cadena sin cerrar |

### 3.3 Operadores aritméticos (4)

| Código | Token | Lexema |
| --- | --- | --- |
| 30 | SUMA | `+` |
| 31 | RESTA | `-` |
| 32 | MULT | `*` |
| 33 | DIV | `/` |

### 3.4 Operadores relacionales (6)

| Código | Token | Lexema |
| --- | --- | --- |
| 40 | MENOR | `<` |
| 41 | MAYOR | `>` |
| 42 | MENOR_IGUAL | `<=` |
| 43 | MAYOR_IGUAL | `>=` |
| 44 | IGUAL | `==` |
| 45 | DIFERENTE | `!=` |

### 3.5 Asignación y delimitadores (4)

| Código | Token | Lexema |
| --- | --- | --- |
| 50 | ASIGNACION | `=` |
| 60 | PAR_ABRE | `(` |
| 61 | PAR_CIERRA | `)` |
| 62 | PUNTO_COMA | `;` |

### 3.6 Categorías descartables (2)

| Código | Categoría | Patrón | Tratamiento |
| --- | --- | --- | --- |
| 90 | COMENTARIO | `#` seguido de cero o más caracteres de Texto, hasta el fin de línea | Se reconoce y se descarta |
| 91 | BLANCO | Uno o más espacios, tabulaciones, saltos de línea (`\n`) o retornos de carro (`\r`) | Se reconoce y se descarta; actualiza línea y columna |

### 3.7 Marcador del analizador sintáctico

| Código | Token | Origen |
| --- | --- | --- |
| 99 | EOF | Lo agrega el analizador léxico al terminar el archivo; no corresponde a ningún lexema |

Los códigos se agrupan por decenas según la categoría. Así se puede agregar un token nuevo en su grupo sin renumerar los demás.

## 4. Reglas de reconocimiento

### Regla 1: Lexema más largo

El analizador léxico siempre consume la secuencia más larga de caracteres que forme un token válido.

| Entrada | Se reconoce como | No como |
| --- | --- | --- |
| `sino` | SINO | SI seguido de NO |
| `<=` | MENOR_IGUAL | MENOR seguido de ASIGNACION |
| `==` | IGUAL | dos ASIGNACION |
| `11.5` | DECIMAL | ENTERO, punto, ENTERO |
| `kilos2` | ID | ID seguido de ENTERO |
| `finca` | ID | FIN seguido de ID `ca` |

### Regla 2: Prioridad de palabra reservada sobre identificador

Las palabras reservadas cumplen también el patrón de ID. Cuando el lexema más largo coincide **exactamente** con una palabra reservada, se clasifica como palabra reservada. Si continúa con otra letra, dígito o guion bajo, la Regla 1 lo convierte en ID.

| Entrada | Resultado | Motivo |
| --- | --- | --- |
| `si` | SI | Coincide exactamente con la palabra reservada |
| `siembra` | ID | El lexema más largo no es una palabra reservada |
| `dato` | DATO | Coincide exactamente |
| `datos`, `dato_1` | ID | Continúa con letra, dígito o guion bajo |
| `o`, `y` | O, Y | Coinciden exactamente; por eso no existen variables llamadas `o` ni `y` |
| `nota` | ID | Empieza como `no` pero continúa |

En el AFD, esto significa que los estados que aceptan una palabra reservada también tienen transiciones hacia el camino de identificador. Esas transiciones se construyen en AFD-3 y se justifican en AFD-6.

Una consecuencia de esta regla es que no se puede declarar una variable con el nombre de una palabra reservada. En `dato si = 3;` el lexema `si` se clasifica como SI, y el analizador sintáctico rechaza la declaración porque esperaba un ID.

### Regla 3: Descarte de comentarios y blancos

COMENTARIO y BLANCO se reconocen para avanzar en el texto y llevar la cuenta de línea y columna, pero no se entregan al analizador sintáctico.

Entre una palabra reservada y un ID debe haber al menos un blanco: `datokilos` es un solo ID. Entre tokens que empiezan con símbolos distintos no hace falta blanco: `mostrar(kilos);` produce MOSTRAR, PAR_ABRE, ID, PAR_CIERRA y PUNTO_COMA.

## 5. Errores léxicos

Un error léxico ocurre cuando ningún token puede reconocerse desde la posición actual. El analizador reporta el carácter, la línea y la columna, y continúa desde el siguiente carácter (tarea LXR-2).

| Caso | Ejemplo | Motivo |
| --- | --- | --- |
| Carácter fuera de Σ | `Kilos`, `año`, `a,b`, `x:` | Mayúsculas, `ñ`, tildes, coma y dos puntos no pertenecen al alfabeto |
| `!` sin `=` | `! (x > 2)` | `!` solo es válido como parte de `!=`; la negación se escribe `no` |
| Punto sin dígitos a ambos lados | `12.`, `.5` | DECIMAL exige dígitos antes y después del punto. En `12.` se reconoce ENTERO `12` y el punto queda en error |
| Cadena sin cerrar o con salto de línea | `"secar de nuevo` | La comilla de cierre nunca llega |
| Carácter no permitido dentro de cadena o comentario | `"Cafe"`, `# Revisar` | El contenido solo admite caracteres de Texto |
| Guion bajo al inicio | `_kilos` | Un ID debe empezar con letra |

Hay casos que el analizador léxico acepta pero el sintáctico rechaza. Por ejemplo, `2lotes` se divide en ENTERO `2` e ID `lotes`, y el error aparece en el análisis sintáctico. Lo mismo ocurre con `-5`, que se divide en RESTA y ENTERO.

## 6. Prefijos compartidos (insumo para AFD-1 y AFD-2)

Estos grupos de tokens comparten el comienzo, por lo que en el AFD comparten estados. En ellos hay estados de aceptación intermedios que deben justificarse en AFD-6.

| Prefijo | Tokens que lo comparten | Estado de aceptación intermedio |
| --- | --- | --- |
| `s`, `si` | SI, SINO | `si` acepta SI antes de continuar a `sino` |
| `m` | MIENTRAS, MOSTRAR | Ninguno (`m` sola es ID) |
| `n`, `no` | NO | `no` acepta NO; si continúa, es ID |
| `f`, `fin` | FIN | `fin` acepta FIN; si continúa, es ID |
| `<` | MENOR, MENOR_IGUAL | `<` acepta MENOR antes de `<=` |
| `>` | MAYOR, MAYOR_IGUAL | `>` acepta MAYOR antes de `>=` |
| `=` | ASIGNACION, IGUAL | `=` acepta ASIGNACION antes de `==` |
| `!` | DIFERENTE | `!` **no** es de aceptación: solo `!=` lo es |
| Dígitos | ENTERO, DECIMAL | Los dígitos aceptan ENTERO; el punto **no** es de aceptación hasta llegar otro dígito |
| Cualquier letra | ID y las 12 palabras reservadas | Cada palabra reservada acepta en su última letra; todo el camino también acepta ID |

## 7. Cobertura de los programas de ejemplo

Los 3 programas de `ejemplos/` usan las 32 categorías:

| Programa | Tokens que aporta |
| --- | --- |
| `ejemplo1_produccion.cft` | INICIO, FIN, DATO, MOSTRAR, ID, ENTERO, DECIMAL, CADENA, SUMA, RESTA, MULT, DIV, ASIGNACION, PAR_ABRE, PAR_CIERRA, PUNTO_COMA, COMENTARIO, BLANCO |
| `ejemplo2_clasificacion.cft` | SI, ENTONCES, SINO, Y, MENOR, MENOR_IGUAL, MAYOR_IGUAL, DIFERENTE |
| `ejemplo3_secado.cft` | MIENTRAS, HACER, O, NO, MAYOR, IGUAL, y un comentario al final de una línea de código |

## 8. Ejemplo de tokenización

Línea 7 de `ejemplo3_secado.cft`:

```
si (dia == 5 o no (humedad > 20)) entonces
```

| # | Lexema | Token | Código |
| --- | --- | --- | --- |
| 1 | `si` | SI | 4 |
| 2 | `(` | PAR_ABRE | 60 |
| 3 | `dia` | ID | 20 |
| 4 | `==` | IGUAL | 44 |
| 5 | `5` | ENTERO | 21 |
| 6 | `o` | O | 11 |
| 7 | `no` | NO | 12 |
| 8 | `(` | PAR_ABRE | 60 |
| 9 | `humedad` | ID | 20 |
| 10 | `>` | MAYOR | 41 |
| 11 | `20` | ENTERO | 21 |
| 12 | `)` | PAR_CIERRA | 61 |
| 13 | `)` | PAR_CIERRA | 61 |
| 14 | `entonces` | ENTONCES | 5 |

Los blancos entre lexemas se reconocen como BLANCO (código 91) y se descartan.
