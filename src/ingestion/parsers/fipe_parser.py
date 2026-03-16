"""
Módulo de parsing e transformação de payloads FIPE.

Responsabilidades:
- receber dados brutos coletados da API FIPE;
- validar minimamente a estrutura recebida;
- transformar payloads externos em estruturas intermediárias estáveis;
- aplicar normalização inicial de nomes e descrições.

Este módulo NÃO deve:
- realizar chamadas HTTP;
- persistir dados em banco;
- conhecer detalhes operacionais de transação.

Observação:
- este arquivo define contratos e placeholders documentados;
- a implementação real das regras será feita na etapa de transformação.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ParsedFipeBrand:
    """
    Estrutura intermediária de marca extraída da FIPE.
    """

    external_source: str
    external_code: str
    raw_name: str
    normalized_name: str


@dataclass(slots=True)
class ParsedFipeModel:
    """
    Estrutura intermediária de modelo extraída da FIPE.
    """

    brand_external_code: str
    external_source: str
    external_code: str
    raw_name: str
    normalized_name: str


@dataclass(slots=True)
class ParsedFipeVehicle:
    """
    Estrutura intermediária de veículo/ano/variação extraída da FIPE.

    Observação:
    - neste momento, tratamos o retorno FIPE como evidência externa inicial;
    - a consolidação completa do domínio interno será refinada depois.
    """

    brand_external_code: str
    model_external_code: str
    external_source: str
    external_code: str
    raw_label: str
    normalized_label: str
    model_year: str | None
    fuel_type: str | None


class FipeParser:
    """
    Parser principal dos payloads FIPE.

    A ideia é manter uma camada explícita entre:
    payload bruto externo -> estrutura intermediária controlada.
    """

    EXTERNAL_SOURCE = "fipe"

    def parse_brand(self, payload: dict) -> ParsedFipeBrand:
        """
        Converte o payload bruto de marca em estrutura intermediária.

        Args:
            payload: registro bruto retornado pela API FIPE.

        Returns:
            Estrutura intermediária de marca.

        Raises:
            NotImplementedError: enquanto a regra real de parsing não for adicionada.
        """
        raise NotImplementedError("Parsing de marca FIPE ainda não foi implementado.")

    def parse_model(self, brand_code: str, payload: dict) -> ParsedFipeModel:
        """
        Converte o payload bruto de modelo em estrutura intermediária.

        Args:
            brand_code: código externo da marca à qual o modelo pertence.
            payload: registro bruto retornado pela API FIPE.

        Returns:
            Estrutura intermediária de modelo.

        Raises:
            NotImplementedError: enquanto a regra real de parsing não for adicionada.
        """
        raise NotImplementedError("Parsing de modelo FIPE ainda não foi implementado.")

    def parse_vehicle(self, brand_code: str, model_code: str, payload: dict) -> ParsedFipeVehicle:
        """
        Converte o payload bruto de ano/versão em estrutura intermediária de veículo.

        Args:
            brand_code: código externo da marca.
            model_code: código externo do modelo.
            payload: registro bruto retornado pela API FIPE.

        Returns:
            Estrutura intermediária de veículo.

        Raises:
            NotImplementedError: enquanto a regra real de parsing não for adicionada.
        """
        raise NotImplementedError("Parsing de veículo FIPE ainda não foi implementado.")

    def normalize_text(self, value: str) -> str:
        """
        Normaliza texto de forma previsível para uso em deduplicação lógica.

        Regras esperadas na implementação futura:
        - trim;
        - lowercase;
        - remoção controlada de espaços excedentes;
        - eventual remoção de caracteres acessórios, se validado.

        Args:
            value: texto original.

        Returns:
            Texto normalizado.

        Raises:
            NotImplementedError: enquanto a normalização real não for adicionada.
        """
        raise NotImplementedError("Normalização de texto FIPE ainda não foi implementada.")

    def extract_year_and_fuel(self, raw_label: str) -> tuple[str | None, str | None]:
        """
        Extrai ano e combustível de um rótulo bruto vindo da FIPE.

        Este método existe para explicitar que:
        - o formato textual da FIPE não deve ser espalhado pelo projeto;
        - a interpretação do rótulo deve ficar concentrada nesta camada.

        Args:
            raw_label: descrição textual bruta vinda da API.

        Returns:
            Tupla contendo:
            - ano/modelo interpretado, quando possível;
            - combustível interpretado, quando possível.

        Raises:
            NotImplementedError: enquanto a extração real não for adicionada.
        """
        raise NotImplementedError("Extração de ano/combustível FIPE ainda não foi implementada.")