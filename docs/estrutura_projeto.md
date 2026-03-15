catalogo_autopecas/
│
├── database/
│   ├── schema.sql
│   ├── seeds/
│   └── migrations/
│
├── docker/
│   └── docker-compose.yml
│
├── docs/
│   ├── arquitetura.md
│   ├── modelo_dados.md
│   ├── pipeline_dados.md
│   ├── regra_ouro.md
│   └── roadmap.md
│
├── data/
│   ├── raw/
│   ├── staging/
│   └── processed/
│
├── src/
│   ├── shared/
│   │   ├── config.py
│   │   ├── db.py
│   │   ├── logging_config.py
│   │   └── utils.py
│   │
│   ├── ingestion/
│   │   ├── scrapers/
│   │   ├── parsers/
│   │   ├── collectors/
│   │   └── loaders/
│   │
│   ├── processing/
│   │   ├── normalization/
│   │   │   ├── code_normalizer.py
│   │   │   └── code_service.py
│   │   │
│   │   ├── equivalence/
│   │   │   ├── equivalence_engine.py
│   │   │   ├── equivalence_loader.py
│   │   │   └── equivalence_scorer.py
│   │   │
│   │   ├── clustering/
│   │   │   └── cluster_service.py
│   │   │
│   │   └── consolidation/
│   │       └── consolidation_service.py
│   │
│   ├── domain/
│   │   ├── manufacturers/
│   │   ├── vehicles/
│   │   ├── motors/
│   │   ├── codes/
│   │   ├── clusters/
│   │   └── applications/
│   │
│   └── delivery/
│       ├── api/
│       │   └── main.py
│       └── cli/
│
├── tests/
│   ├── unit/
│   ├── integration/
│   └── conftest.py
│
├── .gitignore
├── README.md
└── requirements.txt




---
---

# Estrutura do Projeto

Este documento descreve a organização do repositório do Catálogo Automotivo Inteligente.

A estrutura foi projetada para suportar:

- ingestão de dados
- processamento técnico
- consolidação do catálogo
- entrega via API ou CLI

---

# Estrutura Geral

catalogo_autopecas/

├── database/  
│   ├── schema.sql  
│   ├── seeds/  
│   └── migrations/  

├── docker/  
│   └── docker-compose.yml  

├── docs/  
│   ├── arquitetura.md  
│   ├── modelo_dados.md  
│   ├── pipeline_dados.md  
│   ├── regra_ouro.md  
│   ├── estrutura_projeto.md  
│   └── roadmap.md  

├── data/  
│   ├── raw/  
│   ├── staging/  
│   └── processed/  

---


# Código Fonte

src/

## shared

Componentes compartilhados por todo o sistema.

src/shared/

config.py  
Configuração central da aplicação.

db.py  
Conexão com banco de dados.

logging_config.py  
Configuração de logging do projeto.

utils.py  
Funções utilitárias gerais.

---

## ingestion

Responsável pela coleta de dados.

src/ingestion/

scrapers/  
Scrapers para sites de autopeças.

collectors/  
Coleta de dados estruturados.

parsers/  
Extração de dados das páginas.

loaders/  
Inserção de dados brutos no banco.

---

## processing

Responsável pelo processamento técnico dos dados.

src/processing/

### normalization

Normalização de códigos.

code_normalizer.py  
Remove ruídos de códigos automotivos.

code_service.py  
Serviços para inserção segura de códigos.

---

### equivalence

Descoberta de equivalências.

equivalence_engine.py  
Construção do grafo de equivalências.

equivalence_loader.py  
Carga de equivalências para clusterização.

equivalence_scorer.py  
Algoritmo de pontuação de equivalências.

---

### clustering

Geração de clusters de peças.

cluster_service.py  
Serviço de clusterização baseado em grafos.

---

### consolidation

Transformação de clusters descobertos em clusters consolidados.

consolidation_service.py  
Processo de consolidação do catálogo.

---

## catalog

Domínio consolidado do catálogo.

src/catalog/

part_service.py  
Gerenciamento de peças consolidadas.

application_service.py  
Gerenciamento de aplicações peça → motor → veículo.

---

## delivery

Camada de entrega do sistema.

src/delivery/

api/  
API de consulta do catálogo.

cli/  
Ferramentas de linha de comando.

---

# Testes

tests/

unit/  
Testes unitários.

integration/  
Testes com banco de dados.

conftest.py  
Fixtures compartilhadas.

---

# Dados

data/

raw/  
Dados coletados diretamente das fontes.

staging/  
Dados intermediários após limpeza.

processed/  
Dados prontos para consumo.

---

# Objetivo da Arquitetura

Separar claramente:

- ingestão de dados
- processamento técnico
- domínio do catálogo
- entrega do sistema

Isso permite:

- evolução independente das camadas
- maior escalabilidade
- melhor manutenção do código