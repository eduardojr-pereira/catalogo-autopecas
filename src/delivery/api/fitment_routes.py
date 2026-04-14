"""
fitment_routes.py

Rotas HTTP mínimas de fitment do catálogo automotivo.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Path, Query

from src.catalog.query_service import (
    find_fitment_by_vehicle_filters,
    find_parts_by_motor_id,
    find_parts_by_vehicle_id,
)
from src.delivery.api.dependencies import (
    get_db_cursor,
    require_non_blank,
    require_positive_int,
)

router = APIRouter(prefix="/fitment", tags=["fitment"])


def _build_list_response(items: list[dict]) -> dict:
    """
    Padroniza resposta de lista da API.
    """
    return {
        "count": len(items),
        "items": items,
    }


@router.get("/vehicle/{vehicle_id}")
def get_fitment_by_vehicle_id(
    vehicle_id: int = Path(..., description="ID do veículo"),
    part_type_id: int | None = Query(None, ge=1),
    only_published: bool = Query(False),
    cursor=Depends(get_db_cursor),
) -> dict:
    vehicle_id = require_positive_int(vehicle_id, "vehicle_id")

    items = find_parts_by_vehicle_id(
        cursor=cursor,
        vehicle_id=vehicle_id,
        part_type_id=part_type_id,
        only_published=only_published,
    )
    return _build_list_response(items)


@router.get("/motor/{motor_id}")
def get_fitment_by_motor_id(
    motor_id: int = Path(..., description="ID do motor"),
    part_type_id: int | None = Query(None, ge=1),
    only_published: bool = Query(False),
    cursor=Depends(get_db_cursor),
) -> dict:
    motor_id = require_positive_int(motor_id, "motor_id")

    items = find_parts_by_motor_id(
        cursor=cursor,
        motor_id=motor_id,
        part_type_id=part_type_id,
        only_published=only_published,
    )
    return _build_list_response(items)


@router.get("/search")
def get_fitment_by_vehicle_filters(
    brand: str = Query(..., description="Marca do veículo"),
    model: str = Query(..., description="Modelo do veículo"),
    model_year: int = Query(..., ge=1, description="Ano modelo"),
    part_type_name: str | None = Query(None),
    version: str | None = Query(None),
    only_published: bool = Query(False),
    cursor=Depends(get_db_cursor),
) -> dict:
    brand = require_non_blank(brand, "brand")
    model = require_non_blank(model, "model")

    if part_type_name is not None:
        part_type_name = require_non_blank(part_type_name, "part_type_name")

    if version is not None:
        version = require_non_blank(version, "version")

    items = find_fitment_by_vehicle_filters(
        cursor=cursor,
        brand=brand,
        model=model,
        model_year=model_year,
        part_type_name=part_type_name,
        version=version,
        only_published=only_published,
    )
    return _build_list_response(items)