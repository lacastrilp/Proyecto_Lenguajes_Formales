# FUNDAMENTOS TEÓRICOS DE COMPILADORES
### *Compilers: Principles, Techniques, and Tools* (2da Edición) — Aho, Lam, Sethi, Ullman - Secciones 4.4, 4.5, 4.6, 5.1 y 5.2

---

## 1. INTRODUCCIÓN Y CONTEXTO GENERAL

En el diseño de la fase de análisis sintáctico (*syntax analysis* o *parsing*) y traducción dirigida por la sintaxis (*syntax-directed translation*), el compilador toma como entrada una secuencia de componentes léxicos (*tokens*) producida por el analizador léxico (*lexer/scanner*) y construye una representación en forma de árbol que refleja la estructura gramatical del programa de acuerdo con una **Gramática Libre de Contexto** (*Context-Free Grammar* o *CFG*).

Una gramática libre de contexto $G$ se define formalmente como una 4-tupla:
$$G = (V_N, V_T, P, S)$$
donde:
- $V_N$ (o $N$): Conjunto finito de símbolos no terminales (*nonterminals*).
- $V_T$ (o $T$): Conjunto finito de símbolos terminales o tokens (*terminals*).
- $P$: Conjunto finito de producciones (*productions*) de la forma $A \rightarrow \alpha$, donde $A \in V_N$ y $\alpha \in (V_N \cup V_T)^*$.
- $S \in V_N$: Símbolo inicial de la gramática (*start symbol*).

El análisis sintáctico se clasifica fundamentalmente en dos grandes estrategias:
1. **Análisis Sintáctico Descendente (*Top-Down Parsing*)**: Construye el árbol sintáctico desde la raíz (el símbolo inicial $S$) hacia las hojas (la cadena de entrada $w$).
2. **Análisis Sintáctico Ascendente (*Bottom-Up Parsing*)**: Construye el árbol sintáctico desde las hojas (la cadena de entrada $w$) hacia la raíz ($S$), aplicando reducciones sucesivas correspondientes al reverso de una derivación más a la derecha (*rightmost derivation in reverse*).

A continuación se analizan a profundidad las cinco secciones fundamentales del texto guía.

---

## 2. SECCIÓN 4.4: ANÁLISIS SINTÁCTICO DESCENDENTE (*TOP-DOWN PARSING*)

### 2.1 Visión General y Descenso Recursivo (*Recursive-Descent Parsing*)
El objetivo del análisis descendente es encontrar una **derivación más a la izquierda** (*leftmost derivation*) para una cadena de entrada $w$:
$$S \Rightarrow_{lm}^* w$$

En cada paso, si el símbolo actual a expandir es un no terminal $A$, el parser debe seleccionar cuál de las producciones $A \rightarrow \alpha_1 \mid \alpha_2 \mid \dots \mid \alpha_k$ debe ser aplicada.

- **Descenso Recursivo General**: Puede requerir retroceso (*backtracking*). Si una alternativa elegida no coincide con la entrada más adelante, el parser debe deshacer las decisiones tomadas y probar la siguiente alternativa. El retroceso es computacionalmente ineficiente e inadecuado para la mayoría de compiladores comerciales.
- **Análisis Predictivo (*Predictive Parsing*)**: Es una forma eficiente de descenso recursivo o análisis dirigido por tabla que **no requiere backtracking**. Al observar únicamente el símbolo actual de entrada (símbolo de preanálisis o *lookahead symbol*), el parser determina unívocamente qué producción aplicar.

Para construir analizadores predictivos deterministas, es indispensable calcular dos conjuntos fundamentales: $\text{FIRST}$ y $\text{FOLLOW}$.

---

### 2.2 Conjuntos $\text{FIRST}$ y $\text{FOLLOW}$ (Sección 4.4.2)

#### 2.2.1 Definición de $\text{FIRST}(\alpha)$
Sea $\alpha \in (V_N \cup V_T)^*$ una cadena de símbolos gramaticales. Se define $\text{FIRST}(\alpha)$ como el conjunto de terminales que inician las cadenas derivadas a partir de $\alpha$:
$$\text{FIRST}(\alpha) = \{ a \in V_T \mid \alpha \Rightarrow^* a\beta \text{ para algún } \beta \in (V_N \cup V_T)^* \}$$

Si $\alpha \Rightarrow^* \epsilon$ (es decir, $\alpha$ puede derivar la cadena vacía $\epsilon$), entonces $\epsilon \in \text{FIRST}(\alpha)$.

