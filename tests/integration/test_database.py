"""
test_database.py

Testes de integração para validar a estrutura mínima esperada do banco.
"""

from __future__ import annotations

import pytest


def get_existing_schemas(cursor) -> set[str]:
    cursor.execute("""
        SELECT schema_name
        FROM information_schema.schemata
    """)
    return {row[0] for row in cursor.fetchall()}


def get_existing_tables(cursor, schema_name: str) -> set[str]:
    cursor.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = %s
          AND table_type = 'BASE TABLE'
    """, (schema_name,))
    return {row[0] for row in cursor.fetchall()}


def get_existing_columns(cursor, schema_name: str, table_name: str) -> set[str]:
    cursor.execute("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_schema = %s
          AND table_name = %s
    """, (schema_name, table_name))
    return {row[0] for row in cursor.fetchall()}


def get_foreign_key_columns(cursor, schema_name: str, table_name: str) -> set[str]:
    cursor.execute("""
        SELECT kcu.column_name
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu
          ON tc.constraint_name = kcu.constraint_name
         AND tc.table_schema = kcu.table_schema
        WHERE tc.constraint_type = 'FOREIGN KEY'
          AND tc.table_schema = %s
          AND tc.table_name = %s
    """, (schema_name, table_name))
    return {row[0] for row in cursor.fetchall()}


def get_indexes(cursor, schema_name: str, table_name: str) -> set[str]:
    cursor.execute("""
        SELECT indexname
        FROM pg_indexes
        WHERE schemaname = %s
          AND tablename = %s
    """, (schema_name, table_name))
    return {row[0] for row in cursor.fetchall()}


def assert_table_has_columns(cursor, schema_name: str, table_name: str, expected_columns: set[str]) -> None:
    existing_columns = get_existing_columns(cursor, schema_name, table_name)
    missing_columns = expected_columns - existing_columns
    assert not missing_columns, (
        f"Tabela {schema_name}.{table_name} sem colunas esperadas: "
        f"{sorted(missing_columns)}"
    )


def assert_table_has_foreign_keys(cursor, schema_name: str, table_name: str, expected_fk_columns: set[str]) -> None:
    existing_fk_columns = get_foreign_key_columns(cursor, schema_name, table_name)
    missing_fk_columns = expected_fk_columns - existing_fk_columns
    assert not missing_fk_columns, (
        f"Tabela {schema_name}.{table_name} sem FKs esperadas em: "
        f"{sorted(missing_fk_columns)}"
    )


def assert_table_has_indexes(cursor, schema_name: str, table_name: str, expected_indexes: set[str]) -> None:
    existing_indexes = get_indexes(cursor, schema_name, table_name)
    missing_indexes = expected_indexes - existing_indexes
    assert not missing_indexes, (
        f"Tabela {schema_name}.{table_name} sem índices esperados: "
        f"{sorted(missing_indexes)}"
    )


def test_required_schemas_exist(db_cursor):
    expected_schemas = {
        "reference",
        "discovery",
        "catalog",
        "compatibility",
        "publication",
    }

    existing_schemas = get_existing_schemas(db_cursor)
    missing_schemas = expected_schemas - existing_schemas

    assert not missing_schemas, f"Schemas ausentes: {sorted(missing_schemas)}"


def test_required_tables_exist(db_cursor):
    expected_tables_by_schema = {
        "reference": {
            "manufacturers",
            "part_types",
            "part_type_aliases",
            "position_types",
            "side_types",
            "fuel_types",
            "body_types",
            "attribute_units",
            "attribute_definitions",
            "vehicle_brands",
            "vehicle_models",
            "vehicles",
            "motors",
            "vehicle_motors",
        },
        "discovery": {
            "sources",
            "codes",
            "code_evidence",
            "code_equivalences",
        },
        "catalog": {
            "parts",
            "part_attributes",
            "clusters",
            "cluster_codes",
            "applications",
        },
        "compatibility": {
            "rules",
            "evidence",
            "decisions",
        },
        "publication": {
            "batches",
            "catalog_versions",
            "published_parts",
            "published_applications",
        },
    }

    for schema_name, expected_tables in expected_tables_by_schema.items():
        existing_tables = get_existing_tables(db_cursor, schema_name)
        missing_tables = expected_tables - existing_tables

        assert not missing_tables, (
            f"Tabelas ausentes em {schema_name}: {sorted(missing_tables)}"
        )


