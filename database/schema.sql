/*
===============================================================================
schema.sql
===============================================================================

SCHEMA PRINCIPAL DO CATÁLOGO AUTOMOTIVO

Este arquivo define a estrutura base do banco de dados PostgreSQL do projeto.

Ele representa o núcleo estrutural do sistema e estabelece as entidades,
relacionamentos, constraints e índices necessários para suportar:

- descoberta de códigos
- equivalências entre peças
- clusterização
- consolidação do catálogo
- aplicações em motores e veículos


-------------------------------------------------------------------------------
VISÃO GERAL DA ARQUITETURA
-------------------------------------------------------------------------------

O banco é dividido em três schemas principais:

reference
    Dados estruturais e relativamente estáveis do domínio automotivo.

discovery
    Dados descobertos durante coleta, scraping, validação e enriquecimento.

catalog
    Dados consolidados e utilizáveis como catálogo final.


-------------------------------------------------------------------------------
SCHEMA REFERENCE
-------------------------------------------------------------------------------

Responsável por armazenar entidades fundamentais do domínio.

Exemplos de tabelas:

- reference.manufacturers
- reference.part_types
- reference.part_type_aliases
- reference.vehicles
- reference.motors
- reference.vehicle_motors

Essas tabelas representam o conhecimento base do sistema.


-------------------------------------------------------------------------------
SCHEMA DISCOVERY
-------------------------------------------------------------------------------

Responsável por armazenar dados coletados e relações descobertas.

Exemplos de tabelas:

- discovery.sources
- discovery.codes
- discovery.code_evidence
- discovery.code_equivalences

Essa camada é deliberadamente mais flexível, pois suporta hipóteses,
descobertas e equivalências ainda não consolidadas.


-------------------------------------------------------------------------------
SCHEMA CATALOG
-------------------------------------------------------------------------------

Responsável por armazenar o catálogo consolidado.

Exemplos de tabelas:

- catalog.parts
- catalog.part_attributes
- catalog.clusters
- catalog.cluster_codes
- catalog.applications

Essa camada é a base para buscas, fitment e futuras APIs.


-------------------------------------------------------------------------------
PRINCÍPIO DE NEGÓCIO MAIS IMPORTANTE
-------------------------------------------------------------------------------

Equivalência descoberta não implica identidade técnica absoluta.

Por isso o schema foi desenhado para separar:

- descoberta
- validação
- consolidação

Essa separação reduz risco de erro técnico no catálogo final.


-------------------------------------------------------------------------------
OBJETIVOS ESTRUTURAIS DO SCHEMA
-------------------------------------------------------------------------------

- suportar crescimento incremental do catálogo
- permitir rastreabilidade das equivalências
- possibilitar clusterização de códigos
- associar peças a motores e veículos
- permitir evolução futura para SaaS automotivo


-------------------------------------------------------------------------------
RELAÇÃO COM OUTROS ARQUIVOS
-------------------------------------------------------------------------------

Este arquivo funciona em conjunto com:

- database/seeds/reference_seed.sql
- database/seeds/canonical_seed.sql
- database/migrations/001_canonical_domain.sql
- database/migrations/002_compatibility_engine.sql
- database/migrations/003_publication_versioning.sql

O `schema.sql` define a base principal.
As migrations futuras expandirão essa base para níveis mais avançados
de governança, compatibilidade e versionamento.


-------------------------------------------------------------------------------
STATUS
-------------------------------------------------------------------------------

Arquivo ativo e central do projeto.

Toda alteração estrutural relevante do banco deve ser refletida aqui
ou em migrations complementares, conforme a estratégia adotada.

===============================================================================
*/







/*
=========================================================
CATÁLOGO AUTOMOTIVO - SCHEMA FINAL
Banco: PostgreSQL
=========================================================
*/

CREATE SCHEMA IF NOT EXISTS reference;
CREATE SCHEMA IF NOT EXISTS discovery;
CREATE SCHEMA IF NOT EXISTS catalog;


/*
=========================================================
REFERENCE SCHEMA
=========================================================
*/

CREATE TABLE reference.manufacturers (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    manufacturer_type TEXT NOT NULL DEFAULT 'unknown',
    country TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CHECK (manufacturer_type IN ('oem', 'aftermarket', 'marketplace', 'unknown'))
);

CREATE INDEX idx_manufacturers_type
ON reference.manufacturers(manufacturer_type);


CREATE TABLE reference.part_types (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    normalized_name TEXT NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_part_types_normalized_name
ON reference.part_types(normalized_name);


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


CREATE TABLE reference.vehicles (
    id SERIAL PRIMARY KEY,
    brand TEXT NOT NULL,
    model TEXT NOT NULL,
    model_year INTEGER NOT NULL,
    version TEXT,
    body_type TEXT,
    fuel_type TEXT,
    market TEXT NOT NULL DEFAULT 'BR',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_vehicles_lookup
ON reference.vehicles(brand, model, model_year);

CREATE INDEX idx_vehicles_market
ON reference.vehicles(market);


CREATE TABLE reference.motors (
    id SERIAL PRIMARY KEY,
    code TEXT NOT NULL UNIQUE,
    description TEXT,
    displacement NUMERIC(5,2),
    fuel_type TEXT,
    aspiration TEXT,
    valve_count INTEGER,
    power_hp NUMERIC(6,2),
    engine_family TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_motors_engine_family
ON reference.motors(engine_family);

CREATE INDEX idx_motors_fuel_type
ON reference.motors(fuel_type);


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
=========================================================
DISCOVERY SCHEMA
=========================================================
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


/*
Evita duplicidade lógica simples de pares A-B e B-A.
Usa LEAST/GREATEST para normalizar a ordem do par.
*/
CREATE UNIQUE INDEX idx_equiv_unique_pair
ON discovery.code_equivalences (
    LEAST(code_id_1, code_id_2),
    GREATEST(code_id_1, code_id_2)
);


/*
=========================================================
CATALOG SCHEMA
=========================================================
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
    attribute_name TEXT NOT NULL,
    attribute_value TEXT NOT NULL,
    unit TEXT,
    source TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (part_id)
        REFERENCES catalog.parts(id)
        ON DELETE CASCADE
);

CREATE INDEX idx_part_attributes_part_id
ON catalog.part_attributes(part_id);

CREATE INDEX idx_part_attributes_name
ON catalog.part_attributes(attribute_name);


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
    side TEXT,
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



