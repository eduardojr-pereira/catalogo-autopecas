"""
Módulo responsável por coletar dados brutos da API pública da Tabela FIPE.

Objetivo
--------
Encapsular o consumo HTTP da FIPE em uma camada isolada, previsível e reutilizável,
sem acoplamento com parser, loader ou persistência.

Diretrizes de arquitetura
-------------------------
- Este módulo retorna dados crus da API FIPE.
- Este módulo não realiza transformação para o schema interno.
- Este módulo não acessa banco de dados.
- Este módulo concentra tratamento de erros de comunicação.
- Este módulo deve ser facilmente mockável em testes.

Fonte externa
-------------
API pública utilizada:
https://parallelum.com.br/fipe/api/v1
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import requests


FIPE_BASE_URL = "https://parallelum.com.br/fipe/api/v1"
FIPE_TIMEOUT_SECONDS = 10
ALLOWED_VEHICLE_TYPES = {"carros", "motos", "caminhoes"}


class FipeApiError(Exception):
    """
    Exceção de domínio para falhas no consumo da API FIPE.

    Esta exceção padroniza erros de comunicação, payload inválido
    e respostas inesperadas da fonte externa.
    """


@dataclass(frozen=True)
class FipeApiCollector:
    """
    Cliente HTTP síncrono para a API pública da Tabela FIPE.

    Parâmetros
    ----------
    base_url:
        URL base da API FIPE.
    timeout:
        Timeout das requisições HTTP, em segundos.
    session:
        Sessão HTTP injetável para facilitar testes e reaproveitamento de conexão.
    """

    base_url: str = FIPE_BASE_URL
    timeout: int = FIPE_TIMEOUT_SECONDS
    session: requests.Session | None = None

    def __post_init__(self) -> None:
        """
        Garante a existência de uma sessão HTTP utilizável.

        Como a dataclass está frozen, usamos object.__setattr__.
        """
        if self.session is None:
            object.__setattr__(self, "session", requests.Session())

    def list_brands(self, vehicle_type: str) -> list[dict[str, Any]]:
        """
        Lista marcas para um tipo de veículo.

        Exemplo de endpoint:
        GET /carros/marcas
        """
        self._validate_vehicle_type(vehicle_type)
        path = f"/{vehicle_type}/marcas"
        response = self._get_json(path)

        if response is None:
            return []

        if not isinstance(response, list):
            raise FipeApiError("Resposta inválida ao listar marcas da FIPE.")

        return response

    def list_models(self, vehicle_type: str, brand_code: str) -> list[dict[str, Any]]:
        """
        Lista modelos de uma marca.

        Exemplo de endpoint:
        GET /carros/marcas/{brand_code}/modelos

        Observação
        ----------
        A FIPE normalmente retorna um objeto com chaves como:
        {
            "modelos": [...],
            "anos": [...]
        }

        Aqui padronizamos o retorno apenas para a lista de modelos.
        """
        self._validate_vehicle_type(vehicle_type)
        path = f"/{vehicle_type}/marcas/{brand_code}/modelos"
        response = self._get_json(path)

        if response is None:
            return []

        if not isinstance(response, dict):
            raise FipeApiError("Resposta inválida ao listar modelos da FIPE.")

        models = response.get("modelos", [])

        if not isinstance(models, list):
            raise FipeApiError("Campo 'modelos' inválido na resposta da FIPE.")

        return models

    def list_years(
        self,
        vehicle_type: str,
        brand_code: str,
        model_code: str,
    ) -> list[dict[str, Any]]:
        """
        Lista anos/combinações de ano e combustível para um modelo.

        Exemplo de endpoint:
        GET /carros/marcas/{brand_code}/modelos/{model_code}/anos
        """
        self._validate_vehicle_type(vehicle_type)
        path = f"/{vehicle_type}/marcas/{brand_code}/modelos/{model_code}/anos"
        response = self._get_json(path)

        if response is None:
            return []

        if not isinstance(response, list):
            raise FipeApiError("Resposta inválida ao listar anos da FIPE.")

        return response

    def get_vehicle(
        self,
        vehicle_type: str,
        brand_code: str,
        model_code: str,
        year_code: str,
    ) -> dict[str, Any]:
        """
        Obtém o detalhe de um veículo/ano específico.

        Exemplo de endpoint:
        GET /carros/marcas/{brand_code}/modelos/{model_code}/anos/{year_code}
        """
        self._validate_vehicle_type(vehicle_type)
        path = (
            f"/{vehicle_type}/marcas/{brand_code}/modelos/"
            f"{model_code}/anos/{year_code}"
        )
        response = self._get_json(path)

        if response is None:
            return {}

        if not isinstance(response, dict):
            raise FipeApiError("Resposta inválida ao obter detalhe de veículo da FIPE.")

        return response

    def _get_json(self, path: str) -> Any:
        """
        Executa GET e retorna o JSON decodificado.

        Regras
        ------
        - HTTP não-2xx gera FipeApiError.
        - Erros de rede geram FipeApiError.
        - JSON inválido gera FipeApiError.
        """
        url = f"{self.base_url.rstrip('/')}/{path.lstrip('/')}"

        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
        except requests.RequestException as exc:
            raise FipeApiError(f"Falha na comunicação com a API FIPE: {exc}") from exc

        if not response.content:
            return None

        try:
            return response.json()
        except ValueError as exc:
            raise FipeApiError("Resposta da API FIPE não contém JSON válido.") from exc

    @staticmethod
    def _validate_vehicle_type(vehicle_type: str) -> None:
        """
        Valida os tipos oficiais aceitos pela FIPE.

        Tipos permitidos:
        - carros
        - motos
        - caminhoes
        """
        if vehicle_type not in ALLOWED_VEHICLE_TYPES:
            allowed = ", ".join(sorted(ALLOWED_VEHICLE_TYPES))
            raise ValueError(
                f"vehicle_type inválido: '{vehicle_type}'. "
                f"Valores permitidos: {allowed}."
            )