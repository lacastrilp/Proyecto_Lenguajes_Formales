# INFORME TÉCNICO OFICIAL Y AUDITORÍA DEL PROYECTO
## ST0270 / SI2002 Lenguajes Formales y Compiladores (2026-2)
### Analizadores Sintácticos LL(1), SLR(1) y Evaluador de Definiciones Dirigidas por la Sintaxis (SDD)

---

### Integrantes del Grupo:
- **Luis Alejandro Castrillón Piedrahita** (`lacastrilp@eafit.edu.co`)
- **Manuela Buriticá Guzmán** (`mburiticg1@eafit.edu.co`)
- **Maria Juliana Henao Rua** (`mjhenaor@eafit.edu.co`)

**Institución:** Universidad EAFIT — Escuela de Ciencias Aplicadas e Ingeniería  
**Documento Base de Requisitos:** `docs/LF_project_2026_2.pdf`  
**Informe Compilado Oficial:** [`report.pdf`](file:///home/lacastrilp/Documentos/Semestre_2026_2/Lenguajes_Formales/ProyectoFinal/report.pdf) (en la raíz del repositorio)  
**Código Fuente LaTeX:** [`docs/report.tex`](file:///home/lacastrilp/Documentos/Semestre_2026_2/Lenguajes_Formales/ProyectoFinal/docs/report.tex)  

---

## 1. Auditoría del Proyecto y Diagnóstico de "Demasiados Informes"

### 1.1 Diagnóstico de la Dispersión y Redundancia Documental Previa
Durante la inspección del repositorio se constató la presencia de múltiples documentos con funciones solapadas o nombres inconsistentes:
1. **`report.pdf` (anterior) e `INFORME_ITEM4.pdf`:** Eran copias binarias exactamente idénticas (mismo hash SHA-256). Correspondían a una versión preliminar generada con artefactos tipográficos en fórmulas matemáticas (como `$FIRST(\alpha)\text{FIRST}(\alpha)$`) y marcadores de posición sin reemplazar (`[Nombre Completo del Estudiante 2]`, `[Nombre Completo del Estudiante 3]`).
2. **`docs/INFORME_ITEM4.md`:** Borrador intermedio en Markdown que contenía los nombres actualizados de los estudiantes, pero su alcance estaba restringido conceptualmente al "Item 4", en lugar de actuar como el informe consolidado del proyecto.
3. **`docs/TEORIA_COMPILADORES.md`:** Documento de 404 líneas que resume la teoría formal de los capítulos 4 y 5 del *Dragon Book*. Es un recurso didáctico de estudio excelente para la sustentación oral (Item 5), pero no debe confundirse con el informe entregable formal.
4. **`docs/LecturesLeng.pdf`:** Documento de 101 páginas correspondiente a las lecturas teóricas asignadas de Aho et al. (material bibliográfico del curso, no un informe).
5. **`README.md` (inglés) y `README_ES.md` (español):** Coexistían dos versiones del manual de usuario. La Sección 4.2 del enunciado exige obligatoriamente un archivo `README.md` en inglés con formato Markdown.

### 1.2 Medidas Correctivas Aplicadas
- **Eliminación de duplicados innecesarios:** Se eliminó `INFORME_ITEM4.pdf` para cumplir estrictamente con la regla de entrega 4.2.4 (*"Do not include unnecessary files or directories in your submission"*).
- **Generación del informe único oficial:** Se escribió [`docs/report.tex`](file:///home/lacastrilp/Documentos/Semestre_2026_2/Lenguajes_Formales/ProyectoFinal/docs/report.tex) y se compiló mediante `pdflatex` produciendo el documento canónico [`report.pdf`](file:///home/lacastrilp/Documentos/Semestre_2026_2/Lenguajes_Formales/ProyectoFinal/report.pdf) (13 páginas) en la raíz, con los nombres reales de los integrantes, tipografía matemática formal y tablas sin errores.
- **Corrección en `examples/grammar_informe.txt`:** Se unificaron las alternativas de $R$ en una sola línea (`R -> ,L e`), solucionando el formato estipulado en la Sección 2.2.1.
- **Unificación documental:** Este documento (`docs/INFORME_OFICIAL_PROYECTO.md`) se establece como la fuente de verdad y auditoría técnica integral en Markdown.

---

## 2. Inventario y Análisis Archivo por Archivo

A continuación se detalla el rol, tecnología y estado de cada archivo del proyecto:

| Ruta del Archivo | Propósito / Responsabilidad Técnica | Estado de Cumplimiento |
|---|---|---|
| [`main.py`](file:///home/lacastrilp/Documentos/Semestre_2026_2/Lenguajes_Formales/ProyectoFinal/main.py) | Punto de entrada CLI para los Items 1 y 2. Procesa argumentos (`--sets`, `--tables`, `--trace`, `--html`), clasifica la gramática y gestiona el bucle interactivo de selección de parser según la Sección 2.2.2. | **100% Conforme** con Sección 2.2 |
| [`sdd_main.py`](file:///home/lacastrilp/Documentos/Semestre_2026_2/Lenguajes_Formales/ProyectoFinal/sdd_main.py) | Punto de entrada CLI para el Item 3. Procesa secuencias de cadenas, construye árboles con los parsers de Item 2, calcula orden topológico de dependencias, evalúa atributos e identifica circularidad (`--circular`). | **100% Conforme** con Sección 3 |
| [`run_tests.sh`](file:///home/lacastrilp/Documentos/Semestre_2026_2/Lenguajes_Formales/ProyectoFinal/run_tests.sh) | Script ejecutable de automatización que corre 31 pruebas unitarias, los 3 ejemplos del enunciado, el evaluador SDD y la generación HTML. | **100% Funcional** (cero errores) |
| [`report.pdf`](file:///home/lacastrilp/Documentos/Semestre_2026_2/Lenguajes_Formales/ProyectoFinal/report.pdf) | Informe técnico oficial compilado en PDF ubicado en la raíz del proyecto, según exige la Sección 4.1 y 4.2.3. | **100% Conforme** (13 páginas, LaTeX) |
| [`docs/report.tex`](file:///home/lacastrilp/Documentos/Semestre_2026_2/Lenguajes_Formales/ProyectoFinal/docs/report.tex) | Código fuente en LaTeX para la compilación reproducible del informe PDF. | **100% Reproducible** con `pdflatex` |
| [`README.md`](file:///home/lacastrilp/Documentos/Semestre_2026_2/Lenguajes_Formales/ProyectoFinal/README.md) | Guía obligatoria en inglés con autores, versiones de entorno, comandos de compilación/ejecución y declaración de IA generativa. | **100% Conforme** con Sección 4.2.2 |
| [`README_ES.md`](file:///home/lacastrilp/Documentos/Semestre_2026_2/Lenguajes_Formales/ProyectoFinal/README_ES.md) | Versión complementaria en español del README para referencia interna del equipo. | **Actualizado** |
| [`index.html`](file:///home/lacastrilp/Documentos/Semestre_2026_2/Lenguajes_Formales/ProyectoFinal/index.html) | Visualizador web interactivo autónomo con diagramas SVG del autómata LR(0), grafo de dependencias y laboratorio SDD paso a paso. | **Conforme** (Requisito opcional) |
| [`src/common/grammar.py`](file:///home/lacastrilp/Documentos/Semestre_2026_2/Lenguajes_Formales/ProyectoFinal/src/common/grammar.py) | Modelo de Gramática Libre de Contexto (CFG). Parsea el formato de entrada $n$ + producciones, extrae terminales, no terminales e inicial $S$. | **100% Conforme** con Sección 2.2.1 |
| [`src/common/parse_tree.py`](file:///home/lacastrilp/Documentos/Semestre_2026_2/Lenguajes_Formales/ProyectoFinal/src/common/parse_tree.py) | Estructura `ParseTreeNode` con ID único, símbolo, hijos y almacenamiento de atributos semánticos. Genera árbol indentado por profundidad. | **100% Conforme** con Paso 5.2 y 5.5 |
| [`src/common/html_formatter.py`](file:///home/lacastrilp/Documentos/Semestre_2026_2/Lenguajes_Formales/ProyectoFinal/src/common/html_formatter.py) | Generador del visualizador HTML interactivo, exportando estados, tablas y grafos vectoriales SVG. | **Conforme** |
| [`src/item1_first_follow/first_follow.py`](file:///home/lacastrilp/Documentos/Semestre_2026_2/Lenguajes_Formales/ProyectoFinal/src/item1_first_follow/first_follow.py) | Algoritmos de punto fijo para FIRST(X), FIRST de cadenas y FOLLOW(A) con soporte de $\epsilon$. Formateo con `--sets`. | **100% Conforme** con Sección 4.4.2 |
| [`src/item2_parsers/ll1_parser.py`](file:///home/lacastrilp/Documentos/Semestre_2026_2/Lenguajes_Formales/ProyectoFinal/src/item2_parsers/ll1_parser.py) | Construcción de tabla predictiva $M[A, a]$ (Algoritmo 4.31), verificación de 3 condiciones LL(1) y parser de pila (Algoritmo 4.34). | **100% Conforme** con Sección 4.4.3 y 4.4.4 |
| [`src/item2_parsers/slr1_parser.py`](file:///home/lacastrilp/Documentos/Semestre_2026_2/Lenguajes_Formales/ProyectoFinal/src/item2_parsers/slr1_parser.py) | Gramática aumentada, clausura LR(0), GOTO, tablas ACTION y GOTO (Algoritmo 4.46) y parser shift-reduce LR (Algoritmo 4.44). | **100% Conforme** con Sección 4.6.2 a 4.6.4 |
| [`src/item2_parsers/report_output.py`](file:///home/lacastrilp/Documentos/Semestre_2026_2/Lenguajes_Formales/ProyectoFinal/src/item2_parsers/report_output.py) | Funciones de formateo textual en tablas ASCII para autómata LR(0), tablas LL(1)/SLR(1) y trazas de ejecución. | **Conforme** |
| [`src/item3_sdd/sdd.py`](file:///home/lacastrilp/Documentos/Semestre_2026_2/Lenguajes_Formales/ProyectoFinal/src/item3_sdd/sdd.py) | Representación pura de la SDD como datos (`SemanticRule`, `SDDDefinition`). Implementa la SDD oficial del proyecto y versión circular. | **100% Conforme** con Paso 5.1 |
| [`src/item3_sdd/sdd_evaluator.py`](file:///home/lacastrilp/Documentos/Semestre_2026_2/Lenguajes_Formales/ProyectoFinal/src/item3_sdd/sdd_evaluator.py) | Motor evaluador agnóstico a la SDD. Grafo de dependencias, orden topológico de Kahn, detección de ciclos con DFS y evaluación de atributos. | **100% Conforme** con Paso 5.3, 5.4, 5.5 |
| [`src/item3_sdd/visualizer.py`](file:///home/lacastrilp/Documentos/Semestre_2026_2/Lenguajes_Formales/ProyectoFinal/src/item3_sdd/visualizer.py) | Visualizador interactivo de terminal paso a paso (`--interactive`) con dibujo de cajas Unicode del árbol sintáctico. | **Conforme** (Requisito opcional) |
| [`tests/test_examples.py`](file:///home/lacastrilp/Documentos/Semestre_2026_2/Lenguajes_Formales/ProyectoFinal/tests/test_examples.py) | Pruebas de los Ejemplos 1, 2 y 3 del enunciado, evaluación de las 5+ cadenas de SDD y detección de circularidad. | **100% Superado** (6 pruebas) |
| [`tests/test_first_follow.py`](file:///home/lacastrilp/Documentos/Semestre_2026_2/Lenguajes_Formales/ProyectoFinal/tests/test_first_follow.py) | Pruebas de conjuntos FIRST/FOLLOW con múltiples símbolos anulables y ordenamiento ASCII + `e` + `$`. | **100% Superado** (6 pruebas) |
| [`tests/test_item2_libro.py`](file:///home/lacastrilp/Documentos/Semestre_2026_2/Lenguajes_Formales/ProyectoFinal/tests/test_item2_libro.py) | Pruebas con gramáticas clásicas del libro (Ej. 4.30, 4.48, Ejercicio 4.6.5 LL(1) no SLR(1), Ejercicio 4.6.6 SLR(1) no LL(1)). | **100% Superado** (10 pruebas) |
| [`tests/test_ll1_conditions.py`](file:///home/lacastrilp/Documentos/Semestre_2026_2/Lenguajes_Formales/ProyectoFinal/tests/test_ll1_conditions.py) | Pruebas exhaustivas de las 3 condiciones formales de equivalencia LL(1) de la Sección 4.4.3. | **100% Superado** (9 pruebas) |
| [`examples/grammar_ex1.txt`](file:///home/lacastrilp/Documentos/Semestre_2026_2/Lenguajes_Formales/ProyectoFinal/examples/grammar_ex1.txt) | Ejemplo 1 del enunciado: Expresiones aritméticas con precedencia (SLR(1), no LL(1)). | **Conforme** |
| [`examples/grammar_ex2.txt`](file:///home/lacastrilp/Documentos/Semestre_2026_2/Lenguajes_Formales/ProyectoFinal/examples/grammar_ex2.txt) | Ejemplo 2 del enunciado: Gramática tanto LL(1) como SLR(1). | **Conforme** |
| [`examples/grammar_ex3.txt`](file:///home/lacastrilp/Documentos/Semestre_2026_2/Lenguajes_Formales/ProyectoFinal/examples/grammar_ex3.txt) | Ejemplo 3 del enunciado: Gramática ambigua con recursión izquierda directa (ni LL(1) ni SLR(1)). | **Conforme** |
| [`examples/grammar_informe.txt`](file:///home/lacastrilp/Documentos/Semestre_2026_2/Lenguajes_Formales/ProyectoFinal/examples/grammar_informe.txt) | Gramática propia para los Items 1 y 2 ($S \rightarrow L$, $L \rightarrow bR$, $R \rightarrow ,L \mid e$). | **Conforme** |
| [`examples/grammar_sdd.txt`](file:///home/lacastrilp/Documentos/Semestre_2026_2/Lenguajes_Formales/ProyectoFinal/examples/grammar_sdd.txt) | Gramática propia seleccionada para el Item 3 (expresiones binarias con ponderación de profundidad). | **Conforme** |
| [`examples/test_strings_sdd.txt`](file:///home/lacastrilp/Documentos/Semestre_2026_2/Lenguajes_Formales/ProyectoFinal/examples/test_strings_sdd.txt) | Cadenas de prueba para el Item 3: más corta (`0`), válida (`1+0`), anidada (`(1)`), profunda (`((1+0)+(1))`) e inválida (`1++0`). | **Conforme** con Paso 6 |

---

## 3. Matriz de Requisitos: Lo que se Pide vs Lo que Realmente Hay

| Requisito en `LF_project_2026_2.pdf` | Especificación Exacta | Implementación en el Proyecto | Estado |
|---|---|---|:---:|
| **Logística (Sec. 1)** | Grupos de 2 o 3 estudiantes. Sustentación oral obligatoria donde todos deben poder explicar el código y trazar a mano. | Grupo de 3 integrantes identificados formalmente con correos institucionales EAFIT. | **Cumplido** |
| **Integridad y Uso de IA (Sec. 1, 4.2)** | Citar secciones/algoritmos del libro. Declarar herramientas de IA usadas y propósito en `README.md`. | Secciones y algoritmos citados explícitamente en el código y en el informe. Declaración formal en `README.md` y `report.pdf`. | **Cumplido** |
| **Convenciones de Gramática (Sec. 2.2)** | $S$ inicial; no terminales en mayúsculas; terminales caracteres simples no mayúsculas; $\epsilon=e$; fin de cadena $\$$; cada no terminal en exactamente una línea izquierda. | Validado en `Grammar.from_text` y aplicado rigurosamente en todos los archivos de gramática. | **Cumplido** |
| **Entrada / Salida (Sec. 2.2.1, 2.2.2)** | Leer $n$ + producciones. Evaluar si es LL(1) y SLR(1). Si ambos: consultar parser (T, B, Q). Imprimir `yes`/`no` por cadena. | Implementado exactamente en `main.py` (`run_parsing_loop`, selección T/B/Q y terminación con línea vacía). | **Cumplido** |
| **Item 1: FIRST y FOLLOW (Sec. 2.1, 4.4.2)** | Algoritmos de la Sección 4.4.2. Soportar $\epsilon$. Argumento `--sets` imprime en orden alfabético: `First(A) = {...}` y `Follow(A) = {...}` con terminales en orden ASCII, luego `e`, luego `$`. | Implementado en `src/item1_first_follow/first_follow.py`. Salida idéntica al requerimiento. | **Cumplido** |
| **Item 2: Parser LL(1) (Sec. 2.1, 4.4.3, 4.4.4)** | Tabla predictiva de Algoritmo 4.31. Probar condición formal de LL(1). Parser no recursivo con pila (Algoritmo 4.34). No transformar la gramática. | Implementado en `LL1Parser`. Incluye método `check_ll1_conditions()` que verifica las 3 condiciones analíticas del libro. | **Cumplido** |
| **Item 2: Parser SLR(1) (Sec. 2.1, 4.5, 4.6)** | Colección canónica LR(0) con CLOSURE y GOTO (4.6.2). Tablas ACTION y GOTO con FOLLOW (4.6.4). Parser ascendente LR (4.6.3). Manejo de $\epsilon$. | Implementado en `SLR1Parser`. Reducciones vacías no desapilan estados; detecta conflictos shift/reduce y reduce/reduce. | **Cumplido** |
| **Item 3: Paso 1 Gramática (Sec. 3)** | G1: Cumple convención 2.2 y es LL(1) o SLR(1). G2: $\ge 3$ no terminales, $\ge 6$ producciones, $\ge 1$ recursivo. G3: No estar en el libro ni guía. | Gramática con 4 no terminales, 7 producciones, 3 recursivos. Es tanto LL(1) como SLR(1). Original. | **Cumplido** |
| **Item 3: Paso 2 SDD en Papel (Sec. 3)** | Tabla de atributos (símbolo, nombre, clase, tipo, significado). Reglas en formato Fig. 5.1. Al menos 1 sintetizado y 1 heredado. $S$ sin heredados. | Tabla con atributos `val`, `max_d` (sintetizados), `d` (heredado), `lexval`. $S$ solo sintetizados. | **Cumplido** |
| **Item 3: Paso 3 Ejemplo a Mano (Sec. 3)** | Cadena $\ge 4$ terminales. Árbol anotado, grafo de dependencias ($u \rightarrow v$ usado a definido) y orden topológico. | Ejemplo desarrollado con cadena `(1+0)` (5 terminales). Incluido en informe y verificado por software. | **Cumplido** |
| **Item 3: Paso 4 Clasificación (Sec. 3)** | Determinar si es S-atribuida, L-atribuida, ambas o ninguna, con justificación de Sec. 5.2.3 y 5.2.4. | Clasificada formalmente como **L-atribuida** (no S-atribuida por usar atributos heredados). | **Cumplido** |
| **Item 3: Paso 5 Evaluador (Sec. 3)** | 1. SDD como datos (agnóstico). 2. Árbol sintáctico de Item 2. 3. Grafo de dependencias. 4. Orden topológico y detección de ciclos. 5. Salida: árbol anotado indentado, orden topológico y valor de $S$. | Implementado en `SDDEvaluator` y `SemanticRule`. Algoritmo de Kahn + DFS para detección de ciclos. | **Cumplido** |
| **Item 3: Paso 6 Pruebas (Sec. 3)** | Al menos 5 cadenas (más corta, inválida, profunda). Probar detección de circularidad con regla alterada. | Probadas 6 cadenas en `test_strings_sdd.txt` y validación de circularidad con flag `--circular`. | **Cumplido** |
| **Item 3: Visualizador Opcional (Sec. 3)** | Interfaz paso a paso para árbol, grafo y evaluación. | Doble visualizador: CLI interactivo con Enter (`--interactive`) y visualizador web SVG (`index.html`). | **Cumplido (Plus)** |
| **Item 4: Informe en PDF (Sec. 4.1)** | Debe contener: algoritmos y estructuras de datos; gramática propia con sets, tablas y traza; SDD completa con pasos 3, 4 y 6; problemas y soluciones. | Documentado y compilado en [`report.pdf`](file:///home/lacastrilp/Documentos/Semestre_2026_2/Lenguajes_Formales/ProyectoFinal/report.pdf) en la raíz (13 páginas). | **Cumplido** |
| **Entrega: README.md en inglés (Sec. 4.2)** | Markdown en inglés: Nombres completos, versiones de SO, Python y herramientas, instrucciones de ejecución e IA usada. | Presente en [`README.md`](file:///home/lacastrilp/Documentos/Semestre_2026_2/Lenguajes_Formales/ProyectoFinal/README.md). | **Cumplido** |
| **Entrega: Limpieza de Archivos (Sec. 4.2)** | No incluir archivos innecesarios (binarios, temporales, duplicados). | Eliminados `INFORME_ITEM4.pdf` y archivos auxiliares de compilación LaTeX (`.aux`, `.log`, `.toc`, `.out`). | **Cumplido** |

---

## 4. Demostración Matemática y Traza de los Items 1 y 2

### 4.1 Gramática Propia Analizada
```text
3
S -> L
L -> bR
R -> ,L e
```

### 4.2 Conjuntos de Simulación Formal
- **FIRST:**
  - $\text{FIRST}(L) = \{b\}$
  - $\text{FIRST}(R) = \{,, e\}$
  - $\text{FIRST}(S) = \text{FIRST}(L) = \{b\}$
- **FOLLOW:**
  - $\text{FOLLOW}(S) = \{\$\}$
  - $\text{FOLLOW}(L) = \text{FOLLOW}(S) \cup \text{FOLLOW}(R) = \{\$\}$
  - $\text{FOLLOW}(R) = \text{FOLLOW}(L) = \{\$\}$

### 4.3 Tabla Predictiva LL(1)
$$M[A, a]$$
- Fila $S$: para $b \in \text{FIRST}(L)$, asigna $S \rightarrow L$.
- Fila $L$: para $b \in \text{FIRST}(bR)$, asigna $L \rightarrow bR$.
- Fila $R$: para $, \in \text{FIRST}(,L)$, asigna $R \rightarrow ,L$. Dado que $\epsilon \in \text{FIRST}(e)$, para $\$ \in \text{FOLLOW}(R)$ asigna $R \rightarrow e$.

Sin colisiones de celdas: **Gramática es LL(1)**.

### 4.4 Autómata LR(0) y Tabla SLR(1)
- Estados: 7 ($I_0 \dots I_6$).
- Transiciones shift en terminales $b$ y $,$.
- Reducciones asignadas en $\text{FOLLOW}(\text{cabeza})$:
  - En Estado 3: $R \rightarrow \cdot$ reduce en $\text{FOLLOW}(R) = \{\$\}$.
  - En Estado 4: $L \rightarrow bR \cdot$ reduce en $\text{FOLLOW}(L) = \{\$\}$.
  - En Estado 6: $R \rightarrow ,L \cdot$ reduce en $\text{FOLLOW}(R) = \{\$\}$.
  - En Estado 2: $S \rightarrow L \cdot$ reduce en $\text{FOLLOW}(S) = \{\$\}$.

No se presentan conflictos shift/reduce ni reduce/reduce: **Gramática es SLR(1)**.

---

## 5. Guía de Ejecución Rápida

Todos los módulos operan exclusivamente con la biblioteca estándar de Python (versión 3.12+):

```bash
# 1. Ejecutar la suite completa de pruebas automatizadas:
bash run_tests.sh

# 2. Ejecutar Item 1 y 2 con conjuntos First/Follow (--sets):
python3 main.py --sets examples/grammar_ex2.txt

# 3. Ver tablas LL(1), autómata LR(0) y tabla SLR(1):
python3 main.py --tables examples/grammar_informe.txt

# 4. Generar la traza paso a paso de una cadena:
python3 main.py --trace b,b examples/grammar_informe.txt

# 5. Ejecutar el evaluador SDD (Item 3) sobre cadenas de prueba:
python3 sdd_main.py examples/test_strings_sdd.txt

# 6. Ejecutar evaluación paso a paso interactiva en consola:
python3 sdd_main.py --interactive examples/test_strings_sdd.txt

# 7. Demostrar la detección de circularidad en SDD:
printf "1\n\n" | python3 sdd_main.py --circular

# 8. Recompilar el informe oficial en PDF si se edita docs/report.tex:
pdflatex -interaction=nonstopmode -output-directory=. docs/report.tex
rm -f report.aux report.log report.out report.toc
```

---

## 6. Preparación para la Sustentación Oral (Item 5)

De acuerdo con la Sección 1 y 5 de `docs/LF_project_2026_2.pdf`, durante la sustentación oral (semanas 17–18):
1. **No se requieren diapositivas:** La defensa se basa en la explicación del código, ejecución en vivo y resolución de ejercicios a mano.
2. **Capacidad de modificación en caliente:** Cada integrante debe poder modificar funciones del código en vivo (por ejemplo, alterar una regla de cálculo de FIRST/FOLLOW o añadir un nuevo atributo en la SDD).
3. **Traza a mano:** Capacidad de trazar el autómata LR(0) o simular la pila del parser sobre una nueva gramática provista por los profesores.
4. **Material de estudio teórico:** Se recomienda revisar [`docs/TEORIA_COMPILADORES.md`](file:///home/lacastrilp/Documentos/Semestre_2026_2/Lenguajes_Formales/ProyectoFinal/docs/TEORIA_COMPILADORES.md) para un repaso exhaustivo de definiciones formales de Aho et al.
