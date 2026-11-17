"""
Módulo del Evaluador Genérico de SDD basado en Grafos de Dependencia.

Implementa los requisitos de la Sección 3 (Paso 5) de LF_project_2026_2.pdf y
las Secciones 5.1 y 5.2 de Aho et al. (Dragón Book):
1. El evaluador es completamente agnóstico a la SDD específica (la SDD se pasa como datos).
2. Construye el Grafo de Dependencias entre instancias de atributos de los nodos del árbol.
3. Detecta ciclos y reporta si la definición es circular (Paso 5.4).
4. Calcula el orden topológico y evalúa los atributos en dicho orden.
5. Emite los resultados requeridos: árbol anotado, orden de evaluación y valor principal.
"""

from typing import Dict, List, Tuple, Set, Any, Optional
from collections import defaultdict, deque
from src.parse_tree import ParseTreeNode
from src.sdd import SDDDefinition, SemanticRule


# Identificador único de instancia de atributo: (id_nodo, nombre_atributo)
AttrInstance = Tuple[int, str]


class SDDEvaluationError(Exception):
    """Excepción lanzada cuando ocurre un error durante la evaluación semántica."""
    pass


class SDDCircularDefinitionError(SDDEvaluationError):
    """Excepción lanzada cuando se detecta un ciclo en el grafo de dependencias."""
    def __init__(self, message: str, cycle_path: Optional[List[str]] = None):
        super().__init__(message)
        self.cycle_path = cycle_path or []


