"""
test_database.py

Testes de integração do schema refatorado do catálogo automotivo.
Cobre as principais tabelas dos schemas:

- reference
- discovery
- catalog
"""


# ------------------------------------------------------
# FUNÇÕES AUXILIARES
# ------------------------------------------------------
def insert_manufacturer(db_cursor, name, manufacturer_type="unknown"):
    """
    Insere um fabricante e retorna o id criado.
    """
    db_cursor.execute("""
        INSERT INTO reference.manufacturers (
            name,
            manufacturer_type
        )
        VALUES (%s, %s)
        RETURNING id
    """, (name, manufacturer_type))

    return db_cursor.fetchone()[0]


def insert_part_type(db_cursor, name, normalized_name, description=None):
    """
    Insere um tipo de peça e retorna o id criado.
    """
    db_cursor.execute("""
        INSERT INTO reference.part_types (
            name,
            normalized_name,
            description
        )
        VALUES (%s, %s, %s)
        RETURNING id
    """, (name, normalized_name, description))

    return db_cursor.fetchone()[0]


def insert_part(db_cursor, name, normalized_name, part_type_id, description=None, status="active"):
    """
    Insere uma peça consolidada e retorna o id criado.
    """
    db_cursor.execute("""
        INSERT INTO catalog.parts (
            name,
            normalized_name,
            part_type_id,
            description,
            status
        )
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id
    """, (name, normalized_name, part_type_id, description, status))

    return db_cursor.fetchone()[0]


def insert_cluster(db_cursor, name, cluster_type="discovery", part_id=None):
    """
    Insere um cluster e retorna o id criado.
    """
    db_cursor.execute("""
        INSERT INTO catalog.clusters (
            part_id,
            name,
            cluster_type
        )
        VALUES (%s, %s, %s)
        RETURNING id
    """, (part_id, name, cluster_type))

    return db_cursor.fetchone()[0]


def insert_motor(
    db_cursor,
    code,
    description,
    displacement=None,
    fuel_type=None,
    aspiration=None,
    valve_count=None,
    power_hp=None,
    engine_family=None
):
    """
    Insere um motor e retorna o id criado.
    """
    db_cursor.execute("""
        INSERT INTO reference.motors (
            code,
            description,
            displacement,
            fuel_type,
            aspiration,
            valve_count,
            power_hp,
            engine_family
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
    """, (
        code,
        description,
        displacement,
        fuel_type,
        aspiration,
        valve_count,
        power_hp,
        engine_family
    ))

    return db_cursor.fetchone()[0]


def insert_vehicle(
    db_cursor,
    brand,
    model,
    model_year,
    version=None,
    body_type=None,
    fuel_type=None,
    market="BR"
):
    """
    Insere um veículo e retorna o id criado.
    """
    db_cursor.execute("""
        INSERT INTO reference.vehicles (
            brand,
            model,
            model_year,
            version,
            body_type,
            fuel_type,
            market
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING id
    """, (
        brand,
        model,
        model_year,
        version,
        body_type,
        fuel_type,
        market
    ))

    return db_cursor.fetchone()[0]


def insert_source(
    db_cursor,
    name,
    source_type="unknown",
    base_url=None,
    notes=None
):
    """
    Insere uma fonte de descoberta e retorna o id criado.
    """
    db_cursor.execute("""
        INSERT INTO discovery.sources (
            name,
            source_type,
            base_url,
            notes
        )
        VALUES (%s, %s, %s, %s)
        RETURNING id
    """, (
        name,
        source_type,
        base_url,
        notes
    ))

    return db_cursor.fetchone()[0]


def insert_code(db_cursor, manufacturer_id, code, normalized_code):
    """
    Insere um código em discovery.codes e retorna o id criado.
    """
    db_cursor.execute("""
        INSERT INTO discovery.codes (
            manufacturer_id,
            code,
            normalized_code
        )
        VALUES (%s, %s, %s)
        RETURNING id
    """, (manufacturer_id, code, normalized_code))

    return db_cursor.fetchone()[0]


# ------------------------------------------------------
# TESTE 1
# Inserção de fabricante com tipo
# ------------------------------------------------------
def test_insert_manufacturer(db_cursor):
    manufacturer_id = insert_manufacturer(
        db_cursor,
        "Bosch Test",
        "aftermarket"
    )

    assert manufacturer_id is not None


