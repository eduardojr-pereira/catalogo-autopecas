"""
Testes do parser FIPE.

Objetivos:
- validar o contrato público do parser;
- garantir transformação previsível dos payloads brutos;
- proteger campos obrigatórios e rastreabilidade;
- documentar o comportamento esperado para marcas, modelos, anos e veículos.
"""

from __future__ import annotations

import pytest

from src.ingestion.parsers.fipe_parser import FipeParser, FipeParserError


def build_parser() -> FipeParser:
    """
    Cria uma instância padrão do parser para os testes.
    """
    return FipeParser()


def test_should_parse_brand_with_tracking_fields() -> None:
    parser = build_parser()

    raw_brand = {
        "codigo": "59",
        "nome": "VW - VolksWagen",
    }

    parsed = parser.parse_brand(raw_brand, vehicle_type="carros")

    assert parsed == {
        "name": "VW - VolksWagen",
        "external_source": "fipe",
        "external_code": "59",
        "vehicle_type": "carros",
    }


def test_should_parse_model_with_brand_context() -> None:
    parser = build_parser()

    raw_model = {
        "codigo": 5940,
        "nome": "Gol 1.0",
    }

    parsed = parser.parse_model(
        raw_model,
        brand_external_code="59",
        vehicle_type="carros",
    )

    assert parsed == {
        "name": "Gol 1.0",
        "external_source": "fipe",
        "external_code": "5940",
        "brand_external_code": "59",
        "vehicle_type": "carros",
    }


def test_should_parse_year_with_year_and_fuel_label() -> None:
    parser = build_parser()

    raw_year = {
        "codigo": "2014-1",
        "nome": "2014 Gasolina",
    }

    parsed = parser.parse_year(
        raw_year,
        brand_external_code="59",
        model_external_code="5940",
        vehicle_type="carros",
    )

    assert parsed == {
        "external_source": "fipe",
        "external_code": "2014-1",
        "brand_external_code": "59",
        "model_external_code": "5940",
        "vehicle_type": "carros",
        "label": "2014 Gasolina",
        "model_year": 2014,
        "fuel_label": "Gasolina",
    }


def test_should_parse_vehicle_detail_with_tracking_fields() -> None:
    parser = build_parser()

    raw_vehicle = {
        "Valor": "R$ 35.000,00",
        "Marca": "VW - VolksWagen",
        "Modelo": "Gol 1.0",
        "AnoModelo": 2014,
        "Combustivel": "Gasolina",
        "CodigoFipe": "005340-6",
        "MesReferencia": "março de 2026",
        "SiglaCombustivel": "G",
    }

    parsed = parser.parse_vehicle(
        raw_vehicle,
        brand_external_code="59",
        model_external_code="5940",
        year_external_code="2014-1",
        vehicle_type="carros",
    )

    assert parsed == {
        "brand_name": "VW - VolksWagen",
        "model_name": "Gol 1.0",
        "model_year": 2014,
        "fuel_label": "Gasolina",
        "fipe_code": "005340-6",
        "price_text": "R$ 35.000,00",
        "reference_month": "março de 2026",
        "fuel_abbreviation": "G",
        "vehicle_type": "carros",
        "external_source": "fipe",
        "external_code": "2014-1",
        "brand_external_code": "59",
        "model_external_code": "5940",
    }


def test_should_raise_error_for_invalid_vehicle_type() -> None:
    parser = build_parser()

    with pytest.raises(FipeParserError, match="vehicle_type inválido"):
        parser.parse_brand(
            {"codigo": "59", "nome": "VW - VolksWagen"},
            vehicle_type="avioes",
        )


def test_should_raise_error_when_brand_code_is_missing() -> None:
    parser = build_parser()

    with pytest.raises(FipeParserError, match="Campo obrigatório ausente"):
        parser.parse_brand(
            {"nome": "VW - VolksWagen"},
            vehicle_type="carros",
        )


def test_should_raise_error_when_model_name_is_empty() -> None:
    parser = build_parser()

    with pytest.raises(FipeParserError, match="Campo obrigatório vazio"):
        parser.parse_model(
            {"codigo": "5940", "nome": "   "},
            brand_external_code="59",
            vehicle_type="carros",
        )


def test_should_raise_error_when_year_label_is_invalid() -> None:
    parser = build_parser()

    with pytest.raises(FipeParserError, match="Não foi possível extrair o ano modelo"):
        parser.parse_year(
            {"codigo": "foo", "nome": "Gasolina"},
            brand_external_code="59",
            model_external_code="5940",
            vehicle_type="carros",
        )


def test_should_raise_error_when_vehicle_year_is_not_integer() -> None:
    parser = build_parser()

    raw_vehicle = {
        "Marca": "VW - VolksWagen",
        "Modelo": "Gol 1.0",
        "AnoModelo": "abc",
        "Combustivel": "Gasolina",
        "CodigoFipe": "005340-6",
    }

    with pytest.raises(FipeParserError, match="não pôde ser convertido para inteiro"):
        parser.parse_vehicle(
            raw_vehicle,
            brand_external_code="59",
            model_external_code="5940",
            year_external_code="2014-1",
            vehicle_type="carros",
        )


def test_should_allow_missing_optional_vehicle_fields() -> None:
    parser = build_parser()

    raw_vehicle = {
        "Marca": "VW - VolksWagen",
        "Modelo": "Gol 1.0",
        "AnoModelo": 2014,
        "Combustivel": "Gasolina",
        "CodigoFipe": "005340-6",
    }

    parsed = parser.parse_vehicle(
        raw_vehicle,
        brand_external_code="59",
        model_external_code="5940",
        year_external_code="2014-1",
        vehicle_type="carros",
    )

    assert parsed["price_text"] is None
    assert parsed["reference_month"] is None
    assert parsed["fuel_abbreviation"] is None