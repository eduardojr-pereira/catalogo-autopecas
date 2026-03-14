# Arquitetura do Sistema – Catálogo Automotivo

## 1. Objetivo da Arquitetura

A arquitetura do sistema foi projetada para construir um **catálogo automotivo técnico escalável**, capaz de:

* descobrir códigos de peças automaticamente
* mapear equivalências entre fabricantes
* organizar peças em clusters funcionais
* relacionar peças com motores e veículos
* crescer automaticamente conforme novos dados são coletados

O sistema é baseado em **clusters de peças formados a partir de uma rede de equivalência entre códigos**.

Essa abordagem permite que o catálogo funcione mesmo quando:

* o código OEM não é conhecido
* existem múltiplos OEM para a mesma peça
* fabricantes fornecem equivalências incompletas

---

# 2. Princípio Central da Arquitetura

O sistema utiliza **clusters de peças** como entidade central.

Um cluster representa **uma peça funcional única**, independente do fabricante ou código.

Exemplo conceitual:

Cluster: Filtro de óleo motor R18

Códigos pertencentes ao cluster:

Honda 15400-RTA-003
Bosch 0986AF0051
Mahle OC1196
Fram PH7317
Mann W610/3

Todos os códigos representam a mesma peça funcional.

Aplicações são associadas ao **cluster**, e não aos códigos individuais.

---

# 3. Rede de Equivalência de Códigos

O sistema mantém uma **rede de equivalência entre códigos de peças**.

Cada código é tratado como um nó em um grafo.

Relações de equivalência formam arestas entre esses nós.

Exemplo:

Bosch 0986AF0051 ↔ Mahle OC1196
Mahle OC1196 ↔ Fram PH7317
Fram PH7317 ↔ Honda 15400-RTA-003

Todos os códigos conectados formam um **cluster de peça**.

Clusters são obtidos identificando **componentes conectados do grafo de equivalências**.

---

# 4. Estrutura Arquitetural Geral

A arquitetura do sistema pode ser representada da seguinte forma:

Discovery Engine
↓
Codes
↓
Code Equivalence Network
↓
Cluster Engine
↓
Clusters
↓
Applications
↓
Motors
↓
Vehicles

---

# 5. Componentes do Sistema

## Discovery Engine

Responsável por **descobrir novos códigos e equivalências**.

Fontes de dados:

* catálogos de fabricantes
* lojas de autopeças
* bases públicas
* scraping de páginas técnicas

Funções principais:

* identificar códigos de peças
* extrair equivalências entre códigos
* coletar aplicações de peças
* alimentar o banco de dados bruto

Entradas típicas:

veículo + nome da peça
ou código de peça conhecido

Saídas:

códigos encontrados
equivalências entre códigos
possíveis aplicações

---

## Code Equivalence Network

Representa a rede de equivalência entre códigos.

Função:

armazenar relações entre códigos que representam a mesma peça.

Cada relação adiciona uma conexão ao grafo.

Essa rede é utilizada para:

* identificar clusters
* detectar códigos duplicados
* expandir relações entre fabricantes

---

## Cluster Engine

Responsável por **gerar e manter clusters de peças**.

Funções:

* identificar componentes conectados da rede de equivalência
* criar novos clusters quando necessário
* atualizar clusters existentes
* garantir consistência do catálogo

Cada cluster representa **uma peça funcional única**.

---

## Catalog Engine

Responsável por gerenciar o catálogo estruturado.

Funções:

* associar códigos a clusters
* manter relações entre clusters e aplicações
* relacionar clusters com motores
* relacionar motores com veículos

Esse módulo garante a integridade e consistência do catálogo.

---

# 6. Estrutura Funcional do Catálogo

A estrutura funcional do catálogo é:

Cluster de Peça
│
├── Códigos de Peça
│      └ Fabricantes
│
└── Aplicações
│
└ Motores
│
└ Veículos

---

# 7. Fluxo de Consulta no Catálogo

O sistema deve ser capaz de responder diferentes tipos de consulta.

## Consulta por veículo

Fluxo:

Veículo
→ Motor
→ Clusters aplicáveis
→ Códigos equivalentes

---

## Consulta por código de peça

Fluxo:

Código
→ Cluster
→ Aplicações
→ Veículos compatíveis

---

## Consulta por nome de peça

Fluxo:

Nome da peça
→ Peça padronizada
→ Clusters
→ Aplicações

---

# 8. Expansão Automática do Catálogo

O catálogo cresce automaticamente conforme novos dados são descobertos.

Fluxo de expansão:

novo código encontrado
↓
descoberta de equivalências
↓
expansão da rede de equivalência
↓
formação ou expansão de clusters
↓
novas aplicações associadas
↓
expansão do catálogo

---

# 9. Camadas do Sistema

O sistema é dividido em duas camadas principais.

Discovery Layer

Responsável pela coleta e descoberta de dados.

Inclui:

scrapers
coleta de catálogos
extração de equivalências

Catalog Layer

Responsável pela organização e estrutura do catálogo.

Inclui:

clusters de peças
aplicações
motores
veículos

---

# 10. Benefícios da Arquitetura

Essa arquitetura oferece várias vantagens:

* independência de OEM como chave central
* capacidade de operar mesmo com dados incompletos
* expansão automática do catálogo
* facilidade de integração com novos fabricantes
* escalabilidade para milhões de códigos e aplicações
