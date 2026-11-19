import unittest

from src.common.grammar import Grammar
from src.item1_first_follow.first_follow import (
    compute_first,
    compute_follow,
    first_of_string,
    format_set_elements,
    format_sets_output,
)

class TestFirstFollow(unittest.TestCase):

    def setUp(self):
        # S no aparece primero y A, B y C pueden producir ε.
        self.grammar = Grammar.from_text(
            """4
            B -> b e
            S -> ABC
            C -> c e
            A -> a e"""
        )

        self.first = compute_first(self.grammar)
        self.follow = compute_follow(self.grammar, self.first)

    def test_first_con_varios_simbolos_anulables(self):
        """FIRST debe avanzar por todos los símbolos que producen ε."""
        self.assertEqual(self.first["A"], {"a", "e"})
        self.assertEqual(self.first["B"], {"b", "e"})
        self.assertEqual(self.first["C"], {"c", "e"})
        self.assertEqual(self.first["S"], {"a", "b", "c", "e"})

    def test_first_de_cadenas(self):
        """Verifica FIRST de cadenas y de la cadena vacía."""
        self.assertEqual(
            first_of_string(self.first, "ABC"),
            {"a", "b", "c", "e"},
        )
        self.assertEqual(
            first_of_string(self.first, "ABc"),
            {"a", "b", "c"},
        )
        self.assertEqual(first_of_string(self.first, ""), {"e"})
        self.assertEqual(first_of_string(self.first, "e"), {"e"})

    def test_follow_con_sufijos_anulables(self):
        """FOLLOW debe propagarse cuando el sufijo puede producir ε."""
        self.assertEqual(self.follow["S"], {"$"})
        self.assertEqual(self.follow["A"], {"b", "c", "$"})
        self.assertEqual(self.follow["B"], {"c", "$"})
        self.assertEqual(self.follow["C"], {"$"})

        for conjunto in self.follow.values():
            self.assertNotIn("e", conjunto)

    def test_simbolo_inicial_no_es_la_primera_produccion(self):
        """El símbolo inicial debe seguir siendo S."""
        self.assertNotEqual(self.grammar.nonterminals[0], "S")
        self.assertEqual(self.grammar.start_symbol, "S")
        self.assertIn("$", self.follow["S"])

    def test_orden_de_elementos(self):
        """Terminales en ASCII, después e y finalmente $."""
        self.assertEqual(
            format_set_elements({"z", "0", "+", "e", "$"}),
            "{+, 0, z, e, $}",
        )

    def test_formato_de_salida(self):
        """Verifica el formato exacto y el orden de los no terminales."""
        esperado = (
            "First(A) = {a, e}\n"
            "First(B) = {b, e}\n"
            "First(C) = {c, e}\n"
            "First(S) = {a, b, c, e}\n"
            "Follow(A) = {b, c, $}\n"
            "Follow(B) = {c, $}\n"
            "Follow(C) = {$}\n"
            "Follow(S) = {$}"
        )

        self.assertEqual(
            format_sets_output(self.grammar, self.first, self.follow),
            esperado,
        )


if __name__ == "__main__":
    unittest.main()