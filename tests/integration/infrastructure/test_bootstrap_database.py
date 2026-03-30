"""
test_bootstrap_database.py

Testes de integração responsáveis por validar o bootstrap do banco.

Objetivos destes testes:

1) Garantir que o banco de dados está acessível.
2) Validar que os schemas principais foram criados.
3) Confirmar que tabelas essenciais existem.
4) Verificar se os dados canônicos foram carregados.
5) Proteger índices críticos do sistema.

Esses testes ajudam a detectar regressões no bootstrap do banco,
principalmente após alterações em:

- database/schema.sql
- database/seeds/canonical_seed.sql
"""


# ---------------------------------------------------------------------
# TESTE DE CONEXÃO
# ---------------------------------------------------------------------

def test_database_connection(db_cursor):
    """
    Verifica se é possível executar uma query simples no banco.

    Esse teste confirma que:
    - a conexão com o PostgreSQL está funcionando
    - o banco catalogo_test foi selecionado corretamente
    """

    db_cursor.execute("SELECT 1")

    result = db_cursor.fetchone()

    assert result[0] == 1


# ---------------------------------------------------------------------
# TESTE DE EXISTÊNCIA DOS SCHEMAS
# ---------------------------------------------------------------------

def test_schemas_exist(db_cursor):
    """
    Verifica se os schemas principais do projeto existem.
    """

    db_cursor.execute(
        """
        SELECT schema_name
        FROM information_schema.schemata
        WHERE schema_name IN (
            'reference',
            'discovery',
            'catalog',
            'compatibility',
            'publication'
        )
        """
    )

    schemas = {row[0] for row in db_cursor.fetchall()}

    assert "reference" in schemas
    assert "discovery" in schemas
    assert "catalog" in schemas
    assert "compatibility" in schemas
    assert "publication" in schemas


# ---------------------------------------------------------------------
# TESTE DE EXISTÊNCIA DAS TABELAS PRINCIPAIS
# ---------------------------------------------------------------------

def test_core_tables_exist(db_cursor):
    """
    Verifica se as tabelas essenciais do sistema foram criadas.
    """

    db_cursor.execute(
        """
        SELECT table_schema, table_name
        FROM information_schema.tables
        WHERE (table_schema, table_name) IN (
            ('reference','vehicle_brands'),
            ('reference','vehicle_models'),
            ('reference','vehicles'),
            ('catalog','parts'),
            ('catalog','applications'),
            ('discovery','codes')
        )
        """
    )

    tables = {(row[0], row[1]) for row in db_cursor.fetchall()}

    assert ("reference", "vehicle_brands") in tables
    assert ("reference", "vehicle_models") in tables
    assert ("reference", "vehicles") in tables
    assert ("catalog", "parts") in tables
    assert ("catalog", "applications") in tables
    assert ("discovery", "codes") in tables


# ---------------------------------------------------------------------
# TESTE DE DOMÍNIOS CANÔNICOS
# ---------------------------------------------------------------------

def test_canonical_domains_loaded(db_cursor):
    """
    Verifica se os domínios canônicos foram carregados.

    Esses dados vêm de:
    database/seeds/canonical_seed.sql
    """

    domains = [
        "fuel_types",
        "position_types",
        "side_types",
        "body_types",
    ]

    for table in domains:

        db_cursor.execute(
            f"SELECT COUNT(*) FROM reference.{table}"
        )

        count = db_cursor.fetchone()[0]

        assert count > 0, f"Tabela reference.{table} não possui dados canônicos"


# ---------------------------------------------------------------------
# TESTE DE VALORES CANÔNICOS ESPERADOS
# ---------------------------------------------------------------------

def test_expected_fuel_types(db_cursor):
    """
    Garante que os tipos de combustível esperados existem.

    Isso protege o projeto contra alterações acidentais no seed.
    """

    db_cursor.execute(
        """
        SELECT code
        FROM reference.fuel_types
        """
    )

    fuel_types = {row[0] for row in db_cursor.fetchall()}

    expected = {
        "gasoline",
        "diesel",
        "flex",
        "hybrid",
        "electric",
    }

    for fuel in expected:
        assert fuel in fuel_types


# ---------------------------------------------------------------------
# TESTE DO ÍNDICE DE UNICIDADE DE VEÍCULOS
# ---------------------------------------------------------------------

def test_vehicle_uniqueness_index_exists(db_cursor):
    """
    Verifica se o índice que protege duplicidade lógica de veículos existe.

    Índice esperado:

    idx_unique_vehicle_configuration
    """

    db_cursor.execute(
        """
        SELECT indexname
        FROM pg_indexes
        WHERE schemaname = 'reference'
        AND indexname = 'idx_unique_vehicle_configuration'
        """
    )

    index = db_cursor.fetchone()

    assert index is not None