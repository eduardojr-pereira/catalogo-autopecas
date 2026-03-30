# Arquitetura de Dados — Catálogo Automotivo Inteligente

## 1. Objetivo deste documento

Este documento descreve a arquitetura de dados do projeto **Catálogo Automotivo Inteligente**
com foco na modelagem conceitual e na organização do banco PostgreSQL.

O objetivo é oferecer uma visão técnica clara para onboarding de desenvolvedores,
analistas de dados e responsáveis por evolução de domínio.

O escopo deste material cobre:

- separação por schemas;
- entidades centrais;
- fluxo de evolução de dados;
- princípios de modelagem adotados;
- diretrizes de rastreabilidade, auditoria e versionamento.

> Observação: este documento foca em **conceitos de modelagem e organização**,
> não em scripts SQL completos.

---

## 2. Contexto de negócio e motivação

No domínio de autopeças, o mesmo item pode ser representado por múltiplos códigos,
com nomenclaturas diferentes entre fabricantes, distribuidores e fontes de mercado.

Além da variação de códigos, há desafios adicionais:

- equivalências técnicas incompletas;
- inconsistências de aplicação por veículo/motor;
- dependência de interpretação humana para decisões críticas;
- necessidade de histórico para auditoria técnica;
- necessidade de publicação controlada por versão.

A arquitetura de dados foi desenhada para resolver esse cenário com uma abordagem
progressiva, em camadas, onde cada schema tem responsabilidade explícita.

---

## 3. Visão geral da arquitetura de dados

A base PostgreSQL é organizada em **cinco schemas funcionais**:

1. `reference`
2. `discovery`
3. `catalog`
4. `compatibility`
5. `publication`

Essa divisão não é apenas organizacional; ela materializa os estágios de maturidade
do dado dentro do ciclo de vida do catálogo.

Em termos conceituais, o fluxo principal é:

```text
reference
   ↓
discovery
   ↓
catalog
   ↓
compatibility
   ↓
publication
```

Leitura funcional desse fluxo:

- dados estruturais do domínio;
- dados descobertos automaticamente;
- catálogo consolidado para consulta;
- decisões técnicas auditáveis;
- snapshots publicados e versionados.

---

## 4. Princípios de modelagem adotados

### 4.1 Separação entre descoberta e verdade consolidada

A arquitetura distingue explicitamente:

- o que foi **coletado/descoberto** (`discovery`);
- o que foi **consolidado para operação** (`catalog`).

Esse desacoplamento evita que sinais fracos ou hipóteses automáticas impactem
imediatamente o catálogo principal.

### 4.2 Rastreabilidade de evidências

Toda inferência relevante deve poder ser rastreada para:

- fonte;
- dado bruto coletado;
- data/hora de coleta;
- confiança associada.

Isso permite revisão técnica posterior e reprocessamento com critérios novos.

### 4.3 Estrutura preparada para ingestão automática

A modelagem suporta alto volume de entrada com baixa fricção:

- entidades de coleta simples;
- armazenamento de conteúdo bruto;
- separação de dados transitórios versus estáveis;
- índices direcionados a lookup técnico.

### 4.4 Capacidade de auditoria técnica

As decisões de compatibilidade precisam registrar:

- regra aplicada (quando houver);
- evidências associadas;
- decisão final;
- nível de confiança;
- observações técnicas.

Assim, cada decisão torna-se explicável e auditável.

### 4.5 Suporte a versionamento do catálogo

Publicação não é sobrescrita destrutiva.

Em vez disso, o modelo preserva snapshots por versão para:

- reproduzir estado histórico;
- comparar versões;
- rollback operacional;
- governança de mudança.

---

## 5. Schema `reference` — base estrutural do domínio

### 5.1 Papel do schema

O schema `reference` concentra dados estruturais e domínios relativamente estáveis.

Ele funciona como alicerce para os demais schemas e oferece:

- vocabulário controlado;
- taxonomias técnicas;
- estrutura automotiva canônica;
- chaves de referência para integridade relacional.

### 5.2 Grupos de entidades em `reference`

#### 5.2.1 Fabricantes e taxonomia de peças

- `manufacturers`: fabricantes de peças;
- `part_types`: tipos técnicos de peças;
- `part_type_aliases`: variações comerciais e sinônimos de tipos.

Essa camada reduz ambiguidade na busca e no mapeamento entre fontes.

#### 5.2.2 Domínios canônicos auxiliares

Domínios de classificação usados em múltiplos pontos:

- `position_types` (posição de aplicação);
- `side_types` (lado de aplicação);
- `fuel_types` (combustível);
- `body_types` (carroceria);
- `attribute_units` e `attribute_definitions` (atributos técnicos).

Esses domínios reduzem texto livre e aumentam consistência semântica.

#### 5.2.3 Estrutura automotiva de veículos

