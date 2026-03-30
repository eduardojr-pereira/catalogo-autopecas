# Arquitetura do Sistema — Catálogo Automotivo

## 1. Visão geral

### 1.1 Contexto

O **Catálogo Automotivo Inteligente** organiza dados de autopeças para uso técnico e comercial.

O sistema foi desenhado para tratar desafios recorrentes do setor:

- variações de códigos entre fabricantes;
- equivalências com diferentes níveis de confiança;
- relação peça ↔ motor ↔ veículo (fitment) distribuída em fontes múltiplas;
- necessidade de revisão técnica antes de publicação.

### 1.2 Objetivo arquitetural

A arquitetura busca suportar, de ponta a ponta:

1. ingestão de dados externos;
2. descoberta de relações úteis;
3. consolidação progressiva em catálogo estável;
4. avaliação técnica de compatibilidade;
5. publicação versionada para consumo via API.

### 1.3 Stack principal

- **Python**
- **FastAPI**
- **PostgreSQL**
- **Docker**

### 1.4 Escopo desta documentação

Este documento descreve:

- princípios arquiteturais;
- arquitetura lógica do sistema;
- organização de dados por schemas;
- fluxo de dados;
- componentes principais;
- diretrizes de evolução futura.

---

## 2. Princípio arquitetural central

### 2.1 Separar descoberta de catálogo consolidado

A decisão estrutural mais importante é separar:

- **descoberta automatizada de dados**;
- **catálogo consolidado para uso operacional**.

No domínio automotivo, equivalência descoberta não significa identidade técnica absoluta.

Por isso, o pipeline não promove automaticamente toda descoberta para o catálogo publicado.

### 2.2 Implicações práticas

Essa separação garante que o sistema trate explicitamente quatro fases:

1. descoberta de dados;
2. validação técnica;
3. consolidação do catálogo;
4. publicação versionada.

### 2.3 Benefícios

- redução de falso positivo técnico;
- melhoria de auditabilidade;
- rastreio de evidências;
- previsibilidade para consumidores da API;
- evolução segura das regras de domínio.

---

## 3. Princípios arquiteturais do projeto

### 3.1 Separação entre descoberta e catálogo consolidado

A arquitetura define fronteiras claras para evitar mistura entre hipótese e verdade publicada.

- `discovery` trata dados descobertos e evidências.
- `catalog` trata entidades consolidadas.
- `publication` trata versões estáveis para consumo.

### 3.2 Rastreabilidade de evidências

Toda relação relevante deve manter contexto de origem e justificativa técnica.

Isso permite:

- revisar decisões;
- comparar fontes;
- evoluir regras com base em histórico real.

### 3.3 Decisões técnicas auditáveis

Decisões não devem ser caixas-pretas.

A arquitetura preserva trilha de:

- entrada observada;
- regra aplicada;
- resultado produzido;
- estado final publicado.

### 3.4 Versionamento de catálogo

O catálogo é tratado como ativo versionado, não como estado único mutável.

Com isso, o sistema suporta:

- estabilidade de contrato;
- comparação entre releases;
- rollback lógico;
- governança de publicação.

### 3.5 Escalabilidade para ingestão automática

A camada de discovery pode crescer em volume sem comprometer a qualidade do catálogo consolidado.

A arquitetura suporta ingestão contínua com separação de estágios.

---

## 4. Arquitetura lógica do sistema

## 4.1 Visão por camadas

A solução é organizada em camadas funcionais.

1. **Fontes e ingestão**
2. **Discovery layer**
3. **Rede de equivalências e clusterização**
4. **Consolidação de catálogo**
5. **Fitment e compatibilidade**
6. **Publicação versionada**
7. **API de entrega**

### 4.2 Fontes e ingestão

Responsável por coletar dados externos e estruturar entrada inicial.

Características:

- heterogeneidade de formato;
- variação de qualidade;
- necessidade de preservar metadados de origem.

### 4.3 Discovery layer

Responsável por gerar conhecimento inicial a partir de dados ingeridos.

Funções principais:

- normalização de códigos;
- descoberta de equivalências candidatas;
- armazenamento de evidências e scores.

### 4.4 Rede de equivalências

As equivalências descobertas são representadas como uma rede de relações.

Objetivo arquitetural:

- capturar conectividade entre códigos sem assumir identidade técnica final.

### 4.5 Clusterização

A clusterização agrupa códigos relacionados em conjuntos coerentes.

Objetivo arquitetural:

