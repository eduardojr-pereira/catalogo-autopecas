"""
Testes estruturais do banco de dados.

Responsabilidades deste arquivo:
- validar que os schemas principais existem;
- validar que as tabelas principais foram criadas;
- validar colunas críticas do domínio;
- validar foreign keys relevantes;
- validar índices e constraints essenciais do schema.

Este arquivo NÃO deve:
- testar regras de negócio do loader;
- testar parsing da FIPE;
- validar conteúdo de seeds;
- testar serviços de aplicação.

Observação:
- estes testes funcionam como proteção contra regressões estruturais
  no schema.sql;
- o foco principal desta revisão está no domínio de veículos, pois ele
  foi alterado para suportar identidade externa por
  (external_source, external_code).
"""

from __future__ import annotations

from collections.abc import Iterable

import pytest


# ============================================================================
# HELPERS
# ============================================================================


def _fetch_all_as_set(cursor, query: str, params: Iterable | None = None) -> set[str]:
    """
    Executa uma consulta e retorna a primeira coluna como conjunto.

    Args:
        cursor:
            Cursor ativo do banco.
        query:
            SQL a ser executado.
        params:
            Parâmetros opcionais.

    Returns:
        Conjunto com os valores da primeira coluna retornada.
    """
    cursor.execute(query, params or ())
    return {row[0] for row in cursor.fetchall()}


def _fetch_columns(cursor, schema: str, table: str) -> set[str]:
    """
    Retorna o conjunto de colunas de uma tabela.

    Args:
        cursor:
            Cursor ativo do banco.
        schema:
            Nome do schema.
        table:
            Nome da tabela.

    Returns:
        Conjunto com os nomes das colunas.
    """
    return _fetch_all_as_set(
        cursor,
        """
        SELECT column_name
        FROM information_schema.columns
        WHERE table_schema = %s
          AND table_name = %s
        ORDER BY ordinal_position;
        """,
        (schema, table),
    )


def _fetch_indexes(cursor, schema: str, table: str) -> dict[str, str]:
    """
    Retorna os índices de uma tabela.

    Args:
        cursor:
            Cursor ativo do banco.
        schema:
            Nome do schema.
        table:
            Nome da tabela.

    Returns:
        Dicionário no formato:
            {
                index_name: index_definition,
                ...
            }
    """
    cursor.execute(
        """
        SELECT indexname, indexdef
        FROM pg_indexes
        WHERE schemaname = %s
          AND tablename = %s;
        """,
        (schema, table),
    )
    return {row[0]: row[1] for row in cursor.fetchall()}


def _fetch_foreign_keys(cursor, schema: str, table: str) -> set[tuple[str, str, str]]:
    """
    Retorna as foreign keys de uma tabela.

    Formato retornado:
        {
            (column_name, foreign_table_schema, foreign_table_name),
            ...
        }

    Args:
        cursor:
            Cursor ativo do banco.
        schema:
            Nome do schema.
        table:
            Nome da tabela.

    Returns:
        Conjunto com as foreign keys encontradas.
    """
    cursor.execute(
        """
        SELECT
            kcu.column_name,
            ccu.table_schema AS foreign_table_schema,
            ccu.table_name AS foreign_table_name
        FROM information_schema.table_constraints AS tc
        JOIN information_schema.key_column_usage AS kcu
          ON tc.constraint_name = kcu.constraint_name
         AND tc.table_schema = kcu.table_schema
        JOIN information_schema.constraint_column_usage AS ccu
          ON ccu.constraint_name = tc.constraint_name
         AND ccu.table_schema = tc.table_schema
        WHERE tc.constraint_type = 'FOREIGN KEY'
          AND tc.table_schema = %s
          AND tc.table_name = %s;
        """,
        (schema, table),
    )
    return {(row[0], row[1], row[2]) for row in cursor.fetchall()}


# ============================================================================
# TESTES DE SCHEMAS
# ============================================================================


def test_required_schemas_exist(db_connection) -> None:
    """
    Garante que os schemas oficiais do projeto existem.
    """
    expected_schemas = {
        "reference",
        "discovery",
        "catalog",
        "compatibility",
        "publication",
    }

    with db_connection.cursor() as cursor:
        actual_schemas = _fetch_all_as_set(
            cursor,
            """
            SELECT schema_name
            FROM information_schema.schemata
            WHERE schema_name IN (
                'reference',
                'discovery',
                'catalog',
                'compatibility',
                'publication'
            );
            """,
        )

    assert actual_schemas == expected_schemas


# ============================================================================
# TESTES DE TABELAS PRINCIPAIS
# ============================================================================


