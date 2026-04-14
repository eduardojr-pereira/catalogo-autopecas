"""
main.py

Ponto de entrada da API mínima do catálogo automotivo.
"""

from __future__ import annotations

from fastapi import FastAPI

from src.delivery.api.fitment_routes import router as fitment_router
from src.delivery.api.search_routes import router as search_router

app = FastAPI(
    title="Catálogo Automotivo Inteligente",
    version="0.1.0",
    description="API mínima de busca e fitment do catálogo automotivo.",
)


@app.get("/health", tags=["health"])
def healthcheck() -> dict:
    """
    Healthcheck simples da aplicação.
    """
    return {"status": "ok"}


app.include_router(search_router)
app.include_router(fitment_router)