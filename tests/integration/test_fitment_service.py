"""
test_fitment_service.py

Testes de integração dos serviços de fitment.

Valida:
- busca por veículo
- busca por motor
- busca por filtros comerciais de veículo
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.catalog.fitment_service import (  # noqa: E402
    find_parts_by_vehicle_id,
    find_parts_by_motor_id,
    find_fitment_by_vehicle_filters,
)


# ------------------------------------------------------
# FUNÇÕES AUXILIARES
# ------------------------------------------------------
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


def insert_cluster(db_cursor, name, part_id, cluster_type="consolidated"):
    """
    Insere cluster vinculado a uma peça e retorna o id.
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


def insert_motor(db_cursor, code, description):
    """
    Insere motor e retorna o id.
    """
    db_cursor.execute("""
        INSERT INTO reference.motors (
            code,
            description
        )
        VALUES (%s, %s)
        RETURNING id
    """, (code, description))

    return db_cursor.fetchone()[0]


def insert_vehicle(db_cursor, brand, model, model_year, version=None):
    """
    Insere veículo e retorna o id.
    """
    db_cursor.execute("""
        INSERT INTO reference.vehicles (
            brand,
            model,
            model_year,
            version
        )
        VALUES (%s, %s, %s, %s)
        RETURNING id
    """, (brand, model, model_year, version))

    return db_cursor.fetchone()[0]


def link_vehicle_motor(db_cursor, vehicle_id, motor_id):
    """
    Cria vínculo entre veículo e motor.
    """
    db_cursor.execute("""
        INSERT INTO reference.vehicle_motors (
            vehicle_id,
            motor_id
        )
        VALUES (%s, %s)
    """, (vehicle_id, motor_id))


def insert_application(
    db_cursor,
    cluster_id,
    motor_id=None,
    vehicle_id=None,
    confidence_score=0.900
):
    """
    Insere aplicação de cluster por motor e/ou veículo.
    """
    db_cursor.execute("""
        INSERT INTO catalog.applications (
            cluster_id,
            motor_id,
            vehicle_id,
            confidence_score
        )
        VALUES (%s, %s, %s, %s)
        RETURNING id
    """, (cluster_id, motor_id, vehicle_id, confidence_score))

    return db_cursor.fetchone()[0]


# ------------------------------------------------------
# TESTE 1
# Busca por veículo
# ------------------------------------------------------
def test_find_parts_by_vehicle_id(db_cursor):
    """
    Verifica se o serviço retorna a peça correta a partir do veículo.
    """
    part_type_id = insert_part_type(
        db_cursor,
        "Filtro de Óleo",
        "FILTRO DE OLEO"
    )

    part_id = insert_part(
        db_cursor,
        "Filtro de Óleo Honda R18",
        "FILTRO DE OLEO HONDA R18",
        part_type_id
    )

    cluster_id = insert_cluster(
        db_cursor,
        "Cluster Filtro Honda R18",
        part_id
    )

    motor_id = insert_motor(
        db_cursor,
        "R18A1",
        "Motor Honda R18"
    )

    vehicle_id = insert_vehicle(
        db_cursor,
        "Honda",
        "Civic",
        2010,
        "LXS"
    )

    link_vehicle_motor(db_cursor, vehicle_id, motor_id)

    insert_application(
        db_cursor,
        cluster_id,
        motor_id=motor_id,
        confidence_score=0.950
    )

    result = find_parts_by_vehicle_id(db_cursor, vehicle_id)

    assert len(result) == 1
    assert result[0]["vehicle_id"] == vehicle_id
    assert result[0]["part_id"] == part_id
    assert result[0]["part_type_name"] == "Filtro de Óleo"


# ------------------------------------------------------
# TESTE 2
# Busca por motor
# ------------------------------------------------------
def test_find_parts_by_motor_id(db_cursor):
    """
    Verifica se o serviço retorna a peça correta a partir do motor.
    """
    part_type_id = insert_part_type(
        db_cursor,
        "Vela de Ignição",
        "VELA DE IGNICAO"
    )

    part_id = insert_part(
        db_cursor,
        "Vela Honda R18",
        "VELA HONDA R18",
        part_type_id
    )

    cluster_id = insert_cluster(
        db_cursor,
        "Cluster Vela Honda R18",
        part_id
    )

    motor_id = insert_motor(
        db_cursor,
        "R18A1_TEST",
        "Motor Honda R18 Test"
    )

    insert_application(
        db_cursor,
        cluster_id,
        motor_id=motor_id,
        confidence_score=0.880
    )

    result = find_parts_by_motor_id(db_cursor, motor_id)

    assert len(result) == 1
    assert result[0]["motor_id"] == motor_id
    assert result[0]["part_id"] == part_id
    assert result[0]["part_name"] == "Vela Honda R18"


# ------------------------------------------------------
# TESTE 3
# Busca por filtros comerciais
# ------------------------------------------------------
def test_find_fitment_by_vehicle_filters(db_cursor):
    """
    Verifica se a busca comercial por marca, modelo e ano funciona.
    """
    part_type_id = insert_part_type(
        db_cursor,
        "Filtro de Ar",
        "FILTRO DE AR"
    )

    part_id = insert_part(
        db_cursor,
        "Filtro de Ar Civic",
        "FILTRO DE AR CIVIC",
        part_type_id
    )

    cluster_id = insert_cluster(
        db_cursor,
        "Cluster Filtro de Ar Civic",
        part_id
    )

    motor_id = insert_motor(
        db_cursor,
        "R18_FILTER_TEST",
        "Motor para filtro de ar"
    )

    vehicle_id = insert_vehicle(
        db_cursor,
        "Honda",
        "Civic",
        2011,
        "LXL"
    )

    link_vehicle_motor(db_cursor, vehicle_id, motor_id)

    insert_application(
        db_cursor,
        cluster_id,
        motor_id=motor_id,
        confidence_score=0.910
    )

    result = find_fitment_by_vehicle_filters(
        db_cursor,
        brand="Honda",
        model="Civic",
        model_year=2011,
        part_type_name="Filtro de Ar",
        version="LXL"
    )

    assert len(result) == 1
    assert result[0]["vehicle_id"] == vehicle_id
    assert result[0]["part_id"] == part_id
    assert result[0]["part_type_name"] == "Filtro de Ar"