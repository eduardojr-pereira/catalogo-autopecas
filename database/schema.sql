/*
===============================================================================
CATÁLOGO AUTOMOTIVO INTELIGENTE
DATABASE SCHEMA
===============================================================================

Este arquivo define a estrutura do banco de dados do projeto.

Responsabilidades deste arquivo:
- criação de schemas
- criação de tabelas
- criação de constraints
- criação de índices

Este arquivo NÃO deve conter:
- carga inicial de dados
- dados canônicos
- seeds de referência
- views

Fluxo oficial de provisionamento do banco:

1) database/schema.sql
2) database/seeds/canonical_seed.sql
3) database/seeds/reference_seed.sql
4) database/views

Observação arquitetural importante
-------------------------------------------------------------------------------

O domínio de veículos utiliza a hierarquia:

vehicle_brands → vehicle_models → vehicles

Durante a fase atual do projeto, alguns campos textuais coexistem com
campos canônicos para facilitar ingestões progressivas.

Campos canônicos devem ser priorizados em novos fluxos.
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
Fabricantes
-------------------------------------------------------------------------------
*/
CREATE TABLE reference.manufacturers (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    manufacturer_type TEXT NOT NULL DEFAULT 'unknown',
    country TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CHECK (manufacturer_type IN ('oem','aftermarket','marketplace','unknown'))
);

CREATE INDEX idx_manufacturers_type
ON reference.manufacturers(manufacturer_type);



/*
-------------------------------------------------------------------------------
Tipos de peça
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
Aliases de tipo de peça
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
Unidades de atributos técnicos
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
Definições de atributos técnicos
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

    CHECK (data_type IN ('text','integer','numeric','boolean'))
);

CREATE INDEX idx_attribute_definitions_code
ON reference.attribute_definitions(code);



/*
-------------------------------------------------------------------------------
Marcas de veículos
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



/*
-------------------------------------------------------------------------------
Modelos de veículos
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



/*
-------------------------------------------------------------------------------
Veículos
-------------------------------------------------------------------------------

Representa uma configuração específica de veículo.

Estrutura do domínio:
vehicle_brands → vehicle_models → vehicles

Campos texto (brand_text, model_text) são transitórios.

Proteção contra duplicidade lógica
-------------------------------------------------------------------------------

É aplicado um índice único parcial baseado em:

(model_id, model_year, version, market)

A restrição é aplicada apenas quando model_id não é NULL,
permitindo coexistência com registros transitórios.
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

CREATE INDEX idx_vehicles_body_type_id
ON reference.vehicles(body_type_id);

CREATE INDEX idx_vehicles_fuel_type_id
ON reference.vehicles(fuel_type_id);


/*
Proteção contra duplicidade lógica
*/
CREATE UNIQUE INDEX idx_unique_vehicle_configuration
ON reference.vehicles (
    model_id,
    model_year,
    COALESCE(version,''),
    market
)
WHERE model_id IS NOT NULL;



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



/*
-------------------------------------------------------------------------------
Relacionamento veículo → motor
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
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);



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



CREATE TABLE discovery.code_equivalences (
    id SERIAL PRIMARY KEY,
    code_id_1 INTEGER NOT NULL,
    code_id_2 INTEGER NOT NULL,
    source TEXT,
    equivalence_type TEXT NOT NULL DEFAULT 'suspected',
    validation_status TEXT NOT NULL DEFAULT 'discovered',
    confidence_score NUMERIC(4,3) NOT NULL DEFAULT 0.5,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (code_id_1)
        REFERENCES discovery.codes(id)
        ON DELETE CASCADE,

    FOREIGN KEY (code_id_2)
        REFERENCES discovery.codes(id)
        ON DELETE CASCADE
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
        ON DELETE RESTRICT
);



/*
-------------------------------------------------------------------------------
Atributos técnicos de peças

Modo transitório:
attribute_name

Modo canônico:
attribute_definition_id

Estratégia futura: convergir para attribute_definition_id.
-------------------------------------------------------------------------------
*/
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



CREATE TABLE catalog.clusters (
    id SERIAL PRIMARY KEY,
    part_id INTEGER,
    name TEXT,
    cluster_type TEXT NOT NULL DEFAULT 'discovery',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);



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
    confidence_score NUMERIC(4,3) NOT NULL DEFAULT 0.5,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (cluster_id)
        REFERENCES catalog.clusters(id)
        ON DELETE CASCADE,

    FOREIGN KEY (motor_id)
        REFERENCES reference.motors(id)
        ON DELETE CASCADE,

    FOREIGN KEY (vehicle_id)
        REFERENCES reference.vehicles(id)
        ON DELETE CASCADE
);



/*
===============================================================================
COMPATIBILITY SCHEMA
===============================================================================
*/


/*
rule_type atualmente é textual.

Estratégia futura: normalizar em tabela reference.rule_types.
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
        ON DELETE CASCADE
);



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
        ON DELETE SET NULL
);



/*
===============================================================================
PUBLICATION SCHEMA
===============================================================================
*/


CREATE TABLE publication.batches (
    id SERIAL PRIMARY KEY,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    finished_at TIMESTAMP,
    status TEXT NOT NULL DEFAULT 'running',
    notes TEXT
);



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