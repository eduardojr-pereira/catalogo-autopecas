# Visão geral
Projeto em desenvolvimento para construir um catálogo técnico automotivo com foco em qualidade de dados, rastreabilidade e evolução contínua.

A proposta é transformar dados fragmentados de peças em uma base estruturada para uso técnico e comercial.

# Problema que o projeto resolve
No ecossistema de autopeças, códigos variam entre fabricantes, equivalências nem sempre são explícitas e o fitment (peça ↔ motor ↔ veículo) costuma estar disperso em múltiplas fontes.

Este projeto organiza esse cenário em um catálogo versionável, consultável e auditável.

# Objetivos principais
- Normalizar códigos de peças.
- Descobrir equivalências entre fabricantes.
- Clusterizar códigos equivalentes.
- Relacionar peças, motores e veículos (fitment).
- Suportar busca técnica e comercial.
- Permitir revisão técnica e publicação versionada.

# Resumo da arquitetura
Fluxo principal:

**fontes externas → ingestão → discovery → catalog → compatibility/publication → API**

Resumo das etapas:
- Fontes externas planejadas: API da Tabela FIPE, scrapers de catálogos automotivos e marketplaces.
- Ingestão: coleta e estruturação inicial dos dados.
- Discovery: identificação de códigos e relações de equivalência com evidências.
- Catalog: consolidação em entidades e clusters utilizáveis.
- Compatibility/Publication: cálculo de compatibilidade, revisão e publicação versionada.
- API: exposição para consulta técnica e operacional.

# Resumo da arquitetura de dados
O PostgreSQL é organizado por schemas funcionais:

- `reference`: dados de referência (fabricantes, taxonomias, veículos, motores e bases estruturais).
- `discovery`: dados descobertos durante ingestão/processamento (códigos, evidências e equivalências).
- `catalog`: visão consolidada do catálogo (peças, clusters e relações estáveis).
- `compatibility`: regras e resultados de compatibilidade/fitment.
- `publication`: versões publicadas, estados de revisão e trilha de publicação.

# Stack tecnológica
- Python
- FastAPI
- PostgreSQL
- Docker

# Como rodar o projeto localmente
```bash
# 1) Subir a infraestrutura
docker compose -f docker/docker-compose.yml up -d

# 2) Aplicar o schema
docker exec -i catalogo_postgres psql -U admin -d catalogo < database/schema.sql
```

# Estrutura resumida do repositório
```text
catalogo-autopecas/
├── src/              # Código da aplicação (domínio, processamento e API)
├── database/         # Schema, views e seeds
├── docker/           # Ambiente local com Docker Compose
├── docs/             # Documentação técnica complementar
├── tests/            # Testes unitários e de integração
└── README.md
```

# Documentação complementar
- Documentação técnica: `docs/`
- INCLUIR LINKS

## Autor
Defina aqui o responsável pelo projeto (nome e contato).

# Licença
Uso para fins educacionais e de portfólio. Defina uma licença formal antes de distribuição pública/comercial.