#### Algoritmo para calcular $\text{FIRST}(X)$ para todo símbolo gramatical $X$:
1. **Caso Terminal**: Si $X$ es un terminal ($X \in V_T$), entonces:
   $$\text{FIRST}(X) = \{ X \}$$
2. **Producción $\epsilon$**: Si existe una producción $X \rightarrow \epsilon$, entonces:
   $$\epsilon \in \text{FIRST}(X)$$
3. **Caso No Terminal**: Si $X$ es un no terminal ($X \in V_N$) y existe una producción $X \rightarrow Y_1 Y_2 \dots Y_k$:
   - Para $i = 1, 2, \dots, k$:
     - Se añaden todos los terminales de $\text{FIRST}(Y_i) \setminus \{ \epsilon \}$ a $\text{FIRST}(X)$.
     - Si $\epsilon \notin \text{FIRST}(Y_i)$, se detiene la propagación (los símbolos posteriores $Y_{i+1}, \dots$ no aportarán terminales directos al inicio de la cadena generada por esta producción).
   - Si para todo $i \in \{1, \dots, k\}$ se cumple que $\epsilon \in \text{FIRST}(Y_i)$, entonces se añade $\epsilon$ a $\text{FIRST}(X)$ (indicando que $X$ es anulable o *nullable*).

#### Extensión de $\text{FIRST}$ a Cadenas de Símbolos $\text{FIRST}(X_1 X_2 \dots X_n)$:
Para una cadena cualquiera $\alpha = X_1 X_2 \dots X_n$:
1. Se añade a $\text{FIRST}(\alpha)$ todos los terminales de $\text{FIRST}(X_1) \setminus \{ \epsilon \}$.
2. Si $\epsilon \in \text{FIRST}(X_1)$, se añaden todos los terminales de $\text{FIRST}(X_2) \setminus \{ \epsilon \}$, y así sucesivamente mientras los prefijos continúen derivando $\epsilon$.
3. Si todos los símbolos $X_1, \dots, X_n$ contienen $\epsilon$ en sus respectivos conjuntos $\text{FIRST}$ (o si la cadena es vacía $\epsilon$), entonces $\epsilon \in \text{FIRST}(\alpha)$.

---

#### 2.2.2 Definición de $\text{FOLLOW}(A)$
Para un no terminal $A \in V_N$, $\text{FOLLOW}(A)$ se define como el conjunto de terminales $a$ que pueden aparecer inmediatamente a la derecha de $A$ en alguna forma sentencial derivada a partir del símbolo inicial $S$:
$$\text{FOLLOW}(A) = \{ a \in V_T \mid S \Rightarrow^* \alpha A a \beta \text{ para algunos } \alpha, \beta \in (V_N \cup V_T)^* \}$$

Además, si $A$ puede ser el símbolo más a la derecha en alguna forma sentencial ($S \Rightarrow^* \alpha A$), el marcador de fin de cadena $\$$ pertenece a $\text{FOLLOW}(A)$.

#### Algoritmo para calcular $\text{FOLLOW}(A)$ para todo $A \in V_N$:
1. **Regla del Símbolo Inicial**:
   $$\$ \in \text{FOLLOW}(S)$$
   donde $S$ es el símbolo inicial de la gramática y $\$$ es el marcador de fin de entrada (*input endmarker*).
2. **Propagación por Posición Contigua**:
   Si existe una producción $A \rightarrow \alpha B \beta$, entonces todo terminal en $\text{FIRST}(\beta)$ excepto $\epsilon$ se añade a $\text{FOLLOW}(B)$:
   $$(\text{FIRST}(\beta) \setminus \{ \epsilon \}) \subseteq \text{FOLLOW}(B)$$
3. **Propagación por Derivación Nula al Extremo Derecho**:
   Si existe una producción $A \rightarrow \alpha B$, o una producción $A \rightarrow \alpha B \beta$ donde $\epsilon \in \text{FIRST}(\beta)$ (es decir, $\beta \Rightarrow^* \epsilon$), entonces todo lo que pertenece a $\text{FOLLOW}(A)$ se añade a $\text{FOLLOW}(B)$:
   $$\text{FOLLOW}(A) \subseteq \text{FOLLOW}(B)$$

Las reglas 2 y 3 se aplican de manera iterativa hasta alcanzar un punto fijo (*fixed point*), donde ningún conjunto $\text{FOLLOW}$ experimente cambios.

---

### 2.3 Gramáticas LL(1) (Sección 4.4.3)
La denominación **LL(1)** significa:
- **L**: Escaneo de izquierda a derecha (*Left-to-right scan of the input*).
- **L**: Construcción de una derivación más a la izquierda (*Leftmost derivation*).
- **1**: Uso de un único símbolo de preanálisis (*1 lookahead token*).

