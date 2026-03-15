"""
equivalence_loader.py

Lê equivalências do banco, gera clusters de descoberta
e grava o resultado nas tabelas do catálogo.
"""

import logging

from processing.equivalence.equivalence_engine import generate_clusters
from src.shared.config import get_app_config
from src.shared.db import get_connection


app_config = get_app_config()

logging.basicConfig(
    level=getattr(logging, app_config.log_level.upper(), logging.INFO),
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)


def load_equivalences(cursor, min_confidence=0.50):
    """
    Busca equivalências aptas a participar dos clusters de descoberta.

    Regras:
    - ignora relações rejeitadas
    - exige confiança mínima
    """
    cursor.execute("""
        SELECT code_id_1, code_id_2
        FROM discovery.code_equivalences
        WHERE validation_status <> 'rejected'
          AND confidence_score >= %s
    """, (min_confidence,))

    rows = cursor.fetchall()
    logger.info("Equivalências carregadas para clusterização: %s", len(rows))

    return rows


def load_existing_discovery_cluster_map(cursor):
    """
    Carrega apenas clusters do tipo 'discovery'.
    """
    cursor.execute("""
        SELECT cc.cluster_id, cc.code_id
        FROM catalog.cluster_codes cc
        JOIN catalog.clusters c
          ON c.id = cc.cluster_id
        WHERE c.cluster_type = 'discovery'
        ORDER BY cc.cluster_id
    """)

    rows = cursor.fetchall()

    grouped = {}
    for cluster_id, code_id in rows:
        grouped.setdefault(cluster_id, set()).add(code_id)

    cluster_map = {
        frozenset(code_ids): cluster_id
        for cluster_id, code_ids in grouped.items()
    }

    logger.info("Clusters discovery existentes carregados: %s", len(cluster_map))

    return cluster_map


def ensure_cluster_code_link(cursor, cluster_id, code_id):
    """
    Garante que o vínculo cluster ↔ código exista uma única vez.
    """
    cursor.execute("""
        SELECT 1
        FROM catalog.cluster_codes
        WHERE cluster_id = %s
          AND code_id = %s
        LIMIT 1
    """, (cluster_id, code_id))

    if cursor.fetchone():
        return False

    cursor.execute("""
        INSERT INTO catalog.cluster_codes (cluster_id, code_id)
        VALUES (%s, %s)
    """, (cluster_id, code_id))

    return True


def save_discovery_clusters(cursor, clusters):
    """
    Salva clusters do tipo discovery sem recriar tudo do zero.
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
            logger.info("Cluster discovery reutilizado: id=%s tamanho=%s", cluster_id, len(cluster))
        else:
            cursor.execute("""
                INSERT INTO catalog.clusters (name, cluster_type)
                VALUES (%s, %s)
                RETURNING id
            """, (None, 'discovery'))

            cluster_id = cursor.fetchone()[0]
            existing_cluster_map[cluster_key] = cluster_id
            created_clusters += 1
            logger.info("Novo cluster discovery criado: id=%s tamanho=%s", cluster_id, len(cluster))

        for code_id in cluster:
            inserted = ensure_cluster_code_link(cursor, cluster_id, code_id)
            if inserted:
                inserted_links += 1

    logger.info(
        "Resumo | novos_clusters=%s reutilizados=%s novos_links=%s",
        created_clusters,
        reused_clusters,
        inserted_links
    )


def run(min_confidence=0.50):
    """
    Executa o pipeline de clusterização de descoberta.
    """
    conn = get_connection()
    cur = conn.cursor()

    try:
        logger.info("Iniciando geração de clusters de descoberta...")

        equivalences = load_equivalences(cur, min_confidence=min_confidence)

        if not equivalences:
            logger.warning("Nenhuma equivalência elegível encontrada.")
            return

        clusters = generate_clusters(equivalences)

        logger.info("Clusters gerados em memória: %s", len(clusters))

        save_discovery_clusters(cur, clusters)

        conn.commit()
        logger.info("Processo concluído com sucesso.")

    except Exception as exc:
        conn.rollback()
        logger.exception("Erro ao gerar clusters: %s", exc)
        raise

    finally:
        cur.close()
        conn.close()
        logger.info("Conexão encerrada.")


if __name__ == "__main__":
    run()