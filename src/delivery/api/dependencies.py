"""
dependencies.py

Dependências compartilhadas da camada HTTP.

Responsabilidades:
- fornecer cursor de banco em modo dict;
- validar entradas simples reutilizáveis;
- evitar duplicação entre rotas de busca e fitment.
"""

from __future__ import annotations

from collections.abc import Generator

from fastapi import HTTPException

from src.shared.db import get_cursor


def get_db_cursor() -> Generator:
    """
    Fornece cursor em modo dict para uso nas rotas.
    """
    with get_cursor(dict_mode=True) as cursor:
        yield cursor


def require_non_blank(value: str, field_name: str) -> str:
    """
    Garante que um campo textual obrigatório não seja vazio.
    """
    normalized = value.strip()

    if not normalized:
        raise HTTPException(
            status_code=400,
            detail=f"Parâmetro '{field_name}' não pode ser vazio.",
        )

    return normalized


def require_positive_int(value: int, field_name: str) -> int:
    """
    Garante que um inteiro seja positivo.
    """
    if value <= 0:
        raise HTTPException(
            status_code=400,
            detail=f"Parâmetro '{field_name}' deve ser maior que zero.",
        )

    return value