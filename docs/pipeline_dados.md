# Pipeline de Dados – Catálogo Automotivo

## 1. Objetivo

O pipeline de dados é responsável por:

- coletar códigos
- normalizar códigos
- identificar equivalências
- qualificar equivalências
- gerar clusters de descoberta
- consolidar clusters confiáveis
- associar aplicações a motores e veículos

---

## 2. Fluxo Geral

Fontes de Dados  
↓  
Scrapers / APIs  
↓  
Data Raw  
↓  
Normalização de Códigos  
↓  
Extração de Equivalências  
↓  
Qualificação das Equivalências  
↓  
Rede de Equivalência  
↓  
Clusters de Descoberta  
↓  
Consolidação  
↓  
Clusters Consolidados  
↓  
Associação de Aplicações  
↓  
Banco do Catálogo  
↓  
API de Consulta  

---

## 3. Qualificação de Equivalências

Cada equivalência descoberta deve ser registrada com atributos que permitam avaliar sua confiabilidade:

- `source`
- `equivalence_type`
- `validation_status`
- `confidence_score`

Isso evita que o pipeline trate uma equivalência comercial fraca como identidade técnica forte.

---

## 4. Clusterização

### Cluster de Descoberta
Forma grupos conectados com base em equivalências descobertas.

### Cluster Consolidado
Forma grupos usados pelo catálogo principal após filtros de qualidade.

---

## 5. Benefícios

- crescimento rápido do catálogo
- rastreabilidade das relações
- separação entre hipótese e verdade operacional
- menor risco de erro técnico