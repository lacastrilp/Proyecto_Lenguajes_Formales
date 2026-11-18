"""
Módulo de Representación de Árboles Sintácticos Anotados (Annotated Parse Trees).

Define la estructura de nodo para árboles de derivación construidos tanto
por parsers LL(1) como SLR(1), permitiendo asociar atributos semánticos
y visualizarlos de acuerdo con las especificaciones del proyecto.
"""

from typing import List, Dict, Any, Optional


class ParseTreeNode:
    """
    Nodo de un Árbol Sintáctico Anotado.
    
    Atributos:
        symbol (str): Símbolo gramatical (terminal o no terminal).
        production (Optional[str]): Cadena de la producción utilizada si es no terminal (ej. "L -> BR").
        children (List[ParseTreeNode]): Lista de nodos hijos en orden de izquierda a derecha.
        attributes (Dict[str, Any]): Diccionario de atributos semánticos asociados (ej. {'val': 5, 'd': 1}).
        node_id (int): Identificador numérico único del nodo para el grafo de dependencias.
    """
    _id_counter: int = 0

    def __init__(self, symbol: str, production: Optional[str] = None, children: Optional[List["ParseTreeNode"]] = None):
        ParseTreeNode._id_counter += 1
        self.node_id: int = ParseTreeNode._id_counter
        self.symbol: str = symbol
        self.production: Optional[str] = production
        self.children: List["ParseTreeNode"] = children if children is not None else []
        self.attributes: Dict[str, Any] = {}

    @classmethod
    def reset_counter(cls) -> None:
        """Reinicia el contador global de IDs de nodos."""
        cls._id_counter = 0

    def is_leaf(self) -> bool:
        """Indica si el nodo es una hoja (terminal o epsilon)."""
        return len(self.children) == 0

    def add_child(self, child: "ParseTreeNode") -> None:
        """Añade un nodo hijo a la lista."""
        self.children.append(child)

    def set_attribute(self, attr_name: str, value: Any) -> None:
        """Asigna un valor a un atributo semántico en este nodo."""
        self.attributes[attr_name] = value

    def get_attribute(self, attr_name: str) -> Any:
        """Obtiene el valor de un atributo semántico."""
        return self.attributes.get(attr_name)

    def format_tree(self, depth: int = 0, indent_str: str = "  ") -> List[str]:
        """
        Retorna la representación textual del árbol sintáctico anotado:
        un nodo por línea, indentado por profundidad, con sus atributos.
        Formato:
          S {val=3, max_d=1}
            L {val=3, d=0, max_d=1}
              ...
        """
        indent = indent_str * depth
        if self.attributes:
            attrs_str = ", ".join(f"{k}={v}" for k, v in sorted(self.attributes.items()))
            line = f"{indent}{self.symbol} {{{attrs_str}}}"
        else:
            line = f"{indent}{self.symbol}"
        
        lines = [line]
        for child in self.children:
            lines.extend(child.format_tree(depth + 1, indent_str))
        return lines

    def print_annotated(self, depth: int = 0) -> None:
        """Imprime directamente el árbol sintáctico anotado por consola."""
        for line in self.format_tree(depth):
            print(line)

    def __repr__(self) -> str:
        attrs = ", ".join(f"{k}={v}" for k, v in self.attributes.items())
        return f"Node({self.node_id}: {self.symbol} [{attrs}])"
