"""
query_service.py

Camada oficial de consultas do catálogo automotivo.

Objetivo
--------
Concentrar, em um único módulo, as consultas de busca e fitment do
catálogo automotivo.

Este módulo unifica a antiga separação entre `search_service.py` e
`fitment_service.py`, reduzindo dispersão de queries SQL e tornando
mais clara a fronteira da camada de consulta do catálogo.

Escopo
------
Este serviço reúne consultas para:

- busca por código;
- busca por nome de peça;
- busca por tipo de peça;
- busca por alias de tipo de peça;
- busca de equivalentes por código;
- busca de peças por veículo;
- busca de peças por motor;
- busca de fitment por filtros comerciais.

Observações arquiteturais
-------------------------
- esta camada é orientada a consulta;
- este módulo pode executar SQL diretamente via cursor;
- este módulo não deve concentrar regras pesadas de compatibilidade;
- este módulo não substitui a futura camada de publicação formal;
- o filtro `only_published=True` continua usando
  `catalog.parts.status = 'active'` como aproximação de catálogo visível.

Modelagem oficial de veículos
-----------------------------
As consultas de fitment utilizam a estrutura oficial:

vehicle_brands -> vehicle_models -> vehicles
"""

from __future__ import annotations

from typing import Any

from src.processing.normalization.code_normalizer import normalize_code
from src.shared.utils import normalize_text


# ======================================================
# HELPERS INTERNOS
# ======================================================

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


# ======================================================
# BUSCA POR CÓDIGO
# ======================================================

def search_by_code(
    cursor,
    code: str,
    only_published: bool = False,
) -> list[dict[str, Any]]:
    """
    Busca códigos e sua vinculação com fabricante, cluster e peça.

    Retorna:
    - código encontrado;
    - fabricante;
    - cluster vinculado, se existir;
    - peça consolidada vinculada, se existir.
    """
    normalized_code = normalize_code(code)

    query = """
        SELECT DISTINCT
            dc.id AS code_id,
            dc.code,
            dc.normalized_code,

            m.id AS manufacturer_id,
            m.name AS manufacturer_name,
            m.manufacturer_type,

            c.id AS cluster_id,
            c.cluster_type,

            p.id AS part_id,
            p.name AS part_name,
            p.normalized_name AS part_normalized_name,
            p.status AS part_status,

            pt.id AS part_type_id,
            pt.name AS part_type_name

        FROM discovery.codes dc
        JOIN reference.manufacturers m
          ON m.id = dc.manufacturer_id
        LEFT JOIN catalog.cluster_codes cc
          ON cc.code_id = dc.id
        LEFT JOIN catalog.clusters c
          ON c.id = cc.cluster_id
        LEFT JOIN catalog.parts p
          ON p.id = c.part_id
        LEFT JOIN reference.part_types pt
          ON pt.id = p.part_type_id
        WHERE dc.normalized_code = %s
    """

    params: list[Any] = [normalized_code]

    if only_published:
        query += " AND p.status = 'active'"

    query += """
        ORDER BY
            p.name NULLS LAST,
            c.id NULLS LAST,
            dc.id
    """

    cursor.execute(query, params)
    return cursor.fetchall()


# ======================================================
# BUSCA POR NOME DA PEÇA
# ======================================================

def search_by_part_name(
    cursor,
    part_name: str,
    only_published: bool = False,
    limit: int = 50,
) -> list[dict[str, Any]]:
    """
    Busca peças por nome normalizado com correspondência parcial.
    """
    normalized_name = _normalize_lookup_text(part_name)

    query = """
        SELECT
            p.id AS part_id,
            p.name AS part_name,
            p.normalized_name,
            p.status AS part_status,
            p.description,

            pt.id AS part_type_id,
            pt.name AS part_type_name

        FROM catalog.parts p
        JOIN reference.part_types pt
          ON pt.id = p.part_type_id
        WHERE p.normalized_name LIKE %s
    """

    params: list[Any] = [f"%{normalized_name}%"]

    if only_published:
        query += " AND p.status = 'active'"

    query += """
        ORDER BY p.name
        LIMIT %s
    """

    params.append(limit)

    cursor.execute(query, params)
    return cursor.fetchall()


# ======================================================
# BUSCA POR TIPO DE PEÇA
# ======================================================

