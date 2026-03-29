"""
fitment_service.py

Serviços de consulta de fitment do catálogo automotivo.

Responsável por:
- buscar peças por veículo
- buscar peças por motor
- buscar fitment por filtros comerciais

Observação importante:
A modelagem de veículos foi refatorada para usar:

vehicle_brands -> vehicle_models -> vehicles

Por isso este módulo passa a consultar a estrutura oficial de marca e modelo,
usando fallback para brand_text e model_text apenas como apoio de transição.

Enquanto a camada formal de publicação ainda não existe, o filtro
`only_published=True` continua usando `catalog.parts.status = 'active'`
como aproximação de catálogo visível.
"""

from typing import Any

from src.shared.utils import normalize_text


def _normalize_lookup_text(value: str | None) -> str | None:
    """
    Normaliza texto de entrada para comparação semântica consistente.
    """
    if value is None:
        return None

    normalized = normalize_text(value)
    if normalized is None:
        return None

    return normalized.upper()


def find_parts_by_vehicle_id(
    cursor,
    vehicle_id: int,
    part_type_id: int | None = None,
    only_published: bool = False
) -> list[dict[str, Any]]:
    """
    Busca peças aplicáveis a um veículo.
    """
    query = """
        SELECT DISTINCT *
        FROM (

            SELECT
                v.id AS vehicle_id,
                vb.id AS brand_id,
                vb.name AS brand_name,
                vm.id AS model_id,
                vm.name AS model_name,
                v.brand_text,
                v.model_text,
                v.model_year,
                v.version_name,
                v.body_type,
                v.fuel_type,
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
                a.position_type_id,
                a.side,
                a.side_type_id,
                a.notes,
                a.source,
                a.confidence_score
            FROM reference.vehicles v
            LEFT JOIN reference.vehicle_models vm
              ON vm.id = v.model_id
            LEFT JOIN reference.vehicle_brands vb
              ON vb.id = vm.brand_id
            JOIN reference.vehicle_motors veh_mot
              ON veh_mot.vehicle_id = v.id
            JOIN catalog.applications a
              ON a.motor_id = veh_mot.motor_id
            JOIN catalog.clusters c
              ON c.id = a.cluster_id
            JOIN catalog.parts p
              ON p.id = c.part_id
            JOIN reference.part_types pt
              ON pt.id = p.part_type_id
            WHERE v.id = %s

            UNION

            SELECT
                v.id AS vehicle_id,
                vb.id AS brand_id,
                vb.name AS brand_name,
                vm.id AS model_id,
                vm.name AS model_name,
                v.brand_text,
                v.model_text,
                v.model_year,
                v.version_name,
                v.body_type,
                v.fuel_type,
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
                a.position_type_id,
                a.side,
                a.side_type_id,
                a.notes,
                a.source,
                a.confidence_score
            FROM reference.vehicles v
            LEFT JOIN reference.vehicle_models vm
              ON vm.id = v.model_id
            LEFT JOIN reference.vehicle_brands vb
              ON vb.id = vm.brand_id
            JOIN catalog.applications a
              ON a.vehicle_id = v.id
            JOIN catalog.clusters c
              ON c.id = a.cluster_id
            JOIN catalog.parts p
              ON p.id = c.part_id
            JOIN reference.part_types pt
              ON pt.id = p.part_type_id
            WHERE v.id = %s

        ) fitment_result
        WHERE 1 = 1
    """

    params: list[Any] = [vehicle_id, vehicle_id]

    if part_type_id is not None:
        query += " AND part_type_id = %s"
        params.append(part_type_id)

    if only_published:
        query += " AND part_status = 'active'"

    query += """
        ORDER BY
            part_type_name,
            part_name,
            confidence_score DESC,
            cluster_id
    """

    cursor.execute(query, params)
    return cursor.fetchall()


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
            m.displacement,
            m.fuel_type,
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
            a.position_type_id,
            a.side,
            a.side_type_id,
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

    cursor.execute(query, params)
    return cursor.fetchall()


