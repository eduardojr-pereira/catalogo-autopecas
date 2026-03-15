/*
===============================================================================
CATÁLOGO AUTOMOTIVO INTELIGENTE
DATABASE SCHEMA
===============================================================================

Este arquivo define a estrutura completa do banco de dados do projeto.

O banco está organizado em cinco camadas principais:

reference
    Dados estruturais e vocabulários controlados.

discovery
    Dados descobertos durante coleta e enriquecimento.

catalog
    Catálogo operacional consolidado.

compatibility
    Motor de decisão técnica de compatibilidade.

publication
    Versionamento e publicação do catálogo.

Observação importante:
Este schema foi refatorado para suportar a estrutura:

vehicle_brands -> vehicle_models -> vehicles

Essa modelagem é mais compatível com a futura integração com a API da
Tabela FIPE, que será usada como fonte de marcas, modelos e veículos.

===============================================================================
*/


/*
===============================================================================
CRIAÇÃO DOS SCHEMAS
===============================================================================
*/
CREATE SCHEMA IF NOT EXISTS reference;
CREATE SCHEMA IF NOT EXISTS discovery;
CREATE SCHEMA IF NOT EXISTS catalog;
CREATE SCHEMA IF NOT EXISTS compatibility;
CREATE SCHEMA IF NOT EXISTS publication;



/*
===============================================================================
REFERENCE SCHEMA
===============================================================================
*/


/*
-------------------------------------------------------------------------------
Fabricantes de peças

Exemplos:
- Honda
- Bosch
- Mahle
- NGK
-------------------------------------------------------------------------------
*/
CREATE TABLE reference.manufacturers (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    manufacturer_type TEXT NOT NULL DEFAULT 'unknown',
    country TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CHECK (manufacturer_type IN ('oem', 'aftermarket', 'marketplace', 'unknown'))
);

CREATE INDEX idx_manufacturers_type
ON reference.manufacturers(manufacturer_type);


