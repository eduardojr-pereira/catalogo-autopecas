"""
Testes do parser FIPE.

Objetivos desta suíte:
- documentar a fronteira entre payload externo e estrutura intermediária;
- registrar cenários esperados de parsing;
- preparar a futura implementação de normalização e extração.

Observação:
- nesta fase, os testes são placeholders documentados;
- a lógica real será coberta quando o parser for implementado.
"""

from src.ingestion.parsers.fipe_parser import FipeParser


def build_parser() -> FipeParser:
    """
    Cria uma instância do parser para uso nos testes.
    """
    return FipeParser()


def test_should_expose_contract_for_parse_brand() -> None:
    """
    Deve expor contrato para parsing de marca.
    """
    parser = build_parser()

    assert hasattr(parser, "parse_brand")


def test_should_expose_contract_for_parse_model() -> None:
    """
    Deve expor contrato para parsing de modelo.
    """
    parser = build_parser()

    assert hasattr(parser, "parse_model")


def test_should_expose_contract_for_parse_vehicle() -> None:
    """
    Deve expor contrato para parsing de veículo.
    """
    parser = build_parser()

    assert hasattr(parser, "parse_vehicle")


def test_should_expose_contract_for_text_normalization() -> None:
    """
    Deve expor contrato para normalização de texto.
    """
    parser = build_parser()

    assert hasattr(parser, "normalize_text")


def test_should_expose_contract_for_year_and_fuel_extraction() -> None:
    """
    Deve expor contrato para extração de ano e combustível.
    """
    parser = build_parser()

    assert hasattr(parser, "extract_year_and_fuel")