#### Teorema de Caracterización LL(1):
Una gramática libre de contexto $G$ es LL(1) si y sólo si, para cualquier par de producciones distintas con la misma cabeza $A \rightarrow \alpha \mid \beta$, se cumplen simultáneamente las siguientes tres condiciones:
1. **Disyunción de Terminales Iniciales**:
   $$\text{FIRST}(\alpha) \cap \text{FIRST}(\beta) = \emptyset$$
   No existe ningún terminal $a$ que pueda iniciar una cadena derivada tanto de $\alpha$ como de $\beta$.
2. **Exclusividad de la Cadena Vacía**:
   A lo sumo una de las dos alternativas ($\alpha$ o $\beta$) puede derivar la cadena vacía $\epsilon$:
   $$\neg (\epsilon \in \text{FIRST}(\alpha) \land \epsilon \in \text{FIRST}(\beta))$$
3. **Disyunción con el Contexto Posterior**:
   Si $\beta \Rightarrow^* \epsilon$ (es decir, $\epsilon \in \text{FIRST}(\beta)$), entonces:
   $$\text{FIRST}(\alpha) \cap \text{FOLLOW}(A) = \emptyset$$
   De manera análoga, si $\alpha \Rightarrow^* \epsilon$, entonces $\text{FIRST}(\beta) \cap \text{FOLLOW}(A) = \emptyset$.

#### Algoritmo 4.31: Construcción de la Tabla de Análisis Predictivo $M[A, a]$
La tabla bidimensional $M$ indexa no terminales $A \in V_N$ en las filas y terminales $a \in (V_T \cup \{ \$ \})$ en las columnas.
Para cada producción $A \rightarrow \alpha$ de la gramática $G$:
1. Para cada terminal $a \in \text{FIRST}(\alpha)$ (con $a \neq \epsilon$):
   $$\text{Añadir } A \rightarrow \alpha \text{ a } M[A, a]$$
2. Si $\epsilon \in \text{FIRST}(\alpha)$:
   - Para cada símbolo $b \in \text{FOLLOW}(A)$ (donde $b$ puede ser un terminal o el marcador $\$$):
     $$\text{Añadir } A \rightarrow \alpha \text{ a } M[A, b]$$

**Decisión**: La gramática $G$ es **LL(1)** si y sólo si ninguna celda $M[A, a]$ contiene más de una producción. Si alguna celda contiene dos o más producciones, existe una colisión o ambigüedad de decisión predictiva y la gramática **no es LL(1)**.

---

### 2.4 Analizador Predictivo No Recursivo Dirigido por Tabla (Sección 4.4.4 / Algoritmo 4.34)
El analizador sintáctico descendente no recursivo utiliza una pila (*stack*) explícita que contiene símbolos gramaticales y un buffer de entrada con el marcador de fin de cadena $\$$.

```
                +---------------------------------------+
ENTRADA:        |  a_1  |  a_2  |  ...  |  a_n  |   $   |
                +---------------------------------------+
                                   ^
                                   | (puntero de preanálisis ip)
                +-------+
                |  X    |  (tope de la pila)
                |  Y    |
                |  ...  |
  PILA:         |  $    |
                +-------+
                    |
                    v
         +--------------------+
         |  PROGRAMA PARSER   | <---> TABLA DE PARSEO M[A, a]
         +--------------------+
```

#### Procedimiento de Ejecución:
1. **Inicialización**: La pila se inicializa con el marcador de fin de cadena en el fondo y el símbolo inicial de la gramática en el tope: `stack = ['$', S]`. El apuntador de entrada apunta al primer símbolo de la cadena $w\$$.
2. **Bucle Principal**: Sea $X$ el símbolo en el tope de la pila y $a$ el símbolo actual de preanálisis:
   - **Caso 1: Coincidencia Final**:
     Si $X = a = \$$, el análisis concluye exitosamente (*Accept*). La cadena pertenece al lenguaje.
   - **Caso 2: Coincidencia de Terminal (*Match*)**:
     Si $X = a \neq \$$, se extrae $X$ de la pila (`stack.pop()`) y se avanza el apuntador de entrada al siguiente símbolo.
   - **Caso 3: Error de Terminal**:
     Si $X \in V_T$ y $X \neq a$, se reporta error sintáctico (*Syntax Error*).
   - **Caso 4: Expansión de No Terminal**:
     Si $X \in V_N$:
     - Se consulta la entrada $M[X, a]$.
     - Si $M[X, a] = \{ X \rightarrow Y_1 Y_2 \dots Y_k \}$:
       - Se extrae $X$ de la pila (`stack.pop()`).
       - Si la producción no es $\epsilon$ ($Y_1 \dots Y_k \neq \epsilon$), se apilan los símbolos del cuerpo en orden inverso: se apila $Y_k$, luego $Y_{k-1}, \dots$, hasta apilar $Y_1$, de modo que $Y_1$ quede en el tope.
       - Si la producción es $X \rightarrow \epsilon$, no se apila ningún símbolo adicional.
     - Si $M[X, a] = \emptyset$ (celda vacía), se reporta error sintáctico.

