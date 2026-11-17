"""
Módulo de Definición y Procesamiento de Gramáticas Libres de Contexto (CFG).

Este módulo modela gramáticas libres de contexto según las convenciones
especificadas en el documento LF_project_2026_2.pdf y Aho et al. (Dragón Book, Sec. 4.4 - 4.6):
- El símbolo inicial siempre es 'S'.
- Los símbolos no terminales son letras mayúsculas ('A'-'Z').
- Los símbolos terminales son caracteres individuales (no mayúsculas, ni espacios, ni 'e', ni '$').
- La cadena vacía épsilon (ε) se representa exclusivamente por la letra 'e'.
- El marcador de fin de cadena es '$'.
"""

from typing import Dict, List, Set, Tuple


class Grammar:
    """
    Representa una Gramática Libre de Contexto (CFG).
    
    Atributos:
        nonterminals (List[str]): Lista ordenada de símbolos no terminales.
        terminals (List[str]): Lista ordenada en ASCII de símbolos terminales.
        productions (Dict[str, List[str]]): Mapeo de cada no terminal a su lista de alternativas.
        start_symbol (str): Símbolo inicial de la gramática (por defecto 'S').
    """

    def __init__(self, raw_rules: Dict[str, List[str]], start_symbol: str = "S"):
        self.start_symbol = start_symbol
        self.productions: Dict[str, List[str]] = dict(raw_rules)
        self.nonterminals: List[str] = list(self.productions.keys())
        
        # Recolectar todos los símbolos para determinar el conjunto de terminales
        all_symbols: Set[str] = set()
        for head, bodies in self.productions.items():
            for body in bodies:
                for char in body:
                    all_symbols.add(char)
        
        # Los terminales son todos los caracteres que no son no terminales, ni 'e' (épsilon), ni '$'
        terminal_set = (all_symbols - set(self.nonterminals)) - {"e", "$"}
        self.terminals: List[str] = sorted(list(terminal_set))

    @classmethod
    def from_text(cls, text: str) -> "Grammar":
        """
        Construye una instancia de Grammar a partir de una cadena con el formato especificado:
        Línea 1: n (número de no terminales)
        Líneas 2 a n+1: <no terminal> -> <alternativas separadas por espacio>
        """
        lines = [line.strip() for line in text.strip().splitlines() if line.strip()]
        if not lines:
            raise ValueError("El texto de la gramática está vacío.")
        
        num_nonterminals = int(lines[0])
        rules: Dict[str, List[str]] = {}
        
        for i in range(1, num_nonterminals + 1):
            if i >= len(lines):
                break
            line = lines[i]
            if "->" not in line:
                raise ValueError(f"Línea de producción inválida (falta '->'): {line}")
            head, body_part = line.split("->", 1)
            head = head.strip()
            alternatives = body_part.strip().split()
            rules[head] = alternatives
            
        return cls(rules, start_symbol="S")

    def is_nonterminal(self, symbol: str) -> bool:
        """Indica si un símbolo es no terminal."""
        return symbol in self.nonterminals

    def is_terminal(self, symbol: str) -> bool:
        """Indica si un símbolo es terminal."""
        return symbol in self.terminals

    def __str__(self) -> str:
        res = [f"Grammar with {len(self.nonterminals)} nonterminals (Start: {self.start_symbol}):"]
        for head, bodies in self.productions.items():
            res.append(f"  {head} -> {' '.join(bodies)}")
        return "\n".join(res)
