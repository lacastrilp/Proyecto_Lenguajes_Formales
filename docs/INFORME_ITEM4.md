# Informe Tecnico: Analizadores Sintacticos LL(1), SLR(1) y Evaluador SDD
## Curso: Lenguajes Formales y Compiladores (2026-2)
### Integrantes del Grupo:
- Estudiante 1: lacastrilp (lacastrilp@eafit.edu.co)
- Estudiante 2: [Nombre Completo del Estudiante 2]
- Estudiante 3: [Nombre Completo del Estudiante 3 (si aplica)]

---

## 1. Algoritmos y Estructuras de Datos

Basamos nuestra solucion en los algoritmos del texto de Aho, Lam, Sethi y Ullman (Compilers: Principles, Techniques, and Tools, 2da edicion, 2006). Organizamos el codigo dentro del paquete `src/` utilizando unicamente la biblioteca estandar de Python.

### 1.1 Referencias al Libro Guia

1. Calculo de FIRST y FOLLOW (Seccion 4.4.2):
En `src/first_follow.py` implementamos el calculo iterativo de punto fijo sobre diccionarios de conjuntos (`dict[str, set[str]]`). Para FIRST evaluamos simbolo a simbolo en las producciones, acumulando terminales hasta encontrar un simbolo no anulable. En FOLLOW inicializamos con `$` en el simbolo inicial y propagamos terminales segun las ocurrencias de no terminales en los cuerpos de las producciones.

2. Tabla Predictiva LL(1) (Algoritmo 4.31, Seccion 4.4.3):
En `src/ll1_parser.py` construimos la tabla `M[A, a]` recorriendo cada alternativa $A \rightarrow \alpha$. Asignamos la produccion a las celdas indexadas por los terminales de $\text{FIRST}(\alpha)$. Si $\epsilon \in \text{FIRST}(\alpha)$, asignamos la produccion a los terminales de $\text{FOLLOW}(A)$. Si una celda recibe mas de una produccion, marcamos la gramatica como no LL(1).

3. Analizador Predictivo no Recursivo (Algoritmo 4.34, Seccion 4.4.4):
La clase `LL1Parser` maneja una lista de Python como pila de simbolos, inicializada con `['$', S]`. Al leer la entrada token a token, reemplaza no terminales por el cuerpo inverso de la produccion dictada por la tabla. Durante este proceso enlazamos nodos de `ParseTreeNode` para construir el arbol de derivacion.

4. Automata LR(0) y Tablas SLR(1) (Algoritmos 4.44 y 4.46, Secciones 4.6.2 a 4.6.4):
En `src/slr1_parser.py` aumentamos la gramatica con $S' \rightarrow S$. Representamos cada item LR(0) mediante una tupla `(head, body, dot_index)`. La funcion `closure` expande no terminales a la derecha del punto, y `goto` calcula las transiciones de estados. La coleccion canonica de conjuntos de items se almacena en una lista de conjuntos congelados (`frozenset`). La tabla `ACTION` registra desplazamientos hacia nuevos estados y reducciones en terminales pertenecientes a $\text{FOLLOW}(A)$. Si detectamos colisiones shift/reduce o reduce/reduce, marcamos la gramatica como no SLR(1). El metodo `parse` procesa la entrada manipulando una pila de estados enteros y reduciendo handles para generar el arbol sintactico.

5. Evaluador de Definiciones Dirigidas por la Sintaxis (Secciones 5.1 y 5.2):
En `src/sdd.py` y `src/sdd_evaluator.py` separamos las reglas semanticas del motor de calculo. Representamos cada regla como un objeto `SemanticRule` con indices de simbolos relativos y funciones de evaluacion. La clase `SDDEvaluator` recorre el arbol concreto generado por cualquiera de los dos parsers, instancia los vertices $(node\_id, attribute)$ y agrega aristas dirigidas desde los atributos requeridos hacia los atributos calculados. Aplicamos el algoritmo de Kahn con una cola `collections.deque` para obtener el orden topologico. Si la cola se vacia antes de procesar todos los vertices, ejecutamos una busqueda en profundidad (DFS) con marcas de tres estados (blanco, gris y negro) para aislar y reportar el ciclo exacto.

### 1.2 Estructuras de Datos Empleadas

