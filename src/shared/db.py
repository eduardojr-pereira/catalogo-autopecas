"""
db.py

Utilitários de conexão com PostgreSQL.
"""

import psycopg2

from src.shared.config import get_database_config


def get_connection():
    """
    Cria e retorna uma conexão com PostgreSQL usando a configuração central.
    """
    db_config = get_database_config()

    return psycopg2.connect(
        host=db_config.host,
        database=db_config.database,
        user=db_config.user,
        password=db_config.password,
        port=db_config.port,
    )