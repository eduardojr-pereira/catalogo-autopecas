"""
Testes da CLI de importação FIPE.

Objetivos desta suíte:
- documentar o ponto de entrada operacional da importação;
- validar a composição inicial das dependências;
- preparar o terreno para testes de orquestração.

Observação:
- nesta etapa, os testes são placeholders documentados.
"""

from src.delivery.cli.import_fipe import FipeImportCommand


def build_command() -> FipeImportCommand:
    """
    Cria uma instância do comando de importação FIPE.
    """
    return FipeImportCommand()


def test_should_initialize_import_command() -> None:
    """
    Deve inicializar o comando com as dependências esperadas.
    """
    command = build_command()

    assert command is not None
    assert hasattr(command, "collector")
    assert hasattr(command, "parser")
    assert hasattr(command, "loader")


def test_should_expose_contract_for_import_brands() -> None:
    """
    Deve expor contrato para importação de marcas.
    """
    command = build_command()

    assert hasattr(command, "import_brands")


def test_should_expose_contract_for_import_models() -> None:
    """
    Deve expor contrato para importação de modelos.
    """
    command = build_command()

    assert hasattr(command, "import_models")


def test_should_expose_contract_for_import_vehicles() -> None:
    """
    Deve expor contrato para importação de veículos.
    """
    command = build_command()

    assert hasattr(command, "import_vehicles")


def test_should_expose_contract_for_full_import_execution() -> None:
    """
    Deve expor contrato para execução completa da importação.
    """
    command = build_command()

    assert hasattr(command, "run_full_import")
