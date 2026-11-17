# PROYECTO FINAL: LENGUAJES FORMALES Y COMPILADORES (2026-2)
## Analizadores Sintácticos LL(1), SLR(1) y Evaluador Genérico de Definiciones Dirigidas por la Sintaxis (SDD)

---

## 1. INFORMACIÓN GENERAL Y REQUISITOS DE ENTREGA

### 1.1 Integrantes del Grupo
- **Estudiante 1:** [Nombre Completo del Estudiante 1]
- **Estudiante 2:** [Nombre Completo del Estudiante 2]
- *(Opcional)* **Estudiante 3:** [Nombre Completo del Estudiante 3]

### 1.2 Entorno de Ejecución, Sistema Operativo y Versiones
- **Sistema Operativo:** Linux (Ubuntu 22.04 LTS / Debian o compatible POSIX x86_64).
- **Lenguaje de Programación:** Python 3 (Probado y compatible con Python 3.10, 3.11, 3.12 y 3.14).
- **Librerías Externas:** **Ninguna** (Se utiliza exclusivamente la Biblioteca Estándar de Python: `sys`, `collections`, `typing`, `argparse`, `unittest`, `deque`). Cumple al 100% la regla de no usar generadores de parsers (Yacc, Bison, ANTLR, Lark, NLTK).
- **Herramientas de Soporte:** `bash`, `unittest`.

### 1.3 Declaración de Uso Responsable de Herramientas de IA Generativa
> *De conformidad con las normas de integridad académica del curso:*  
> Se utilizaron modelos de IA generativa como soporte para la consulta de sintaxis, revisión conceptual de las demostraciones formales de Aho et al. y estructuración inicial de plantillas de prueba. Todo el diseño algorítmico, las estructuras de datos, las tablas de parseo, los grafos de dependencias y el código final fueron analizados, verificados y comprendidos en su totalidad por los integrantes del grupo, quienes están en capacidad plena de explicar cualquier línea de código, trazar gramáticas a mano y modificar la solución en tiempo real durante la sustentación oral.

---

## 2. MARCO TEÓRICO: SECCIONES 4.4, 4.5, 4.6, 5.1 Y 5.2 (DRAGON BOOK)

Este proyecto se basa estrictamente en el libro de texto de referencia:  
**Aho, Lam, Sethi, Ullman. *Compilers: Principles, Techniques, and Tools* (2da Edición), Addison-Wesley, 2006.**

