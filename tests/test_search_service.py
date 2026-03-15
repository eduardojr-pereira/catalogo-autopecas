"""
test_search_service.py

Testes de integração dos serviços de busca.

Valida:
- busca por código
- busca por nome da peça
- busca por tipo de peça
- busca por alias de tipo de peça
- busca de equivalentes por código
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.catalog.search_service import (  # noqa: E402
    search_by_code,
    search_by_part_name,
    search_by_part_type,
    search_by_part_type_alias,
    search_equivalents_by_code,
)


# ------------------------------------------------------
# FUNÇÕES AUXILIARES
# ------------------------------------------------------
def insert_manufacturer(db_cursor, name, manufacturer_type="aftermarket"):
    """
    Insere fabricante e retorna o id.
    """
    db_cursor.execute("""
        INSERT INTO reference.manufacturers (
            name,
            manufacturer_type
        )
        VALUES (%s, %s)
        RETURNING id
    """, (name, manufacturer_type))

    return db_cursor.fetchone()[0]


def insert_part_type(db_cursor, name, normalized_name):
    """
    Insere tipo de peça e retorna o id.
    """
    db_cursor.execute("""
        INSERT INTO reference.part_types (
            name,
            normalized_name
        )
        VALUES (%s, %s)
        RETURNING id
    """, (name, normalized_name))

    return db_cursor.fetchone()[0]


def insert_part_type_alias(db_cursor, part_type_id, alias, normalized_alias):
    """
    Insere alias de tipo de peça.
    """
    db_cursor.execute("""
        INSERT INTO reference.part_type_aliases (
            part_type_id,
            alias,
            normalized_alias
        )
        VALUES (%s, %s, %s)
    """, (part_type_id, alias, normalized_alias))


def insert_part(db_cursor, name, normalized_name, part_type_id, status="active"):
    """
    Insere peça consolidada e retorna o id.
    """
    db_cursor.execute("""
        INSERT INTO catalog.parts (
            name,
            normalized_name,
            part_type_id,
            status
        )
        VALUES (%s, %s, %s, %s)
        RETURNING id
    """, (name, normalized_name, part_type_id, status))

    return db_cursor.fetchone()[0]


def insert_cluster(db_cursor, part_id, name="Cluster Teste", cluster_type="consolidated"):
    """
    Insere cluster e retorna o id.
    """
    db_cursor.execute("""
        INSERT INTO catalog.clusters (
            part_id,
            name,
            cluster_type
        )
        VALUES (%s, %s, %s)
        RETURNING id
    """, (part_id, name, cluster_type))

    return db_cursor.fetchone()[0]


def insert_code(db_cursor, manufacturer_id, code, normalized_code):
    """
    Insere código e retorna o id.
    """
    db_cursor.execute("""
        INSERT INTO discovery.codes (
            manufacturer_id,
            code,
            normalized_code
        )
        VALUES (%s, %s, %s)
        RETURNING id
    """, (manufacturer_id, code, normalized_code))

    return db_cursor.fetchone()[0]


def link_code_to_cluster(db_cursor, cluster_id, code_id):
    """
    Relaciona código ao cluster.
    """
    db_cursor.execute("""
        INSERT INTO catalog.cluster_codes (
            cluster_id,
            code_id
        )
        VALUES (%s, %s)
    """, (cluster_id, code_id))


# ------------------------------------------------------
# TESTE 1
# Busca por código
# ------------------------------------------------------
def test_search_by_code(db_cursor):
    """
    Verifica se a busca por código retorna fabricante e peça.
    """
    manufacturer_id = insert_manufacturer(db_cursor, "Bosch Test")
    part_type_id = insert_part_type(db_cursor, "Filtro de Óleo", "FILTRO DE OLEO")
    part_id = insert_part(
        db_cursor,
        "Filtro Bosch Honda",
        "FILTRO BOSCH HONDA",
        part_type_id
    )
    cluster_id = insert_cluster(db_cursor, part_id)

    code_id = insert_code(
        db_cursor,
        manufacturer_id,
        "OC-1196",
        "OC1196"
    )

    link_code_to_cluster(db_cursor, cluster_id, code_id)

    result = search_by_code(db_cursor, "oc-1196")

    assert len(result) == 1
    assert result[0]["manufacturer_name"] == "Bosch Test"
    assert result[0]["part_id"] == part_id
    assert result[0]["normalized_code"] == "OC1196"


# ------------------------------------------------------
# TESTE 2
# Busca por nome da peça
# ------------------------------------------------------
def test_search_by_part_name(db_cursor):
    """
    Verifica se a busca por nome retorna a peça correta.
    """
    part_type_id = insert_part_type(db_cursor, "Filtro de Ar", "FILTRO DE AR")

    part_id = insert_part(
        db_cursor,
        "Filtro de Ar Civic",
        "FILTRO DE AR CIVIC",
        part_type_id
    )

    result = search_by_part_name(db_cursor, "filtro de ar")

    assert len(result) == 1
    assert result[0]["part_id"] == part_id
    assert result[0]["part_name"] == "Filtro de Ar Civic"


# ------------------------------------------------------
# TESTE 3
# Busca por tipo de peça
# ------------------------------------------------------
def test_search_by_part_type(db_cursor):
    """
    Verifica se a busca por tipo de peça retorna itens daquele tipo.
    """
    part_type_id = insert_part_type(db_cursor, "Pastilha de Freio", "PASTILHA DE FREIO")

    insert_part(
        db_cursor,
        "Pastilha Dianteira Civic",
        "PASTILHA DIANTEIRA CIVIC",
        part_type_id
    )

    result = search_by_part_type(db_cursor, "pastilha de freio")

    assert len(result) == 1
    assert result[0]["part_type_name"] == "Pastilha de Freio"


# ------------------------------------------------------
# TESTE 4
# Busca por alias do tipo de peça
# ------------------------------------------------------
def test_search_by_part_type_alias(db_cursor):
    """
    Verifica se o alias resolve corretamente para as peças do tipo.
    """
    part_type_id = insert_part_type(db_cursor, "Vela de Ignição", "VELA DE IGNICAO")

    insert_part_type_alias(
        db_cursor,
        part_type_id,
        "Vela",
        "VELA"
    )

    part_id = insert_part(
        db_cursor,
        "Vela Honda Civic",
        "VELA HONDA CIVIC",
        part_type_id
    )

    result = search_by_part_type_alias(db_cursor, "vela")

    assert len(result) == 1
    assert result[0]["part_id"] == part_id
    assert result[0]["part_type_name"] == "Vela de Ignição"


# ------------------------------------------------------
# TESTE 5
# Busca de equivalentes por código
# ------------------------------------------------------
def test_search_equivalents_by_code(db_cursor):
    """
    Verifica se códigos do mesmo cluster são retornados como equivalentes.
    """
    bosch_id = insert_manufacturer(db_cursor, "Bosch Eq Test")
    mahle_id = insert_manufacturer(db_cursor, "Mahle Eq Test")

    part_type_id = insert_part_type(db_cursor, "Filtro de Óleo", "FILTRO DE OLEO")
    part_id = insert_part(
        db_cursor,
        "Filtro Equivalente",
        "FILTRO EQUIVALENTE",
        part_type_id
    )
    cluster_id = insert_cluster(db_cursor, part_id)

    source_code_id = insert_code(
        db_cursor,
        bosch_id,
        "0986-AF0051",
        "0986AF0051"
    )

    equivalent_code_id = insert_code(
        db_cursor,
        mahle_id,
        "OC-1196",
        "OC1196"
    )

    link_code_to_cluster(db_cursor, cluster_id, source_code_id)
    link_code_to_cluster(db_cursor, cluster_id, equivalent_code_id)

    result = search_equivalents_by_code(db_cursor, "0986-AF0051")

    assert len(result) == 1
    assert result[0]["equivalent_code_id"] == equivalent_code_id
    assert result[0]["manufacturer_name"] == "Mahle Eq Test"
    assert result[0]["part_id"] == part_id