---

## 3. SECCIÓN 4.5: ANÁLISIS SINTÁCTICO ASCENDENTE (*BOTTOM-UP PARSING*)

### 3.1 Reducciones (*Reductions*) (Sección 4.5.1)
El análisis ascendente reconstruye el árbol sintáctico comenzando desde las hojas (los tokens de entrada) y ascendiendo de manera iterativa hacia la raíz ($S$).

En cada etapa, el parser identifica una subcadena en la forma sentencial actual que coincide con el cuerpo de una producción $A \rightarrow \beta$, y la **reduce** reemplazándola por el no terminal $A$.
Formalmente, si:
$$S \Rightarrow_{rm}^* \alpha A w \Rightarrow_{rm} \alpha \beta w$$
la reducción consiste en transformar la forma sentencial derecha (*right-sentential form*) $\alpha \beta w$ de vuelta a $\alpha A w$. Una secuencia completa de reducciones que alcanza el símbolo inicial $S$ traza de forma exacta el **reverso de una derivación más a la derecha** (*rightmost derivation in reverse* o derivación canónica).

---

### 3.2 Poda de Mangos (*Handle Pruning*) (Sección 4.5.2)
- **Definición de Mango (*Handle*)**: Un *handle* de una forma sentencial derecha $\gamma = \alpha \beta w$ (donde $w$ contiene únicamente terminales) es una producción $A \rightarrow \beta$ y una posición en $\gamma$ donde la subcadena $\beta$ puede ser reemplazada por $A$ para obtener la forma sentencial derecha anterior en una derivación más a la derecha de $\gamma$.
- Si una gramática es ambigua, una misma forma sentencial puede admitir múltiples handles. En gramáticas no ambiguas, toda forma sentencial derecha válida posee exactamente un handle único.
- El proceso de encontrar sucesivamente el handle y reemplazarlo por su cabeza no terminal se conoce como **poda de mangos** (*handle pruning*).

---

### 3.3 El Modelo Shift-Reduce (Sección 4.5.3)
Un analizador ascendente tipo *shift-reduce* utiliza una pila para almacenar los símbolos de las formas sentenciales y un buffer de entrada:

