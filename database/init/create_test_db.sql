-- ==========================================================
-- create_test_db.sql
-- Cria role e banco de testes para execução da suíte.
-- Compatível com execução via psql no bootstrap do Docker.
-- Evita falhas em recriação de ambiente e CI/CD.
-- ==========================================================

-- ----------------------------------------------------------
-- 1) Cria a role de testes somente se ainda não existir
-- ----------------------------------------------------------
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

-- ----------------------------------------------------------
-- 2) Cria o banco de testes somente se ainda não existir
--    Observação:
--    CREATE DATABASE não pode ser executado dentro de DO,
--    função ou transação. Por isso usamos SELECT + \gexec.
-- ----------------------------------------------------------
SELECT
    'CREATE DATABASE catalog_test OWNER catalog_test ENCODING ''UTF8'''
WHERE NOT EXISTS (
    SELECT 1
    FROM pg_database
    WHERE datname = 'catalog_test'
)
\gexec