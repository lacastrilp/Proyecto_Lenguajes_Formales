from typing import Dict, Tuple, Set, Optional, List, FrozenSet
from collections import defaultdict
from src.common.grammar import Grammar
from src.common.parse_tree import ParseTreeNode

LR0Item = Tuple[str, str, int]

class SLR1Parser:

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
  
        moved_items: Set[LR0Item] = set()
        for head, body, pos in items:
            if pos < len(body) and body[pos] == symbol:
                moved_items.add((head, body, pos + 1))
        return self._closure(moved_items)

    def _build_automaton_and_tables(self) -> None:

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

        for i, state_items in enumerate(self.canonical_collection):
            for head, body, pos in state_items:
                if pos < len(body):
                    symbol = body[pos]

                    if self.grammar.is_terminal(symbol):
                        target_state = self._goto(state_items, symbol)
                        if target_state in self.canonical_collection:
                            j = self.canonical_collection.index(target_state)
                            self.action_table[(i, symbol)].add(("shift", j))
                else:

                    if head == self.AUGMENTED_START:
                        self.action_table[(i, "$")].add(("accept",))
                    else:
                        prod_str = "e" if body == "" else body
                        for a in self.follow_sets[head]:
                            self.action_table[(i, a)].add(("reduce", head, prod_str, len(body)))

            for nt in self.grammar.nonterminals:
                target_state = self._goto(state_items, nt)
                if target_state and target_state in self.canonical_collection:
                    j = self.canonical_collection.index(target_state)
                    self.goto_table[(i, nt)] = j

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

    def parse(self, input_string: str, trace: Optional[List[List[str]]] = None) -> Tuple[bool, Optional[ParseTreeNode]]:
        
        if not self.is_slr1:
            raise ValueError("No se puede analizar con SLR(1): la gramática no es SLR(1).")

        ParseTreeNode.reset_counter()

        tokens = "" if input_string == "e" else input_string
        for c in tokens:
            if not self.grammar.is_terminal(c):
                return False, None

        tokens_with_end = tokens + "$"

        ip = 0

        state_stack: List[int] = [0]
        node_stack: List[ParseTreeNode] = []

        while True:
            current_state = state_stack[-1]
            lookahead = tokens_with_end[ip]

            actions = self.action_table.get((current_state, lookahead), set())
            if trace is not None:
                if actions:
                    act = next(iter(actions))
                    if act[0] == "shift":
                        action_text = f"shift to {act[1]}"
                    elif act[0] == "reduce":
                        action_text = f"reduce by {act[1]} -> {act[2]}"
                    else:
                        action_text = "accept"
                else:
                    action_text = "error"
                trace.append([str(len(trace) + 1),
                              " ".join(str(st) for st in state_stack),
                              "".join(n.symbol for n in node_stack),
                              tokens_with_end[ip:], action_text])
            if not actions:
                return False, None

            action = next(iter(actions))
            action_type = action[0]

            if action_type == "shift":
                next_state = action[1]
                state_stack.append(next_state)

                leaf_node = ParseTreeNode(lookahead)
                leaf_node.set_attribute("lexval", lookahead)
                node_stack.append(leaf_node)
                ip += 1

            elif action_type == "reduce":
                head = action[1]
                prod_body = action[2]
                body_length = action[3]

                popped_children: List[ParseTreeNode] = []
                if body_length == 0:
                    eps_node = ParseTreeNode("e")
                    eps_node.set_attribute("lexval", "e")
                    popped_children.append(eps_node)
                else:
                    for _ in range(body_length):
                        state_stack.pop()
                        popped_children.append(node_stack.pop())
                    popped_children.reverse()

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
                if node_stack:
                    return True, node_stack[-1]
                return True, None