- Tablas de parseo y conjuntos: Diccionarios hash (`dict`) combinados con `set` y `frozenset` para indexar celdas $(estado, terminal)$ y calcular uniones e intersecciones en tiempo promedio $O(1)$.
- Pilas de parsing: Listas dinamicas de Python (`list`) operadas con `append` y `pop` para representar la pila de analisis sintactico y la pila auxiliar de arboles.
- Grafo de dependencias: Lista de adyacencias representada con `defaultdict(set)` y contador de grados de entrada `defaultdict(int)`.
- Arbol sintactico concreto: Nodos `ParseTreeNode` con identificador entero consecutivo, lista ordenada de hijos, referencia a la produccion aplicada y diccionario interno de valores de atributos.

---

## 2. Items 1 y 2: Gramatica Propia, Analisis y Traza

Disenamos una gramatica propia para modelar secuencias de identificadores `b` delimitadas por comas, asegurando que cumpla el formato de la Seccion 2.2 sin espacios internos en las alternativas:

```text
3
S -> L
L -> bR
R -> ,L e
```

Simbolos no terminales: $S, L, R$.
Simbolos terminales: `b`, `,`.
Cadena vacia: `e`.

### 2.1 Conjuntos FIRST y FOLLOW

El comando `python3 main.py --sets` genera los siguientes conjuntos ordenados:

```text
First(L) = {b}
First(R) = {,, e}
First(S) = {b}
Follow(L) = {$}
Follow(R) = {$}
Follow(S) = {$}
```

### 2.2 Tabla Predictiva LL(1)

Construimos la tabla predictiva aplicando el Algoritmo 4.31:

| No Terminal | `b` | `,` | `$` |
| :---: | :---: | :---: | :---: |
| **S** | $S \rightarrow L$ | | |
| **L** | $L \rightarrow bR$ | | |
| **R** | | $R \rightarrow ,L$ | $R \rightarrow e$ |

Ninguna celda contiene mas de una produccion. La gramatica es LL(1).

### 2.3 Coleccion Canonica de Items LR(0) y Tabla SLR(1)

Aumentamos la gramatica con la produccion $S' \rightarrow S$. La coleccion canonica consta de 7 estados:

- Estado 0:
  $S' \rightarrow \cdot S$
  $S \rightarrow \cdot L$
  $L \rightarrow \cdot bR$

- Estado 1:
  $S' \rightarrow S \cdot$

- Estado 2:
  $S \rightarrow L \cdot$

- Estado 3:
  $L \rightarrow b \cdot R$
  $R \rightarrow \cdot ,L$
  $R \rightarrow \cdot$

- Estado 4:
  $L \rightarrow bR \cdot$

- Estado 5:
  $R \rightarrow , \cdot L$
  $L \rightarrow \cdot bR$

- Estado 6:
  $R \rightarrow ,L \cdot$

Transiciones GOTO:
- $\text{GOTO}(0, S) = 1$
- $\text{GOTO}(0, L) = 2$
- $\text{GOTO}(3, R) = 4$
- $\text{GOTO}(5, L) = 6$

Tabla de analisis SLR(1):

| Estado | `b` | `,` | `$` | `S` | `L` | `R` |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **0** | shift 3 | | | 1 | 2 | |
| **1** | | | accept | | | |
| **2** | | | reduce $S \rightarrow L$ | | | |
| **3** | | shift 5 | reduce $R \rightarrow e$ | | | 4 |
| **4** | | | reduce $L \rightarrow bR$ | | | |
| **5** | shift 3 | | | | 6 | |
| **6** | | | reduce $R \rightarrow ,L$ | | | |

La tabla no contiene conflictos shift/reduce ni reduce/reduce. La gramatica es SLR(1).

### 2.4 Traza Paso a Paso con el Parser SLR(1)

Probamos el parser ascendente con una cadena aceptada (`b,b`) y una cadena rechazada (`b,`).

#### Traza de la cadena aceptada: `b,b$`

1. Pila: `[0]`, Entrada: `b,b$`.  
   Accion: $\text{ACTION}[0, b] = \text{shift } 3$.
2. Pila: `[0, 3]`, Entrada: `,b$`.  
   Accion: $\text{ACTION}[3, ,] = \text{shift } 5$.
3. Pila: `[0, 3, 5]`, Entrada: `b$`.  
   Accion: $\text{ACTION}[5, b] = \text{shift } 3$.
4. Pila: `[0, 3, 5, 3]`, Entrada: `$`.  
   Accion: $\text{ACTION}[3, \$] = \text{reduce } R \rightarrow e$ (longitud 0).  
   Tope expuesto: 3. $\text{GOTO}[3, R] = 4$. Apilar 4.
