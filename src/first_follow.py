"""
Módulo de Cálculo de Conjuntos FIRST y FOLLOW.

Implementa los algoritmos descritos en la Sección 4.4.2 del libro
'Compilers: Principles, Techniques, and Tools' (Aho et al., 2da Edición).

Soporta de manera rigurosa y correcta gramáticas con producciones épsilon (e).
"""

from typing import Dict, Set, List
from src.grammar import Grammar


def compute_first(grammar: Grammar) -> Dict[str, Set[str]]:
    """
    Calcula el conjunto FIRST(X) para cada símbolo de la gramática X in (V_N U V_T U {'e'}).
    
    Reglas (Sección 4.4.2):
    1. Si X es terminal, FIRST(X) = {X}.
    2. Si existe la producción X -> e, entonces e in FIRST(X).
    3. Si X es no terminal y X -> Y_1 Y_2 ... Y_k es una producción:
       Para i de 1 a k:
         Añadir FIRST(Y_i) - {e} a FIRST(X).
         Si e no pertenece a FIRST(Y_i), romper el ciclo.
       Si todos los Y_i derivan e (o k == 0), añadir e a FIRST(X).
       
    Se itera hasta alcanzar un punto fijo.
    """
    first: Dict[str, Set[str]] = {}

    # 1. Caso base: terminales y épsilon
    for t in grammar.terminals:
        first[t] = {t}
    first["e"] = {"e"}

    for nt in grammar.nonterminals:
        first[nt] = set()

    # 2. Iteración hasta punto fijo
    changed = True
    while changed:
        changed = False
        for head in grammar.nonterminals:
            for alt in grammar.productions.get(head, []):
                if alt == "e":
                    if "e" not in first[head]:
                        first[head].add("e")
                        changed = True
                else:
                    all_nullable = True
                    for char in alt:
                        char_first = first.get(char, {char})
                        # Añadir todos los no-épsilon
                        for s in char_first:
                            if s != "e" and s not in first[head]:
                                first[head].add(s)
                                changed = True
                        if "e" not in char_first:
                            all_nullable = False
                            break
                    if all_nullable:
                        if "e" not in first[head]:
                            first[head].add("e")
                            changed = True

    return first


def first_of_string(first_sets: Dict[str, Set[str]], alpha: str) -> Set[str]:
    """
    Extiende FIRST a una cadena arbitraria de símbolos alpha = X_1 X_2 ... X_k.
    
    Reglas (Sección 4.4.2):
    - Si alpha es vacía o 'e', retorna {'e'}.
    - Añade FIRST(X_1) - {e}.
    - Si e in FIRST(X_1), añade FIRST(X_2) - {e}, y así sucesivamente.
    - Si para todo i, e in FIRST(X_i), entonces añade 'e'.
    """
    if not alpha or alpha == "e":
        return {"e"}

    result: Set[str] = set()
    all_nullable = True

    for char in alpha:
        char_first = first_sets.get(char, {char})
        result |= (char_first - {"e"})
        if "e" not in char_first:
            all_nullable = False
            break

    if all_nullable:
        result.add("e")

    return result


def compute_follow(grammar: Grammar, first_sets: Dict[str, Set[str]]) -> Dict[str, Set[str]]:
    """
    Calcula el conjunto FOLLOW(A) para todo símbolo no terminal A in V_N.
    
    Reglas (Sección 4.4.2):
    1. Añadir '$' a FOLLOW(S), donde S es el símbolo inicial.
    2. Si existe una producción A -> alpha B beta, entonces todo lo perteneciente
       a FIRST(beta) excepto 'e' se añade a FOLLOW(B).
    3. Si existe una producción A -> alpha B, o A -> alpha B beta donde e in FIRST(beta),
       entonces todo lo perteneciente a FOLLOW(A) se añade a FOLLOW(B).
       
    Se itera hasta alcanzar un punto fijo.
    """
    follow: Dict[str, Set[str]] = {nt: set() for nt in grammar.nonterminals}
    follow[grammar.start_symbol].add("$")

    changed = True
    while changed:
        changed = False
        for head, bodies in grammar.productions.items():
            for body in bodies:
                if body == "e":
                    continue
                k = len(body)
                for i in range(k):
                    symbol = body[i]
                    if grammar.is_nonterminal(symbol):
                        beta = body[i + 1:]
                        beta_first = first_of_string(first_sets, beta)
                        
                        # Regla 2: FIRST(beta) - {e} en FOLLOW(symbol)
                        for s in (beta_first - {"e"}):
                            if s not in follow[symbol]:
                                follow[symbol].add(s)
                                changed = True
                        
                        # Regla 3: Si beta =>* e, FOLLOW(head) en FOLLOW(symbol)
                        if "e" in beta_first:
                            for s in follow[head]:
                                if s not in follow[symbol]:
                                    follow[symbol].add(s)
                                    changed = True

    return follow


def format_set_elements(s: Set[str]) -> str:
    """
    Formatea los elementos de un conjunto entre llaves { ... }:
    Escribe los terminales en orden ASCII, seguido de 'e' (si pertenece),
    y luego por '$' (si pertenece), separados por coma y espacio.
    """
    regular_terms = sorted([x for x in s if x not in ("e", "$")])
    elements = list(regular_terms)
    if "e" in s:
        elements.append("e")
    if "$" in s:
        elements.append("$")
    return "{" + ", ".join(elements) + "}"


def format_sets_output(grammar: Grammar, first_sets: Dict[str, Set[str]], follow_sets: Dict[str, Set[str]]) -> str:
    """
    Genera la salida requerida por el parámetro CLI '--sets':
    Imprime una línea por cada no terminal (en orden alfabético) para cada uno
    de los dos conjuntos (primero todos los FIRST, luego todos los FOLLOW),
    en el formato:
      First(A) = {a, d}
      Follow(A) = {b, $}
    """
    lines: List[str] = []
    sorted_nts = sorted(grammar.nonterminals)

    for nt in sorted_nts:
        lines.append(f"First({nt}) = {format_set_elements(first_sets[nt])}")

    for nt in sorted_nts:
        lines.append(f"Follow({nt}) = {format_set_elements(follow_sets[nt])}")

    return "\n".join(lines)
