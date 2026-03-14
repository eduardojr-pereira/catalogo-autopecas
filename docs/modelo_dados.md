# Modelo de Dados – Catálogo Automotivo

## 1. Visão Geral

Este projeto implementa um **catálogo automotivo técnico baseado em clusters de peças e rede de equivalência entre códigos**.

O objetivo é permitir:

* identificar peças compatíveis com veículos
* mapear códigos OEM e aftermarket
* relacionar equivalentes entre fabricantes
* escalar o catálogo automaticamente a partir de novas fontes de dados

A arquitetura foi projetada para suportar **expansão automática do catálogo**, evitando dependência exclusiva de OEM ou cadastro manual de aplicações.

---

# 2. Conceito Central do Modelo

O núcleo do sistema é o **Cluster de Peça**.

Um cluster representa **uma peça funcional única**, independentemente do fabricante ou código utilizado.

Exemplo conceitual:

Cluster: Filtro de óleo motor Honda R18

Códigos pertencentes ao cluster:

Honda 15400-RTA-003
Bosch 0986AF0051
Mahle OC1196
Fram PH7317
Mann W610/3

Todos esses códigos representam **a mesma peça funcional**.

---

# 3. Rede de Equivalência de Códigos

O sistema utiliza uma **rede de equivalência** para descobrir automaticamente quais códigos pertencem ao mesmo cluster.

Cada código é tratado como um **nó em um grafo**.

As relações de equivalência formam **arestas entre os códigos**.

Exemplo:

Bosch 0986AF0051 ↔ Mahle OC1196
Mahle OC1196 ↔ Fram PH7317
Fram PH7317 ↔ Honda 15400-RTA-003

Todos os códigos conectados pertencem ao **mesmo cluster de peça**.

Clusters são formados automaticamente a partir dos **componentes conectados da rede de equivalências**.

---

# 4. Estrutura Conceitual do Catálogo

A estrutura principal do catálogo é:

CLUSTER_DE_PECA
│
├── CODIGOS_DE_PECA
│      └ FABRICANTES
│
└── APLICACOES
│
└ MOTORES
│
└ VEICULOS

Aplicações são associadas ao **cluster**, não aos códigos individuais.

Isso garante que todos os códigos equivalentes compartilhem as mesmas aplicações.

---

# 5. Entidades Principais

## Montadoras

Representa fabricantes de veículos.

Exemplos:

Honda
Volkswagen
Fiat
Toyota

Essa entidade evita repetição de nomes de fabricantes em registros de veículos.

---

## Veículos

Representa modelos de veículos.

Exemplos:

Honda Civic
Volkswagen Golf
Fiat Palio
Toyota Corolla

Informações comuns:

* montadora
* modelo
* geração
* ano de início
* ano de fim

---

## Motores

Define versões de motorização associadas aos veículos.

Exemplos:

R18
EA111
Fire 1.4
TSI 1.4

Informações típicas:

* código do motor
* cilindrada
* combustível
* potência

---

## Veículo_Motor

Tabela que relaciona veículos e motores.

Um veículo pode possuir **várias motorizações**.

Exemplo:

Civic → Motor R18
Civic → Motor K20
Golf → Motor TSI
Golf → Motor MSI

---

## Sistemas Automotivos

Organiza peças por sistemas do veículo.

Exemplos:

Lubrificação
Freios
Suspensão
Arrefecimento
Ignição
Transmissão
Elétrica

---

## Peças

Define o tipo genérico de peça.

Exemplos:

Filtro de óleo
Filtro de ar
Pastilha de freio
Disco de freio
Vela de ignição

Cada peça pertence a um sistema automotivo.

---

## Sinônimos de Peças

Permite mapear diferentes nomes usados para a mesma peça.

Exemplo:

Filtro de óleo
Filtro óleo
Filtro lubrificante
Oil filter

Todos apontam para uma **peça padronizada**.

Isso melhora significativamente a busca no catálogo.

---

# 6. Cluster de Peça

Representa um grupo de códigos equivalentes que descrevem a mesma peça funcional.

Cada cluster pode possuir:

* múltiplos códigos OEM
* múltiplos códigos aftermarket
* múltiplos fabricantes

Aplicações são associadas ao cluster.

---

# 7. Códigos de Peça

Representa qualquer código de peça existente no mercado.

Tipos comuns:

OEM
Aftermarket
Código interno
Código de e-commerce

Cada código está associado a:

* um fabricante
* um cluster de peça

---

# 8. Fabricantes

Representa fabricantes de peças automotivas.

Exemplos:

Bosch
Mahle
NGK
SKF
Gates
TRW

Fabricantes produzem códigos aftermarket e podem fornecer equivalências.

---

# 9. Equivalência de Códigos

Representa relações de equivalência entre dois códigos.

Exemplo:

Bosch 0986AF0051 ↔ Mahle OC1196

Tipos possíveis de equivalência:

OEM equivalence
Aftermarket equivalence
Cross reference
Substituição

Essas relações formam a **rede de equivalência utilizada para gerar clusters automaticamente**.

---

# 10. Aplicações

Define em quais motores um determinado cluster pode ser utilizado.

Exemplo:

Cluster: Filtro de óleo motor R18

Aplicações:

Motor R18 → Civic 2008
Motor R18 → Civic 2009
Motor R18 → Civic 2010

Todos os códigos do cluster herdam essas aplicações.

---

# 11. Estrutura Geral do Banco (Conceitual)

Entidades principais do sistema:

Montadoras
Veículos
Motores
Veículo_Motor

Sistemas
Peças
Sinônimos de Peças

Clusters de Peça
Códigos de Peça
Fabricantes

Equivalência de Códigos

Aplicações

---

# 12. Camadas do Sistema

O sistema possui duas camadas principais.

## Discovery Engine

Responsável por descobrir novos códigos e equivalências a partir de:

* veículos
* nomes de peças
* catálogos de fabricantes
* lojas de autopeças

Entrada típica:

veículo + peça

Saída:

códigos encontrados e possíveis equivalências.

---

## Catalog Engine

Responsável por manter a estrutura do catálogo.

Funções principais:

* gerenciar clusters de peças
* manter rede de equivalência de códigos
* associar aplicações aos clusters
* garantir integridade das relações.

---

# 13. Expansão Automática do Catálogo

O catálogo cresce automaticamente à medida que novas equivalências são descobertas.

Fluxo de expansão:

novo código encontrado
↓
descoberta de equivalentes
↓
formação ou expansão de cluster
↓
novas aplicações associadas
↓
expansão do catálogo

Esse modelo permite que o catálogo cresça **exponencialmente conforme novos dados são coletados**.

---

# 14. Objetivo do Modelo

Permitir responder perguntas como:

Qual peça serve para este veículo?

Quais equivalentes existem para este código?

Em quais veículos um determinado código pode ser aplicado?

Qual o OEM correspondente a um código aftermarket?

Quais fabricantes produzem peças equivalentes para determinada aplicação?
