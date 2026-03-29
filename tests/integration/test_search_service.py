"""
test_search_service.py

Testes de integração para o módulo search_service.
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.catalog.search_service import (
    search_by_code,
    search_by_part_name,
    search_by_part_type,
    search_by_part_type_alias,
    search_equivalents_by_code,
)
from src.processing.normalization.code_normalizer import normalize_code
from src.shared.utils import normalize_text


def norm_text(value: str) -> str:
    return normalize_text(value).upper()


def create_manufacturer(cursor, name="Bosch", manufacturer_type="aftermarket"):
    cursor.execute("""
        INSERT INTO reference.manufacturers (
            name,
            manufacturer_type
        )
        VALUES (%s, %s)
        RETURNING id
    """, (name, manufacturer_type))

    return cursor.fetchone()["id"]


def create_part_type(cursor, name="Filtro de Óleo", normalized_name=None):
    if normalized_name is None:
        normalized_name = norm_text(name)

    cursor.execute("""
        INSERT INTO reference.part_types (
            name,
            normalized_name
        )
        VALUES (%s, %s)
        RETURNING id
    """, (name, normalized_name))

    return cursor.fetchone()["id"]


def create_part_type_alias(cursor, part_type_id, alias="Filtro Óleo", normalized_alias=None):
    if normalized_alias is None:
        normalized_alias = norm_text(alias)

    cursor.execute("""
        INSERT INTO reference.part_type_aliases (
            part_type_id,
            alias,
            normalized_alias
        )
        VALUES (%s, %s, %s)
    """, (part_type_id, alias, normalized_alias))


def create_part(
    cursor,
    part_type_id,
    name="Filtro de Óleo Motor R18",
    normalized_name=None,
    status="active"
):
    if normalized_name is None:
        normalized_name = norm_text(name)

    cursor.execute("""
        INSERT INTO catalog.parts (
            name,
            normalized_name,
            part_type_id,
            status
        )
        VALUES (%s, %s, %s, %s)
        RETURNING id
    """, (name, normalized_name, part_type_id, status))

    return cursor.fetchone()["id"]


def create_cluster(cursor, part_id, name="Cluster Filtro", cluster_type="consolidated"):
    cursor.execute("""
        INSERT INTO catalog.clusters (
            part_id,
            name,
            cluster_type
        )
        VALUES (%s, %s, %s)
        RETURNING id
    """, (part_id, name, cluster_type))

    return cursor.fetchone()["id"]


def create_code(cursor, manufacturer_id, code, normalized_code=None):
    if normalized_code is None:
        normalized_code = normalize_code(code)

    cursor.execute("""
        INSERT INTO discovery.codes (
            manufacturer_id,
            code,
            normalized_code
        )
        VALUES (%s, %s, %s)
        RETURNING id
    """, (manufacturer_id, code, normalized_code))

    return cursor.fetchone()["id"]


def link_code_to_cluster(cursor, cluster_id, code_id):
    cursor.execute("""
        INSERT INTO catalog.cluster_codes (
            cluster_id,
            code_id
        )
        VALUES (%s, %s)
    """, (cluster_id, code_id))


def test_search_by_code(db_dict_cursor):
    cursor = db_dict_cursor

    manufacturer_id = create_manufacturer(cursor, "Bosch Test")
    part_type_id = create_part_type(cursor)
    part_id = create_part(cursor, part_type_id)
    cluster_id = create_cluster(cursor, part_id)

    code_id = create_code(cursor, manufacturer_id, "OC-1196")

    link_code_to_cluster(cursor, cluster_id, code_id)

    results = search_by_code(cursor, "oc-1196")

    assert len(results) == 1
    assert results[0]["code_id"] == code_id
    assert results[0]["manufacturer_name"] == "Bosch Test"
    assert results[0]["cluster_id"] == cluster_id
    assert results[0]["part_id"] == part_id


def test_search_by_part_name(db_dict_cursor):
    cursor = db_dict_cursor

    part_type_id = create_part_type(cursor)
    part_id = create_part(
        cursor,
        part_type_id,
        name="Filtro de Ar do Motor",
    )

    results = search_by_part_name(cursor, "filtro de ar")

    assert len(results) == 1
    assert results[0]["part_id"] == part_id


def test_search_by_part_type(db_dict_cursor):
    cursor = db_dict_cursor

    part_type_id = create_part_type(
        cursor,
        name="Vela de Ignição",
    )

    part_id = create_part(
        cursor,
        part_type_id,
        name="Vela NGK Civic",
    )

    results = search_by_part_type(cursor, "vela de ignição")

    assert len(results) == 1
    assert results[0]["part_id"] == part_id


def test_search_by_part_type_alias(db_dict_cursor):
    cursor = db_dict_cursor

    part_type_id = create_part_type(
        cursor,
        name="Pastilha de Freio",
    )

    create_part_type_alias(
        cursor,
        part_type_id,
        alias="Pastilha",
    )

    part_id = create_part(
        cursor,
        part_type_id,
        name="Pastilha Dianteira Civic",
    )

    results = search_by_part_type_alias(cursor, "pastilha")

    assert len(results) == 1
    assert results[0]["part_id"] == part_id


def test_search_equivalents_by_code(db_dict_cursor):
    cursor = db_dict_cursor

    manufacturer_id_1 = create_manufacturer(cursor, "Bosch Eq Test")
    manufacturer_id_2 = create_manufacturer(cursor, "Mahle Eq Test")

    part_type_id = create_part_type(cursor)
    part_id = create_part(cursor, part_type_id)
    cluster_id = create_cluster(cursor, part_id)

    source_code_id = create_code(cursor, manufacturer_id_1, "0986-AF0051")
    equivalent_code_id = create_code(cursor, manufacturer_id_2, "OC-1196")

    link_code_to_cluster(cursor, cluster_id, source_code_id)
    link_code_to_cluster(cursor, cluster_id, equivalent_code_id)

    results = search_equivalents_by_code(cursor, "0986-AF0051")

    assert len(results) == 1
    assert results[0]["source_code_id"] == source_code_id
    assert results[0]["equivalent_code_id"] == equivalent_code_id
    assert results[0]["manufacturer_name"] == "Mahle Eq Test"