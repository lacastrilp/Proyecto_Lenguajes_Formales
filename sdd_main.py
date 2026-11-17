#!/usr/bin/env python3
"""
Punto de Entrada para el Item 3: Evaluador de la Definición Dirigida por la Sintaxis (SDD).

Uso:
  python3 sdd_main.py [--interactive] [--circular] [archivo_cadenas]

Especificaciones de Entrada y Salida (Sección 3 de LF_project_2026_2.pdf):
  - Las cadenas se leen una por línea hasta recibir una línea vacía.
  - Para cada cadena:
      * Si la cadena no pertenece al lenguaje, imprime 'no'.
      * Si pertenece, imprime:
          1. El árbol sintáctico anotado (un nodo por línea, indentado por profundidad, con sus atributos).
          2. El orden de evaluación (orden topológico del grafo de dependencias).
          3. El valor del atributo principal del símbolo inicial ('val').
  - Si la SDD es circular, reporta que la definición es circular y se detiene.
"""

import os
import sys
import argparse
from src.grammar import Grammar
from src.first_follow import compute_first, compute_follow
from src.ll1_parser import LL1Parser
from src.slr1_parser import SLR1Parser
from src.sdd import create_project_sdd, create_circular_sdd
from src.sdd_evaluator import SDDEvaluator, SDDCircularDefinitionError
from src.visualizer import SDDVisualizer, render_tree_ascii


def main():
    parser_arg = argparse.ArgumentParser(description="Evaluador de SDD con Grafo de Dependencias (Item 3)")
    parser_arg.add_argument("--interactive", action="store_true", help="Activa el visualizador interactivo paso a paso")
    parser_arg.add_argument("--circular", action="store_true", help="Usa una regla circular para demostrar detección de ciclos")
    parser_arg.add_argument("--parser", choices=["ll1", "slr1"], default="slr1", help="Parser a utilizar para construir el árbol (por defecto: slr1)")
    parser_arg.add_argument("input_file", nargs="?", default=None, help="Archivo opcional con cadenas a evaluar")

    args = parser_arg.parse_args()

    # 1. Cargar la SDD (normal o circular según el flag)
    sdd = create_circular_sdd() if args.circular else create_project_sdd()
    evaluator = SDDEvaluator(sdd)
    visualizer = SDDVisualizer(sdd)

    # 2. Inicializar la gramática y el parser correspondiente
    grammar = Grammar.from_text(sdd.grammar_text)
    first_sets = compute_first(grammar)
    follow_sets = compute_follow(grammar, first_sets)

    if args.parser == "ll1":
        parser = LL1Parser(grammar, first_sets, follow_sets)
    else:
        parser = SLR1Parser(grammar, follow_sets)

    # 3. Leer cadenas desde archivo o stdin
    if args.input_file:
        input_path = args.input_file
        if not os.path.exists(input_path):
            alt_path = os.path.join("examples", input_path)
            if os.path.exists(alt_path):
                input_path = alt_path
        stream = open(input_path, "r", encoding="utf-8")
    else:
        stream = sys.stdin

    try:
        while True:
            line = stream.readline()
            if line == "":  # Fin de archivo (EOF)
                break
            stripped = line.rstrip("\r\n")
            if stripped == "":  # Línea vacía termina la secuencia
                break

            # Parsear la cadena con el parser propio de Item 2
            success, parse_tree = parser.parse(stripped)

            if not success or parse_tree is None:
                print("no")
                continue

            # Evaluar la SDD sobre el árbol sintáctico
            try:
                if args.interactive:
                    visualizer.display_dependency_graph(parse_tree)
                    visualizer.run_interactive(parse_tree)
                else:
                    order_labels, main_val = evaluator.evaluate(parse_tree)

                    # Salida requerida en el Paso 5.5:
                    # 1. Árbol sintáctico anotado (un nodo por línea, indentado por profundidad)
                    for tree_line in parse_tree.format_tree():
                        print(tree_line)

                    # 2. Orden de evaluación
                    print("Orden de evaluacion:", ", ".join(order_labels))

                    # 3. Valor del atributo principal del símbolo inicial
                    print(f"Valor de {sdd.main_attribute} en {grammar.start_symbol}: {main_val}")

            except SDDCircularDefinitionError as circ_err:
                # Paso 5.4: Si el grafo tiene un ciclo, reportar que es circular y detenerse
                print(f"Error: {circ_err}")
                if circ_err.cycle_path:
                    print(f"Ciclo identificado: {' -> '.join(circ_err.cycle_path)}")
                # Se detiene la evaluación
                break

    finally:
        if args.input_file and stream != sys.stdin:
            stream.close()


if __name__ == "__main__":
    main()
