"""
Módulo de coleta de dados da API FIPE.

Responsabilidades:
- centralizar a comunicação HTTP com a API FIPE;
- expor métodos de coleta desacoplados do restante do pipeline;
- padronizar comportamento de timeout, retry e validação básica;
- retornar payloads brutos para posterior parsing.

Este módulo NÃO deve:
- conhecer detalhes do schema interno do banco;
- aplicar regras de transformação de domínio;
- persistir dados diretamente.

Observação:
- neste estágio, o arquivo atua como placeholder documentado;
- a implementação real das chamadas HTTP será feita na etapa de cliente/coleta.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class FipeApiCollectorConfig:
    """
    Configuração do coletor da API FIPE.

    A implementação real poderá ser alimentada futuramente por `shared.config`
    ou por variáveis de ambiente do projeto.
    """

    base_url: str
    timeout_seconds: float = 10.0
    max_retries: int = 3


class FipeApiCollector:
    """
    Coletor HTTP da API FIPE.

    Fluxo esperado:
    1. consultar marcas;
    2. consultar modelos por marca;
    3. consultar anos/versões por modelo;
    4. retornar payloads brutos para a camada de parsing.

    Este coletor deve permanecer simples e previsível, funcionando como
    fronteira externa entre o projeto e a API FIPE.
    """

    def __init__(self, config: FipeApiCollectorConfig) -> None:
        """
        Inicializa o coletor com a configuração necessária.

        Args:
            config: configuração do coletor FIPE.
        """
        self._config = config

    @property
    def base_url(self) -> str:
        """
        Retorna a URL base configurada para a API FIPE.
        """
        return self._config.base_url

    def get_brands(self) -> list[dict[str, Any]]:
        """
        Coleta a lista bruta de marcas da API FIPE.

        Returns:
            Lista de dicionários exatamente no formato retornado pela API externa.

        Raises:
            NotImplementedError: enquanto a implementação real não for adicionada.
        """
        raise NotImplementedError("Implementação do endpoint de marcas ainda não foi adicionada.")

    def get_models(self, brand_code: str) -> dict[str, Any]:
        """
        Coleta a lista bruta de modelos de uma marca específica.

        Args:
            brand_code: código externo da marca na FIPE.

        Returns:
            Payload bruto retornado pela API FIPE para modelos.

        Raises:
            NotImplementedError: enquanto a implementação real não for adicionada.
        """
        raise NotImplementedError("Implementação do endpoint de modelos ainda não foi adicionada.")

    def get_years(self, brand_code: str, model_code: str) -> list[dict[str, Any]]:
        """
        Coleta a lista bruta de anos/combinações de veículo para um modelo.

        Args:
            brand_code: código externo da marca na FIPE.
            model_code: código externo do modelo na FIPE.

        Returns:
            Lista de payloads brutos de anos/versões do modelo consultado.

        Raises:
            NotImplementedError: enquanto a implementação real não for adicionada.
        """
        raise NotImplementedError("Implementação do endpoint de anos ainda não foi adicionada.")

    def _build_url(self, resource_path: str) -> str:
        """
        Constrói a URL absoluta de um recurso da API.

        Args:
            resource_path: caminho relativo do recurso.

        Returns:
            URL absoluta montada a partir da base configurada.
        """
        base = self.base_url.rstrip("/")
        path = resource_path.lstrip("/")
        return f"{base}/{path}"

    def _request_json(self, resource_path: str) -> Any:
        """
        Executa requisição HTTP e retorna JSON desserializado.

        Este método será o ponto central para:
        - timeout;
        - retry;
        - tratamento de status code;
        - validação mínima de payload.

        Args:
            resource_path: caminho relativo do endpoint.

        Returns:
            Estrutura JSON desserializada.

        Raises:
            NotImplementedError: enquanto a implementação real não for adicionada.
        """
        raise NotImplementedError("Camada HTTP do coletor FIPE ainda não foi implementada.")