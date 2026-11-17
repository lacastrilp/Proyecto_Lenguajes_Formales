# INFORME DEL PROYECTO FINAL (ITEM 4)
## LENGUAJES FORMALES Y COMPILADORES (2026-2)
### Profesores: Adolfo Andrés Castro, César Augusto Guerra, Oscar Andrés Rodríguez, Sergio Ramírez Rico

---

## 1. SECCIONES, ALGORITMOS Y ESTRUCTURAS DE DATOS EMPLEADAS

Para el desarrollo del proyecto se siguieron fielmente las definiciones y algoritmos expuestos en el libro *Compilers: Principles, Techniques, and Tools* (2da Edición) de Aho, Lam, Sethi y Ullman:

### 1.1 Secciones y Algoritmos del Libro del Dragón
1. **Cálculo de FIRST y FOLLOW (Sección 4.4.2)**:
   - Se implementó el cálculo iterativo de punto fijo para $\text{FIRST}(X)$ y su extensión a cadenas $\text{FIRST}(X_1 \dots X_n)$, asegurando el tratamiento exacto de $\epsilon$ (`e`).
   - Se implementó el cálculo de $\text{FOLLOW}(A)$ garantizando la adición del marcador de fin de cadena $\$$ a $\text{FOLLOW}(S)$ y la propagación contextual por producciones $A \rightarrow \alpha B \beta$ y $A \rightarrow \alpha B$.
2. **Construcción de la Tabla Predictiva LL(1) (Algoritmo 4.31, Sección 4.4.3)**:
   - Mapeo bidimensional $M[A, a]$ para cada producción $A \rightarrow \alpha$.
   - Detección formal de gramáticas no LL(1) ante cualquier celda con cardinalidad mayor a 1.
3. **Analizador Predictivo No Recursivo Dirigido por Tabla (Algoritmo 4.34, Sección 4.4.4)**:
   - Simulación de pila con el marcador $\$$ en el fondo y el símbolo inicial en el tope, con reemplazo inverso de símbolos en derivaciones.
4. **Construcción del Autómata LR(0) y Tablas SLR(1) (Algoritmo 4.46, Secciones 4.6.2 y 4.6.4)**:
   - Función $\text{CLOSURE}(I)$ y función de transición $\text{GOTO}(I, X)$.
   - Colección canónica de conjuntos de ítems LR(0) sobre la gramática aumentada $S' \rightarrow S$.
   - Construcción de las tablas $\text{ACTION}[s, a]$ y $\text{GOTO}[s, A]$, asociando reducciones únicamente para terminales pertenecientes a $\text{FOLLOW}(A)$.
   - Detección de gramáticas no SLR(1) por presencia de conflictos shift/reduce o reduce/reduce.
5. **Algoritmo de Parseo LR (Algoritmo 4.44, Sección 4.6.3)**:
   - Manejo de pila de estados numéricos y transiciones mediante $\text{ACTION}$ y $\text{GOTO}$.
6. **Definiciones Dirigidas por la Sintaxis y Grafos de Dependencia (Secciones 5.1 y 5.2)**:
   - Representación de reglas semánticas como datos puros desacoplados del evaluador.
   - Instanciación dinámica del Grafo de Dependencias (DAG) en cada nodo del árbol sintáctico.
   - Ordenamiento topológico con el Algoritmo de Kahn y detección de circularidad en tiempo $\mathcal{O}(V + E)$.

### 1.2 Estructuras de Datos Utilizadas
- **Grafos y Conjuntos**: Diccionarios de Python (`dict`) con conjuntos de hashing (`set` y `frozenset`) para representar relaciones de adyacencia, colecciones canónicas de ítems e invariantes de conjuntos $\text{FIRST}$ y $\text{FOLLOW}$.
- **Pilas y Colas**: Listas de Python (`list`) para las pilas del parser descendente y ascendente, y colas de doble extremo (`collections.deque`) para el procesamiento en tiempo $\mathcal{O}(1)$ del ordenamiento topológico.
- **Árbol Sintáctico**: Clase `ParseTreeNode` con referencias ordenadas a hijos, atributos dinámicos e identificadores únicos enteros.

---

## 2. ITEMS 1 Y 2: GRAMÁTICA PROPIA, CONJUNTOS Y PARSEO PASO A PASO

