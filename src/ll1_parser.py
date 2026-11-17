"""
Módulo del Analizador Sintáctico Descendente No Recursivo LL(1).

Implementa:
1. La construcción de la tabla de análisis sintáctico predictivo (Algoritmo 4.31).
2. La verificación de la condición LL(1) (ausencia de entradas múltiples en la tabla).
3. El algoritmo de análisis sintáctico no recursivo dirigido por tabla con pila (Algoritmo 4.34).
4. La construcción del árbol sintáctico (Parse Tree) para su posterior uso en la SDD.
"""

from typing import Dict, Tuple, Set, Optional, List
from collections import defaultdict
from src.grammar import Grammar
from src.first_follow import first_of_string
from src.parse_tree import ParseTreeNode


class LL1Parser:
    """
    Analizador predictivo LL(1) no recursivo basado en tabla.
    """

    def __init__(self, grammar: Grammar, first_sets: Dict[str, Set[str]], follow_sets: Dict[str, Set[str]]):
        self.grammar = grammar
        self.first_sets = first_sets
        self.follow_sets = follow_sets
        self.table: Dict[Tuple[str, str], Set[Tuple[str, str]]] = defaultdict(set)
        self.is_ll1: bool = True
        self.conflicts: List[str] = []
        self._build_table()

    def _build_table(self) -> None:
        """
        Construye la tabla de parseo predictivo M[A, a] según el Algoritmo 4.31:
        Para cada producción A -> alpha:
          1. Para cada terminal 'a' in FIRST(alpha) (con a != 'e'):
             añadir A -> alpha a M[A, a].
          2. Si 'e' in FIRST(alpha):
             Para cada símbolo 'b' in FOLLOW(A) (terminal o '$'):
               añadir A -> alpha a M[A, b].
        """
        for head, bodies in self.grammar.productions.items():
            for body in bodies:
                first_body = first_of_string(self.first_sets, body)
                
                # Regla 1: terminales en FIRST(alpha)
                for a in (first_body - {"e"}):
                    self.table[(head, a)].add((head, body))
                
                # Regla 2: si e in FIRST(alpha), FOLLOW(head)
                if "e" in first_body:
                    for b in self.follow_sets[head]:
                        self.table[(head, b)].add((head, body))

        # Verificar si existen colisiones (múltiples producciones en una misma celda)
        for (head, sym), prods in self.table.items():
            if len(prods) > 1:
                self.is_ll1 = False
                prods_str = ", ".join(f"{h}->{b}" for h, b in prods)
                self.conflicts.append(f"Conflicto en M[{head}, {sym}]: {prods_str}")

    def parse(self, input_string: str) -> Tuple[bool, Optional[ParseTreeNode]]:
        """
        Ejecuta el Algoritmo 4.34 sobre la cadena de entrada 'input_string'.
        
        Manejo de cadena vacía:
        Según la Sección 2.2.2 de LF_project_2026_2.pdf, la cadena vacía se proporciona
        como una línea que contiene únicamente 'e'. Si input_string == 'e', se analiza como "".
        
        Retorna:
            (True, root_node) si la cadena es aceptada, generando su árbol sintáctico.
            (False, None) si la cadena contiene errores sintácticos.
        """
        if not self.is_ll1:
            raise ValueError("No se puede analizar con LL(1): la gramática no es LL(1).")

        ParseTreeNode.reset_counter()
        
        # Procesar cadena vacía especial 'e'
        tokens = "" if input_string == "e" else input_string
        tokens_with_end = tokens + "$"
        ip = 0

        # La pila almacena pares: (símbolo_gramatical, nodo_en_el_árbol)
        root_node = ParseTreeNode(self.grammar.start_symbol)
        stack: List[Tuple[str, Optional[ParseTreeNode]]] = [("$", None), (self.grammar.start_symbol, root_node)]

        while stack:
            X, node = stack.pop()
            a = tokens_with_end[ip]

            if X == "$" and a == "$":
                # Análisis finalizado con éxito
                return True, root_node

            if X == a and X != "$":
                # Coincidencia de terminal (match)
                if node is not None:
                    node.set_attribute("lexval", a)
                ip += 1
            elif self.grammar.is_terminal(X) or X == "$":
                # Discrepancia entre terminal esperado y terminal recibido
                return False, None
            else:
                # X es un no terminal
                entries = self.table.get((X, a), set())
                if not entries:
                    # Celda de error sintáctico
                    return False, None

                head, body = next(iter(entries))
                if node is not None:
                    node.production = f"{head} -> {body}"

                if body == "e":
                    # Producción épsilon: se crea un hijo hoja 'e'
                    if node is not None:
                        eps_node = ParseTreeNode("e", children=[])
                        eps_node.set_attribute("lexval", "e")
                        node.add_child(eps_node)
                else:
                    # Crear los nodos hijos para los símbolos del cuerpo
                    child_nodes: List[ParseTreeNode] = []
                    for char in body:
                        c_node = ParseTreeNode(char)
                        child_nodes.append(c_node)
                        if node is not None:
                            node.add_child(c_node)

                    # Apilar en orden inverso para que el primer símbolo quede en el tope
                    for char, c_node in reversed(list(zip(body, child_nodes))):
                        stack.append((char, c_node))

        return False, None
