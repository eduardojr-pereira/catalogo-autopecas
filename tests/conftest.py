"""
conftest.py

Configuração compartilhada de testes com pytest.

Responsabilidades:

- ativar modo de teste
- conectar no banco catalogo_test
- fornecer conexão e cursor
- garantir rollback após cada teste

Isso garante isolamento completo entre testes.
"""

import os
import sys
from pathlib import Path

import pytest


# ativa modo de teste
os.environ["TESTING"] = "1"


sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.shared.db import get_connection  # noqa: E402


# ------------------------------------------------------
# FIXTURE DE CONEXÃO
# ------------------------------------------------------

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

    conn.close()


# ------------------------------------------------------
# FIXTURE DE CURSOR
# ------------------------------------------------------

@pytest.fixture
def db_cursor(db_connection):
    """
    Fornece cursor SQL para execução de queries nos testes.
    """

    cursor = db_connection.cursor()

    yield cursor

    cursor.close()


# ------------------------------------------------------
# LIMPEZA AUTOMÁTICA
# ------------------------------------------------------

@pytest.fixture(autouse=True)
def rollback_after_test(db_connection):
    """
    Garante que qualquer alteração feita por um teste
    seja revertida ao final.

    Isso mantém o banco limpo entre testes.
    """

    yield

    db_connection.rollback()