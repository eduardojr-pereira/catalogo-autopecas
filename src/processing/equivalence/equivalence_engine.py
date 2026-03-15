"""
equivalence_engine.py

Responsável por transformar relações de equivalência
em grupos conectados de códigos.

Cada grupo conectado representa um cluster potencial.
"""


def build_graph(equivalences):
    """
    Constrói um grafo simples a partir de uma lista de equivalências.

    Parâmetro
    ---------
    equivalences : list[tuple]
        Lista de pares (code_a, code_b)

    Retorno
    -------
    dict
        Dicionário onde cada código aponta para seus vizinhos.
    """

    graph = {}

    for code_a, code_b in equivalences:
        # garante que o nó exista no grafo
        if code_a not in graph:
            graph[code_a] = set()

        if code_b not in graph:
            graph[code_b] = set()

        # cria ligação nos dois sentidos
        graph[code_a].add(code_b)
        graph[code_b].add(code_a)

    return graph


def find_connected_components(graph):
    """
    Encontra grupos conectados dentro do grafo.

    Cada grupo conectado representa um cluster de equivalência.

    Parâmetro
    ---------
    graph : dict
        Grafo montado pela função build_graph

    Retorno
    -------
    list[set]
        Lista de conjuntos, onde cada conjunto é um cluster
    """

    visited = set()
    components = []

    for node in graph:
        if node in visited:
            continue

        # inicia busca em profundidade
        stack = [node]
        component = set()

        while stack:
            current = stack.pop()

            if current in visited:
                continue

            visited.add(current)
            component.add(current)

            for neighbor in graph[current]:
                if neighbor not in visited:
                    stack.append(neighbor)

        components.append(component)

    return components


def generate_clusters(equivalences):
    """
    Gera clusters a partir de uma lista de equivalências.

    Etapas:
    1. monta o grafo
    2. encontra componentes conectados
    3. retorna os clusters
    """

    graph = build_graph(equivalences)
    clusters = find_connected_components(graph)

    return clusters