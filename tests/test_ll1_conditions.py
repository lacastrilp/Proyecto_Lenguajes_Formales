import unittest
from src.common.grammar import Grammar
from src.item1_first_follow.first_follow import compute_first, compute_follow
from src.item2_parsers.ll1_parser import LL1Parser
from src.item2_parsers.report_output import format_ll1_table, format_lr0_automaton, format_slr_tables

def build(text):
    g = Grammar.from_text(text)
    first = compute_first(g)
    return LL1Parser(g, first, compute_follow(g, first))


class TestLL1Conditions(unittest.TestCase):

    def test_ejemplo_2_es_ll1(self):
        p = build("3\nS -> AB\nA -> aA d\nB -> bBc e")
        self.assertTrue(p.is_ll1)
        self.assertEqual(p.violations, [])

    def test_ejemplo_1_no_es_ll1(self):
        p = build("3\nS -> S+T T\nT -> T*F F\nF -> (S) i")
        self.assertFalse(p.is_ll1)

    def test_ejemplo_3_no_es_ll1(self):
        p = build("1\nS -> SS a")
        self.assertFalse(p.is_ll1)

    def test_ejercicio_4_6_5_es_ll1(self):
        p = build("3\nS -> AaAb BbBa\nA -> e\nB -> e")
        self.assertTrue(p.is_ll1)

    def test_ejercicio_4_6_6_no_es_ll1(self):
        p = build("2\nS -> SA A\nA -> a")
        self.assertFalse(p.is_ll1)

    def test_condicion_1(self):
        p = build("4\nS -> A\nA -> aB aC\nB -> b\nC -> c")
        self.assertTrue(any("Condición 1" in v for v in p.violations))

    def test_condicion_2(self):
        p = build("4\nS -> A\nA -> B C\nB -> e\nC -> e")
        self.assertTrue(any("Condición 2" in v for v in p.violations))

    def test_condicion_3(self):
        p = build("2\nS -> Aa\nA -> a e")
        self.assertTrue(any("Condición 3" in v for v in p.violations))

    def test_tabla_y_condicion_coinciden(self):
        for text in ["3\nS -> AB\nA -> aA d\nB -> bBc e",
                     "3\nS -> S+T T\nT -> T*F F\nF -> (S) i",
                     "1\nS -> SS a",
                     "3\nS -> AaAb BbBa\nA -> e\nB -> e",
                     "2\nS -> SA A\nA -> a"]:
            self.assertTrue(build(text).methods_agree, text)


if __name__ == "__main__":
    unittest.main()
