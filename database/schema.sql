/*
=========================================================
CATÁLOGO AUTOMOTIVO - ESTRUTURA INICIAL DO BANCO
Banco: PostgreSQL

Este schema cria três camadas principais:

reference  -> dados estruturais (fabricantes, veículos, motores)
discovery  -> dados descobertos (códigos e equivalências)
catalog    -> catálogo consolidado (clusters e aplicações)

=========================================================
*/


/*
=========================================================
CRIAR SCHEMAS (SEPARAÇÃO LÓGICA DO BANCO)
=========================================================
*/

CREATE SCHEMA IF NOT EXISTS reference;
CREATE SCHEMA IF NOT EXISTS discovery;
CREATE SCHEMA IF NOT EXISTS catalog;



/*
=========================================================
REFERENCE SCHEMA
Contém dados estruturais e relativamente estáveis
=========================================================
*/


/*
---------------------------------------------------------
FABRICANTES DE PEÇAS
Ex: Bosch, Mahle, NGK, Honda
---------------------------------------------------------
*/
CREATE TABLE reference.manufacturers (

    id SERIAL PRIMARY KEY,

    -- nome do fabricante
    name TEXT NOT NULL UNIQUE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);



/*
---------------------------------------------------------
VEÍCULOS
Inicialmente podem ser populados com dados da FIPE
---------------------------------------------------------
*/
CREATE TABLE reference.vehicles (

    id SERIAL PRIMARY KEY,

    brand TEXT NOT NULL,
    model TEXT NOT NULL,
    year INTEGER NOT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);



/*
---------------------------------------------------------
MOTORES
Ex: R18, K20, EA111
---------------------------------------------------------
*/
CREATE TABLE reference.motors (

    id SERIAL PRIMARY KEY,

    code TEXT NOT NULL,
    description TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);



/*
---------------------------------------------------------
RELAÇÃO VEÍCULO ↔ MOTOR
Um veículo pode ter múltiplos motores
---------------------------------------------------------
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
=========================================================
DISCOVERY SCHEMA
Dados descobertos automaticamente pelo sistema
=========================================================
*/


/*
---------------------------------------------------------
CÓDIGOS DE PEÇAS
Cada registro representa um código de peça de um fabricante
---------------------------------------------------------
*/
CREATE TABLE discovery.codes (

    id SERIAL PRIMARY KEY,

    -- fabricante do código
    manufacturer_id INTEGER NOT NULL,

    -- código original da peça
    code TEXT NOT NULL,

    /*
    código normalizado

    exemplo:
    15400-RTA-003
    15400 RTA 003

    viram

    15400RTA003
    */
    normalized_code TEXT NOT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (manufacturer_id)
        REFERENCES reference.manufacturers(id)
);


/*
Índice extremamente importante para buscas rápidas por código
*/
CREATE INDEX idx_codes_normalized
ON discovery.codes(normalized_code);


/*
Evita duplicação do mesmo código para o mesmo fabricante
*/
CREATE UNIQUE INDEX idx_codes_unique
ON discovery.codes(manufacturer_id, normalized_code);




/*
---------------------------------------------------------
REDE DE EQUIVALÊNCIA ENTRE CÓDIGOS

Representa conexões no grafo de equivalência

Exemplo:
Bosch 0986AF0051 ↔ Mahle OC1196
---------------------------------------------------------
*/
CREATE TABLE discovery.code_equivalences (

    id SERIAL PRIMARY KEY,

    code_id_1 INTEGER NOT NULL,
    code_id_2 INTEGER NOT NULL,

    /*
    origem da equivalência

    exemplos:
    catalog
    scraper
    manual
    */
    source TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (code_id_1)
        REFERENCES discovery.codes(id)
        ON DELETE CASCADE,

    FOREIGN KEY (code_id_2)
        REFERENCES discovery.codes(id)
        ON DELETE CASCADE
);



/*
Índices importantes para percorrer o grafo de equivalência
*/
CREATE INDEX idx_equiv_code1
ON discovery.code_equivalences(code_id_1);

CREATE INDEX idx_equiv_code2
ON discovery.code_equivalences(code_id_2);




/*
=========================================================
CATALOG SCHEMA
Camada consolidada do catálogo
=========================================================
*/


/*
---------------------------------------------------------
CLUSTERS DE PEÇAS

Cada cluster representa uma peça funcional única
independente de fabricante
---------------------------------------------------------
*/
CREATE TABLE catalog.clusters (

    id SERIAL PRIMARY KEY,

    /*
    nome opcional do cluster
    muitos clusters podem não ter nome
    */
    name TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);




/*
---------------------------------------------------------
RELAÇÃO CLUSTER ↔ CÓDIGOS

Todos os códigos equivalentes pertencem ao mesmo cluster
---------------------------------------------------------
*/
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



/*
Índices para consultas rápidas
*/
CREATE INDEX idx_cluster_codes_cluster
ON catalog.cluster_codes(cluster_id);

CREATE INDEX idx_cluster_codes_code
ON catalog.cluster_codes(code_id);




/*
---------------------------------------------------------
APLICAÇÕES

Define onde uma peça (cluster) pode ser usada
---------------------------------------------------------
*/
CREATE TABLE catalog.applications (

    cluster_id INTEGER NOT NULL,
    motor_id INTEGER NOT NULL,

    PRIMARY KEY (cluster_id, motor_id),

    FOREIGN KEY (cluster_id)
        REFERENCES catalog.clusters(id)
        ON DELETE CASCADE,

    FOREIGN KEY (motor_id)
        REFERENCES reference.motors(id)
        ON DELETE CASCADE
);



/*
Índice para busca por motor
*/
CREATE INDEX idx_applications_motor
ON catalog.applications(motor_id);