class SDDEvaluator:
    """
    Evaluador genérico de SDDs sobre árboles sintácticos.
    """

    def __init__(self, sdd: SDDDefinition):
        self.sdd = sdd

    def build_dependency_graph(
        self, root: ParseTreeNode
    ) -> Tuple[
        Dict[AttrInstance, Set[AttrInstance]],  # adyacencia: u -> {v} (u debe evaluarse antes que v)
        Dict[AttrInstance, int],                # in-degree de cada vértice
        Dict[AttrInstance, Tuple[Any, List[AttrInstance], ParseTreeNode, str]], # info de cómputo
        Dict[AttrInstance, str],                # etiquetas legibles para visualización
        Dict[int, ParseTreeNode]                # mapeo id_nodo -> ParseTreeNode
    ]:
        """
        Recorre el árbol sintáctico e instancia las reglas semánticas para construir el grafo de dependencias.
        """
        adj: Dict[AttrInstance, Set[AttrInstance]] = defaultdict(set)
        in_degree: Dict[AttrInstance, int] = defaultdict(int)
        compute_info: Dict[AttrInstance, Tuple[Any, List[AttrInstance], ParseTreeNode, str]] = {}
        labels: Dict[AttrInstance, str] = {}
        all_vertices: Set[AttrInstance] = set()
        nodes_by_id: Dict[int, ParseTreeNode] = {}

        # Recorrido recursivo para recopilar nodos y sus reglas
        def traverse(node: ParseTreeNode):
            nodes_by_id[node.node_id] = node

            # Registrar atributos preexistentes de hojas (ej. lexval)
            for attr_name in node.attributes.keys():
                v = (node.node_id, attr_name)
                all_vertices.add(v)
                labels[v] = f"{node.symbol}_{node.node_id}.{attr_name}"
                if v not in in_degree:
                    in_degree[v] = 0

            # Si el nodo es interno y tiene producción asociada
            if node.production:
                rules = self.sdd.get_rules_for_production(node.production)
                for rule in rules:
                    # Determinar nodo destino
                    target_idx, target_attr = rule.target
                    if target_idx == 0:
                        target_node = node
                    else:
                        target_node = node.children[target_idx - 1]

                    target_v = (target_node.node_id, target_attr)
                    all_vertices.add(target_v)
                    labels[target_v] = f"{target_node.symbol}_{target_node.node_id}.{target_attr}"
                    if target_v not in in_degree:
                        in_degree[target_v] = 0

                    dep_vertices: List[AttrInstance] = []
                    for dep_idx, dep_attr in rule.dependencies:
                        if dep_idx == 0:
                            dep_node = node
                        else:
                            dep_node = node.children[dep_idx - 1]
                        dep_v = (dep_node.node_id, dep_attr)
                        all_vertices.add(dep_v)
                        labels[dep_v] = f"{dep_node.symbol}_{dep_node.node_id}.{dep_attr}"
                        if dep_v not in in_degree:
                            in_degree[dep_v] = 0

                        dep_vertices.append(dep_v)
                        # Arista dirigida: dep_v -> target_v (dep_v se evalúa ANTES que target_v)
                        if target_v not in adj[dep_v]:
                            adj[dep_v].add(target_v)
                            in_degree[target_v] += 1

                    compute_info[target_v] = (rule.compute_fn, dep_vertices, target_node, target_attr)

            for child in node.children:
                traverse(child)

        traverse(root)
        for v in all_vertices:
            if v not in in_degree:
                in_degree[v] = 0

        return adj, in_degree, compute_info, labels, nodes_by_id

    def _find_cycle(self, all_vertices: Set[AttrInstance], adj: Dict[AttrInstance, Set[AttrInstance]]) -> List[AttrInstance]:
        """Encuentra un ciclo dirigido en el grafo usando DFS para reporte de depuración."""
        visited: Dict[AttrInstance, int] = {v: 0 for v in all_vertices}  # 0=no visitado, 1=en progreso, 2=completo
        parent: Dict[AttrInstance, AttrInstance] = {}
        cycle_found: List[AttrInstance] = []

        def dfs(u: AttrInstance):
            nonlocal cycle_found
            visited[u] = 1
            for v in adj.get(u, set()):
                if visited[v] == 1:
                    # Ciclo detectado: reconstruir camino
                    cur = u
                    cycle_found = [v, cur]
                    while cur != v and cur in parent:
                        cur = parent[cur]
                        cycle_found.append(cur)
                    cycle_found.reverse()
                    return True
                elif visited[v] == 0:
                    parent[v] = u
                    if dfs(v):
                        return True
            visited[u] = 2
            return False

        for node in all_vertices:
            if visited[node] == 0:
                if dfs(node):
                    break
        return cycle_found

    def evaluate(self, root: ParseTreeNode) -> Tuple[List[str], Any]:
        """
        Evalúa los atributos del árbol sintáctico en orden topológico.
        
        Retorna:
            (evaluation_order_labels, main_attribute_value)
            
        Lanza:
            SDDCircularDefinitionError si se detecta un ciclo.
        """
        adj, in_degree, compute_info, labels, nodes_by_id = self.build_dependency_graph(root)
        all_vertices = set(in_degree.keys())

        # Algoritmo de Kahn para ordenamiento topológico
        queue = deque([v for v in all_vertices if in_degree[v] == 0])
        topo_order: List[AttrInstance] = []

        while queue:
            u = queue.popleft()
            topo_order.append(u)

            # Ejecutar el cálculo del atributo
            if u in compute_info:
                compute_fn, dep_vertices, target_node, target_attr = compute_info[u]
                args = [nodes_by_id[d_node_id].get_attribute(d_attr) for d_node_id, d_attr in dep_vertices]
                # Verificar que todas las dependencias tengan valor
                try:
                    val = compute_fn(*args)
                except Exception as e:
                    raise SDDEvaluationError(f"Error evaluando regla para {labels[u]}: {e}")
                target_node.set_attribute(target_attr, val)

            for neighbor in adj.get(u, set()):
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        if len(topo_order) < len(all_vertices):
            # Existe al menos un ciclo dirigido
            cycle_nodes = self._find_cycle(all_vertices, adj)
            cycle_str = " -> ".join(labels.get(cn, str(cn)) for cn in cycle_nodes)
            raise SDDCircularDefinitionError(
                f"Error: La definición dirigida por la sintaxis (SDD) es CIRCULAR.\n"
                f"Ciclo detectado en las dependencias: {cycle_str}",
                cycle_path=[labels.get(cn, str(cn)) for cn in cycle_nodes]
            )

        order_labels = [labels[v] for v in topo_order]
        main_value = root.get_attribute(self.sdd.main_attribute)
        return order_labels, main_value
