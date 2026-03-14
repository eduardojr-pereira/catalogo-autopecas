import psycopg2 # Importa a biblioteca usada para conectar ao PostgreSQL
import pytest # Importa o pytest, que é o framework de testes


# ------------------------------------------------------
# FIXTURE DE CONEXÃO
# ------------------------------------------------------
@pytest.fixture
def db_connection():
    """
    Cria uma conexão com o banco PostgreSQL para ser usada nos testes.

    O pytest executa esta fixture antes do teste que precisa dela
    e, ao final, fecha a conexão automaticamente.
    """
    conn = psycopg2.connect(
        host="localhost",      # endereço do banco
        database="catalogo",   # nome do banco criado no Docker
        user="admin",          # usuário definido no docker-compose
        password="admin",      # senha definida no docker-compose
        port=5432              # porta exposta pelo container
    )

    # Desabilita commit automático para termos controle manual
    conn.autocommit = False

    yield conn

    # Fecha a conexão ao final do teste
    conn.close()


# ------------------------------------------------------
# FIXTURE DE CURSOR
# ------------------------------------------------------
@pytest.fixture
def db_cursor(db_connection):
    """
    Cria um cursor para executar comandos SQL.
    """
    cur = db_connection.cursor()
    yield cur
    cur.close()


# ------------------------------------------------------
# FIXTURE DE LIMPEZA
# ------------------------------------------------------
@pytest.fixture(autouse=True)
def rollback_after_test(db_connection):
    """
    Garante que cada teste seja desfeito ao final.

    Isso evita que os dados de teste fiquem acumulando no banco
    a cada execução do pytest.
    """
    yield
    db_connection.rollback()