def test_required_tables_exist(db_connection) -> None:
    """
    Garante que as tabelas principais do projeto existem.
    """
    expected_tables = {
        ("reference", "manufacturers"),
        ("reference", "part_types"),
        ("reference", "part_type_aliases"),
        ("reference", "position_types"),
        ("reference", "side_types"),
        ("reference", "fuel_types"),
        ("reference", "body_types"),
        ("reference", "attribute_units"),
        ("reference", "attribute_definitions"),
        ("reference", "vehicle_brands"),
        ("reference", "vehicle_models"),
        ("reference", "vehicles"),
        ("reference", "motors"),
        ("reference", "vehicle_motors"),
        ("discovery", "sources"),
        ("discovery", "codes"),
        ("discovery", "code_evidence"),
        ("discovery", "code_equivalences"),
        ("catalog", "parts"),
        ("catalog", "part_attributes"),
        ("catalog", "clusters"),
        ("catalog", "cluster_codes"),
        ("catalog", "applications"),
        ("compatibility", "rules"),
        ("compatibility", "evidence"),
        ("compatibility", "decisions"),
        ("publication", "batches"),
        ("publication", "catalog_versions"),
        ("publication", "published_parts"),
        ("publication", "published_applications"),
    }

    with db_connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT table_schema, table_name
            FROM information_schema.tables
            WHERE table_type = 'BASE TABLE'
              AND table_schema IN (
                  'reference',
                  'discovery',
                  'catalog',
                  'compatibility',
                  'publication'
              );
            """
        )
        actual_tables = {(row[0], row[1]) for row in cursor.fetchall()}

    missing = expected_tables - actual_tables
    assert not missing, f"Tabelas ausentes: {sorted(missing)}"


# ============================================================================
# TESTES DO DOMÍNIO DE VEÍCULOS
# ============================================================================


def test_vehicle_brands_columns(db_connection) -> None:
    """
    Garante as colunas contratuais de reference.vehicle_brands.
    """
    expected_columns = {
        "id",
        "name",
        "normalized_name",
        "external_source",
        "external_code",
        "created_at",
    }

    with db_connection.cursor() as cursor:
        actual_columns = _fetch_columns(cursor, "reference", "vehicle_brands")

    assert actual_columns == expected_columns
    assert "fipe_brand_code" not in actual_columns


def test_vehicle_models_columns(db_connection) -> None:
    """
    Garante as colunas contratuais de reference.vehicle_models.
    """
    expected_columns = {
        "id",
        "brand_id",
        "name",
        "normalized_name",
        "external_source",
        "external_code",
        "created_at",
    }

    with db_connection.cursor() as cursor:
        actual_columns = _fetch_columns(cursor, "reference", "vehicle_models")

    assert actual_columns == expected_columns
    assert "fipe_model_code" not in actual_columns


def test_vehicles_columns(db_connection) -> None:
    """
    Garante as colunas contratuais de reference.vehicles.
    """
    expected_columns = {
        "id",
        "brand_id",
        "model_id",
        "brand_text",
        "model_text",
        "model_year",
        "version_name",
        "body_type",
        "body_type_id",
        "fuel_type",
        "fuel_type_id",
        "market",
        "fipe_code",
        "external_source",
        "external_code",
        "created_at",
    }

    with db_connection.cursor() as cursor:
        actual_columns = _fetch_columns(cursor, "reference", "vehicles")

    assert actual_columns == expected_columns
    assert "version" not in actual_columns
    assert "fipe_vehicle_code" not in actual_columns


# ============================================================================
# TESTES DE FOREIGN KEYS DO DOMÍNIO DE VEÍCULOS
# ============================================================================


def test_vehicle_models_foreign_keys(db_connection) -> None:
    """
    Garante a FK principal de vehicle_models -> vehicle_brands.
    """
    expected_fk = ("brand_id", "reference", "vehicle_brands")

    with db_connection.cursor() as cursor:
        foreign_keys = _fetch_foreign_keys(cursor, "reference", "vehicle_models")

    assert expected_fk in foreign_keys


def test_vehicles_foreign_keys(db_connection) -> None:
    """
    Garante as FKs principais de reference.vehicles.
    """
    expected_fks = {
        ("brand_id", "reference", "vehicle_brands"),
        ("model_id", "reference", "vehicle_models"),
        ("body_type_id", "reference", "body_types"),
        ("fuel_type_id", "reference", "fuel_types"),
    }

    with db_connection.cursor() as cursor:
        foreign_keys = _fetch_foreign_keys(cursor, "reference", "vehicles")

    missing = expected_fks - foreign_keys
    assert not missing, f"FKs ausentes em reference.vehicles: {sorted(missing)}"


def test_vehicle_motors_foreign_keys(db_connection) -> None:
    """
    Garante as FKs da tabela de relacionamento vehicle_motors.
    """
    expected_fks = {
        ("vehicle_id", "reference", "vehicles"),
        ("motor_id", "reference", "motors"),
    }

    with db_connection.cursor() as cursor:
        foreign_keys = _fetch_foreign_keys(cursor, "reference", "vehicle_motors")

    missing = expected_fks - foreign_keys
    assert not missing, f"FKs ausentes em reference.vehicle_motors: {sorted(missing)}"


# ============================================================================
# TESTES DE ÍNDICES E IDENTIDADE EXTERNA
# ============================================================================


def test_vehicle_brands_indexes(db_connection) -> None:
    """
    Garante os índices essenciais de vehicle_brands.
    """
    expected_indexes = {
        "idx_vehicle_brands_external_identity",
        "idx_vehicle_brands_normalized_name",
    }

    with db_connection.cursor() as cursor:
        indexes = _fetch_indexes(cursor, "reference", "vehicle_brands")

    for index_name in expected_indexes:
        assert index_name in indexes, f"Índice ausente: {index_name}"

    external_identity_sql = indexes["idx_vehicle_brands_external_identity"]
    assert "external_source" in external_identity_sql
    assert "external_code" in external_identity_sql
    assert "UNIQUE" in external_identity_sql


def test_vehicle_models_indexes(db_connection) -> None:
    """
    Garante os índices essenciais de vehicle_models.
    """
    expected_indexes = {
        "idx_vehicle_models_external_identity",
        "idx_vehicle_models_unique",
        "idx_vehicle_models_brand_id",
    }

    with db_connection.cursor() as cursor:
        indexes = _fetch_indexes(cursor, "reference", "vehicle_models")

    for index_name in expected_indexes:
        assert index_name in indexes, f"Índice ausente: {index_name}"

    external_identity_sql = indexes["idx_vehicle_models_external_identity"]
    assert "external_source" in external_identity_sql
    assert "external_code" in external_identity_sql
    assert "UNIQUE" in external_identity_sql


def test_vehicles_indexes(db_connection) -> None:
    """
    Garante os índices essenciais de reference.vehicles.
    """
    expected_indexes = {
        "idx_vehicles_external_identity",
        "idx_vehicles_brand_id",
        "idx_vehicles_model_id",
        "idx_vehicles_model_year",
        "idx_vehicles_body_type_id",
        "idx_vehicles_fuel_type_id",
        "idx_unique_vehicle_configuration",
    }

    with db_connection.cursor() as cursor:
        indexes = _fetch_indexes(cursor, "reference", "vehicles")

    for index_name in expected_indexes:
        assert index_name in indexes, f"Índice ausente: {index_name}"

    external_identity_sql = indexes["idx_vehicles_external_identity"]
    assert "external_source" in external_identity_sql
    assert "external_code" in external_identity_sql
    assert "UNIQUE" in external_identity_sql

    unique_configuration_sql = indexes["idx_unique_vehicle_configuration"]
    assert "model_id" in unique_configuration_sql
    assert "model_year" in unique_configuration_sql
    assert "version_name" in unique_configuration_sql
    assert "fuel_type" in unique_configuration_sql
    assert "market" in unique_configuration_sql


# ============================================================================
# TESTES DE COLUNAS CRÍTICAS DE OUTRAS TABELAS
# ============================================================================


@pytest.mark.parametrize(
    ("schema_name", "table_name", "required_columns"),
    [
        (
            "discovery",
            "codes",
            {"id", "manufacturer_id", "code", "normalized_code", "created_at"},
        ),
        (
            "catalog",
            "parts",
            {"id", "name", "normalized_name", "part_type_id", "description", "status", "created_at"},
        ),
        (
            "catalog",
            "applications",
            {
                "id",
                "cluster_id",
                "motor_id",
                "vehicle_id",
                "position",
                "position_type_id",
                "side",
                "side_type_id",
                "notes",
                "source",
                "confidence_score",
                "created_at",
            },
        ),
        (
            "compatibility",
            "rules",
            {"id", "name", "description", "rule_type", "rule_expression", "priority", "is_active", "created_at"},
        ),
        (
            "publication",
            "catalog_versions",
            {"id", "version_number", "batch_id", "created_at", "notes"},
        ),
    ],
)
def test_critical_tables_have_expected_columns(
    db_connection,
    schema_name: str,
    table_name: str,
    required_columns: set[str],
) -> None:
    """
    Garante colunas mínimas de tabelas importantes fora do núcleo de veículos.
    """
    with db_connection.cursor() as cursor:
        actual_columns = _fetch_columns(cursor, schema_name, table_name)

    missing = required_columns - actual_columns
    assert not missing, f"Colunas ausentes em {schema_name}.{table_name}: {sorted(missing)}"