Modelagem central de veículos com hierarquia explícita:

- `vehicle_brands`;
- `vehicle_models`;
- `vehicles`.

Hierarquia conceitual:

```text
vehicle_brands (marca)
   └── vehicle_models (modelo)
          └── vehicles (configuração/ano/versão)
```

Essa estrutura está preparada para integração com fontes padronizadas de mercado,
incluindo códigos externos quando disponíveis.

#### 5.2.4 Estrutura de motores e associação com veículos

- `motors` define o motor como entidade técnica independente;
- `vehicle_motors` materializa a relação N:N entre veículos e motores.

Esse desenho é essencial para fitment técnico, pois uma peça pode depender
simultaneamente de características de veículo e motor.

### 5.3 Entidades-chave solicitadas neste documento

#### `vehicle_brands`

Representa a marca automotiva (ex.: Honda, Toyota, Fiat).

Função no modelo:

- raiz da taxonomia de veículos;
- ponto de normalização de nomes de marca;
- referência para modelos.

#### `vehicle_models`

Representa o modelo associado a uma marca (ex.: Civic, Corolla, Gol).

Função no modelo:

- segmentar a linha de produto da marca;
- viabilizar deduplicação por marca+nome normalizado;
- servir de ponte para as configurações reais em `vehicles`.

#### `vehicles`

Representa uma configuração de veículo no catálogo técnico,
com dimensões como ano/modelo/versão e metadados complementares.

Função no modelo:

- granularidade de aplicação de peça;
- referência para relações com motores;
- suporte a transição controlada entre campos textuais e canônicos.

#### `motors`

Representa o motor como entidade reutilizável no domínio.

Função no modelo:

- centralizar características técnicas do conjunto motriz;
- permitir aplicações específicas por motor;
- reduzir duplicidade quando o mesmo motor equipa múltiplos veículos.

#### `vehicle_motors`

Entidade associativa para relação N:N veículo ↔ motor.

Função no modelo:

- mapear combinações válidas;
- suportar busca por interseção veículo + motor;
- evitar redundância de atributos técnicos em múltiplas tabelas.

---

## 6. Schema `discovery` — aquisição e hipótese de conhecimento

### 6.1 Papel do schema

O schema `discovery` registra dados obtidos automaticamente a partir de fontes externas.

Essa camada não representa verdade final; representa **sinais coletados**,
com diferentes níveis de confiança.

### 6.2 Objetivo de negócio

Preservar o máximo de informação útil para análise posterior,
sem bloquear ingestão por causa de incerteza inicial.

### 6.3 Entidades centrais

- `sources`: catálogo de origens de dados;
- `codes`: códigos de peças descobertos;
- `code_evidence`: evidências associadas a cada código;
- `code_equivalences`: hipóteses/descobertas de equivalência entre códigos.

### 6.4 Entidades-chave solicitadas neste documento

#### `codes`

Representa códigos de peça vinculados a fabricantes.

Função no modelo:

- unidade primária de descoberta;
- base para detecção de equivalências;
- elo entre evidência bruta e consolidação em clusters.

#### `code_evidence`

Representa evidência coletada para um código,
com contexto de origem e conteúdo bruto.

Função no modelo:

- lastro técnico da descoberta;
- suporte a auditoria e revisão;
- fonte para enriquecimento de confiança.

### 6.5 Equivalências descobertas

A entidade `code_equivalences` permite representar relações entre pares de códigos
com metadados de tipo, status de validação e confiança.

Conceitos importantes:

- equivalência pode nascer como suspeita;
- validação pode evoluir ao longo do tempo;
- confiança é contínua e revisável;
- pares são tratados de forma não-direcional para evitar duplicidade lógica.

### 6.6 Decisões de modelagem relevantes em `discovery`

- ingestão orientada a append e enriquecimento incremental;
- minimização de perda de dado coletado;
- preservação de contexto de origem;
- separação entre fato observado e interpretação consolidada.

---

## 7. Schema `catalog` — verdade operacional consolidada

### 7.1 Papel do schema

O schema `catalog` representa o estado operacional do catálogo,
pronto para consulta técnica e consumo por APIs.

Ele recebe entradas de `discovery`, mas aplica estruturação para uso consistente.

### 7.2 Entidades centrais

- `parts`: peça consolidada;
- `part_attributes`: atributos técnicos da peça;
- `clusters`: agrupamentos de códigos equivalentes;
- `cluster_codes`: vínculo entre cluster e códigos de `discovery`;
- `applications`: aplicações técnicas da peça/cluster em veículo/motor.

### 7.3 Entidades-chave solicitadas neste documento

#### `clusters`

Representa agrupamentos de códigos considerados equivalentes
ou relacionados à mesma peça consolidada.

Função no modelo:

- núcleo de unificação entre múltiplos códigos de mercado;
- abstração para busca técnica;
- ponte entre descoberta e aplicação.

