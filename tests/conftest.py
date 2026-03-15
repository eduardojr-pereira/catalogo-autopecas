"""
conftest.py

Configuração compartilhada de testes com pytest para o catálogo automotivo.

Este arquivo fornece:
- conexão com PostgreSQL
- cursor para execução de SQL
- rollback automático após cada teste

Assim, cada teste roda de forma isolada e não deixa resíduos no banco.
"""

import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.shared.db import get_connection  # noqa: E402


# ------------------------------------------------------
# FIXTURE DE CONEXÃO
# ------------------------------------------------------
@pytest.fixture
def db_connection():
    """
    Cria uma conexão com o PostgreSQL para ser usada nos testes.

    A conexão é aberta no início do teste e fechada ao final.
    O autocommit fica desabilitado para permitir rollback controlado.
    """
    conn = get_connection()
    conn.autocommit = False

    yield conn

    conn.close()


# ------------------------------------------------------
# FIXTURE DE CURSOR
# ------------------------------------------------------
@pytest.fixture
def db_cursor(db_connection):
    """
    Cria um cursor para executar comandos SQL durante o teste.
    """
    cur = db_connection.cursor()
    yield cur
    cur.close()


# ------------------------------------------------------
# FIXTURE DE LIMPEZA
# ------------------------------------------------------
@pytest.fixture(autouse=True)
def rollback_after_test(db_connection):
    """
    Garante que toda alteração feita por um teste seja desfeita ao final.

    Isso mantém os testes isolados e evita acúmulo de dados no banco.
    """
    yield
    db_connection.rollback()