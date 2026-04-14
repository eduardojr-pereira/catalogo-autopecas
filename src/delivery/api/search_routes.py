"""
search_routes.py

Rotas HTTP mínimas de busca do catálogo automotivo.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Path, Query

from src.catalog.query_service import (
    search_by_code,
    search_by_part_name,
    search_by_part_type,
    search_by_part_type_alias,
    search_equivalents_by_code,
)
from src.delivery.api.dependencies import get_db_cursor, require_non_blank

router = APIRouter(prefix="/search", tags=["search"])


def _build_list_response(items: list[dict]) -> dict:
    """
    Padroniza resposta de lista da API.
    """
    return {
        "count": len(items),
        "items": items,
    }


@router.get("/code/{code}")
def get_search_by_code(
    code: str = Path(..., description="Código da peça"),
    only_published: bool = Query(False),
    cursor=Depends(get_db_cursor),
) -> dict:
    code = require_non_blank(code, "code")

    items = search_by_code(
        cursor=cursor,
        code=code,
        only_published=only_published,
    )
    return _build_list_response(items)


@router.get("/part")
def get_search_by_part_name(
    name: str = Query(..., description="Nome parcial da peça"),
    only_published: bool = Query(False),
    limit: int = Query(50, ge=1, le=200),
    cursor=Depends(get_db_cursor),
) -> dict:
    name = require_non_blank(name, "name")

    items = search_by_part_name(
        cursor=cursor,
        part_name=name,
        only_published=only_published,
        limit=limit,
    )
    return _build_list_response(items)


@router.get("/part-type")
def get_search_by_part_type(
    name: str = Query(..., description="Nome do tipo de peça"),
    only_published: bool = Query(False),
    limit: int = Query(50, ge=1, le=200),
    cursor=Depends(get_db_cursor),
) -> dict:
    name = require_non_blank(name, "name")

    items = search_by_part_type(
        cursor=cursor,
        part_type_name=name,
        only_published=only_published,
        limit=limit,
    )
    return _build_list_response(items)


@router.get("/part-type-alias")
def get_search_by_part_type_alias(
    alias: str = Query(..., description="Alias do tipo de peça"),
    only_published: bool = Query(False),
    limit: int = Query(50, ge=1, le=200),
    cursor=Depends(get_db_cursor),
) -> dict:
    alias = require_non_blank(alias, "alias")

    items = search_by_part_type_alias(
        cursor=cursor,
        alias=alias,
        only_published=only_published,
        limit=limit,
    )
    return _build_list_response(items)


@router.get("/equivalents/{code}")
def get_search_equivalents_by_code(
    code: str = Path(..., description="Código base para busca de equivalentes"),
    only_published: bool = Query(False),
    cursor=Depends(get_db_cursor),
) -> dict:
    code = require_non_blank(code, "code")

    items = search_equivalents_by_code(
        cursor=cursor,
        code=code,
        only_published=only_published,
    )
    return _build_list_response(items)