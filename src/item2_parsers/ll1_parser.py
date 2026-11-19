from typing import Dict, Tuple, Set, Optional, List
from collections import defaultdict
from src.common.grammar import Grammar
from src.item1_first_follow.first_follow import first_of_string
from src.common.parse_tree import ParseTreeNode


class LL1Parser:
  
    def __init__(self, grammar: Grammar, first_sets: Dict[str, Set[str]], follow_sets: Dict[str, Set[str]]):
        self.grammar = grammar
        self.first_sets = first_sets
        self.follow_sets = follow_sets
        self.table: Dict[Tuple[str, str], Set[Tuple[str, str]]] = defaultdict(set)
        self.is_ll1: bool = True
        self.conflicts: List[str] = []
        self._build_table()

        # Condición LL(1) de la sección 4.4.3 (las tres reglas)
        self.violations: List[str] = self.check_ll1_conditions()
        table_says_ll1 = self.is_ll1        
        self.is_ll1 = len(self.violations) == 0
        # Verificación cruzada: los dos métodos deben coincidir
        self.methods_agree: bool = (self.is_ll1 == table_says_ll1)

    def _build_table(self) -> None:

        for head, bodies in self.grammar.productions.items():
            for body in bodies:
                first_body = first_of_string(self.first_sets, body)
                
                for a in (first_body - {"e"}):
                    self.table[(head, a)].add((head, body))
                
                if "e" in first_body:
                    for b in self.follow_sets[head]:
                        self.table[(head, b)].add((head, body))

        for (head, sym), prods in self.table.items():
            if len(prods) > 1:
                self.is_ll1 = False
                prods_str = ", ".join(f"{h}->{b}" for h, b in prods)
                self.conflicts.append(f"Conflicto en M[{head}, {sym}]: {prods_str}")

    
    def check_ll1_conditions(self) -> List[str]:
        
        violations: List[str] = []
        for head, bodies in self.grammar.productions.items():
            alts = list(dict.fromkeys(bodies)) 
            for i in range(len(alts)):
                for j in range(i + 1, len(alts)):
                    alpha, beta = alts[i], alts[j]
                    first_a = first_of_string(self.first_sets, alpha)
                    first_b = first_of_string(self.first_sets, beta)
                    follow_head = self.follow_sets[head]

                    # Condición 1
                    common = (first_a - {"e"}) & (first_b - {"e"})
                    if common:
                        violations.append(
                            f"Condición 1 en {head}: {alpha} y {beta} "
                            f"comparten {sorted(common)}")

                    # Condición 2
                    if "e" in first_a and "e" in first_b:
                        violations.append(
                            f"Condición 2 en {head}: {alpha} y {beta} "
                            f"derivan ambas la cadena vacía")

                    # Condición 3 (en los dos sentidos)
                    if "e" in first_b:
                        clash = (first_a - {"e"}) & follow_head
                        if clash:
                            violations.append(
                                f"Condición 3 en {head}: {beta} deriva e y "
                                f"FIRST({alpha}) comparte {sorted(clash)} con FOLLOW({head})")
                    if "e" in first_a:
                        clash = (first_b - {"e"}) & follow_head
                        if clash:
                            violations.append(
                                f"Condición 3 en {head}: {alpha} deriva e y "
                                f"FIRST({beta}) comparte {sorted(clash)} con FOLLOW({head})")
        return violations
    
    def parse(self, input_string: str, trace: Optional[List[List[str]]] = None) -> Tuple[bool, Optional[ParseTreeNode]]:
        
        if not self.is_ll1:
            raise ValueError("No se puede analizar con LL(1): la gramática no es LL(1).")

        ParseTreeNode.reset_counter()
        
        tokens = "" if input_string == "e" else input_string
        for c in tokens:
            if not self.grammar.is_terminal(c):
                return False, None

        tokens_with_end = tokens + "$"

        ip = 0

        root_node = ParseTreeNode(self.grammar.start_symbol)
        stack: List[Tuple[str, Optional[ParseTreeNode]]] = [("$", None), (self.grammar.start_symbol, root_node)]

        while stack:
                    if trace is not None:
                        top, cur = stack[-1][0], tokens_with_end[ip]
                        if top == "$" and cur == "$":
                            action = "aceptar"
                        elif top == cur:
                            action = f"match {cur}"
                        elif self.grammar.is_terminal(top) or top == "$":
                            action = "error"
                        else:
                            entry = self.table.get((top, cur), set())
                            if entry:
                                h, b = next(iter(entry))
                                action = f"output {h} -> {b}"
                            else:
                                action = "error"
                        trace.append([tokens[:ip],
                                      "".join(sym for sym, _ in reversed(stack)),
                                      tokens_with_end[ip:], action])
        
                    X, node = stack.pop()
                    a = tokens_with_end[ip]

                    if X == "$" and a == "$":
                        return True, root_node

                    if X == a and X != "$":
                        if node is not None:
                            node.set_attribute("lexval", a)
                        ip += 1
                    elif self.grammar.is_terminal(X) or X == "$":
                        return False, None
                    else:
                        entries = self.table.get((X, a), set())
                        if not entries:
                            return False, None

                        head, body = next(iter(entries))
                        if node is not None:
                            node.production = f"{head} -> {body}"

                        if body == "e":
                            if node is not None:
                                eps_node = ParseTreeNode("e", children=[])
                                eps_node.set_attribute("lexval", "e")
                                node.add_child(eps_node)
                        else:
                            child_nodes: List[ParseTreeNode] = []
                            for char in body:
                                c_node = ParseTreeNode(char)
                                child_nodes.append(c_node)
                                if node is not None:
                                    node.add_child(c_node)

                            for char, c_node in reversed(list(zip(body, child_nodes))):
                                stack.append((char, c_node))

        return False, None