#### `cluster_codes`

Tabela associativa entre cluster e código descoberto.

Função no modelo:

- rastrear quais códigos alimentam um cluster;
- preservar ligação com histórico de descoberta;
- permitir evolução incremental de agrupamentos.

#### `applications`

Representa aplicação técnica de um cluster em um contexto automotivo.

Esse contexto pode ser definido por:

- `vehicle_id`;
- `motor_id`;
- ou ambos, conforme granularidade técnica necessária.

A entidade também contempla metadados de posição/lado/confiança,
importantes para qualidade de fitment.

### 7.4 Conceito de consolidação

Consolidar não significa apagar origem.

No modelo adotado:

- a origem é preservada em `discovery`;
- a visão utilizável é disponibilizada em `catalog`;
- a relação entre ambas é explícita (ex.: `cluster_codes`).

Isso mantém o catálogo operável sem perder rastreabilidade.

---

## 8. Schema `compatibility` — avaliação técnica auditável

### 8.1 Papel do schema

O schema `compatibility` formaliza a camada de decisão técnica,
onde aplicações propostas podem ser avaliadas e classificadas.

É o ponto em que regras, evidências e decisão se conectam.

### 8.2 Entidades centrais

- `rules`: regras técnicas com expressão estruturada;
- `evidence`: evidência de compatibilidade por aplicação;
- `decisions`: decisão final (ou em progresso) por aplicação.

### 8.3 Modelo de governança técnica

A arquitetura permite coexistência de:

- decisões inferidas automaticamente;
- decisões pendentes de revisão;
- decisões aprovadas/rejeitadas com justificativa.

Com isso, o sistema suporta operação híbrida:

- automação para escala;
- revisão humana para casos críticos;
- histórico completo para auditoria.

### 8.4 Papel de auditoria

Para cada aplicação avaliada, é possível recuperar:

- qual regra foi usada;
- quais evidências sustentam a avaliação;
- qual foi a decisão;
- qual o nível de confiança associado;
- quando a decisão foi registrada.

Esse encadeamento é essencial para explicabilidade técnica.

---

## 9. Schema `publication` — versão publicada como produto

### 9.1 Papel do schema

O schema `publication` materializa o catálogo publicado em versões,
com controle de ciclo de publicação.

### 9.2 Entidades centrais

- `batches`: execução operacional da publicação;
- `catalog_versions`: versões numeradas do catálogo;
- `published_parts`: peças incluídas por versão;
- `published_applications`: aplicações incluídas por versão.

### 9.3 Conceito de snapshot versionado

Cada versão representa um snapshot lógico do catálogo disponibilizado.

Benefícios:

- reprodutibilidade de consultas históricas;
- trilha clara de evolução de conteúdo;
- governança de release técnico;
- base para rollback quando necessário.

### 9.4 Relação entre execução e versão

`batches` registra o processo (início/fim/status),
enquanto `catalog_versions` registra o artefato versionado.

Essa separação diferencia:

- estado da execução;
- estado do produto publicado.

---

## 10. Fluxo conceitual entre schemas

### 10.1 Fluxo macro

```text
reference  →  discovery  →  catalog  →  compatibility  →  publication
```

### 10.2 Etapa 1 — referência estrutural (`reference`)

A base de domínio é definida com:

- entidades canônicas;
- taxonomias estáveis;
- relacionamentos de veículo e motor.

Essa camada reduz ambiguidades para as etapas seguintes.

### 10.3 Etapa 2 — descoberta (`discovery`)

Dados externos são ingeridos e transformados em:

- códigos;
- evidências;
- hipóteses de equivalência.

Não há imposição de verdade consolidada neste estágio.

### 10.4 Etapa 3 — consolidação (`catalog`)

Os sinais de descoberta são organizados em estruturas operacionais:

- peças;
- clusters;
- aplicações.

Aqui o dado passa de hipótese bruta para catálogo consultável.

### 10.5 Etapa 4 — decisão técnica (`compatibility`)

As aplicações são avaliadas tecnicamente com:

- regras;
- evidências complementares;
- decisões auditáveis.

Essa etapa controla qualidade técnica antes da publicação.

### 10.6 Etapa 5 — publicação (`publication`)

O conteúdo aprovado é encapsulado em versões publicadas,
com rastreio de execução por batch.

Resultado: catálogo versionado pronto para consumo estável.

---

## 11. Visão conceitual das entidades principais

### 11.1 Núcleo automotivo (veículo/motor)

```text
vehicle_brands
   └── vehicle_models
          └── vehicles
                 └── vehicle_motors ─── motors
```

Responsabilidade:

- estruturar o universo de aplicação de peças;
- suportar fitment por veículo, motor ou combinação;
- manter semântica técnica consistente.

### 11.2 Núcleo de descoberta de códigos