def search_by_part_type(
    cursor,
    part_type_name: str,
    only_published: bool = False,
    limit: int = 50,
) -> list[dict[str, Any]]:
    """
    Busca peças por tipo de peça normalizado.
    """
    normalized_name = _normalize_lookup_text(part_type_name)

    query = """
        SELECT
            p.id AS part_id,
            p.name AS part_name,
            p.normalized_name,
            p.status AS part_status,

            pt.id AS part_type_id,
            pt.name AS part_type_name

        FROM catalog.parts p
        JOIN reference.part_types pt
          ON pt.id = p.part_type_id
        WHERE pt.normalized_name = %s
    """

    params: list[Any] = [normalized_name]

    if only_published:
        query += " AND p.status = 'active'"

    query += """
        ORDER BY p.name
        LIMIT %s
    """

    params.append(limit)

    cursor.execute(query, params)
    return cursor.fetchall()


# ======================================================
# BUSCA POR ALIAS DE TIPO DE PEÇA
# ======================================================

def search_by_part_type_alias(
    cursor,
    alias: str,
    only_published: bool = False,
    limit: int = 50,
) -> list[dict[str, Any]]:
    """
    Busca peças a partir de alias do tipo de peça.
    """
    normalized_alias = _normalize_lookup_text(alias)

    query = """
        SELECT
            p.id AS part_id,
            p.name AS part_name,
            p.normalized_name,
            p.status AS part_status,

            pt.id AS part_type_id,
            pt.name AS part_type_name,

            pta.alias

        FROM reference.part_type_aliases pta
        JOIN reference.part_types pt
          ON pt.id = pta.part_type_id
        JOIN catalog.parts p
          ON p.part_type_id = pt.id
        WHERE pta.normalized_alias = %s
    """

    params: list[Any] = [normalized_alias]

    if only_published:
        query += " AND p.status = 'active'"

    query += """
        ORDER BY p.name
        LIMIT %s
    """

    params.append(limit)

    cursor.execute(query, params)
    return cursor.fetchall()


# ======================================================
# BUSCA DE EQUIVALENTES POR CÓDIGO
# ======================================================

def search_equivalents_by_code(
    cursor,
    code: str,
    only_published: bool = False,
) -> list[dict[str, Any]]:
    """
    Busca códigos equivalentes pertencentes ao mesmo cluster.
    """
    normalized_code = normalize_code(code)

    query = """
        SELECT DISTINCT
            source_code.id AS source_code_id,
            source_code.code AS source_code,
            source_code.normalized_code AS source_normalized_code,

            target_code.id AS equivalent_code_id,
            target_code.code AS equivalent_code,
            target_code.normalized_code AS equivalent_normalized_code,

            m.id AS manufacturer_id,
            m.name AS manufacturer_name,
            m.manufacturer_type,

            c.id AS cluster_id,
            c.cluster_type,

            p.id AS part_id,
            p.name AS part_name,
            p.status AS part_status

        FROM discovery.codes source_code
        JOIN catalog.cluster_codes source_cc
          ON source_cc.code_id = source_code.id
        JOIN catalog.cluster_codes target_cc
          ON target_cc.cluster_id = source_cc.cluster_id
        JOIN discovery.codes target_code
          ON target_code.id = target_cc.code_id
        JOIN reference.manufacturers m
          ON m.id = target_code.manufacturer_id
        JOIN catalog.clusters c
          ON c.id = source_cc.cluster_id
        LEFT JOIN catalog.parts p
          ON p.id = c.part_id
        WHERE source_code.normalized_code = %s
          AND source_code.id <> target_code.id
    """

    params: list[Any] = [normalized_code]

    if only_published:
        query += " AND p.status = 'active'"

    query += """
        ORDER BY
            manufacturer_name,
            equivalent_code
    """

    cursor.execute(query, params)
    return cursor.fetchall()


# ======================================================
# FITMENT POR VEÍCULO
# ======================================================

def find_parts_by_vehicle_id(
    cursor,
    vehicle_id: int,
    part_type_id: int | None = None,
    only_published: bool = False,
) -> list[dict[str, Any]]:
    """
    Busca peças aplicáveis a um veículo.

    A consulta considera:
    - aplicações vindas por motor vinculado ao veículo;
    - aplicações diretas no próprio veículo.
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


# ======================================================
# FITMENT POR MOTOR
# ======================================================

def find_parts_by_motor_id(
    cursor,
    motor_id: int,
    part_type_id: int | None = None,
    only_published: bool = False,
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


# ======================================================
# FITMENT POR FILTROS COMERCIAIS
# ======================================================

def find_fitment_by_vehicle_filters(
    cursor,
    brand: str,
    model: str,
    model_year: int,
    part_type_name: str | None = None,
    version: str | None = None,
    only_published: bool = False,
) -> list[dict[str, Any]]:
    """
    Busca fitment por filtros comerciais de veículo.

    A consulta usa:
    - marca;
    - modelo;
    - ano modelo;
    - versão opcional;
    - tipo de peça opcional.
    """
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