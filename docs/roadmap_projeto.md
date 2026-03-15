# Roadmap do Projeto - Catálogo Automotivo Inteligente

Este documento apresenta a evolução técnica do projeto e as próximas etapas planejadas para transformar o catálogo automotivo em uma plataforma escalável capaz de evoluir para API pública ou SaaS.

O roadmap está organizado em três partes:

1. Evoluções já implementadas
2. Implementações futuras (ordem cronológica)
3. Possíveis melhorias arquiteturais


---

# Evoluções já implementadas

## Estrutura inicial do projeto

- criação do repositório
- definição da estrutura de diretórios
- separação entre código, dados, infraestrutura e documentação

Estrutura principal:
- database
- docker
- data
- src
- test
  

---

# Infraestrutura

## Docker + PostgreSQL

Infraestrutura local containerizada para desenvolvimento reproduzível.

Implementado:

- container PostgreSQL
- inicialização via `docker-compose`
- execução do `schema.sql`
- conexão padronizada via `config.py`

Benefícios:

- ambiente isolado
- fácil replicação
- banco consistente entre desenvolvedores


---

# Modelagem de dados

## Arquitetura em camadas

O banco foi dividido em três camadas principais:
- reference → dados estruturais
- discovery → dados descobertos
- catalog → catálogo consolidado
