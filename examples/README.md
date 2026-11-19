# Ejemplos de Gramáticas y Cadenas de Prueba

Este directorio contiene las gramáticas de prueba y los archivos de cadenas utilizados para verificar la implementación de los analizadores sintácticos LL(1), SLR(1) y el evaluador de SDD.

---

## 1. `grammar_ex1.txt` (Ejemplo 1 del Enunciado)
- **Descripción**: Gramática de expresiones aritméticas con precedencia y asociatividad estándar (`+`, `*`, paréntesis e identificador `i`).
- **Propiedad formal**: Es **SLR(1)** pero **NO es LL(1)** debido a la presencia de recursión por la izquierda en las producciones de $S$ y $T$.
- **Contenido**:
  ```text
  3
  S -> S+T T
  T -> T*F F
  F -> (S) i
  ```
- **Cadenas de prueba sugeridas**:
  - `i+i` $\rightarrow$ `yes`
  - `(i)` $\rightarrow$ `yes`
  - `(i+i)*i)` $\rightarrow$ `no` (paréntesis sin balancear)

---

## 2. `grammar_ex2.txt` (Ejemplo 2 del Enunciado)
- **Descripción**: Gramática que modela estructuras anidadas y alternativas con terminales `a`, `b`, `c`, `d`, `e`.
- **Propiedad formal**: Es **tanto LL(1) como SLR(1)**. Permite al usuario seleccionar interactivamente qué parser utilizar (`T` para LL(1), `B` para SLR(1)).
- **Contenido**:
  ```text
  3
  S -> AB
  A -> aA d
  B -> bBc e
  ```
- **Conjuntos First y Follow** (`--sets`):
  - $\text{First}(A) = \{a, d\}$, $\text{First}(B) = \{b, e\}$, $\text{First}(S) = \{a, d\}$
  - $\text{Follow}(A) = \{b, \$\}$, $\text{Follow}(B) = \{c, \$\}$, $\text{Follow}(S) = \{\$\}$
- **Cadenas de prueba sugeridas**:
  - `d` $\rightarrow$ `yes`
  - `adbc` $\rightarrow$ `yes`
  - `a` $\rightarrow$ `no`

---

## 3. `grammar_ex3.txt` (Ejemplo 3 del Enunciado)
- **Descripción**: Gramática ambigua con recursión izquierda directa.
- **Propiedad formal**: **Ni LL(1) ni SLR(1)**.
- **Contenido**:
  ```text
  1
  S -> SS a
  ```
- **Comportamiento esperado**:
  El analizador reporta inmediatamente: `Grammar is neither LL(1) nor SLR(1).` y finaliza.

---

## 4. `grammar_sdd.txt` (Gramática Oficial del Item 3)
- **Descripción**: Gramática seleccionada para la Definición Dirigida por la Sintaxis (SDD). Cumple las condiciones G1, G2 y G3 de la Sección 3 del proyecto.
- **Propiedad formal**: Es **tanto LL(1) como SLR(1)**, posee 4 no terminales y 7 producciones con recursión.
- **Contenido**:
  ```text
  4
  S -> L
  L -> BR
  R -> +L e
  B -> (L) 0 1
  ```

---

## 5. `test_strings_sdd.txt` (Cadenas de Prueba para Item 3)
- **Descripción**: Batería de cadenas de prueba para el evaluador de SDD.
- **Contenido y Salidas Esperadas**:
  1. `0` $\rightarrow$ `val = 0`, `max_d = 0` (Cadena más corta)
  2. `1` $\rightarrow$ `val = 1`, `max_d = 0`
  3. `1+0` $\rightarrow$ `val = 1`, `max_d = 0` (Suma simple)
  4. `(1)` $\rightarrow$ `val = 2`, `max_d = 1` (Profundidad 1, ponderación $2^1$)
  5. `((1+0)+(1))` $\rightarrow$ `val = 8`, `max_d = 2` (Recursión y anidamiento múltiple)
  6. `1++0` $\rightarrow$ `no` (Cadena sintácticamente inválida)

---

## .6 `grammar_informe.txt` (Gramática propia de los Items 1 y 2)
- **Descripción**: Gramática propia (no aparece en el enunciado) de listas de elementos `b` separados por comas, por ejemplo `b`, `b,b` o `b,b,b`.
- **Propiedad formal**: Es **tanto LL(1) como SLR(1)**. Tiene 3 no terminales, 5 producciones y un no terminal anulable (`R`) que además es recursivo.
- **Contenido** (atención: `,L e` lleva un espacio, y son **dos alternativas**, `,L` y la vacía):
  ```text
  3
  S -> L
  L -> bR
  R -> ,L e
  ```