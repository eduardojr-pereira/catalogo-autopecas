"""
conftest.py

Configuração compartilhada de testes com pytest.

Responsabilidades:
- ativar modo de teste
- conectar no banco catalogo_test
- fornecer conexão e cursores
- garantir rollback após cada teste
- fornecer cliente HTTP da API usando a mesma transação do teste
"""

import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
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


@pytest.fixture
def api_client(db_connection):
    """
    Cria um TestClient usando a mesma conexão transacional do teste.

    Isso garante que os dados inseridos pelo teste
    fiquem visíveis para a API.
    """
    from src.delivery.api.dependencies import get_db_cursor
    from src.delivery.api.main import app

    def override_get_db_cursor():
        cursor = db_connection.cursor(row_factory=dict_row)
        try:
            yield cursor
        finally:
            cursor.close()

    app.dependency_overrides[get_db_cursor] = override_get_db_cursor

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()