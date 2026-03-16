"""
CLI de importação FIPE.

Responsabilidades:
- servir como ponto de entrada operacional para a importação;
- orquestrar coletor, parser e loader;
- permitir execução controlada por etapa.

Este módulo NÃO deve:
- concentrar regras de transformação;
- implementar persistência diretamente;
- conter detalhes de HTTP da API FIPE.

Observação:
- neste estágio, a CLI é um placeholder documentado;
- a implementação real será adicionada após o fechamento do contrato da fase.
"""

from __future__ import annotations

from src.ingestion.collectors.fipe_api_collector import (
    FipeApiCollector,
    FipeApiCollectorConfig,
)
from src.ingestion.loaders.vehicle_reference_loader import VehicleReferenceLoader
from src.ingestion.parsers.fipe_parser import FipeParser


class FipeImportCommand:
    """
    Comando de importação FIPE.

    Este comando representa a orquestração de alto nível da fase 2:
    - importar marcas;
    - importar modelos;
    - importar veículos;
    - permitir execução total ou parcial.
    """

    def __init__(self) -> None:
        """
        Inicializa dependências do comando.

        Em versões futuras, esta composição poderá migrar para um container
        de dependências ou factory do projeto.
        """
        self.collector = FipeApiCollector(
            config=FipeApiCollectorConfig(
                base_url="https://parallelum.com.br/fipe/api/v1"
            )
        )
        self.parser = FipeParser()
        self.loader = VehicleReferenceLoader()

    def import_brands(self) -> None:
        """
        Executa a importação de marcas.

        Fluxo esperado:
        1. coletar payload bruto;
        2. parsear cada registro;
        3. persistir com upsert.

        Raises:
            NotImplementedError: enquanto a orquestração real não for adicionada.
        """
        raise NotImplementedError("Importação de marcas ainda não foi implementada.")

    def import_models(self) -> None:
        """
        Executa a importação de modelos por marca.

        Fluxo esperado:
        1. iterar sobre marcas disponíveis;
        2. coletar modelos da marca;
        3. parsear cada registro;
        4. persistir com upsert.

        Raises:
            NotImplementedError: enquanto a orquestração real não for adicionada.
        """
        raise NotImplementedError("Importação de modelos ainda não foi implementada.")

    def import_vehicles(self) -> None:
        """
        Executa a importação de veículos/anos/variações por modelo.

        Fluxo esperado:
        1. iterar sobre marcas e modelos;
        2. coletar anos/combinações FIPE;
        3. parsear cada registro;
        4. persistir com upsert.

        Raises:
            NotImplementedError: enquanto a orquestração real não for adicionada.
        """
        raise NotImplementedError("Importação de veículos ainda não foi implementada.")

    def run_full_import(self) -> None:
        """
        Executa a importação completa da FIPE em ordem segura.

        Ordem esperada:
        1. marcas;
        2. modelos;
        3. veículos.

        Raises:
            NotImplementedError: enquanto a orquestração real não for adicionada.
        """
        raise NotImplementedError("Execução completa do importador ainda não foi implementada.")


def main() -> None:
    """
    Ponto de entrada da CLI FIPE.

    A implementação futura poderá receber argumentos para executar:
    - somente marcas;
    - somente modelos;
    - somente veículos;
    - importação completa.
    """
    command = FipeImportCommand()
    command.run_full_import()


if __name__ == "__main__":
    main()