"""
Módulo de carga de referências de veículos.

Responsabilidades:
- persistir marcas, modelos e veículos no banco PostgreSQL;
- aplicar validação de campos obrigatórios antes da persistência;
- resolver dependências relacionais entre marca, modelo e veículo;
- garantir idempotência por meio de UPSERT com chaves externas;
- expor um orquestrador para carga completa em ordem obrigatória.

Este módulo NÃO deve:
- realizar chamadas HTTP;
- conhecer detalhes de coleta externa;
- transformar payload bruto da fonte;
- depender de CLI para execução;
- acoplar persistência com parsing.

Estratégia oficial:
- a fonte externa é rastreada por external_source + external_code;
- a ordem obrigatória de carga é:
    1) marcas
    2) modelos
    3) veículos
- a carga deve ser idempotente.

Contrato esperado:
brands:
[
    {
        "external_code": "...",
        "name": "..."
    }
]

models:
[
    {
        "external_code": "...",
        "brand_external_code": "...",
        "name": "..."
    }
]

vehicles:
[
    {
        "external_code": "...",
        "brand_external_code": "...",
        "model_external_code": "...",
        "model_year": 2020,
        "fuel_type": "...",
        "version_name": "...",
        "fipe_code": "..."
    }
]
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping

import psycopg
from psycopg import Connection
from psycopg.rows import dict_row


DEFAULT_EXTERNAL_SOURCE = "fipe"


class VehicleReferenceLoaderError(Exception):
    """Exceção base do loader de referências de veículos."""


class RequiredFieldError(VehicleReferenceLoaderError):
    """Erro lançado quando um campo obrigatório não é informado."""


class DependencyNotFoundError(VehicleReferenceLoaderError):
    """Erro lançado quando uma dependência relacional obrigatória não existe."""


@dataclass(frozen=True, slots=True)
class LoadResult:
    """
    Resultado resumido de uma etapa de carga.

    Observação:
    - como a estratégia usa UPSERT, o contador representa o número de registros
      processados pela etapa, e não necessariamente apenas inserções novas.
    """

    processed_count: int


@dataclass(frozen=True, slots=True)
class LoadAllResult:
    """Resultado consolidado da execução do orquestrador completo."""

    brands: LoadResult
    models: LoadResult
    vehicles: LoadResult


class VehicleReferenceLoader:
    """
    Loader de referências de veículos com persistência direta em PostgreSQL.

    Parâmetros:
    - connection:
        conexão psycopg já aberta e controlada externamente.
    - external_source:
        identificador oficial da fonte externa rastreada no domínio.
    """

    def __init__(
        self,
        connection: Connection[Any],
        external_source: str = DEFAULT_EXTERNAL_SOURCE,
    ) -> None:
        if not external_source or not external_source.strip():
            raise ValueError("external_source deve ser informado.")

        self._connection = connection
        self._external_source = external_source.strip()

    @property
    def external_source(self) -> str:
        """Retorna a fonte externa configurada para a carga."""
        return self._external_source

    def load_brands(self, brands: Iterable[Mapping[str, Any]]) -> LoadResult:
        """
        Carrega marcas em reference.vehicle_brands.

        Regras:
        - external_code é obrigatório;
        - name é obrigatório;
        - a carga é idempotente via ON CONFLICT.
        """
        processed_count = 0

        with self._connection.transaction():
            with self._connection.cursor() as cursor:
                for index, brand in enumerate(brands):
                    external_code = self._require_str(
                        payload=brand,
                        field_name="external_code",
                        entity_name="brand",
                        index=index,
                    )
                    name = self._require_str(
                        payload=brand,
                        field_name="name",
                        entity_name="brand",
                        index=index,
                    )

                    cursor.execute(
                        """
                        INSERT INTO reference.vehicle_brands (
                            external_source,
                            external_code,
                            name
                        )
                        VALUES (%s, %s, %s)
                        ON CONFLICT (external_source, external_code)
                        DO UPDATE
                        SET
                            name = EXCLUDED.name
                        """,
                        (self._external_source, external_code, name),
                    )
                    processed_count += 1

        return LoadResult(processed_count=processed_count)

    def load_models(self, models: Iterable[Mapping[str, Any]]) -> LoadResult:
        """
        Carrega modelos em reference.vehicle_models.

        Regras:
        - external_code é obrigatório;
        - brand_external_code é obrigatório;
        - name é obrigatório;
        - a marca referenciada deve existir previamente;
        - a carga é idempotente via ON CONFLICT.
        """
        processed_count = 0

        with self._connection.transaction():
            with self._connection.cursor(row_factory=dict_row) as cursor:
                for index, model in enumerate(models):
                    external_code = self._require_str(
                        payload=model,
                        field_name="external_code",
                        entity_name="model",
                        index=index,
                    )
                    brand_external_code = self._require_str(
                        payload=model,
                        field_name="brand_external_code",
                        entity_name="model",
                        index=index,
                    )
                    name = self._require_str(
                        payload=model,
                        field_name="name",
                        entity_name="model",
                        index=index,
                    )

                    brand_id = self._find_brand_id_or_raise(
                        cursor=cursor,
                        brand_external_code=brand_external_code,
                        model_index=index,
                    )

                    cursor.execute(
                        """
                        INSERT INTO reference.vehicle_models (
                            brand_id,
                            external_source,
                            external_code,
                            name
                        )
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (external_source, external_code)
                        DO UPDATE
                        SET
                            brand_id = EXCLUDED.brand_id,
                            name = EXCLUDED.name
                        """,
                        (brand_id, self._external_source, external_code, name),
                    )
                    processed_count += 1

        return LoadResult(processed_count=processed_count)

    def load_vehicles(self, vehicles: Iterable[Mapping[str, Any]]) -> LoadResult:
        """
        Carrega veículos em reference.vehicles.

        Regras:
        - external_code é obrigatório;
        - brand_external_code é obrigatório;
        - model_external_code é obrigatório;
        - model_year é obrigatório;
        - fuel_type é obrigatório;
        - version_name é obrigatório;
        - a marca referenciada deve existir;
        - o modelo referenciado deve existir;
        - a carga é idempotente via ON CONFLICT.
        """
        processed_count = 0

        with self._connection.transaction():
            with self._connection.cursor(row_factory=dict_row) as cursor:
                for index, vehicle in enumerate(vehicles):
                    external_code = self._require_str(
                        payload=vehicle,
                        field_name="external_code",
                        entity_name="vehicle",
                        index=index,
                    )
                    brand_external_code = self._require_str(
                        payload=vehicle,
                        field_name="brand_external_code",
                        entity_name="vehicle",
                        index=index,
                    )
                    model_external_code = self._require_str(
                        payload=vehicle,
                        field_name="model_external_code",
                        entity_name="vehicle",
                        index=index,
                    )
                    model_year = self._require_int(
                        payload=vehicle,
                        field_name="model_year",
                        entity_name="vehicle",
                        index=index,
                    )
                    fuel_type = self._require_str(
                        payload=vehicle,
                        field_name="fuel_type",
                        entity_name="vehicle",
                        index=index,
                    )
                    version_name = self._require_str(
                        payload=vehicle,
                        field_name="version_name",
                        entity_name="vehicle",
                        index=index,
                    )
                    fipe_code = self._optional_str(vehicle.get("fipe_code"))

                    brand_id = self._find_brand_id_or_raise(
                        cursor=cursor,
                        brand_external_code=brand_external_code,
                        model_index=index,
                        entity_name="vehicle",
                    )
                    model_id = self._find_model_id_or_raise(
                        cursor=cursor,
                        model_external_code=model_external_code,
                        vehicle_index=index,
                    )

                    cursor.execute(
                        """
                        INSERT INTO reference.vehicles (
                            brand_id,
                            model_id,
                            external_source,
                            external_code,
                            model_year,
                            fuel_type,
                            version_name,
                            fipe_code
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (external_source, external_code)
                        DO UPDATE
                        SET
                            brand_id = EXCLUDED.brand_id,
                            model_id = EXCLUDED.model_id,
                            model_year = EXCLUDED.model_year,
                            fuel_type = EXCLUDED.fuel_type,
                            version_name = EXCLUDED.version_name,
                            fipe_code = EXCLUDED.fipe_code
                        """,
                        (
                            brand_id,
                            model_id,
                            self._external_source,
                            external_code,
                            model_year,
                            fuel_type,
                            version_name,
                            fipe_code,
                        ),
                    )
                    processed_count += 1

        return LoadResult(processed_count=processed_count)

    def load_all(
        self,
        *,
        brands: Iterable[Mapping[str, Any]],
        models: Iterable[Mapping[str, Any]],
        vehicles: Iterable[Mapping[str, Any]],
    ) -> LoadAllResult:
        """
        Executa a carga completa respeitando a ordem oficial do domínio.

        Ordem obrigatória:
        - marcas
        - modelos
        - veículos
        """
        brand_result = self.load_brands(brands)
        model_result = self.load_models(models)
        vehicle_result = self.load_vehicles(vehicles)

        return LoadAllResult(
            brands=brand_result,
            models=model_result,
            vehicles=vehicle_result,
        )

    def _find_brand_id_or_raise(
        self,
        *,
        cursor: psycopg.Cursor[Any],
        brand_external_code: str,
        model_index: int,
        entity_name: str = "model",
    ) -> int:
        """
        Busca o brand_id pela identidade externa oficial.

        Lança erro explícito quando a marca ainda não foi carregada.
        """
        cursor.execute(
            """
            SELECT brand_id
            FROM reference.vehicle_brands
            WHERE external_source = %s
              AND external_code = %s
            """,
            (self._external_source, brand_external_code),
        )
        row = cursor.fetchone()

        if row is None:
            raise DependencyNotFoundError(
                f"{entity_name}[{model_index}] referencia brand_external_code "
                f"inexistente: {brand_external_code!r}."
            )

        return int(row["brand_id"])

    def _find_model_id_or_raise(
        self,
        *,
        cursor: psycopg.Cursor[Any],
        model_external_code: str,
        vehicle_index: int,
    ) -> int:
        """
        Busca o model_id pela identidade externa oficial.

        Lança erro explícito quando o modelo ainda não foi carregado.
        """
        cursor.execute(
            """
            SELECT model_id
            FROM reference.vehicle_models
            WHERE external_source = %s
              AND external_code = %s
            """,
            (self._external_source, model_external_code),
        )
        row = cursor.fetchone()

        if row is None:
            raise DependencyNotFoundError(
                f"vehicle[{vehicle_index}] referencia model_external_code "
                f"inexistente: {model_external_code!r}."
            )

        return int(row["model_id"])

    @staticmethod
    def _require_str(
        *,
        payload: Mapping[str, Any],
        field_name: str,
        entity_name: str,
        index: int,
    ) -> str:
        """Valida e retorna um campo string obrigatório."""
        value = payload.get(field_name)

        if value is None:
            raise RequiredFieldError(
                f"{entity_name}[{index}] campo obrigatório ausente: {field_name!r}."
            )

        if not isinstance(value, str):
            raise RequiredFieldError(
                f"{entity_name}[{index}] campo {field_name!r} deve ser string."
            )

        normalized = value.strip()
        if not normalized:
            raise RequiredFieldError(
                f"{entity_name}[{index}] campo {field_name!r} não pode ser vazio."
            )

        return normalized

    @staticmethod
    def _require_int(
        *,
        payload: Mapping[str, Any],
        field_name: str,
        entity_name: str,
        index: int,
    ) -> int:
        """Valida e retorna um campo inteiro obrigatório."""
        value = payload.get(field_name)

        if value is None:
            raise RequiredFieldError(
                f"{entity_name}[{index}] campo obrigatório ausente: {field_name!r}."
            )

        if not isinstance(value, int):
            raise RequiredFieldError(
                f"{entity_name}[{index}] campo {field_name!r} deve ser inteiro."
            )

        return value

    @staticmethod
    def _optional_str(value: Any) -> str | None:
        """Normaliza uma string opcional."""
        if value is None:
            return None

        if not isinstance(value, str):
            raise RequiredFieldError("Campo opcional informado com tipo inválido.")

        normalized = value.strip()
        return normalized or None