"""
test_search_service.py

Testes de integração para o módulo search_service.

Este arquivo valida:
- busca por código
- busca por nome da peça
- busca por tipo de peça
- busca por alias de tipo de peça
- busca de equivalentes por código

Os testes usam a estrutura atual do catálogo:

discovery.codes
catalog.clusters
catalog.cluster_codes
catalog.parts
reference.part_types
reference.part_type_aliases
reference.manufacturers
"""

import sys
from pathlib import Path

# permite importar módulos da pasta src
sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.catalog.search_service import (
    search_by_code,
    search_by_part_name,
    search_by_part_type,
    search_by_part_type_alias,
    search_equivalents_by_code,
)


# ------------------------------------------------------
# FUNÇÕES AUXILIARES DE CRIAÇÃO DE DADOS
# ------------------------------------------------------

def create_manufacturer(db_cursor, name="Bosch", manufacturer_type="aftermarket"):
    """
    Cria um fabricante de peça.
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


def create_part_type(db_cursor, name="Filtro de Óleo", normalized_name="FILTRO DE OLEO"):
    """
    Cria um tipo de peça.
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


def create_part_type_alias(db_cursor, part_type_id, alias="Filtro Óleo", normalized_alias="FILTRO OLEO"):
    """
    Cria um alias para um tipo de peça.
    """
    db_cursor.execute("""
        INSERT INTO reference.part_type_aliases (
            part_type_id,
            alias,
            normalized_alias
        )
        VALUES (%s, %s, %s)
    """, (part_type_id, alias, normalized_alias))


def create_part(
    db_cursor,
    part_type_id,
    name="Filtro de Óleo Motor R18",
    normalized_name="FILTRO DE OLEO MOTOR R18",
    status="active"
):
    """
    Cria uma peça consolidada.
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


def create_cluster(db_cursor, part_id, name="Cluster Filtro", cluster_type="consolidated"):
    """
    Cria um cluster vinculado a uma peça.
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


def create_code(db_cursor, manufacturer_id, code, normalized_code):
    """
    Cria um código de peça.
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
    Relaciona um código a um cluster.
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
    Verifica se a busca por código retorna:
    - código
    - fabricante
    - cluster
    - peça
    """
    manufacturer_id = create_manufacturer(
        db_cursor,
        name="Bosch Test",
        manufacturer_type="aftermarket"
    )

    part_type_id = create_part_type(db_cursor)
    part_id = create_part(db_cursor, part_type_id)
    cluster_id = create_cluster(db_cursor, part_id)

    code_id = create_code(
        db_cursor,
        manufacturer_id,
        code="OC-1196",
        normalized_code="OC1196"
    )

    link_code_to_cluster(db_cursor, cluster_id, code_id)

    results = search_by_code(db_cursor, "oc-1196")

    assert len(results) == 1
    assert results[0]["code_id"] == code_id
    assert results[0]["manufacturer_name"] == "Bosch Test"
    assert results[0]["cluster_id"] == cluster_id
    assert results[0]["part_id"] == part_id
    assert results[0]["part_name"] == "Filtro de Óleo Motor R18"


# ------------------------------------------------------
# TESTE 2
# Busca por nome da peça
# ------------------------------------------------------

def test_search_by_part_name(db_cursor):
    """
    Verifica se a busca por nome retorna a peça correta.
    """
    part_type_id = create_part_type(db_cursor)
    part_id = create_part(
        db_cursor,
        part_type_id,
        name="Filtro de Ar do Motor",
        normalized_name="FILTRO DE AR DO MOTOR"
    )

    results = search_by_part_name(db_cursor, "filtro de ar")

    assert len(results) == 1
    assert results[0]["part_id"] == part_id
    assert results[0]["part_name"] == "Filtro de Ar do Motor"


# ------------------------------------------------------
# TESTE 3
# Busca por tipo de peça
# ------------------------------------------------------

def test_search_by_part_type(db_cursor):
    """
    Verifica se a busca por tipo de peça retorna peças desse tipo.
    """
    part_type_id = create_part_type(
        db_cursor,
        name="Vela de Ignição",
        normalized_name="VELA DE IGNICAO"
    )

    part_id = create_part(
        db_cursor,
        part_type_id,
        name="Vela NGK Civic",
        normalized_name="VELA NGK CIVIC"
    )

    results = search_by_part_type(db_cursor, "vela de ignição")

    assert len(results) == 1
    assert results[0]["part_id"] == part_id
    assert results[0]["part_type_name"] == "Vela de Ignição"


# ------------------------------------------------------
# TESTE 4
# Busca por alias de tipo de peça
# ------------------------------------------------------

def test_search_by_part_type_alias(db_cursor):
    """
    Verifica se a busca por alias resolve o tipo de peça corretamente.
    """
    part_type_id = create_part_type(
        db_cursor,
        name="Pastilha de Freio",
        normalized_name="PASTILHA DE FREIO"
    )

    create_part_type_alias(
        db_cursor,
        part_type_id,
        alias="Pastilha",
        normalized_alias="PASTILHA"
    )

    part_id = create_part(
        db_cursor,
        part_type_id,
        name="Pastilha Dianteira Civic",
        normalized_name="PASTILHA DIANTEIRA CIVIC"
    )

    results = search_by_part_type_alias(db_cursor, "pastilha")

    assert len(results) == 1
    assert results[0]["part_id"] == part_id
    assert results[0]["part_type_name"] == "Pastilha de Freio"
    assert results[0]["alias"] == "Pastilha"


# ------------------------------------------------------
# TESTE 5
# Busca de equivalentes por código
# ------------------------------------------------------

def test_search_equivalents_by_code(db_cursor):
    """
    Verifica se a busca por equivalentes retorna
    códigos do mesmo cluster, exceto o código de origem.
    """
    manufacturer_id_1 = create_manufacturer(
        db_cursor,
        name="Bosch Eq Test",
        manufacturer_type="aftermarket"
    )

    manufacturer_id_2 = create_manufacturer(
        db_cursor,
        name="Mahle Eq Test",
        manufacturer_type="aftermarket"
    )

    part_type_id = create_part_type(db_cursor)
    part_id = create_part(db_cursor, part_type_id)
    cluster_id = create_cluster(db_cursor, part_id)

    source_code_id = create_code(
        db_cursor,
        manufacturer_id_1,
        code="0986-AF0051",
        normalized_code="0986AF0051"
    )

    equivalent_code_id = create_code(
        db_cursor,
        manufacturer_id_2,
        code="OC-1196",
        normalized_code="OC1196"
    )

    link_code_to_cluster(db_cursor, cluster_id, source_code_id)
    link_code_to_cluster(db_cursor, cluster_id, equivalent_code_id)

    results = search_equivalents_by_code(db_cursor, "0986-AF0051")

    assert len(results) == 1
    assert results[0]["source_code_id"] == source_code_id
    assert results[0]["equivalent_code_id"] == equivalent_code_id
    assert results[0]["manufacturer_name"] == "Mahle Eq Test"
    assert results[0]["cluster_id"] == cluster_id
    assert results[0]["part_id"] == part_id