```text
codes
  ├── code_evidence
  └── code_equivalences
```

Responsabilidade:

- registrar coleta e sinais de equivalência;
- armazenar contexto de origem;
- permitir revisão e refinamento de confiança.

### 11.3 Núcleo de consolidação

```text
clusters ─── cluster_codes ─── codes
    │
    └── applications ─── (vehicles / motors)
```

Responsabilidade:

- converter códigos dispersos em unidades consultáveis;
- conectar equivalência de códigos a aplicações reais;
- manter ligação entre consolidado e descoberta.

---

## 12. Diretrizes de qualidade e integridade

### 12.1 Integridade referencial

A modelagem usa chaves estrangeiras para preservar consistência entre camadas,
com estratégias de deleção coerentes ao papel de cada entidade.

### 12.2 Normalização pragmática

O desenho prioriza:

- redução de redundância estrutural;
- manutenção de campos auxiliares quando úteis para transição/compatibilidade;
- equilíbrio entre pureza relacional e operação real.

### 12.3 Controle de confiança

Campos de `confidence_score` em entidades críticas permitem:

- diferenciar hipótese forte de fraca;
- priorizar revisão;
- alimentar decisão técnica baseada em evidência.

### 12.4 Evolução incremental

A arquitetura é orientada a evolução contínua,
sem exigir refatorações destrutivas para incorporar novas fontes.

---

## 13. Como interpretar “verdade” no sistema

No contexto deste projeto, “verdade” é tratada em níveis:

1. **Observado**: dado coletado (`discovery`);
2. **Consolidado operacional**: dado estruturado para consumo (`catalog`);
3. **Validado tecnicamente**: dado com decisão de compatibilidade (`compatibility`);
4. **Publicado**: snapshot oficial por versão (`publication`).

Esse modelo reduz risco de decisões prematuras e melhora governança do catálogo.

---

## 14. Benefícios arquiteturais para o produto

A organização por schemas e estágios de maturidade traz ganhos concretos:

- melhor isolamento de responsabilidades;
- menor acoplamento entre coleta e publicação;
- maior explicabilidade das decisões;
- facilidade para auditoria técnica;
- base sólida para escalar ingestão automática;
- versionamento robusto para operação comercial.

---

## 15. Riscos controlados pelo desenho atual

### 15.1 Mistura entre hipótese e dado consolidado

Mitigação: separação entre `discovery` e `catalog`.

### 15.2 Perda de contexto de origem

Mitigação: uso de `sources` e `code_evidence`.

### 15.3 Decisão técnica opaca

Mitigação: encadeamento `rules` + `evidence` + `decisions`.

### 15.4 Publicação sem trilha histórica

Mitigação: `batches` + `catalog_versions` + itens publicados por versão.

---

## 16. Diretrizes para novos desenvolvedores

### 16.1 Ao integrar nova fonte externa

- registre/identifique a origem em `discovery.sources`;
- persista códigos em `discovery.codes`;
- preserve contexto bruto em `discovery.code_evidence`;
- evite publicar inferências diretamente em `catalog`.

### 16.2 Ao criar lógica de consolidação

- trate `clusters` como unidade de equivalência operacional;
- vincule sempre os códigos de origem em `cluster_codes`;
- gere `applications` com confiança e contexto suficientes para revisão.

### 16.3 Ao implementar revisão técnica

- prefira registrar decisão em `compatibility.decisions`;
- associe evidências relevantes em `compatibility.evidence`;
- mantenha observações técnicas objetivas e auditáveis.

### 16.4 Ao publicar versão

- execute publicação com controle por `batches`;
- crie `catalog_versions` monotônicas;
- congele peças e aplicações via tabelas de publicação;
- preserve histórico, sem sobrescrever snapshots anteriores.

---

## 17. Considerações sobre evolução futura

A arquitetura atual já oferece pontos de extensão naturais:

- novos tipos de evidência em discovery/compatibility;
- enriquecimento de atributos técnicos em `catalog.part_attributes`;
- incremento de regras em `compatibility.rules`;
- pipelines mais sofisticados de publicação.

Como a separação de responsabilidades está clara,
é possível evoluir etapas específicas sem comprometer o fluxo completo.

---
## 18. Resumo executivo da arquitetura
A arquitetura de dados do Catálogo Automotivo Inteligente adota um modelo em camadas
que combina:
- base referencial sólida (`reference`);
- descoberta ampla e rastreável (`discovery`);
- consolidação operacional (`catalog`);
- decisão técnica auditável (`compatibility`);
- publicação versionada (`publication`).

Com esse desenho, o sistema consegue tratar incerteza de dados de mercado,
ao mesmo tempo em que entrega catálogo confiável, auditável e evolutivo.
Esse equilíbrio entre ingestão automática e governança técnica é o elemento central da estratégia de dados do projeto.