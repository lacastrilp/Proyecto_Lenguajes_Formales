#!/usr/bin/env python3
"""
Punto de Entrada Principal para los Items 1 y 2 del Proyecto.
Lenguajes Formales / Compiladores.

Uso:
  python3 main.py [--sets] [archivo_gramatica]

Comportamiento:
  1. Lee la gramática de acuerdo con las especificaciones de la Sección 2.2.1.
  2. Si se suministra el argumento '--sets', imprime los conjuntos FIRST y FOLLOW (Sección 2.1).
  3. Clasifica la gramática según los Casos 1, 2, 3 o 4 (Sección 2.2.2).
  4. Ejecuta el ciclo de lectura y análisis sintáctico imprimiendo 'yes' o 'no'.
"""

import os
import sys
import argparse
from typing import List
from src.grammar import Grammar
from src.first_follow import compute_first, compute_follow, format_sets_output
from src.ll1_parser import LL1Parser
from src.slr1_parser import SLR1Parser


def read_grammar_from_stream(stream) -> Grammar:
    """Lee n y las n producciones desde un stream de entrada."""
    lines: List[str] = []
    # Leer primera línea con n
    while True:
        line = stream.readline()
        if not line:
            break
        stripped = line.strip()
        if stripped:
            lines.append(stripped)
            break

    if not lines:
        sys.exit(0)

    try:
        n = int(lines[0])
    except ValueError:
        sys.stderr.write(f"Error: Se esperaba un número entero n > 0 en la primera línea, se obtuvo: {lines[0]}\n")
        sys.exit(1)

    read_count = 0
    while read_count < n:
        line = stream.readline()
        if not line:
            break
        stripped = line.strip()
        if stripped:
            lines.append(stripped)
            read_count += 1

    grammar_text = "\n".join(lines)
    return Grammar.from_text(grammar_text)


def run_parsing_loop(parser, stream):
    """
    Lee cadenas línea por línea hasta recibir una línea vacía.
    Imprime 'yes' si la cadena pertenece al lenguaje o 'no' si no.
    La cadena vacía se representa como una línea con solo 'e'.
    """
    while True:
        line = stream.readline()
        if line == "":  # EOF
            break
        # Quitar solo el salto de línea al final, preservando espacios si existieran (aunque la convención los prohíbe)
        line = line.rstrip("\r\n")
        if line == "":  # Línea vacía indica fin de cadenas
            break
        
        success, _ = parser.parse(line)
        print("yes" if success else "no")


def main():
    parser_arg = argparse.ArgumentParser(description="Analizador de Gramáticas LL(1) y SLR(1)")
    parser_arg.add_argument("--sets", action="store_true", help="Imprime los conjuntos First y Follow")
    parser_arg.add_argument("--html", action="store_true", help="Genera el visualizador web interactivo (index.html)")
    parser_arg.add_argument("grammar_file", nargs="?", default=None, help="Archivo opcional con la gramática")

    args = parser_arg.parse_args()

    if args.html:
        from src.html_formatter import generate_html_visualizer
        out = generate_html_visualizer("index.html")
        print(f"Visualizador HTML interactivo generado en: {out}")
        if not args.grammar_file and not args.sets:
            return

    # Abrir stream de archivo si se pasó como argumento, o usar sys.stdin
    if args.grammar_file:
        grammar_path = args.grammar_file
        if not os.path.exists(grammar_path):
            alt_path = os.path.join("examples", grammar_path)
            if os.path.exists(alt_path):
                grammar_path = alt_path
        with open(grammar_path, "r", encoding="utf-8") as f:
            grammar = read_grammar_from_stream(f)
        stream = sys.stdin
    else:
        stream = sys.stdin
        grammar = read_grammar_from_stream(stream)

    # 1. Cálculo de First y Follow
    first_sets = compute_first(grammar)
    follow_sets = compute_follow(grammar, first_sets)

    # Si se pasó el flag --sets, imprimir los conjuntos en el formato estricto
    if args.sets:
        sets_output = format_sets_output(grammar, first_sets, follow_sets)
        print(sets_output)

    # 2. Construcción de Parsers y Detección de Casos
    ll1 = LL1Parser(grammar, first_sets, follow_sets)
    slr1 = SLR1Parser(grammar, follow_sets)

    is_ll1 = ll1.is_ll1
    is_slr1 = slr1.is_slr1

    # Caso 1: La gramática es tanto SLR(1) como LL(1)
    if is_ll1 and is_slr1:
        while True:
            try:
                # El prompt debe ser exactamente el especificado en el PDF
                print("Select a parser (T: for LL(1), B: for SLR(1), Q: quit):")
                choice_line = stream.readline()
                if not choice_line:
                    break
                choice = choice_line.strip().upper()
                if choice == "Q":
                    break
                elif choice == "T":
                    run_parsing_loop(ll1, stream)
                elif choice == "B":
                    run_parsing_loop(slr1, stream)
            except (EOFError, KeyboardInterrupt):
                break

    # Caso 2: La gramática es LL(1), no SLR(1)
    elif is_ll1 and not is_slr1:
        print("Grammar is LL(1).")
        run_parsing_loop(ll1, stream)

    # Caso 3: La gramática es SLR(1), no LL(1)
    elif is_slr1 and not is_ll1:
        print("Grammar is SLR(1).")
        run_parsing_loop(slr1, stream)

    # Caso 4: La gramática no es ni LL(1) ni SLR(1)
    else:
        print("Grammar is neither LL(1) nor SLR(1).")
        sys.exit(0)


if __name__ == "__main__":
    main()
