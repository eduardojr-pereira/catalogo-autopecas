"""
utils.py

Funções utilitárias compartilhadas do projeto.

Responsabilidades:
- fornecer helpers genéricos reutilizáveis
- evitar duplicação de lógica simples entre módulos
- manter separação entre utilitário genérico e regra de domínio

Este módulo NÃO deve:
- conter regras de negócio do catálogo
- acessar banco de dados diretamente
- depender de contexto específico (FIPE, catalog, etc)
"""

from typing import Any


def normalize_text(value: Any) -> str | None:
    """
    Normaliza texto de forma genérica.

    Regras:
    - converte para string
    - remove espaços no início e fim
    - reduz múltiplos espaços internos
    - não altera acentuação nem caracteres especiais

    Retorna None se valor for None ou vazio após limpeza.
    """
    if value is None:
        return None

    text = str(value).strip()

    if not text:
        return None

    return " ".join(text.split())