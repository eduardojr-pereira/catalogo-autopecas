"""
Testes do coletor da API FIPE.

Objetivos desta suíte:
- documentar o comportamento esperado do coletor;
- reservar os cenários principais da integração HTTP;
- preparar a estrutura para testes sem dependência da API real.

Observação:
- neste estágio, os testes atuam como placeholders documentados;
- os cenários reais serão implementados junto com a camada HTTP.
"""

from src.ingestion.collectors.fipe_api_collector import (
    FipeApiCollector,
    FipeApiCollectorConfig,
)


def build_collector() -> FipeApiCollector:
    """
    Cria uma instância de coletor para uso nos testes.
    """
    return FipeApiCollector(
        config=FipeApiCollectorConfig(
            base_url="https://parallelum.com.br/fipe/api/v1",
            timeout_seconds=10.0,
            max_retries=3,
        )
    )


def test_should_initialize_collector_with_expected_base_url() -> None:
    """
    Deve inicializar o coletor com a URL base esperada.
    """
    collector = build_collector()

    assert collector.base_url == "https://parallelum.com.br/fipe/api/v1"


def test_should_expose_contract_for_get_brands() -> None:
    """
    Deve expor contrato para coleta de marcas.

    Este teste existe para registrar a presença do método público
    que será implementado na etapa do cliente HTTP.
    """
    collector = build_collector()

    assert hasattr(collector, "get_brands")


def test_should_expose_contract_for_get_models() -> None:
    """
    Deve expor contrato para coleta de modelos por marca.
    """
    collector = build_collector()

    assert hasattr(collector, "get_models")


def test_should_expose_contract_for_get_years() -> None:
    """
    Deve expor contrato para coleta de anos/variações por modelo.
    """
    collector = build_collector()

    assert hasattr(collector, "get_years")