"""
search_service.py

Serviços de busca do catálogo automotivo.

Exemplos:
- busca por código
- busca por nome da peça
- busca por tipo de peça
- busca por alias do tipo de peça
"""

from typing import Any
import re


def normalize_text(value: str | None) -> str | None:
    """
    Normaliza texto para comparação básica.
    """
    if value is None:
        return None

    value = value.strip().upper()
    value = re.sub(r"\s+", " ", value)

    return value


def normalize_code(value: str | None) -> str | None:
    """
    Normaliza código automotivo para busca.
    """
    if value is None:
        return None

    value = value.strip().upper()
    value = re.sub(r"[^A-Z0-9]", "", value)

    return value


def search_by_code(
    cursor,
    code: str,
    only_published: bool = False
) -> list[dict[str, Any]]:
    """
    Busca por código de peça e retorna:
    - código encontrado
    - cluster
    - peça consolidada
    - fabricante
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

    cursor.execute(query, tuple(params))
    rows = cursor.fetchall()

    columns = [desc[0] for desc in cursor.description]
    return [dict(zip(columns, row)) for row in rows]


def search_by_part_name(
    cursor,
    part_name: str,
    only_published: bool = False,
    limit: int = 50
) -> list[dict[str, Any]]:
    """
    Busca por nome da peça consolidada.
    """
    normalized_name = normalize_text(part_name)

    query = """
        SELECT
            p.id AS part_id,
            p.name AS part_name,
            p.normalized_name,
            p.status AS part_status,
            pt.id AS part_type_id,
            pt.name AS part_type_name,
            p.description
        FROM catalog.parts p
        JOIN reference.part_types pt
          ON pt.id = p.part_type_id
        WHERE p.normalized_name LIKE %s
    """

    params: list[Any] = [f"%{normalized_name}%"]

    if only_published:
        query += " AND p.status = 'active'"

    query += """
        ORDER BY
            p.name
        LIMIT %s
    """
    params.append(limit)

    cursor.execute(query, tuple(params))
    rows = cursor.fetchall()

    columns = [desc[0] for desc in cursor.description]
    return [dict(zip(columns, row)) for row in rows]


def search_by_part_type(
    cursor,
    part_type_name: str,
    only_published: bool = False,
    limit: int = 50
) -> list[dict[str, Any]]:
    """
    Busca peças por tipo de peça.
    Exemplo:
    - filtro de óleo
    - vela de ignição
    """
    normalized_name = normalize_text(part_type_name)

    query = """
        SELECT
            p.id AS part_id,
            p.name AS part_name,
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
        ORDER BY
            p.name
        LIMIT %s
    """
    params.append(limit)

    cursor.execute(query, tuple(params))
    rows = cursor.fetchall()

    columns = [desc[0] for desc in cursor.description]
    return [dict(zip(columns, row)) for row in rows]


def search_by_part_type_alias(
    cursor,
    alias: str,
    only_published: bool = False,
    limit: int = 50
) -> list[dict[str, Any]]:
    """
    Busca peças por alias de tipo de peça.
    Exemplo:
    - "filtro óleo"
    - "filtro do motor"
    """
    normalized_alias = normalize_text(alias)

    query = """
        SELECT
            p.id AS part_id,
            p.name AS part_name,
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
        ORDER BY
            p.name
        LIMIT %s
    """
    params.append(limit)

    cursor.execute(query, tuple(params))
    rows = cursor.fetchall()

    columns = [desc[0] for desc in cursor.description]
    return [dict(zip(columns, row)) for row in rows]


def search_equivalents_by_code(
    cursor,
    code: str,
    only_published: bool = False
) -> list[dict[str, Any]]:
    """
    Busca equivalentes de um código via cluster.

    Retorna todos os códigos do mesmo cluster, inclusive fabricante.
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
            c.id AS cluster_id,
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

    cursor.execute(query, tuple(params))
    rows = cursor.fetchall()

    columns = [desc[0] for desc in cursor.description]
    return [dict(zip(columns, row)) for row in rows]