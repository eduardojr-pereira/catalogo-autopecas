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


# ------------------------------------------------------
# FUNÇÃO AUXILIAR
# INSERE UM FABRICANTE E RETORNA O ID
# ------------------------------------------------------
def insert_manufacturer(db_cursor, name):
    """
    Insere um fabricante na tabela reference.manufacturers
    e retorna o ID criado.
    """
    db_cursor.execute("""
        INSERT INTO reference.manufacturers (name)
        VALUES (%s)
        RETURNING id
    """, (name,))

    return db_cursor.fetchone()[0]


# ------------------------------------------------------
# TESTE 1
# Inserção de fabricante
# ------------------------------------------------------
def test_insert_manufacturer(db_cursor):
    """
    Verifica se é possível inserir um fabricante.
    """
    manufacturer_id = insert_manufacturer(db_cursor, "Bosch Test")

    assert manufacturer_id is not None


# ------------------------------------------------------
# TESTE 2
# Inserção de motor
# ------------------------------------------------------
def test_insert_motor(db_cursor):
    """
    Verifica se é possível inserir um motor na tabela reference.motors.
    """
    db_cursor.execute("""
        INSERT INTO reference.motors (code, description)
        VALUES (%s, %s)
        RETURNING id
    """, ("R18_TEST", "Motor Honda R18 de teste"))

    motor_id = db_cursor.fetchone()[0]

    assert motor_id is not None


# ------------------------------------------------------
# TESTE 3
# Inserção de código de peça
# ------------------------------------------------------
def test_insert_code(db_cursor):
    """
    Verifica se é possível inserir um código de peça em discovery.codes.
    """
    manufacturer_id = insert_manufacturer(db_cursor, "Mahle Test")

    db_cursor.execute("""
        INSERT INTO discovery.codes (manufacturer_id, code, normalized_code)
        VALUES (%s, %s, %s)
        RETURNING id
    """, (manufacturer_id, "OC-1196", "OC1196"))

    code_id = db_cursor.fetchone()[0]

    assert code_id is not None


# ------------------------------------------------------
# TESTE 4
# Inserção de equivalência entre códigos
# ------------------------------------------------------
def test_insert_code_equivalence(db_cursor):
    """
    Verifica se é possível registrar uma equivalência entre dois códigos.
    """
    bosch_id = insert_manufacturer(db_cursor, "Bosch Eq Test")
    mahle_id = insert_manufacturer(db_cursor, "Mahle Eq Test")

    # Insere o primeiro código
    db_cursor.execute("""
        INSERT INTO discovery.codes (manufacturer_id, code, normalized_code)
        VALUES (%s, %s, %s)
        RETURNING id
    """, (bosch_id, "0986AF0051", "0986AF0051"))

    code_1_id = db_cursor.fetchone()[0]

    # Insere o segundo código
    db_cursor.execute("""
        INSERT INTO discovery.codes (manufacturer_id, code, normalized_code)
        VALUES (%s, %s, %s)
        RETURNING id
    """, (mahle_id, "OC1196", "OC1196"))

    code_2_id = db_cursor.fetchone()[0]

    # Registra a equivalência entre os dois códigos
    db_cursor.execute("""
        INSERT INTO discovery.code_equivalences (code_id_1, code_id_2, source)
        VALUES (%s, %s, %s)
        RETURNING id
    """, (code_1_id, code_2_id, "pytest"))

    equivalence_id = db_cursor.fetchone()[0]

    assert equivalence_id is not None


# ------------------------------------------------------
# TESTE 5
# Inserção de cluster
# ------------------------------------------------------
def test_insert_cluster(db_cursor):
    """
    Verifica se é possível criar um cluster de peça.
    """
    db_cursor.execute("""
        INSERT INTO catalog.clusters (name)
        VALUES (%s)
        RETURNING id
    """, ("Filtro de óleo motor R18",))

    cluster_id = db_cursor.fetchone()[0]

    assert cluster_id is not None


