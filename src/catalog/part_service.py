"""
part_service.py

Responsável por inserir e consultar peças consolidadas do catálogo.
"""

from src.shared.utils import normalize_text


def insert_part(
    cursor,
    name: str,
    part_type_id: int,
    description: str = None,
    status: str = "active"
):
    """
    Insere uma peça consolidada no catálogo.
    """
    normalized_name = normalize_text(name)

    if normalized_name is not None:
        normalized_name = normalized_name.upper()

    cursor.execute("""
        INSERT INTO catalog.parts (
            name,
            normalized_name,
            part_type_id,
            description,
            status
        )
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id
    """, (name, normalized_name, part_type_id, description, status))

    return cursor.fetchone()[0]


def insert_part_attribute(
    cursor,
    part_id: int,
    attribute_name: str,
    attribute_value: str,
    unit: str = None,
    source: str = None
):
    """
    Insere um atributo técnico flexível para a peça.
    """
    cursor.execute("""
        INSERT INTO catalog.part_attributes (
            part_id,
            attribute_name,
            attribute_value,
            unit,
            source
        )
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id
    """, (part_id, attribute_name, attribute_value, unit, source))

    return cursor.fetchone()[0]


def link_part_to_cluster(cursor, part_id: int, cluster_id: int):
    """
    Vincula uma peça consolidada a um cluster.
    """
    cursor.execute("""
        UPDATE catalog.clusters
        SET part_id = %s
        WHERE id = %s
    """, (part_id, cluster_id))