# Formal Languages and Compilers - Final Project (2026-2)
## LL(1) and SLR(1) Syntax Analyzers and Generic SDD Evaluator

Interactive Web Visualizer: https://lacastrilp.github.io/Proyecto_Lenguajes_Formales/

This repository contains our implementation of the final project for Formal Languages and Compilers (Universidad EAFIT, semester 2026-2). We wrote the entire project in Python 3 using only the standard library.

Documentation in Spanish is available in [README_ES.md](file:///home/lacastrilp/Documentos/Semestre_2026_2/Lenguajes_Formales/ProyectoFinal/README_ES.md) and [docs/INFORME_ITEM4.md](file:///home/lacastrilp/Documentos/Semestre_2026_2/Lenguajes_Formales/ProyectoFinal/docs/INFORME_ITEM4.md). The compiled project report required in the root directory is [INFORME_ITEM4.pdf](file:///home/lacastrilp/Documentos/Semestre_2026_2/Lenguajes_Formales/ProyectoFinal/INFORME_ITEM4.pdf).

---

## 1. General Information and Submission Details

### 1.1 Team Members
- Student 1: lacastrilp (lacastrilp@eafit.edu.co)
- Student 2: [Full Name of Student 2]
- Student 3: [Full Name of Student 3 (if applicable)]

### 1.2 Execution Environment and Tools
- Operating System: Linux (tested on Ubuntu 22.04 LTS and generic POSIX x86_64 environments).
- Language: Python 3 (tested with Python 3.10, 3.11, 3.12, and 3.14).
- External Libraries: None. We used only Python standard modules: `sys`, `os`, `collections`, `typing`, `argparse`, `unittest`, and `deque`. We did not use parser generators or third-party libraries (no Yacc, Bison, ANTLR, Lark, or NLTK).
- Automation: Bash script (`run_tests.sh`) and Python `unittest`.

### 1.3 Use of Generative AI Tools
We used Gemini and ChatGPT as reference support for two specific tasks: querying syntax details for Python `argparse` and `unittest` edge cases, and cross-checking the theoretical definitions of dependency graphs in Section 5.2 of Aho et al. We did not use AI tools to generate the parsing tables, automata, topological sort, or cycle detection code. We wrote all data structures, algorithms, and tests ourselves, and we are ready to defend and trace any part of the implementation during the oral presentation.

---

## 2. Repository Structure

We divided the project into source modules, unit tests, grammar examples, and documentation:

```text
Proyecto_Lenguajes_Formales/
├── .gitignore
├── README.md                 # Project guide in English (Section 4.2)
├── README_ES.md              # Documentation and theoretical guide in Spanish
├── INFORME_ITEM4.pdf         # Compiled PDF report required in the root directory
├── main.py                   # CLI driver for Items 1 and 2 (LL(1) and SLR(1))
├── sdd_main.py               # CLI driver for Item 3 (SDD evaluator)
├── run_tests.sh              # Automated test runner script
│
├── src/                      # Source code package
│   ├── __init__.py
│   ├── grammar.py            # CFG loading and representation
│   ├── first_follow.py       # FIRST and FOLLOW computation and --sets output
│   ├── parse_tree.py         # ParseTreeNode and tree formatting
│   ├── ll1_parser.py         # Algorithm 4.31 (table) and Algorithm 4.34 (LL(1) parser)
│   ├── slr1_parser.py        # Algorithm 4.46 (LR(0)/SLR(1) tables) and Algorithm 4.44 (LR parser)
│   ├── sdd.py                # SemanticRule and SDD data definitions
│   ├── sdd_evaluator.py      # Dependency graph, Kahn topological sort, and cycle detection
│   └── visualizer.py         # Step-by-step terminal execution visualizer
│
├── tests/                    # Unit tests
│   ├── __init__.py
│   └── test_examples.py      # Tests for Examples 1, 2, 3, SDD evaluation, and circularity
│
├── examples/                 # Sample grammars and input strings
│   ├── README.md             # Summary of example grammars
│   ├── grammar_ex1.txt       # Example 1: SLR(1), not LL(1)
│   ├── grammar_ex2.txt       # Example 2: both LL(1) and SLR(1)
│   ├── grammar_ex3.txt       # Example 3: neither LL(1) nor SLR(1)
│   ├── grammar_sdd.txt       # Grammar selected for Item 3
│   └── test_strings_sdd.txt  # Input strings for Item 3
│
└── docs/                     # Specifications and reports
    ├── LF_project_2026_2.pdf # Official project requirements
    ├── LecturesLeng.pdf      # Lecture slides
    ├── INFORME_ITEM4.md      # Item 4 report in Markdown
    └── TEORIA_COMPILADORES.md# Extended theoretical documentation
```

---

## 3. Theoretical Foundations (Textbook References)

We implemented the algorithms described in Aho, Lam, Sethi, and Ullman (*Compilers: Principles, Techniques, and Tools*, 2nd edition, 2006):

1. FIRST and FOLLOW Sets (Section 4.4.2):
In `src/first_follow.py`, we compute FIRST and FOLLOW sets iteratively until reaching a fixed point. For FIRST, we process each production head and body from left to right, propagating terminal symbols and handling epsilon (`e`). For FOLLOW, we place the endmarker `$` in the start symbol set, and propagate terminals following nonterminals across all production bodies.

2. Predictive LL(1) Parsing Table (Algorithm 4.31, Section 4.4.3):
In `src/ll1_parser.py`, we construct the two-dimensional table `M[A, a]`. For every production $A \rightarrow \alpha$, we add the rule to $M[A, a]$ for each $a \in \text{FIRST}(\alpha)$. If $\alpha$ can derive $\epsilon$, we also add the rule to $M[A, b]$ for each $b \in \text{FOLLOW}(A)$. If any cell receives two or more productions, the grammar is not LL(1). We do not apply grammar transformations (such as left-recursion elimination or left-factoring) before running this check, as required by the project rules.

3. Table-Driven Predictive LL(1) Parser (Algorithm 4.34, Section 4.4.4):
The class `LL1Parser` maintains a list as an explicit stack initialized to `['$', S]`. It consumes input tokens one by one. When a nonterminal appears on top of the stack, the parser replaces it with the reversed body of the production looked up in `M`. During expansions, it links children to parents to construct the concrete parse tree.

4. LR(0) Automaton and SLR(1) Parsing Table (Algorithms 4.44 and 4.46, Sections 4.5 and 4.6):
In `src/slr1_parser.py`, we augment the grammar with $S' \rightarrow S$. We represent LR(0) items as `(head, body, dot_index)`. We compute `closure` and `goto` functions to find the canonical collection of LR(0) item sets. The `ACTION` table maps state indices and terminal symbols to shifts or reductions, while `GOTO` maps state indices and nonterminals to target states. Reductions are restricted to terminals in $\text{FOLLOW}(A)$. If any conflict occurs, the grammar is not SLR(1). The parser executes shifts and reductions on a state stack to validate the string and build the parse tree.

5. Syntax-Directed Definitions and Dependency Graphs (Sections 5.1 and 5.2):
In `src/sdd.py` and `src/sdd_evaluator.py`, we store the SDD purely as data without hardcoded attribute names. For each internal tree node, we instantiate semantic rules as vertices in a directed dependency graph. Edges point from attributes used in a calculation to the attribute being defined. We compute a topological evaluation order using Kahn algorithm. If the graph contains a directed cycle, Kahn algorithm terminates before visiting all vertices; we then run a three-color depth-first search (white, gray, black) to identify and print the exact cycle path.

---

## 4. Instructions for Building and Running

### 4.1 Running Items 1 and 2 (`main.py`)

Run the script passing optional flags and a grammar file:

```bash
python3 main.py [--sets] [grammar_file]
```

If you do not specify the path prefix, the script automatically searches inside `examples/`.

#### Example 1: SLR(1), not LL(1)
```bash
python3 main.py examples/grammar_ex1.txt
```
Output:
```text
Grammar is SLR(1).
```
Input:
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

#### Example 2: Both LL(1) and SLR(1), with `--sets`
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
Enter `T` or `B`, then provide strings:
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
Enter `Q` to quit.

#### Example 3: Neither LL(1) nor SLR(1)
```bash
python3 main.py examples/grammar_ex3.txt
```
Output:
```text
Grammar is neither LL(1) nor SLR(1).
```

---

### 4.2 Running Item 3 (`sdd_main.py`)

Run the SDD evaluator passing a file containing strings (one per line, terminated by an empty line):

```bash
python3 sdd_main.py examples/test_strings_sdd.txt
```

For each valid string, the program prints:
1. The annotated parse tree (indented by depth, with attributes).
2. The evaluation order (topological sort of the dependency graph).
3. The value of the main attribute (`val`) of the start symbol ($S$).

If a string does not belong to the language (such as `1++0`), it prints `no`.

#### Circularity Detection Demo (`--circular`):
```bash
python3 sdd_main.py --circular
```
Input `1` followed by an empty line. The evaluator catches the cycle and stops:
```text
Error: Error: La definición dirigida por la sintaxis (SDD) es CIRCULAR.
Ciclo detectado en las dependencias: L_5.val -> S_6.val -> L_5.d -> B_2.d -> B_2.val -> L_5.val
Ciclo identificado: L_5.val -> S_6.val -> L_5.d -> B_2.d -> B_2.val -> L_5.val
```

---

### 4.3 Running Automated Tests (`run_tests.sh`)

We wrote a Bash script that executes unit tests and all CLI verification cases:

```bash
chmod +x run_tests.sh
./run_tests.sh
```

---

### 4.4 Interactive HTML/SVG Web Visualizer (`index.html`)

We built an interactive web visualizer following the light editorial design system from Taller 2 (tactile cards, 2px borders, hard shadows `4px 4px 0px #0f172a`, and SVG diagrams). To generate or update it:

```bash
python3 main.py --html
# or
python3 sdd_main.py --html
```

Open `index.html` in any browser to inspect:
1. FIRST and FOLLOW sets with formal calculation justifications.
2. Interactive SVG diagram of the LR(0) Automaton (7 canonical states) and SLR(1)/LL(1) tables.
3. Step-by-step parse trace cards with two-column alignment (Stack/Input vs Formal Justification).
4. Concrete annotated parse tree and interactive SVG Dependency Graph (DAG) for the SDD.
5. Live expression tester for typing and analyzing custom strings.

---

## 5. Item 3: Grammar, Attributes, and Semantic Rules

### 5.1 Grammar
We chose a grammar that models nested binary addition expressions with parenthesis depth scaling:

```text
4
S -> L
L -> BR
R -> +L e
B -> (L) 0 1
```

- G1: It is both LL(1) and SLR(1).
- G2: It has 4 nonterminals ($S, L, B, R$), 7 productions, and nonterminals $L$ and $R$ are recursive.
- G3: It is an original grammar not taken from the book or project document.

### 5.2 Attribute Table
| Symbol | Attribute | Type | Data Type | Meaning |
| :---: | :---: | :---: | :---: | :--- |
| **S** | `val` | Synthesized | Integer | Final evaluated value of the expression |
| **S** | `max_d` | Synthesized | Integer | Maximum parenthesis nesting depth |
| **L** | `d` | Inherited | Integer | Current nesting depth passed down |
| **L** | `val` | Synthesized | Integer | Sum of values in the list |
| **L** | `max_d` | Synthesized | Integer | Maximum depth in subexpression $L$ |
| **R** | `d` | Inherited | Integer | Depth inherited by remaining terms |
| **R** | `val` | Synthesized | Integer | Value of remaining terms |
| **R** | `max_d` | Synthesized | Integer | Maximum depth in remaining terms |
| **B** | `d` | Inherited | Integer | Depth inherited by block or bit |
| **B** | `val` | Synthesized | Integer | Value of bit or parenthesized block ($2^d$ for `1`, $0$ for `0`) |
| **B** | `max_d` | Synthesized | Integer | Maximum depth in block |
| **Terminals** | `lexval` | Synthesized | Character | Lexical character |

$S$ has no inherited attributes.

### 5.3 Semantic Rules Table (Dragon Book Figure 5.1 Format)
| Production | Semantic Rules |
| :--- | :--- |
| $S \rightarrow L$ | $L.d = 0$<br>$S.val = L.val$<br>$S.max\_d = L.max\_d$ |
| $L \rightarrow B R$ | $B.d = L.d$<br>$R.d = L.d$<br>$L.val = B.val + R.val$<br>$L.max\_d = \max(B.max\_d, R.max\_d)$ |
| $R \rightarrow + L$ | $L.d = R.d$<br>$R.val = L.val$<br>$R.max\_d = L.max\_d$ |
| $R \rightarrow \epsilon$ | $R.val = 0$<br>$R.max\_d = R.d$ |
| $B \rightarrow ( L )$ | $L.d = B.d + 1$<br>$B.val = L.val$<br>$B.max\_d = L.max\_d$ |
| $B \rightarrow 0$ | $B.val = 0$<br>$B.max\_d = B.d$ |
| $B \rightarrow 1$ | $B.val = 2^{B.d}$<br>$B.max\_d = B.d$ |

### 5.4 Classification
The SDD is not S-attributed because it uses the inherited attribute $d$. It is L-attributed because all inherited attributes depend either on inherited attributes of the head or on symbols to their left.

### 5.5 Test Results
- Shortest valid string (`0`): `val = 0`, `max_d = 0`.
- Single bit (`1`): `val = 1`, `max_d = 0`.
- Addition (`1+0`): `val = 1`, `max_d = 0`.
- Nested expression (`(1)`): `val = 2`, `max_d = 1`.
- Deeply nested expression (`((1+0)+(1))`): `val = 8`, `max_d = 2`.
- Invalid string (`1++0`): output `no`.
- Unbalanced string (`(1+`): output `no`.
- Circular test (`--circular`): reports cycle `L_5.val -> S_6.val -> L_5.d -> B_2.d -> B_2.val -> L_5.val` and stops.

---

## 6. Item 4: Problems Encountered and Solutions

1. Epsilon Reductions in SLR(1):
Epsilon productions have right-hand side length 0. When reducing $A \rightarrow \epsilon$, popping items from the state stack would corrupt parser state. We fixed this by popping 0 states, consulting $\text{GOTO}$ for the current state, and appending a leaf node labelled `'e'`.

2. Decoupled SDD Data Representation:
The project requires the evaluator to know nothing about specific attributes. We created the `SemanticRule` class where dependencies and computation functions are referenced by relative child positions.

3. Whitespace in Grammar Alternatives:
The grammar format specifies that alternatives are separated by whitespace and tokens within an alternative have no spaces. Writing `L -> b R` caused the parser to see two alternatives (`b` and `R`). We adjusted our grammar definitions to `L -> bR` and `R -> ,L e`.

4. Path Resolution in CLI Scripts:
Running scripts from outside the root directory caused relative file lookups to fail. We added fallback logic checking `examples/` when a file is not in the working directory.
