"""
config.py

Configuração central do banco de dados do projeto.

Este módulo define:

- parâmetros de conexão
- seleção automática de banco para ambiente de teste

Ambientes suportados:

DEV
    banco: catalogo

TEST
    banco: catalog_test
"""

import os
from dataclasses import dataclass


@dataclass
class DatabaseConfig:
    host: str
    database: str
    user: str
    password: str
    port: int


def get_database_config() -> DatabaseConfig:
    """
    Retorna configuração do banco de dados.

    Se a variável de ambiente TESTING estiver definida,
    o sistema utilizará o banco catalogo_test.
    """

    is_testing = os.getenv("TESTING") == "1"

    database_name = "catalog_test" if is_testing else "catalogo"

    return DatabaseConfig(
        host="localhost",
        database=database_name,
        user="admin",
        password="admin",
        port=5432,
    )