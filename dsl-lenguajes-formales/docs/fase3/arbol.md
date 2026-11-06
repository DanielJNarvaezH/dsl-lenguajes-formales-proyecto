# Fase 3 — Estructura de nodos del árbol de derivación

**Tarea Jira:** PAR-1 — Estructura de nodos del árbol de derivación
**Responsable:** Juan Diego García Albarracín
**Insumos:** `src/lexer/lexer.py` (LXR-1 y LXR-2), `docs/fase3/lexer.md`, `docs/fase3/errores_lexicos.md` y la gramática final de la Fase 2 (`factorizacion.md`, sección 6, y `primero_siguiente_ll1.md`)
**Archivos:** `src/parser/arbol.py` y `tests/test_arbol.py`
**Se complementa con:** PAR-2 y PAR-3 (funciones del parser, que crean los nodos), PAR-4 (errores sintácticos) y ARB-1 (visualización del árbol)

---

## 1. Qué define esta tarea

PAR-1 fija las dos piezas que comparten todas las tareas del analizador sintáctico:

1. **El contrato entre el analizador léxico y el sintáctico:** qué recibe el parser, qué garantiza el lexer y qué no puede hacer el parser con lo que recibe (sección 2).
2. **La clase `Nodo`**, con la que el parser construye el árbol de derivación (secciones 3 a 5).

El archivo `src/parser/arbol.py` no analiza nada: solo define la estructura. Las funciones que crean el árbol son de PAR-2 y PAR-3, y la impresión del árbol es de ARB-1.

## 2. Contrato entre el lexer y el parser

### 2.1 Qué recibe el parser

El parser recibe la lista de `Token` que devuelve `AnalizadorLexico.analizar` o `analizar_archivo`. La clase `Token` ya existe en `src/lexer/lexer.py` desde LXR-1, y `arbol.py` la importa de ahí. **No se define una segunda clase de token en el parser**: dos clases con los mismos datos podrían dejar de coincidir con el tiempo.

| Campo | Contenido | Para qué lo usa el parser |
|---|---|---|
| `tipo` | Nombre del token del catálogo (INICIO, ID, SUMA…) | Para decidir. Es exactamente el nombre del terminal en la BNF, así que el parser compara `tipo` con los terminales de la gramática y consulta la tabla LL(1) con él |
| `lexema` | Texto reconocido | Se guarda en las hojas del árbol para mostrarlo; no participa en ninguna decisión |
| `linea`, `columna` | Posición del primer carácter, desde 1 | Mensajes de error sintáctico (PAR-4) |
| `codigo` | Código numérico del catálogo (propiedad) | Opcional, para mostrar |

`Token` es inmutable (`dataclass(frozen=True)`): el parser lee los tokens, no los modifica.

### 2.2 Qué garantiza el lexer

| # | Garantía | Origen |
|---|---|---|
| 1 | Todo `tipo` pertenece al catálogo de `tokens.py` | El AFD solo devuelve tokens del catálogo (LXR-1 lo valida al cargar la tabla) |
| 2 | No llegan COMENTARIO ni BLANCO | Regla 3 de reconocimiento de la Fase 1 |
| 3 | La lista termina con `EOF`, que aparece una sola vez | LXR-1 |
| 4 | Los tokens están en el orden del texto, con línea y columna crecientes | Recorrido de izquierda a derecha |
| 5 | Los errores léxicos no están en la lista: quedan en `AnalizadorLexico.errores` | LXR-2 |

La garantía 5 significa que, si hubo errores léxicos, la lista igual cumple las garantías 1 a 4, pero le faltan los símbolos con error. Qué hace el programa en ese caso (analizar sintácticamente de todos modos o detenerse) se decide en PAR-5.

### 2.3 `verificar_contrato`

La función `verificar_contrato(tokens)` comprueba las garantías 1 a 4 y lanza `ErrorContrato` si alguna falla. Sirve para dos cosas:

- en las pruebas, para comprobar que el lexer cumple el contrato con todos los archivos del proyecto;
- en el parser, como verificación de entrada si PAR-2/PAR-3 lo consideran útil.

No reemplaza el manejo de errores: un error en el programa del usuario nunca rompe el contrato, porque el lexer siempre entrega una lista válida.