# ------------------------------------------------------
# TESTE 2
# Inserção de tipo de peça
# ------------------------------------------------------
def test_insert_part_type(db_cursor):
    part_type_id = insert_part_type(
        db_cursor,
        "Filtro de Óleo",
        "FILTRO DE OLEO",
        "Elemento de filtragem do óleo do motor"
    )

    assert part_type_id is not None


# ------------------------------------------------------
# TESTE 3
# Inserção de alias de tipo de peça
# ------------------------------------------------------
def test_insert_part_type_alias(db_cursor):
    part_type_id = insert_part_type(
        db_cursor,
        "Filtro de Óleo",
        "FILTRO DE OLEO"
    )

    db_cursor.execute("""
        INSERT INTO reference.part_type_aliases (
            part_type_id,
            alias,
            normalized_alias
        )
        VALUES (%s, %s, %s)
        RETURNING id
    """, (
        part_type_id,
        "Filtro Óleo",
        "FILTRO OLEO"
    ))

    alias_id = db_cursor.fetchone()[0]

    assert alias_id is not None


# ------------------------------------------------------
# TESTE 4
# Inserção de motor com atributos técnicos
# ------------------------------------------------------
def test_insert_motor(db_cursor):
    motor_id = insert_motor(
        db_cursor,
        code="R18A1_TEST",
        description="Motor Honda R18 de teste",
        displacement=1.8,
        fuel_type="gasoline",
        aspiration="natural",
        valve_count=16,
        power_hp=140,
        engine_family="R18"
    )

    assert motor_id is not None


# ------------------------------------------------------
# TESTE 5
# Inserção de veículo enriquecido
# ------------------------------------------------------
def test_insert_vehicle(db_cursor):
    vehicle_id = insert_vehicle(
        db_cursor,
        brand="Honda",
        model="Civic",
        model_year=2010,
        version="LXS",
        body_type="sedan",
        fuel_type="gasoline",
        market="BR"
    )

    assert vehicle_id is not None


# ------------------------------------------------------
# TESTE 6
# Relação entre veículo e motor
# ------------------------------------------------------
def test_vehicle_motor_relationship(db_cursor):
    motor_id = insert_motor(
        db_cursor,
        code="R18_REL_TEST",
        description="Motor R18 para relacionamento",
        displacement=1.8,
        fuel_type="gasoline",
        aspiration="natural"
    )

    vehicle_id = insert_vehicle(
        db_cursor,
        brand="Honda",
        model="Civic",
        model_year=2011,
        version="LXL",
        body_type="sedan",
        fuel_type="gasoline",
        market="BR"
    )

    db_cursor.execute("""
        INSERT INTO reference.vehicle_motors (
            vehicle_id,
            motor_id
        )
        VALUES (%s, %s)
        RETURNING vehicle_id, motor_id
    """, (vehicle_id, motor_id))

    result = db_cursor.fetchone()

    assert result is not None
    assert result[0] == vehicle_id
    assert result[1] == motor_id


# ------------------------------------------------------
# TESTE 7
# Inserção de fonte de descoberta
# ------------------------------------------------------
def test_insert_source(db_cursor):
    source_id = insert_source(
        db_cursor,
        name="Catálogo Bosch Test",
        source_type="catalog",
        base_url="https://example.com/bosch",
        notes="Fonte de teste"
    )

    assert source_id is not None


# ------------------------------------------------------
# TESTE 8
# Inserção de código de peça
# ------------------------------------------------------
def test_insert_code(db_cursor):
    manufacturer_id = insert_manufacturer(
        db_cursor,
        "Mahle Test",
        "aftermarket"
    )

    code_id = insert_code(
        db_cursor,
        manufacturer_id,
        "OC-1196",
        "OC1196"
    )

    assert code_id is not None


# ------------------------------------------------------
# TESTE 9
# Inserção de evidência de código
# ------------------------------------------------------
def test_insert_code_evidence(db_cursor):
    manufacturer_id = insert_manufacturer(
        db_cursor,
        "Fram Evidence Test",
        "aftermarket"
    )

    source_id = insert_source(
        db_cursor,
        name="Marketplace Test",
        source_type="marketplace",
        base_url="https://example.com/marketplace"
    )

    code_id = insert_code(
        db_cursor,
        manufacturer_id,
        "PH7317",
        "PH7317"
    )

    db_cursor.execute("""
        INSERT INTO discovery.code_evidence (
            code_id,
            source_id,
            source_url,
            raw_text
        )
        VALUES (%s, %s, %s, %s)
        RETURNING id
    """, (
        code_id,
        source_id,
        "https://example.com/marketplace/ph7317",
        "Código PH7317 encontrado em página de produto"
    ))

    evidence_id = db_cursor.fetchone()[0]

    assert evidence_id is not None