5. Pila: `[0, 3, 5, 3, 4]`, Entrada: `$`.  
   Accion: $\text{ACTION}[4, \$] = \text{reduce } L \rightarrow bR$ (longitud 2).  
   Desapilar 4 y 3. Tope expuesto: 5. $\text{GOTO}[5, L] = 6$. Apilar 6.
6. Pila: `[0, 3, 5, 6]`, Entrada: `$`.  
   Accion: $\text{ACTION}[6, \$] = \text{reduce } R \rightarrow ,L$ (longitud 2).  
   Desapilar 6 y 5. Tope expuesto: 3. $\text{GOTO}[3, R] = 4$. Apilar 4.
7. Pila: `[0, 3, 4]`, Entrada: `$`.  
   Accion: $\text{ACTION}[4, \$] = \text{reduce } L \rightarrow bR$ (longitud 2).  
   Desapilar 4 y 3. Tope expuesto: 0. $\text{GOTO}[0, L] = 2$. Apilar 2.
8. Pila: `[0, 2]`, Entrada: `$`.  
   Accion: $\text{ACTION}[2, \$] = \text{reduce } S \rightarrow L$ (longitud 1).  
   Desapilar 2. Tope expuesto: 0. $\text{GOTO}[0, S] = 1$. Apilar 1.
9. Pila: `[0, 1]`, Entrada: `$`.  
   Accion: $\text{ACTION}[1, \$] = \text{accept}$.  
   Resultado: `yes`.

#### Traza de la cadena rechazada: `b,$`

1. Pila: `[0]`, Entrada: `b,$`. $\text{ACTION}[0, b] = \text{shift } 3$.
2. Pila: `[0, 3]`, Entrada: `,$`. $\text{ACTION}[3, ,] = \text{shift } 5$.
3. Pila: `[0, 3, 5]`, Entrada: `$`.  
   La celda $\text{ACTION}[5, \$]$ esta vacia (error sintactico).  
   Resultado: `no`.

---

## 3. Item 3: Evaluador de la Definicion Dirigida por la Sintaxis (SDD)

### 3.1 Gramatica Seleccionada (Condiciones G1, G2 y G3)

Seleccionamos una gramatica que modela listas binarias con evaluacion de peso segun la profundidad de anidamiento de parentesis:

```text
4
S -> L
L -> BR
R -> +L e
B -> (L) 0 1
```

- G1: Cumple las convenciones de la Seccion 2.2 y es tanto LL(1) como SLR(1).
- G2: Posee 4 no terminales ($S, L, B, R \ge 3$), 7 producciones ($\ge 6$), y los no terminales $L$ y $R$ son recursivos.
- G3: Es una gramatica original no tomada del libro ni de las guias del curso.

### 3.2 Tabla de Atributos

Verificamos que el simbolo inicial $S$ no posea atributos heredados:

| Simbolo | Atributo | Tipo de Atributo | Tipo de Dato | Descripcion Semantica |
| :---: | :---: | :---: | :---: | :--- |
| **S** | `val` | Sintetizado | Entero | Valor numerico final de la expresion calculada. |
| **S** | `max_d` | Sintetizado | Entero | Nivel maximo de profundidad de parentesis alcanzado. |
| **L** | `d` | Heredado | Entero | Profundidad actual de anidamiento recibida del contexto. |
| **L** | `val` | Sintetizado | Entero | Suma de los valores calculados en la lista de terminos. |
| **L** | `max_d` | Sintetizado | Entero | Profundidad maxima registrada en la subexpresion $L$. |
| **R** | `d` | Heredado | Entero | Profundidad heredada para el resto de la adicion. |
| **R** | `val` | Sintetizado | Entero | Valor sumado de los terminos restantes. |
| **R** | `max_d` | Sintetizado | Entero | Profundidad maxima en los terminos restantes. |
| **B** | `d` | Heredado | Entero | Profundidad heredada para el bloque o bit actual. |
| **B** | `val` | Sintetizado | Entero | Valor numerico ($2^d$ para `1`, $0$ para `0`). |
| **B** | `max_d` | Sintetizado | Entero | Profundidad maxima alcanzada en el bloque. |
| **Terminales** | `lexval` | Sintetizado | Caracter | Caracter constante entregado por el escaner. |

### 3.3 Reglas Semanticas (Formato Figura 5.1 del Dragon Book)

