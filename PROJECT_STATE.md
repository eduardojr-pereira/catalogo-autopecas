# PROJECT_STATE.md

## Projeto
Catálogo Automotivo Inteligente

---

## Objetivo do projeto

Construir um catálogo técnico automotivo com foco em:

- qualidade de dados
- rastreabilidade
- equivalência entre códigos
- fitment peça ↔ motor ↔ veículo
- busca técnica e comercial
- futura revisão técnica e publicação versionada

Arquitetura alvo do projeto:

**fontes externas → ingestão → discovery → catalog → compatibility/publication → API**

---

## Stack atual

- Python
- FastAPI
- PostgreSQL
- Docker

Schemas principais do banco:

- `reference`
- `discovery`
- `catalog`
- `compatibility`
- `publication`

---

## Fase atual

**FASE 4 — VALIDAÇÃO FUNCIONAL DA API E FECHAMENTO DOS TESTES HTTP — CONCLUÍDA**

### Justificativa

Após a consolidação arquitetural interna e a implementação da API mínima, a camada de entrega foi validada com sucesso em dois níveis:

- validação manual via Swagger/OpenAPI
- validação automatizada via testes HTTP de integração

Também foi executada a suíte completa do projeto com sucesso.

### Resultado atual

- `test_search_routes.py` passando
- `test_fitment_routes.py` passando
- suíte completa com **86 testes passando**
- execução geral com **100% green**

---

## Estado consolidado do projeto

### 1. Banco e infraestrutura
Concluído:

- schema principal estruturado
- seeds existentes
- views documentadas
- ambiente local com Docker
- banco de teste isolado
- conexão centralizada em `src/shared/db.py`
- configuração centralizada em `src/shared/config.py`

### 2. Ingestão FIPE
Concluído em camadas separadas:

- `src/ingestion/collectors/fipe_api_collector.py`
- `src/ingestion/parsers/fipe_parser.py`
- `src/ingestion/loaders/vehicle_reference_loader.py`

Status atual:

- collector implementado
- parser implementado
- loader implementado
- contrato de importação definido
- orquestração ponta a ponta ainda não implementada na CLI

### 3. Equivalência e clusterização
Concluído:

- motor puro de equivalência
- geração de clusters
- persistência de clusters discovery
- reutilização de clusters existentes
- idempotência do loader de equivalência

### 4. Camada oficial de consultas
Concluído:

`src/catalog/query_service.py` centraliza:

- busca por código
- busca por nome de peça
- busca por tipo de peça
- busca por alias de tipo de peça
- busca de equivalentes por código
- busca de peças por veículo
- busca de peças por motor
- fitment por filtros comerciais

### 5. API mínima
Concluído:

- `src/delivery/api/main.py`
- `src/delivery/api/search_routes.py`
- `src/delivery/api/fitment_routes.py`
- `src/delivery/api/dependencies.py`

Endpoints mínimos implementados:

- `GET /health`
- `GET /search/code/{code}`
- `GET /search/part`
- `GET /search/part-type`
- `GET /search/part-type-alias`
- `GET /search/equivalents/{code}`
- `GET /fitment/vehicle/{vehicle_id}`
- `GET /fitment/motor/{motor_id}`
- `GET /fitment/search`

Validação concluída em dois níveis:

- validação manual via Swagger/OpenAPI
- validação automatizada via testes HTTP de integração

Resultado:

- aplicação sobe corretamente com Uvicorn
- `/docs` e `openapi.json` respondem corretamente
- rotas principais respondem corretamente
- contrato JSON padronizado em `count` + `items`

### 6. Testes
Estrutura consolidada:

- `tests/contract/...`
- `tests/unit/...`
- `tests/integration/...`
- `tests/placeholders/...`

Concluído recentemente:

- `tests/integration/api/test_search_routes.py`
- `tests/integration/api/test_fitment_routes.py`

Status consolidado:

- testes de busca passando
- testes de fitment passando
- suíte completa do projeto com **86 testes passando**

---

## Consolidações arquiteturais já fechadas

### Camada de catálogo
Concluído:

- unificação de `search_service.py` + `fitment_service.py`
- adoção de `query_service.py` como camada oficial de consultas

### Compatibilidade
Concluído na fronteira arquitetural:

- consolidação em `processing/compatibility/compatibility_engine.py`

### Revisão
Concluído na fronteira arquitetural:

- consolidação de evidência, inferência e decisão em `processing/review/review_service.py`

### Referência
Concluído na fronteira arquitetural:

- consolidação em `reference/reference_service.py`

### Testes
Concluído:

- reorganização da suíte conforme a arquitetura atual
- separação entre testes reais e placeholders
- alinhamento com o estado atual do schema e dos módulos

---

## Onde paramos exatamente

Paramos após:

- consolidação arquitetural interna
- implementação da API mínima
- validação manual completa dos endpoints
- criação dos testes HTTP de integração
- execução completa da suíte com **86 testes passando**

Ou seja:

- a base interna está consolidada
- a camada HTTP mínima está de pé
- a entrega já foi validada manualmente e automaticamente
- o principal gap agora não é mais estrutura de API

O próximo gap real é:

- fazer a API devolver dados reais coerentes
- alimentar o catálogo funcionalmente

---

## Próxima fase

**FASE 5 — ALIMENTAÇÃO FUNCIONAL DO CATÁLOGO E RETORNO REAL DE DADOS**

### Objetivo da próxima fase

Fazer o catálogo deixar de responder apenas estruturalmente e passar a responder com dados reais, por meio de:

- massa mínima funcional no banco
ou
- implementação da orquestração real da importação FIPE

### Ordem recomendada

1. inserir massa mínima funcional para busca
2. inserir massa mínima funcional para fitment
3. validar endpoints com retorno real (`count > 0`)
4. estabilizar o comportamento funcional da API
5. só depois retomar a CLI FIPE real

---

## Pendências imediatas

### 1. Massa mínima funcional
Inserir dados mínimos coerentes para validar resposta real em:

- busca por código
- busca por equivalentes
- busca por nome de peça
- busca por tipo de peça
- fitment por veículo
- fitment por motor
- fitment por filtros comerciais

### 2. Alimentação real do catálogo
A FIPE ainda não alimenta o catálogo automaticamente de ponta a ponta.

Status atual:

- collector existe
- parser existe
- loader existe
- CLI de importação ainda não executa o fluxo real completo

### 3. Revisão do `requirements.txt`
Deixar o arquivo coerente com o stack efetivamente usado no projeto, especialmente:

- FastAPI
- Uvicorn
- Requests
- psycopg3
- pytest
- httpx

### 4. Fechamento funcional da API
Após popular dados reais, repetir a validação dos endpoints para confirmar:

- `count > 0`
- coerência do payload
- consistência entre banco e resposta da API

---

## Pontos de atenção técnicos

- a API mínima consulta apenas o banco
- a API mínima não consome a FIPE diretamente
- a FIPE ainda não alimenta o catálogo automaticamente de ponta a ponta
- o catálogo só retornará dados reais quando houver massa funcional persistida
- manter `query_service.py` como única camada de consulta nesta etapa
- evitar abrir nova frente de publicação, revisão avançada ou compatibilidade profunda antes de fechar a alimentação funcional do catálogo

---

## Marco atual

**API mínima de busca + fitment implementada, validada manualmente e validada automaticamente com 86 testes passando.**

## Próximo passo recomendado

**Iniciar a fase de alimentação funcional do catálogo, começando por massa mínima coerente para busca e fitment.**