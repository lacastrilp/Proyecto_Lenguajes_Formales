"""
Módulo de Visualización Interactiva para el Árbol Sintáctico y la Evaluación de la SDD.

Ofrece una interfaz en terminal clara, elegante y paso a paso para:
1. Visualizar el árbol sintáctico con caracteres Unicode (box-drawing).
2. Inspeccionar el grafo de dependencias y las aristas entre atributos.
3. Evaluar los atributos paso a paso pulsando Enter para avanzar cada cálculo.
"""

import sys
from typing import List, Dict, Set, Any
from src.parse_tree import ParseTreeNode
from src.sdd import SDDDefinition
from src.sdd_evaluator import SDDEvaluator, AttrInstance, SDDCircularDefinitionError


def render_tree_ascii(node: ParseTreeNode, prefix: str = "", is_last: bool = True) -> List[str]:
    """
    Genera una representación jerárquica con caracteres de dibujo de cajas.
    """
    connector = "└── " if is_last else "├── "
    attrs_str = ""
    if node.attributes:
        attrs = ", ".join(f"{k}={v}" for k, v in sorted(node.attributes.items()))
        attrs_str = f" [{attrs}]"
    
    prod_str = f" ({node.production})" if node.production else ""
    line = f"{prefix}{connector}{node.symbol}{prod_str}{attrs_str}"
    lines = [line]

    new_prefix = prefix + ("    " if is_last else "│   ")
    child_count = len(node.children)
    for i, child in enumerate(node.children):
        is_child_last = (i == child_count - 1)
        lines.extend(render_tree_ascii(child, new_prefix, is_child_last))

    return lines


class SDDVisualizer:
    """
    Visualizador interactivo para la evaluación de atributos de la SDD.
    """

    def __init__(self, sdd: SDDDefinition):
        self.sdd = sdd
        self.evaluator = SDDEvaluator(sdd)

    def display_dependency_graph(self, root: ParseTreeNode) -> None:
        """Muestra en consola la lista de vértices y dependencias directas."""
        adj, in_deg, _, labels, _ = self.evaluator.build_dependency_graph(root)
        print("\n" + "=" * 65)
        print("          GRAFO DE DEPENDENCIAS DE ATRIBUTOS (DEPENDENCY GRAPH)")
        print("=" * 65)
        print(f"Total de instancias de atributos (vértices): {len(in_deg)}")
        print("\nDependencias Dirigidas (u -> v significa: u DEBE evaluarse antes que v):")
        for u in sorted(adj.keys(), key=lambda x: labels[x]):
            targets = [labels[v] for v in sorted(adj[u], key=lambda x: labels[x])]
            if targets:
                print(f"  {labels[u]:<20} ──▶  {', '.join(targets)}")
        print("=" * 65 + "\n")

    def run_interactive(self, root: ParseTreeNode) -> None:
        """
        Ejecuta la evaluación paso a paso interactiva, esperando Enter tras cada cálculo.
        """
        adj, in_deg, compute_info, labels, nodes_by_id = self.evaluator.build_dependency_graph(root)
        all_vertices = set(in_deg.keys())

        # Cola de Kahn
        from collections import deque
        queue = deque([v for v in all_vertices if in_deg[v] == 0])
        evaluated: List[AttrInstance] = []

        print("\n" + "=" * 65)
        print("   EVALUACIÓN INTERACTIVA PASO A PASO DE LA SDD (STEP-BY-STEP)")
        print("=" * 65)
        print("Presiona [ENTER] para avanzar al siguiente atributo o escribe 'q' para salir.")

        step = 0
        while queue:
            u = queue.popleft()
            step += 1
            evaluated.append(u)

            val_repr = "Preexistente / Lexval"
            if u in compute_info:
                compute_fn, dep_vertices, target_node, target_attr = compute_info[u]
                args = [nodes_by_id[d_node_id].get_attribute(d_attr) for d_node_id, d_attr in dep_vertices]
                val = compute_fn(*args)
                target_node.set_attribute(target_attr, val)
                val_repr = f"{val}"

            print(f"\n[Paso {step}] Evaluando atributo: {labels[u]}  ===>  Valor: {val_repr}")
            print("-" * 50)
            for line in render_tree_ascii(root):
                print(line)

            for neighbor in adj.get(u, set()):
                in_deg[neighbor] -= 1
                if in_deg[neighbor] == 0:
                    queue.append(neighbor)

            if queue:
                try:
                    cmd = input("\n[Presiona Enter para el siguiente paso / 'q' para terminar]: ").strip()
                    if cmd.lower() == 'q':
                        print("Evaluación interactiva interrumpida por el usuario.")
                        return
                except (EOFError, KeyboardInterrupt):
                    return

        if len(evaluated) < len(all_vertices):
            print("\n[ALERTA] La SDD contiene dependencias circulares.")
        else:
            main_val = root.get_attribute(self.sdd.main_attribute)
            print("\n" + "=" * 65)
            print(f"  EVALUACIÓN FINALIZADA. Valor del atributo principal ({self.sdd.main_attribute}): {main_val}")
            print("=" * 65 + "\n")
