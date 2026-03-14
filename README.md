# Catálogo Automotivo Inteligente




# Visão Geral
Projeto em desenvolvimento para construção de um **catálogo técnico automotivo inteligente**, capaz de:
* descobrir códigos de peças automaticamente
* identificar equivalências entre fabricantes
* agrupar peças equivalentes em clusters
* relacionar peças com motores e veículos
* permitir busca por veículo, código ou peça

O objetivo final é criar uma **base estruturada de autopeças escalável**, que possa evoluir para APIs, ferramentas internas ou um SaaS.

### Problema de Negócio
No mercado automotivo, identificar a peça correta para um veículo pode ser difícil porque:

* o cliente raramente possui o código OEM
* diferentes fabricantes possuem códigos equivalentes
* a mesma peça pode servir para diversos veículos
* catálogos de fornecedores são fragmentados

Este projeto resolve esse problema criando um catálogo estruturado e pesquisável.

### Objetivos do Projeto
Construir um **catálogo automotivo inteligente e escalável**, capaz de consolidar informações de autopeças de múltiplas fontes e organizar essas informações em uma base consistente e consultável.

Capaz de:
* coletar dados automotivos automaticamente
* estruturar relações entre **veículos** e **peças**
* mapear OEM e equivalentes
* permitir busca por **veículo** + **nome da peça**
* criar uma base escalável para APIs ou SaaS

### Motivação

Este projeto foi desenvolvido como projeto de portfólio em engenharia e ciência de dados, demonstrando habilidades em:

* modelagem de dados
* engenharia de dados
* automação de coleta de dados
* arquitetura de pipelines

---
---

# Arquitetura do Projeto

O sistema está dividido em camadas principais:

```
Fontes de Dados
      ↓
Scrapers / APIs
      ↓
Data Raw
      ↓
Normalização de códigos
      ↓
Rede de equivalência
      ↓
Clusterização de peças
      ↓
Associação motor ↔ veículo
      ↓
Banco de dados do catálogo
```
---
---


# Estrutura do Projeto

```
catalogo_autopecas
│
├── database
│   └── schema.sql            # Estrutura do banco PostgreSQL
│
├── docker
│   └── docker-compose.yml    # Infraestrutura do banco com Docker
│
├── docs                      # Documentação do projeto
│
├── scripts                   # Scripts auxiliares
│
├── src                       # Código principal do sistema
│
├── tests                     # Testes
│
├── data                      # Arquivos de dados locais
│
├── venv                      # Ambiente virtual Python
│
├── requirements.txt
├── .gitignore
└── README.md
```

---
---

# Banco de Dados

O banco utiliza **PostgreSQL rodando em container Docker**.

Estrutura lógica do banco:

## Schemas

```
reference   → dados estruturais (fabricantes, veículos, motores)

discovery   → códigos de peças e equivalências descobertas

catalog     → clusters de peças e aplicações consolidadas
```

## Principais tabelas

```
reference.manufacturers
reference.vehicles
reference.motors
reference.vehicle_motors

discovery.codes
discovery.code_equivalences

catalog.clusters
catalog.cluster_codes
catalog.applications
```

## Como subir o banco localmente

Entre na pasta do projeto:

```
cd catalogo_autopecas/docker
```

Suba o banco:

```
docker compose up -d
```

Isso iniciará um container PostgreSQL.

### Conexão com o banco

```
host: localhost
port: 5432
database: catalogo
user: admin
password: admin
```

### Inicializar estrutura do banco

Executar o schema:

```
Get-Content ../database/schema.sql | docker exec -i catalogo_postgres psql -U admin -d catalogo
```

### Verificar tabelas

Entrar no banco:

```
docker exec -it catalogo_postgres psql -U admin -d catalogo
```

Listar tabelas:

```
\dt *.*
```

---
---

# Requisitos

* Docker Desktop
* WSL2 (Windows)
* Python 3.11+
* VSCode (recomendado)

---
---

# Roadmap do Projeto
### Fase 1 — Estrutura inicial
* [x] Definição do modelo de dados
* [x] Estrutura do repositório
* [x] Infraestrutura Docker
* [x] Banco PostgreSQL containerizado

### Fase 2 — Coleta de dados
* [ ] Scraping de catálogos automotivos
* [ ] Integração com APIs de veículos
* [ ] Normalização de nomes de peças

### Fase 3 — Inteligência do catálogo
* [ ] Busca por veículo
* [ ] Busca por nome da peça
* [ ] Sugestão automática de equivalentes

### Fase 4 — Interface
* [ ] API de consulta
* [ ] Interface web simples
* [ ] Integração com sistemas de autopeças

## Estado atual do projeto
### Infraestrutura Concluída
* Docker configurado
* PostgreSQL containerizado
* Schema inicial implementado
* Estrutura de diretórios definida

### Próximos Passos
* validação do modelo de dados
* normalização de códigos
* pipeline de ingestão
* coleta automática de dados de peças

---
---

## Possíveis Evoluções
* O projeto pode evoluir para:
* API pública de consulta de peças
* Integração com sistemas ERP de autopeças
* Sistema de recomendação de peças
* Catálogo SaaS para distribuidores

---
---

# Autor

Eduardo Pereira

Economista e Cientista de Dados interessado em engenharia de dados aplicada a problemas reais de negócio.

---
---

# Licença

Projeto de uso educacional e experimental.

---
---
