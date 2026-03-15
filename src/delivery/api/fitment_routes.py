"""
fitment_routes.py

Rotas de fitment e compatibilidade do catálogo automotivo.

Objetivo futuro:
- expor endpoints HTTP para consulta de aplicações por veículo e motor
- permitir que clientes externos consultem peças compatíveis
- servir como camada pública de fitment do sistema

Responsabilidades futuras:
- receber filtros de veículo e motor
- validar parâmetros de entrada
- chamar fitment_service.py e compatibility_service.py
- retornar resultados estruturados para API

Exemplos de endpoints futuros:
- GET /fitment/vehicle/{vehicle_id}
- GET /fitment/motor/{motor_id}
- GET /fitment/search
- GET /fitment/check

Status atual:
- arquivo reservado para implementação futura
"""