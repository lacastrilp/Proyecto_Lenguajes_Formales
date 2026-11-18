"""
Módulo del Analizador Sintáctico Ascendente SLR(1) (Simple LR).

Implementa:
1. Representación de ítems LR(0) y funciones CLOSURE y GOTO (Sección 4.6.2).
2. Construcción de la colección canónica de conjuntos de ítems LR(0) (Autómata LR(0)).
3. Construcción de las tablas ACTION y GOTO según el Algoritmo 4.46 (Sección 4.6.4).
4. Verificación de la condición SLR(1) (detección de conflictos shift/reduce y reduce/reduce).
5. Algoritmo de análisis sintáctico LR con pila de estados (Algoritmo 4.44).
6. Reconstrucción del árbol sintáctico (Parse Tree) durante las reducciones bottom-up.
"""

from typing import Dict, Tuple, Set, Optional, List, FrozenSet
from collections import defaultdict
from src.common.grammar import Grammar
from src.common.parse_tree import ParseTreeNode


# Tipo de Ítem LR(0): (cabeza, cuerpo_como_string, posicion_del_punto)
# Si cuerpo es cadena vacía "", representa una producción épsilon A -> e con el punto al final.
LR0Item = Tuple[str, str, int]


class SLR1Parser:
    """
    Analizador sintáctico ascendente SLR(1) basado en autómata LR(0) y conjuntos FOLLOW.
    """

    AUGMENTED_START = "S'"

    def __init__(self, grammar: Grammar, follow_sets: Dict[str, Set[str]]):
        self.grammar = grammar
        self.follow_sets = follow_sets
        self.canonical_collection: List[FrozenSet[LR0Item]] = []
        self.action_table: Dict[Tuple[int, str], Set[Tuple]] = defaultdict(set)
        self.goto_table: Dict[Tuple[int, str], int] = {}
        self.is_slr1: bool = True
        self.conflicts: List[str] = []
        
        self._build_automaton_and_tables()

    def _closure(self, items: Set[LR0Item]) -> FrozenSet[LR0Item]:
        """
        Calcula la clausura CLOSURE(I) de un conjunto de ítems LR(0).
        Reglas (Sección 4.6.2):
        1. Todo ítem en I se incluye en CLOSURE(I).
        2. Si [A -> alpha . B beta] está en CLOSURE(I) y B es no terminal,
           añadir [B -> . gamma] a CLOSURE(I) para cada alternativa B -> gamma.
        """
        closure_set = set(items)
        changed = True
        while changed:
            changed = False
            for head, body, pos in list(closure_set):
                if pos < len(body):
                    symbol = body[pos]
                    if self.grammar.is_nonterminal(symbol):
                        for alt in self.grammar.productions.get(symbol, []):
                            alt_body = "" if alt == "e" else alt
                            item: LR0Item = (symbol, alt_body, 0)
                            if item not in closure_set:
                                closure_set.add(item)
                                changed = True
        return frozenset(closure_set)

    def _goto(self, items: FrozenSet[LR0Item], symbol: str) -> FrozenSet[LR0Item]:
        """
        Calcula GOTO(I, X): la clausura del conjunto de ítems [A -> alpha X . beta]
        tales que [A -> alpha . X beta] está en I.
        """
        moved_items: Set[LR0Item] = set()
        for head, body, pos in items:
            if pos < len(body) and body[pos] == symbol:
                moved_items.add((head, body, pos + 1))
        return self._closure(moved_items)

    def _build_automaton_and_tables(self) -> None:
        """
        Construye la colección canónica de conjuntos de ítems LR(0) y las tablas ACTION y GOTO.
        Algoritmo 4.46.
        """
        # 1. Ítem inicial de la gramática aumentada: [S' -> . S]
        start_item: LR0Item = (self.AUGMENTED_START, self.grammar.start_symbol, 0)
        i0 = self._closure({start_item})
        self.canonical_collection = [i0]
        worklist = [i0]

        all_grammar_symbols = self.grammar.nonterminals + self.grammar.terminals

        while worklist:
            current_state = worklist.pop(0)
            for X in all_grammar_symbols:
                next_state = self._goto(current_state, X)
                if next_state and next_state not in self.canonical_collection:
                    self.canonical_collection.append(next_state)
                    worklist.append(next_state)

        # 2. Construcción de tablas ACTION y GOTO
        for i, state_items in enumerate(self.canonical_collection):
            for head, body, pos in state_items:
                if pos < len(body):
                    symbol = body[pos]
                    # Si el símbolo tras el punto es un terminal 'a' -> acción SHIFT
                    if self.grammar.is_terminal(symbol):
                        target_state = self._goto(state_items, symbol)
                        if target_state in self.canonical_collection:
                            j = self.canonical_collection.index(target_state)
                            self.action_table[(i, symbol)].add(("shift", j))
                else:
                    # El punto está al final de la producción
                    if head == self.AUGMENTED_START:
                        # [S' -> S .] -> acción ACCEPT en '$'
                        self.action_table[(i, "$")].add(("accept",))
                    else:
                        # [A -> alpha .] -> acción REDUCE para todo a en FOLLOW(A)
                        prod_str = "e" if body == "" else body
                        for a in self.follow_sets[head]:
                            self.action_table[(i, a)].add(("reduce", head, prod_str, len(body)))

            # Transiciones GOTO para no terminales
            for nt in self.grammar.nonterminals:
                target_state = self._goto(state_items, nt)
                if target_state and target_state in self.canonical_collection:
                    j = self.canonical_collection.index(target_state)
                    self.goto_table[(i, nt)] = j

        # 3. Verificación de conflictos en la tabla ACTION
        for (state, sym), actions in self.action_table.items():
            if len(actions) > 1:
                self.is_slr1 = False
                action_descriptions = []
                for act in actions:
                    if act[0] == "shift":
                        action_descriptions.append(f"shift {act[1]}")
                    elif act[0] == "reduce":
                        action_descriptions.append(f"reduce {act[1]}->{act[2]}")
                    elif act[0] == "accept":
                        action_descriptions.append("accept")
                desc = " / ".join(action_descriptions)
                self.conflicts.append(f"Conflicto en Estado {state}, Símbolo '{sym}': {desc}")

    def parse(self, input_string: str) -> Tuple[bool, Optional[ParseTreeNode]]:
        """
        Ejecuta el Algoritmo 4.44 (LR parsing) sobre la cadena de entrada.
        
        Manejo de cadena vacía:
        Si input_string == 'e', se analiza como "".
        
        Retorna:
            (True, root_node) si la cadena es aceptada, reconstruyendo el árbol de análisis.
            (False, None) si ocurre un error sintáctico.
        """
        if not self.is_slr1:
            raise ValueError("No se puede analizar con SLR(1): la gramática no es SLR(1).")

        ParseTreeNode.reset_counter()

        tokens = "" if input_string == "e" else input_string
        tokens_with_end = tokens + "$"
        ip = 0

        # Pila de estados numéricos
        state_stack: List[int] = [0]
        # Pila paralela de nodos para la construcción ascendente del árbol sintáctico
        node_stack: List[ParseTreeNode] = []

        while True:
            current_state = state_stack[-1]
            lookahead = tokens_with_end[ip]

            actions = self.action_table.get((current_state, lookahead), set())
            if not actions:
                # Error sintáctico: celda vacía
                return False, None

            action = next(iter(actions))
            action_type = action[0]

            if action_type == "shift":
                next_state = action[1]
                state_stack.append(next_state)
                
                # Crear nodo hoja para el terminal desplazado
                leaf_node = ParseTreeNode(lookahead)
                leaf_node.set_attribute("lexval", lookahead)
                node_stack.append(leaf_node)
                ip += 1

            elif action_type == "reduce":
                head = action[1]
                prod_body = action[2]
                body_length = action[3]

                # Desapilar 'body_length' estados y nodos hijos
                popped_children: List[ParseTreeNode] = []
                if body_length == 0:
                    # Producción épsilon A -> e: se crea un hijo hoja 'e'
                    eps_node = ParseTreeNode("e")
                    eps_node.set_attribute("lexval", "e")
                    popped_children.append(eps_node)
                else:
                    for _ in range(body_length):
                        state_stack.pop()
                        popped_children.append(node_stack.pop())
                    # Los nodos fueron desapilados de derecha a izquierda; se invierten a orden natural
                    popped_children.reverse()

                # Crear el nodo padre no terminal con la producción aplicada
                parent_node = ParseTreeNode(
                    symbol=head,
                    production=f"{head} -> {prod_body}",
                    children=popped_children
                )

                state_after_pop = state_stack[-1]
                if (state_after_pop, head) not in self.goto_table:
                    return False, None

                next_state = self.goto_table[(state_after_pop, head)]
                state_stack.append(next_state)
                node_stack.append(parent_node)

            elif action_type == "accept":
                # Análisis completado exitosamente
                if node_stack:
                    return True, node_stack[-1]
                return True, None
