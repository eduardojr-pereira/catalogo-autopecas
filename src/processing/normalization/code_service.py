"""
code_service.py

Responsável por inserir códigos de peças no banco
de forma segura e padronizada.
"""

from src.processing.normalization.code_normalizer import normalize_code


def code_already_exists(cursor, code: str) -> bool:
    """
    Verifica no banco se um código já foi inserido.

    O código recebido pode vir bruto; a função normaliza antes
    de consultar o banco.
    """

    normalized_code = normalize_code(code)

    if normalized_code is None:
        return False

    cursor.execute("""
        SELECT id
        FROM discovery.codes
        WHERE normalized_code = %s
        LIMIT 1
    """, (normalized_code,))

    result = cursor.fetchone()

    return result is not None


def insert_code(cursor, manufacturer_id: int, code: str):
    """
    Insere um código de peça no banco.

    Processo:
    1. normaliza o código
    2. verifica se já existe
    3. insere se não existir
    """

    normalized = normalize_code(code)

    if normalized is None:
        return None

    if code_already_exists(cursor, code):
        return None

    cursor.execute("""
        INSERT INTO discovery.codes (
            manufacturer_id,
            code,
            normalized_code
        )
        VALUES (%s, %s, %s)
        RETURNING id
    """, (manufacturer_id, code, normalized))

    code_id = cursor.fetchone()["id"]

    return code_id