- reduzir fragmentação;
- preparar consolidação de peças;
- facilitar revisão técnica posterior.

### 4.6 Catálogo consolidado

Transforma agrupamentos e relações em entidades estáveis.

Objetivo arquitetural:

- oferecer base confiável para busca e operação de negócio.

### 4.7 Fitment

Relaciona peças com motores e veículos.

Objetivo arquitetural:

- estruturar aplicação técnica de forma consultável e revisável.

### 4.8 Compatibility engine

Avalia evidências e regras para determinar compatibilidade técnica.

Objetivo arquitetural:

- apoiar decisão com transparência e rastreabilidade.

### 4.9 Publication engine

Gera versões do catálogo a partir de estado consolidado e validado.

Objetivo arquitetural:

- disponibilizar snapshots estáveis para consumo externo.

### 4.10 API

Exposição final de capacidades técnicas e comerciais.

Capacidades principais:

- busca por código, peça ou veículo;
- consulta de fitment;
- operações de revisão/publicação.

---

## 5. Arquitetura de dados (PostgreSQL)

### 5.1 Organização por schemas especializados

O banco usa separação por contexto funcional.

#### `reference`

Dados estruturais estáveis de referência.

Exemplos:

- fabricantes;
- taxonomias;
- estruturas de veículos e motores;
- entidades canônicas.

#### `discovery`

Dados descobertos automaticamente.

Exemplos:

- códigos observados;
- evidências;
- equivalências candidatas;
- metadados de origem.

#### `catalog`

Dados consolidados para uso operacional.

Exemplos:

- peças consolidadas;
- clusters estabilizados;
- relações técnicas aprovadas.

#### `compatibility`

Regras e resultados de compatibilidade.

Exemplos:

- critérios de avaliação;
- resultados de engine;
- decisões técnicas rastreáveis.

#### `publication`

Snapshots e governança de release.

Exemplos:

- versões publicadas;
- estado de revisão;
- trilha temporal de publicação.

### 5.2 Por que essa estrutura é importante

A separação por schema protege o ciclo de vida do dado:

- hipótese em `discovery`;
- consolidação em `catalog`;
- decisão técnica em `compatibility`;
- disponibilização estável em `publication`.

### 5.3 Estabilidade versus mutabilidade

- `reference`: alta estabilidade.
- `discovery`: alta mutabilidade.
- `catalog`: mutabilidade controlada.
- `compatibility`: mutabilidade condicionada por regras.
- `publication`: snapshots estáveis por versão.

### 5.4 Governança e integridade

A arquitetura de dados reforça:

- rastreabilidade;
- isolamento de responsabilidade;
- auditoria de decisões;
- previsibilidade de consumo.

---

## 6. Fluxo arquitetural de dados

### 6.1 Fluxo conceitual

```text
Fontes externas
↓
Ingestão de dados
↓
Discovery Layer
↓
Rede de equivalências
↓
Clusterização
↓
Catálogo consolidado
↓
Fitment
↓
Compatibility Engine
↓
Publication Engine
↓
API
```

### 6.2 Etapas detalhadas

#### Etapa A — Fontes externas

Dados entram a partir de fontes variadas e com qualidade heterogênea.

#### Etapa B — Ingestão

O sistema estrutura os dados e preserva metadados de origem.

#### Etapa C — Discovery

São descobertos códigos, relações e equivalências com evidências.

#### Etapa D — Rede de equivalências

As relações são conectadas em uma estrutura que viabiliza análise de agrupamento.

#### Etapa E — Clusterização

Códigos relacionados são agrupados para formar base de consolidação.

#### Etapa F — Catálogo consolidado

Entidades estáveis são geradas para uso técnico e comercial.

#### Etapa G — Fitment

Peças são relacionadas a motores e veículos.

#### Etapa H — Compatibilidade

Regras técnicas avaliam consistência e aplicabilidade.

#### Etapa I — Publicação

O estado aprovado é versionado e publicado.

#### Etapa J — API

Clientes consomem dados técnicos e comerciais com base em versões estáveis.

---

## 7. Componentes principais do sistema

### 7.1 Discovery

**Papel:** coletar e registrar códigos e equivalências observadas.

Responsabilidades:

- processar entradas da ingestão;
- normalizar códigos;
- registrar evidências e contexto;
- produzir relações candidatas.

### 7.2 Clustering

**Papel:** agrupar códigos relacionados em clusters úteis.

Responsabilidades:

- organizar conectividade de equivalências;
- reduzir redundância de representações;
- preparar entrada para consolidação.

