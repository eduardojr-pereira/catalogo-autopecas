"""
Testes do loader de referências de veículos.

Cobertura desta suíte:
- insert de marcas;
- idempotência ao rodar a carga duas vezes;
- erro ao carregar modelo sem marca;
- erro ao carregar veículo sem modelo;
- fluxo completo com load_all().

Observação:
- os testes assumem a existência do schema oficial já aplicado no banco de teste;
- os testes usam PostgreSQL real, alinhados ao padrão do projeto.
"""

from __future__ import annotations

import os

import psycopg
import pytest
from psycopg.rows import dict_row
from psycopg import Connection

from src.ingestion.loaders.vehicle_reference_loader import (
    DependencyNotFoundError,
    LoadAllResult,
    VehicleReferenceLoader,
)


def _get_test_database_dsn() -> str:
    """
    Resolve a URL de conexão do banco de teste.

    Ordem de fallback:
    - TEST_DATABASE_URL
    - DATABASE_TEST_URL
    - DATABASE_URL
    """
    candidates = (
        os.getenv("TEST_DATABASE_URL"),
        os.getenv("DATABASE_TEST_URL"),
        os.getenv("DATABASE_URL"),
    )

    for candidate in candidates:
        if candidate:
            return candidate

    raise RuntimeError(
        "Defina TEST_DATABASE_URL, DATABASE_TEST_URL ou DATABASE_URL "
        "para executar os testes do loader."
    )


@pytest.fixture()
def db_connection() -> Connection:
    """
    Abre uma conexão de teste isolada.

    Cada teste:
    - limpa as tabelas relevantes antes da execução;
    - faz rollback/close ao final.
    """
    connection = psycopg.connect(_get_test_database_dsn(), row_factory=dict_row)

    _truncate_reference_tables(connection)

    try:
        yield connection
    finally:
        connection.rollback()
        connection.close()


@pytest.fixture()
def loader(db_connection: Connection) -> VehicleReferenceLoader:
    """Instancia o loader com a fonte oficial FIPE."""
    return VehicleReferenceLoader(connection=db_connection, external_source="fipe")


def _truncate_reference_tables(connection: Connection) -> None:
    """
    Limpa as tabelas de referência usadas nos testes.

    A ordem segue a dependência relacional.
    """
    with connection.transaction():
        with connection.cursor() as cursor:
            cursor.execute("TRUNCATE TABLE reference.vehicles RESTART IDENTITY CASCADE")
            cursor.execute(
                "TRUNCATE TABLE reference.vehicle_models RESTART IDENTITY CASCADE"
            )
            cursor.execute(
                "TRUNCATE TABLE reference.vehicle_brands RESTART IDENTITY CASCADE"
            )


def _count_rows(connection: Connection, table_name: str) -> int:
    """Conta registros de uma tabela."""
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT COUNT(*) AS total FROM {table_name}")
        row = cursor.fetchone()
        assert row is not None
        return int(row["total"])


def test_load_brands_inserts_rows(
    loader: VehicleReferenceLoader,
    db_connection: Connection,
) -> None:
    """Deve inserir marcas válidas em reference.vehicle_brands."""
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
            SELECT external_source, external_code, name
            FROM reference.vehicle_brands
            ORDER BY external_code
            """
        )
        rows = cursor.fetchall()

    assert rows == [
        {"external_source": "fipe", "external_code": "21", "name": "Fiat"},
        {"external_source": "fipe", "external_code": "22", "name": "Ford"},
    ]


def test_load_brands_is_idempotent_when_executed_twice(
    loader: VehicleReferenceLoader,
    db_connection: Connection,
) -> None:
    """Não deve duplicar marcas ao executar a mesma carga duas vezes."""
    brands = [
        {"external_code": "21", "name": "Fiat"},
        {"external_code": "22", "name": "Ford"},
    ]

    first_result = loader.load_brands(brands)
    second_result = loader.load_brands(brands)

    assert first_result.processed_count == 2
    assert second_result.processed_count == 2
    assert _count_rows(db_connection, "reference.vehicle_brands") == 2


def test_load_models_raises_error_when_brand_does_not_exist(
    loader: VehicleReferenceLoader,
) -> None:
    """Deve falhar ao tentar carregar modelo sem a marca previamente persistida."""
    models = [
        {
            "external_code": "1001",
            "brand_external_code": "9999",
            "name": "Uno",
        }
    ]

    with pytest.raises(DependencyNotFoundError) as exc_info:
        loader.load_models(models)

    assert "brand_external_code" in str(exc_info.value)


def test_load_vehicles_raises_error_when_model_does_not_exist(
    loader: VehicleReferenceLoader,
) -> None:
    """Deve falhar ao tentar carregar veículo sem o modelo previamente persistido."""
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

    with pytest.raises(DependencyNotFoundError) as exc_info:
        loader.load_vehicles(vehicles)

    assert "model_external_code" in str(exc_info.value)


def test_load_all_executes_complete_flow(
    loader: VehicleReferenceLoader,
    db_connection: Connection,
) -> None:
    """Deve executar a carga completa respeitando a ordem oficial."""
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
                b.external_code AS brand_external_code,
                m.external_code AS model_external_code
            FROM reference.vehicles AS v
            INNER JOIN reference.vehicle_brands AS b
                ON b.brand_id = v.brand_id
            INNER JOIN reference.vehicle_models AS m
                ON m.model_id = v.model_id
            """
        )
        row = cursor.fetchone()

    assert row == {
        "external_source": "fipe",
        "external_code": "2001",
        "model_year": 2020,
        "fuel_type": "Flex",
        "version_name": "Uno Attractive 1.0",
        "fipe_code": "001234-5",
        "brand_external_code": "21",
        "model_external_code": "1001",
    }