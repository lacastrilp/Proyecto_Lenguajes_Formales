"""
Módulo de Definición de SDD (Syntax-Directed Definition) como Estructura de Datos Pura.

Cumple estrictamente con el requerimiento del Paso 5 (Sección 3 de LF_project_2026_2.pdf):
'Store the SDD as data: for each production, the list of its semantic rules,
and for each rule the attribute it defines, the attributes it uses, and the
function that computes it. The evaluator must not know anything about your
particular SDD: changing the SDD must only require changing this data.'
"""

from typing import Callable, List, Tuple, Dict, Any


class SemanticRule:
    """
    Representa una regla semántica individual asociada a una producción A -> X_1 ... X_k.
    
    Notación de símbolos:
      - 0 representa la cabeza A (Head).
      - 1, 2, ..., k representan los símbolos del cuerpo X_1, X_2, ..., X_k.
      
    Atributos:
        target: Tupla (índice_símbolo, nombre_atributo) que define la regla.
                Si símbolo == 0, define un atributo sintetizado de la cabeza.
                Si símbolo > 0, define un atributo heredado de un símbolo del cuerpo.
        dependencies: Lista de tuplas (índice_símbolo, nombre_atributo) cuyos valores
                      son necesarios para calcular 'target'.
        compute_fn: Función callable f(inputs) -> Any que recibe los valores de
                    las dependencias en el mismo orden de la lista y retorna el valor calculado.
        description: Cadena legible que describe la regla (ej. "L[1].d = 0").
    """

    def __init__(
        self,
        target: Tuple[int, str],
        dependencies: List[Tuple[int, str]],
        compute_fn: Callable[..., Any],
        description: str = ""
    ):
        self.target = target
        self.dependencies = dependencies
        self.compute_fn = compute_fn
        self.description = description

    def __repr__(self) -> str:
        return f"Rule({self.description or self.target})"


class SDDDefinition:
    """
    Contenedor de datos que almacena las reglas semánticas indexadas por producción.
    """

    def __init__(self, grammar_text: str, rules_by_production: Dict[str, List[SemanticRule]], main_attribute: str = "val"):
        self.grammar_text = grammar_text
        self.rules: Dict[str, List[SemanticRule]] = rules_by_production
        self.main_attribute = main_attribute

    def get_rules_for_production(self, prod_signature: str) -> List[SemanticRule]:
        """Retorna la lista de reglas semánticas para una producción dada (ej. 'L -> BR')."""
        return self.rules.get(prod_signature, [])