A continuación se presenta el marco teórico formal que fundamenta la totalidad de los algoritmos implementados. *(Para una versión de estudio independiente, consultar también [`docs/TEORIA_COMPILADORES.md`](file:///home/lacastrilp/Documentos/Semestre_2026_2/Lenguajes_Formales/ProyectoFinal/docs/TEORIA_COMPILADORES.md)).*

```
                           FLUJO GENERAL DEL COMPILADOR
                           
    +---------------+        +----------------------+        +--------------------+
    | Secuencia de  | -----> | Analizador Sintáctico| -----> | Árbol Sintáctico   |
    | Tokens (Input)|        | (Parser LL(1)/SLR(1))|        | (Parse Tree)       |
    +---------------+        +----------------------+        +--------------------+
                                                                        |
                                                                        v
    +---------------+        +----------------------+        +--------------------+
    | Salida Semántica|<---- | Evaluador de SDD     |<------ | Grafo de           |
    | (Main Value)  |        | (Orden Topológico)   |        | Dependencias (DAG) |
    +---------------+        +----------------------+        +--------------------+
```

---

### 2.1 Sección 4.4: Análisis Sintáctico Descendente (*Top-Down Parsing*)

#### 2.1.1 Descenso Recursivo y Análisis Predictivo (Sección 4.4.1)
El análisis descendente intenta construir el árbol de derivación desde la raíz (el símbolo inicial $S$) hacia las hojas (la cadena de entrada $w$), encontrando una **derivación más a la izquierda** (*leftmost derivation*):
$$S \Rightarrow_{lm}^* w$$
- Si se utiliza retroceso (*backtracking*), el análisis es ineficiente en tiempo.
- El **análisis predictivo** evita el *backtracking* examinando únicamente el símbolo de entrada actual (*lookahead*) para decidir de forma unívoca qué producción aplicar.

#### 2.1.2 Algoritmos de $\text{FIRST}$ y $\text{FOLLOW}$ (Sección 4.4.2)
- **$\text{FIRST}(\alpha)$**: Conjunto de terminales que inician cadenas derivadas de $\alpha$. Si $\alpha \Rightarrow^* \epsilon$, entonces $\epsilon \in \text{FIRST}(\alpha)$.
  - Si $X$ es terminal: $\text{FIRST}(X) = \{X\}$.
  - Si $X \rightarrow \epsilon$: $\epsilon \in \text{FIRST}(X)$.
  - Si $X \rightarrow Y_1 Y_2 \dots Y_k$: añadir $\text{FIRST}(Y_i) \setminus \{\epsilon\}$ mientras los símbolos anteriores deriven $\epsilon$. Si todos derivan $\epsilon$, añadir $\epsilon$.
- **Extensión a Cadenas $\text{FIRST}(X_1 X_2 \dots X_n)$**: Se acumulan los terminales no vacíos de cada símbolo en orden; si un símbolo no deriva $\epsilon$, se detiene la propagación; si todos derivan $\epsilon$, se añade $\epsilon$.
- **$\text{FOLLOW}(A)$**: Conjunto de terminales que pueden aparecer inmediatamente a la derecha de $A$ en alguna forma sentencial derivada:
  1. $\$ \in \text{FOLLOW}(S)$.
  2. Si $A \rightarrow \alpha B \beta$, entonces $(\text{FIRST}(\beta) \setminus \{\epsilon\}) \subseteq \text{FOLLOW}(B)$.
  3. Si $A \rightarrow \alpha B$ o $A \rightarrow \alpha B \beta$ con $\epsilon \in \text{FIRST}(\beta)$, entonces $\text{FOLLOW}(A) \subseteq \text{FOLLOW}(B)$.

#### 2.1.3 Gramáticas LL(1) y Tabla de Análisis Predictivo (Sección 4.4.3 / Algoritmo 4.31)
Una gramática es **LL(1)** si para cualquier par de producciones $A \rightarrow \alpha \mid \beta$:
1. $\text{FIRST}(\alpha) \cap \text{FIRST}(\beta) = \emptyset$.
2. A lo sumo una de ellas deriva $\epsilon$.
3. Si $\beta \Rightarrow^* \epsilon$, entonces $\text{FIRST}(\alpha) \cap \text{FOLLOW}(A) = \emptyset$.

**Construcción de la tabla $M[A, a]$**:
- Para cada producción $A \rightarrow \alpha$:
  - Para todo terminal $a \in \text{FIRST}(\alpha) \setminus \{\epsilon\}$: añadir $A \rightarrow \alpha$ a $M[A, a]$.
  - Si $\epsilon \in \text{FIRST}(\alpha)$: para todo $b \in \text{FOLLOW}(A)$ (incluyendo $\$$): añadir $A \rightarrow \alpha$ a $M[A, b]$.
- Si alguna celda contiene dos o más producciones, la gramática **no es LL(1)**.

#### 2.1.4 Analizador No Recursivo Dirigido por Tabla (Sección 4.4.4 / Algoritmo 4.34)
Mantiene una pila con el marcador $\$$ en el fondo y $S$ en el tope (`['$', S]`), y lee la entrada $w\$$. En cada paso compara el tope $X$ con el lookahead $a$:
- Si $X = a = \$ \rightarrow$ **Aceptar**.
- Si $X = a \neq \$ \rightarrow$ Desapilar $X$ y avanzar el puntero de entrada.
- Si $X \in V_T \land X \neq a \rightarrow$ **Error sintáctico**.
- Si $X \in V_N \rightarrow$ Consultar $M[X, a]$. Si existe la producción $X \rightarrow Y_1 \dots Y_k$, desapilar $X$ y apilar $Y_k, \dots, Y_1$. Si $X \rightarrow \epsilon$, solo desapilar $X$. Si la celda está vacía, **Error sintáctico**.

---

### 2.2 Sección 4.5: Análisis Sintáctico Ascendente (*Bottom-Up Parsing*)

#### 2.2.1 Reducciones y Mangos (*Handles*) (Secciones 4.5.1 y 4.5.2)
- El parser ascendente reconstruye la derivación desde las hojas hacia la raíz. En cada paso identifica una subcadena en la forma sentencial derecha actual que coincide con el cuerpo de una producción $A \rightarrow \beta$ y la **reduce** a $A$.
- Esta secuencia corresponde al **reverso exacto de una derivación más a la derecha** (*rightmost derivation in reverse*).
- Un **mango (*handle*)** es una producción $A \rightarrow \beta$ y una posición en una forma sentencial derecha $\alpha \beta w$ tal que al sustituir $\beta$ por $A$ se obtiene la forma sentencial previa $\alpha A w$.

#### 2.2.2 Análisis Desplazamiento-Reducción (*Shift-Reduce Parsing*) (Sección 4.5.3)
Utiliza una pila para almacenar los símbolos ya leídos y un buffer de entrada:
1. **Shift (Desplazar)**: Mover el siguiente terminal de la entrada al tope de la pila.
2. **Reduce (Reducir)**: El extremo derecho del handle está en el tope de la pila; se extraen los símbolos del cuerpo y se apila la cabeza del no terminal.
3. **Accept (Aceptar)**: Entrada consumida y pila reducida al símbolo inicial.
4. **Error**: Discrepancia sintáctica.

#### 2.2.3 Conflictos en Shift-Reduce (Sección 4.5.4)
- **Conflicto Shift/Reduce**: El analizador no puede determinar si debe desplazar el lookahead o reducir los símbolos del tope.
- **Conflicto Reduce/Reduce**: El analizador debe reducir, pero hay múltiples producciones candidatas.

---

### 2.3 Sección 4.6: Análisis LR Simple (SLR(1))

#### 2.3.1 Ítems LR(0) y Gramática Aumentada (Sección 4.6.2)
- Un **ítem LR(0)** es una producción con un punto ($\cdot$) en alguna posición de su cuerpo: $[A \rightarrow \alpha \cdot \beta]$. Indica qué parte de la producción ya se leyó ($\alpha$) y qué se espera ver ($\beta$).
  - La producción vacía $A \rightarrow \epsilon$ genera un único ítem: $[A \rightarrow \cdot]$ (el punto ya está al final, listo para reducir).
- **Gramática Aumentada**: Se añade $S' \rightarrow S$. Permite definir inequívocamente la acción de aceptación cuando se reduce $S' \rightarrow S$.

#### 2.3.2 Operaciones $\text{CLOSURE}$ y $\text{GOTO}$
- **$\text{CLOSURE}(I)$**:
  - Todo ítem en $I$ está en $\text{CLOSURE}(I)$.
  - Si $[A \rightarrow \alpha \cdot B \beta] \in \text{CLOSURE}(I)$, se añade $[B \rightarrow \cdot \gamma]$ para cada producción $B \rightarrow \gamma$.
- **$\text{GOTO}(I, X)$**:
  - Es $\text{CLOSURE}(\{ [A \rightarrow \alpha X \cdot \beta] \mid [A \rightarrow \alpha \cdot X \beta] \in I \})$.
- **Colección Canónica $C = \{ I_0, I_1, \dots, I_n \}$**: Estados del autómata finito determinista LR(0) que reconoce los **prefijos viables** de la gramática.

#### 2.3.3 Construcción de Tablas SLR(1) (Algoritmo 4.46)
Para cada estado $i$ (conjunto $I_i$):
1. Si $[A \rightarrow \alpha \cdot a \beta] \in I_i$ con $a$ terminal y $\text{GOTO}(I_i, a) = I_j \rightarrow \text{ACTION}[i, a] = \text{shift } j$.
2. Si $[A \rightarrow \alpha \cdot] \in I_i$ con $A \neq S' \rightarrow$ para todo $a \in \text{FOLLOW}(A)$, $\text{ACTION}[i, a] = \text{reduce } A \rightarrow \alpha$.
3. Si $[S' \rightarrow S \cdot] \in I_i \rightarrow \text{ACTION}[i, \$] = \text{accept}$.
4. Para no terminales $A$: si $\text{GOTO}(I_i, A) = I_j \rightarrow \text{GOTO}[i, A] = j$.
- **Criterio SLR(1)**: La gramática es SLR(1) si y sólo si no existe ningún conflicto (shift/reduce o reduce/reduce) en la tabla $\text{ACTION}$.

#### 2.3.4 Algoritmo de Parseo LR (Algoritmo 4.44)
Mantiene una pila de estados $s_0 s_1 \dots s_m$ e interactúa con $\text{ACTION}$ y $\text{GOTO}$:
- Si $\text{ACTION}[s_m, a] = \text{shift } j$: apilar estado $j$, avanzar entrada.
- Si $\text{ACTION}[s_m, a] = \text{reduce } A \rightarrow \beta$: desapilar $|\beta|$ estados, sea $s'$ el nuevo tope; apilar $\text{GOTO}[s', A]$.
- Si $\text{ACTION}[s_m, a] = \text{accept}$: éxito.
- En cualquier otro caso: error.

---

### 2.4 Sección 5.1: Definiciones Dirigidas por la Sintaxis (SDDs)
Una SDD es una gramática libre de contexto junto con atributos y reglas semánticas:
- **Atributos Sintetizados (*Synthesized Attributes*)**: Definidos en el nodo cabeza a partir de los atributos de sus hijos y de sí mismo ($A.s = f(\text{hijos})$). Flujo de información ascendente.
- **Atributos Heredados (*Inherited Attributes*)**: Definidos en un símbolo del cuerpo a partir de atributos de su padre, sus hermanos y de sí mismo ($X_j.i = f(\text{padre}, \text{hermanos})$). Flujo descendente o lateral.
- **Restricciones Clave**:
  - Los **terminales** solo poseen atributos sintetizados provistos por el escáner (`lexval`), nunca heredados.
  - El **símbolo inicial $S$** no puede tener atributos heredados.

---

### 2.5 Sección 5.2: Órdenes de Evaluación para SDDs

#### 2.5.1 Grafo de Dependencias (*Dependency Graph*) y Orden Topológico
- **Vértices**: Una instancia por cada atributo de cada nodo del árbol sintáctico ($N.a$).
- **Aristas**: Si el cálculo de $X.b$ requiere el valor de $Y.c$, se traza una arista dirigida:
  $$Y.c \longrightarrow X.b$$
  indicando que $Y.c$ debe evaluarse antes que $X.b$.
- **Detección de Circularidad**: Si el grafo contiene un ciclo dirigido, la SDD es **circular** y no puede evaluarse.
- **Orden Topológico**: En un grafo sin ciclos (DAG), cualquier ordenamiento topológico (calculado por el Algoritmo de Kahn o DFS) define una secuencia válida de cómputo.

#### 2.5.2 Clases de SDD
- **S-Atribuida**: Todos sus atributos son sintetizados. Se evalúa naturalmente en un recorrido post-orden (durante el análisis ascendente LR).
- **L-Atribuida**: Admite atributos sintetizados y heredados, con la restricción de que un atributo heredado de un símbolo $X_j$ solo puede depender de los atributos heredados de la cabeza o de atributos de símbolos situados estrictamente a su izquierda ($X_1, \dots, X_{j-1}$). Puede evaluarse en una única pasada en profundidad de izquierda a derecha.

---

## 3. ARQUITECTURA Y DECISIONES DE DISEÑO DEL PROYECTO

### 3.1 Estructura Modular del Código
El código fuente se organizó en el paquete [`src/`](file:///home/lacastrilp/Documentos/Semestre_2026_2/Lenguajes_Formales/ProyectoFinal/src/) con una estricta separación de responsabilidades:

```
ProyectoFinal/
├── src/
│   ├── __init__.py           # Inicializador de paquete
│   ├── grammar.py            # Modelado formal de CFGs, validaciones y lectura de entrada
│   ├── first_follow.py       # Algoritmos de FIRST, FOLLOW y formateador --sets
│   ├── parse_tree.py         # Nodo de árbol sintáctico anotado y formateador visual
│   ├── ll1_parser.py         # Algoritmos 4.31 y 4.34 (Tabla y Parser Predictivo LL(1))
│   ├── slr1_parser.py        # Algoritmos 4.44 y 4.46 (Autómata LR(0), Tablas y Parser SLR(1))
│   ├── sdd.py                # Estructura de datos pura para SDDs (Reglas semánticas desacopladas)
│   ├── sdd_evaluator.py      # Evaluador genérico con grafo de dependencias y orden topológico
│   └── visualizer.py         # Visualizador interactivo en terminal paso a paso
├── tests/
│   └── test_examples.py      # Suite unitaria que cubre Ejemplos 1, 2, 3, Item 3 y circularidad
├── docs/
│   ├── LF_project_2026_2.pdf # Enunciado y rúbrica oficial del proyecto
│   ├── LecturesLeng.pdf      # Diapositivas y notas del curso
│   ├── INFORME_ITEM4.md      # Informe final del Item 4
│   └── TEORIA_COMPILADORES.md# Marco teórico formal exhaustivo
├── examples/                 # Gramáticas y cadenas de prueba
│   ├── grammar_ex1.txt
│   ├── grammar_ex2.txt
│   ├── grammar_ex3.txt
│   ├── grammar_sdd.txt
│   ├── test_strings_sdd.txt
│   └── README.md
├── main.py                   # CLI para Items 1 y 2
├── sdd_main.py               # CLI para Item 3
├── run_tests.sh              # Script de verificación automatizada
├── README_ES.md              # Documentación en español
└── README.md                 # Documentación maestra en inglés
```

### 3.2 Decisiones de Diseño Fundamentales
1. **Desacoplamiento Absoluto de la SDD (Datos, no Código)**:  
   Tal como exige el Paso 5.1 de la guía, la clase `SDDEvaluator` no tiene ningún conocimiento sobre los atributos `val`, `d` o `max_d`. Todas las reglas semánticas se declaran en instancias de `SemanticRule` dentro de `src/sdd.py`. Cambiar la SDD requiere únicamente cambiar la estructura de datos, sin tocar una sola línea del evaluador.
2. **Reconstrucción del Árbol Sintáctico en Ambos Parsers**:  
   - En LL(1): Se mantiene una pila paralela de nodos del árbol; al aplicar una producción $A \rightarrow Y_1 \dots Y_k$, se crean los nodos hijos y se enlazan de izquierda a derecha.
   - En SLR(1): Durante cada reducción por $A \rightarrow \beta$, se desapilan $|\beta|$ nodos de la pila de árboles, se convierten en hijos del nuevo nodo $A$, y este se apila nuevamente.
3. **Manejo Riguroso de Producciones Épsilon ($\epsilon$)**:  
   La cadena vacía se representa como la letra `'e'`. Si la entrada para el parser es `'e'`, se procesa internamente como cadena de longitud 0 (`""`), asegurando que las producciones nulas sean analizadas de forma idéntica en LL(1) y SLR(1).
4. **Detección y Trazado de Ciclos**:  
   El evaluador no solo detecta si un grafo de dependencias es circular (cuando el orden topológico de Kahn procesa menos vértices que el total), sino que utiliza una búsqueda en profundidad (DFS) con tres colores (blanco, gris, negro) para reconstruir y mostrar en consola la ruta exacta del ciclo:  
   `L_5.val -> S_6.val -> L_5.d -> B_2.d -> B_2.val -> L_5.val`.

---

## 4. DETALLES DE IMPLEMENTACIÓN DEL ITEM 3 (GUÍA PASO A PASO)

### 4.1 Paso 1: Gramática Seleccionada
Cumple rigurosamente las condiciones G1, G2 y G3 de la Sección 3:
- **G1**: Sigue las convenciones de la Sección 2.2, y es **tanto LL(1) como SLR(1)** (permite parsear con cualquiera de los dos analizadores del Item 2).
- **G2**: Posee 4 no terminales ($S, L, B, R \ge 3$), 7 producciones ($\ge 6$), y el no terminal $L$ (junto con $R$) es recursivo.
- **G3**: No pertenece a los ejemplos del libro ni del enunciado.

```
4
S -> L
L -> BR
R -> +L e
B -> (L) 0 1
```

### 4.2 Paso 2: Definición de la SDD en Papel

#### Tabla de Atributos:
| Símbolo | Atributo | Tipo de Atributo | Tipo de Dato | Significado Semántico |
| :---: | :---: | :---: | :---: | :--- |
| **S** | `val` | Sintetizado | Entero | Valor numérico final de la expresión ponderada. |
| **S** | `max_d` | Sintetizado | Entero | Máxima profundidad de anidamiento de paréntesis alcanzada. |
| **L** | `d` | **Heredado** | Entero | Nivel actual de profundidad de anidamiento heredado. |
| **L** | `val` | Sintetizado | Entero | Suma de los valores de los términos en la lista. |
| **L** | `max_d` | Sintetizado | Entero | Máxima profundidad encontrada en la subexpresión $L$. |
| **R** | `d` | **Heredado** | Entero | Profundidad heredada para el resto de la suma. |
| **R** | `val` | Sintetizado | Entero | Valor aportado por los términos restantes. |
| **R** | `max_d` | Sintetizado | Entero | Máxima profundidad en los términos restantes. |
| **B** | `d` | **Heredado** | Entero | Profundidad heredada para el bloque o dígito actual. |
| **B** | `val` | Sintetizado | Entero | Valor del bloque (para `1` es $2^d$, para `0` es 0). |
| **B** | `max_d` | Sintetizado | Entero | Máxima profundidad encontrada en el bloque. |
| **Term.** | `lexval` | Sintetizado | Carácter | Carácter léxico provisto por el escáner. |

#### Tabla de Producciones y Reglas Semánticas (Formato Dragon Book Fig. 5.1):
| Producción | Reglas Semánticas |
| :--- | :--- |
| $S \rightarrow L$ | $L.d = 0$;<br>$S.val = L.val$;<br>$S.max\_d = L.max\_d$ |
| $L \rightarrow B R$ | $B.d = L.d$;<br>$R.d = L.d$;<br>$L.val = B.val + R.val$;<br>$L.max\_d = \max(B.max\_d, R.max\_d)$ |
| $R \rightarrow + L$ | $L.d = R.d$;<br>$R.val = L.val$;<br>$R.max\_d = L.max\_d$ |
| $R \rightarrow \epsilon$ | $R.val = 0$;<br>$R.max\_d = R.d$ |
| $B \rightarrow ( L )$ | $L.d = B.d + 1$;<br>$B.val = L.val$;<br>$B.max\_d = L.max\_d$ |
| $B \rightarrow 0$ | $B.val = 0$;<br>$B.max\_d = B.d$ |
| $B \rightarrow 1$ | $B.val = 2^{B.d}$;<br>$B.max\_d = B.d$ |

### 4.3 Paso 3: Ejemplo a Mano
Tomamos la cadena con 5 terminales: `(1)+0` ($\ge 4$ terminales).

#### Árbol Sintáctico Anotado:
```
S {val=2, max_d=1}
└── L {d=0, val=2, max_d=1}
    ├── B {d=0, val=2, max_d=1}
    │   ├── ( {lexval='('}
    │   ├── L {d=1, val=2, max_d=1}
    │   │   ├── B {d=1, val=2, max_d=1}
    │   │   │   └── 1 {lexval='1'}
    │   │   └── R {d=1, val=0, max_d=1}
    │   │       └── e {lexval='e'}
    │   └── ) {lexval=')'}
    └── R {d=0, val=0, max_d=0}
        ├── + {lexval='+'}
        └── L {d=0, val=0, max_d=0}
            ├── B {d=0, val=0, max_d=0}
            │   └── 0 {lexval='0'}
            └── R {d=0, val=0, max_d=0}
                └── e {lexval='e'}
```

#### Grafo de Dependencias entre Atributos:
1. $L_{raiz}.d \rightarrow B_1.d$, $R_1.d$.
2. $B_1.d \rightarrow L_{sub}.d$ (con $L_{sub}.d = B_1.d + 1 = 1$).
3. $L_{sub}.d \rightarrow B_2.d$ y $R_2.d$.
4. $B_2.d \rightarrow B_2.val$ ($2^1 = 2$).
5. $R_2.d \rightarrow R_2.max\_d$, y $R_2.val = 0$.
6. $B_2.val, R_2.val \rightarrow L_{sub}.val = 2$.
7. $L_{sub}.val \rightarrow B_1.val = 2$.
8. De forma paralela en la rama derecha ($+0$): $R_1.d \rightarrow L_{der}.d \rightarrow B_3.d \rightarrow B_3.val = 0$, $R_3.val = 0 \rightarrow L_{der}.val = 0 \rightarrow R_1.val = 0$.
9. $B_1.val, R_1.val \rightarrow L_{raiz}.val = 2 + 0 = 2$.
10. $L_{raiz}.val \rightarrow S.val = 2$.

#### Orden Topológico Válido:
$L_0.d \rightarrow B_1.d \rightarrow L_1.d \rightarrow B_2.d \rightarrow B_2.val \rightarrow R_2.d \rightarrow R_2.val \rightarrow L_1.val \rightarrow B_1.val \rightarrow R_1.d \rightarrow L_2.d \rightarrow B_3.d \rightarrow B_3.val \rightarrow R_3.val \rightarrow L_2.val \rightarrow R_1.val \rightarrow L_0.val \rightarrow S.val$.

### 4.4 Paso 4: Clasificación de la SDD
- **¿Es S-Atribuida?** **NO**. Posee atributos heredados ($d$), y por definición formal (Sección 5.2.3), una definición S-atribuida contiene exclusivamente atributos sintetizados.
- **¿Es L-Atribuida?** **SÍ**. Para cada producción $A \rightarrow X_1 \dots X_n$, cada atributo heredado $X_j.d$ depende únicamente del atributo heredado de la cabeza $A.d$ (o es una constante 0, o suma 1 al atributo heredado de la cabeza). Jamás depende de atributos situados a su derecha. Por tanto, satisface estrictamente la condición de la Sección 5.2.4.

---

## 5. GUÍA PASO A PASO PARA COMPILAR, EJECUTAR Y PROBAR

Dado que el proyecto está desarrollado en Python 3 puro utilizando la biblioteca estándar, **no se requiere ningún paso de compilación previa**.

### 5.1 Ejecución de Pruebas Automatizadas
Para verificar de inmediato todos los casos de prueba unitarios, la conformidad con los tres ejemplos del PDF y el evaluador de SDD:
```bash
# Otorgar permisos de ejecución al script de pruebas
chmod +x run_tests.sh

# Ejecutar la suite completa
./run_tests.sh
```

O directamente mediante el módulo de pruebas de Python:
```bash
python3 -m unittest discover -s tests -v
```

---

### 5.2 Ejecución de los Items 1 y 2 (`main.py`)

#### Modo Estándar (Lectura desde archivo o stdin):
```bash
# Ejemplo 1 (SLR(1), no LL(1))
python3 main.py grammar_ex1.txt

# Ejemplo 2 (LL(1) y SLR(1)) con selección interactiva de parser
python3 main.py grammar_ex2.txt

# Ejemplo 3 (Ni LL(1) ni SLR(1))
python3 main.py grammar_ex3.txt
```

#### Uso del argumento `--sets`:
Imprime los conjuntos FIRST y FOLLOW para cada no terminal en orden alfabético, formateados exactamente como lo exige la Sección 2.1:
```bash
python3 main.py --sets grammar_ex2.txt
```
**Salida producida:**
```text
First(A) = {a, d}
First(B) = {b, e}
First(S) = {a, d}
Follow(A) = {b, $}
Follow(B) = {c, $}
Follow(S) = {$}
Select a parser (T: for LL(1), B: for SLR(1), Q: quit):
```

---

### 5.3 Ejecución del Item 3: Evaluador de SDD (`sdd_main.py`)

#### Modo Estándar con archivo de prueba:
Evalúa la lista de cadenas del archivo [`test_strings_sdd.txt`](file:///home/lacastrilp/Documentos/Semestre_2026_2/Lenguajes_Formales/ProyectoFinal/test_strings_sdd.txt):
```bash
python3 sdd_main.py test_strings_sdd.txt
```

#### Modo Interactivo (Visualizador Paso a Paso):
Permite inspeccionar el grafo de dependencias y avanzar atributo por atributo pulsando la tecla `Enter`:
```bash
python3 sdd_main.py --interactive
```
*(Escriba una cadena como `(1)+0` y presione Enter para ver el cálculo dinámico).*

#### Prueba de Detección de Definición Circular:
Demuestra que el evaluador detecta ciclos y detiene la ejecución reportando el ciclo:
```bash
python3 sdd_main.py --circular
```
*(Ingrese la cadena `1` y observe la alerta de ciclo).*

---

## 6. BANCO DE PREGUNTAS Y RESPUESTAS PARA LA SUSTENTACIÓN ORAL

A continuación se preparan las preguntas más rigurosas que el profesor o jurado evaluador podría realizar durante la defensa oral del proyecto, junto con las respuestas técnicas y matemáticas exactas:

---

### P1: ¿Por qué una gramática con recursión izquierda directa como $A \rightarrow A\alpha \mid \beta$ nunca puede ser LL(1)?
**Respuesta:**  
En una producción con recursión izquierda $A \rightarrow A\alpha \mid \beta$, para cualquier terminal $a \in \text{FIRST}(\beta)$, dicho terminal necesariamente pertenecerá también a $\text{FIRST}(A\alpha)$ (dado que $A \Rightarrow \beta \Rightarrow a\dots$). Por consiguiente:
$$\text{FIRST}(A\alpha) \cap \text{FIRST}(\beta) \neq \emptyset$$
Esto viola la primera condición de las gramáticas LL(1) (disyunción de terminales iniciales), provocando que la celda $M[A, a]$ de la tabla predictiva contenga simultáneamente al menos dos producciones ($A \rightarrow A\alpha$ y $A \rightarrow \beta$), lo que genera un conflicto determinista irresoluble para un lookahead de 1 símbolo.

---

### P2: ¿Cuál es la diferencia exacta entre un analizador LR(0) y un analizador SLR(1)?
**Respuesta:**  
Ambos construyen exactamente el mismo autómata determinista de colecciones canónicas de ítems LR(0). La diferencia radica exclusivamente en cómo se determinan las acciones de **reducción**:
- En **LR(0)**, cuando un estado contiene un ítem completo $[A \rightarrow \alpha \cdot]$, el parser coloca la acción $\text{reduce } A \rightarrow \alpha$ en **todas las columnas de terminales** de la fila de ese estado, sin mirar el lookahead.
- En **SLR(1)** (*Simple LR*), el parser utiliza el símbolo de preanálisis de longitud 1 y coloca la reducción $\text{reduce } A \rightarrow \alpha$ **únicamente en las columnas correspondientes a los terminales que pertenecen a $\text{FOLLOW}(A)$**.  
Esto reduce drásticamente los conflictos shift/reduce y reduce/reduce, permitiendo a SLR(1) analizar una familia mucho más amplia de gramáticas no ambiguas.

---

### P3: ¿Por qué en la gramática aumentada añadimos la producción $S' \rightarrow S$?
**Respuesta:**  
Si no aumentáramos la gramática y el símbolo inicial original $S$ apareciera en el lado derecho de alguna producción (por ejemplo, en gramáticas recursivas como $S \rightarrow (S) \mid a$), el parser no podría distinguir cuándo una reducción a $S$ corresponde a una subexpresión interna o cuándo representa la culminación del análisis de toda la entrada. Al crear $S'$ exclusivo con la producción $S' \rightarrow S$, garantizamos que $S'$ nunca aparezca en el cuerpo de ninguna regla; por tanto, la reducción $S' \rightarrow S$ ocurre única y exclusivamente cuando se ha reconocido toda la cadena y el lookahead es $\$$, señalando la aceptación definitiva (*Accept*).

---

### P4: ¿Cómo maneja su implementación las producciones épsilon ($\epsilon$) en los ítems LR(0)?
**Respuesta:**  
Siguiendo la Sección 4.6.2 del libro del Dragón, una producción vacía $A \rightarrow \epsilon$ genera **un único ítem**: $[A \rightarrow \cdot]$. Dado que el cuerpo tiene longitud cero ($|\epsilon| = 0$), el punto se encuentra conceptualmente al final desde el inicio. Por lo tanto:
1. No existe ningún símbolo posterior al punto para realizar transiciones $\text{GOTO}$.
2. En la construcción de la tabla SLR(1), para todo estado que contenga $[A \rightarrow \cdot]$, se añade la acción $\text{reduce } A \rightarrow \epsilon$ en todas las columnas $a \in \text{FOLLOW}(A)$.
3. Durante el análisis sintáctico LR, al ejecutar esta reducción se extraen $0$ estados de la pila, preservando el estado actual para consultar $\text{GOTO}[s, A]$.

---

### P5: En el evaluador de SDD, ¿por qué el símbolo inicial $S$ no puede tener atributos heredados?
**Respuesta:**  
Por definición (Sección 5.1.1), un atributo heredado de un nodo en el árbol sintáctico se computa a partir de los atributos de su nodo padre o de sus hermanos. Debido a que el símbolo inicial $S$ es la **raíz absoluta del árbol sintáctico**, no tiene ningún nodo superior ni hermanos que puedan suministrarle un valor heredado. Cualquier atributo de $S$ debe ser sintetizado a partir de las ramas hijas o constituir un valor global preexistente.

---

### P6: ¿Cómo garantiza su algoritmo de ordenamiento topológico la detección de circularidad en la SDD?
**Respuesta:**  
Se utiliza el **Algoritmo de Kahn**. Se calcula el grado de entrada (*in-degree*) de cada vértice del grafo de dependencias y se encolan los vértices con grado 0 (aquellos que no dependen de nadie, como los `lexval` de las hojas o constantes iniciales). Al procesar cada vértice, se descuenta 1 en el grado de entrada de sus vecinos.  
Si el grafo es acíclico (DAG), todos los vértices llegarán a tener grado de entrada 0 y serán procesados ($|V_{orden}| = |V_{total}|$). Si existe algún ciclo dirigido, los vértices que forman parte del ciclo (o que dependen de él) nunca podrán reducir su grado de entrada a 0, quedando atascados. Si al vaciarse la cola $|V_{orden}| < |V_{total}|$, el evaluador declara formalmente que la definición es circular y aborta la evaluación sin caer en un bucle infinito.

---

### P7: Si una gramática no es SLR(1), ¿significa necesariamente que es ambigua?
**Respuesta:**  
**No**. Toda gramática ambigua falla en ser SLR(1), pero existen muchas gramáticas libres de contexto **completamente no ambiguas** que tampoco son SLR(1). Un ejemplo clásico es:
$$S \rightarrow L = R \mid R, \quad L \rightarrow * R \mid id, \quad R \rightarrow L$$
Esta gramática no es ambigua, pero genera un conflicto shift/reduce en SLR(1) porque el conjunto $\text{FOLLOW}(R)$ contiene el símbolo `$=$`, a pesar de que en esa posición sentencial específica nunca podría ocurrir una reducción válida a $R$ seguida de `$=$`. Para resolver estas situaciones se crearon analizadores más potentes como **LR(1) Canónico** o **LALR(1)**, que incorporan el contexto del lookahead directamente dentro de los ítems.

---

### P8: ¿Cómo se implementó el requisito de que el evaluador no conozca la SDD?
**Respuesta:**  
Se implementó mediante el patrón de diseño donde la SDD es puramente una estructura de datos inmutable (`SDDDefinition`). Cada regla semántica se almacena como una tupla:  
`(destino, dependencias, función_computo)`.  
La clase `SDDEvaluator` simplemente lee esta lista de reglas al visitar cada nodo interno del árbol, genera las aristas dirigidas en el grafo de dependencias, resuelve el orden topológico matemáticamente invocando la función `compute_fn(*args)`, y escribe el resultado en el diccionario de atributos del nodo correspondiente. Cambiar la semántica del lenguaje equivale a reemplazar el diccionario de reglas en `src/sdd.py`, sin alterar una sola línea de código en `src/sdd_evaluator.py`.

---

## 7. REFERENCIAS BIBLIOGRÁFICAS
1. **Aho, Alfred V., Lam, Monica S., Sethi, Ravi, Ullman, Jeffrey D.** (2006). *Compilers: Principles, Techniques, and Tools* (2nd Edition). Addison-Wesley Longman Publishing Co., Inc. ISBN: 0321486811.
   - Sección 4.4: *Top-Down Parsing* (pp. 217–233).
   - Sección 4.5: *Bottom-Up Parsing* (pp. 233–242).
   - Sección 4.6: *Introduction to LR Parsing: Simple LR* (pp. 242–259).
   - Sección 5.1: *Syntax-Directed Definitions* (pp. 303–311).
   - Sección 5.2: *Evaluation Orders for SDD's* (pp. 311–324).
2. **Universidad EAFIT.** *LF_project_2026_2.pdf*: Guía y especificación formal del proyecto final de Lenguajes Formales y Compiladores (Semestre 2026-2).
