# Importação FIPE

## Objetivo

Documentar o fluxo inicial de importação de dados da FIPE para popular:

- `reference.vehicle_brands`
- `reference.vehicle_models`
- `reference.vehicles`

A finalidade desta fase é construir a base inicial de veículos do projeto
Catálogo Automotivo Inteligente com rastreabilidade mínima, idempotência
e baixo acoplamento ao formato externo.

---

## Escopo da fase

Esta fase cobre:

1. importação de marcas;
2. importação de modelos por marca;
3. importação de anos/variações por modelo;
4. persistência em tabelas de referência do domínio interno.

Esta fase não cobre ainda:

- enriquecimento técnico avançado;
- vínculo com peças;
- fitment completo;
- taxonomia refinada de versões;
- consolidação semântica avançada além do mínimo necessário.

---

## Estrutura adotada

A importação segue o padrão arquitetural já existente no projeto:

- `src/ingestion/collectors`
- `src/ingestion/parsers`
- `src/ingestion/loaders`
- `src/delivery/cli`

### Arquivos previstos

- `src/ingestion/collectors/fipe_api_collector.py`
- `src/ingestion/parsers/fipe_parser.py`
- `src/ingestion/loaders/vehicle_reference_loader.py`
- `src/delivery/cli/import_fipe.py`

---

## Responsabilidade por camada

### Collector

Responsável por:

- comunicação com a API FIPE;
- tratamento de timeout/retry;
- retorno de payload bruto.

Não deve:

- conhecer schema interno;
- persistir dados;
- aplicar regras de domínio.

### Parser

Responsável por:

- transformar payload bruto em estrutura intermediária;
- normalizar nomes;
- extrair atributos relevantes do texto externo.

Não deve:

- chamar API;
- gravar no banco.

### Loader

Responsável por:

- persistir dados parseados;
- garantir idempotência;
- preservar integridade referencial.

Não deve:

- interpretar payload bruto;
- concentrar regras HTTP.

### CLI

Responsável por:

- orquestrar as etapas da importação;
- servir como ponto de entrada operacional;
- permitir execução futura por subetapas.

---

## Estratégia de identidade externa

A FIPE não deve definir a identidade primária do domínio interno.

Decisão adotada:

- usar chave primária interna própria;
- armazenar rastreabilidade externa com:
  - `external_source = "fipe"`
  - `external_code = <codigo_externo>`

Essa decisão permite integrar futuramente outras fontes além da FIPE sem
quebrar o domínio interno.

---

## Estratégia de idempotência

A importação deve ser reexecutável sem duplicar registros.

### Marcas
Chave lógica principal:
- `external_source + external_code`

Defesa secundária:
- nome normalizado

### Modelos
Chave lógica principal:
- `brand + external_source + external_code`

Defesa secundária:
- `brand + normalized_name`

### Veículos
Chave lógica principal:
- `model + external_source + external_code`

---

## Fluxo esperado

### Importação de marcas
1. coletar marcas;
2. parsear registros;
3. persistir com upsert.

### Importação de modelos
1. iterar sobre marcas;
2. coletar modelos por marca;
3. parsear registros;
4. persistir com upsert.

### Importação de veículos
1. iterar sobre marcas e modelos;
2. coletar anos/variações;
3. parsear registros;
4. persistir com upsert.

---

## Riscos conhecidos

- a FIPE não foi desenhada como catálogo técnico de autopeças;
- há risco de diferença entre nomenclatura comercial e nomenclatura técnica;
- ano, combustível e versão podem vir acoplados em descrições textuais;
- há risco de duplicidade semântica entre registros.

---

## Próximos passos

1. implementar o coletor HTTP;
2. implementar o parser;
3. implementar o loader;
4. implementar a CLI real;
5. adicionar testes com fixtures;
6. executar carga piloto local.