# Pipeline de Dados – Catálogo Automotivo

## 1. Objetivo do Pipeline

O pipeline de dados define o fluxo de processamento responsável por:

* coletar dados de diferentes fontes
* normalizar códigos de peças
* identificar equivalências
* gerar clusters de peças
* associar aplicações a motores e veículos

O pipeline foi projetado para permitir **expansão contínua do catálogo automotivo**.

---

# 2. Visão Geral do Pipeline

O fluxo geral do pipeline é:

Fontes de Dados
↓
Scrapers / APIs
↓
Data Raw
↓
Normalização de Dados
↓
Extração de Equivalências
↓
Rede de Equivalência de Códigos
↓
Clusterização
↓
Associação de Aplicações
↓
Banco do Catálogo
↓
API de Consulta
↓
Interface de Busca

---

# 3. Fontes de Dados

O sistema coleta informações de múltiplas fontes.

Principais tipos de fontes:

catálogos de fabricantes
sites de autopeças
documentação técnica
bases públicas de veículos

Essas fontes podem fornecer:

* códigos de peças
* equivalências entre fabricantes
* aplicações em veículos
* descrições técnicas

---

# 4. Scrapers e APIs

Ferramentas responsáveis pela coleta automatizada de dados.

Funções:

* acessar páginas web
* extrair informações estruturadas
* salvar dados brutos

Saída dessa etapa:

dados não processados contendo:

códigos de peças
fabricantes
equivalências
aplicações

---

# 5. Data Raw

Armazena dados coletados **sem transformação**.

Objetivos:

* preservar a informação original
* permitir reprocessamento
* auditar fontes de dados

Exemplos de dados armazenados:

catálogos de fabricantes
resultados de scraping
arquivos JSON ou CSV

---

# 6. Normalização de Dados

Processo responsável por padronizar os dados coletados.

Atividades:

padronização de códigos de peças
remoção de caracteres inválidos
padronização de fabricantes
normalização de nomes de peças

Isso evita duplicações causadas por variações de escrita.

---

# 7. Extração de Equivalências

Nesta etapa são identificadas relações entre códigos de peças.

Exemplo:

Bosch 0986AF0051 equivalente a Mahle OC1196

Essas relações são extraídas de:

catálogos técnicos
tabelas de cross reference
descrições de produtos

---

# 8. Rede de Equivalência de Códigos

Todas as equivalências são armazenadas em uma rede.

Estrutura conceitual:

código A ↔ código B
código B ↔ código C
código C ↔ código D

Essa rede representa um **grafo de equivalência entre códigos de peças**.

---

# 9. Clusterização

Processo que identifica **clusters de peças equivalentes**.

Cada cluster corresponde a um grupo de códigos conectados na rede de equivalência.

Exemplo:

Cluster 1001

Bosch 0986AF0051
Mahle OC1196
Fram PH7317
Honda 15400-RTA-003

Todos pertencem ao mesmo cluster.

---

# 10. Associação de Aplicações

Após a formação dos clusters, são associadas aplicações.

Aplicações definem:

em quais motores a peça pode ser utilizada.

Exemplo:

Cluster 1001 → Motor R18

---

# 11. Integração com Veículos

Motores são associados a veículos.

Exemplo:

Motor R18 → Honda Civic 2008
Motor R18 → Honda Civic 2009
Motor R18 → Honda Civic 2010

---

# 12. Banco do Catálogo

Após o processamento, os dados estruturados são armazenados no banco do catálogo.

Principais entidades armazenadas:

clusters de peças
códigos de peças
fabricantes
equivalências
aplicações
motores
veículos

---

# 13. API de Consulta

A API permite que aplicações externas consultem o catálogo.

Consultas possíveis:

buscar peças por veículo
buscar equivalentes por código
listar aplicações de uma peça

---

# 14. Interface de Busca

Camada responsável pela interação com o usuário.

Permite buscas como:

veículo + peça
código de peça
nome da peça

---

# 15. Crescimento do Catálogo

O pipeline foi projetado para permitir expansão contínua.

Cada novo código ou equivalência adicionada pode:

expandir clusters existentes
criar novos clusters
revelar novas aplicações

Isso permite que o catálogo cresça **automaticamente conforme novos dados são coletados**.