## 3. La clase `Nodo`

### 3.1 Atributos

| Atributo | Contenido |
|---|---|
| `simbolo` | En un no terminal, su nombre con `< >`, como en la BNF (`<suma_prima>`). En un terminal, el tipo del token (`ID`, `SUMA`). En una hoja vacía, `ε` |
| `regla` | Solo en los no terminales: la etiqueta de la producción que se le aplicó (`P1`, `R10`, `F2`…), con la numeración de la Fase 2 |
| `token` | Solo en los terminales: el `Token` emparejado |
| `hijos` | Lista de nodos, en el orden del lado derecho de la regla |

### 3.2 Tres tipos de nodo

| Tipo | Se crea con | `regla` | `token` | `hijos` |
|---|---|---|---|---|
| No terminal | `Nodo.no_terminal("<suma>", "R9")` | La etiqueta | `None` | Los símbolos del lado derecho |
| Terminal | `Nodo.terminal(token)` | `None` | El token | Ninguno: siempre es hoja |
| Vacío | `Nodo.vacio()` | `None` | `None` | Ninguno: siempre es hoja |

Los constructores validan lo básico: el no terminal debe ir entre `< >` y tener regla, el terminal debe recibir un `Token` distinto de `EOF`, y una hoja no acepta hijos.

### 3.3 Consultas

| Método o propiedad | Devuelve |
|---|---|
| `agregar(hijo)` | Agrega el hijo al final y lo devuelve |
| `es_no_terminal`, `es_terminal`, `es_vacio`, `es_hoja` | El tipo de nodo |
| `recorrer()` | Todos los nodos en preorden: el nodo y luego cada hijo, de izquierda a derecha |
| `hojas()` | Las hojas de izquierda a derecha, incluidas las ε |
| `frontera()` | Los tokens de las hojas, en orden: la cadena que deriva el subárbol |
| `derivacion_izquierda()` | Las etiquetas de las reglas en preorden |
| `posicion` | (línea, columna) del primer token del subárbol, o `None` si no tiene tokens |

Dos árboles son iguales (`==`) si coinciden en símbolos, reglas, tokens e hijos. Eso permite a TST-1 comparar el árbol que produce el parser con un árbol esperado.

`recorrer` es iterativo, no recursivo: la lista `<sentencias>` es recursiva por la derecha (R1), así que un programa largo produce un árbol profundo, y un recorrido recursivo podría superar el límite de recursión de Python. Las pruebas lo comprueban con un árbol de 5 000 niveles.

## 4. Decisiones de diseño

| Decisión | Motivo |
|---|---|
| Las reglas ε producen una hoja `ε` | Así lo exige la definición de árbol de derivación: cada nodo interior tiene como hijos los símbolos de su regla, y la regla ε tiene un único símbolo, ε. Es la forma de los árboles de GIC-4 y GIC-5, y la que permite comparar el árbol con la derivación a mano |
| Cada no terminal guarda su regla | En la sustentación se puede señalar cualquier nodo y decir qué regla de la BNF lo generó. Además, `derivacion_izquierda()` reconstruye la derivación más a la izquierda, que es el mismo orden en que el analizador LL(1) aplica las reglas (sección 11 de GIC-6) |
| `EOF` no está en el árbol | La gramática no lo genera: `<programa> ::= INICIO <sentencias> FIN`. `EOF` solo le indica al parser que el programa terminó |
| Se reutiliza `Token` del lexer | Un solo contrato, sin copias que puedan desincronizarse |
| `arbol.py` no imprime ni exporta | Es tarea de ARB-1. `Nodo` solo tiene un `repr` corto para depurar |
| El árbol es de derivación, no abstracto | La rúbrica pide el árbol de derivación sintáctica. Por eso conserva los no terminales `_prima` y las hojas ε, y los operadores quedan en la cadena de `<suma_prima>` y `<termino_prima>` tal como los deja la gramática de GIC-4 (sección 7.2 de `recursividad.md`) |

## 5. Ejemplo

Árbol de `inicio x = 1; fin`, armado regla por regla con la gramática final. Entre corchetes va la regla de cada no terminal, y entre comillas el lexema de cada terminal. El formato de impresión es solo ilustrativo: el definitivo lo define ARB-1.

