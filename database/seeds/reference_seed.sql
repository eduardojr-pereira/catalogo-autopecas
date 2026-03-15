/*
===============================================================================
reference_seed.sql
===============================================================================

SEED: Dados de Referência do Catálogo Automotivo

Este arquivo conterá os dados iniciais das tabelas de referência do sistema.

O objetivo é popular entidades estruturais e relativamente estáveis do domínio,
permitindo que o banco tenha uma base mínima consistente para testes,
desenvolvimento e futuras integrações.


-------------------------------------------------------------------------------
OBJETIVO
-------------------------------------------------------------------------------

Inserir dados fundamentais das tabelas do schema `reference`.

Esses dados servem como base para:

- testes automatizados
- desenvolvimento local
- primeiros cenários de uso do catálogo
- validação das regras de negócio


-------------------------------------------------------------------------------
EXEMPLOS DE DADOS QUE PODERÃO SER INSERIDOS
-------------------------------------------------------------------------------

Fabricantes

    Honda
    Toyota
    Bosch
    Mahle
    NGK
    Denso


Tipos de fabricante

    oem
    aftermarket
    marketplace
    unknown


Tipos de peça

    filtro de óleo
    filtro de ar
    vela de ignição
    pastilha de freio
    amortecedor


Aliases de tipos de peça

    filtro óleo
    vela
    pastilha
    amortecedor dianteiro


Veículos e motores de exemplo

    Honda Civic 2010
    Honda Fit 2012
    Toyota Corolla 2015

    R18A1
    L15B
    2ZR-FE


-------------------------------------------------------------------------------
BENEFÍCIOS
-------------------------------------------------------------------------------

- acelera configuração do ambiente local
- reduz trabalho manual no banco
- padroniza massa inicial de testes
- facilita demonstração do projeto


-------------------------------------------------------------------------------
RELAÇÃO COM OUTROS ARQUIVOS
-------------------------------------------------------------------------------

Este arquivo complementa:

- database/schema.sql
- database/seeds/canonical_seed.sql

Enquanto `reference_seed.sql` alimenta dados estruturais do domínio,
`canonical_seed.sql` alimenta vocabulários controlados e taxonomias.


-------------------------------------------------------------------------------
STATUS
-------------------------------------------------------------------------------

Arquivo reservado para implementação futura.

===============================================================================
*/