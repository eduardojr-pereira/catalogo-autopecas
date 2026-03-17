"""
Testes do loader de referência de veículos.

Objetivos desta suíte:
- documentar o contrato de persistência da importação FIPE;
- registrar expectativas de idempotência e integridade referencial;
- preparar a estrutura para os testes reais da camada de carga.

Observação:
- os testes abaixo são placeholders documentados;
- a persistência real será validada em etapa posterior.
"""

from src.ingestion.loaders.vehicle_reference_loader import VehicleReferenceLoader


def build_loader() -> VehicleReferenceLoader:
    """
    Cria uma instância do loader para uso nos testes.
    """
    return VehicleReferenceLoader()


def test_should_initialize_loader() -> None:
    """
    Deve inicializar o loader sem erro.
    """
    loader = build_loader()

    assert loader is not None


def test_should_expose_contract_for_upsert_brand() -> None:
    """
    Deve expor contrato para upsert de marca.
    """
    loader = build_loader()

    assert hasattr(loader, "upsert_brand")


def test_should_expose_contract_for_upsert_model() -> None:
    """
    Deve expor contrato para upsert de modelo.
    """
    loader = build_loader()

    assert hasattr(loader, "upsert_model")


def test_should_expose_contract_for_upsert_vehicle() -> None:
    """
    Deve expor contrato para upsert de veículo.
    """
    loader = build_loader()

    assert hasattr(loader, "upsert_vehicle")


def test_should_expose_contract_for_brand_integrity_validation() -> None:
    """
    Deve expor contrato para validação de existência de marca.
    """
    loader = build_loader()

    assert hasattr(loader, "ensure_brand_exists")


def test_should_expose_contract_for_model_integrity_validation() -> None:
    """
    Deve expor contrato para validação de existência de modelo.
    """
    loader = build_loader()

    assert hasattr(loader, "ensure_model_exists")