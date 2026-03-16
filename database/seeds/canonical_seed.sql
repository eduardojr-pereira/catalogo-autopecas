/*
===============================================================================
canonical_seed.sql
===============================================================================

SEED: Dados Canônicos do Domínio Automotivo

Este arquivo popula os vocabulários controlados e definições canônicas
utilizadas pelo banco de dados do projeto.

Responsabilidades deste arquivo:
- inserir domínios controlados do schema reference
- garantir padronização mínima para atributos, combustível, lado,
  posição e carroceria
- preparar o ambiente para testes, ingestão e uso local

Este arquivo deve ser executado APÓS:
- database/schema.sql

Este arquivo deve ser executado ANTES de:
- database/seeds/reference_seed.sql
- os arquivos SQL de views em database/views
- testes que dependam de dados canônicos previamente carregados

Estratégia de idempotência:
- todos os inserts usam ON CONFLICT DO NOTHING
- isso permite reexecução segura em ambiente local

Observação técnica:
Evitar, em comentários de bloco, textos que contenham a sequência
barra + asterisco, pois isso pode ser interpretado pelo parser SQL
como início de um novo comentário de bloco.
===============================================================================
*/


/*
===============================================================================
POSITION TYPES
===============================================================================

Domínio canônico de posição de aplicação da peça.
===============================================================================
*/
INSERT INTO reference.position_types (
    code,
    name,
    description
)
VALUES
    ('front', 'Front', 'Aplicação na parte dianteira'),
    ('rear', 'Rear', 'Aplicação na parte traseira'),
    ('inner', 'Inner', 'Aplicação interna'),
    ('outer', 'Outer', 'Aplicação externa'),
    ('upper', 'Upper', 'Aplicação superior'),
    ('lower', 'Lower', 'Aplicação inferior')
ON CONFLICT (code) DO NOTHING;


/*
===============================================================================
SIDE TYPES
===============================================================================

Domínio canônico de lado de aplicação da peça.
===============================================================================
*/
INSERT INTO reference.side_types (
    code,
    name,
    description
)
VALUES
    ('left', 'Left', 'Aplicação no lado esquerdo'),
    ('right', 'Right', 'Aplicação no lado direito'),
    ('both', 'Both', 'Aplicação nos dois lados')
ON CONFLICT (code) DO NOTHING;


/*
===============================================================================
FUEL TYPES
===============================================================================

Domínio canônico de combustível para veículos e motores.
===============================================================================
*/
INSERT INTO reference.fuel_types (
    code,
    name,
    description
)
VALUES
    ('gasoline', 'Gasoline', 'Veículo ou motor movido a gasolina'),
    ('diesel', 'Diesel', 'Veículo ou motor movido a diesel'),
    ('flex', 'Flex', 'Veículo ou motor flexível'),
    ('hybrid', 'Hybrid', 'Veículo híbrido'),
    ('electric', 'Electric', 'Veículo elétrico')
ON CONFLICT (code) DO NOTHING;


/*
===============================================================================
BODY TYPES
===============================================================================

Domínio canônico de carroceria.
===============================================================================
*/
INSERT INTO reference.body_types (
    code,
    name,
    description
)
VALUES
    ('sedan', 'Sedan', 'Carroceria sedan'),
    ('hatch', 'Hatch', 'Carroceria hatch'),
    ('suv', 'SUV', 'Carroceria utilitário esportivo'),
    ('pickup', 'Pickup', 'Carroceria pickup'),
    ('wagon', 'Wagon', 'Carroceria station wagon')
ON CONFLICT (code) DO NOTHING;


/*
===============================================================================
ATTRIBUTE UNITS
===============================================================================

Unidades canônicas de atributos técnicos.
===============================================================================
*/
INSERT INTO reference.attribute_units (
    code,
    name,
    symbol,
    description
)
VALUES
    ('millimeter', 'Millimeter', 'mm', 'Milímetro'),
    ('centimeter', 'Centimeter', 'cm', 'Centímetro'),
    ('kilogram', 'Kilogram', 'kg', 'Quilograma'),
    ('bar', 'Bar', 'bar', 'Unidade de pressão bar'),
    ('volt', 'Volt', 'V', 'Unidade de tensão elétrica')
ON CONFLICT (code) DO NOTHING;


/*
===============================================================================
ATTRIBUTE DEFINITIONS
===============================================================================

Definições canônicas de atributos técnicos.

Observação importante:
As referências a default_unit_id dependem da existência prévia dos registros
em reference.attribute_units. Por isso este bloco deve vir após a carga de
attribute_units.
===============================================================================
*/
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