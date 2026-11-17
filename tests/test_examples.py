"""
Suite de Pruebas Automatizadas para el Proyecto de Lenguajes Formales.

Verifica:
1. Ejemplo 1 del documento LF_project_2026_2.pdf (Gramática SLR(1), no LL(1)).
2. Ejemplo 2 del documento (Gramática tanto LL(1) como SLR(1), conjuntos First y Follow).
3. Ejemplo 3 del documento (Gramática ni LL(1) ni SLR(1)).
4. Pruebas completas del Item 3 (SDD):
   - Cadena más corta.
   - Cadena válida con suma y anidamiento.
   - Cadena profundamente anidada.
   - Cadena que NO pertenece al lenguaje.
   - Prueba de detección de circularidad en la SDD.
"""

import unittest
from src.grammar import Grammar
from src.first_follow import compute_first, compute_follow, format_sets_output
from src.ll1_parser import LL1Parser
from src.slr1_parser import SLR1Parser
from src.sdd import create_project_sdd, create_circular_sdd
from src.sdd_evaluator import SDDEvaluator, SDDCircularDefinitionError


class TestProjectExamples(unittest.TestCase):

    def test_example_1(self):
        """Ejemplo 1: Expresiones aritméticas con precedencia (SLR(1), no LL(1))."""
        raw_grammar = """3
S -> S+T T
T -> T*F F
F -> (S) i"""
        g = Grammar.from_text(raw_grammar)
        first_sets = compute_first(g)
        follow_sets = compute_follow(g, first_sets)

        ll1 = LL1Parser(g, first_sets, follow_sets)
        slr1 = SLR1Parser(g, follow_sets)

        self.assertFalse(ll1.is_ll1, "El ejemplo 1 no debe ser LL(1) debido a recursión izquierda.")
        self.assertTrue(slr1.is_slr1, "El ejemplo 1 debe ser SLR(1).")

        # Cadenas especificadas en el PDF
        self.assertTrue(slr1.parse("i+i")[0])
        self.assertTrue(slr1.parse("(i)")[0])
        self.assertFalse(slr1.parse("(i+i)*i)")[0])

    def test_example_2(self):
        """Ejemplo 2: Gramática tanto LL(1) como SLR(1)."""
        raw_grammar = """3
S -> AB
A -> aA d
B -> bBc e"""
        g = Grammar.from_text(raw_grammar)
        first_sets = compute_first(g)
        follow_sets = compute_follow(g, first_sets)

        ll1 = LL1Parser(g, first_sets, follow_sets)
        slr1 = SLR1Parser(g, follow_sets)

        self.assertTrue(ll1.is_ll1, "El ejemplo 2 debe ser LL(1).")
        self.assertTrue(slr1.is_slr1, "El ejemplo 2 debe ser SLR(1).")

        # Verificar conjuntos First y Follow
        expected_output = (
            "First(A) = {a, d}\n"
            "First(B) = {b, e}\n"
            "First(S) = {a, d}\n"
            "Follow(A) = {b, $}\n"
            "Follow(B) = {c, $}\n"
            "Follow(S) = {$}"
        )
        self.assertEqual(format_sets_output(g, first_sets, follow_sets), expected_output)

        # Cadenas analizadas con LL(1)
        self.assertTrue(ll1.parse("d")[0])
        self.assertTrue(ll1.parse("adbc")[0])
        self.assertFalse(ll1.parse("a")[0])

        # Cadenas analizadas con SLR(1)
        self.assertTrue(slr1.parse("d")[0])
        self.assertTrue(slr1.parse("adbc")[0])
        self.assertFalse(slr1.parse("a")[0])

    def test_example_3(self):
        """Ejemplo 3: Gramática ambigua con recursión izquierda directa (ni LL(1) ni SLR(1))."""
        raw_grammar = """1
S -> SS a"""
        g = Grammar.from_text(raw_grammar)
        first_sets = compute_first(g)
        follow_sets = compute_follow(g, first_sets)

        ll1 = LL1Parser(g, first_sets, follow_sets)
        slr1 = SLR1Parser(g, follow_sets)

        self.assertFalse(ll1.is_ll1, "El ejemplo 3 no debe ser LL(1).")
        self.assertFalse(slr1.is_slr1, "El ejemplo 3 no debe ser SLR(1).")

    def test_item3_sdd_evaluator(self):
        """Pruebas completas del evaluador SDD con la gramática oficial de Item 3."""
        sdd = create_project_sdd()
        evaluator = SDDEvaluator(sdd)
        grammar = Grammar.from_text(sdd.grammar_text)
        follow_sets = compute_follow(grammar, compute_first(grammar))
        parser = SLR1Parser(grammar, follow_sets)

        # 1. Cadena más corta: '0' y '1'
        ok, tree = parser.parse("0")
        self.assertTrue(ok)
        order, val = evaluator.evaluate(tree)
        self.assertEqual(val, 0)

        ok, tree = parser.parse("1")
        self.assertTrue(ok)
        order, val = evaluator.evaluate(tree)
        self.assertEqual(val, 1)  # 2^0 = 1

        # 2. Expresión simple con suma: '1+0'
        ok, tree = parser.parse("1+0")
        self.assertTrue(ok)
        order, val = evaluator.evaluate(tree)
        self.assertEqual(val, 1)

        # 3. Anidamiento con paréntesis: '(1)' -> d=1, 2^1 = 2
        ok, tree = parser.parse("(1)")
        self.assertTrue(ok)
        order, val = evaluator.evaluate(tree)
        self.assertEqual(val, 2)
        self.assertEqual(tree.get_attribute("max_d"), 1)

        # 4. Cadena profundamente anidada: '((1+0)+(1))'
        # Nivel 2: 1 at d=2 -> val=4. 0 at d=2 -> 0. Suma = 4.
        # Nivel 2: 1 at d=2 -> val=4.
        # Total = 4 + 4 = 8.
        ok, tree = parser.parse("((1+0)+(1))")
        self.assertTrue(ok)
        order, val = evaluator.evaluate(tree)
        self.assertEqual(val, 8)
        self.assertEqual(tree.get_attribute("max_d"), 2)

        # 5. Cadena que NO pertenece al lenguaje
        ok, tree = parser.parse("1++0")
        self.assertFalse(ok)
        self.assertIsNone(tree)

        ok, tree = parser.parse("(1+")
        self.assertFalse(ok)
        self.assertIsNone(tree)

    def test_item3_circular_detection(self):
        """Verifica que el evaluador detecte y reporte definiciones circulares en la SDD."""
        circular_sdd = create_circular_sdd()
        evaluator = SDDEvaluator(circular_sdd)
        grammar = Grammar.from_text(circular_sdd.grammar_text)
        follow_sets = compute_follow(grammar, compute_first(grammar))
        parser = SLR1Parser(grammar, follow_sets)

        ok, tree = parser.parse("1")
        self.assertTrue(ok)
        with self.assertRaises(SDDCircularDefinitionError) as ctx:
            evaluator.evaluate(tree)

        self.assertIn("CIRCULAR", str(ctx.exception))
        self.assertTrue(len(ctx.exception.cycle_path) > 0)


if __name__ == "__main__":
    unittest.main()
