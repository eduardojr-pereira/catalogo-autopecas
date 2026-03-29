"""
equivalence_loader.py

Lê equivalências validadas do banco, gera clusters de descoberta
e grava o resultado nas tabelas do catálogo.

Responsabilidades:
- carregar equivalências elegíveis para clusterização;
- carregar clusters discovery já existentes;
- criar novos clusters discovery quando necessário;
- garantir vínculos cluster ↔ código sem duplicação;
- executar o fluxo operacional de clusterização.

Este módulo NÃO deve:
- configurar logging global da aplicação;
- depender de configuração global de app;
- conter regras de normalização de código;
- substituir o motor puro de equivalência.
"""

import logging
from typing import Any

from src.processing.equivalence.equivalence_engine import generate_clusters
from src.shared.db import get_cursor


logger = logging.getLogger(__name__)


def load_equivalences(cursor, min_confidence: float = 0.50) -> list[tuple[int, int]]:
    """
    Busca equivalências aptas a participar dos clusters de descoberta.

    Regras:
    - ignora relações rejeitadas;
    - exige confiança mínima.

    Retorna:
    - lista de pares (code_id_1, code_id_2)
    """
    cursor.execute("""
        SELECT
            code_id_1,
            code_id_2
        FROM discovery.code_equivalences
        WHERE validation_status <> 'rejected'
          AND confidence_score >= %s
    """, (min_confidence,))

    rows = cursor.fetchall()

    equivalences = [
        (int(row["code_id_1"]), int(row["code_id_2"]))
        for row in rows
    ]

    logger.info("Equivalências carregadas para clusterização: %s", len(equivalences))

    return equivalences


def load_existing_discovery_cluster_map(cursor) -> dict[frozenset[int], int]:
    """
    Carrega apenas clusters do tipo discovery.

    Retorna:
    - mapa no formato:
      {
          frozenset({code_id_1, code_id_2, ...}): cluster_id
      }
    """
    cursor.execute("""
        SELECT
            cc.cluster_id,
            cc.code_id
        FROM catalog.cluster_codes cc
        JOIN catalog.clusters c
          ON c.id = cc.cluster_id
        WHERE c.cluster_type = 'discovery'
        ORDER BY cc.cluster_id, cc.code_id
    """)

    rows = cursor.fetchall()

    grouped: dict[int, set[int]] = {}

    for row in rows:
        cluster_id = int(row["cluster_id"])
        code_id = int(row["code_id"])
        grouped.setdefault(cluster_id, set()).add(code_id)

    cluster_map = {
        frozenset(code_ids): cluster_id
        for cluster_id, code_ids in grouped.items()
    }

    logger.info("Clusters discovery existentes carregados: %s", len(cluster_map))

    return cluster_map


def ensure_cluster_code_link(cursor, cluster_id: int, code_id: int) -> bool:
    """
    Garante que o vínculo cluster ↔ código exista uma única vez.

    Retorna:
    - True se o vínculo foi criado;
    - False se já existia.
    """
    cursor.execute("""
        SELECT 1
        FROM catalog.cluster_codes
        WHERE cluster_id = %s
          AND code_id = %s
        LIMIT 1
    """, (cluster_id, code_id))

    if cursor.fetchone() is not None:
        return False

    cursor.execute("""
        INSERT INTO catalog.cluster_codes (
            cluster_id,
            code_id
        )
        VALUES (%s, %s)
    """, (cluster_id, code_id))

    return True


def create_discovery_cluster(cursor) -> int:
    """
    Cria um novo cluster do tipo discovery e retorna seu id.
    """
    cursor.execute("""
        INSERT INTO catalog.clusters (
            name,
            cluster_type
        )
        VALUES (%s, %s)
        RETURNING id
    """, (None, "discovery"))

    row = cursor.fetchone()
    return int(row["id"])


def save_discovery_clusters(cursor, clusters: list[set[int]]) -> dict[str, int]:
    """
    Salva clusters do tipo discovery sem recriar tudo do zero.

    Regras:
    - reutiliza cluster existente quando o conjunto de códigos é idêntico;
    - cria novo cluster quando o conjunto ainda não existe;
    - garante vínculo único entre cluster e código.

    Retorna:
    - resumo operacional da persistência.
    """
    existing_cluster_map = load_existing_discovery_cluster_map(cursor)

    created_clusters = 0
    reused_clusters = 0
    inserted_links = 0

    for cluster in clusters:
        cluster_key = frozenset(cluster)

        if cluster_key in existing_cluster_map:
            cluster_id = existing_cluster_map[cluster_key]
            reused_clusters += 1
            logger.info(
                "Cluster discovery reutilizado: id=%s tamanho=%s",
                cluster_id,
                len(cluster),
            )
        else:
            cluster_id = create_discovery_cluster(cursor)
            existing_cluster_map[cluster_key] = cluster_id
            created_clusters += 1
            logger.info(
                "Novo cluster discovery criado: id=%s tamanho=%s",
                cluster_id,
                len(cluster),
            )

        for code_id in sorted(cluster):
            inserted = ensure_cluster_code_link(
                cursor=cursor,
                cluster_id=cluster_id,
                code_id=code_id,
            )
            if inserted:
                inserted_links += 1

    logger.info(
        "Resumo | novos_clusters=%s reutilizados=%s novos_links=%s",
        created_clusters,
        reused_clusters,
        inserted_links,
    )

    return {
        "created_clusters": created_clusters,
        "reused_clusters": reused_clusters,
        "inserted_links": inserted_links,
    }


def _run_with_cursor(cursor, min_confidence: float = 0.50) -> dict[str, Any]:
    """
    Executa o pipeline usando um cursor já fornecido.

    Esse modo é útil para testes e cenários em que o chamador
    controla explicitamente a transação.
    """
    equivalences = load_equivalences(
        cursor=cursor,
        min_confidence=min_confidence,
    )

    if not equivalences:
        logger.warning("Nenhuma equivalência elegível encontrada.")
        return {
            "equivalence_count": 0,
            "cluster_count": 0,
            "created_clusters": 0,
            "reused_clusters": 0,
            "inserted_links": 0,
        }

    clusters = generate_clusters(equivalences)

    logger.info("Clusters gerados em memória: %s", len(clusters))

    persistence_summary = save_discovery_clusters(
        cursor=cursor,
        clusters=clusters,
    )

    return {
        "equivalence_count": len(equivalences),
        "cluster_count": len(clusters),
        **persistence_summary,
    }


def run(min_confidence: float = 0.50, cursor=None) -> dict[str, Any]:
    """
    Executa o pipeline de clusterização de descoberta.

    Parâmetros:
    - min_confidence: confiança mínima exigida.
    - cursor: cursor opcional injetado externamente.

    Retorna:
    - resumo operacional da execução.
    """
    logger.info("Iniciando geração de clusters de descoberta...")

    try:
        if cursor is not None:
            summary = _run_with_cursor(
                cursor=cursor,
                min_confidence=min_confidence,
            )
        else:
            with get_cursor() as managed_cursor:
                summary = _run_with_cursor(
                    cursor=managed_cursor,
                    min_confidence=min_confidence,
                )

        logger.info("Processo concluído com sucesso.")
        return summary

    except Exception as exc:
        logger.exception("Erro ao gerar clusters: %s", exc)
        raise

    finally:
        logger.info("Conexão encerrada.")


if __name__ == "__main__":
    run()