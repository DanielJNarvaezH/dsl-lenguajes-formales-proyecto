# Cafetal — Especificación informal

Cafetal es un lenguaje para registrar y calcular la producción de una finca cafetera.
Los archivos fuente usan la extensión `.cft`.

## Elementos léxicos
- **Palabras reservadas:** inicio, fin, dato, si, entonces, sino, mientras, hacer, mostrar, y, o, no
- **Identificadores:** empiezan con letra minúscula; después pueden tener letras minúsculas,
  dígitos o guion bajo. Ej: `lote_norte`, `kilos2`. No pueden ser palabras reservadas.
- **Números:** enteros (`320`) o decimales con punto (`11.5`). No hay números negativos literales.
- **Cadenas:** texto entre comillas dobles, sin tildes ni ñ y sin saltos de línea. Ej: `"Secar de nuevo"`
- **Operadores aritméticos:** `+  -  *  /`
- **Operadores relacionales:** `<  >  <=  >=  ==  !=`
- **Operadores lógicos:** `y  o  no`
- **Asignación:** `=`
- **Delimitadores:** `(  )  ;`
- **Comentarios:** desde `#` hasta el final de la línea (se ignoran)
- **Espacios, tabulaciones y saltos de línea** solo separan tokens.

## Construcciones

| Construcción | Sintaxis | Ejemplo |
|---|---|---|
| Programa | `inicio <sentencias> fin` | `inicio ... fin` |
| Declaración | `dato <id> = <expresión> ;` | `dato kilos = 250;` |
| Asignación | `<id> = <expresión> ;` | `kilos = kilos + 30;` |
| Salida | `mostrar ( <expresión o cadena> ) ;` | `mostrar(kilos);` |
| Condicional | `si ( <condición> ) entonces <sentencias> fin` | |
| Condicional con alternativa | `si ( <condición> ) entonces <sentencias> sino <sentencias> fin` | |
| Ciclo | `mientras ( <condición> ) hacer <sentencias> fin` | |

## Reglas
- Toda declaración, asignación y salida termina en `;`.
- Una variable debe declararse con `dato` antes de usarse en una asignación.
- Los bloques de `si` y `mientras` siempre se cierran con `fin`, por lo que el `sino`
  siempre pertenece al `si` abierto más cercano.
- Precedencia, de mayor a menor:
    1. `( )`
    2. `*  /`  (asociatividad izquierda)
    3. `+  -`  (asociatividad izquierda)
    4. relacionales (no asociativos: `a < b < c` no es válido)
    5. `no`
    6. `y`
    7. `o`