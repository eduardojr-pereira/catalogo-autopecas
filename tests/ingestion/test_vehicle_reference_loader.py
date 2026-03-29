"""
test_vehicle_reference_loader.py

Testes do loader de referências de veículos.

Agora com isolamento explícito por teste, independente do conftest.
"""

from __future__ import annotations

import pytest

from src.ingestion.loaders.vehicle_reference_loader import (
    DependencyNotFoundError,
    LoadAllResult,
    VehicleReferenceLoader,
)


# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def loader(db_connection) -> VehicleReferenceLoader:
    return VehicleReferenceLoader(connection=db_connection, external_source="fipe")


@pytest.fixture(autouse=True)
def clean_vehicle_tables(db_connection):
    """
    Garante isolamento TOTAL entre testes deste módulo.

    Ordem importante por FK:
    vehicles → models → brands
    """
    with db_connection.cursor() as cursor:
        cursor.execute("TRUNCATE reference.vehicles CASCADE")
        cursor.execute("TRUNCATE reference.vehicle_models CASCADE")
        cursor.execute("TRUNCATE reference.vehicle_brands CASCADE")

    db_connection.commit()

    yield


# =============================================================================
# HELPERS
# =============================================================================


def _count_rows(db_connection, table_name: str) -> int:
    with db_connection.cursor() as cursor:
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        return int(cursor.fetchone()[0])


# =============================================================================
# TESTES DE MARCAS
# =============================================================================


def test_load_brands_inserts_rows(loader, db_connection):
    brands = [
        {"external_code": "21", "name": "Fiat"},
        {"external_code": "22", "name": "Ford"},
    ]

    result = loader.load_brands(brands)

    assert result.processed_count == 2
    assert _count_rows(db_connection, "reference.vehicle_brands") == 2

    with db_connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT external_source, external_code, name, normalized_name
            FROM reference.vehicle_brands
            ORDER BY external_code
            """
        )
        rows = cursor.fetchall()

    assert rows == [
        ("fipe", "21", "Fiat", "FIAT"),
        ("fipe", "22", "Ford", "FORD"),
    ]


def test_load_brands_is_idempotent_when_executed_twice(loader, db_connection):
    brands = [
        {"external_code": "21", "name": "Fiat"},
        {"external_code": "22", "name": "Ford"},
    ]

    loader.load_brands(brands)
    loader.load_brands(brands)

    assert _count_rows(db_connection, "reference.vehicle_brands") == 2


# =============================================================================
# TESTES DE DEPENDÊNCIA
# =============================================================================


def test_load_models_raises_error_when_brand_does_not_exist(loader):
    models = [
        {
            "external_code": "1001",
            "brand_external_code": "9999",
            "name": "Uno",
        }
    ]

    with pytest.raises(DependencyNotFoundError):
        loader.load_models(models)


def test_load_vehicles_raises_error_when_model_does_not_exist(loader):
    loader.load_brands(
        [
            {"external_code": "21", "name": "Fiat"},
        ]
    )

    vehicles = [
        {
            "external_code": "v-uno-2020-flex",
            "brand_external_code": "21",
            "model_external_code": "modelo-ausente",
            "model_year": 2020,
            "fuel_type": "Flex",
            "version_name": "Uno Attractive 1.0",
            "fipe_code": "001234-5",
        }
    ]

    with pytest.raises(DependencyNotFoundError):
        loader.load_vehicles(vehicles)


# =============================================================================
# TESTE DE FLUXO COMPLETO
# =============================================================================


def test_load_all_executes_complete_flow(loader, db_connection):
    brands = [
        {"external_code": "21", "name": "Fiat"},
    ]
    models = [
        {
            "external_code": "1001",
            "brand_external_code": "21",
            "name": "Uno",
        }
    ]
    vehicles = [
        {
            "external_code": "2001",
            "brand_external_code": "21",
            "model_external_code": "1001",
            "model_year": 2020,
            "fuel_type": "Flex",
            "version_name": "Uno Attractive 1.0",
            "fipe_code": "001234-5",
        }
    ]

    result = loader.load_all(
        brands=brands,
        models=models,
        vehicles=vehicles,
    )

    assert isinstance(result, LoadAllResult)
    assert result.brands.processed_count == 1
    assert result.models.processed_count == 1
    assert result.vehicles.processed_count == 1

    assert _count_rows(db_connection, "reference.vehicle_brands") == 1
    assert _count_rows(db_connection, "reference.vehicle_models") == 1
    assert _count_rows(db_connection, "reference.vehicles") == 1

    with db_connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT
                v.external_source,
                v.external_code,
                v.model_year,
                v.fuel_type,
                v.version_name,
                v.fipe_code,
                b.external_code,
                m.external_code
            FROM reference.vehicles v
            JOIN reference.vehicle_brands b
                ON b.id = v.brand_id
            JOIN reference.vehicle_models m
                ON m.id = v.model_id
            """
        )
        row = cursor.fetchone()

    assert row == (
        "fipe",
        "2001",
        2020,
        "Flex",
        "Uno Attractive 1.0",
        "001234-5",
        "21",
        "1001",
    )