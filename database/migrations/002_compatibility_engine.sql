/*
===============================================================================
002_compatibility_engine.sql
===============================================================================

MIGRAÇÃO: Motor de Compatibilidade e Regras Técnicas

Este arquivo introduz a base estrutural do motor de compatibilidade do catálogo.

O objetivo é permitir que o sistema determine se uma peça é compatível com um
veículo ou motor com base em regras técnicas e evidências.


-------------------------------------------------------------------------------
PROBLEMA QUE ESTA MIGRAÇÃO RESOLVE
-------------------------------------------------------------------------------

Em muitos catálogos automotivos simples, aplicações são registradas apenas como:

    peça → veículo

Sem registro de:

- evidência técnica
- origem da informação
- regras aplicadas
- nível de confiança


-------------------------------------------------------------------------------
SOLUÇÃO
-------------------------------------------------------------------------------

Introduzir tabelas que suportam decisões técnicas explicáveis.

Estruturas planejadas:

catalog.compatibility_rules
catalog.rule_conditions
catalog.application_evidence
catalog.compatibility_decisions
catalog.inferred_applications


-------------------------------------------------------------------------------
EXEMPLO DE FLUXO FUTURO
-------------------------------------------------------------------------------

1) Sistema coleta evidência de equivalência

2) Regras de compatibilidade são avaliadas

3) Motor de decisão calcula score de confiança

4) Decisão é registrada

5) Aplicação pode ser aprovada ou rejeitada


-------------------------------------------------------------------------------
BENEFÍCIOS ARQUITETURAIS
-------------------------------------------------------------------------------

- decisões de compatibilidade rastreáveis
- explicação técnica de aplicações
- redução de erro humano
- suporte a inferência automática


-------------------------------------------------------------------------------
STATUS
-------------------------------------------------------------------------------

Arquivo reservado para implementação futura.

A implementação ocorrerá após consolidação do domínio canônico.

===============================================================================
*/