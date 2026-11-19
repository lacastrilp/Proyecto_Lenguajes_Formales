import os
import sys
import argparse
from typing import List

from src.common.grammar import Grammar
from src.item1_first_follow.first_follow import (
    compute_first,
    compute_follow,
    format_sets_output
)
from src.item2_parsers.ll1_parser import LL1Parser
from src.item2_parsers.slr1_parser import SLR1Parser
from src.item2_parsers.report_output import (
    format_ll1_table,
    format_lr0_automaton,
    format_slr_tables,
    format_trace_ll1,
    format_trace_slr
)


def read_grammar_from_stream(stream) -> Grammar:
    lines: List[str] = []

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
        sys.stderr.write(
            f"Error: Se esperaba un número entero n > 0 "
            f"en la primera línea, se obtuvo: {lines[0]}\n"
        )
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

    if read_count < n:
        sys.stderr.write(
            "Error: No se recibieron todas las producciones de la gramática.\n"
        )
        sys.exit(1)

    grammar_text = "\n".join(lines)

    return Grammar.from_text(grammar_text)


def run_parsing_loop(parser, stream):

    while True:
        line = stream.readline()

        if line == "":
            break

        line = line.rstrip("\r\n")

        if line == "":
            break

        success, _ = parser.parse(line)

        print("yes" if success else "no")


def main():

    parser_arg = argparse.ArgumentParser(
        description="Analizador de Gramáticas LL(1) y SLR(1)"
    )

    parser_arg.add_argument(
        "--sets",
        action="store_true",
        help="Imprime los conjuntos First y Follow"
    )

    parser_arg.add_argument(
        "--tables",
        action="store_true",
        help="Imprime la tabla LL(1), el autómata LR(0) y las tablas SLR(1)"
    )

    parser_arg.add_argument(
        "--trace",
        default=None,
        help="Imprime la traza paso a paso de una cadena (usa e para la cadena vacía)"
    )

    parser_arg.add_argument(
        "--html",
        action="store_true",
        help="Genera el visualizador web interactivo (index.html)"
    )

    parser_arg.add_argument(
        "grammar_file",
        nargs="?",
        default=None,
        help="Archivo opcional con la gramática"
    )

    args = parser_arg.parse_args()

    # Generación del visualizador HTML
    if args.html:
        from src.common.html_formatter import generate_html_visualizer

        out = generate_html_visualizer("index.html")

        print(f"Visualizador HTML interactivo generado en: {out}")

        if not args.grammar_file and not args.sets and not args.tables and args.trace is None:
            return

    # Lectura de la gramática
    if args.grammar_file:

        grammar_path = args.grammar_file

        if not os.path.exists(grammar_path):
            alt_path = os.path.join("examples", grammar_path)

            if os.path.exists(alt_path):
                grammar_path = alt_path

        if not os.path.exists(grammar_path):
            sys.stderr.write(
                f"Error: No se encontró el archivo de gramática: {args.grammar_file}\n"
            )
            sys.exit(1)

        with open(grammar_path, "r", encoding="utf-8") as f:
            grammar = read_grammar_from_stream(f)

        stream = sys.stdin

    else:
        stream = sys.stdin
        grammar = read_grammar_from_stream(stream)

    # 1. Cálculo de First y Follow
    first_sets = compute_first(grammar)
    follow_sets = compute_follow(grammar, first_sets)

    # 2. Impresión de conjuntos First y Follow
    if args.sets:
        sets_output = format_sets_output(
            grammar,
            first_sets,
            follow_sets
        )

        print(sets_output)

    # 3. Construcción de los parsers
    ll1 = LL1Parser(grammar, first_sets, follow_sets)
    slr1 = SLR1Parser(grammar, follow_sets)

    # 4. Impresión de tablas y autómata
    if args.tables:
        print(format_ll1_table(ll1))
        print(format_lr0_automaton(slr1))
        print(format_slr_tables(slr1))

    # 5. Impresión de trazas
    if args.trace is not None:

        if ll1.is_ll1:
            rows = []

            ll1.parse(args.trace, rows)

            print("Traza LL(1) para la cadena:", args.trace)
            print(format_trace_ll1(rows))

        if slr1.is_slr1:
            rows = []

            slr1.parse(args.trace, rows)

            print("Traza SLR(1) para la cadena:", args.trace)
            print(format_trace_slr(rows))

        if not ll1.is_ll1 and not slr1.is_slr1:
            print("Grammar is neither LL(1) nor SLR(1).")

        return

    # 6. Detección del tipo de gramática
    is_ll1 = ll1.is_ll1
    is_slr1 = slr1.is_slr1

    # Caso 1: La gramática es tanto SLR(1) como LL(1)
    if is_ll1 and is_slr1:

        while True:
            try:
                print(
                    "Select a parser (T: for LL(1), B: for SLR(1), Q: quit):"
                )

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
