"""
config.py

Fonte única de configuração do projeto.

Responsável por:
- ler variáveis de ambiente
- fornecer configurações padronizadas do banco
- evitar credenciais hardcoded espalhadas pelo projeto
"""

from dataclasses import dataclass
import os


def _get_env(name: str, default: str | None = None) -> str | None:
    """
    Lê uma variável de ambiente.
    """
    return os.getenv(name, default)


def _get_env_int(name: str, default: int) -> int:
    """
    Lê uma variável de ambiente inteira.
    """
    value = os.getenv(name)

    if value is None:
        return default

    return int(value)


@dataclass(frozen=True)
class DatabaseConfig:
    host: str
    database: str
    user: str
    password: str
    port: int


@dataclass(frozen=True)
class AppConfig:
    db: DatabaseConfig
    environment: str
    log_level: str


def get_database_config() -> DatabaseConfig:
    """
    Retorna a configuração do banco de dados.

    Variáveis suportadas:
    - CATALOGO_DB_HOST
    - CATALOGO_DB_NAME
    - CATALOGO_DB_USER
    - CATALOGO_DB_PASSWORD
    - CATALOGO_DB_PORT
    """
    return DatabaseConfig(
        host=_get_env("CATALOGO_DB_HOST", "localhost"),
        database=_get_env("CATALOGO_DB_NAME", "catalogo"),
        user=_get_env("CATALOGO_DB_USER", "admin"),
        password=_get_env("CATALOGO_DB_PASSWORD", "admin"),
        port=_get_env_int("CATALOGO_DB_PORT", 5432),
    )


def get_app_config() -> AppConfig:
    """
    Retorna a configuração geral da aplicação.
    """
    return AppConfig(
        db=get_database_config(),
        environment=_get_env("CATALOGO_ENV", "development"),
        log_level=_get_env("CATALOGO_LOG_LEVEL", "INFO"),
    )