Las cuatro acciones básicas de un parser shift-reduce son:
1. **Desplazar (*Shift*)**: Mover el símbolo actual de preanálisis de la entrada hacia el tope de la pila.
2. **Reducir (*Reduce*)**: El extremo derecho del handle se encuentra en el tope de la pila. El analizador identifica la longitud $k = |\beta|$ del handle, extrae esos $k$ elementos y apila la cabeza del no terminal $A$.
3. **Aceptar (*Accept*)**: Si la pila contiene únicamente el símbolo inicial $S$ (o en gramáticas aumentadas, tras reducir $S' \rightarrow S$) y la entrada está en $\$$, el análisis finaliza con éxito.
4. **Error (*Error*)**: Se detecta una discrepancia que indica que la cadena no pertenece al lenguaje.

---

### 3.4 Conflictos en el Análisis Shift-Reduce (Sección 4.5.4)
Durante el análisis shift-reduce pueden presentarse situaciones donde el parser no puede tomar una decisión determinista basada únicamente en el estado actual y el lookahead:
1. **Conflicto Desplazamiento-Reducción (*Shift/Reduce Conflict*)**: El parser no puede determinar si debe desplazar el siguiente símbolo de entrada o reducir los símbolos que se encuentran actualmente en el tope de la pila. Ejemplo clásico: el problema del *dangling-else*.
2. **Conflicto Reducción-Reducción (*Reduce/Reduce Conflict*)**: El parser sabe que debe realizar una reducción, pero existen dos o más producciones distintas que aplican al mismo contenido del tope de la pila. Es un síntoma común de gramáticas ambiguas o mal factorizadas.

---

## 4. SECCIÓN 4.6: INTRODUCCIÓN AL ANÁLISIS LR: SIMPLE LR (SLR)

### 4.1 Ventajas de los Analizadores LR (Sección 4.6.1)
Los analizadores **LR** ($L$: *Left-to-right scanning*, $R$: *Rightmost derivation in reverse*, $k$: *lookahead* de $k$ tokens) presentan ventajas fundamentales sobre los analizadores LL:
1. Son más generales y potentes: prácticamente todos los constructos de lenguajes de programación expresables mediante gramáticas libres de contexto pueden ser analizados mediante gramáticas LR.
2. Reconocen superconjuntos estrictos de los lenguajes LL: $\text{LL}(1) \subset \text{LR}(1)$.
3. Detectan errores sintácticos tan pronto como es teóricamente posible durante un escaneo de izquierda a derecha.

---

### 4.2 Ítems y el Autómata LR(0) (Sección 4.6.2)

#### 4.2.1 Ítems LR(0)
Un **ítem LR(0)** de una gramática $G$ es una producción de $G$ con un punto ($\cdot$) situado en alguna posición de su cuerpo.
- Indica cuánto del cuerpo de una producción ha sido ya reconocido por el parser (lo que está a la izquierda del punto) y qué se espera ver a continuación (a la derecha del punto).
- Para una producción $A \rightarrow X Y Z$, se generan cuatro ítems:
  $$[A \rightarrow \cdot X Y Z], \quad [A \rightarrow X \cdot Y Z], \quad [A \rightarrow X Y \cdot Z], \quad [A \rightarrow X Y Z \cdot]$$
- **Caso Especial $\epsilon$**: La producción vacía $A \rightarrow \epsilon$ genera **un único ítem**:
  $$[A \rightarrow \cdot]$$
  En este ítem, el punto ya se encuentra al final de la producción, lo que indica que una reducción por $A \rightarrow \epsilon$ está lista inmediatamente.

#### 4.2.2 Gramática Aumentada (*Augmented Grammar*)
Dada una gramática $G$ con símbolo inicial $S$, su **gramática aumentada** $G'$ se obtiene introduciendo un nuevo símbolo inicial $S'$ y la producción:
$$S' \rightarrow S$$
El propósito de $G'$ es definir unívocamente la condición de aceptación del parser: cuando el analizador reduce mediante $S' \rightarrow S$, el análisis concluye exitosamente.

---

#### 4.2.3 Función Clausura ($\text{CLOSURE}$)
Sea $I$ un conjunto de ítems para una gramática $G$. La función $\text{CLOSURE}(I)$ es el conjunto de ítems construido mediante las siguientes reglas:
1. Inicialmente, todo ítem en $I$ se incluye en $\text{CLOSURE}(I)$.
2. Si $[A \rightarrow \alpha \cdot B \beta]$ pertenece a $\text{CLOSURE}(I)$, donde $B$ es un no terminal, y $B \rightarrow \gamma$ es una producción de la gramática, entonces se añade el ítem $[B \rightarrow \cdot \gamma]$ a $\text{CLOSURE}(I)$, si no se encuentra ya presente.
3. Se repite el paso 2 hasta que no se puedan añadir más ítems nuevos.

#### 4.2.4 Función Transición ($\text{GOTO}$)
Sea $I$ un conjunto de ítems y $X$ un símbolo gramatical cualquiera ($X \in V_N \cup V_T$). Se define $\text{GOTO}(I, X)$ como la clausura del conjunto de todos los ítems $[A \rightarrow \alpha X \cdot \beta]$ tales que $[A \rightarrow \alpha \cdot X \beta] \in I$:
$$\text{GOTO}(I, X) = \text{CLOSURE}(\{ [A \rightarrow \alpha X \cdot \beta] \mid [A \rightarrow \alpha \cdot X \beta] \in I \})$$

Intuitivamente, $\text{GOTO}(I, X)$ representa el estado al que transita el autómata cuando el símbolo $X$ es procesado estando en el estado $I$.

#### 4.2.5 Colección Canónica de Conjuntos de Ítems LR(0)
La colección canónica $C = \{ I_0, I_1, \dots, I_m \}$ constituye el conjunto de estados del autómata finito determinista LR(0):
1. $I_0 = \text{CLOSURE}(\{ [S' \rightarrow \cdot S] \})$.
2. Se inicializa $C = \{ I_0 \}$.
3. Para cada conjunto de ítems $I \in C$ y cada símbolo gramatical $X \in (V_N \cup V_T)$:
   - Si $\text{GOTO}(I, X) \neq \emptyset$ y $\text{GOTO}(I, X) \notin C$, se añade $\text{GOTO}(I, X)$ a $C$.
4. Se repite el paso 3 hasta que ningún conjunto nuevo sea añadido a $C$.

---

### 4.3 Algoritmo de Análisis LR (Sección 4.6.3 / Algoritmo 4.44)
El analizador LR mantiene una pila de estados:
$$s_0 s_1 s_2 \dots s_m$$
donde cada $s_i$ es un estado del autómata LR(0) ($s_m$ es el estado en el tope). La tabla de análisis LR se compone de dos funciones:
1. $\text{ACTION}[s, a]$: Define la acción sintáctica cuando el estado en el tope es $s$ y el terminal de preanálisis es $a$ (con $a \in V_T \cup \{ \$ \}$).
2. $\text{GOTO}[s, A]$: Define el siguiente estado cuando se realiza una reducción a un no terminal $A \in V_N$.

#### Algoritmo de Ejecución:
Sea $s$ el estado en el tope de la pila y $a$ el símbolo actual de preanálisis:
1. Si $\text{ACTION}[s, a] = \text{shift } j$:
   - Se apila el estado $j$ en la pila de estados.
   - Se avanza el apuntador de entrada al siguiente símbolo.
2. Si $\text{ACTION}[s, a] = \text{reduce } A \rightarrow \beta$:
   - Sea $r = |\beta|$ la longitud del cuerpo de la producción. Se extraen $r$ estados de la pila (si $\beta = \epsilon$, se extraen 0 estados).
   - Sea $s'$ el nuevo estado en el tope de la pila tras el desapilado.
   - Se apila el estado $\text{GOTO}[s', A]$.
3. Si $\text{ACTION}[s, a] = \text{accept}$:
   - El análisis concluye exitosamente.
4. Si $\text{ACTION}[s, a] = \text{error}$:
   - Se invoca la rutina de recuperación o reporte de error sintáctico.

---

### 4.4 Construcción de Tablas SLR(1) (Sección 4.6.4 / Algoritmo 4.46)
El método **SLR(1)** (*Simple LR with 1 lookahead token*) utiliza los conjuntos de ítems LR(0) junto con la información de contexto proporcionada por los conjuntos $\text{FOLLOW}$ para resolver ambigüedades en las reducciones.

#### Algoritmo 4.46: Construcción de la Tabla de Parseo SLR:
Sea $C = \{ I_0, I_1, \dots, I_n \}$ la colección canónica de conjuntos de ítems LR(0) para la gramática aumentada $G'$. El estado $i$ corresponde al conjunto $I_i$. Las entradas de la tabla se determinan como sigue:

1. **Acciones de Desplazamiento (*Shift*)**:
   Para cada ítem $[A \rightarrow \alpha \cdot a \beta] \in I_i$, donde $a$ es un terminal ($a \in V_T$):
   $$\text{Si } \text{GOTO}(I_i, a) = I_j, \text{ entonces fijar } \text{ACTION}[i, a] = \text{shift } j$$

2. **Acciones de Reducción (*Reduce*)**:
   Para cada ítem de producción completa $[A \rightarrow \alpha \cdot] \in I_i$, donde $A \neq S'$:
   $$\text{Para todo } a \in \text{FOLLOW}(A) \text{ (incluyendo } \$ \text{)}, \text{ fijar } \text{ACTION}[i, a] = \text{reduce } A \rightarrow \alpha$$

3. **Acción de Aceptación (*Accept*)**:
   Si el ítem de inicio $[S' \rightarrow S \cdot] \in I_i$:
   $$\text{Fijar } \text{ACTION}[i, \$] = \text{accept}$$

4. **Transiciones $\text{GOTO}$ para No Terminales**:
   Para cada no terminal $A \in V_N$:
   $$\text{Si } \text{GOTO}(I_i, A) = I_j, \text{ entonces fijar } \text{GOTO}[i, A] = j$$

5. **Entradas no definidas**: Cualquier celda no asignada en $\text{ACTION}$ o $\text{GOTO}$ se marca como $\text{error}$.

#### Criterio de Gramática SLR(1):
Una gramática es **SLR(1)** si y sólo si la tabla $\text{ACTION}$ resultante no contiene ningún conflicto:
- Ninguna celda contiene tanto un desplazamiento como una reducción (ausencia de conflictos *shift/reduce*).
- Ninguna celda contiene dos o más reducciones diferentes (ausencia de conflictos *reduce/reduce*).

---

### 4.5 Prefijos Viables (*Viable Prefixes*) (Sección 4.6.5)
- **Definición**: Un *prefijo viable* es un prefijo de una forma sentencial derecha que puede aparecer en la pila de un analizador shift-reduce sin sobrepasar el extremo derecho del handle correspondiente.
- Mientras la pila contenga un prefijo viable, el parser no ha cometido un error irreversible y puede continuar operando hacia una reducción válida.
- **Teorema Fundamental**: El autómata LR(0) construido mediante la colección canónica de ítems reconoce exactamente el lenguaje regular de todos los prefijos viables de la gramática.

---

## 5. SECCIÓN 5.1: DEFINICIONES DIRIGIDAS POR LA SINTAXIS (*SYNTAX-DIRECTED DEFINITIONS - SDDs*)

### 5.1 Concepto de SDD y Tipos de Atributos (Sección 5.1.1)
Una **Definición Dirigida por la Sintaxis (SDD)** es una gramática libre de contexto complementada con atributos asociados a los símbolos gramaticales y reglas semánticas (*semantic rules*) asociadas a las producciones.

Si $X$ es un símbolo y $a$ es un atributo asociado a $X$, el valor de dicho atributo en un nodo del árbol sintáctico se denota $X.a$. Los atributos se clasifican formalmente en dos categorías:

#### 1. Atributos Sintetizados (*Synthesized Attributes*):
Un atributo $A.s$ en un nodo $N$ del árbol sintáctico es **sintetizado** si su valor se calcula exclusivamente a partir de los valores de los atributos en los **hijos de $N$** y de otros atributos del propio nodo $N$.
- Flujo de información: **Ascendente** (de abajo hacia arriba en el árbol sintáctico).
- Si la producción es $A \rightarrow X_1 X_2 \dots X_k$, una regla semántica sintetizada define un atributo de la cabeza:
  $$A.s = f(X_1.a_1, X_2.a_2, \dots, X_k.a_k, A.a_0)$$

#### 2. Atributos Heredados (*Inherited Attributes*):
Un atributo $B.i$ en un nodo $N$ del árbol sintáctico es **heredado** si su valor se calcula a partir de los valores de los atributos en el **padre de $N$**, en los **hermanos de $N$** y en el propio nodo $N$.
- Flujo de información: **Descendente y lateral** (de arriba hacia abajo o entre hermanos).
- Si la producción es $A \rightarrow X_1 X_2 \dots X_j \dots X_k$, una regla semántica heredada define un atributo de uno de los símbolos del cuerpo:
  $$X_j.i = f(A.a_0, X_1.a_1, \dots, X_k.a_k)$$

#### Restricciones Fundamentales:
- **Terminales**: Los símbolos terminales únicamente poseen atributos sintetizados provistos por el analizador léxico (por ejemplo, el valor léxico `lexval`). Los terminales **nunca** tienen atributos heredados calculados por reglas semánticas de una producción.
- **Símbolo Inicial**: El símbolo inicial $S$ de la gramática **no debe poseer atributos heredados**, dado que no tiene nodo padre que le proporcione contexto superior.

---

### 5.2 Árboles Sintácticos Anotados (*Annotated Parse Trees*) (Sección 5.1.2)
Un árbol sintáctico anotado (o decorado) es un árbol de derivación en el cual cada nodo contiene los valores concretos calculados para cada uno de los atributos asociados a su símbolo gramatical correspondiente.

---

## 6. SECCIÓN 5.2: ÓRDENES DE EVALUACIÓN PARA SDDs

### 6.1 Grafos de Dependencia (*Dependency Graphs*) (Sección 5.2.1)
El grafo de dependencias formaliza las relaciones de precedencia computacional impuestas por las reglas semánticas en un árbol sintáctico concreto:
- **Vértices**: Para cada nodo $N$ del árbol sintáctico y cada atributo $a$ asociado a su símbolo gramatical, existe un vértice denotado $N.a$.
- **Aristas Dirigidas**: Si una regla semántica para calcular el valor del atributo $X.b$ utiliza como argumento el valor del atributo $Y.c$, se traza una arista dirigida desde el atributo utilizado hacia el atributo definido:
  $$Y.c \longrightarrow X.b$$
  Esta dirección indica inequívocamente que **$Y.c$ debe evaluarse antes que $X.b$**.

---

### 6.2 Ordenamiento Topológico y Detección de Circularidad (Sección 5.2.2)
- **Definición de SDD Circular**: Si para algún árbol sintáctico el grafo de dependencias contiene un **ciclo dirigido** (por ejemplo, $u \rightarrow v \rightarrow \dots \rightarrow u$), la SDD es **circular**. En tal caso, no existe ningún ordenamiento secuencial en el cual los atributos puedan ser evaluados, y el compilador debe abortar reportando una definición circular.
- **Orden Topológico (*Topological Sort*)**: Si el grafo de dependencias es un Grafo Dirigido Acíclico (*DAG*), cualquier ordenamiento topológico de sus vértices define un orden de evaluación válido y consistente:
  $$\text{Si existe una arista } u \rightarrow v, \text{ entonces } u \text{ aparece antes que } v \text{ en el orden topológico.}$$

#### Algoritmo de Kahn para Ordenamiento Topológico:
1. Calcular el grado de entrada (*in-degree*) de cada vértice $v$.
2. Insertar en una cola $Q$ todos los vértices con grado de entrada 0 (aquellos que no dependen de ningún otro atributo, como los `lexval` de los terminales o constantes iniciales).
3. Mientras $Q$ no esté vacía:
   - Extraer un vértice $u$ de $Q$ y añadirlo al orden de evaluación.
   - Para cada arista dirigida $(u, v)$: decrementar el grado de entrada de $v$.
   - Si el grado de entrada de $v$ se reduce a 0, insertar $v$ en $Q$.
4. Si al finalizar el algoritmo el orden contiene todos los vértices del grafo, la evaluación es factible. Si no contiene todos los vértices, existe al menos un ciclo en el grafo, confirmando que la definición es circular.

---

### 6.3 Definiciones S-Atribuidas (*S-Attributed Definitions*) (Sección 5.2.3)
Una SDD es **S-atribuida** si **todos sus atributos son sintetizados**.
- **Propiedad de Evaluación**: Como no existen dependencias descendentes ni laterales, los atributos pueden ser evaluados en un recorrido post-orden (*bottom-up*).
- **Integración con Parsers Ascendentes**: Una SDD S-atribuida puede evaluarse de manera natural y directa durante el análisis LR, calculando las reglas semánticas inmediatamente al ejecutar cada reducción en la pila del parser.

---

### 6.4 Definiciones L-Atribuidas (*L-Attributed Definitions*) (Sección 5.2.4)
La clase de definiciones **L-atribuidas** (*L* de *Left-to-right*) amplía a las definiciones S-atribuidas permitiendo el uso restringido de atributos heredados sin inducir ciclos.

#### Definición Formal:
Una SDD es L-atribuida si cada atributo es:
1. Sintetizado, o bien
2. Heredado, sujeto a la siguiente restricción: para toda producción:
   $$A \rightarrow X_1 X_2 \dots X_n$$
   un atributo heredado $X_j.i$ de un símbolo $X_j$ en el cuerpo sólo puede depender de:
   - Los atributos heredados de la cabeza $A$ ($A.i$).
   - Atributos (sintetizados o heredados) de los símbolos $X_1, X_2, \dots, X_{j-1}$ que se encuentran situados **estrictamente a la izquierda** de $X_j$ en el cuerpo de la producción.
   - Otros atributos del propio $X_j$, siempre que no se formen ciclos de dependencia interna.

#### Consecuencia Arquitectónica:
Toda definición L-atribuida puede ser evaluada en una **única pasada en profundidad de izquierda a derecha** (*depth-first, left-to-right traversal*), lo que la hace compatible de forma directa con analizadores predictivos descendentes LL(1).

---

## 7. MATRIZ COMPARATIVA Y SÍNTESIS

| Característica | Top-Down / LL(1) (Sec 4.4) | Bottom-Up / SLR(1) (Sec 4.5 - 4.6) | SDD S-Atribuida (Sec 5.2.3) | SDD L-Atribuida (Sec 5.2.4) |
| :--- | :--- | :--- | :--- | :--- |
| **Dirección del Análisis** | Descendente (Raíz $\rightarrow$ Hojas) | Ascendente (Hojas $\rightarrow$ Raíz) | Ascendente (Post-orden) | Recorrido Izq. a Der. (Pre/In/Post) |
| **Derivación Asociada** | Derivación más a la izquierda ($lm$) | Reverso de más a la derecha ($rm^{-1}$) | Correspondiente al parseo | Compatible con LL y LR |
| **Estructura Clave** | Pila de símbolos + Tabla $M[A, a]$ | Pila de estados + Tablas $\text{ACTION}/\text{GOTO}$ | Pila semántica en reducciones | Grafo de dependencias / Pasada única |
| **Condición de No Conflicto** | $\text{FIRST}(\alpha) \cap \text{FIRST}(\beta) = \emptyset$, etc. | Sin colisiones *shift/reduce* ni *reduce/reduce* | N/A (atributos libres de ciclo) | Dependencias heredadas sólo hacia la izquierda |
| **Tipos de Atributos Admitidos** | N/A | N/A | Exclusivamente sintetizados | Sintetizados y heredados hacia la izquierda |

---
Este marco teórico provee las bases matemáticas y algorítmicas exactas para la implementación modular del proyecto.
