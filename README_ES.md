# Proyecto Final: Lenguajes Formales y Compiladores (2026-2)
## Analizadores Sintacticos LL(1), SLR(1) y Evaluador Generico de SDD

Visualizador Web Interactivo: https://lacastrilp.github.io/Proyecto_Lenguajes_Formales/

Implementamos este proyecto para el curso de Lenguajes Formales y Compiladores en la Universidad EAFIT (semestre 2026-2). El desarrollo esta hecho en Python 3 utilizando unicamente la biblioteca estandar.

El informe tecnico requerido en formato PDF para la entrega se encuentra compilado en la raiz del repositorio: [INFORME_ITEM4.pdf](file:///home/lacastrilp/Documentos/Semestre_2026_2/Lenguajes_Formales/ProyectoFinal/INFORME_ITEM4.pdf). La version en ingles requerida por la Seccion 4.2 del enunciado esta en [README.md](file:///home/lacastrilp/Documentos/Semestre_2026_2/Lenguajes_Formales/ProyectoFinal/README.md).

---

## 1. Informacion del Equipo y Entorno

### 1.1 Integrantes
- Luis Alejandro Castrillón Piedrahita (lacastrilp@eafit.edu.co)
- Manuela Buriticá Guzmán (mburiticg1@eafit.edu.co)
- Maria Juliana Henao Rua (mjhenaor@eafit.edu.co)

### 1.2 Entorno de Ejecucion
- Sistema Operativo: Linux (probado en Ubuntu 22.04 LTS y entornos POSIX x86_64).
- Lenguaje: Python 3 (probado en versiones 3.10, 3.11, 3.12 y 3.14).
- Librerias: Ninguna externa. Usamos unicamente modulos estandar: `sys`, `os`, `collections`, `typing`, `argparse`, `unittest` y `deque`. No empleamos generadores de parsers como Yacc, Bison, ANTLR, Lark o NLTK.
- Herramientas auxiliares: Bash (`run_tests.sh`) y el modulo `unittest`.

### 1.3 Uso de Herramientas de IA Generativa
Utilizamos Gemini y ChatGPT exclusivamente para resolver dudas puntuales de sintaxis con `argparse` y `unittest`, y para verificar las definiciones teoricas de grafos de dependencias expuestas en la Seccion 5.2 de Aho et al. Todo el diseno de algoritmos, estructuras de datos, tablas de analisis, automatas y casos de prueba fue desarrollado y analizado directamente por nosotros. Estamos en capacidad de explicar cualquier funcion y trazar gramaticas a mano durante la sustentacion oral.

---

## 2. Estructura del Repositorio

Distribuimos el proyecto en modulos de codigo organizados por items de entrega, pruebas unitarias, ejemplos y documentos:

```text
Proyecto_Lenguajes_Formales/
├── .gitignore
├── README.md                 # Documentacion oficial en ingles (Seccion 4.2)
├── README_ES.md              # Documentacion detallada en espanol
├── report.pdf                # Informe academico obligatorio compilado en PDF (raiz)
├── INFORME_ITEM4.pdf         # Copia del informe tecnico Item 4
├── index.html                # Visualizador interactivo web HTML/SVG
├── main.py                   # Ejecutable CLI para Items 1 y 2 (LL(1) y SLR(1))
├── sdd_main.py               # Ejecutable CLI para Item 3 (Evaluador de SDD)
├── run_tests.sh              # Script Bash para ejecucion y verificacion integral
│
├── src/                      # Codigo fuente modularizado por items de la rubrica
│   ├── __init__.py
│   ├── common/               # Modulos comunes compartidos
│   │   ├── __init__.py
│   │   ├── grammar.py        # Lectura y modelado de gramaticas CFG
│   │   ├── parse_tree.py     # Nodos del arbol de derivacion y render
│   │   └── html_formatter.py # Generador del visualizador web interactivo
│   ├── item1_first_follow/   # Item 1: Calculo de FIRST y FOLLOW
│   │   ├── __init__.py
│   │   └── first_follow.py   # Algoritmos de punto fijo y formateador --sets
│   ├── item2_parsers/        # Item 2: Analizadores sintacticos
│   │   ├── __init__.py
│   │   ├── ll1_parser.py     # Tabla predictiva y parser LL(1) no recursivo
│   │   └── slr1_parser.py    # Coleccion LR(0), tablas ACTION/GOTO y parser SLR(1)
│   └── item3_sdd/            # Item 3: Evaluacion dirigida por sintaxis
│       ├── __init__.py
│       ├── sdd.py            # Representacion pura de datos de la SDD
│       ├── sdd_evaluator.py  # Grafo de dependencias, orden topologico y ciclos
│       └── visualizer.py     # Visualizador interactivo en terminal
│
├── tests/                    # Pruebas automatizadas
│   ├── __init__.py
│   └── test_examples.py      # Pruebas de Ejemplos 1, 2, 3, evaluacion SDD y ciclos
│
├── examples/                 # Gramaticas y cadenas de prueba
│   ├── README.md             # Guia de ejemplos
│   ├── grammar_ex1.txt       # Ejemplo 1: SLR(1), no LL(1)
│   ├── grammar_ex2.txt       # Ejemplo 2: LL(1) y SLR(1)
│   ├── grammar_ex3.txt       # Ejemplo 3: ni LL(1) ni SLR(1)
│   ├── grammar_sdd.txt       # Gramatica seleccionada para el Item 3
│   └── test_strings_sdd.txt  # Cadenas de prueba para el Item 3
│
└── docs/                     # Enunciados, informes y teoria
    ├── LF_project_2026_2.pdf # Enunciado oficial
    ├── LecturesLeng.pdf      # Diapositivas de clase
    ├── INFORME_ITEM4.md      # Informe tecnico en Markdown
    └── TEORIA_COMPILADORES.md# Documentacion teorica detallada
```

---

## 3. Fundamentos Teoricos (Referencias al Dragon Book)

Seguimos las definiciones y algoritmos de Aho, Lam, Sethi y Ullman (*Compilers: Principles, Techniques, and Tools*, 2da edicion, 2006):

1. Conjuntos FIRST y FOLLOW (Sección 4.4.2): Calculamos FIRST y FOLLOW mediante iteraciones de punto fijo en `src/item1_first_follow/first_follow.py`, hasta que ningún conjunto cambia. Para FIRST procesamos símbolos de izquierda a derecha en cada cuerpo, incorporando terminales y avanzando mientras el símbolo actual pueda derivar la cadena vacía, representada por `e`. La función `first_of_string` extiende este cálculo a secuencias de símbolos `e` incluye e cuando todos son anulables. Para FOLLOW agregamos `$` al conjunto del símbolo inicial `S`, incorporamos FIRST del sufijo sin `e` y propagamos FOLLOW de la cabeza cuando dicho sufijo es anulable o vacío. La salida del flag `--sets` ordena los no terminales alfabéticamente y los terminales en orden ASCII, seguidos de `e` y finalmente `$`, si pertenecen al conjunto.

2. Tabla de Parseo Predictivo LL(1) (Algoritmo 4.31, Seccion 4.4.3):
En `src/ll1_parser.py` construimos la tabla bidimensional $M[A, a]$. Para cada produccion $A \rightarrow \alpha$, agregamos la regla a $M[A, a]$ para cada terminal $a \in \text{FIRST}(\alpha)$. Si $\alpha \Rightarrow^* \epsilon$, agregamos la regla a $M[A, b]$ para cada $b \in \text{FOLLOW}(A)$. Si una celda recibe mas de una regla, la gramatica no es LL(1). No aplicamos transformaciones previas a la gramatica (como eliminacion de recursion izquierda), respetando la restriccion del enunciado.

3. Analizador Predictivo no Recursivo (Algoritmo 4.34, Seccion 4.4.4):
La clase `LL1Parser` opera con una pila de simbolos inicializada con `['$', S]`. Al comparar el tope con el lookahead, desapila terminales coincidentes o reemplaza no terminales con el reverso de la produccion dictada por $M$. Durante este proceso enlazamos nodos para construir el arbol sintactico.

4. Automata LR(0) y Tabla SLR(1) (Algoritmos 4.44 y 4.46, Secciones 4.5 y 4.6):
En `src/slr1_parser.py` aumentamos la gramatica con $S' \rightarrow S$. Modelamos los items LR(0) como tuplas `(cabeza, cuerpo, punto)`. Calculamos las funciones `closure` y `goto` para obtener la coleccion canonica de items. En la tabla `ACTION` registramos desplazamientos a nuevos estados y reducciones restringidas a terminales de $\text{FOLLOW}(A)$. En `GOTO` mapeamos transiciones sobre no terminales. La presencia de conflictos invalida la condicion SLR(1). El parser ejecuta desplazamientos y reducciones sobre una pila de estados para validar la cadena y ensamblar el arbol.

5. SDD, Grafo de Dependencias y Orden Topologico (Secciones 5.1 y 5.2):
En `src/sdd.py` y `src/sdd_evaluator.py` modelamos las reglas semanticas como datos desacoplados del evaluador. Para cada nodo del arbol instanciamos las dependencias como aristas dirigidas desde los atributos requeridos hacia el atributo calculado. Calculamos el orden topologico con el algoritmo de Kahn. Si el grafo contiene ciclos, el algoritmo se detiene por falta de vertices con grado de entrada cero; en ese caso ejecutamos una busqueda DFS de tres colores para reconstruir e imprimir el ciclo.

---

## 4. Instrucciones de Compilacion y Ejecucion en Linux

### 4.1 Ejecucion de Items 1 y 2 (`main.py`)

Sintaxis general:
```bash
python3 main.py [--sets] [archivo_gramatica]
```
Si el archivo no se encuentra en el directorio actual, el programa lo busca en `examples/`.

#### Ejemplo 1: Gramatica SLR(1), no LL(1)
```bash
python3 main.py examples/grammar_ex1.txt
```
Imprime:
```text
Grammar is SLR(1).
```
Ingresando cadenas:
```text
i+i
(i)
(i+i)*i)

```
Salida generada:
```text
yes
yes
no
```

#### Ejemplo 2: Gramatica LL(1) y SLR(1), con `--sets`
```bash
python3 main.py --sets examples/grammar_ex2.txt
```
Salida generada:
```text
First(A) = {a, d}
First(B) = {b, e}
First(S) = {a, d}
Follow(A) = {b, $}
Follow(B) = {c, $}
Follow(S) = {$}
Select a parser (T: for LL(1), B: for SLR(1), Q: quit):
```
Al ingresar `T` o `B`:
```text
d
adbc
a

```
Salida generada:
```text
yes
yes
no
Select a parser (T: for LL(1), B: for SLR(1), Q: quit):
```
Ingresar `Q` para salir.

#### Ejemplo 3: Gramatica ni LL(1) ni SLR(1)
```bash
python3 main.py examples/grammar_ex3.txt
```
Salida generada:
```text
Grammar is neither LL(1) nor SLR(1).
```

---

### 4.2 Ejecucion de Item 3 (`sdd_main.py`)

Para evaluar cadenas contra la definicion dirigida por la sintaxis:

```bash
python3 sdd_main.py examples/test_strings_sdd.txt
```

Para cada cadena valida el evaluador imprime:
1. El arbol sintactico anotado (nodo por linea indentado por profundidad con sus atributos).
2. El orden de evaluacion topologico.
3. El valor del atributo principal (`val`) en el simbolo inicial ($S$).

Si la cadena no pertenece al lenguaje, imprime `no`.

#### Demostracion de Deteccion de Ciclos (`--circular`):
```bash
python3 sdd_main.py --circular
```
Al ingresar `1` seguido de una linea vacia, reporta el ciclo y detiene la ejecucion:
```text
Error: Error: La definición dirigida por la sintaxis (SDD) es CIRCULAR.
Ciclo detectado en las dependencias: L_5.val -> S_6.val -> L_5.d -> B_2.d -> B_2.val -> L_5.val
Ciclo identificado: L_5.val -> S_6.val -> L_5.d -> B_2.d -> B_2.val -> L_5.val
```

---

### 4.3 Verificacion Automatizada (`run_tests.sh`)

Ejecuta todas las pruebas unitarias y casos de prueba del proyecto:

```bash
chmod +x run_tests.sh
./run_tests.sh
```

---

### 4.4 Visualizador Web Interactivo HTML/SVG (`index.html`)

Implementamos un visualizador grafico interactivo aplicando el sistema de diseno editorial de Taller 2 (tarjetas tactiles, bordes oscuros de 2px, sombras duras `4px 4px 0px #0f172a` y grafos SVG). Para generarlo o actualizarlo:

```bash
python3 main.py --html
# o
python3 sdd_main.py --html
```

Al abrir `index.html` en cualquier navegador se visualiza:
1. Conjuntos FIRST y FOLLOW con justificaciones de calculo.
2. Diagrama SVG interactivo del automata LR(0) (7 estados) y tablas SLR(1)/LL(1).
3. Trazas de parseo paso a paso en tarjetas de dos columnas (Pila/Entrada vs Justificacion formal).
4. Evaluador SDD con arbol sintactico concreto decorado y Grafo de Dependencias (DAG) en SVG.
5. Probador interactivo en vivo para evaluar cadenas personalizadas.

---

## 5. Item 3: Gramatica, Atributos y Reglas Semanticas

### 5.1 Gramatica Seleccionada
Modelamos listas de bits binarios con peso segun profundidad de parentesis:

```text
4
S -> L
L -> BR
R -> +L e
B -> (L) 0 1
```

- G1: Sigue las convenciones de la Seccion 2.2 y es tanto LL(1) como SLR(1).
- G2: Posee 4 no terminales ($S, L, B, R$), 7 producciones y recursion en $L$ y $R$.
- G3: Es original y distinta a las de los textos o enunciados del curso.

### 5.2 Tabla de Atributos
| Simbolo | Atributo | Tipo | Tipo de Dato | Descripcion Semantica |
| :---: | :---: | :---: | :---: | :--- |
| **S** | `val` | Sintetizado | Entero | Valor numerico final de la expresion |
| **S** | `max_d` | Sintetizado | Entero | Profundidad maxima de parentesis alcanzada |
| **L** | `d` | Heredado | Entero | Nivel de profundidad heredado del contexto |
| **L** | `val` | Sintetizado | Entero | Suma de valores en la lista |
| **L** | `max_d` | Sintetizado | Entero | Profundidad maxima en subexpresion $L$ |
| **R** | `d` | Heredado | Entero | Profundidad heredada para el resto de la suma |
| **R** | `val` | Sintetizado | Entero | Valor de los terminos restantes |
| **R** | `max_d` | Sintetizado | Entero | Profundidad maxima en los terminos restantes |
| **B** | `d` | Heredado | Entero | Profundidad heredada para el bloque o bit |
| **B** | `val` | Sintetizado | Entero | Valor del bit o bloque ($2^d$ para `1`, $0$ para `0`) |
| **B** | `max_d` | Sintetizado | Entero | Profundidad maxima alcanzada en el bloque |
| **Terminales** | `lexval` | Sintetizado | Caracter | Caracter leido por el escaner |

El simbolo inicial $S$ no posee atributos heredados.

### 5.3 Tabla de Reglas Semanticas (Formato Figura 5.1 Dragon Book)
| Produccion | Reglas Semanticas |
| :--- | :--- |
| $S \rightarrow L$ | $L.d = 0$<br>$S.val = L.val$<br>$S.max\_d = L.max\_d$ |
| $L \rightarrow B R$ | $B.d = L.d$<br>$R.d = L.d$<br>$L.val = B.val + R.val$<br>$L.max\_d = \max(B.max\_d, R.max\_d)$ |
| $R \rightarrow + L$ | $L.d = R.d$<br>$R.val = L.val$<br>$R.max\_d = L.max\_d$ |
| $R \rightarrow \epsilon$ | $R.val = 0$<br>$R.max\_d = R.d$ |
| $B \rightarrow ( L )$ | $L.d = B.d + 1$<br>$B.val = L.val$<br>$B.max\_d = L.max\_d$ |
| $B \rightarrow 0$ | $B.val = 0$<br>$B.max\_d = B.d$ |
| $B \rightarrow 1$ | $B.val = 2^{B.d}$<br>$B.max\_d = B.d$ |

### 5.4 Clasificacion
No es S-atribuida porque utiliza el atributo heredado $d$. Es L-atribuida porque todos los atributos heredados en los cuerpos dependen de atributos heredados de la cabeza o de simbolos a su izquierda.

### 5.5 Resultados de Pruebas
- Cadena mas corta (`0`): `val = 0, max_d = 0`.
- Bit simple (`1`): `val = 1, max_d = 0`.
- Suma simple (`1+0`): `val = 1, max_d = 0`.
- Anidamiento (`(1)`): `val = 2, max_d = 1`.
- Recursion profunda (`((1+0)+(1))`): `val = 8, max_d = 2`.
- Cadena invalida (`1++0`): `no`.
- Cadena invalida (`(1+`): `no`.
- Caso circular temporal (`--circular`): ciclo `L_5.val -> S_6.val -> L_5.d -> B_2.d -> B_2.val -> L_5.val` y detencion controlada.

---

## 6. Item 4: Problemas Encontrados y Soluciones

1. Reducciones epsilon en SLR(1):
Las producciones vacias tienen longitud 0. Extraer estados de la pila como en reducciones normales alteraba la coherencia del automata. Lo corregimos desapilando 0 estados, evaluando $\text{GOTO}$ en el estado actual y agregando un nodo hoja con valor `'e'`.

2. Desacoplamiento de la definicion de la SDD:
El evaluador debia operar de forma abstracta sin nombres fijos de atributos. Creamos la clase `SemanticRule`, asociando computos e indices posicionales relativos de cada hijo.

3. Separacion de simbolos en las alternativas gramaticales:
La convencion del enunciado establece que las alternativas se separan por espacios y que los simbolos dentro de una alternativa no llevan espacios. Definir `L -> b R` hacia que el parser leyera dos alternativas `b` y `R`. Ajustamos la definicion a `L -> bR` y `R -> ,L e`.

4. Resolucion de rutas en los scripts CLI:
Al invocar `main.py` desde carpetas arbitrarias, los archivos relativos fallaban. Implementamos una comprobacion con `os.path.exists` que busca automaticamente en `examples/` si el archivo no esta en el directorio de ejecucion.

## Cómo ejecutar en Windows

No se necesita compilación ni paso de construcción. Instala Python 3.12+.
```
### Ítems 1 y 2: Analizadores LL(1) y SLR(1)
La gramática se lee por entrada estándar, o desde un archivo pasado como argumento:
```powershell
python main.py --sets examples\grammar_ex2.txt

python main.py examples\grammar_ex1.txt

@"
3
S -> AB
A -> aA d
B -> bBc e
"@ | python main.py
```

### Ítem 3: Evaluador de Definiciones Dirigidas por la Sintaxis (SDD)
Evalúa árboles de análisis anotados usando ordenamiento topológico sobre grafos de dependencias:
```powershell
python sdd_main.py examples\test_strings_sdd.txt

python sdd_main.py --parser ll1 examples\test_strings_sdd.txt

python sdd_main.py --interactive examples\test_strings_sdd.txt

@"
1

"@ | python sdd_main.py --circular
```
