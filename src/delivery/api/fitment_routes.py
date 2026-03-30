"""
fitment_routes.py

Rotas de fitment do catálogo automotivo.

Objetivo
--------
Expor endpoints HTTP para consulta de aplicações e compatibilidade
comercial de peças por veículo e motor.

Este módulo representa a camada pública de entrega para consultas
de fitment do catálogo, consumindo a camada oficial de consultas
centralizada em `query_service.py`.

Responsabilidades futuras
-------------------------
- receber filtros de veículo, motor e aplicação;
- validar parâmetros de entrada;
- chamar funções de fitment disponíveis em `query_service.py`;
- retornar respostas estruturadas para API;
- servir como ponto de entrada HTTP para consultas de aplicação.

Consultas previstas
-------------------
- busca de peças por veículo;
- busca de peças por motor;
- busca de fitment por filtros comerciais;
- filtros opcionais por tipo de peça;
- filtro opcional de catálogo visível/publicado.

Exemplos de endpoints futuros
-----------------------------
- GET /fitment/vehicle/{vehicle_id}
- GET /fitment/motor/{motor_id}
- GET /fitment/search

Este módulo NÃO deve
--------------------
- implementar SQL diretamente;
- concentrar regras de compatibilidade profunda;
- substituir a futura camada de compatibilidade técnica;
- acessar banco sem passar pela camada de serviço apropriada.

Observação arquitetural
-----------------------
Com a consolidação de `query_service.py`, este módulo deixa de depender
de `fitment_service.py` e passa a apontar para a camada oficial de
consulta do catálogo.

Status atual
------------
Arquivo reservado para implementação futura.
"""