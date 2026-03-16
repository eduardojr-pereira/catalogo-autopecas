/*
===============================================================================
reference_seed.sql
===============================================================================

SEED: Dados de Referência do Catálogo Automotivo

STATUS ATUAL
-------------------------------------------------------------------------------
Este arquivo está reservado como placeholder.

No momento, ele NÃO realiza carga de dados.

Decisão atual do projeto:
- manter este arquivo no fluxo oficial de bootstrap
- preservar sua função documental
- adiar a criação de uma seed mínima ou carga mais realista para etapa futura

MOTIVAÇÃO
-------------------------------------------------------------------------------
Nesta fase, a validação do banco está priorizando:
- estrutura do schema
- seed canônica obrigatória
- ordem correta de bootstrap
- consistência arquitetural

A carga de dados de referência continuará pendente para evolução posterior,
especialmente quando houver maior maturidade da integração com a API da
Tabela FIPE e das regras de ingestão do domínio.

RELAÇÃO COM OUTROS ARQUIVOS
-------------------------------------------------------------------------------
Este arquivo deve ser executado APÓS:
- database/schema.sql
- database/seeds/canonical_seed.sql

Este arquivo deve ser executado ANTES de:
- arquivos SQL de views em database/views

OBSERVAÇÃO IMPORTANTE
-------------------------------------------------------------------------------
Mesmo vazio, este arquivo permanece no fluxo de bootstrap para:
- manter a ordem oficial do provisionamento
- evitar retrabalho futuro no init do banco
- explicitar que existe uma etapa reservada para dados de referência

===============================================================================
*/