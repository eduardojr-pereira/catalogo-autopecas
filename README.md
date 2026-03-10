# Catálogo Técnico Automotivo Inteligente

## Visão do Projeto

Este projeto tem como objetivo construir um **catálogo técnico automotivo automatizado**, capaz de coletar dados de peças diretamente da internet, estruturar essas informações e disponibilizá-las através de uma API e de uma interface web simples.

O sistema foi projetado inicialmente como um **MVP (Minimum Viable Product)** para validação técnica e funcional, mas com arquitetura preparada para evoluir posteriormente para um **SaaS escalável com inteligência artificial**.

---

# Objetivos

Construir um sistema que:

* colete dados técnicos de peças automotivas automaticamente da internet
* estruture informações técnicas relevantes
* relacione **veículos ↔ peças ↔ códigos OEM ↔ equivalentes**
* permita busca simples para usuários não técnicos
* possa evoluir para um **catálogo automotivo escalável e monetizável**

---

# Arquitetura do MVP

O sistema funciona em um pipeline simples de coleta e estruturação de dados.

```
Usuário busca peça
        ↓
Google Custom Search API
        ↓
lista de páginas relevantes
        ↓
scraper coleta conteúdo das páginas
        ↓
extração de dados técnicos
        ↓
armazenamento em banco estruturado
        ↓
API consulta dados
        ↓
interface web exibe resultados
```

---

# Tecnologias Utilizadas

## Backend

* Python
* FastAPI

Responsável por:

* criação da API
* orquestração do pipeline
* consulta ao banco de dados

---

## Web Scraping

* Requests
* Beautiful Soup

Responsável por:

* coletar páginas da internet
* extrair conteúdo textual
* identificar padrões técnicos

---

## Busca na Internet

* Google Custom Search API

Responsável por:

* encontrar páginas relevantes sobre peças automotivas
* alimentar o sistema de scraping

---

## Banco de Dados

### MVP

SQLite

Motivos:

* leve
* fácil de configurar
* ideal para prototipagem

### Evolução futura

PostgreSQL

Permitirá:

* escalabilidade
* múltiplos usuários
* alta performance
* suporte a SaaS

---

## Frontend

* HTML
* JavaScript
* CSS

Interface simples para:

* buscar peças
* visualizar informações técnicas
* testar a API

---

# Estrutura do Projeto

```
catalogo_autopecas
│
├── api
│   └── main.py
│
├── scraper
│   ├── google_search.py
│   ├── page_scraper.py
│   ├── detect_oem.py
│   └── extract_specs.py
│
├── database
│   ├── connection.py
│   ├── models.py
│   └── insert_data.py
│
├── services
│   └── catalog_builder.py
│
├── ai
│   └── (reservado para futuras integrações de IA)
│
├── frontend
│   ├── index.html
│   ├── app.js
│   └── style.css
│
├── data
│   └── catalogo.db
│
├── requirements.txt
└── README.md
```

---

# Descrição dos Módulos

## api/

Contém a API principal do sistema.

Responsável por:

* expor endpoints de consulta
* integrar banco de dados com frontend
* permitir integração com sistemas externos

Arquivo principal:

```
main.py
```

---

## scraper/

Responsável pela coleta de dados na internet.

### google_search.py

Consulta o Google Custom Search API e retorna uma lista de URLs relevantes.

---

### page_scraper.py

Acessa as páginas encontradas e extrai o conteúdo textual.

---

### detect_oem.py

Identifica padrões de **códigos OEM** presentes no texto.

---

### extract_specs.py

Extrai informações técnicas como:

* dimensões
* peso
* material
* aplicações

---

## database/

Responsável pela estruturação e persistência dos dados.

### connection.py

Gerencia conexão com o banco SQLite.

---

### models.py

Define a estrutura das tabelas do catálogo.

---

### insert_data.py

Insere dados coletados pelo scraper no banco de dados.

---

## services/

Camada de **lógica de negócio do sistema**.

Arquivo principal:

```
catalog_builder.py
```

Responsável por orquestrar o fluxo:

```
buscar peça
↓
coletar páginas
↓
extrair informações
↓
estruturar dados
↓
salvar no banco
```

---

## ai/

Diretório reservado para futuras integrações com **Inteligência Artificial**.

Possíveis módulos futuros:

```
ai_extractor.py
vehicle_normalizer.py
data_validator.py
semantic_search.py
```

Esses módulos permitirão:

* extração semântica de dados
* normalização automática de veículos
* validação inteligente de informações
* busca por linguagem natural

---

# Modelo de Dados da Peça

Cada peça no catálogo idealmente conterá as seguintes informações:

### Peça Base

```
Pastilha de freio dianteira
```

---

### Código OEM

```
04465-0F010
```

---

### Equivalentes

```
TRW CDB1234
Bosch BP1234
```

---

### Aplicação em Veículos

```
Toyota Corolla 2014-2017
```

---

### Dimensões

```
altura
largura
espessura
```

---

### Material

```
cerâmica
```

---

### Posição no Veículo

```
dianteira
```

---

### Peso

```
1.2 kg
```

---

# Evolução Planejada (Futuro)

Após validação do MVP, o sistema poderá evoluir para incluir:

### Inteligência Artificial

* extração semântica de dados técnicos
* normalização automática de veículos
* detecção de equivalentes
* validação de dados entre múltiplas fontes

---

### Busca Inteligente

Permitir consultas como:

```
pastilha corolla 2015
```

ou

```
qual pastilha serve no corolla 2016?
```

---

### Expansão Automática do Catálogo

O sistema poderá descobrir automaticamente novas peças a partir de:

* códigos OEM
* equivalentes
* aplicações em veículos

---

### Transformação em SaaS

Possível evolução para plataforma com:

* assinatura mensal
* catálogo técnico completo
* integração com lojas de autopeças
* busca por placa ou chassi

---

# Status do Projeto

Fase atual:

**MVP técnico em desenvolvimento**

Objetivo imediato:

* validar pipeline de coleta
* estruturar banco de dados
* disponibilizar consulta via API

---

# Licença

Projeto experimental de pesquisa e desenvolvimento.