| Produccion | Reglas Semanticas |
| :--- | :--- |
| $S \rightarrow L$ | $L.d = 0$<br>$S.val = L.val$<br>$S.max\_d = L.max\_d$ |
| $L \rightarrow B R$ | $B.d = L.d$<br>$R.d = L.d$<br>$L.val = B.val + R.val$<br>$L.max\_d = \max(B.max\_d, R.max\_d)$ |
| $R \rightarrow + L$ | $L.d = R.d$<br>$R.val = L.val$<br>$R.max\_d = L.max\_d$ |
| $R \rightarrow \epsilon$ | $R.val = 0$<br>$R.max\_d = R.d$ |
| $B \rightarrow ( L )$ | $L.d = B.d + 1$<br>$B.val = L.val$<br>$B.max\_d = L.max\_d$ |
| $B \rightarrow 0$ | $B.val = 0$<br>$B.max\_d = B.d$ |
| $B \rightarrow 1$ | $B.val = 2^{B.d}$<br>$B.max\_d = B.d$ |

### 3.4 Clasificacion de la SDD

Determinamos que:
1. No es S-atribuida porque utiliza el atributo heredado $d$ en los no terminales $L$, $B$ y $R$.
2. Es L-atribuida porque cada atributo heredado en los cuerpos de las producciones depende exclusivamente de atributos heredados de la cabeza ($L.d \rightarrow B.d$, $L.d \rightarrow R.d$, $R.d \rightarrow L.d$) o del valor del padre sumado a una constante ($B.d + 1 \rightarrow L.d$), sin depender de simbolos situados a su derecha ni de atributos sintetizados de sus hermanos.

### 3.5 Ejemplo Calculado a Mano: Cadena `(1+0)` (5 Terminales)

Probamos a mano la cadena `(1+0)`, que contiene 5 terminales: `(`, `1`, `+`, `0`, `)`.

#### Arbol Sintactico Anotado Resultante:

```text
S {max_d=1, val=2}
  L_16 {d=0, max_d=1, val=2}
    B_13 {d=0, max_d=1, val=2}
      ( {lexval='('}
      L_11 {d=1, max_d=1, val=2}
        B_3 {d=1, max_d=1, val=2}
          1 {lexval='1'}
        R_10 {d=1, max_d=1, val=0}
          + {lexval='+'}
          L_9 {d=1, max_d=1, val=0}
            B_6 {d=1, max_d=1, val=0}
              0 {lexval='0'}
            R_8 {d=1, max_d=1, val=0}
              e {lexval='e'}
      ) {lexval=')'}
    R_15 {d=0, max_d=0, val=0}
      e {lexval='e'}
```

#### Grafo de Dependencias (Aristas "Atributo Usado -> Atributo Definido"):

- Asignacion inicial:
  $L_{16}.d = 0$
  $L_{16}.d \rightarrow B_{13}.d$
  $L_{16}.d \rightarrow R_{15}.d$
- Bloque exterior y parentesis:
  $B_{13}.d \rightarrow L_{11}.d$ (regla $L.d = B.d + 1$)
  $L_{11}.d \rightarrow B_3.d$
  $L_{11}.d \rightarrow R_{10}.d$
- Bit 1 interno ($d=1$):
  $B_3.d \rightarrow B_3.val$ ($2^1 = 2$)
  $B_3.d \rightarrow B_3.max\_d$ ($1$)
- Resto de la suma interior ($+0$):
  $R_{10}.d \rightarrow L_9.d$
  $L_9.d \rightarrow B_6.d$
  $L_9.d \rightarrow R_8.d$
  $B_6.d \rightarrow B_6.val$ ($0$)
  $B_6.d \rightarrow B_6.max\_d$ ($1$)
  $R_8.d \rightarrow R_8.max\_d$ ($1$)
  $R_8.val = 0$
  $B_6.val, R_8.val \rightarrow L_9.val$ ($0 + 0 = 0$)
  $B_6.max\_d, R_8.max\_d \rightarrow L_9.max\_d$ ($\max(1, 1) = 1$)
  $L_9.val \rightarrow R_{10}.val$ ($0$)
  $L_9.max\_d \rightarrow R_{10}.max\_d$ ($1$)
- Sintesis en $L_{11}$:
  $B_3.val, R_{10}.val \rightarrow L_{11}.val$ ($2 + 0 = 2$)
  $B_3.max\_d, R_{10}.max\_d \rightarrow L_{11}.max\_d$ ($\max(1, 1) = 1$)