/*
-------------------------------------------------------------------------------
Tipos de peça

Exemplos:
- Filtro de Óleo
- Vela de Ignição
- Pastilha de Freio
-------------------------------------------------------------------------------
*/
CREATE TABLE reference.part_types (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    normalized_name TEXT NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_part_types_normalized_name
ON reference.part_types(normalized_name);


/*
-------------------------------------------------------------------------------
Aliases de tipos de peça

Permite busca comercial por variações do nome técnico.
-------------------------------------------------------------------------------
*/
CREATE TABLE reference.part_type_aliases (
    id SERIAL PRIMARY KEY,
    part_type_id INTEGER NOT NULL,
    alias TEXT NOT NULL,
    normalized_alias TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (part_type_id)
        REFERENCES reference.part_types(id)
        ON DELETE CASCADE
);

CREATE UNIQUE INDEX idx_part_type_aliases_unique
ON reference.part_type_aliases(part_type_id, normalized_alias);

CREATE INDEX idx_part_type_aliases_normalized_alias
ON reference.part_type_aliases(normalized_alias);


/*
-------------------------------------------------------------------------------
Domínio canônico: posição
-------------------------------------------------------------------------------
*/
CREATE TABLE reference.position_types (
    id SERIAL PRIMARY KEY,
    code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_position_types_code
ON reference.position_types(code);


/*
-------------------------------------------------------------------------------
Domínio canônico: lado
-------------------------------------------------------------------------------
*/
CREATE TABLE reference.side_types (
    id SERIAL PRIMARY KEY,
    code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_side_types_code
ON reference.side_types(code);


/*
-------------------------------------------------------------------------------
Domínio canônico: combustível
-------------------------------------------------------------------------------
*/
CREATE TABLE reference.fuel_types (
    id SERIAL PRIMARY KEY,
    code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_fuel_types_code
ON reference.fuel_types(code);


/*
-------------------------------------------------------------------------------
Domínio canônico: carroceria
-------------------------------------------------------------------------------
*/
CREATE TABLE reference.body_types (
    id SERIAL PRIMARY KEY,
    code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_body_types_code
ON reference.body_types(code);


/*
-------------------------------------------------------------------------------
Domínio canônico: unidades de atributos
-------------------------------------------------------------------------------
*/
CREATE TABLE reference.attribute_units (
    id SERIAL PRIMARY KEY,
    code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    symbol TEXT NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_attribute_units_code
ON reference.attribute_units(code);


/*
-------------------------------------------------------------------------------
Domínio canônico: definições de atributos técnicos
-------------------------------------------------------------------------------
*/
CREATE TABLE reference.attribute_definitions (
    id SERIAL PRIMARY KEY,
    code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    description TEXT,
    data_type TEXT NOT NULL DEFAULT 'text',
    default_unit_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (default_unit_id)
        REFERENCES reference.attribute_units(id)
        ON DELETE SET NULL,

    CHECK (data_type IN ('text', 'integer', 'numeric', 'boolean'))
);

CREATE INDEX idx_attribute_definitions_code
ON reference.attribute_definitions(code);

CREATE INDEX idx_attribute_definitions_default_unit
ON reference.attribute_definitions(default_unit_id);


/*
-------------------------------------------------------------------------------
Marcas de veículos

Esta tabela foi criada para suportar melhor a integração com a API da FIPE.

Exemplos:
- Honda
- Toyota
- Fiat
-------------------------------------------------------------------------------
*/
CREATE TABLE reference.vehicle_brands (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    normalized_name TEXT NOT NULL UNIQUE,
    fipe_brand_code TEXT UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_vehicle_brands_normalized_name
ON reference.vehicle_brands(normalized_name);

CREATE INDEX idx_vehicle_brands_fipe_brand_code
ON reference.vehicle_brands(fipe_brand_code);


/*
-------------------------------------------------------------------------------
Modelos de veículos

Cada modelo pertence a uma marca.

Exemplos:
- Civic
- Corolla
- Gol
-------------------------------------------------------------------------------
*/
CREATE TABLE reference.vehicle_models (
    id SERIAL PRIMARY KEY,
    brand_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    normalized_name TEXT NOT NULL,
    fipe_model_code TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (brand_id)
        REFERENCES reference.vehicle_brands(id)
        ON DELETE CASCADE
);

CREATE UNIQUE INDEX idx_vehicle_models_unique
ON reference.vehicle_models(brand_id, normalized_name);

CREATE INDEX idx_vehicle_models_fipe_model_code
ON reference.vehicle_models(fipe_model_code);

CREATE INDEX idx_vehicle_models_brand_id
ON reference.vehicle_models(brand_id);


/*
-------------------------------------------------------------------------------
Veículos

Representa a configuração/versionamento do veículo.

Compatibilidade temporária:
- mantém brand_text e model_text para transição gradual
- a nova referência oficial é model_id
-------------------------------------------------------------------------------
*/
CREATE TABLE reference.vehicles (
    id SERIAL PRIMARY KEY,

    model_id INTEGER,

    brand_text TEXT,
    model_text TEXT,

    model_year INTEGER NOT NULL,
    version TEXT,

    body_type TEXT,
    body_type_id INTEGER,

    fuel_type TEXT,
    fuel_type_id INTEGER,

    market TEXT NOT NULL DEFAULT 'BR',

    fipe_vehicle_code TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (model_id)
        REFERENCES reference.vehicle_models(id)
        ON DELETE SET NULL,

    FOREIGN KEY (body_type_id)
        REFERENCES reference.body_types(id)
        ON DELETE SET NULL,

    FOREIGN KEY (fuel_type_id)
        REFERENCES reference.fuel_types(id)
        ON DELETE SET NULL
);

CREATE INDEX idx_vehicles_model_id
ON reference.vehicles(model_id);

CREATE INDEX idx_vehicles_model_year
ON reference.vehicles(model_year);

CREATE INDEX idx_vehicles_fipe_vehicle_code
ON reference.vehicles(fipe_vehicle_code);

CREATE INDEX idx_vehicles_brand_model_text
ON reference.vehicles(brand_text, model_text, model_year);

CREATE INDEX idx_vehicles_body_type_id
ON reference.vehicles(body_type_id);

CREATE INDEX idx_vehicles_fuel_type_id
ON reference.vehicles(fuel_type_id);


/*
-------------------------------------------------------------------------------
Motores
-------------------------------------------------------------------------------
*/
CREATE TABLE reference.motors (
    id SERIAL PRIMARY KEY,
    code TEXT NOT NULL UNIQUE,
    description TEXT,
    displacement NUMERIC(5,2),
    fuel_type TEXT,
    fuel_type_id INTEGER,
    aspiration TEXT,
    valve_count INTEGER,
    power_hp NUMERIC(6,2),
    engine_family TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (fuel_type_id)
        REFERENCES reference.fuel_types(id)
        ON DELETE SET NULL
);

CREATE INDEX idx_motors_engine_family
ON reference.motors(engine_family);

CREATE INDEX idx_motors_fuel_type
ON reference.motors(fuel_type);

CREATE INDEX idx_motors_fuel_type_id
ON reference.motors(fuel_type_id);


/*
-------------------------------------------------------------------------------
Relacionamento veículo ↔ motor
-------------------------------------------------------------------------------
*/
CREATE TABLE reference.vehicle_motors (
    vehicle_id INTEGER NOT NULL,
    motor_id INTEGER NOT NULL,

    PRIMARY KEY (vehicle_id, motor_id),

    FOREIGN KEY (vehicle_id)
        REFERENCES reference.vehicles(id)
        ON DELETE CASCADE,

    FOREIGN KEY (motor_id)
        REFERENCES reference.motors(id)
        ON DELETE CASCADE
);

CREATE INDEX idx_vehicle_motors_motor
ON reference.vehicle_motors(motor_id);



/*
===============================================================================
DISCOVERY SCHEMA
===============================================================================
*/


CREATE TABLE discovery.sources (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    source_type TEXT NOT NULL DEFAULT 'unknown',
    base_url TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CHECK (source_type IN ('site', 'catalog', 'marketplace', 'api', 'spreadsheet', 'manual', 'unknown'))
);

CREATE INDEX idx_sources_type
ON discovery.sources(source_type);


CREATE TABLE discovery.codes (
    id SERIAL PRIMARY KEY,
    manufacturer_id INTEGER NOT NULL,
    code TEXT NOT NULL,
    normalized_code TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (manufacturer_id)
        REFERENCES reference.manufacturers(id)
        ON DELETE RESTRICT
);

CREATE INDEX idx_codes_normalized
ON discovery.codes(normalized_code);

CREATE UNIQUE INDEX idx_codes_unique
ON discovery.codes(manufacturer_id, normalized_code);

CREATE INDEX idx_codes_manufacturer
ON discovery.codes(manufacturer_id);


CREATE TABLE discovery.code_evidence (
    id SERIAL PRIMARY KEY,
    code_id INTEGER NOT NULL,
    source_id INTEGER,
    source_url TEXT,
    raw_text TEXT,
    collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (code_id)
        REFERENCES discovery.codes(id)
        ON DELETE CASCADE,

    FOREIGN KEY (source_id)
        REFERENCES discovery.sources(id)
        ON DELETE SET NULL
);

CREATE INDEX idx_code_evidence_code_id
ON discovery.code_evidence(code_id);

CREATE INDEX idx_code_evidence_source_id
ON discovery.code_evidence(source_id);

CREATE INDEX idx_code_evidence_collected_at
ON discovery.code_evidence(collected_at);


CREATE TABLE discovery.code_equivalences (
    id SERIAL PRIMARY KEY,

    code_id_1 INTEGER NOT NULL,
    code_id_2 INTEGER NOT NULL,

    source TEXT,
    equivalence_type TEXT NOT NULL DEFAULT 'suspected',
    validation_status TEXT NOT NULL DEFAULT 'discovered',
    confidence_score NUMERIC(4,3) NOT NULL DEFAULT 0.500,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (code_id_1)
        REFERENCES discovery.codes(id)
        ON DELETE CASCADE,

    FOREIGN KEY (code_id_2)
        REFERENCES discovery.codes(id)
        ON DELETE CASCADE,

    CHECK (code_id_1 <> code_id_2),
    CHECK (confidence_score >= 0.000 AND confidence_score <= 1.000),
    CHECK (equivalence_type IN ('commercial', 'technical', 'cross_reference', 'suspected')),
    CHECK (validation_status IN ('discovered', 'validated', 'rejected'))
);

CREATE INDEX idx_equiv_code1
ON discovery.code_equivalences(code_id_1);

CREATE INDEX idx_equiv_code2
ON discovery.code_equivalences(code_id_2);

CREATE INDEX idx_equiv_validation_status
ON discovery.code_equivalences(validation_status);

CREATE INDEX idx_equiv_type
ON discovery.code_equivalences(equivalence_type);

CREATE INDEX idx_equiv_confidence
ON discovery.code_equivalences(confidence_score);

CREATE UNIQUE INDEX idx_equiv_unique_pair
ON discovery.code_equivalences (
    LEAST(code_id_1, code_id_2),
    GREATEST(code_id_1, code_id_2)
);



/*
===============================================================================
CATALOG SCHEMA
===============================================================================
*/


CREATE TABLE catalog.parts (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    normalized_name TEXT NOT NULL,
    part_type_id INTEGER NOT NULL,
    description TEXT,
    status TEXT NOT NULL DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (part_type_id)
        REFERENCES reference.part_types(id)
        ON DELETE RESTRICT,

    CHECK (status IN ('active', 'review', 'discontinued'))
);

CREATE INDEX idx_parts_normalized_name
ON catalog.parts(normalized_name);

CREATE INDEX idx_parts_part_type
ON catalog.parts(part_type_id);

CREATE INDEX idx_parts_status
ON catalog.parts(status);


CREATE TABLE catalog.part_attributes (
    id SERIAL PRIMARY KEY,
    part_id INTEGER NOT NULL,
    attribute_name TEXT,
    attribute_definition_id INTEGER,
    attribute_value TEXT NOT NULL,
    unit TEXT,
    attribute_unit_id INTEGER,
    source TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (part_id)
        REFERENCES catalog.parts(id)
        ON DELETE CASCADE,

    FOREIGN KEY (attribute_definition_id)
        REFERENCES reference.attribute_definitions(id)
        ON DELETE SET NULL,

    FOREIGN KEY (attribute_unit_id)
        REFERENCES reference.attribute_units(id)
        ON DELETE SET NULL
);

CREATE INDEX idx_part_attributes_part_id
ON catalog.part_attributes(part_id);

CREATE INDEX idx_part_attributes_name
ON catalog.part_attributes(attribute_name);

CREATE INDEX idx_part_attributes_attribute_definition_id
ON catalog.part_attributes(attribute_definition_id);

CREATE INDEX idx_part_attributes_attribute_unit_id
ON catalog.part_attributes(attribute_unit_id);


CREATE TABLE catalog.clusters (
    id SERIAL PRIMARY KEY,
    part_id INTEGER,
    name TEXT,
    cluster_type TEXT NOT NULL DEFAULT 'discovery',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (part_id)
        REFERENCES catalog.parts(id)
        ON DELETE SET NULL,

    CHECK (cluster_type IN ('discovery', 'consolidated'))
);

CREATE INDEX idx_clusters_part_id
ON catalog.clusters(part_id);

CREATE INDEX idx_clusters_type
ON catalog.clusters(cluster_type);


CREATE TABLE catalog.cluster_codes (
    cluster_id INTEGER NOT NULL,
    code_id INTEGER NOT NULL,

    PRIMARY KEY (cluster_id, code_id),

    FOREIGN KEY (cluster_id)
        REFERENCES catalog.clusters(id)
        ON DELETE CASCADE,

    FOREIGN KEY (code_id)
        REFERENCES discovery.codes(id)
        ON DELETE CASCADE
);

CREATE INDEX idx_cluster_codes_cluster
ON catalog.cluster_codes(cluster_id);

CREATE INDEX idx_cluster_codes_code
ON catalog.cluster_codes(code_id);


CREATE TABLE catalog.applications (
    id SERIAL PRIMARY KEY,
    cluster_id INTEGER NOT NULL,
    motor_id INTEGER,
    vehicle_id INTEGER,
    position TEXT,
    position_type_id INTEGER,
    side TEXT,
    side_type_id INTEGER,
    notes TEXT,
    source TEXT,
    confidence_score NUMERIC(4,3) NOT NULL DEFAULT 0.500,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (cluster_id)
        REFERENCES catalog.clusters(id)
        ON DELETE CASCADE,

    FOREIGN KEY (motor_id)
        REFERENCES reference.motors(id)
        ON DELETE CASCADE,

    FOREIGN KEY (vehicle_id)
        REFERENCES reference.vehicles(id)
        ON DELETE CASCADE,

    FOREIGN KEY (position_type_id)
        REFERENCES reference.position_types(id)
        ON DELETE SET NULL,

    FOREIGN KEY (side_type_id)
        REFERENCES reference.side_types(id)
        ON DELETE SET NULL,

    CHECK (confidence_score >= 0.000 AND confidence_score <= 1.000),
    CHECK (side IN ('left', 'right', 'both') OR side IS NULL),
    CHECK (position IN ('front', 'rear', 'inner', 'outer', 'upper', 'lower') OR position IS NULL),
    CHECK (motor_id IS NOT NULL OR vehicle_id IS NOT NULL)
);

CREATE INDEX idx_applications_cluster
ON catalog.applications(cluster_id);

CREATE INDEX idx_applications_motor
ON catalog.applications(motor_id);

CREATE INDEX idx_applications_vehicle
ON catalog.applications(vehicle_id);

CREATE INDEX idx_applications_confidence
ON catalog.applications(confidence_score);

CREATE INDEX idx_applications_position_type_id
ON catalog.applications(position_type_id);

CREATE INDEX idx_applications_side_type_id
ON catalog.applications(side_type_id);



/*
===============================================================================
COMPATIBILITY SCHEMA
===============================================================================

Camada responsável por regras, evidências e decisões técnicas de compatibilidade.
===============================================================================
*/


CREATE TABLE compatibility.rules (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    rule_type TEXT NOT NULL,
    rule_expression JSONB NOT NULL,
    priority INTEGER NOT NULL DEFAULT 100,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_compatibility_rules_rule_type
ON compatibility.rules(rule_type);

CREATE INDEX idx_compatibility_rules_is_active
ON compatibility.rules(is_active);


CREATE TABLE compatibility.evidence (
    id SERIAL PRIMARY KEY,
    application_id INTEGER NOT NULL,
    source TEXT,
    evidence_type TEXT,
    evidence_data JSONB,
    confidence_score NUMERIC(4,3),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (application_id)
        REFERENCES catalog.applications(id)
        ON DELETE CASCADE,

    CHECK (confidence_score IS NULL OR (confidence_score >= 0.000 AND confidence_score <= 1.000))
);

CREATE INDEX idx_compatibility_evidence_application_id
ON compatibility.evidence(application_id);


CREATE TABLE compatibility.decisions (
    id SERIAL PRIMARY KEY,
    application_id INTEGER NOT NULL,
    rule_id INTEGER,
    decision TEXT NOT NULL,
    confidence_score NUMERIC(4,3),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (application_id)
        REFERENCES catalog.applications(id)
        ON DELETE CASCADE,

    FOREIGN KEY (rule_id)
        REFERENCES compatibility.rules(id)
        ON DELETE SET NULL,

    CHECK (decision IN ('approved', 'rejected', 'pending_review', 'inferred')),
    CHECK (confidence_score IS NULL OR (confidence_score >= 0.000 AND confidence_score <= 1.000))
);

CREATE INDEX idx_compatibility_decisions_application_id
ON compatibility.decisions(application_id);

CREATE INDEX idx_compatibility_decisions_rule_id
ON compatibility.decisions(rule_id);

CREATE INDEX idx_compatibility_decisions_decision
ON compatibility.decisions(decision);



/*
===============================================================================
PUBLICATION SCHEMA
===============================================================================

Controla batches, versões e snapshots do catálogo publicado.
===============================================================================
*/


CREATE TABLE publication.batches (
    id SERIAL PRIMARY KEY,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    finished_at TIMESTAMP,
    status TEXT NOT NULL DEFAULT 'running',
    notes TEXT,

    CHECK (status IN ('running', 'completed', 'failed', 'rolled_back'))
);

CREATE INDEX idx_publication_batches_status
ON publication.batches(status);


CREATE TABLE publication.catalog_versions (
    id SERIAL PRIMARY KEY,
    version_number INTEGER NOT NULL UNIQUE,
    batch_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,

    FOREIGN KEY (batch_id)
        REFERENCES publication.batches(id)
        ON DELETE SET NULL
);

CREATE INDEX idx_publication_catalog_versions_batch_id
ON publication.catalog_versions(batch_id);


CREATE TABLE publication.published_parts (
    id SERIAL PRIMARY KEY,
    catalog_version_id INTEGER NOT NULL,
    part_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (catalog_version_id)
        REFERENCES publication.catalog_versions(id)
        ON DELETE CASCADE,

    FOREIGN KEY (part_id)
        REFERENCES catalog.parts(id)
        ON DELETE CASCADE
);

CREATE UNIQUE INDEX idx_published_parts_unique
ON publication.published_parts(catalog_version_id, part_id);


CREATE TABLE publication.published_applications (
    id SERIAL PRIMARY KEY,
    catalog_version_id INTEGER NOT NULL,
    application_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (catalog_version_id)
        REFERENCES publication.catalog_versions(id)
        ON DELETE CASCADE,

    FOREIGN KEY (application_id)
        REFERENCES catalog.applications(id)
        ON DELETE CASCADE
);

CREATE UNIQUE INDEX idx_published_applications_unique
ON publication.published_applications(catalog_version_id, application_id);



/*
===============================================================================
CARGA INICIAL DO DOMÍNIO CANÔNICO
===============================================================================
*/


INSERT INTO reference.position_types (code, name, description)
VALUES
    ('front', 'Front', 'Aplicação na parte dianteira'),
    ('rear', 'Rear', 'Aplicação na parte traseira'),
    ('inner', 'Inner', 'Aplicação interna'),
    ('outer', 'Outer', 'Aplicação externa'),
    ('upper', 'Upper', 'Aplicação superior'),
    ('lower', 'Lower', 'Aplicação inferior')
ON CONFLICT (code) DO NOTHING;


INSERT INTO reference.side_types (code, name, description)
VALUES
    ('left', 'Left', 'Aplicação no lado esquerdo'),
    ('right', 'Right', 'Aplicação no lado direito'),
    ('both', 'Both', 'Aplicação nos dois lados')
ON CONFLICT (code) DO NOTHING;


INSERT INTO reference.fuel_types (code, name, description)
VALUES
    ('gasoline', 'Gasoline', 'Veículo ou motor movido a gasolina'),
    ('diesel', 'Diesel', 'Veículo ou motor movido a diesel'),
    ('flex', 'Flex', 'Veículo ou motor flexível'),
    ('hybrid', 'Hybrid', 'Veículo híbrido'),
    ('electric', 'Electric', 'Veículo elétrico')
ON CONFLICT (code) DO NOTHING;


INSERT INTO reference.body_types (code, name, description)
VALUES
    ('sedan', 'Sedan', 'Carroceria sedan'),
    ('hatch', 'Hatch', 'Carroceria hatch'),
    ('suv', 'SUV', 'Carroceria utilitário esportivo'),
    ('pickup', 'Pickup', 'Carroceria pickup'),
    ('wagon', 'Wagon', 'Carroceria station wagon')
ON CONFLICT (code) DO NOTHING;


INSERT INTO reference.attribute_units (code, name, symbol, description)
VALUES
    ('millimeter', 'Millimeter', 'mm', 'Milímetro'),
    ('centimeter', 'Centimeter', 'cm', 'Centímetro'),
    ('kilogram', 'Kilogram', 'kg', 'Quilograma'),
    ('bar', 'Bar', 'bar', 'Unidade de pressão bar'),
    ('volt', 'Volt', 'V', 'Unidade de tensão elétrica')
ON CONFLICT (code) DO NOTHING;


INSERT INTO reference.attribute_definitions (
    code,
    name,
    description,
    data_type,
    default_unit_id
)
VALUES
    (
        'height',
        'Height',
        'Altura da peça',
        'numeric',
        (SELECT id FROM reference.attribute_units WHERE code = 'millimeter')
    ),
    (
        'inner_diameter',
        'Inner Diameter',
        'Diâmetro interno da peça',
        'numeric',
        (SELECT id FROM reference.attribute_units WHERE code = 'millimeter')
    ),
    (
        'outer_diameter',
        'Outer Diameter',
        'Diâmetro externo da peça',
        'numeric',
        (SELECT id FROM reference.attribute_units WHERE code = 'millimeter')
    ),
    (
        'length',
        'Length',
        'Comprimento da peça',
        'numeric',
        (SELECT id FROM reference.attribute_units WHERE code = 'millimeter')
    ),
    (
        'thread',
        'Thread',
        'Especificação de rosca da peça',
        'text',
        NULL
    ),
    (
        'voltage',
        'Voltage',
        'Tensão elétrica da peça',
        'numeric',
        (SELECT id FROM reference.attribute_units WHERE code = 'volt')
    )
ON CONFLICT (code) DO NOTHING;