"""
code_normalizer.py

Responsável por normalizar e comparar códigos de peças automotivas.
"""

import re


def normalize_code(code: str) -> str:
    """
    Normaliza um código de peça automotiva.

    Regras:
    - remove espaços nas extremidades
    - converte para maiúsculo
    - remove espaços, hífens e caracteres especiais
    - mantém apenas letras e números

    Exemplos:
    15400-RTA-003 -> 15400RTA003 
    oc-1196 -> OC1196
    """

    if code is None:
        return None

    # remove espaços no início e no fim
    code = code.strip()

    # converte para maiúsculo
    code = code.upper()

    # remove tudo que não for letra ou número
    # isso já remove espaços, hífens e outros separadores
    code = re.sub(r"[^A-Z0-9]", "", code)

    return code


def codes_are_equal(code_a: str, code_b: str) -> bool:
    """
    Verifica se dois códigos representam a mesma peça
    após normalização.
    """

    normalized_a = normalize_code(code_a)
    normalized_b = normalize_code(code_b)

    # se algum dos dois for inválido, consideramos que não são iguais
    if normalized_a is None or normalized_b is None:
        return False

    return normalized_a == normalized_b


def code_already_exists(cursor, code: str) -> bool:
    """
    Verifica no banco se um código já foi inserido.

    O código recebido pode vir bruto; a função normaliza antes
    de consultar o banco.
    """

    normalized_code = normalize_code(code)

    # se não houver código válido, considera que não existe
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