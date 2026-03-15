/*
===============================================================================
001_canonical_domain.sql
===============================================================================

MIGRAÇÃO: Domínio Canônico do Catálogo Automotivo

Este arquivo introduz o modelo de domínio canônico do sistema.

O objetivo é reduzir o uso de texto livre em campos críticos e substituí-lo
por vocabulários controlados e estruturas padronizadas.

Isso melhora:

- consistência de dados
- qualidade das consultas
- capacidade de integração com fornecedores
- compatibilidade com padrões internacionais de catálogo automotivo


-------------------------------------------------------------------------------
PROBLEMA QUE ESTA MIGRAÇÃO RESOLVE
-------------------------------------------------------------------------------

No início do projeto muitos atributos são armazenados como texto livre:

    position = "front"
    side = "left"
    fuel_type = "gasoline"

Isso cria problemas:

- inconsistência de escrita
- dificuldade de filtro
- dificuldade de validação
- dificuldade de integração com APIs externas


-------------------------------------------------------------------------------
SOLUÇÃO
-------------------------------------------------------------------------------

Criar tabelas de referência que funcionam como vocabulário controlado.

Exemplos:

reference.position_types
reference.side_types
reference.fuel_types
reference.body_types
reference.attribute_definitions
reference.attribute_units


-------------------------------------------------------------------------------
EXEMPLOS DE USO FUTURO
-------------------------------------------------------------------------------

catalog.applications
    position_type_id → reference.position_types

reference.vehicles
    fuel_type_id → reference.fuel_types

catalog.part_attributes
    attribute_definition_id → reference.attribute_definitions


-------------------------------------------------------------------------------
BENEFÍCIOS ARQUITETURAIS
-------------------------------------------------------------------------------

- padronização do domínio automotivo
- redução de inconsistência de dados
- base sólida para o motor de compatibilidade
- suporte a internacionalização futura


-------------------------------------------------------------------------------
STATUS
-------------------------------------------------------------------------------

Arquivo reservado para implementação futura.
A estrutura será introduzida em fases posteriores do projeto.

===============================================================================
*/
