# Propuesta del DSL: Cafetal

**Tarea Jira:** DSL-1 — Propuesta del dominio del DSL y validación de unicidad
**Responsable:** Daniel Josué Narváez Hincapié
**Equipo:** Daniel Josué Narváez Hincapié · Juan Diego García Albarracín
**Curso:** Teoría de Lenguajes Formales — Universidad del Quindío, 2026-2
**Presentado en clase:** martes 6 de octubre de 2026 (dominio registrado ante la profesora)
**Versión:** 2 — alineada con la especificación informal (DSL-2)

---

## 1. Dominio del lenguaje

**Cafetal** es un mini-lenguaje de programación de dominio específico para registrar y calcular la producción de una finca cafetera: kilos recogidos, días de secado, humedad, defectos y precios. Los archivos fuente usan la extensión `.cft`.

Su vocabulario está tomado del contexto del Eje Cafetero, lo que lo hace propio del grupo. Funciona como un lenguaje imperativo básico: guarda números en variables, evalúa expresiones aritméticas y lógicas, toma decisiones, repite instrucciones y muestra resultados.

## 2. Construcciones

| Construcción | Sintaxis | Ejemplo |
| --- | --- | --- |
| Programa | `inicio` sentencias `fin` | `inicio … fin` |
| Declaración | `dato` identificador `=` expresión `;` | `dato kilos = 250;` |
| Asignación | identificador `=` expresión `;` | `kilos = kilos + 30;` |
| Expresiones aritméticas con jerarquía | `+ - * /`, paréntesis, enteros y decimales | `dato ingreso = kilos * 12500 - 150000 / 2;` |
| Condiciones | relacionales `< > <= >= == !=` y lógicos `y`, `o`, `no` | `humedad >= 10 y humedad <= 12` |
| Condicional | `si (` condición `) entonces` sentencias [`sino` sentencias] `fin` | `si (defectos < 5) entonces … sino … fin` |
| Ciclo | `mientras (` condición `) hacer` sentencias `fin` | `mientras (humedad > 12) hacer … fin` |
| Salida | `mostrar (` expresión o cadena `) ;` | `mostrar("cafe tipo exportacion");` |

## 3. Vocabulario

El catálogo formal de tokens con sus códigos y expresiones regulares se define en la tarea LEX-1.

| Categoría | Elementos |
| --- | --- |
| Palabras reservadas (12) | `inicio`, `fin`, `dato`, `si`, `entonces`, `sino`, `mientras`, `hacer`, `mostrar`, `y`, `o`, `no` |
| Identificadores | Letra minúscula seguida de letras minúsculas, dígitos o guion bajo (ej. `lote_norte`, `kilos2`) |
| Números | Enteros (`320`) y decimales con punto (`11.5`); no hay negativos literales |
| Cadenas | Entre comillas dobles; solo letras minúsculas sin tildes, dígitos, guion bajo y espacio |
| Operadores aritméticos | `+`, `-`, `*`, `/` |
| Operadores relacionales | `<`, `>`, `<=`, `>=`, `==`, `!=` |
| Asignación | `=` |
| Delimitadores | `(`, `)`, `;` |
| Comentarios (se descartan) | Desde `#` hasta el final de la línea; mismo contenido permitido que las cadenas |
| Blancos (se descartan) | Espacio, tabulación, salto de línea y retorno de carro |

## 4. Programa de ejemplo

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

Cada día la humedad baja 6 puntos hasta quedar en 12 o menos. Cuando es el día 5 o la humedad ya no supera 20, el programa avisa que hay que revisar el secador. Al final muestra cuántos días pasaron.

## 5. Decisiones de diseño

| Decisión | Motivo |
| --- | --- |
| Un solo tipo de dato numérico (las cadenas solo se usan en `mostrar`) | Mantiene el lenguaje simple sin perder legibilidad en la salida |
| Programa delimitado por `inicio` y `fin` | Estructura clara para la regla inicial de la gramática |
| Todo bloque se cierra con `fin` | Elimina desde el diseño la ambigüedad del "else colgante": el `sino` pertenece al `si` abierto más cercano |
| Condiciones y `mostrar` entre paréntesis | Separa sin ambigüedad la condición de la palabra `entonces` o `hacer` |
| Fin de instrucción con `;` | Separa las instrucciones sin depender de saltos de línea ni sangría |
| Texto de cadenas y comentarios restringido a minúsculas, dígitos, guion bajo y espacio | Reutiliza los conjuntos de los identificadores y mantiene Σ pequeño |
| Precedencia de mayor a menor: `( )`, `* /`, `+ -`, relacionales, `no`, `y`, `o` | Jerarquía estándar; los relacionales no son asociativos (`a < b < c` no es válido) |

## 6. Material que aporta a cada fase

| Fase | Qué aporta Cafetal |
| --- | --- |
| Fase 1: Formalismo léxico | Prefijos compartidos para justificar estados de aceptación (`si`/`sino`, `<`/`<=`, `>`/`>=`, `=`/`==`), el símbolo `!` que solo es válido seguido de `=`, palabras reservadas de una letra (`y`, `o`) y distinción entre palabra reservada e identificador (`fin` frente a `finca`, `no` frente a `nota`) |
| Fase 2: Estructura sintáctica | Siete niveles de precedencia que estratificar, expresiones naturalmente recursivas por la izquierda (`E → E + T`) y condicional con y sin `sino` que requiere factorización |
| Fase 3: Implementación | Programas cortos y legibles para generar el árbol de derivación y casos de error claros (ej. `kilos = = 3;`) |

## 7. Fuera del alcance

Validaciones semánticas, como el uso de variables no declaradas o declaradas dos veces. El proyecto evalúa el análisis léxico y sintáctico; estas validaciones se agregarían con una tabla de símbolos solo si sobra tiempo.

## 8. Puntos validados con la profesora

- [x] Unicidad del dominio **Cafetal** (registrado en el listado de la clase).
- [x] Fecha de entrega de la Fase 1: **lunes 26 de octubre de 2026**.
- [ ] Notación para terminales que coinciden con metasímbolos de las ER (`(`, `)`, `*`, `+`). Propuesta: escribirlos entre comillas simples, por ejemplo `'('` y `'*'`, declarando la convención en el documento. La profesora ya aceptó en clase una convención equivalente (renombrar símbolos) siempre que se explique.
