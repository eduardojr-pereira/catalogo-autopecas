"""
code_normalizer.py

Responsável por normalizar e comparar códigos de peças automotivas.

Responsabilidades:
- normalizar códigos de peças
- comparar códigos já normalizados por regra única do projeto

Este módulo NÃO deve:
- acessar banco de dados
- executar queries
- conter regras de persistência
"""

import re


def normalize_code(code: str) -> str | None:
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

    code = code.strip().upper()
    code = re.sub(r"[^A-Z0-9]", "", code)

    if not code:
        return None

    return code


def codes_are_equal(code_a: str, code_b: str) -> bool:
    """
    Verifica se dois códigos representam a mesma peça
    após normalização.
    """

    normalized_a = normalize_code(code_a)
    normalized_b = normalize_code(code_b)

    if normalized_a is None or normalized_b is None:
        return False

    return normalized_a == normalized_b