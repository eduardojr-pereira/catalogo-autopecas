# utilitário para import do projeto
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.processing.clustering.equivalence_engine import (
    build_graph,
    find_connected_components,
    generate_clusters,
)


# ------------------------------------------------------
# TESTE 1
# Construção do grafo
# ------------------------------------------------------
def test_build_graph():
    """
    Verifica se o grafo é construído corretamente
    a partir das equivalências.
    """

    equivalences = [
        ("A", "B"),
        ("B", "C"),
    ]

    graph = build_graph(equivalences)

    assert "A" in graph
    assert "B" in graph
    assert "C" in graph
    assert "B" in graph["A"]
    assert "A" in graph["B"]


# ------------------------------------------------------
# TESTE 2
# Componentes conectados
# ------------------------------------------------------
def test_find_connected_components():
    """
    Verifica se o algoritmo identifica corretamente
    os grupos conectados do grafo.
    """

    graph = {
        "A": {"B"},
        "B": {"A", "C"},
        "C": {"B"},
        "D": {"E"},
        "E": {"D"},
    }

    components = find_connected_components(graph)

    # converte para conjuntos imutáveis para facilitar comparação
    normalized = {frozenset(component) for component in components}

    assert frozenset({"A", "B", "C"}) in normalized
    assert frozenset({"D", "E"}) in normalized


# ------------------------------------------------------
# TESTE 3
# Geração de clusters
# ------------------------------------------------------
def test_generate_clusters():
    """
    Verifica se as equivalências são transformadas
    em clusters corretamente.
    """

    equivalences = [
        ("BOSCH_1", "MAHLE_1"),
        ("MAHLE_1", "FRAM_1"),
        ("NGK_1", "DENSO_1"),
    ]

    clusters = generate_clusters(equivalences)

    normalized = {frozenset(cluster) for cluster in clusters}

    assert frozenset({"BOSCH_1", "MAHLE_1", "FRAM_1"}) in normalized
    assert frozenset({"NGK_1", "DENSO_1"}) in normalized