# ------------------------------------------------------
# TESTE 6
# Ligação entre cluster e código
# ------------------------------------------------------
def test_link_code_to_cluster(db_cursor):
    """
    Verifica se é possível associar um código a um cluster.
    """
    manufacturer_id = insert_manufacturer(db_cursor, "Fram Test")

    # Insere código
    db_cursor.execute("""
        INSERT INTO discovery.codes (manufacturer_id, code, normalized_code)
        VALUES (%s, %s, %s)
        RETURNING id
    """, (manufacturer_id, "PH7317", "PH7317"))

    code_id = db_cursor.fetchone()[0]

    # Cria cluster
    db_cursor.execute("""
        INSERT INTO catalog.clusters (name)
        VALUES (%s)
        RETURNING id
    """, ("Cluster teste Fram",))

    cluster_id = db_cursor.fetchone()[0]

    # Liga o código ao cluster
    db_cursor.execute("""
        INSERT INTO catalog.cluster_codes (cluster_id, code_id)
        VALUES (%s, %s)
        RETURNING cluster_id, code_id
    """, (cluster_id, code_id))

    result = db_cursor.fetchone()

    assert result is not None
    assert result[0] == cluster_id
    assert result[1] == code_id


# ------------------------------------------------------
# TESTE 7
# Inserção de veículo
# ------------------------------------------------------
def test_insert_vehicle(db_cursor):
    """
    Verifica se é possível inserir um veículo na tabela reference.vehicles.
    """

    db_cursor.execute("""
        INSERT INTO reference.vehicles (brand, model, year)
        VALUES (%s, %s, %s)
        RETURNING id
    """, ("Honda", "Civic Test", 2010))

    vehicle_id = db_cursor.fetchone()[0]

    assert vehicle_id is not None


# ------------------------------------------------------
# TESTE 8
# Ligação entre veículo e motor
# ------------------------------------------------------
def test_vehicle_motor_relationship(db_cursor):
    """
    Verifica se conseguimos relacionar um veículo com um motor
    usando a tabela reference.vehicle_motors.
    """

    # insere motor
    db_cursor.execute("""
        INSERT INTO reference.motors (code, description)
        VALUES (%s, %s)
        RETURNING id
    """, ("R18_REL_TEST", "Motor R18 para relacionamento"))

    motor_id = db_cursor.fetchone()[0]

    # insere veículo
    db_cursor.execute("""
        INSERT INTO reference.vehicles (brand, model, year)
        VALUES (%s, %s, %s)
        RETURNING id
    """, ("Honda", "Civic Relationship Test", 2011))

    vehicle_id = db_cursor.fetchone()[0]

    # cria relação veículo → motor
    db_cursor.execute("""
        INSERT INTO reference.vehicle_motors (vehicle_id, motor_id)
        VALUES (%s, %s)
        RETURNING vehicle_id, motor_id
    """, (vehicle_id, motor_id))

    result = db_cursor.fetchone()

    assert result is not None
    assert result[0] == vehicle_id
    assert result[1] == motor_id


# ------------------------------------------------------
# TESTE 9
# Aplicação de cluster em motor
# ------------------------------------------------------
def test_cluster_application(db_cursor):
    """
    Verifica se um cluster de peça pode ser associado
    a um motor na tabela catalog.applications.
    """

    # cria motor
    db_cursor.execute("""
        INSERT INTO reference.motors (code, description)
        VALUES (%s, %s)
        RETURNING id
    """, ("R18_APP_TEST", "Motor para teste de aplicação"))

    motor_id = db_cursor.fetchone()[0]

    # cria cluster
    db_cursor.execute("""
        INSERT INTO catalog.clusters (name)
        VALUES (%s)
        RETURNING id
    """, ("Cluster teste aplicação",))

    cluster_id = db_cursor.fetchone()[0]

    # cria aplicação cluster → motor
    db_cursor.execute("""
        INSERT INTO catalog.applications (cluster_id, motor_id)
        VALUES (%s, %s)
        RETURNING cluster_id, motor_id
    """, (cluster_id, motor_id))

    result = db_cursor.fetchone()

    assert result is not None
    assert result[0] == cluster_id
    assert result[1] == motor_id