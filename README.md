# Cafetal: diseño, auditoría e ingeniería inversa de un DSL en Python

Proyecto final de **Teoría de Lenguajes Formales**, Universidad del Quindío, 2026-2. Profesora Ana María Tamayo Ocampo.

**Equipo:** Daniel Josué Narváez Hincapié y Juan Diego García Albarracín.

**Cafetal** es un mini-lenguaje de dominio específico para registrar y calcular la producción de una finca cafetera: kilos recogidos, días de secado, humedad, defectos y precios. Los programas se escriben en archivos `.cft`. El proyecto define el lenguaje desde sus bases formales (alfabeto, expresiones regulares, AFD y gramática independiente del contexto) e implementa en Python su analizador léxico y sintáctico, que genera el árbol de derivación de un programa o el listado de sus errores.

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

## Requisitos

- **Python 3.9 o superior.** Solo se usa la biblioteca estándar: no hay que instalar librerías (`requirements.txt` está vacío a propósito). No se usan generadores de parsers ni el módulo `re`.
- **Opcional: [Graphviz](https://graphviz.org/download/),** solo para dibujar el árbol como imagen PNG.

## Instalación

```
git clone https://github.com/DanielJNarvaezH/dsl-lenguajes-formales-proyecto.git
cd dsl-lenguajes-formales-proyecto/dsl-lenguajes-formales
```

Opcionalmente, crea un entorno virtual con `python -m venv .venv` y actívalo:

| Sistema | Comando para activarlo |
|---|---|
| Windows (PowerShell) | `.venv\Scripts\Activate.ps1` |
| Linux o macOS | `source .venv/bin/activate` |

No hay dependencias que instalar.

## Uso

Todos los comandos se ejecutan desde la carpeta `dsl-lenguajes-formales`.

### Analizar un programa

```
python main.py ejemplos/ejemplo3_secado.cft
```

Si el programa no tiene errores, muestra su árbol de derivación:

```
<programa> [P1]
├── INICIO 'inicio'
├── <sentencias> [R1]
│   ├── <sentencia> [P4]
│   │   └── <declaracion> [D1]
│   │       ├── DATO 'dato'
│   │       ├── ID 'dia'
…
└── FIN 'fin'

Análisis correcto: 57 tokens y 165 reglas aplicadas.
```

Si tiene errores, muestra el listado, primero los léxicos y después los sintácticos:

```
python main.py tests/errores/sintactico2_sentencias.cft
```

```
5 errores sintácticos:
  Error sintáctico en la línea 3, columna 10: se esperaba ID y se encontró 'si' (SI).
  Error sintáctico en la línea 4, columna 13: se esperaba ASIGNACION y se encontró '12' (ENTERO).
  …
5 errores en total; no se muestra el árbol de derivación.
```

### Opciones

| Opción | Efecto |
|---|---|
| `--tokens` | Muestra la lista de tokens antes del árbol |
| `--derivacion` | Muestra la derivación más a la izquierda |
| `--posiciones` | Agrega línea:columna a cada terminal del árbol |
| `--ascii` | Dibuja las ramas del árbol solo con caracteres ASCII |
| `--salida RUTA` | Guarda el árbol en un archivo de texto |
| `--salida-derivacion RUTA` | Guarda la derivación en un archivo de texto |
| `--dot RUTA` | Guarda el árbol en formato DOT de Graphviz |
| `--png RUTA` | Dibuja el árbol como imagen (requiere Graphviz) |

El programa termina con código 0 si no hay errores, 1 si el programa tiene errores léxicos o sintácticos y 2 si no se pudo leer el archivo. `python main.py --help` muestra la ayuda.

### Ejecutar las pruebas

```
python ejecutar_pruebas.py
```

Ejecuta las 170 pruebas de la suite y muestra un resumen por módulo. Con `-v` se ve cada prueba, y se pueden elegir módulos: `python ejecutar_pruebas.py lexer errores`. También funciona `python -m unittest discover -s tests -t .`.

## Cómo funciona

```
programa .cft ──► analizador léxico ──► tokens ──► analizador sintáctico ──► árbol ──► visualización
                  (tabla_afd.csv)                  (tabla_ll1.csv)
```

- **Analizador léxico** (`src/lexer/`): recorre la matriz de transiciones del AFD de la Fase 1 con la regla del lexema más largo. Lista todos los errores léxicos sin detenerse.
- **Analizador sintáctico** (`src/parser/parser.py`): descendente recursivo, con una función por no terminal de la gramática final de la Fase 2, que elige cada regla con la tabla LL(1). Se recupera de los errores en modo pánico con los conjuntos SIGUIENTE.
- **Árbol de derivación** (`src/parser/arbol.py` y `visualizacion.py`): se muestra con sangría, como derivación más a la izquierda o como imagen.

Ni el lexer ni el parser tienen reglas escritas en el código: las tablas de las fases 1 y 2 toman todas las decisiones.

## Estructura del repositorio

```
dsl-lenguajes-formales/
├── main.py                  punto de entrada
├── ejecutar_pruebas.py      ejecuta toda la suite de pruebas
├── src/
│   ├── lexer/               analizador léxico y tabla_afd.csv
│   └── parser/              parser, árbol, visualización, tabla_ll1.csv y siguiente.csv
├── ejemplos/                programas de ejemplo de Cafetal
├── tests/                   pruebas, programas válidos (validos/) y con errores (errores/)
└── docs/
    ├── fase1/               formalismo léxico: alfabeto, ER, AFD y matriz de transiciones
    ├── fase2/               estructura sintáctica: BNF, ambigüedad, recursividad, factorización y LL(1)
    └── fase3/               implementación: documento de la fase y un documento por tarea
```

## Documentación

| Fase | Documento principal |
|---|---|
| Fase 1: formalismo léxico | `dsl-lenguajes-formales/docs/fase1/documento_fase1.md` |
| Fase 2: estructura sintáctica | Documentos de `dsl-lenguajes-formales/docs/fase2/`, en orden: gramática (GIC-1 y GIC-2), ambigüedad (GIC-3), recursividad (GIC-4), factorización (GIC-5) y LL(1) (GIC-6) |
| Fase 3: implementación y parser | `dsl-lenguajes-formales/docs/fase3/documento_fase3.md` |

## Forma de trabajo

- Cada tarea tiene un ID de Jira y un solo responsable.
- Ramas: `feat/<ID>` para una tarea nueva, por ejemplo `feat/PAR-2`, y `fix/<ID>` para corregir una tarea ya fusionada.
- Commits: `<ID>: descripción`, por ejemplo `LXR-1: analizador léxico dirigido por la matriz del AFD`.
- Cada pull request lo revisa el otro integrante antes de fusionarlo a `main`.