def find_fitment_by_vehicle_filters(
    cursor,
    brand: str,
    model: str,
    model_year: int,
    part_type_name: str | None = None,
    version: str | None = None,
    only_published: bool = False
) -> list[dict[str, Any]]:

    normalized_brand = _normalize_lookup_text(brand)
    normalized_model = _normalize_lookup_text(model)
    normalized_version = _normalize_lookup_text(version)
    normalized_part_type_name = _normalize_lookup_text(part_type_name)

    query = """
        SELECT DISTINCT *
        FROM (

            -- VIA MOTOR
            SELECT
                v.id AS vehicle_id,
                vb.id AS brand_id,
                vb.name AS brand_name,
                vm.id AS model_id,
                vm.name AS model_name,
                v.brand_text,
                v.model_text,
                v.model_year,
                v.version_name,
                v.body_type,
                v.fuel_type,

                p.id AS part_id,
                p.name AS part_name,
                p.status AS part_status,

                pt.id AS part_type_id,
                pt.name AS part_type_name,
                pt.normalized_name AS part_type_normalized_name,

                c.id AS cluster_id,
                a.id AS application_id,
                a.position,
                a.position_type_id,
                a.side,
                a.side_type_id,
                a.notes,
                a.source,
                a.confidence_score

            FROM reference.vehicles v
            LEFT JOIN reference.vehicle_models vm ON vm.id = v.model_id
            LEFT JOIN reference.vehicle_brands vb ON vb.id = vm.brand_id

            JOIN reference.vehicle_motors veh_mot ON veh_mot.vehicle_id = v.id
            JOIN catalog.applications a ON a.motor_id = veh_mot.motor_id
            JOIN catalog.clusters c ON c.id = a.cluster_id
            JOIN catalog.parts p ON p.id = c.part_id
            JOIN reference.part_types pt ON pt.id = p.part_type_id

            WHERE
                UPPER(vb.normalized_name) = %s
                AND UPPER(vm.normalized_name) = %s
                AND v.model_year = %s

            UNION

            -- DIRETO NO VEÍCULO
            SELECT
                v.id AS vehicle_id,
                vb.id AS brand_id,
                vb.name AS brand_name,
                vm.id AS model_id,
                vm.name AS model_name,
                v.brand_text,
                v.model_text,
                v.model_year,
                v.version_name,
                v.body_type,
                v.fuel_type,

                p.id AS part_id,
                p.name AS part_name,
                p.status AS part_status,

                pt.id AS part_type_id,
                pt.name AS part_type_name,
                pt.normalized_name AS part_type_normalized_name,

                c.id AS cluster_id,
                a.id AS application_id,
                a.position,
                a.position_type_id,
                a.side,
                a.side_type_id,
                a.notes,
                a.source,
                a.confidence_score

            FROM reference.vehicles v
            LEFT JOIN reference.vehicle_models vm ON vm.id = v.model_id
            LEFT JOIN reference.vehicle_brands vb ON vb.id = vm.brand_id

            JOIN catalog.applications a ON a.vehicle_id = v.id
            JOIN catalog.clusters c ON c.id = a.cluster_id
            JOIN catalog.parts p ON p.id = c.part_id
            JOIN reference.part_types pt ON pt.id = p.part_type_id

            WHERE
                UPPER(vb.normalized_name) = %s
                AND UPPER(vm.normalized_name) = %s
                AND v.model_year = %s

        ) fitment_result
        WHERE 1 = 1
    """

    params: list[Any] = [
        normalized_brand,
        normalized_model,
        model_year,
        normalized_brand,
        normalized_model,
        model_year,
    ]

    if normalized_version is not None:
        query += " AND UPPER(COALESCE(version_name, '')) = %s"
        params.append(normalized_version)

    if normalized_part_type_name is not None:
        query += " AND UPPER(part_type_normalized_name) = %s"
        params.append(normalized_part_type_name)

    if only_published:
        query += " AND part_status = 'active'"

    query += """
        ORDER BY
            part_type_name,
            part_name,
            confidence_score DESC
    """

    cursor.execute(query, params)
    return cursor.fetchall()