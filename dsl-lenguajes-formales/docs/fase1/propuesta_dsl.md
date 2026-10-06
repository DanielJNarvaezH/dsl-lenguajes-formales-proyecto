# Propuesta del DSL: Cafetal

**Tarea Jira:** DSL-1 — Propuesta del dominio del DSL y validación de unicidad
**Responsable:** Daniel Josué Narváez Hincapié
**Equipo:** Daniel Josué Narváez Hincapié · Juan Diego García Albarracín
**Curso:** Teoría de Lenguajes Formales — Universidad del Quindío, 2026-2
**Presentado en clase:** martes 6 de octubre de 2026

---

## 1. Dominio del lenguaje

**Cafetal** es un mini-lenguaje de programación de dominio específico para registrar y calcular la producción de una finca cafetera: kilos recogidos, días de cosecha, precios y condiciones de calidad.

Su vocabulario está tomado del contexto del Eje Cafetero, lo que lo hace propio del grupo. Funciona como un lenguaje imperativo básico: guarda números en variables, evalúa expresiones aritméticas, toma decisiones y repite instrucciones.

## 2. Construcciones mínimas

| Construcción | Sintaxis | Ejemplo |
| --- | --- | --- |
| Declaración | `dato` identificador `=` expresión `;` | `dato kilos = 0 ;` |
| Asignación | identificador `=` expresión `;` | `kilos = kilos + 25 ;` |
| Expresiones aritméticas con jerarquía | `+ - * /`, paréntesis, enteros y decimales | `precio = kilos * 2.5 + 1000 ;` |
| Condicional | `si` condición `entonces` instrucciones [`sino` instrucciones] `finsi` | `si kilos > 300 entonces mostrar kilos ; finsi` |
| Ciclo | `mientras` condición `hacer` instrucciones `finmientras` | `mientras dia < 8 hacer dia = dia + 1 ; finmientras` |
| Salida | `mostrar` expresión `;` | `mostrar kilos ;` |

Una **condición** es una comparación entre dos expresiones con `<`, `>` o `==`.

## 3. Vocabulario preliminar

El catálogo formal de tokens con sus expresiones regulares se define en la tarea LEX-1. Como punto de partida, el lenguaje usa:

| Categoría | Elementos |
| --- | --- |
| Palabras reservadas (9) | `dato`, `si`, `entonces`, `sino`, `finsi`, `mientras`, `hacer`, `finmientras`, `mostrar` |
| Identificadores | Letra minúscula seguida de letras minúsculas o dígitos (ej. `kilos`, `lote2`) |
| Números | Enteros (`25`) y decimales con punto (`2.5`) |
| Operadores aritméticos | `+`, `-`, `*`, `/` |
| Operadores relacionales | `<`, `>`, `==` |
| Asignación | `=` |
| Delimitadores | `(`, `)`, `;` |
| Blancos (se descartan) | espacio, tabulación, salto de línea |

## 4. Programa de ejemplo

```
dato kilos = 0 ;
dato dia = 1 ;
mientras dia < 8 hacer
    kilos = kilos + 25 * 2 ;
    dia = dia + 1 ;
finmientras
si kilos > 300 entonces
    mostrar kilos * 2.5 ;
sino
    mostrar 0 ;
finsi
```

Durante 7 días se suman 50 kilos diarios (`25 * 2` se evalúa antes que la suma, por jerarquía). Al terminar, `kilos` vale 350; como `350 > 300`, el programa muestra `875`.

## 5. Decisiones de diseño

| Decisión | Motivo |
| --- | --- |
| Un solo tipo de dato (numérico) | Reduce el número de tokens, el tamaño del AFD y de la matriz de transiciones |
| Bloques cerrados con `finsi` y `finmientras` | Elimina desde el diseño la ambigüedad del "else colgante" |
| Fin de instrucción con `;` | Separa las instrucciones sin depender de saltos de línea ni sangría |
| Solo letras minúsculas en identificadores | Alfabeto Σ más pequeño y ER más cortas |
| `dato` como palabra de declaración | Lectura natural y sin prefijo compartido con otras palabras reservadas |

## 6. Material que aporta a cada fase

| Fase | Qué aporta Cafetal |
| --- | --- |
| Fase 1: Formalismo léxico | Prefijos compartidos para justificar estados de aceptación (`si`/`sino`, `finsi`/`finmientras`, `=`/`==`) y distinción entre palabra reservada e identificador (`dato` frente a `datos`) |
| Fase 2: Estructura sintáctica | Expresiones naturalmente recursivas por la izquierda (`E → E + T`), condicional con y sin `sino` que requiere factorización, y jerarquía de operadores que resolver sin ambigüedad |
| Fase 3: Implementación | Programas cortos y legibles para generar el árbol de derivación y casos de error claros (ej. `kilos = = 3 ;`) |

## 7. Fuera del alcance (ampliable si la profesora lo solicita)

Cadenas de texto, comentarios, operadores lógicos (`y`, `o`), operadores relacionales adicionales (`<=`, `>=`, `!=`) y lectura de datos. Pueden agregarse como tokens nuevos sin rehacer el diseño.

## 8. Puntos para validar con la profesora

- [ ] Aprobación de la unicidad del dominio **Cafetal**.
- [ ] Fecha propuesta de entrega de la Fase 1: **viernes 23 de octubre de 2026**.
- [ ] Notación para terminales que coinciden con metasímbolos de las ER (`(`, `)`, `*`, `+`). Propuesta: escribirlos entre comillas simples, por ejemplo `'('` y `'*'`.

**Plan B** si el dominio coincide con el de otro grupo: **Parqueo**, un lenguaje para calcular tarifas de un parqueadero, con la misma estructura y otro vocabulario.
