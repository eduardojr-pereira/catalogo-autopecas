"""
test_equivalence_loader.py

Testes de integração do equivalence_loader.

Valida:
- leitura de equivalências
- geração de clusters
- persistência correta
- idempotência do processo
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.processing.equivalence.equivalence_loader import run  # noqa: E402


def insert_manufacturer(cursor, name: str) -> int:
    cursor.execute("""
        INSERT INTO reference.manufacturers (
            name,
            manufacturer_type
        )
        VALUES (%s, %s)
        RETURNING id
    """, (name, "aftermarket"))

    return int(cursor.fetchone()["id"])


def insert_code(
    cursor,
    manufacturer_id: int,
    code: str,
    normalized_code: str,
) -> int:
    cursor.execute("""
        INSERT INTO discovery.codes (
            manufacturer_id,
            code,
            normalized_code
        )
        VALUES (%s, %s, %s)
        RETURNING id
    """, (manufacturer_id, code, normalized_code))

    return int(cursor.fetchone()["id"])


def insert_equivalence(
    cursor,
    code_a: int,
    code_b: int,
    confidence: float = 0.9,
) -> None:
    cursor.execute("""
        INSERT INTO discovery.code_equivalences (
            code_id_1,
            code_id_2,
            confidence_score,
            validation_status
        )
        VALUES (%s, %s, %s, 'approved')
    """, (code_a, code_b, confidence))


def count_discovery_clusters_for_codes(cursor, code_ids: list[int]) -> int:
    cursor.execute("""
        SELECT COUNT(DISTINCT cc.cluster_id) AS total
        FROM catalog.cluster_codes cc
        JOIN catalog.clusters c
          ON c.id = cc.cluster_id
        WHERE c.cluster_type = 'discovery'
          AND cc.code_id = ANY(%s)
    """, (code_ids,))

    return int(cursor.fetchone()["total"])


def count_links_for_codes(cursor, code_ids: list[int]) -> int:
    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM catalog.cluster_codes
        WHERE code_id = ANY(%s)
    """, (code_ids,))

    return int(cursor.fetchone()["total"])


def test_equivalence_loader_creates_clusters(db_dict_cursor):
    cursor = db_dict_cursor

    manufacturer_id = insert_manufacturer(cursor, "TEST_EQ_CLUSTER")

    c1 = insert_code(cursor, manufacturer_id, "A1", "A1")
    c2 = insert_code(cursor, manufacturer_id, "B1", "B1")
    c3 = insert_code(cursor, manufacturer_id, "C1", "C1")
    c4 = insert_code(cursor, manufacturer_id, "D1", "D1")

    insert_equivalence(cursor, c1, c2)
    insert_equivalence(cursor, c2, c3)
    insert_equivalence(cursor, c4, c4)

    summary = run(cursor=cursor)

    total_clusters = count_discovery_clusters_for_codes(
        cursor,
        [c1, c2, c3, c4],
    )

    assert summary["equivalence_count"] == 3
    assert summary["cluster_count"] == 2
    assert summary["created_clusters"] == 2
    assert total_clusters == 2


def test_equivalence_loader_creates_links(db_dict_cursor):
    cursor = db_dict_cursor

    manufacturer_id = insert_manufacturer(cursor, "TEST_EQ_LINKS")

    c1 = insert_code(cursor, manufacturer_id, "X1", "X1")
    c2 = insert_code(cursor, manufacturer_id, "Y1", "Y1")

    insert_equivalence(cursor, c1, c2)

    summary = run(cursor=cursor)

    total_links = count_links_for_codes(cursor, [c1, c2])

    assert summary["equivalence_count"] == 1
    assert summary["cluster_count"] == 1
    assert summary["inserted_links"] == 2
    assert total_links == 2


def test_equivalence_loader_is_idempotent(db_dict_cursor):
    cursor = db_dict_cursor

    manufacturer_id = insert_manufacturer(cursor, "TEST_EQ_IDEMPOTENT")

    c1 = insert_code(cursor, manufacturer_id, "Z1", "Z1")
    c2 = insert_code(cursor, manufacturer_id, "Z2", "Z2")

    insert_equivalence(cursor, c1, c2)

    first_summary = run(cursor=cursor)
    first_run_links = count_links_for_codes(cursor, [c1, c2])

    second_summary = run(cursor=cursor)
    second_run_links = count_links_for_codes(cursor, [c1, c2])

    assert first_summary["created_clusters"] == 1
    assert first_summary["inserted_links"] == 2
    assert second_summary["created_clusters"] == 0
    assert second_summary["reused_clusters"] == 1
    assert second_summary["inserted_links"] == 0
    assert first_run_links == second_run_links == 2