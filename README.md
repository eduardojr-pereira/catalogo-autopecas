# Catálogo Automotivo Inteligente

Sistema de **catalogação técnica de autopeças** que relaciona veículos, peças, códigos OEM e equivalentes comerciais.

O objetivo do projeto é construir uma base estruturada que permita identificar rapidamente **qual peça serve em qual veículo**, mesmo quando o usuário **não conhece o código OEM**.

Este projeto simula a arquitetura de dados utilizada por **catálogos automotivos profissionais**, utilizados por autopeças, distribuidores e oficinas.

---

# Problema de Negócio

No mercado automotivo, identificar a peça correta para um veículo pode ser difícil porque:

* o cliente raramente possui o **código OEM**
* diferentes fabricantes possuem **códigos equivalentes**
* a mesma peça pode servir para **diversos veículos**
* catálogos de fornecedores são **fragmentados**

Este projeto resolve esse problema criando um **catálogo estruturado e pesquisável**.

---

# Objetivos do Projeto

Construir um sistema capaz de:

* coletar dados automotivos automaticamente
* estruturar relações entre **veículos e peças**
* mapear **OEM e equivalentes**
* permitir busca por **veículo + nome da peça**
* criar uma base escalável para APIs ou SaaS

---

# Tecnologias Utilizadas

* Python — coleta e processamento de dados
* PostgreSQL — banco de dados relacional
* Docker — ambiente reproduzível
* Web Scraping — coleta de informações técnicas
* APIs automotivas — enriquecimento de dados

---

# Arquitetura do Projeto

```
Internet
   ↓
Coleta automática (Scraping / APIs)
   ↓
Pipeline de processamento
   ↓
Banco de dados estruturado
   ↓
Catálogo automotivo pesquisável
```

---

# Modelo Conceitual

O catálogo é estruturado em quatro entidades principais:

```
Veículo
   ↓
Aplicação
   ↓
Peça
   ↓
OEM / Equivalentes
```

Exemplo:

```
Veículo
Gol 1.6 2015

Peça
Pastilha de Freio

OEM
VW 5U0698151

Equivalentes
Bosch BP1234
Cobreq N1234
```

---

# Estrutura do Projeto

```
catalogo-auto
│
├── data
│   └── datasets brutos
│
├── scripts
│   ├── coleta
│   ├── processamento
│   └── carga
│
├── database
│   └── schema.sql
│
├── docker
│   └── docker-compose.yml
│
├── requirements.txt
│
└── README.md
```

---

# Configuração do Ambiente

Este projeto utiliza **Docker** para garantir reprodutibilidade.

## 1 — Clonar o repositório

```
git clone https://github.com/seuusuario/catalogo-auto.git
```

```
cd catalogo-auto
```

---

## 2 — Subir o banco de dados

```
docker compose up -d
```

Isso iniciará um container com **PostgreSQL**.

---

## 3 — Instalar dependências Python

```
pip install -r requirements.txt
```

---

# Pipeline de Dados

O pipeline segue as seguintes etapas:

### 1. Identificação da peça

Entrada inicial:

```
veículo
nome da peça
```

Exemplo:

```
Gol 1.6 2015
pastilha de freio
```

---

### 2. Descoberta de código OEM

Coleta automática em:

* catálogos online
* distribuidores
* fabricantes

---

### 3. Expansão de equivalentes

Após obter o OEM:

```
OEM → equivalentes comerciais
```

Exemplo:

```
OEM VW 5U0698151

equivalentes:

Bosch
TRW
Cobreq
Fras-le
```

---

### 4. Estruturação no banco

Dados são inseridos no banco com relações:

```
veiculos
pecas
oem
equivalentes
aplicacoes
```

---

# Roadmap do Projeto

## Fase 1 — Estrutura inicial

* [x] Definição do modelo de dados
* [x] Estrutura do repositório
* [ ] Criação do banco

---

## Fase 2 — Coleta de dados

* [ ] Scraping de catálogos automotivos
* [ ] Integração com APIs de veículos
* [ ] Normalização de nomes de peças

---

## Fase 3 — Inteligência do catálogo

* [ ] Busca por veículo
* [ ] Busca por nome da peça
* [ ] Sugestão automática de equivalentes

---

## Fase 4 — Interface

* [ ] API de consulta
* [ ] Interface web simples
* [ ] Integração com sistemas de autopeças

---

# Possíveis Evoluções

O projeto pode evoluir para:

* API pública de consulta de peças
* integração com sistemas ERP de autopeças
* sistema de recomendação de peças
* catálogo SaaS para distribuidores

---

# Motivação

Este projeto foi desenvolvido como **projeto de portfólio em engenharia e ciência de dados**, demonstrando habilidades em:

* modelagem de dados
* engenharia de dados
* automação de coleta de dados
* arquitetura de pipelines

---

# Autor

Eduardo Pereira

Economista e Cientista de Dados interessado em **engenharia de dados aplicada a problemas reais de negócio**.

---

# Licença

Projeto de uso educacional e experimental.
