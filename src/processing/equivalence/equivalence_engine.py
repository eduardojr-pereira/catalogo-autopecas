"""
equivalence_engine.py

Responsável por transformar relações de equivalência
em grupos conectados de códigos.

Cada grupo conectado representa um cluster potencial.

Responsabilidades:
- montar grafo de equivalências
- identificar componentes conectados
- retornar clusters determinísticos

Este módulo NÃO deve:
- acessar banco de dados
- conter lógica de persistência
"""

from typing import Dict, List, Set, Tuple


def build_graph(equivalences: List[Tuple[int, int]]) -> Dict[int, Set[int]]:
    """
    Constrói um grafo simples a partir de uma lista de equivalências.
    """
    graph: Dict[int, Set[int]] = {}

    for code_a, code_b in equivalences:
        graph.setdefault(code_a, set()).add(code_b)
        graph.setdefault(code_b, set()).add(code_a)

    return graph


def find_connected_components(graph: Dict[int, Set[int]]) -> List[Set[int]]:
    """
    Encontra grupos conectados dentro do grafo.
    """
    visited: Set[int] = set()
    components: List[Set[int]] = []

    for node in sorted(graph.keys()):  # 🔒 determinismo
        if node in visited:
            continue

        stack = [node]
        component: Set[int] = set()

        while stack:
            current = stack.pop()

            if current in visited:
                continue

            visited.add(current)
            component.add(current)

            # 🔒 determinismo também nos vizinhos
            for neighbor in sorted(graph[current]):
                if neighbor not in visited:
                    stack.append(neighbor)

        components.append(component)

    return components


def generate_clusters(equivalences: List[Tuple[int, int]]) -> List[Set[int]]:
    """
    Gera clusters a partir de uma lista de equivalências.
    """
    if not equivalences:
        return []

    graph = build_graph(equivalences)
    clusters = find_connected_components(graph)

    # 🔒 ordena clusters por menor id para consistência global
    clusters.sort(key=lambda cluster: min(cluster))

    return clusters