"""
review_routes.py

Rotas de revisão e governança técnica do catálogo.

Objetivo futuro:
- expor endpoints para aprovação e rejeição de inferências, decisões e aplicações
- suportar workflows humanos de validação técnica
- integrar evidência, compatibilidade e publicação

Responsabilidades futuras:
- listar itens pendentes de revisão
- aprovar aplicações inferidas
- rejeitar decisões de compatibilidade
- registrar notas de revisão

Exemplos de endpoints futuros:
- GET /review/pending
- POST /review/application/{id}/approve
- POST /review/application/{id}/reject
- POST /review/decision/{id}/approve

Status atual:
- arquivo reservado para implementação futura
"""