### 2.1 Gramática Propia Seleccionada
Para ilustrar los Ítems 1 y 2, se diseñó la siguiente gramática propia (distinta a los ejemplos del enunciado), que modela listas delimitadas con operaciones de agrupación:
```text
3
S -> L
L -> b R
R -> , L e
```
Terminales: `b`, `,`. No terminales: `S`, `L`, `R`.

### 2.2 Conjuntos $\text{FIRST}$ y $\text{FOLLOW}$
Calculados automáticamente por nuestro programa con el argumento `--sets`:
```text
First(L) = {b}
First(R) = {,, e}
First(S) = {b}
Follow(L) = {$}
Follow(R) = {$}
Follow(S) = {$}
```

### 2.3 Tabla de Parseo Predictivo LL(1)
- $M[S, b] = \{ S \rightarrow L \}$
- $M[L, b] = \{ L \rightarrow b R \}$
- $M[R, ,] = \{ R \rightarrow , L \}$
- $M[R, \$] = \{ R \rightarrow e \}$

Como ninguna celda contiene más de una producción, la gramática es **LL(1)**.

### 2.4 Autómata LR(0) y Tabla SLR(1)
Gramática aumentada: $S' \rightarrow S$.
- Estado 0: $\text{CLOSURE}(\{[S' \rightarrow \cdot S]\}) = \{[S' \rightarrow \cdot S], [S \rightarrow \cdot L], [L \rightarrow \cdot b R]\}$.
- $\text{GOTO}(0, S) = \text{Estado 1}: \{[S' \rightarrow S \cdot]\} \rightarrow \text{ACTION}[1, \$] = \text{accept}$.
- $\text{GOTO}(0, b) = \text{Estado 2}: \{[L \rightarrow b \cdot R], [R \rightarrow \cdot , L], [R \rightarrow \cdot]\}$.
  - Como $[R \rightarrow \cdot]$ está completo y $\text{FOLLOW}(R) = \{\$\}$, $\text{ACTION}[2, \$] = \text{reduce } R \rightarrow e$.
  - Como $[R \rightarrow \cdot , L]$ tiene el punto antes de `,`, $\text{ACTION}[2, ,] = \text{shift } 3$.
  - No hay conflicto entre `,` y `$` porque son símbolos disjuntos.

La tabla SLR(1) no presenta colisiones; la gramática es **tanto LL(1) como SLR(1)**.

### 2.5 Traza de Análisis Paso a Paso de una Cadena
Cadena de prueba: `b,b` (con fin de cadena `$`).

#### Traza con el Analizador Ascendente SLR(1):
1. **Pila:** `[0]`, **Entrada:** `b,b$`.  
   Acción: $\text{ACTION}[0, b] = \text{shift } 2$.
2. **Pila:** `[0, 2]`, **Entrada:** `,b$`.  
   Acción: $\text{ACTION}[2, ,] = \text{shift } 3$.
3. **Pila:** `[0, 2, 3]`, **Entrada:** `b$`.  
   Acción: $\text{ACTION}[3, b] = \text{shift } 2$.
4. **Pila:** `[0, 2, 3, 2]`, **Entrada:** `$`.  
   Acción: $\text{ACTION}[2, \$] = \text{reduce } R \rightarrow e$. (Longitud 0).
5. **Pila:** `[0, 2, 3, 2, 4]`, **Entrada:** `$`.  
   Acción: $\text{ACTION}[4, \$] = \text{reduce } L \rightarrow b R$. (Longitud 2).
6. **Pila:** `[0, 2, 3, 5]`, **Entrada:** `$`.  
   Acción: $\text{ACTION}[5, \$] = \text{reduce } R \rightarrow , L$. (Longitud 2).
7. **Pila:** `[0, 2, 4]`, **Entrada:** `$`.  
   Acción: $\text{ACTION}[4, \$] = \text{reduce } L \rightarrow b R$. (Longitud 2).
8. **Pila:** `[0, 6]`, **Entrada:** `$`.  
   Acción: $\text{ACTION}[6, \$] = \text{reduce } S \rightarrow L$. (Longitud 1).
9. **Pila:** `[0, 1]`, **Entrada:** `$`.  
   Acción: $\text{ACTION}[1, \$] = \text{accept}$. **(Resultado: yes)**.

---

## 3. ITEM 3: DEFINICIÓN DIRIGIDA POR LA SINTAXIS (SDD)

### 3.1 Gramática y Reglas Semánticas
Gramática seleccionada (4 no terminales, 7 producciones, recursiva):
```text
S -> L
L -> BR
R -> +L e
B -> (L) 0 1
```

- Atributo heredado: $d$ (profundidad de anidamiento / escala).
- Atributos sintetizados: $val$ (valor numérico calculado con base $2^d$ para bits 1), $max\_d$ (profundidad máxima).

Reglas Semánticas:
- $S \rightarrow L$: $L.d = 0; \quad S.val = L.val; \quad S.max\_d = L.max\_d$.
- $L \rightarrow B R$: $B.d = L.d; \quad R.d = L.d; \quad L.val = B.val + R.val; \quad L.max\_d = \max(B.max\_d, R.max\_d)$.
- $R \rightarrow + L$: $L.d = R.d; \quad R.val = L.val; \quad R.max\_d = L.max\_d$.
- $R \rightarrow \epsilon$: $R.val = 0; \quad R.max\_d = R.d$.
- $B \rightarrow ( L )$: $L.d = B.d + 1; \quad B.val = L.val; \quad B.max\_d = L.max\_d$.
- $B \rightarrow 0$: $B.val = 0; \quad B.max\_d = B.d$.
- $B \rightarrow 1$: $B.val = 2^{B.d}; \quad B.max\_d = B.d$.

### 3.2 Clasificación (Paso 4)
- **No es S-atribuida**: Emplea el atributo heredado $d$.
- **Es L-atribuida**: Todo atributo heredado depende exclusivamente de la cabeza de la producción o de símbolos a su izquierda.

### 3.3 Resultados de Pruebas (Paso 6)
1. **Cadena más corta (`0`)**: `val = 0`, `max_d = 0`.
2. **Cadena simple (`1`)**: `val = 1`, `max_d = 0`.
3. **Cadena con suma (`1+0`)**: `val = 1`, `max_d = 0`.
4. **Cadena con anidamiento (`(1)`)**: `val = 2` ($2^1$), `max_d = 1`.
5. **Cadena con recursión profunda (`((1+0)+(1))`)**: `val = 8`, `max_d = 2`.
6. **Cadena no válida (`1++0`)**: Rechazada (`no`).
7. **Prueba de Circularidad**: Al inducir $L.d = S.val + 1$, el evaluador reportó:  
   `Error: La definición dirigida por la sintaxis (SDD) es CIRCULAR. Ciclo: L_5.val -> S_6.val -> L_5.d -> B_2.d -> B_2.val -> L_5.val`.

---

## 4. DIFICULTADES ENCONTRADAS Y SOLUCIONES IMPLEMENTADAS

1. **Tratamiento de Producciones $\epsilon$ en SLR(1)**:  
   *Problema:* Al inicio, si una producción era $A \rightarrow \epsilon$, el ítem LR(0) podía confundirse con una transición pendiente si no se trataba con longitud 0.  
   *Solución:* Se representó como ítem $[A \rightarrow \cdot]$ con cuerpo de longitud 0. En la reducción, se desapilan 0 estados de la pila de estados y se genera un nodo hoja decorado `'e'`.
2. **Desacoplamiento Estricto de la SDD y el Evaluador**:  
   *Problema:* Evitar que la clase evaluadora tuviera referencias cableadas a atributos como `val` o `d`.  
   *Solución:* Se modeló la regla semántica como un objeto de datos de primera clase (`SemanticRule`), permitiendo que el evaluador opere puramente sobre índices relativos de símbolos y funciones genéricas.
3. **Manejo de la Cadena Vacía en la Entrada**:  
   *Problema:* En la consola, una línea vacía termina la secuencia de cadenas a analizar, por lo que la cadena vacía $\epsilon$ se recibe como un renglón con `'e'`.  
   *Solución:* Se implementó un filtro en la capa de entrada que traduce la línea `'e'` a la cadena vacía real `""`, permitiendo parsear $\epsilon$ sin colisionar con el terminador de entrada.
