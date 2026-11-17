#!/bin/bash
# Script de ejecución automatizada de pruebas y verificación integral
# Proyecto Final: Lenguajes Formales y Compiladores

set -e
cd "$(dirname "$0")"

echo "================================================================="
echo "   1. EJECUTANDO PRUEBAS UNITARIAS (PYTHON UNITTEST)"
echo "================================================================="
python3 -m unittest discover -s tests -v

echo ""
echo "================================================================="
echo "   2. VERIFICANDO EJEMPLO 1: SLR(1), no LL(1)"
echo "      Archivo: examples/grammar_ex1.txt"
echo "================================================================="
python3 main.py examples/grammar_ex1.txt << 'EOF'
i+i
(i)
(i+i)*i)

EOF

echo ""
echo "================================================================="
echo "   3. VERIFICANDO EJEMPLO 2: LL(1) y SLR(1) CON --sets"
echo "      Archivo: examples/grammar_ex2.txt"
echo "================================================================="
python3 main.py --sets examples/grammar_ex2.txt << 'EOF'
T
d
adbc
a

Q
EOF

echo ""
echo "================================================================="
echo "   4. VERIFICANDO EJEMPLO 3: neither LL(1) nor SLR(1)"
echo "      Archivo: examples/grammar_ex3.txt"
echo "================================================================="
python3 main.py examples/grammar_ex3.txt

echo ""
echo "================================================================="
echo "   5. VERIFICANDO ITEM 3: SDD EVALUATOR CON CADENAS DE PRUEBA"
echo "      Archivo: examples/test_strings_sdd.txt"
echo "================================================================="
python3 sdd_main.py examples/test_strings_sdd.txt

echo ""
echo "================================================================="
echo "   6. VERIFICANDO DETECCIÓN DE DEFINICIÓN CIRCULAR EN SDD"
echo "================================================================="
python3 sdd_main.py --circular << 'EOF'
1

EOF

echo ""
echo "================================================================="
echo "   7. VERIFICANDO RESOLUCIÓN AUTOMÁTICA DE RUTAS EN examples/"
echo "================================================================="
python3 main.py grammar_ex1.txt << 'EOF'
i+i

EOF

echo ""
echo ">>> TODAS LAS PRUEBAS Y CASOS DE PRUEBA FINALIZARON EXITOSAMENTE <<<"
