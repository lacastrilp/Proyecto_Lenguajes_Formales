# Formal Languages Project 2026-2: LL(1), SLR(1) and SDD Evaluation

## Group members
- Luis Alejandro Castrillón Piedrahita (lacastrilp@eafit.edu.co)
- Manuela Buriticá Guzmán (mburiticg1@eafit.edu.co)
- Maria Juliana Henao Rua (mjhenaor@eafit.edu.co)

## Environment
- **Operating System:** Linux x86_64 (Debian / Kali GNU/Linux)
- **Python Version:** Python 3.12+ (tested on Python 3.14.8)
- **External libraries:** None (Standard library only: `sys`, `os`, `argparse`, `typing`, `collections`, `unittest`)

## Project layout (by assignment item)
| Item | Files | Description |
|---|---|---|
| **1. FIRST and FOLLOW** | [`src/item1_first_follow/first_follow.py`](src/item1_first_follow/first_follow.py) | Iterative fixed-point FIRST/FOLLOW calculation and `--sets` formatter |
| **2. LL(1) and SLR(1) parsers** | [`src/item2_parsers/ll1_parser.py`](src/item2_parsers/ll1_parser.py)<br>[`src/item2_parsers/slr1_parser.py`](src/item2_parsers/slr1_parser.py) | Predictive LL(1) table parser and bottom-up SLR(1) LR(0) automaton parser |
| **3. SDD evaluator** | [`src/item3_sdd/sdd.py`](src/item3_sdd/sdd.py)<br>[`src/item3_sdd/sdd_evaluator.py`](src/item3_sdd/sdd_evaluator.py)<br>[`src/item3_sdd/visualizer.py`](src/item3_sdd/visualizer.py) | Pure data SDD representation, topological dependency graph evaluator, cycle detection and CLI visualizer |
| **Shared** | [`src/common/grammar.py`](src/common/grammar.py)<br>[`src/common/parse_tree.py`](src/common/parse_tree.py)<br>[`src/common/html_formatter.py`](src/common/html_formatter.py) | CFG definition, parse tree node representation, and optional interactive HTML visualizer generator |
| **Entry points** | [`main.py`](main.py)<br>[`sdd_main.py`](sdd_main.py) | CLI driver for Items 1-2 and CLI driver for Item 3 SDD evaluation |
| **Examples and tests** | [`examples/`](examples/)<br>[`tests/test_examples.py`](tests/test_examples.py)<br>[`run_tests.sh`](run_tests.sh) | Grammar/strings test suites and automated test runner script |
| **4. Report** | [`report.pdf`](report.pdf)<br>[`INFORME_ITEM4.pdf`](INFORME_ITEM4.pdf)<br>[`docs/INFORME_ITEM4.md`](docs/INFORME_ITEM4.md) | Technical comparison report between LL(1) and SLR(1) parsing algorithms |

## How to Run

No compilation or build step is needed. All scripts use standard Python 3.

### Items 1 and 2: LL(1) and SLR(1) Parsers
Grammar read from standard input, or from a file passed as an argument:
```bash
# Print FIRST and FOLLOW sets (--sets) and run grammar classification
python3 main.py --sets examples/grammar_ex2.txt

# Run directly on an input grammar file
python3 main.py examples/grammar_ex1.txt

# Or provide grammar through standard input (stdin)
python3 main.py << 'EOF'
3
S -> AB
A -> aA d
B -> bBc e
EOF
```

### Item 3: Syntax-Directed Definition (SDD) Evaluator
Evaluates annotated parse trees using topological sort on dependency graphs:
```bash
# Evaluate test strings with default SLR(1) parser
python3 sdd_main.py examples/test_strings_sdd.txt

# Evaluate using LL(1) parser
python3 sdd_main.py --parser ll1 examples/test_strings_sdd.txt

# Interactive terminal step-by-step evaluation
python3 sdd_main.py --interactive examples/test_strings_sdd.txt

# Demonstrate circular dependency detection
python3 sdd_main.py --circular << 'EOF'
1

EOF
```

## How to Run on Windows

No compilation or build step is needed. Install Python 3.12+.

### Items 1 and 2: LL(1) and SLR(1) Parsers
Grammar read from standard input, or from a file passed as an argument:
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

### Item 3: Syntax-Directed Definition (SDD) Evaluator
Evaluates annotated parse trees using topological sort on dependency graphs:
```powershell
python sdd_main.py examples\test_strings_sdd.txt

python sdd_main.py --parser ll1 examples\test_strings_sdd.txt

python sdd_main.py --interactive examples\test_strings_sdd.txt

@"
1

"@ | python sdd_main.py --circular
```

### Optional Interactive Web Visualizer
Generates an interactive, standalone HTML/SVG visualizer (`index.html`) to inspect automata, tables, and trees:
```bash
python3 main.py --html
# Open index.html in any browser:
# xdg-open index.html
```

### Run All Automated Tests
Executes unit tests and checks all assignment examples:
```bash
bash run_tests.sh
```

---

## Academic References (Dragon Book)
Algorithms strictly follow *Compilers: Principles, Techniques, and Tools* (Aho, Lam, Sethi, Ullman - 2nd Edition):
- **FIRST and FOLLOW Sets:** Section 4.4.2 (Rules for $FIRST(X)$ and $FOLLOW(A)$).
- **LL(1) Table Construction:** Algorithm 4.31, Section 4.4.3.
- **LL(1) Table-Driven Predictive Parser:** Algorithm 4.34, Section 4.4.4.
- **LR(0) Collection & Automaton (CLOSURE, GOTO):** Section 4.6.2.
- **SLR(1) Parsing Table Construction:** Algorithm 4.46, Section 4.6.4.
- **SLR(1) Shift-Reduce Parsing Algorithm:** Algorithm 4.44, Section 4.6.3.
- **Syntax-Directed Definitions & Dependency Graphs:** Sections 5.1 & 5.2 (Topological evaluation order & cycle detection).

---

## Generative AI Usage Statement
Generative AI tools (Claude 3.5 Sonnet and Google Gemini) were utilized responsibly as support tools during the project:
1. Assisting in structural code organization, test suite verification, and ensuring adherence to the submission layout guidelines specified in `LF_project_2026_2.pdf`.
2. Assisting in formatting LaTeX/Markdown documentation and drafting the comparative analysis for Item 4.
All theoretical implementations of the parsing algorithms, LR(0) automaton generation, dependency graphs, and SDD rules were implemented, verified, and audited by the authors according to the course textbook.
