"""
Parser de payloads da API FIPE para estruturas internas do projeto.

Responsabilidades:
- transformar payloads brutos da FIPE em dicionários compatíveis com o domínio interno;
- padronizar campos mínimos de rastreabilidade da fonte externa;
- validar presença mínima de campos esperados;
- manter a camada de parsing desacoplada de HTTP e persistência.

Este módulo NÃO deve:
- realizar chamadas HTTP;
- conhecer detalhes de sessão/transação de banco;
- persistir entidades;
- aplicar regras complexas de negócio do catálogo final.

Observações:
- a FIPE é tratada como fonte externa de referência, não como identidade primária do domínio;
- o parser preserva rastreabilidade com `external_source="fipe"` e `external_code`;
- normalizações avançadas de nomenclatura podem ser adicionadas futuramente em outra camada.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


FIPE_EXTERNAL_SOURCE = "fipe"
ALLOWED_VEHICLE_TYPES = {"carros", "motos", "caminhoes"}


class FipeParserError(ValueError):
    """
    Erro de parsing para payloads inválidos ou incompletos da FIPE.
    """


@dataclass(slots=True, frozen=True)
class FipeParser:
    """
    Parser de dados brutos da FIPE.

    A classe converte payloads externos em estruturas internas mínimas
    para posterior carga nas tabelas `reference.*`.
    """

    external_source: str = FIPE_EXTERNAL_SOURCE

    def parse_brand(
        self,
        raw_brand: dict[str, Any],
        *,
        vehicle_type: str,
    ) -> dict[str, Any]:
        """
        Converte uma marca bruta da FIPE em payload interno.

        Args:
            raw_brand:
                Dicionário bruto retornado pela FIPE, por exemplo:
                {"codigo": "59", "nome": "VW - VolksWagen"}
            vehicle_type:
                Tipo FIPE consultado: carros, motos ou caminhoes.

        Returns:
            Dicionário interno pronto para posterior persistência.

        Raises:
            FipeParserError:
                Se os campos mínimos obrigatórios não estiverem presentes.
        """
        self._validate_vehicle_type(vehicle_type)

        external_code = self._require_value(raw_brand, "codigo", context="marca")
        name = self._require_value(raw_brand, "nome", context="marca")

        return {
            "name": self._normalize_text(name),
            "external_source": self.external_source,
            "external_code": str(external_code),
            "vehicle_type": vehicle_type,
        }

    def parse_model(
        self,
        raw_model: dict[str, Any],
        *,
        brand_external_code: str,
        vehicle_type: str,
    ) -> dict[str, Any]:
        """
        Converte um modelo bruto da FIPE em payload interno.

        Args:
            raw_model:
                Dicionário bruto retornado pela FIPE, por exemplo:
                {"codigo": 5940, "nome": "Gol 1.0"}
            brand_external_code:
                Código externo da marca na FIPE, usado para rastreabilidade contextual.
            vehicle_type:
                Tipo FIPE consultado.

        Returns:
            Dicionário interno do modelo.

        Raises:
            FipeParserError:
                Se os campos mínimos obrigatórios não estiverem presentes.
        """
        self._validate_vehicle_type(vehicle_type)

        external_code = self._require_value(raw_model, "codigo", context="modelo")
        name = self._require_value(raw_model, "nome", context="modelo")

        return {
            "name": self._normalize_text(name),
            "external_source": self.external_source,
            "external_code": str(external_code),
            "brand_external_code": str(brand_external_code),
            "vehicle_type": vehicle_type,
        }

    def parse_year(
        self,
        raw_year: dict[str, Any],
        *,
        brand_external_code: str,
        model_external_code: str,
        vehicle_type: str,
    ) -> dict[str, Any]:
        """
        Converte um item bruto de ano/combustível da FIPE em payload intermediário.

        Exemplo de entrada:
            {"codigo": "2014-1", "nome": "2014 Gasolina"}

        Args:
            raw_year:
                Payload bruto retornado pelo endpoint de anos.
            brand_external_code:
                Código externo da marca.
            model_external_code:
                Código externo do modelo.
            vehicle_type:
                Tipo FIPE consultado.

        Returns:
            Dicionário intermediário útil para posterior consulta de detalhe do veículo
            e eventual carga em `reference.vehicles`.

        Raises:
            FipeParserError:
                Se os campos mínimos obrigatórios não estiverem presentes.
        """
        self._validate_vehicle_type(vehicle_type)

        external_code = self._require_value(raw_year, "codigo", context="ano")
        name = self._require_value(raw_year, "nome", context="ano")

        parsed_name = self._parse_year_label(str(name))

        return {
            "external_source": self.external_source,
            "external_code": str(external_code),
            "brand_external_code": str(brand_external_code),
            "model_external_code": str(model_external_code),
            "vehicle_type": vehicle_type,
            "label": self._normalize_text(name),
            "model_year": parsed_name["model_year"],
            "fuel_label": parsed_name["fuel_label"],
        }

    def parse_vehicle(
        self,
        raw_vehicle: dict[str, Any],
        *,
        brand_external_code: str,
        model_external_code: str,
        year_external_code: str,
        vehicle_type: str,
    ) -> dict[str, Any]:
        """
        Converte o detalhe bruto de veículo da FIPE em payload interno de veículo.

        Exemplo resumido de entrada:
            {
                "Valor": "R$ 35.000,00",
                "Marca": "VW - VolksWagen",
                "Modelo": "Gol 1.0",
                "AnoModelo": 2014,
                "Combustivel": "Gasolina",
                "CodigoFipe": "005340-6",
                "MesReferencia": "março de 2026",
                "TipoVeiculo": 1,
                "SiglaCombustivel": "G"
            }

        Args:
            raw_vehicle:
                Payload bruto retornado pelo endpoint de detalhe.
            brand_external_code:
                Código externo da marca.
            model_external_code:
                Código externo do modelo.
            year_external_code:
                Código externo da combinação ano/combustível.
            vehicle_type:
                Tipo FIPE consultado.

        Returns:
            Dicionário interno de veículo.

        Raises:
            FipeParserError:
                Se campos mínimos obrigatórios não estiverem presentes.
        """
        self._validate_vehicle_type(vehicle_type)

        brand_name = self._require_value(raw_vehicle, "Marca", context="veículo")
        model_name = self._require_value(raw_vehicle, "Modelo", context="veículo")
        model_year = self._require_value(raw_vehicle, "AnoModelo", context="veículo")
        fuel_label = self._require_value(raw_vehicle, "Combustivel", context="veículo")
        fipe_code = self._require_value(raw_vehicle, "CodigoFipe", context="veículo")

        return {
            "brand_name": self._normalize_text(brand_name),
            "model_name": self._normalize_text(model_name),
            "model_year": self._coerce_int(model_year, field_name="AnoModelo"),
            "fuel_label": self._normalize_text(fuel_label),
            "fipe_code": self._normalize_text(fipe_code),
            "price_text": self._optional_text(raw_vehicle.get("Valor")),
            "reference_month": self._optional_text(raw_vehicle.get("MesReferencia")),
            "fuel_abbreviation": self._optional_text(raw_vehicle.get("SiglaCombustivel")),
            "vehicle_type": vehicle_type,
            "external_source": self.external_source,
            "external_code": str(year_external_code),
            "brand_external_code": str(brand_external_code),
            "model_external_code": str(model_external_code),
        }

    @staticmethod
    def _require_value(
        payload: dict[str, Any],
        field_name: str,
        *,
        context: str,
    ) -> Any:
        """
        Garante que um campo obrigatório exista e não esteja vazio.
        """
        if field_name not in payload:
            raise FipeParserError(
                f"Campo obrigatório ausente no payload de {context}: '{field_name}'."
            )

        value = payload[field_name]

        if value is None:
            raise FipeParserError(
                f"Campo obrigatório nulo no payload de {context}: '{field_name}'."
            )

        if isinstance(value, str) and not value.strip():
            raise FipeParserError(
                f"Campo obrigatório vazio no payload de {context}: '{field_name}'."
            )

        return value

    @staticmethod
    def _normalize_text(value: Any) -> str:
        """
        Normaliza texto mínimo removendo espaços excedentes.
        """
        return str(value).strip()

    @staticmethod
    def _optional_text(value: Any) -> str | None:
        """
        Normaliza um campo textual opcional.
        """
        if value is None:
            return None

        normalized = str(value).strip()
        return normalized or None

    @staticmethod
    def _coerce_int(value: Any, *, field_name: str) -> int:
        """
        Converte um valor para inteiro com erro explícito quando inválido.
        """
        try:
            return int(value)
        except (TypeError, ValueError) as exc:
            raise FipeParserError(
                f"Campo '{field_name}' não pôde ser convertido para inteiro: {value!r}."
            ) from exc

    @staticmethod
    def _parse_year_label(label: str) -> dict[str, Any]:
        """
        Extrai ano modelo e rótulo de combustível a partir do campo `nome`
        retornado pelo endpoint de anos da FIPE.

        Exemplos:
            '2014 Gasolina' -> {model_year: 2014, fuel_label: 'Gasolina'}
            '32000 Diesel'  -> {model_year: 32000, fuel_label: 'Diesel'}

        Observação:
        a FIPE pode usar códigos/valores especiais em alguns cenários.
        Aqui preservamos a estratégia simples:
        - primeiro token numérico -> model_year
        - restante do texto -> fuel_label
        """
        normalized = label.strip()

        if not normalized:
            raise FipeParserError("Rótulo de ano da FIPE está vazio.")

        parts = normalized.split(maxsplit=1)

        if not parts:
            raise FipeParserError("Rótulo de ano da FIPE está inválido.")

        try:
            model_year = int(parts[0])
        except ValueError as exc:
            raise FipeParserError(
                f"Não foi possível extrair o ano modelo do rótulo FIPE: {label!r}."
            ) from exc

        fuel_label = parts[1].strip() if len(parts) > 1 else None

        return {
            "model_year": model_year,
            "fuel_label": fuel_label,
        }

    @staticmethod
    def _validate_vehicle_type(vehicle_type: str) -> None:
        """
        Valida os tipos de veículo aceitos pela integração FIPE.
        """
        if vehicle_type not in ALLOWED_VEHICLE_TYPES:
            allowed = ", ".join(sorted(ALLOWED_VEHICLE_TYPES))
            raise FipeParserError(
                f"vehicle_type inválido: '{vehicle_type}'. Valores permitidos: {allowed}."
            )