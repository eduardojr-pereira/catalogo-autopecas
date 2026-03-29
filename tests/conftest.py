"""
conftest.py

Configuração compartilhada de testes com pytest.

Responsabilidades:
- ativar modo de teste
- conectar no banco catalogo_test
- fornecer conexão e cursores
- garantir rollback após cada teste

Isso garante isolamento entre testes sem conflitar
com transações internas abertas pelo código testado.
"""

import os
import sys
from pathlib import Path

import pytest
from psycopg.rows import dict_row


# ativa modo de teste
os.environ["TESTING"] = "1"

sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.shared.db import get_connection  # noqa: E402


@pytest.fixture
def db_connection():
    """
    Cria uma conexão com o banco de testes.

    O autocommit permanece desabilitado para permitir
    rollback automático após cada teste.
    """
    conn = get_connection()
    conn.autocommit = False

    yield conn

    conn.rollback()
    conn.close()


@pytest.fixture
def db_cursor(db_connection):
    """
    Fornece cursor SQL padrão para testes estruturais e queries manuais.

    Este cursor retorna linhas em formato tuple.
    """
    cursor = db_connection.cursor()

    yield cursor

    cursor.close()


@pytest.fixture
def db_dict_cursor(db_connection):
    """
    Fornece cursor SQL com rows em formato dict.

    Este cursor deve ser usado em testes que esperam acesso
    por chave, como row["id"].
    """
    cursor = db_connection.cursor(row_factory=dict_row)

    yield cursor

    cursor.close()