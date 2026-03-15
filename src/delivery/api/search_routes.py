"""
search_routes.py

Rotas de busca do catálogo automotivo.

Objetivo futuro:
- expor endpoints HTTP para consultas textuais e estruturadas do catálogo
- permitir busca por código, nome de peça, tipo de peça e equivalentes
- servir como camada pública de consulta do sistema

Responsabilidades futuras:
- receber parâmetros de busca da API
- validar entradas do usuário
- chamar search_service.py
- retornar respostas padronizadas em JSON

Exemplos de endpoints futuros:
- GET /search/code/{code}
- GET /search/part
- GET /search/part-type
- GET /search/equivalents/{code}

Status atual:
- arquivo reservado para implementação futura
"""