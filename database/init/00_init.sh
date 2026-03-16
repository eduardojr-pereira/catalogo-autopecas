#!/usr/bin/env bash
set -e

echo "============================================================"
echo "Iniciando bootstrap do banco: ${POSTGRES_DB}"
echo "============================================================"

run_sql() {
  local db_name="$1"
  local file_path="$2"

  echo ""
  echo "Executando arquivo SQL em ${db_name}: ${file_path}"

  psql \
    -v ON_ERROR_STOP=1 \
    --username "${POSTGRES_USER}" \
    --dbname "${db_name}" \
    -f "${file_path}"
}

bootstrap_database() {
  local db_name="$1"

  echo ""
  echo "------------------------------------------------------------"
  echo "Bootstrap do banco: ${db_name}"
  echo "------------------------------------------------------------"

  run_sql "${db_name}" "/app/database/schema.sql"
  run_sql "${db_name}" "/app/database/seeds/canonical_seed.sql"
  run_sql "${db_name}" "/app/database/seeds/reference_seed.sql"
  run_sql "${db_name}" "/app/database/views/catalog_public_views.sql"
  run_sql "${db_name}" "/app/database/views/catalog_search_views.sql"
}

echo ""
echo "Criando role de teste se necessário..."
psql -v ON_ERROR_STOP=1 --username "${POSTGRES_USER}" --dbname postgres <<'SQL'
DO
$$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_catalog.pg_roles
        WHERE rolname = 'catalog_test'
    ) THEN
        CREATE ROLE catalog_test
            LOGIN
            PASSWORD 'catalog_test';
    END IF;
END
$$;
SQL

echo ""
echo "Criando banco de teste se necessário..."
psql -v ON_ERROR_STOP=1 --username "${POSTGRES_USER}" --dbname postgres <<'SQL'
SELECT
    'CREATE DATABASE catalog_test OWNER catalog_test ENCODING ''UTF8'''
WHERE NOT EXISTS (
    SELECT 1
    FROM pg_database
    WHERE datname = 'catalog_test'
)
\gexec
SQL

bootstrap_database "${POSTGRES_DB}"
bootstrap_database "catalog_test"

echo ""
echo "============================================================"
echo "Bootstrap do banco finalizado com sucesso."
echo "============================================================"