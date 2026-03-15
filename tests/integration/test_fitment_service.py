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

# permite importar módulos da pasta src
sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.catalog.fitment_service import (
    find_parts_by_vehicle_id,
    find_parts_by_motor_id,
    find_fitment_by_vehicle_filters
)


# ------------------------------------------------------
# FUNÇÕES AUXILIARES DE CRIAÇÃO DE DADOS
# ------------------------------------------------------

def create_brand(db_cursor, name="Honda"):
    """
    Cria uma marca de veículo.
    """
    db_cursor.execute("""
        INSERT INTO reference.vehicle_brands (
            name,
            normalized_name
        )
        VALUES (%s, %s)
        RETURNING id
    """, (name, name.upper()))

    return db_cursor.fetchone()[0]


def create_model(db_cursor, brand_id, name="Civic"):
    """
    Cria um modelo vinculado à marca.
    """
    db_cursor.execute("""
        INSERT INTO reference.vehicle_models (
            brand_id,
            name,
            normalized_name
        )
        VALUES (%s, %s, %s)
        RETURNING id
    """, (brand_id, name, name.upper()))

    return db_cursor.fetchone()[0]


def create_vehicle(db_cursor, model_id, year=2010):
    """
    Cria um veículo.
    """
    db_cursor.execute("""
        INSERT INTO reference.vehicles (
            model_id,
            model_year,
            brand_text,
            model_text
        )
        VALUES (%s, %s, %s, %s)
        RETURNING id
    """, (model_id, year, "Honda", "Civic"))

    return db_cursor.fetchone()[0]


def create_motor(db_cursor):
    """
    Cria um motor simples.
    """
    db_cursor.execute("""
        INSERT INTO reference.motors (
            code,
            description,
            displacement
        )
        VALUES (%s, %s, %s)
        RETURNING id
    """, ("R18_TEST", "Motor Honda R18", 1.8))

    return db_cursor.fetchone()[0]


def create_vehicle_motor_link(db_cursor, vehicle_id, motor_id):
    """
    Relaciona veículo e motor.
    """
    db_cursor.execute("""
        INSERT INTO reference.vehicle_motors (
            vehicle_id,
            motor_id
        )
        VALUES (%s, %s)
    """, (vehicle_id, motor_id))


def create_part_type(db_cursor):
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
    """, ("Filtro de Óleo", "FILTRO DE OLEO"))

    return db_cursor.fetchone()[0]


def create_part(db_cursor, part_type_id):
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
    """, (
        "Filtro de Óleo Motor R18",
        "FILTRO DE OLEO MOTOR R18",
        part_type_id,
        "active"
    ))

    return db_cursor.fetchone()[0]


def create_cluster(db_cursor, part_id):
    """
    Cria cluster consolidado vinculado à peça.
    """
    db_cursor.execute("""
        INSERT INTO catalog.clusters (
            name,
            cluster_type,
            part_id
        )
        VALUES (%s, %s, %s)
        RETURNING id
    """, ("Cluster filtro óleo", "consolidated", part_id))

    return db_cursor.fetchone()[0]


def create_application_motor(db_cursor, cluster_id, motor_id):
    """
    Cria aplicação vinculada ao motor.
    """
    db_cursor.execute("""
        INSERT INTO catalog.applications (
            cluster_id,
            motor_id,
            confidence_score
        )
        VALUES (%s, %s, %s)
    """, (cluster_id, motor_id, 0.95))


def create_application_vehicle(db_cursor, cluster_id, vehicle_id):
    """
    Cria aplicação vinculada diretamente ao veículo.
    """
    db_cursor.execute("""
        INSERT INTO catalog.applications (
            cluster_id,
            vehicle_id,
            confidence_score
        )
        VALUES (%s, %s, %s)
    """, (cluster_id, vehicle_id, 0.95))


# ------------------------------------------------------
# TESTE 1
# Busca por vehicle_id
# ------------------------------------------------------

def test_find_parts_by_vehicle_id(db_cursor):

    brand_id = create_brand(db_cursor)
    model_id = create_model(db_cursor, brand_id)
    vehicle_id = create_vehicle(db_cursor, model_id)

    motor_id = create_motor(db_cursor)
    create_vehicle_motor_link(db_cursor, vehicle_id, motor_id)

    part_type_id = create_part_type(db_cursor)
    part_id = create_part(db_cursor, part_type_id)

    cluster_id = create_cluster(db_cursor, part_id)

    create_application_motor(db_cursor, cluster_id, motor_id)

    results = find_parts_by_vehicle_id(db_cursor, vehicle_id)

    assert len(results) > 0
    assert results[0]["part_name"] == "Filtro de Óleo Motor R18"


# ------------------------------------------------------
# TESTE 2
# Busca por motor_id
# ------------------------------------------------------

def test_find_parts_by_motor_id(db_cursor):

    motor_id = create_motor(db_cursor)

    part_type_id = create_part_type(db_cursor)
    part_id = create_part(db_cursor, part_type_id)

    cluster_id = create_cluster(db_cursor, part_id)

    create_application_motor(db_cursor, cluster_id, motor_id)

    results = find_parts_by_motor_id(db_cursor, motor_id)

    assert len(results) > 0
    assert results[0]["part_name"] == "Filtro de Óleo Motor R18"


# ------------------------------------------------------
# TESTE 3
# Busca por filtros comerciais
# ------------------------------------------------------

def test_find_fitment_by_vehicle_filters(db_cursor):

    brand_id = create_brand(db_cursor)
    model_id = create_model(db_cursor, brand_id)
    vehicle_id = create_vehicle(db_cursor, model_id)

    motor_id = create_motor(db_cursor)

    create_vehicle_motor_link(db_cursor, vehicle_id, motor_id)

    part_type_id = create_part_type(db_cursor)
    part_id = create_part(db_cursor, part_type_id)

    cluster_id = create_cluster(db_cursor, part_id)

    create_application_motor(db_cursor, cluster_id, motor_id)

    results = find_fitment_by_vehicle_filters(
        db_cursor,
        brand="Honda",
        model="Civic",
        model_year=2010
    )

    assert len(results) > 0
    assert results[0]["part_name"] == "Filtro de Óleo Motor R18"