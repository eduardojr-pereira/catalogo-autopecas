"""
test_fitment_service.py

Testes de integração para o módulo fitment_service.

Este arquivo valida se o serviço de consulta de aplicações
(fitment) retorna corretamente as peças aplicáveis a:

- veículos
- motores
- filtros comerciais de busca

Ele utiliza a estrutura oficial de veículos:

vehicle_brands -> vehicle_models -> vehicles
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.catalog.fitment_service import (
    find_fitment_by_vehicle_filters,
    find_parts_by_motor_id,
    find_parts_by_vehicle_id,
)
from src.shared.utils import normalize_text


def norm_text(value: str) -> str:
    return normalize_text(value).upper()


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


def create_part_type(cursor, name="Filtro de Óleo"):
    cursor.execute("""
        INSERT INTO reference.part_types (
            name,
            normalized_name
        )
        VALUES (%s, %s)
        RETURNING id
    """, (name, norm_text(name)))

    return cursor.fetchone()["id"]


def create_part(cursor, part_type_id, name="Filtro de Óleo Motor R18", status="active"):
    cursor.execute("""
        INSERT INTO catalog.parts (
            name,
            normalized_name,
            part_type_id,
            status
        )
        VALUES (%s, %s, %s, %s)
        RETURNING id
    """, (
        name,
        norm_text(name),
        part_type_id,
        status,
    ))

    return cursor.fetchone()["id"]


def create_cluster(cursor, part_id, name="Cluster filtro óleo"):
    cursor.execute("""
        INSERT INTO catalog.clusters (
            name,
            cluster_type,
            part_id
        )
        VALUES (%s, %s, %s)
        RETURNING id
    """, (name, "consolidated", part_id))

    return cursor.fetchone()["id"]


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


def test_find_parts_by_vehicle_id(db_dict_cursor):
    cursor = db_dict_cursor

    brand_id = create_brand(cursor)
    model_id = create_model(cursor, brand_id)
    vehicle_id = create_vehicle(cursor, brand_id, model_id)

    motor_id = create_motor(cursor)
    create_vehicle_motor_link(cursor, vehicle_id, motor_id)

    part_type_id = create_part_type(cursor)
    part_id = create_part(cursor, part_type_id)
    cluster_id = create_cluster(cursor, part_id)

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
    cluster_id = create_cluster(cursor, part_id)

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
    cluster_id = create_cluster(cursor, part_id)

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