def create_project_sdd() -> SDDDefinition:
    """
    Crea y retorna la SDD oficial del proyecto para el Item 3.
    
    Gramática Seleccionada:
      S -> L
      L -> BR
      R -> +L e
      B -> (L) 0 1
      
    Atributos:
      - d (Heredado): Profundidad de anidamiento de paréntesis / factor de escala posicional.
      - val (Sintetizado): Valor numérico acumulado y ponderado (2^d para bits 1).
      - max_d (Sintetizado): Máxima profundidad de anidamiento alcanzada.
    """
    grammar_text = """4
S -> L
L -> BR
R -> +L e
B -> (L) 0 1"""

    rules: Dict[str, List[SemanticRule]] = {}

    # 1. S -> L  (S es símbolo 0, L es símbolo 1)
    # L.d = 0
    # S.val = L.val
    # S.max_d = L.max_d
    rules["S -> L"] = [
        SemanticRule((1, "d"), [], lambda: 0, "L.d = 0"),
        SemanticRule((0, "val"), [(1, "val")], lambda l_val: l_val, "S.val = L.val"),
        SemanticRule((0, "max_d"), [(1, "max_d")], lambda l_max: l_max, "S.max_d = L.max_d")
    ]

    # 2. L -> BR (L es 0, B es 1, R es 2)
    # B.d = L.d
    # R.d = L.d
    # L.val = B.val + R.val
    # L.max_d = max(B.max_d, R.max_d)
    rules["L -> BR"] = [
        SemanticRule((1, "d"), [(0, "d")], lambda l_d: l_d, "B.d = L.d"),
        SemanticRule((2, "d"), [(0, "d")], lambda l_d: l_d, "R.d = L.d"),
        SemanticRule((0, "val"), [(1, "val"), (2, "val")], lambda b_val, r_val: b_val + r_val, "L.val = B.val + R.val"),
        SemanticRule((0, "max_d"), [(1, "max_d"), (2, "max_d")], lambda b_m, r_m: max(b_m, r_m), "L.max_d = max(B.max_d, R.max_d)")
    ]

    # 3. R -> +L (R es 0, '+' es 1, L es 2)
    # L.d = R.d
    # R.val = L.val
    # R.max_d = L.max_d
    rules["R -> +L"] = [
        SemanticRule((2, "d"), [(0, "d")], lambda r_d: r_d, "L.d = R.d"),
        SemanticRule((0, "val"), [(2, "val")], lambda l_val: l_val, "R.val = L.val"),
        SemanticRule((0, "max_d"), [(2, "max_d")], lambda l_max: l_max, "R.max_d = L.max_d")
    ]

    # 4. R -> e  (R es 0, 'e' es 1)
    # R.val = 0
    # R.max_d = R.d
    rules["R -> e"] = [
        SemanticRule((0, "val"), [], lambda: 0, "R.val = 0"),
        SemanticRule((0, "max_d"), [(0, "d")], lambda r_d: r_d, "R.max_d = R.d")
    ]

    # 5. B -> (L) (B es 0, '(' es 1, L es 2, ')' es 3)
    # L.d = B.d + 1
    # B.val = L.val
    # B.max_d = L.max_d
    rules["B -> (L)"] = [
        SemanticRule((2, "d"), [(0, "d")], lambda b_d: b_d + 1, "L.d = B.d + 1"),
        SemanticRule((0, "val"), [(2, "val")], lambda l_val: l_val, "B.val = L.val"),
        SemanticRule((0, "max_d"), [(2, "max_d")], lambda l_max: l_max, "B.max_d = L.max_d")
    ]

    # 6. B -> 0  (B es 0, '0' es 1)
    # B.val = 0
    # B.max_d = B.d
    rules["B -> 0"] = [
        SemanticRule((0, "val"), [], lambda: 0, "B.val = 0"),
        SemanticRule((0, "max_d"), [(0, "d")], lambda b_d: b_d, "B.max_d = B.d")
    ]

    # 7. B -> 1  (B es 0, '1' es 1)
    # B.val = 2 ** B.d (peso exponencial de acuerdo al nivel de anidamiento)
    # B.max_d = B.d
    rules["B -> 1"] = [
        SemanticRule((0, "val"), [(0, "d")], lambda b_d: 2 ** b_d, "B.val = 2 ** B.d"),
        SemanticRule((0, "max_d"), [(0, "d")], lambda b_d: b_d, "B.max_d = B.d")
    ]

    return SDDDefinition(grammar_text, rules, main_attribute="val")


def create_circular_sdd() -> SDDDefinition:
    """
    Crea una versión deliberadamente circular de la SDD para verificar el detector de ciclos.
    
    Modificación que induce el ciclo:
    En S -> L, en lugar de L.d = 0 (constante), hacemos que L.d dependa de S.val:
      L.d = S.val + 1
    Dado que S.val depende de L.val, y L.val depende de B.val y R.val,
    los cuales a su vez dependen de B.d y R.d (propagados desde L.d),
    se produce el ciclo directo:
      L.d -> L.val -> S.val -> L.d
    """
    base_sdd = create_project_sdd()
    circular_rules = dict(base_sdd.rules)

    # Reemplazamos las reglas de S -> L con una regla circular
    circular_rules["S -> L"] = [
        SemanticRule((1, "d"), [(0, "val")], lambda s_val: s_val + 1, "L.d = S.val + 1 (CIRCULAR)"),
        SemanticRule((0, "val"), [(1, "val")], lambda l_val: l_val, "S.val = L.val"),
        SemanticRule((0, "max_d"), [(1, "max_d")], lambda l_max: l_max, "S.max_d = L.max_d")
    ]

    return SDDDefinition(base_sdd.grammar_text, circular_rules, main_attribute="val")
