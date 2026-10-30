# Fase 2 — BNF de sentencias de control y salida

**Tarea Jira:** GIC-2 — BNF de sentencias de control y entrada/salida
**Responsable:** Juan Diego García Albarracín
**Insumos:** especificación informal (`docs/fase1/especificacion_informal.md`, DSL-2), catálogo de tokens (`docs/fase1/catalogo_tokens.md`, LEX-1)
**Se complementa con:** el documento de GIC-1 (programa, declaraciones y expresiones)

---

## 1. Alcance

GIC-1 define el programa, la lista `<sentencias>`, la declaración y la jerarquía de expresiones, y deja pendientes las cuatro sentencias que se definen aquí:

| No terminal | Construcción | Ejemplo |
|---|---|---|
| `<asignacion>` | Asignación | `humedad = humedad - 6;` |
| `<salida>` | Impresión con `mostrar` | `mostrar("revisar el secador");` |
| `<condicional>` | Condicional con y sin `sino` | `si (defectos < 5) entonces … sino … fin` |
| `<ciclo>` | Ciclo `mientras` | `mientras (humedad > 12) hacer … fin` |

**Lectura.** Cafetal no tiene instrucción de lectura. La especificación informal solo define la salida con `mostrar`, y los datos se escriben en el programa con `dato`. Por eso esta tarea cubre la salida pero no la entrada.

Se usan la misma notación y los mismos terminales que GIC-1: no terminales en minúsculas entre `< >`, terminales con el nombre del token en MAYÚSCULAS, `::=`, `|` y ε. Igual que en GIC-1, esta es la **gramática inicial**: se escribe de la forma más natural, y la factorización y el análisis LL(1) se hacen en GIC-5 y GIC-6.

## 2. Reglas

```
<asignacion>  ::= ID ASIGNACION <expresion> PUNTO_COMA

<salida>      ::= MOSTRAR PAR_ABRE <argumento> PAR_CIERRA PUNTO_COMA
<argumento>   ::= <expresion>
               |  CADENA

<condicional> ::= SI PAR_ABRE <expresion> PAR_CIERRA ENTONCES <sentencias> FIN
               |  SI PAR_ABRE <expresion> PAR_CIERRA ENTONCES <sentencias> SINO <sentencias> FIN

<ciclo>       ::= MIENTRAS PAR_ABRE <expresion> PAR_CIERRA HACER <sentencias> FIN
```

### 2.1 Explicación de cada regla

- **Asignación.** Igual que la declaración de GIC-1, pero sin `DATO`: un identificador ya existente recibe el valor de una expresión. Como empieza con ID y la declaración con DATO, nunca se confunden.
- **Salida.** `mostrar` recibe un único argumento entre paréntesis. El argumento es una `<expresion>` o una `CADENA`. Se necesita la alternativa CADENA porque en GIC-1 las cadenas no forman parte de las expresiones: `"kilos" + 1` no es una expresión válida, pero `mostrar("kilos cosechados");` sí es una sentencia válida. Se agrega el no terminal `<argumento>` a los de GIC-1.
- **Condicional.** La condición es una `<expresion>`, porque GIC-1 usa una sola jerarquía para expresiones aritméticas y lógicas. Los dos bloques usan `<sentencias>` de GIC-1, así que pueden estar vacíos o contener cualquier sentencia, incluidos otros `si` y `mientras`. Las dos alternativas comparten el prefijo `SI PAR_ABRE <expresion> PAR_CIERRA ENTONCES <sentencias>`; su factorización le corresponde a GIC-5.
- **Ciclo.** Misma forma que el condicional sin `sino`, con `MIENTRAS` y `HACER`.

**Paréntesis obligatorios.** La condición de `si` y `mientras` y el argumento de `mostrar` van siempre entre paréntesis propios de la sentencia. Esos paréntesis no son los de `<factor>` de GIC-1. Por eso `si ((a + b) > 2)` se lee sin problema: el primer `(` es de la sentencia y el segundo es del factor.

### 2.2 Por qué el condicional no es ambiguo

En muchos lenguajes, `si a entonces si b entonces x sino y` es ambiguo: el `sino` puede pertenecer a cualquiera de los dos `si` (el problema del "else colgante"). En Cafetal **todo bloque termina con su propio `fin`**, así que el programador tiene que escribir explícitamente cuál de los dos casos quiere, y cada texto tiene una sola lectura:

| Texto | Significado |
|---|---|
| `si (a) entonces si (b) entonces x = 1; sino x = 2; fin fin` | El `sino` pertenece al `si` interno |
| `si (a) entonces si (b) entonces x = 1; fin sino x = 2; fin` | El `sino` pertenece al `si` externo |
| `si (a) entonces si (b) entonces x = 1; sino x = 2; fin` | No es derivable: falta un `fin` |

Los árboles de las dos primeras entradas muestran que en cada caso el `sino` queda bajo un único `<condicional>`, el que cierra su propio `fin`:

![Árboles del sino colgante](arboles/img/gic2_arboles_sentencias-SinoColgante.drawio.png)

*Fuente editable: `arboles/gic2_arboles_sentencias.drawio`, página SinoColgante.*

