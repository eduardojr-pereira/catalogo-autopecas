# Modelo de Dados – Catálogo Automotivo

## 1. Visão Geral

Este projeto implementa um catálogo automotivo técnico baseado em:

- códigos de peças
- rede de equivalência entre códigos
- clusters de peças
- aplicações em motores e veículos

O sistema distingue claramente:

- **equivalência descoberta**
- **equivalência validada**
- **agrupamento de descoberta**
- **agrupamento consolidado**

Isso é necessário porque, no domínio automotivo, duas peças podem aparecer como equivalentes em uma fonte comercial sem serem tecnicamente idênticas em todas as dimensões ou aplicações.

---

## 2. Conceito Central

O sistema possui duas camadas de agrupamento:

### Cluster de Descoberta
Grupo de códigos conectados por equivalências descobertas.

Objetivo:
- explorar relações
- expandir o catálogo
- organizar hipóteses de equivalência

### Cluster Consolidado
Grupo de códigos já validados com confiança técnica suficiente.

Objetivo:
- suportar consulta confiável
- servir como base principal do catálogo
- reduzir risco de equivalências incorretas

---

## 3. Entidades Principais

### Reference Schema

#### manufacturers
Fabricantes de peças.

#### vehicles
Veículos.

#### motors
Motores.

#### vehicle_motors
Relacionamento entre veículos e motores.

---

### Discovery Schema

#### codes
Todos os códigos de peças encontrados pelo sistema.

Campos relevantes:
- fabricante
- código bruto
- código normalizado

#### code_equivalences
Relações de equivalência descobertas entre códigos.

Importante:
esta tabela não representa, por si só, identidade técnica absoluta.

Campos relevantes:
- source
- equivalence_type
- validation_status
- confidence_score
- notes

---

### Catalog Schema

#### clusters
Clusters de peças.

Campos relevantes:
- cluster_type (`discovery` ou `consolidated`)

#### cluster_codes
Relacionamento entre clusters e códigos.

#### applications
Relacionamento entre cluster e motor.

---

## 4. Regra de Negócio Essencial

Nem toda equivalência descoberta deve gerar fusão automática de cluster consolidado.

Exemplos de risco:
- diferenças dimensionais
- roscas diferentes
- revisões de peça
- pequenas variações aceitas por alguns marketplaces, mas não por catálogos técnicos rigorosos

Portanto:
- relações descobertas alimentam clusters de descoberta
- relações validadas podem alimentar clusters consolidados

---

## 5. Fluxo Conceitual

Código descoberto  
↓  
Equivalência descoberta  
↓  
Cluster de descoberta  
↓  
Validação técnica / aumento de confiança  
↓  
Cluster consolidado  
↓  
Aplicações confiáveis