```
<programa> [P1]
├── INICIO 'inicio'
├── <sentencias> [R1]
│   ├── <sentencia> [P5]
│   │   └── <asignacion> [A1]
│   │       ├── ID 'x'
│   │       ├── ASIGNACION '='
│   │       ├── <expresion> [R3]
│   │       │   ├── <conjuncion> [R6]
│   │       │   │   ├── <negacion> [E6]
│   │       │   │   │   └── <comparacion> [F1]
│   │       │   │   │       ├── <suma> [R9]
│   │       │   │   │       │   ├── <termino> [R13]
│   │       │   │   │       │   │   ├── <factor> [E23]
│   │       │   │   │       │   │   │   └── ENTERO '1'
│   │       │   │   │       │   │   └── <termino_prima> [R16]
│   │       │   │   │       │   │       └── ε
│   │       │   │   │       │   └── <suma_prima> [R12]
│   │       │   │   │       │       └── ε
│   │       │   │   │       └── <comparacion_prima> [F3]
│   │       │   │   │           └── ε
│   │       │   │   └── <conjuncion_prima> [R8]
│   │       │   │       └── ε
│   │       │   └── <expresion_prima> [R5]
│   │       │       └── ε
│   │       └── PUNTO_COMA ';'
│   └── <sentencias> [R2]
│       └── ε
└── FIN 'fin'
```

Para este árbol:

- `frontera()` devuelve los 6 tokens INICIO, ID, ASIGNACION, ENTERO, PUNTO_COMA y FIN: la entrada sin `EOF`.
- `derivacion_izquierda()` devuelve P1, R1, P5, A1, R3, R6, E6, F1, R9, R13, E23, R16, R12, F3, R8, R5, R2, en el mismo orden en que las aplica el analizador predictivo de GIC-6.

### 5.1 Cómo lo usarán PAR-2 y PAR-3

Con una función por no terminal, cada función crea su nodo, le agrega un hijo por cada símbolo del lado derecho de la regla elegida y lo devuelve. Por ejemplo, para `R13 <termino> ::= <factor> <termino_prima>`, que es la única regla de `<termino>`:

```python
def termino(self):
    nodo = Nodo.no_terminal("<termino>", "R13")
    nodo.agregar(self.factor())
    nodo.agregar(self.termino_prima())
    return nodo
```

Un terminal se agrega con `nodo.agregar(Nodo.terminal(token_emparejado))`, y una regla ε con `nodo.agregar(Nodo.vacio())`. La forma de elegir la regla y de emparejar tokens la definen PAR-2 y PAR-3; el ejemplo solo muestra cómo se arma el nodo.

## 6. Pruebas

```
python -m unittest tests.test_arbol -v
```

| Grupo | Qué comprueba |
|---|---|
| Nodo | Los tres tipos de nodo y sus propiedades, `agregar`, las validaciones de los constructores y el `repr` |
| Árbol completo | Dos programas armados regla por regla con la gramática final (`inicio x = 1; fin` y un `si … sino … fin` con comparación y `mostrar` de una cadena): la frontera es la entrada sin `EOF`, `derivacion_izquierda()` coincide con el orden del analizador LL(1) de GIC-6, las ε están donde deben (solo como hijo único de R2, R5, R8, F3, R12 y R16), la posición de cada subárbol, la igualdad estructural y un árbol de 5 000 niveles |
| Contrato | El lexer cumple el contrato con los 3 programas de `ejemplos/`, los 3 de `tests/errores/` y un archivo vacío; `verificar_contrato` detecta cada incumplimiento (lista vacía, sin `EOF`, `EOF` en medio, tipo fuera del catálogo, token descartable, orden alterado y elemento que no es `Token`); con errores léxicos la lista sigue cumpliendo |
| Restricciones | `arbol.py` no importa `re` |

Resultado: **15 pruebas, todas correctas.** Con las de LXR-1 y LXR-2, la suite completa tiene 54 pruebas y todas pasan:

```
python -m unittest tests.test_lexer tests.test_errores_lexicos tests.test_arbol -v
```