- Sintesis hacia la raiz:
  $L_{11}.val \rightarrow B_{13}.val$ ($2$)
  $L_{11}.max\_d \rightarrow B_{13}.max\_d$ ($1$)
  $R_{15}.d \rightarrow R_{15}.max\_d$ ($0$), $R_{15}.val = 0$
  $B_{13}.val, R_{15}.val \rightarrow L_{16}.val$ ($2 + 0 = 2$)
  $B_{13}.max\_d, R_{15}.max\_d \rightarrow L_{16}.max\_d$ ($\max(1, 0) = 1$)
  $L_{16}.val \rightarrow S_{17}.val$ ($2$)
  $L_{16}.max\_d \rightarrow S_{17}.max\_d$ ($1$)

#### Orden Topologico:

El algoritmo de Kahn produce el siguiente orden de evaluacion valido:

`R_8.val, e_7.lexval, 1_2.lexval, +_4.lexval, (_1.lexval, )_12.lexval, R_15.val, L_16.d, e_14.lexval, B_6.val, 0_5.lexval, R_15.d, B_13.d, L_9.val, R_15.max_d, L_11.d, R_10.val, B_3.d, R_10.d, B_3.max_d, B_3.val, L_9.d, L_11.val, B_6.d, R_8.d, B_13.val, B_6.max_d, R_8.max_d, L_16.val, L_9.max_d, S_17.val, R_10.max_d, L_11.max_d, B_13.max_d, L_16.max_d, S_17.max_d`

Valor final de `val` en $S$: **2**.

### 3.6 Resultados de Pruebas (Paso 6)

Ejecutamos la suite con los casos exigidos por el enunciado:

1. Cadena mas corta (`0`): genera `val = 0, max_d = 0`.
2. Cadena simple (`1`): genera `val = 1, max_d = 0` ($2^0 = 1$).
3. Suma simple (`1+0`): genera `val = 1, max_d = 0`.
4. Cadena con anidamiento (`(1)`): genera `val = 2, max_d = 1` ($2^1 = 2$).
5. Cadena con anidamiento profundo (`((1+0)+(1))`): genera `val = 8, max_d = 2` ($2^2 + 2^2 = 8$).
6. Cadena sintacticamente invalida (`1++0`): rechazada de inmediato imprimiendo `no`.
7. Deteccion de definicion circular (`--circular`): alteramos la regla de $S \rightarrow L$ para forzar $L.d = S.val + 1$. Al procesar la entrada `1`, el evaluador detecta la imposibilidad de resolver el orden topologico y reporta el ciclo:  
   `Ciclo identificado: L_5.val -> S_6.val -> L_5.d -> B_2.d -> B_2.val -> L_5.val`

---

## 4. Dificultades Encontradas y Soluciones

1. Manejo de reducciones epsilon en SLR(1):
Las producciones de la forma $A \rightarrow \epsilon$ tienen longitud cero. Si el parser desapila simbolos como en una reduccion ordinaria, altera el estado actual de la pila. Solucionamos esto asegurando que para producciones vacias se extraigan 0 estados de la pila, consultando directamente $\text{GOTO}[tope, A]$ y apilando una hoja etiquetada con `'e'`.

2. Desacoplamiento estricto de la SDD frente al evaluador:
El requisito 5.1 exige que el evaluador no conozca nombres de atributos particulares como `val` o `d`. Lo resolvimos creando la clase `SemanticRule`, donde cada regla se modela como una tupla de indice destino, funcion de computo y lista de dependencias referenciadas por posicion relativa dentro de la produccion.

3. Separacion de alternativas en el parser de gramaticas:
El enunciado estipula que las alternativas van separadas por espacios en blanco y que los simbolos dentro de una alternativa no llevan espacios. Al redactar las primeras pruebas escribimos `L -> b R`, lo cual provoco que el parser interpretara `b` y `R` como dos alternativas independientes en lugar de una secuencia contigua. Corregimos el parser y las gramaticas de prueba escribiendo `L -> bR` y `R -> ,L e`.

4. Resolucion de rutas relativas:
Al ejecutar `main.py` y `sdd_main.py` desde carpetas distintas, el acceso a archivos de gramaticas podia fallar si el usuario no especificaba la ruta completa. Incorporamos una verificacion con `os.path.exists`: si el archivo no se halla en el directorio actual, el programa lo busca automaticamente dentro de la carpeta `examples/`.
