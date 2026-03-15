"""
test_database.py

Testes de integração do schema do catálogo automotivo.

Este arquivo valida as principais estruturas do banco, cobrindo:
- reference
- discovery
- catalog
- compatibility
- publication

Observação importante:
A modelagem de veículos foi refatorada para usar a estrutura:

vehicle_brands -> vehicle_models -> vehicles

Por isso os testes agora inserem marcas e modelos explicitamente
antes de criar registros em reference.vehicles.
"""


# ------------------------------------------------------
# FUNÇÕES AUXILIARES
# ------------------------------------------------------
def insert_manufacturer(db_cursor, name, manufacturer_type="unknown"):
    """
    Insere um fabricante de peça e retorna o id criado.
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


def insert_vehicle_brand(db_cursor, name, normalized_name, fipe_brand_code=None):
    """
    Insere uma marca de veículo e retorna o id criado.
    """
    db_cursor.execute("""
        INSERT INTO reference.vehicle_brands (
            name,
            normalized_name,
            fipe_brand_code
        )
        VALUES (%s, %s, %s)
        RETURNING id
    """, (name, normalized_name, fipe_brand_code))

    return db_cursor.fetchone()[0]


def insert_vehicle_model(db_cursor, brand_id, name, normalized_name, fipe_model_code=None):
    """
    Insere um modelo de veículo e retorna o id criado.
    """
    db_cursor.execute("""
        INSERT INTO reference.vehicle_models (
            brand_id,
            name,
            normalized_name,
            fipe_model_code
        )
        VALUES (%s, %s, %s, %s)
        RETURNING id
    """, (brand_id, name, normalized_name, fipe_model_code))

    return db_cursor.fetchone()[0]


def insert_part(db_cursor, name, normalized_name, part_type_id, description=None, status="active"):
    """
    Insere uma peça consolidada no catálogo e retorna o id criado.
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
    fuel_type_id=None,
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
            fuel_type_id,
            aspiration,
            valve_count,
            power_hp,
            engine_family
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
    """, (
        code,
        description,
        displacement,
        fuel_type,
        fuel_type_id,
        aspiration,
        valve_count,
        power_hp,
        engine_family
    ))

    return db_cursor.fetchone()[0]


def insert_vehicle(
    db_cursor,
    model_id,
    model_year,
    version=None,
    brand_text=None,
    model_text=None,
    body_type=None,
    body_type_id=None,
    fuel_type=None,
    fuel_type_id=None,
    market="BR",
    fipe_vehicle_code=None
):
    """
    Insere um veículo e retorna o id criado.

    Observação:
    - model_id é a nova referência oficial
    - brand_text e model_text são mantidos temporariamente
      para compatibilidade e transição gradual
    """
    db_cursor.execute("""
        INSERT INTO reference.vehicles (
            model_id,
            brand_text,
            model_text,
            model_year,
            version,
            body_type,
            body_type_id,
            fuel_type,
            fuel_type_id,
            market,
            fipe_vehicle_code
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
    """, (
        model_id,
        brand_text,
        model_text,
        model_year,
        version,
        body_type,
        body_type_id,
        fuel_type,
        fuel_type_id,
        market,
        fipe_vehicle_code
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
# Inserção de marca de veículo
# ------------------------------------------------------
def test_insert_vehicle_brand(db_cursor):
    brand_id = insert_vehicle_brand(
        db_cursor,
        "Honda",
        "HONDA",
        "25"
    )

    assert brand_id is not None


# ------------------------------------------------------
# TESTE 5
# Inserção de modelo de veículo
# ------------------------------------------------------
def test_insert_vehicle_model(db_cursor):
    brand_id = insert_vehicle_brand(
        db_cursor,
        "Honda",
        "HONDA",
        "25"
    )

    model_id = insert_vehicle_model(
        db_cursor,
        brand_id,
        "Civic",
        "CIVIC",
        "4828"
    )

    assert model_id is not None


# ------------------------------------------------------
# TESTE 6
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
# TESTE 7
# Inserção de veículo com novo modelo brand->model->vehicle
# ------------------------------------------------------
def test_insert_vehicle(db_cursor):
    brand_id = insert_vehicle_brand(
        db_cursor,
        "Honda",
        "HONDA",
        "25"
    )

    model_id = insert_vehicle_model(
        db_cursor,
        brand_id,
        "Civic",
        "CIVIC",
        "4828"
    )

    vehicle_id = insert_vehicle(
        db_cursor,
        model_id=model_id,
        brand_text="Honda",
        model_text="Civic",
        model_year=2010,
        version="LXS",
        body_type="sedan",
        fuel_type="gasoline",
        market="BR",
        fipe_vehicle_code="2010-1"
    )

    assert vehicle_id is not None


# ------------------------------------------------------
# TESTE 8
# Relação entre veículo e motor
# ------------------------------------------------------
def test_vehicle_motor_relationship(db_cursor):
    # cria a estrutura marca -> modelo -> veículo
    brand_id = insert_vehicle_brand(
        db_cursor,
        "Honda",
        "HONDA",
        "25"
    )

    model_id = insert_vehicle_model(
        db_cursor,
        brand_id,
        "Civic",
        "CIVIC",
        "4828"
    )

    vehicle_id = insert_vehicle(
        db_cursor,
        model_id=model_id,
        brand_text="Honda",
        model_text="Civic",
        model_year=2011,
        version="LXL",
        body_type="sedan",
        fuel_type="gasoline",
        market="BR"
    )

    motor_id = insert_motor(
        db_cursor,
        code="R18_REL_TEST",
        description="Motor R18 para relacionamento",
        displacement=1.8,
        fuel_type="gasoline",
        aspiration="natural"
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
# TESTE 9
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
# TESTE 10
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
# TESTE 11
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
# TESTE 12
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
# TESTE 13
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
# TESTE 14
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
# TESTE 15
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
# TESTE 16
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
# TESTE 17
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
# TESTE 18
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
# TESTE 19
# Aplicação por veículo
# ------------------------------------------------------
def test_insert_application_by_vehicle(db_cursor):
    brand_id = insert_vehicle_brand(
        db_cursor,
        "Honda",
        "HONDA",
        "25"
    )

    model_id = insert_vehicle_model(
        db_cursor,
        brand_id,
        "Civic",
        "CIVIC",
        "4828"
    )

    vehicle_id = insert_vehicle(
        db_cursor,
        model_id=model_id,
        brand_text="Honda",
        model_text="Civic",
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
# TESTE 20
# Aplicação por veículo e motor
# ------------------------------------------------------
def test_insert_application_with_vehicle_and_motor(db_cursor):
    brand_id = insert_vehicle_brand(
        db_cursor,
        "Honda",
        "HONDA",
        "25"
    )

    model_id = insert_vehicle_model(
        db_cursor,
        brand_id,
        "Civic",
        "CIVIC",
        "4828"
    )

    vehicle_id = insert_vehicle(
        db_cursor,
        model_id=model_id,
        brand_text="Honda",
        model_text="Civic",
        model_year=2010,
        version="LXS",
        body_type="sedan",
        fuel_type="gasoline",
        market="BR"
    )

    motor_id = insert_motor(
        db_cursor,
        code="R18A1_APP_TEST",
        description="Motor Honda R18",
        displacement=1.8,
        fuel_type="gasoline",
        aspiration="natural"
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
# TESTE 21
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
# TESTE 22
# Fabricante OEM
# ------------------------------------------------------
def test_insert_oem_manufacturer(db_cursor):
    manufacturer_id = insert_manufacturer(
        db_cursor,
        "Honda OEM Test",
        "oem"
    )

    assert manufacturer_id is not None


# ------------------------------------------------------
# TESTE 23
# Inserção de regra de compatibilidade
# ------------------------------------------------------
def test_insert_compatibility_rule(db_cursor):
    db_cursor.execute("""
        INSERT INTO compatibility.rules (
            name,
            description,
            rule_type,
            rule_expression,
            priority,
            is_active
        )
        VALUES (%s, %s, %s, %s::jsonb, %s, %s)
        RETURNING id
    """, (
        "Regra por motor",
        "Valida compatibilidade por motor",
        "motor_match",
        '{"field": "motor_id", "operator": "equals"}',
        100,
        True
    ))

    rule_id = db_cursor.fetchone()[0]

    assert rule_id is not None


# ------------------------------------------------------
# TESTE 24
# Inserção de evidência de compatibilidade
# ------------------------------------------------------
def test_insert_compatibility_evidence(db_cursor):
    brand_id = insert_vehicle_brand(
        db_cursor,
        "Honda",
        "HONDA",
        "25"
    )

    model_id = insert_vehicle_model(
        db_cursor,
        brand_id,
        "Civic",
        "CIVIC",
        "4828"
    )

    vehicle_id = insert_vehicle(
        db_cursor,
        model_id=model_id,
        brand_text="Honda",
        model_text="Civic",
        model_year=2012
    )

    cluster_id = insert_cluster(
        db_cursor,
        name="Cluster compat evidence",
        cluster_type="consolidated"
    )

    application_id = insert_application_for_test(
        db_cursor,
        cluster_id=cluster_id,
        vehicle_id=vehicle_id
    )

    db_cursor.execute("""
        INSERT INTO compatibility.evidence (
            application_id,
            source,
            evidence_type,
            evidence_data,
            confidence_score
        )
        VALUES (%s, %s, %s, %s::jsonb, %s)
        RETURNING id
    """, (
        application_id,
        "pytest",
        "catalog_match",
        '{"source": "manual", "match": true}',
        0.920
    ))

    evidence_id = db_cursor.fetchone()[0]

    assert evidence_id is not None


# ------------------------------------------------------
# TESTE 25
# Inserção de decisão de compatibilidade
# ------------------------------------------------------
def test_insert_compatibility_decision(db_cursor):
    brand_id = insert_vehicle_brand(
        db_cursor,
        "Toyota",
        "TOYOTA",
        "39"
    )

    model_id = insert_vehicle_model(
        db_cursor,
        brand_id,
        "Corolla",
        "COROLLA",
        "5214"
    )

    vehicle_id = insert_vehicle(
        db_cursor,
        model_id=model_id,
        brand_text="Toyota",
        model_text="Corolla",
        model_year=2015
    )

    cluster_id = insert_cluster(
        db_cursor,
        name="Cluster compat decision",
        cluster_type="consolidated"
    )

    application_id = insert_application_for_test(
        db_cursor,
        cluster_id=cluster_id,
        vehicle_id=vehicle_id
    )

    db_cursor.execute("""
        INSERT INTO compatibility.rules (
            name,
            description,
            rule_type,
            rule_expression
        )
        VALUES (%s, %s, %s, %s::jsonb)
        RETURNING id
    """, (
        "Regra pytest decisão",
        "Regra para teste de decisão",
        "vehicle_match",
        '{"field": "vehicle_id", "operator": "equals"}'
    ))

    rule_id = db_cursor.fetchone()[0]

    db_cursor.execute("""
        INSERT INTO compatibility.decisions (
            application_id,
            rule_id,
            decision,
            confidence_score,
            notes
        )
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id
    """, (
        application_id,
        rule_id,
        "approved",
        0.970,
        "Decisão aprovada em teste"
    ))

    decision_id = db_cursor.fetchone()[0]

    assert decision_id is not None


# ------------------------------------------------------
# TESTE 26
# Inserção de batch de publicação
# ------------------------------------------------------
def test_insert_publication_batch(db_cursor):
    db_cursor.execute("""
        INSERT INTO publication.batches (
            status,
            notes
        )
        VALUES (%s, %s)
        RETURNING id
    """, (
        "running",
        "Batch iniciado em teste"
    ))

    batch_id = db_cursor.fetchone()[0]

    assert batch_id is not None


# ------------------------------------------------------
# TESTE 27
# Inserção de versão de catálogo
# ------------------------------------------------------
def test_insert_catalog_version(db_cursor):
    db_cursor.execute("""
        INSERT INTO publication.batches (
            status,
            notes
        )
        VALUES (%s, %s)
        RETURNING id
    """, (
        "completed",
        "Batch concluído em teste"
    ))

    batch_id = db_cursor.fetchone()[0]

    db_cursor.execute("""
        INSERT INTO publication.catalog_versions (
            version_number,
            batch_id,
            notes
        )
        VALUES (%s, %s, %s)
        RETURNING id
    """, (
        1,
        batch_id,
        "Primeira versão publicada em teste"
    ))

    version_id = db_cursor.fetchone()[0]

    assert version_id is not None


# ------------------------------------------------------
# TESTE 28
# Inserção de peça publicada
# ------------------------------------------------------
def test_insert_published_part(db_cursor):
    part_type_id = insert_part_type(
        db_cursor,
        "Filtro de Combustível",
        "FILTRO DE COMBUSTIVEL"
    )

    part_id = insert_part(
        db_cursor,
        name="Filtro de Combustível Test",
        normalized_name="FILTRO DE COMBUSTIVEL TEST",
        part_type_id=part_type_id
    )

    db_cursor.execute("""
        INSERT INTO publication.batches (
            status
        )
        VALUES (%s)
        RETURNING id
    """, ("completed",))

    batch_id = db_cursor.fetchone()[0]

    db_cursor.execute("""
        INSERT INTO publication.catalog_versions (
            version_number,
            batch_id
        )
        VALUES (%s, %s)
        RETURNING id
    """, (1, batch_id))

    version_id = db_cursor.fetchone()[0]

    db_cursor.execute("""
        INSERT INTO publication.published_parts (
            catalog_version_id,
            part_id
        )
        VALUES (%s, %s)
        RETURNING id
    """, (version_id, part_id))

    published_part_id = db_cursor.fetchone()[0]

    assert published_part_id is not None


# ------------------------------------------------------
# TESTE 29
# Inserção de aplicação publicada
# ------------------------------------------------------
def test_insert_published_application(db_cursor):
    brand_id = insert_vehicle_brand(
        db_cursor,
        "Honda",
        "HONDA",
        "25"
    )

    model_id = insert_vehicle_model(
        db_cursor,
        brand_id,
        "Fit",
        "FIT",
        "3310"
    )

    vehicle_id = insert_vehicle(
        db_cursor,
        model_id=model_id,
        brand_text="Honda",
        model_text="Fit",
        model_year=2014
    )

    cluster_id = insert_cluster(
        db_cursor,
        name="Cluster publicação aplicação",
        cluster_type="consolidated"
    )

    application_id = insert_application_for_test(
        db_cursor,
        cluster_id=cluster_id,
        vehicle_id=vehicle_id
    )

    db_cursor.execute("""
        INSERT INTO publication.batches (
            status
        )
        VALUES (%s)
        RETURNING id
    """, ("completed",))

    batch_id = db_cursor.fetchone()[0]

    db_cursor.execute("""
        INSERT INTO publication.catalog_versions (
            version_number,
            batch_id
        )
        VALUES (%s, %s)
        RETURNING id
    """, (1, batch_id))

    version_id = db_cursor.fetchone()[0]

    db_cursor.execute("""
        INSERT INTO publication.published_applications (
            catalog_version_id,
            application_id
        )
        VALUES (%s, %s)
        RETURNING id
    """, (version_id, application_id))

    published_application_id = db_cursor.fetchone()[0]

    assert published_application_id is not None


# ------------------------------------------------------
# FUNÇÃO AUXILIAR INTERNA
# ------------------------------------------------------
def insert_application_for_test(
    db_cursor,
    cluster_id,
    motor_id=None,
    vehicle_id=None,
    confidence_score=0.900
):
    """
    Função auxiliar usada pelos testes de compatibility e publication.

    Ela encapsula a criação mínima de uma aplicação válida
    no catálogo operacional.
    """
    db_cursor.execute("""
        INSERT INTO catalog.applications (
            cluster_id,
            motor_id,
            vehicle_id,
            confidence_score
        )
        VALUES (%s, %s, %s, %s)
        RETURNING id
    """, (cluster_id, motor_id, vehicle_id, confidence_score))

    return db_cursor.fetchone()[0]