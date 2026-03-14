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

    # Abre conexão com o banco
    conn = psycopg2.connect(
        host="localhost",      # endereço do banco
        database="catalogo",   # nome do banco criado no Docker
        user="admin",          # usuário definido no docker-compose
        password="admin",      # senha definida no docker-compose
        port=5432              # porta exposta pelo container
    )

    # Entrega a conexão para o teste
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

    Depende da fixture db_connection, ou seja, o pytest primeiro
    cria a conexão e depois cria o cursor.
    """

    # Cria cursor a partir da conexão
    cur = db_connection.cursor()

    # Entrega o cursor para o teste
    yield cur

    # Fecha o cursor ao final do teste
    cur.close()


# ------------------------------------------------------
# TESTE 1
# Inserção de fabricante
# ------------------------------------------------------
def test_insert_manufacturer(db_connection, db_cursor):
    """
    Verifica se é possível inserir um fabricante na tabela
    reference.manufacturers e obter o ID gerado pelo banco.
    """

    # Executa inserção de um fabricante de teste
    db_cursor.execute("""
        INSERT INTO reference.manufacturers (name)
        VALUES ('Test Manufacturer Fixture')
        RETURNING id
    """)

    # Captura o ID retornado pelo banco
    manufacturer_id = db_cursor.fetchone()[0]

    # Confirma a transação
    db_connection.commit()

    # Valida que o ID foi realmente gerado
    assert manufacturer_id is not None


# ------------------------------------------------------
# TESTE 2
# Inserção de motor
# ------------------------------------------------------
def test_insert_motor(db_connection, db_cursor):
    """
    Verifica se é possível inserir um motor na tabela
    reference.motors e obter o ID gerado.
    """

    # Executa inserção de um motor de teste
    db_cursor.execute("""
        INSERT INTO reference.motors (code, description)
        VALUES ('TEST_ENGINE_FIXTURE', 'Motor de teste com fixture')
        RETURNING id
    """)

    # Captura o ID criado
    motor_id = db_cursor.fetchone()[0]

    # Confirma a transação
    db_connection.commit()

    # Valida que o ID foi gerado
    assert motor_id is not None


# ------------------------------------------------------
# TESTE 3
# Consulta de fabricante inserido
# ------------------------------------------------------
def test_select_manufacturer(db_connection, db_cursor):
    """
    Insere um fabricante e depois consulta esse registro
    para validar que a leitura no banco também está funcionando.
    """

    # Insere fabricante de teste
    db_cursor.execute("""
        INSERT INTO reference.manufacturers (name)
        VALUES ('Manufacturer Select Test')
        RETURNING id
    """)

    manufacturer_id = db_cursor.fetchone()[0]

    # Confirma a inserção
    db_connection.commit()

    # Consulta o registro recém-criado
    db_cursor.execute("""
        SELECT id, name
        FROM reference.manufacturers
        WHERE id = %s
    """, (manufacturer_id,))

    result = db_cursor.fetchone()

    # Verifica se o resultado existe
    assert result is not None

    # Verifica se o ID retornado é o mesmo inserido
    assert result[0] == manufacturer_id

    # Verifica se o nome retornado é o esperado
    assert result[1] == 'Manufacturer Select Test'

