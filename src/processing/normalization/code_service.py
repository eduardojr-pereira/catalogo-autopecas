"""
code_service.py

Responsável por inserir códigos de peças no banco
de forma segura e padronizada.
"""

# importa funções do normalizador
from src.processing.normalization.code_normalizer import (
    normalize_code,
    code_already_exists
)


def insert_code(cursor, manufacturer_id: int, code: str):
    """
    Insere um código de peça no banco.

    Processo:
    1. normaliza o código
    2. verifica se já existe
    3. insere se não existir
    """

    # normaliza o código recebido
    normalized = normalize_code(code)

    # verifica se já existe no banco
    if code_already_exists(cursor, normalized):
        return None

    # insere novo código
    cursor.execute("""
        INSERT INTO discovery.codes (
            manufacturer_id,
            code,
            normalized_code
        )
        VALUES (%s, %s, %s)
        RETURNING id
    """, (manufacturer_id, code, normalized))

    code_id = cursor.fetchone()[0]

    return code_id