"""
test_query_service.py

Testes de integração para o módulo query_service.

Este arquivo consolida os testes antes separados entre:

- search_service
- fitment_service

O objetivo é validar a camada oficial de consultas do catálogo,
incluindo:

- busca por código;
- busca por nome de peça;
- busca por tipo de peça;
- busca por alias de tipo de peça;
- busca de equivalentes por código;
- busca de peças por veículo;
- busca de peças por motor;
- busca de fitment por filtros comerciais.
"""

from src.catalog.query_service import (
    find_fitment_by_vehicle_filters,
    find_parts_by_motor_id,
    find_parts_by_vehicle_id,
    search_by_code,
    search_by_part_name,
    search_by_part_type,
    search_by_part_type_alias,
    search_equivalents_by_code,
)
from src.processing.normalization.code_normalizer import normalize_code
from src.shared.utils import normalize_text


def norm_text(value: str) -> str:
    """
    Normaliza texto para persistência de dados de teste.
    """
    return normalize_text(value).upper()


# ======================================================
# HELPERS DE DADOS
# ======================================================

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


def create_brand(cursor, name="Honda", external_source="test", external_code="brand-honda"):
    cursor.execute("""
        INSERT INTO reference.vehicle_brands (
            name,
            normalized_name,
            external_source,
            external_code
        )
        VALUES (%s, %s, %s, %s)
        RETURNING id
    """, (name, norm_text(name), external_source, external_code))

    return cursor.fetchone()["id"]


def create_model(
    cursor,
    brand_id,
    name="Civic",
    external_source="test",
    external_code="model-civic",
):
    cursor.execute("""
        INSERT INTO reference.vehicle_models (
            brand_id,
            name,
            normalized_name,
            external_source,
            external_code
        )
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id
    """, (brand_id, name, norm_text(name), external_source, external_code))

    return cursor.fetchone()["id"]


def create_vehicle(
    cursor,
    brand_id,
    model_id,
    year=2010,
    version_name="LXS 1.8",
    market="BR",
    external_source="test",
    external_code="vehicle-civic-2010-lxs",
):
    cursor.execute("""
        INSERT INTO reference.vehicles (
            brand_id,
            model_id,
            brand_text,
            model_text,
            model_year,
            version_name,
            market,
            external_source,
            external_code
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
    """, (
        brand_id,
        model_id,
        "Honda",
        "Civic",
        year,
        version_name,
        market,
        external_source,
        external_code,
    ))

    return cursor.fetchone()["id"]


def create_motor(cursor, code="R18_TEST"):
    cursor.execute("""
        INSERT INTO reference.motors (
            code,
            description,
            displacement
        )
        VALUES (%s, %s, %s)
        RETURNING id
    """, (code, "Motor Honda R18", 1.8))

    return cursor.fetchone()["id"]


def create_vehicle_motor_link(cursor, vehicle_id, motor_id):
    cursor.execute("""
        INSERT INTO reference.vehicle_motors (
            vehicle_id,
            motor_id
        )
        VALUES (%s, %s)
    """, (vehicle_id, motor_id))


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
    status="active",
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


def create_application_motor(cursor, cluster_id, motor_id):
    cursor.execute("""
        INSERT INTO catalog.applications (
            cluster_id,
            motor_id,
            confidence_score
        )
        VALUES (%s, %s, %s)
        RETURNING id
    """, (cluster_id, motor_id, 0.95))

    return cursor.fetchone()["id"]


def create_application_vehicle(cursor, cluster_id, vehicle_id):
    cursor.execute("""
        INSERT INTO catalog.applications (
            cluster_id,
            vehicle_id,
            confidence_score
        )
        VALUES (%s, %s, %s)
        RETURNING id
    """, (cluster_id, vehicle_id, 0.95))

    return cursor.fetchone()["id"]


# ======================================================
# TESTES DE BUSCA
# ======================================================

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


# ======================================================
# TESTES DE FITMENT
# ======================================================

def test_find_parts_by_vehicle_id(db_dict_cursor):
    cursor = db_dict_cursor

    brand_id = create_brand(cursor)
    model_id = create_model(cursor, brand_id)
    vehicle_id = create_vehicle(cursor, brand_id, model_id)

    motor_id = create_motor(cursor)
    create_vehicle_motor_link(cursor, vehicle_id, motor_id)

    part_type_id = create_part_type(cursor)
    part_id = create_part(cursor, part_type_id)
    cluster_id = create_cluster(cursor, part_id, name="Cluster filtro óleo")

    create_application_motor(cursor, cluster_id, motor_id)

    results = find_parts_by_vehicle_id(cursor, vehicle_id)

    assert len(results) > 0
    assert results[0]["vehicle_id"] == vehicle_id
    assert results[0]["part_id"] == part_id
    assert results[0]["part_name"] == "Filtro de Óleo Motor R18"


def test_find_parts_by_motor_id(db_dict_cursor):
    cursor = db_dict_cursor

    motor_id = create_motor(cursor)

    part_type_id = create_part_type(cursor)
    part_id = create_part(cursor, part_type_id)
    cluster_id = create_cluster(cursor, part_id, name="Cluster filtro óleo")

    create_application_motor(cursor, cluster_id, motor_id)

    results = find_parts_by_motor_id(cursor, motor_id)

    assert len(results) > 0
    assert results[0]["motor_id"] == motor_id
    assert results[0]["part_id"] == part_id
    assert results[0]["part_name"] == "Filtro de Óleo Motor R18"


def test_find_fitment_by_vehicle_filters(db_dict_cursor):
    cursor = db_dict_cursor

    brand_id = create_brand(cursor, name="Honda", external_code="brand-honda-fitment")
    model_id = create_model(
        cursor,
        brand_id,
        name="Civic",
        external_code="model-civic-fitment",
    )
    vehicle_id = create_vehicle(
        cursor,
        brand_id,
        model_id,
        year=2010,
        version_name="LXS 1.8",
        external_code="vehicle-civic-2010-lxs-fitment",
    )

    motor_id = create_motor(cursor, code="R18_TEST_FITMENT")
    create_vehicle_motor_link(cursor, vehicle_id, motor_id)

    part_type_id = create_part_type(cursor, name="Filtro de Óleo")
    part_id = create_part(cursor, part_type_id)
    cluster_id = create_cluster(cursor, part_id, name="Cluster filtro óleo")

    create_application_motor(cursor, cluster_id, motor_id)

    results = find_fitment_by_vehicle_filters(
        cursor,
        brand="Honda",
        model="Civic",
        model_year=2010,
        part_type_name="Filtro de Óleo",
        version="LXS 1.8",
    )

    assert len(results) > 0
    assert results[0]["vehicle_id"] == vehicle_id
    assert results[0]["part_id"] == part_id
    assert results[0]["part_name"] == "Filtro de Óleo Motor R18"