### 7.3 Catalog

**Papel:** consolidar peças e relações em visão estável.

Responsabilidades:

- formar entidades canônicas;
- sustentar consultas técnicas;
- servir de base para publicação.

### 7.4 Fitment Engine

**Papel:** mapear aplicação peça ↔ motor ↔ veículo.

Responsabilidades:

- estruturar relações de aplicação;
- combinar dados de catálogo e referência;
- preparar dados para avaliação de compatibilidade.

### 7.5 Compatibility Engine

**Papel:** avaliar evidências e regras técnicas.

Responsabilidades:

- aplicar critérios de decisão;
- classificar relações de compatibilidade;
- manter decisões auditáveis.

### 7.6 Publication Engine

**Papel:** gerar versões publicadas do catálogo.

Responsabilidades:

- selecionar estado consolidado apto;
- criar snapshot versionado;
- registrar metadados de release.

### 7.7 Search Engine

**Papel:** permitir busca por código, peça ou veículo.

Responsabilidades:

- oferecer consulta técnica e comercial;
- operar sobre catálogo consolidado/publicado;
- responder com previsibilidade por versão.

---

## 8. Mapeamento para estrutura atual do projeto

A base atual do projeto já contém serviços que refletem essa arquitetura.

### 8.1 Núcleo de processamento

- normalização de códigos;
- engine e scorer de equivalências;
- clusterização;
- consolidação;
- regras de fitment e compatibilidade.

### 8.2 Núcleo de catálogo

- serviços de partes;
- serviços de evidência e decisão;
- serviços de fitment, compatibilidade e busca;
- serviços de versionamento e publicação.

### 8.3 Entrega por API

- rotas de busca;
- rotas de fitment;
- rotas de revisão;
- rotas de publicação.

Essa organização reforça a separação entre processamento de domínio e exposição externa.

---

## 9. Princípios de design (aplicados ao domínio)

### 9.1 Modelagem orientada a domínio técnico

Conceitos arquiteturais centrais:

- código normalizado;
- equivalência com evidência;
- cluster técnico;
- fitment;
- compatibilidade;
- publicação versionada.

### 9.2 Fronteiras explícitas

Cada componente possui responsabilidade única predominante.

Impacto esperado:

- menor acoplamento;
- maior clareza de evolução;
- testes mais direcionados.

### 9.3 Auditabilidade por construção

A arquitetura é projetada para permitir explicação de decisões técnicas.

Perguntas que o sistema deve responder:

- de onde veio esse dado?
- qual evidência sustentou a relação?
- qual regra foi aplicada?
- em qual versão isso foi publicado?

### 9.4 Evolução incremental segura

Novas regras e novas fontes podem ser introduzidas sem romper contratos publicados.

A estratégia é:

- experimentar em discovery;
- validar em compatibility;
- consolidar em catalog;
- publicar em versão controlada.

### 9.5 Escalabilidade com governança

Escalar não é apenas processar mais dados, mas manter qualidade e confiabilidade.

A arquitetura prioriza:

- separação de estágios;
- rastreabilidade;
- versionamento;
- revisabilidade.

---

## 10. Evolução futura

### 10.1 Evolução de ingestão

- ampliar conectores de fontes;
- formalizar níveis de confiança por origem;
- automatizar validações de qualidade de entrada.

### 10.2 Evolução de discovery e scoring

- calibrar scorers por histórico técnico;
- medir precisão por tipo de equivalência;
- diferenciar com mais precisão sugestão e decisão.

### 10.3 Evolução de compatibilidade

- enriquecer conjunto de regras;
- aumentar explicabilidade de decisões;
- criar métricas de desempenho técnico por regra.

### 10.4 Evolução de publicação

- diffs entre versões;
- trilha de aprovação mais explícita;
- critérios de prontidão de release por domínio.

### 10.5 Evolução de busca e API

- filtros técnicos avançados;
- respostas orientadas a contexto de versão;
- endpoints de rastreabilidade para auditoria funcional.

---

## 11. Conclusão

A arquitetura do Catálogo Automotivo Inteligente foi concebida para equilibrar:

- capacidade de descoberta automatizada;
- qualidade técnica auditável;
- estabilidade operacional para consumo.

A separação entre descoberta e catálogo consolidado, combinada com versionamento de publicação, cria uma base robusta para crescimento contínuo do produto.

Esse modelo permite expandir cobertura e inteligência sem abrir mão de governança, rastreabilidade e confiança nos dados técnicos publicados.