# ------------------------------------------------------
# TESTE 10
# Inserção de equivalência entre códigos
# ------------------------------------------------------
def test_insert_code_equivalence(db_cursor):
    bosch_id = insert_manufacturer(
        db_cursor,
        "Bosch Eq Test",
        "aftermarket"
    )
    mahle_id = insert_manufacturer(
        db_cursor,
        "Mahle Eq Test",
        "aftermarket"
    )

    code_1_id = insert_code(
        db_cursor,
        bosch_id,
        "0986AF0051",
        "0986AF0051"
    )

    code_2_id = insert_code(
        db_cursor,
        mahle_id,
        "OC1196",
        "OC1196"
    )

    db_cursor.execute("""
        INSERT INTO discovery.code_equivalences (
            code_id_1,
            code_id_2,
            source,
            equivalence_type,
            validation_status,
            confidence_score,
            notes
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING id
    """, (
        code_1_id,
        code_2_id,
        "pytest",
        "cross_reference",
        "discovered",
        0.850,
        "Equivalência de teste"
    ))

    equivalence_id = db_cursor.fetchone()[0]

    assert equivalence_id is not None


# ------------------------------------------------------
# TESTE 11
# Inserção de peça consolidada
# ------------------------------------------------------
def test_insert_part(db_cursor):
    part_type_id = insert_part_type(
        db_cursor,
        "Filtro de Óleo",
        "FILTRO DE OLEO"
    )

    part_id = insert_part(
        db_cursor,
        name="Filtro de Óleo Motor Honda R18",
        normalized_name="FILTRO DE OLEO MOTOR HONDA R18",
        part_type_id=part_type_id,
        description="Peça consolidada para motor Honda R18",
        status="active"
    )

    assert part_id is not None


# ------------------------------------------------------
# TESTE 12
# Inserção de atributo técnico da peça
# ------------------------------------------------------
def test_insert_part_attribute(db_cursor):
    part_type_id = insert_part_type(
        db_cursor,
        "Filtro de Óleo",
        "FILTRO DE OLEO"
    )

    part_id = insert_part(
        db_cursor,
        name="Filtro de Óleo Motor Honda R18",
        normalized_name="FILTRO DE OLEO MOTOR HONDA R18",
        part_type_id=part_type_id
    )

    db_cursor.execute("""
        INSERT INTO catalog.part_attributes (
            part_id,
            attribute_name,
            attribute_value,
            unit,
            source
        )
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id
    """, (
        part_id,
        "altura",
        "85",
        "mm",
        "manual"
    ))

    attribute_id = db_cursor.fetchone()[0]

    assert attribute_id is not None


# ------------------------------------------------------
# TESTE 13
# Inserção de cluster discovery
# ------------------------------------------------------
def test_insert_discovery_cluster(db_cursor):
    cluster_id = insert_cluster(
        db_cursor,
        name="Cluster descoberta filtro óleo",
        cluster_type="discovery"
    )

    assert cluster_id is not None


# ------------------------------------------------------
# TESTE 14
# Inserção de cluster consolidated vinculado à peça
# ------------------------------------------------------
def test_insert_consolidated_cluster_linked_to_part(db_cursor):
    part_type_id = insert_part_type(
        db_cursor,
        "Filtro de Óleo",
        "FILTRO DE OLEO"
    )

    part_id = insert_part(
        db_cursor,
        name="Filtro de Óleo Motor Honda R18",
        normalized_name="FILTRO DE OLEO MOTOR HONDA R18",
        part_type_id=part_type_id
    )

    cluster_id = insert_cluster(
        db_cursor,
        name="Cluster consolidado filtro óleo Honda R18",
        cluster_type="consolidated",
        part_id=part_id
    )

    assert cluster_id is not None


# ------------------------------------------------------
# TESTE 15
# Ligação entre cluster e código
# ------------------------------------------------------
def test_link_code_to_cluster(db_cursor):
    manufacturer_id = insert_manufacturer(
        db_cursor,
        "Fram Cluster Test",
        "aftermarket"
    )

    code_id = insert_code(
        db_cursor,
        manufacturer_id,
        "PH7317",
        "PH7317"
    )

    cluster_id = insert_cluster(
        db_cursor,
        name="Cluster teste Fram",
        cluster_type="discovery"
    )

    db_cursor.execute("""
        INSERT INTO catalog.cluster_codes (
            cluster_id,
            code_id
        )
        VALUES (%s, %s)
        RETURNING cluster_id, code_id
    """, (cluster_id, code_id))

    result = db_cursor.fetchone()

    assert result is not None
    assert result[0] == cluster_id
    assert result[1] == code_id


