# Formal Languages and Compilers - Final Project (2026-2)
## LL(1) and SLR(1) Syntax Analyzers & Generic Syntax-Directed Definition (SDD) Evaluator

[![Python 3.10+](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.14-blue.svg)](https://www.python.org/)
[![Status](https://img.shields.io/badge/tests-passing-brightgreen.svg)]()
[![Documentation](https://img.shields.io/badge/docs-English%20%7C%20Espa%C3%B1ol-orange.svg)]()

> **Language Notice:** This master documentation is provided in **English** as explicitly required by Section 4.2 of the project specification (`LF_project_2026_2.pdf`). A full Spanish version with detailed theoretical proofs is available in [`README_ES.md`](file:///home/lacastrilp/Documentos/Semestre_2026_2/Lenguajes_Formales/ProyectoFinal/README_ES.md) and [`docs/INFORME_ITEM4.md`](file:///home/lacastrilp/Documentos/Semestre_2026_2/Lenguajes_Formales/ProyectoFinal/docs/INFORME_ITEM4.md).

---

## 1. General Information & Submission Requirements

### 1.1 Team Members
- **Student 1:** `lacastrilp` (<lacastrilp@eafit.edu.co>) - Universidad EAFIT
- *(Team member details can be customized in this section if applicable).*

### 1.2 Execution Environment, Operating System & Versions
- **Operating System:** Linux (Ubuntu 22.04 LTS / Debian / POSIX x86_64 compatible).
- **Programming Language:** Python 3 (Tested on Python 3.10, 3.11, 3.12, and 3.14).
- **External Libraries:** **None.** (Exclusively uses the Python Standard Library: `sys`, `os`, `collections`, `typing`, `argparse`, `unittest`, `deque`). Strictly complies with the zero-external-parser-library rule (no Yacc, Bison, ANTLR, Lark, or NLTK).
- **Supporting Tools:** `bash`, `unittest`.

### 1.3 Statement on Responsible Use of AI Tools
> *In compliance with academic integrity guidelines:*  
> Generative AI models were used as reference support for syntax queries, reviewing conceptual definitions from Aho et al., and structuring initial test cases. All data structures, algorithmic design (FIRST/FOLLOW sets, LR(0) automata closure/goto, parsing tables, dependency graphs, topological sorting, and cycle tracing) were developed, validated, and thoroughly analyzed by the team members, who are fully capable of defending the code, tracing grammars manually, and modifying the implementation during oral examination.

---

## 2. Project Architecture & Organization

The codebase is organized into modular packages with clean separation of concerns:

```
Proyecto_Lenguajes_Formales/
├── .gitignore              # Standard Python gitignore rules
├── README.md               # Master documentation (English, per Section 4.2)
├── README_ES.md            # Complete Spanish manual and theoretical reference
├── main.py                 # CLI driver for Items 1 and 2 (interactive parsing & classification)
├── sdd_main.py             # CLI driver for Item 3 (SDD evaluation & cycle detection)
├── run_tests.sh            # Automated verification script for all unit tests & examples
│
├── src/                    # Core modular library
│   ├── __init__.py         # Package initializer
│   ├── grammar.py          # CFG representation, input parsing, and validation
│   ├── first_follow.py     # Fixed-point FIRST, FOLLOW, and formatted output (--sets)
│   ├── parse_tree.py       # Annotated ParseTreeNode and ASCII tree renderer
│   ├── ll1_parser.py       # Algorithm 4.31 & 4.34 (LL(1) Table & Predictive Parser)
│   ├── slr1_parser.py      # Algorithm 4.44 & 4.46 (LR(0) Collection, SLR(1) Table & Parser)
│   ├── sdd.py              # Pure data representation for SDD (decoupled semantic rules)
│   ├── sdd_evaluator.py    # Generic SDD evaluator, dependency DAG, Kahn topological sort & cycle trace
│   └── visualizer.py       # Interactive step-by-step terminal visualizer
│
├── tests/                  # Unit test suite
│   ├── __init__.py
│   └── test_examples.py    # Automated test cases covering Examples 1-3, SDD, and circularity
│
├── examples/               # Sample grammars and test files
│   ├── README.md           # Description of all sample grammars and expected outputs
│   ├── grammar_ex1.txt     # Example 1: SLR(1), not LL(1) (arithmetic expressions)
│   ├── grammar_ex2.txt     # Example 2: Both LL(1) and SLR(1)
│   ├── grammar_ex3.txt     # Example 3: Neither LL(1) nor SLR(1) (ambiguous)
│   ├── grammar_sdd.txt     # Official grammar for Item 3 SDD
│   └── test_strings_sdd.txt# Test inputs for Item 3 SDD
│
└── docs/                   # Academic documentation and references
    ├── LF_project_2026_2.pdf    # Official course project specification
    ├── LecturesLeng.pdf         # Course reference lectures and notes
    ├── INFORME_ITEM4.md         # Final written report for Item 4
    └── TEORIA_COMPILADORES.md   # Exhaustive theoretical framework
```

---

## 3. Theoretical Foundations (Textbook Citations)

The implementation strictly follows:  
**Aho, Lam, Sethi, Ullman. *Compilers: Principles, Techniques, and Tools* (2nd Edition), Addison-Wesley, 2006 (The Dragon Book).**

```
                             COMPILER WORKFLOW OVERVIEW
                             
     +---------------+        +----------------------+        +--------------------+
     | Token Stream  | -----> | Syntax Analyzer      | -----> | Concrete Parse     |
     | (Input String)|        | (LL(1) / SLR(1))     |        | Tree (Annotated)   |
     +---------------+        +----------------------+        +--------------------+
                                                                         |
                                                                         v
     +---------------+        +----------------------+        +--------------------+
     | Semantic      |<------ | SDD Evaluator        |<------ | Dependency Graph   |
     | Output (val)  |        | (Topological Sort)   |        | (DAG or Cycle)     |
     +---------------+        +----------------------+        +--------------------+
```

### 3.1 Top-Down Parsing & LL(1) (Sections 4.4.1 – 4.4.4)
- **FIRST Sets (Section 4.4.2):** For any grammar symbol string $\alpha$, $\text{FIRST}(\alpha)$ is the set of terminals that begin strings derived from $\alpha$. Computed using a fixed-point iteration over productions. If $\alpha \Rightarrow^* \epsilon$, then $\epsilon \in \text{FIRST}(\alpha)$.
- **FOLLOW Sets (Section 4.4.2):** For nonterminal $A$, $\text{FOLLOW}(A)$ is the set of terminals that can appear immediately to the right of $A$ in some sentential form, including $\$$ for the start symbol $S$.
- **Predictive Parsing Table $M[A, a]$ (Algorithm 4.31):**
  - For each production $A \rightarrow \alpha$:
    - For each terminal $a \in \text{FIRST}(\alpha) \setminus \{\epsilon\}$, add $A \rightarrow \alpha$ to $M[A, a]$.
    - If $\epsilon \in \text{FIRST}(\alpha)$, add $A \rightarrow \alpha$ to $M[A, b]$ for each $b \in \text{FOLLOW}(A)$ (including $\$$).
  - A grammar is **LL(1)** if and only if no cell $M[A, a]$ contains multiple productions.
- **Table-Driven LL(1) Parser (Algorithm 4.34):**
  Maintains a stack initialized to `['$', S]` and scans input $w\$$. In each step:
  - If top $X = a = \$$, accept.
  - If top $X = a \neq \$$, pop $X$ and advance lookahead.
  - If top $X \in V_N$, lookup $M[X, a]$. If production $X \rightarrow Y_1 \dots Y_k$ exists, pop $X$ and push $Y_k \dots Y_1$. If $X \rightarrow \epsilon$, pop $X$. Otherwise, syntax error.

### 3.2 Bottom-Up Parsing & SLR(1) (Sections 4.5 – 4.6)
- **LR(0) Items & Augmented Grammar (Section 4.6.2):** An LR(0) item $[A \rightarrow \alpha \cdot \beta]$ indicates that $\alpha$ has been parsed and $\beta$ is expected. The grammar is augmented with $S' \rightarrow S$.
- **$\text{CLOSURE}(I)$ & $\text{GOTO}(I, X)$ (Section 4.6.2):**
  - $\text{CLOSURE}(I)$ recursively expands items where the dot precedes a nonterminal.
  - $\text{GOTO}(I, X) = \text{CLOSURE}(\{[A \rightarrow \alpha X \cdot \beta] \mid [A \rightarrow \alpha \cdot X \beta] \in I\})$.
- **SLR(1) Parsing Table Construction (Algorithm 4.46):**
  For state $i$ corresponding to item set $I_i$:
  1. If $[A \rightarrow \alpha \cdot a \beta] \in I_i$ ($a \in V_T$) and $\text{GOTO}(I_i, a) = I_j$, set $\text{ACTION}[i, a] = \text{shift } j$.
  2. If $[A \rightarrow \alpha \cdot] \in I_i$ ($A \neq S'$), for all $a \in \text{FOLLOW}(A)$, set $\text{ACTION}[i, a] = \text{reduce } A \rightarrow \alpha$.
  3. If $[S' \rightarrow S \cdot] \in I_i$, set $\text{ACTION}[i, \$] = \text{accept}$.
  4. For $A \in V_N$, if $\text{GOTO}(I_i, A) = I_j$, set $\text{GOTO}[i, A] = j$.
  - A grammar is **SLR(1)** if and only if no conflicting actions (shift/reduce or reduce/reduce) exist.
- **LR Parsing Algorithm (Algorithm 4.44):**
  Maintains a stack of states `[0]`. Uses $\text{ACTION}$ and $\text{GOTO}$ to shift terminal tokens and reduce handles, reconstructing the rightmost derivation in reverse.

### 3.3 Syntax-Directed Definitions (SDDs) & Evaluation Orders (Sections 5.1 – 5.2)
- **Synthesized Attributes:** Computed at a head node from its children ($A.s = f(\text{children})$).
- **Inherited Attributes:** Computed at a body node from its parent or siblings ($X_j.i = f(\text{parent}, \text{siblings})$).
- **Dependency Graph (Section 5.2.1):** Directed graph where nodes are attribute instances ($N.a$) and directed edges $U \rightarrow V$ mean $U$ must be evaluated before $V$.
- **Evaluation via Topological Sorting:** A valid evaluation order corresponds to a topological sort of the dependency graph (Kahn's algorithm).
- **Circularity Detection:** If the graph contains a directed cycle, Kahn's algorithm fails to visit all nodes. A 3-color DFS (White, Gray, Black) reconstructs the exact circular dependency path.

---

## 4. Instructions for Building & Running

### 4.1 Prerequisites
- Python 3.10 or higher.
- No third-party packages need to be installed.

### 4.2 Running Items 1 & 2: LL(1) and SLR(1) Analyzers (`main.py`)

Syntax:
```bash
python3 main.py [--sets] [grammar_file]
```
*(Note: If `grammar_file` is not found in the current working directory, the script automatically searches inside `examples/`)*.

#### Example A: Example 1 (SLR(1), not LL(1))
```bash
python3 main.py examples/grammar_ex1.txt
```
Program output:
```text
Grammar is SLR(1).
```
Input strings:
```text
i+i
(i)
(i+i)*i)

```
Output:
```text
yes
yes
no
```

#### Example B: Example 2 (Both LL(1) and SLR(1)) with `--sets`
```bash
python3 main.py --sets examples/grammar_ex2.txt
```
Output:
```text
First(A) = {a, d}
First(B) = {b, e}
First(S) = {a, d}
Follow(A) = {b, $}
Follow(B) = {c, $}
Follow(S) = {$}
Select a parser (T: for LL(1), B: for SLR(1), Q: quit):
```
Enter `T`, then input:
```text
d
adbc
a

```
Output:
```text
yes
yes
no
Select a parser (T: for LL(1), B: for SLR(1), Q: quit):
```
Enter `Q` to exit.

#### Example C: Example 3 (Neither LL(1) nor SLR(1))
```bash
python3 main.py examples/grammar_ex3.txt
```
Output:
```text
Grammar is neither LL(1) nor SLR(1).
```

---

### 4.3 Running Item 3: SDD Evaluator (`sdd_main.py`)

Syntax:
```bash
python3 sdd_main.py [--interactive] [--circular] [--parser {slr1,ll1}] [strings_file]
```

#### Normal Evaluation on Sample Test Strings:
```bash
python3 sdd_main.py examples/test_strings_sdd.txt
```
For each valid string, the program outputs:
1. The **annotated parse tree** (one node per line, indented by depth, displaying all attributes).
2. The **evaluation order** (topological sort of the dependency DAG).
3. The **main value** of the start symbol (`val` at `S`).

If a string does not belong to the grammar (e.g. `1++0`), it prints `no`.

#### Circular Dependency Demonstration (`--circular`):
```bash
python3 sdd_main.py --circular
```
Input `1` followed by an empty line. The evaluator immediately catches the circular dependency:
```text
Error: Error: La definición dirigida por la sintaxis (SDD) es CIRCULAR.
Ciclo detectado en las dependencias: L_5.val -> S_6.val -> L_5.d -> B_2.d -> B_2.val -> L_5.val
Ciclo identificado: L_5.val -> S_6.val -> L_5.d -> B_2.d -> B_2.val -> L_5.val
```

---

### 4.4 Automated Testing & Verification Suite (`run_tests.sh`)

To execute the entire unit test suite and verify all test examples in one command:
```bash
chmod +x run_tests.sh
./run_tests.sh
```

---

## 5. Item 3: Selected SDD Specification

### 5.1 Grammar (Satisfies G1, G2, G3)
The grammar models nested arithmetic binary bit-lists with depth-dependent scaling:
```text
4
S -> L
L -> BR
R -> +L e
B -> (L) 0 1
```
- **G1:** Follows Section 2.2 conventions; is **both LL(1) and SLR(1)**.
- **G2:** 4 nonterminals ($S, L, B, R \ge 3$), 7 productions ($\ge 6$), recursive ($L$ and $R$).
- **G3:** Completely original, not from the textbook or assignment handouts.

### 5.2 Attribute Table
| Symbol | Attribute | Type | Data Type | Description |
| :---: | :---: | :---: | :---: | :--- |
| **S** | `val` | Synthesized | Integer | Final evaluated numeric value of the expression. |
| **S** | `max_d` | Synthesized | Integer | Maximum parenthesis nesting depth reached. |
| **L** | `d` | **Inherited** | Integer | Inherited nesting depth level. |
| **L** | `val` | Synthesized | Integer | Sum of term values in the list. |
| **L** | `max_d` | Synthesized | Integer | Maximum depth found in subexpression $L$. |
| **R** | `d` | **Inherited** | Integer | Inherited depth for the remaining summation terms. |
| **R** | `val` | Synthesized | Integer | Value contributed by the remaining terms. |
| **R** | `max_d` | Synthesized | Integer | Maximum depth in the remaining terms. |
| **B** | `d` | **Inherited** | Integer | Inherited depth for current block or bit. |
| **B** | `val` | Synthesized | Integer | Block value (for `1`: $2^d$, for `0`: 0). |
| **B** | `max_d` | Synthesized | Integer | Maximum depth found in the block. |
| **Terminals** | `lexval` | Synthesized | Char | Lexical value provided by scanner. |

### 5.3 Semantic Rules (Dragon Book Figure 5.1 Format)
| Production | Semantic Rules |
| :--- | :--- |
| $S \rightarrow L$ | $L.d = 0$;<br>$S.val = L.val$;<br>$S.max\_d = L.max\_d$ |
| $L \rightarrow B R$ | $B.d = L.d$;<br>$R.d = L.d$;<br>$L.val = B.val + R.val$;<br>$L.max\_d = \max(B.max\_d, R.max\_d)$ |
| $R \rightarrow + L$ | $L.d = R.d$;<br>$R.val = L.val$;<br>$R.max\_d = L.max\_d$ |
| $R \rightarrow \epsilon$ | $R.val = 0$;<br>$R.max\_d = R.d$ |
| $B \rightarrow ( L )$ | $L.d = B.d + 1$;<br>$B.val = L.val$;<br>$B.max\_d = L.max\_d$ |
| $B \rightarrow 0$ | $B.val = 0$;<br>$B.max\_d = B.d$ |
| $B \rightarrow 1$ | $B.val = 2^{B.d}$;<br>$B.max\_d = B.d$ |

### 5.4 Classification
- **Not S-attributed:** Uses inherited attributes ($d$).
- **Is L-attributed:** All inherited attributes depend strictly on attributes of the head or symbols strictly to the left.

### 5.5 Test Results Summary
| Test Input String | Expected `val` | Expected `max_d` | Status | Notes |
| :--- | :---: | :---: | :---: | :--- |
| `0` | `0` | `0` | Accepted | Shortest valid string ($2^0 \times 0$) |
| `1` | `1` | `0` | Accepted | Single bit at depth 0 ($2^0 = 1$) |
| `1+0` | `1` | `0` | Accepted | Simple binary addition |
| `(1)` | `2` | `1` | Accepted | Nested bit at depth 1 ($2^1 = 2$) |
| `((1+0)+(1))` | `8` | `2` | Accepted | Multiple nesting levels ($4 + 4 = 8$) |
| `1++0` | - | - | Rejected (`no`) | Invalid syntax (adjacent operators) |
| `(1` | - | - | Rejected (`no`) | Unbalanced parenthesis |

---

## 6. Item 4: Challenges Encountered & Solutions

1. **Handling $\epsilon$ (`e`) in SLR(1) Reductions:**
   - *Problem:* An $\epsilon$-production $A \rightarrow \epsilon$ has a right-hand side of length 0. Standard reduction pops $|\beta|$ states, which for $\epsilon$ is 0 states.
   - *Solution:* Explicitly represented $\epsilon$-items as $[A \rightarrow \cdot]$ with body length 0. During reduction, 0 states are popped, the GOTO state is pushed, and an annotated leaf node `'e'` is attached to the parse tree.
2. **Decoupling SDD Definitions from Evaluator Engine:**
   - *Problem:* Step 5.1 of the project instructions strictly mandates storing the SDD as pure data without hardcoding attribute names in the evaluator.
   - *Solution:* Encapsulated semantic rules in declarative `SemanticRule` data classes where dependencies and computation functions are indexed by symbol position. The `SDDEvaluator` operates purely on abstract graphs and topological ordering.
3. **Empty String Distinction in Console I/O:**
   - *Problem:* A blank line indicates EOF/end of input strings, preventing raw empty lines from representing the empty string $\epsilon$.
   - *Solution:* Preserved the convention where `'e'` represents $\epsilon$, mapping it internally to length-0 parsing.
4. **Interactive Path Resolution:**
   - *Problem:* Running tests and commands from different working directories could cause relative path issues with grammar files.
   - *Solution:* Implemented dual-path fallback in `main.py` and `sdd_main.py`, automatically resolving files both in the root directory and inside `examples/`.

---

## 7. License & Academic Integrity
Developed as part of the Formal Languages and Compilers course (2026-2), Universidad EAFIT.
Academic use permitted under the terms of the MIT License.
