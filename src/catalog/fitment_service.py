"""
fitment_service.py

Responsável por consultas de aplicação automotiva (fitment).

Exemplos de uso:
- encontrar peças por veículo
- encontrar peças por motor
- filtrar por tipo de peça
"""

from typing import Any


def find_parts_by_vehicle_id(
    cursor,
    vehicle_id: int,
    part_type_id: int | None = None,
    only_published: bool = False
) -> list[dict[str, Any]]:
    """
    Busca peças aplicáveis a um veículo com base em:
    vehicle -> vehicle_motors -> applications -> clusters -> parts

    Regras:
    - retorna apenas clusters vinculados a parts
    - pode filtrar por tipo de peça
    - pode filtrar apenas peças publicadas
    """
    query = """
        SELECT DISTINCT
            v.id AS vehicle_id,
            v.brand,
            v.model,
            v.model_year,
            p.id AS part_id,
            p.name AS part_name,
            p.normalized_name,
            p.status AS part_status,
            pt.id AS part_type_id,
            pt.name AS part_type_name,
            c.id AS cluster_id,
            c.cluster_type,
            a.id AS application_id,
            a.position,
            a.side,
            a.notes,
            a.source,
            a.confidence_score
        FROM reference.vehicles v
        JOIN reference.vehicle_motors vm
          ON vm.vehicle_id = v.id
        JOIN catalog.applications a
          ON a.motor_id = vm.motor_id
             OR a.vehicle_id = v.id
        JOIN catalog.clusters c
          ON c.id = a.cluster_id
        JOIN catalog.parts p
          ON p.id = c.part_id
        JOIN reference.part_types pt
          ON pt.id = p.part_type_id
        WHERE v.id = %s
    """

    params: list[Any] = [vehicle_id]

    if part_type_id is not None:
        query += " AND pt.id = %s"
        params.append(part_type_id)

    if only_published:
        query += " AND p.status = 'active'"

    query += """
        ORDER BY
            pt.name,
            p.name,
            a.confidence_score DESC,
            c.id
    """

    cursor.execute(query, tuple(params))
    rows = cursor.fetchall()

    columns = [desc[0] for desc in cursor.description]
    return [dict(zip(columns, row)) for row in rows]


def find_parts_by_motor_id(
    cursor,
    motor_id: int,
    part_type_id: int | None = None,
    only_published: bool = False
) -> list[dict[str, Any]]:
    """
    Busca peças aplicáveis diretamente a um motor.
    """
    query = """
        SELECT DISTINCT
            m.id AS motor_id,
            m.code AS motor_code,
            m.description AS motor_description,
            p.id AS part_id,
            p.name AS part_name,
            p.normalized_name,
            p.status AS part_status,
            pt.id AS part_type_id,
            pt.name AS part_type_name,
            c.id AS cluster_id,
            c.cluster_type,
            a.id AS application_id,
            a.position,
            a.side,
            a.notes,
            a.source,
            a.confidence_score
        FROM reference.motors m
        JOIN catalog.applications a
          ON a.motor_id = m.id
        JOIN catalog.clusters c
          ON c.id = a.cluster_id
        JOIN catalog.parts p
          ON p.id = c.part_id
        JOIN reference.part_types pt
          ON pt.id = p.part_type_id
        WHERE m.id = %s
    """

    params: list[Any] = [motor_id]

    if part_type_id is not None:
        query += " AND pt.id = %s"
        params.append(part_type_id)

    if only_published:
        query += " AND p.status = 'active'"

    query += """
        ORDER BY
            pt.name,
            p.name,
            a.confidence_score DESC,
            c.id
    """

    cursor.execute(query, tuple(params))
    rows = cursor.fetchall()

    columns = [desc[0] for desc in cursor.description]
    return [dict(zip(columns, row)) for row in rows]


def find_fitment_by_vehicle_filters(
    cursor,
    brand: str,
    model: str,
    model_year: int,
    part_type_name: str | None = None,
    version: str | None = None,
    only_published: bool = False
) -> list[dict[str, Any]]:
    """
    Busca aplicações usando filtros comerciais de veículo.

    Ideal para cenários como:
    - Honda Civic 2010
    - Honda Civic 2010 filtro de óleo
    """
    query = """
        SELECT DISTINCT
            v.id AS vehicle_id,
            v.brand,
            v.model,
            v.model_year,
            v.version,
            v.body_type,
            v.fuel_type,
            p.id AS part_id,
            p.name AS part_name,
            p.status AS part_status,
            pt.id AS part_type_id,
            pt.name AS part_type_name,
            c.id AS cluster_id,
            a.id AS application_id,
            a.position,
            a.side,
            a.notes,
            a.source,
            a.confidence_score
        FROM reference.vehicles v
        JOIN reference.vehicle_motors vm
          ON vm.vehicle_id = v.id
        JOIN catalog.applications a
          ON a.motor_id = vm.motor_id
             OR a.vehicle_id = v.id
        JOIN catalog.clusters c
          ON c.id = a.cluster_id
        JOIN catalog.parts p
          ON p.id = c.part_id
        JOIN reference.part_types pt
          ON pt.id = p.part_type_id
        WHERE UPPER(v.brand) = UPPER(%s)
          AND UPPER(v.model) = UPPER(%s)
          AND v.model_year = %s
    """

    params: list[Any] = [brand, model, model_year]

    if version is not None:
        query += " AND UPPER(COALESCE(v.version, '')) = UPPER(%s)"
        params.append(version)

    if part_type_name is not None:
        query += " AND UPPER(pt.name) = UPPER(%s)"
        params.append(part_type_name)

    if only_published:
        query += " AND p.status = 'active'"

    query += """
        ORDER BY
            pt.name,
            p.name,
            a.confidence_score DESC
    """

    cursor.execute(query, tuple(params))
    rows = cursor.fetchall()

    columns = [desc[0] for desc in cursor.description]
    return [dict(zip(columns, row)) for row in rows]