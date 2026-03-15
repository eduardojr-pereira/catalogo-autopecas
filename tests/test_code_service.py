import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.processing.normalization.code_service import insert_code


def test_insert_new_code(db_cursor):
    """
    Verifica se um código novo é inserido corretamente.
    """

    # cria fabricante
    db_cursor.execute("""
        INSERT INTO reference.manufacturers (name)
        VALUES ('Service Test Manufacturer')
        RETURNING id
    """)

    manufacturer_id = db_cursor.fetchone()[0]

    # insere código
    code_id = insert_code(db_cursor, manufacturer_id, "OC-1196")

    assert code_id is not None


def test_duplicate_code_not_inserted(db_cursor):
    """
    Verifica se códigos duplicados não são inseridos.
    """

    # cria fabricante
    db_cursor.execute("""
        INSERT INTO reference.manufacturers (name)
        VALUES ('Duplicate Manufacturer')
        RETURNING id
    """)

    manufacturer_id = db_cursor.fetchone()[0]

    # primeira inserção
    insert_code(db_cursor, manufacturer_id, "OC-1196")

    # segunda inserção
    result = insert_code(db_cursor, manufacturer_id, "OC1196")

    # deve retornar None pois já existe
    assert result is None