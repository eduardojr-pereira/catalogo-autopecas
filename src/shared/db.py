"""
db.py

Utilitários de conexão com PostgreSQL.
"""

from contextlib import contextmanager
import psycopg
from psycopg.rows import dict_row
from src.shared.config import get_database_config
from typing import Any, Sequence

def get_connection():
    """
    Cria e retorna conexão com PostgreSQL (psycopg3).
    """
    db_config = get_database_config()

    return psycopg.connect(
        host=db_config.host,
        dbname=db_config.database,
        user=db_config.user,
        password=db_config.password,
        port=db_config.port,
    )


@contextmanager
def get_cursor(dict_mode: bool = True):
    conn = get_connection()

    try:
        if dict_mode:
            cursor = conn.cursor(row_factory=dict_row)
        else:
            cursor = conn.cursor()

        yield cursor
        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        cursor.close()
        conn.close()


def execute_query(cursor, query: str, params: Sequence[Any] | None = None):
    if params is None:
        cursor.execute(query)
    else:
        cursor.execute(query, params)