# ------------------------------------------------------
# TESTE 16
# Aplicação por motor
# ------------------------------------------------------
def test_insert_application_by_motor(db_cursor):
    motor_id = insert_motor(
        db_cursor,
        code="R18_APP_MOTOR_TEST",
        description="Motor para teste de aplicação por motor",
        displacement=1.8,
        fuel_type="gasoline"
    )

    cluster_id = insert_cluster(
        db_cursor,
        name="Cluster aplicação por motor",
        cluster_type="consolidated"
    )

    db_cursor.execute("""
        INSERT INTO catalog.applications (
            cluster_id,
            motor_id,
            position,
            side,
            notes,
            source,
            confidence_score
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING id
    """, (
        cluster_id,
        motor_id,
        "front",
        "both",
        "Aplicação por motor de teste",
        "pytest",
        0.900
    ))

    application_id = db_cursor.fetchone()[0]

    assert application_id is not None


# ------------------------------------------------------
# TESTE 17
# Aplicação por veículo
# ------------------------------------------------------
def test_insert_application_by_vehicle(db_cursor):
    vehicle_id = insert_vehicle(
        db_cursor,
        brand="Honda",
        model="Civic",
        model_year=2010,
        version="LXS",
        body_type="sedan",
        fuel_type="gasoline",
        market="BR"
    )

    cluster_id = insert_cluster(
        db_cursor,
        name="Cluster aplicação por veículo",
        cluster_type="consolidated"
    )

    db_cursor.execute("""
        INSERT INTO catalog.applications (
            cluster_id,
            vehicle_id,
            notes,
            source,
            confidence_score
        )
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id
    """, (
        cluster_id,
        vehicle_id,
        "Aplicação por veículo de teste",
        "pytest",
        0.880
    ))

    application_id = db_cursor.fetchone()[0]

    assert application_id is not None


# ------------------------------------------------------
# TESTE 18
# Aplicação por veículo e motor
# ------------------------------------------------------
def test_insert_application_with_vehicle_and_motor(db_cursor):
    motor_id = insert_motor(
        db_cursor,
        code="R18A1_APP_TEST",
        description="Motor Honda R18",
        displacement=1.8,
        fuel_type="gasoline",
        aspiration="natural"
    )

    vehicle_id = insert_vehicle(
        db_cursor,
        brand="Honda",
        model="Civic",
        model_year=2010,
        version="LXS",
        body_type="sedan",
        fuel_type="gasoline",
        market="BR"
    )

    cluster_id = insert_cluster(
        db_cursor,
        name="Cluster filtro óleo Honda R18",
        cluster_type="consolidated"
    )

    db_cursor.execute("""
        INSERT INTO catalog.applications (
            cluster_id,
            motor_id,
            vehicle_id,
            position,
            side,
            notes,
            source,
            confidence_score
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
    """, (
        cluster_id,
        motor_id,
        vehicle_id,
        "front",
        "both",
        "Aplicação validada para catálogo consolidado",
        "pytest",
        0.950
    ))

    application_id = db_cursor.fetchone()[0]

    assert application_id is not None


# ------------------------------------------------------
# TESTE 19
# Vincular peça a cluster via update
# ------------------------------------------------------
def test_link_part_to_existing_cluster(db_cursor):
    part_type_id = insert_part_type(
        db_cursor,
        "Pastilha de Freio",
        "PASTILHA DE FREIO"
    )

    part_id = insert_part(
        db_cursor,
        name="Pastilha de Freio Dianteira Civic",
        normalized_name="PASTILHA DE FREIO DIANTEIRA CIVIC",
        part_type_id=part_type_id
    )

    cluster_id = insert_cluster(
        db_cursor,
        name="Cluster sem peça vinculada",
        cluster_type="consolidated"
    )

    db_cursor.execute("""
        UPDATE catalog.clusters
        SET part_id = %s
        WHERE id = %s
        RETURNING part_id
    """, (part_id, cluster_id))

    result = db_cursor.fetchone()

    assert result is not None
    assert result[0] == part_id


# ------------------------------------------------------
# TESTE 20
# Fabricante OEM
# ------------------------------------------------------
def test_insert_oem_manufacturer(db_cursor):
    manufacturer_id = insert_manufacturer(
        db_cursor,
        "Honda OEM Test",
        "oem"
    )

    assert manufacturer_id is not None