"""
test_equivalence_engine.py

Testes unitários do motor de equivalência.

Valida:
- construção do grafo
- identificação de componentes conectados
- geração de clusters determinísticos
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.processing.equivalence.equivalence_engine import (  # noqa: E402
    build_graph,
    find_connected_components,
    generate_clusters,
)


# ------------------------------------------------------
# TESTE 1
# Construção do grafo
# ------------------------------------------------------
def test_build_graph():
    equivalences = [
        (1, 2),
        (2, 3),
    ]

    graph = build_graph(equivalences)

    assert 1 in graph
    assert 2 in graph
    assert 3 in graph
    assert 2 in graph[1]
    assert 1 in graph[2]


# ------------------------------------------------------
# TESTE 2
# Componentes conectados
# ------------------------------------------------------
def test_find_connected_components():
    graph = {
        1: {2},
        2: {1, 3},
        3: {2},
        4: {5},
        5: {4},
    }

    components = find_connected_components(graph)

    normalized = {frozenset(component) for component in components}

    assert frozenset({1, 2, 3}) in normalized
    assert frozenset({4, 5}) in normalized


# ------------------------------------------------------
# TESTE 3
# Geração de clusters
# ------------------------------------------------------
def test_generate_clusters():
    equivalences = [
        (1, 2),
        (2, 3),
        (4, 5),
    ]

    clusters = generate_clusters(equivalences)

    normalized = [set(cluster) for cluster in clusters]

    assert {1, 2, 3} in normalized
    assert {4, 5} in normalized


# ------------------------------------------------------
# TESTE 4
# Determinismo dos clusters
# ------------------------------------------------------
def test_generate_clusters_deterministic_order():
    equivalences = [
        (10, 11),
        (1, 2),
        (2, 3),
    ]

    clusters = generate_clusters(equivalences)

    # ordenado pelo menor id do cluster
    assert clusters[0] == {1, 2, 3}
    assert clusters[1] == {10, 11}


# ------------------------------------------------------
# TESTE 5
# Lista vazia
# ------------------------------------------------------
def test_generate_clusters_empty():
    clusters = generate_clusters([])

    assert clusters == []