Se comprobó con un analizador general, que no supone nada sobre la forma de la gramática, que las dos primeras entradas, dentro de `inicio … fin`, tienen **exactamente un** árbol de derivación cada una, y que la tercera no tiene ninguno.

## 3. Gramática completa (GIC-1 + GIC-2)

Para citar las reglas en las derivaciones, cada alternativa se numera. Las reglas P, D y E son las de GIC-1 sin cambios; las reglas A, M, C y L son las de este documento.

```

P1   <programa> ::= INICIO <sentencias> FIN
P2   <sentencias> ::= <sentencias> <sentencia>
P3   <sentencias> ::= ε
P4   <sentencia> ::= <declaracion>
P5   <sentencia> ::= <asignacion>
P6   <sentencia> ::= <salida>
P7   <sentencia> ::= <condicional>
P8   <sentencia> ::= <ciclo>
D1   <declaracion> ::= DATO ID ASIGNACION <expresion> PUNTO_COMA
E1   <expresion> ::= <expresion> O <conjuncion>
E2   <expresion> ::= <conjuncion>
E3   <conjuncion> ::= <conjuncion> Y <negacion>
E4   <conjuncion> ::= <negacion>
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
E15  <suma> ::= <suma> SUMA <termino>
E16  <suma> ::= <suma> RESTA <termino>
E17  <suma> ::= <termino>
E18  <termino> ::= <termino> MULT <factor>
E19  <termino> ::= <termino> DIV <factor>
E20  <termino> ::= <factor>
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

N = N de GIC-1 ∪ {`<asignacion>`, `<salida>`, `<argumento>`, `<condicional>`, `<ciclo>`}, T = los 30 tokens del catálogo que llegan al analizador sintáctico, S = `<programa>`.

## 4. Validación: derivación de los programas de ejemplo

Los tres programas de `ejemplos/` se convirtieron en tokens con el AFD de la Fase 1 y se derivaron desde `<programa>` con la gramática completa. Además, un analizador general contó los árboles de derivación de cada programa, para confirmar que no hay ambigüedad en estas entradas:

| Programa | Tokens | Sentencias | Árboles de derivación | Resultado |
|---|---|---|---|---|
| `ejemplo1_produccion.cft` | 66 | 10 | 1 | Derivable |
| `ejemplo2_clasificacion.cft` | 62 | 9 | 1 | Derivable |
| `ejemplo3_secado.cft` | 57 | 8 | 1 | Derivable |

**Cómo leer las derivaciones.** Son derivaciones **más a la izquierda**: en cada línea se reemplaza el no terminal que está más a la izquierda, y al inicio de la línea aparece la regla aplicada. Como `<sentencias>` es recursiva por la izquierda (P2), la derivación primero despliega la lista completa y después deriva cada sentencia en orden. Para que las líneas se puedan leer:

- cuando una sentencia queda completa, sus tokens se reemplazan por **wₖ** (línea "=");
- cada expresión se deriva en un solo paso **⇒\***, con la lista de reglas aplicadas entre corchetes; las condiciones de `si` y `mientras` se abrevian después como **cₖ**;
- al final de cada derivación están los tokens de cada wₖ y cₖ.

La sección 4.4 muestra una condición derivada paso a paso, sin abreviar.

### 4.1 `ejemplo1_produccion.cft` — Producción de dos lotes

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

### 4.2 `ejemplo2_clasificacion.cft` — Clasificación del café

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

### 4.3 `ejemplo3_secado.cft` — Días de secado

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

### 4.4 Derivación completa de una condición

Condición del `si` de `ejemplo3_secado.cft`: `dia == 5 o no (humedad > 20)`. El `o` aparece en el primer paso (E1) porque es el operador de menor precedencia, y la comparación `humedad > 20` queda dentro de un `<factor>` entre paréntesis (E21), debajo del `no` (E5).

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

### 4.5 Árbol de derivación de `ejemplo3_secado.cft`

Las expresiones aparecen abreviadas (⇒\*) con los tokens que generan; el resto del árbol corresponde a la derivación de la sección 4.3.

![Árbol de derivación de ejemplo3_secado.cft](arboles/img/gic2_arboles_sentencias-Secado.drawio.png)

*Fuente editable: `arboles/gic2_arboles_sentencias.drawio`, página Secado. El árbol completo de la condición del `si` está en `arboles/gic1_arboles_expresiones.drawio`, página Condicion.*

## 5. Pendientes para las siguientes tareas

| Tarea | Qué queda por hacer sobre las reglas de este documento |
|---|---|
| GIC-4 (Diego) | Ninguna regla de GIC-2 es recursiva por la izquierda; las sentencias anidadas usan `<sentencias>`, que se transforma en GIC-4 junto con las reglas de GIC-1 |
| GIC-5 (Daniel) | Factorizar las dos alternativas de `<condicional>`, que comparten el prefijo `SI PAR_ABRE <expresion> PAR_CIERRA ENTONCES <sentencias>` |
| GIC-6 (Diego) | Incluir `<asignacion>`, `<salida>`, `<argumento>`, `<condicional>` y `<ciclo>` en el cálculo de PRIMERO y SIGUIENTE y en la tabla LL(1). Las alternativas de `<argumento>` no generan conflicto: CADENA no puede empezar una `<expresion>` |