def test_vehicle_brands_columns(db_cursor):
    expected_columns = {
        "id",
        "name",
        "normalized_name",
        "external_source",
        "external_code",
        "created_at",
    }

    assert_table_has_columns(
        db_cursor,
        "reference",
        "vehicle_brands",
        expected_columns,
    )


def test_vehicle_models_columns(db_cursor):
    expected_columns = {
        "id",
        "brand_id",
        "name",
        "normalized_name",
        "external_source",
        "external_code",
        "created_at",
    }

    assert_table_has_columns(
        db_cursor,
        "reference",
        "vehicle_models",
        expected_columns,
    )


def test_vehicles_columns(db_cursor):
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

    assert_table_has_columns(
        db_cursor,
        "reference",
        "vehicles",
        expected_columns,
    )


def test_vehicle_models_foreign_keys(db_cursor):
    expected_fk_columns = {"brand_id"}

    assert_table_has_foreign_keys(
        db_cursor,
        "reference",
        "vehicle_models",
        expected_fk_columns,
    )


def test_vehicles_foreign_keys(db_cursor):
    expected_fk_columns = {
        "brand_id",
        "model_id",
        "body_type_id",
        "fuel_type_id",
    }

    assert_table_has_foreign_keys(
        db_cursor,
        "reference",
        "vehicles",
        expected_fk_columns,
    )


def test_vehicle_motors_foreign_keys(db_cursor):
    expected_fk_columns = {"vehicle_id", "motor_id"}

    assert_table_has_foreign_keys(
        db_cursor,
        "reference",
        "vehicle_motors",
        expected_fk_columns,
    )


def test_vehicle_brands_indexes(db_cursor):
    expected_indexes = {
        "idx_vehicle_brands_external_identity",
        "idx_vehicle_brands_normalized_name",
    }

    assert_table_has_indexes(
        db_cursor,
        "reference",
        "vehicle_brands",
        expected_indexes,
    )


def test_vehicle_models_indexes(db_cursor):
    expected_indexes = {
        "idx_vehicle_models_external_identity",
        "idx_vehicle_models_unique",
        "idx_vehicle_models_brand_id",
    }

    assert_table_has_indexes(
        db_cursor,
        "reference",
        "vehicle_models",
        expected_indexes,
    )


def test_vehicles_indexes(db_cursor):
    expected_indexes = {
        "idx_vehicles_external_identity",
        "idx_vehicles_brand_id",
        "idx_vehicles_model_id",
        "idx_vehicles_model_year",
        "idx_vehicles_body_type_id",
        "idx_vehicles_fuel_type_id",
        "idx_unique_vehicle_configuration",
    }

    assert_table_has_indexes(
        db_cursor,
        "reference",
        "vehicles",
        expected_indexes,
    )


@pytest.mark.parametrize(
    ("schema_name", "table_name", "required_columns"),
    [
        (
            "discovery",
            "codes",
            {
                "id",
                "manufacturer_id",
                "code",
                "normalized_code",
                "created_at",
            },
        ),
        (
            "catalog",
            "parts",
            {
                "id",
                "name",
                "normalized_name",
                "part_type_id",
                "description",
                "status",
                "created_at",
            },
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
            {
                "id",
                "name",
                "description",
                "rule_type",
                "rule_expression",
                "priority",
                "is_active",
                "created_at",
            },
        ),
        (
            "publication",
            "catalog_versions",
            {
                "id",
                "version_number",
                "batch_id",
                "created_at",
                "notes",
            },
        ),
    ],
)
def test_critical_tables_have_expected_columns(
    db_cursor,
    schema_name: str,
    table_name: str,
    required_columns: set[str],
):
    assert_table_has_columns(
        db_cursor,
        schema_name,
        table_name,
        required_columns,
    )