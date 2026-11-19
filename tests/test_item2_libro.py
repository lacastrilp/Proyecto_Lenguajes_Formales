import unittest
from src.common.grammar import Grammar
from src.item1_first_follow.first_follow import compute_first, compute_follow
from src.item2_parsers.ll1_parser import LL1Parser
from src.item2_parsers.slr1_parser import SLR1Parser

def build(text):
    g = Grammar.from_text(text)
    first = compute_first(g)
    follow = compute_follow(g, first)
    return g, first, follow, LL1Parser(g, first, follow), SLR1Parser(g, follow)

EXPR = "5\nS -> TA\nA -> +TA e\nT -> FB\nB -> *FB e\nF -> (S) i"

class TestClasificacion(unittest.TestCase):

    def test_ejercicio_4_6_5_ll1_pero_no_slr1(self):
        _, _, _, ll1, slr1 = build("3\nS -> AaAb BbBa\nA -> e\nB -> e")
        self.assertTrue(ll1.is_ll1)
        self.assertFalse(slr1.is_slr1)

    def test_ejercicio_4_6_6_slr1_pero_no_ll1(self):
        _, _, _, ll1, slr1 = build("2\nS -> SA A\nA -> a")
        self.assertFalse(ll1.is_ll1)
        self.assertTrue(slr1.is_slr1)

    def test_ejemplo_4_48_no_es_slr1(self):
        _, _, _, ll1, slr1 = build("3\nS -> L=R R\nL -> *R i\nR -> L")
        self.assertFalse(slr1.is_slr1)
        self.assertFalse(ll1.is_ll1)

    def test_expresiones_sin_recursion_izquierda(self):
        _, _, _, ll1, slr1 = build(EXPR)
        self.assertTrue(ll1.is_ll1)
        self.assertTrue(slr1.is_slr1)


class TestFirstFollowLibro(unittest.TestCase):

    def test_ejemplo_4_30(self):
        _, first, follow, _, _ = build(EXPR)
        self.assertEqual(first["F"], {"(", "i"})
        self.assertEqual(first["T"], {"(", "i"})
        self.assertEqual(first["S"], {"(", "i"})
        self.assertEqual(first["A"], {"+", "e"})
        self.assertEqual(first["B"], {"*", "e"})
        self.assertEqual(follow["S"], {")", "$"})
        self.assertEqual(follow["A"], {")", "$"})
        self.assertEqual(follow["T"], {"+", ")", "$"})
        self.assertEqual(follow["B"], {"+", ")", "$"})
        self.assertEqual(follow["F"], {"+", "*", ")", "$"})


class TestParsers(unittest.TestCase):

    def test_expresiones_ambos_parsers_coinciden(self):
        _, _, _, ll1, slr1 = build(EXPR)
        validas = ["i", "i+i*i", "(i)", "(i+i)*i", "i*i*i+i"]
        invalidas = ["", "+", "i+", ")i", "(i", "i i", "ii", "(i+i)*i)"]
        for s in validas:
            self.assertTrue(ll1.parse(s)[0], f"LL(1) debía aceptar {s}")
            self.assertTrue(slr1.parse(s)[0], f"SLR(1) debía aceptar {s}")
        for s in invalidas:
            self.assertFalse(ll1.parse(s)[0], f"LL(1) debía rechazar {s}")
            self.assertFalse(slr1.parse(s)[0], f"SLR(1) debía rechazar {s}")

    def test_cadena_vacia_en_el_lenguaje(self):
        _, _, _, ll1, slr1 = build("1\nS -> aS e")
        self.assertTrue(ll1.parse("e")[0])
        self.assertTrue(slr1.parse("e")[0])
        self.assertTrue(ll1.parse("aaa")[0])
        self.assertTrue(slr1.parse("aaa")[0])

    def test_cadena_vacia_fuera_del_lenguaje(self):
        _, _, _, ll1, slr1 = build("3\nS -> AB\nA -> aA d\nB -> bBc e")
        self.assertFalse(ll1.parse("e")[0])
        self.assertFalse(slr1.parse("e")[0])

    def test_caracteres_invalidos_se_rechazan(self):
        _, _, _, ll1, slr1 = build(EXPR)
        for s in ["i$i", "i$", "$", "iei", "x", "I"]:
            self.assertFalse(ll1.parse(s)[0], s)
            self.assertFalse(slr1.parse(s)[0], s)

    def test_ejemplo_1_del_enunciado(self):
        _, _, _, ll1, slr1 = build("3\nS -> S+T T\nT -> T*F F\nF -> (S) i")
        for s, esperado in [("i+i", True), ("(i)", True), ("(i+i)*i)", False)]:
            self.assertEqual(slr1.parse(s)[0], esperado, s)

    def test_error_si_se_usa_un_parser_que_no_aplica(self):
        _, _, _, ll1, slr1 = build("1\nS -> SS a")
        with self.assertRaises(ValueError):
            ll1.parse("a")
        with self.assertRaises(ValueError):
            slr1.parse("a")


if __name__ == "__main__":
    unittest.main()
