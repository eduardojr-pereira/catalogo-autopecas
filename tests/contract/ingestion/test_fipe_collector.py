"""
Testes da camada coletora da API FIPE.

Objetivo
--------
Garantir que o collector:
- monte corretamente as chamadas;
- normalize os retornos esperados;
- trate falhas HTTP;
- trate payload inválido;
- mantenha comportamento previsível e isolado.
"""

from __future__ import annotations

from unittest.mock import Mock

import pytest
import requests

from src.ingestion.collectors.fipe_api_collector import FipeApiCollector, FipeApiError


def build_response(
    *,
    json_data=None,
    content: bytes = b'{"ok": true}',
    raise_for_status_side_effect=None,
) -> Mock:
    """
    Cria um mock de response HTTP compatível com os cenários do collector.
    """
    response = Mock()
    response.content = content
    response.json = Mock(return_value=json_data)
    response.raise_for_status = Mock()

    if raise_for_status_side_effect is not None:
        response.raise_for_status.side_effect = raise_for_status_side_effect

    return response


def test_list_brands_returns_data() -> None:
    session = Mock()
    session.get.return_value = build_response(
        json_data=[
            {"codigo": "59", "nome": "VW - VolksWagen"},
            {"codigo": "22", "nome": "Ford"},
        ]
    )

    collector = FipeApiCollector(session=session)

    result = collector.list_brands("carros")

    assert result == [
        {"codigo": "59", "nome": "VW - VolksWagen"},
        {"codigo": "22", "nome": "Ford"},
    ]
    session.get.assert_called_once_with(
        "https://parallelum.com.br/fipe/api/v1/carros/marcas",
        timeout=10,
    )


def test_list_models_returns_models_key_only() -> None:
    session = Mock()
    session.get.return_value = build_response(
        json_data={
            "modelos": [
                {"codigo": 1, "nome": "Gol"},
                {"codigo": 2, "nome": "Voyage"},
            ],
            "anos": [
                {"codigo": "2014-1", "nome": "2014 Gasolina"},
            ],
        }
    )

    collector = FipeApiCollector(session=session)

    result = collector.list_models("carros", "59")

    assert result == [
        {"codigo": 1, "nome": "Gol"},
        {"codigo": 2, "nome": "Voyage"},
    ]
    session.get.assert_called_once_with(
        "https://parallelum.com.br/fipe/api/v1/carros/marcas/59/modelos",
        timeout=10,
    )


def test_list_years_returns_data() -> None:
    session = Mock()
    session.get.return_value = build_response(
        json_data=[
            {"codigo": "2014-1", "nome": "2014 Gasolina"},
            {"codigo": "2014-2", "nome": "2014 Álcool"},
        ]
    )

    collector = FipeApiCollector(session=session)

    result = collector.list_years("carros", "59", "5940")

    assert result == [
        {"codigo": "2014-1", "nome": "2014 Gasolina"},
        {"codigo": "2014-2", "nome": "2014 Álcool"},
    ]
    session.get.assert_called_once_with(
        "https://parallelum.com.br/fipe/api/v1/carros/marcas/59/modelos/5940/anos",
        timeout=10,
    )


def test_get_vehicle_returns_detail() -> None:
    session = Mock()
    session.get.return_value = build_response(
        json_data={
            "Valor": "R$ 35.000,00",
            "Marca": "VW - VolksWagen",
            "Modelo": "Gol 1.0",
            "AnoModelo": 2014,
            "Combustivel": "Gasolina",
            "CodigoFipe": "005340-6",
        }
    )

    collector = FipeApiCollector(session=session)

    result = collector.get_vehicle("carros", "59", "5940", "2014-1")

    assert result["CodigoFipe"] == "005340-6"
    session.get.assert_called_once_with(
        "https://parallelum.com.br/fipe/api/v1/carros/marcas/59/modelos/5940/anos/2014-1",
        timeout=10,
    )


def test_invalid_vehicle_type_raises_value_error() -> None:
    collector = FipeApiCollector(session=Mock())

    with pytest.raises(ValueError):
        collector.list_brands("avioes")


def test_http_error_is_wrapped_as_fipe_api_error() -> None:
    session = Mock()
    session.get.return_value = build_response(
        json_data=None,
        raise_for_status_side_effect=requests.HTTPError("500 Server Error"),
    )

    collector = FipeApiCollector(session=session)

    with pytest.raises(FipeApiError, match="Falha na comunicação com a API FIPE"):
        collector.list_brands("carros")


def test_network_error_is_wrapped_as_fipe_api_error() -> None:
    session = Mock()
    session.get.side_effect = requests.ConnectionError("connection failed")

    collector = FipeApiCollector(session=session)

    with pytest.raises(FipeApiError, match="Falha na comunicação com a API FIPE"):
        collector.list_brands("carros")


def test_invalid_json_raises_fipe_api_error() -> None:
    response = Mock()
    response.content = b"not-json"
    response.raise_for_status = Mock()
    response.json.side_effect = ValueError("invalid json")

    session = Mock()
    session.get.return_value = response

    collector = FipeApiCollector(session=session)

    with pytest.raises(FipeApiError, match="JSON válido"):
        collector.list_brands("carros")


def test_empty_response_returns_empty_list_for_list_methods() -> None:
    response = Mock()
    response.content = b""
    response.raise_for_status = Mock()

    session = Mock()
    session.get.return_value = response

    collector = FipeApiCollector(session=session)

    assert collector.list_brands("carros") == []


def test_empty_response_returns_empty_dict_for_get_vehicle() -> None:
    response = Mock()
    response.content = b""
    response.raise_for_status = Mock()

    session = Mock()
    session.get.return_value = response

    collector = FipeApiCollector(session=session)

    assert collector.get_vehicle("carros", "59", "5940", "2014-1") == {}