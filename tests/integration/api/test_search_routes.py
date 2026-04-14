"""
test_search_routes.py

Testes de integração HTTP para as rotas de busca.
"""

from src.processing.normalization.code_normalizer import normalize_code
from src.shared.utils import normalize_text


def norm_text(value: str) -> str:
    """
    Normaliza texto para persistência de dados de teste.
    """
    return normalize_text(value).upper()


def create_manufacturer(cursor, name="Bosch", manufacturer_type="aftermarket"):
    cursor.execute(
        """
        INSERT INTO reference.manufacturers (
            name,
            manufacturer_type
        )
        VALUES (%s, %s)
        RETURNING id
        """,
        (name, manufacturer_type),
    )
    return cursor.fetchone()["id"]


def create_part_type(cursor, name="Filtro de Óleo", normalized_name=None):
    if normalized_name is None:
        normalized_name = norm_text(name)

    cursor.execute(
        """
        INSERT INTO reference.part_types (
            name,
            normalized_name
        )
        VALUES (%s, %s)
        RETURNING id
        """,
        (name, normalized_name),
    )
    return cursor.fetchone()["id"]


def create_part_type_alias(cursor, part_type_id, alias="Filtro", normalized_alias=None):
    if normalized_alias is None:
        normalized_alias = norm_text(alias)

    cursor.execute(
        """
        INSERT INTO reference.part_type_aliases (
            part_type_id,
            alias,
            normalized_alias
        )
        VALUES (%s, %s, %s)
        """,
        (part_type_id, alias, normalized_alias),
    )


def create_part(
    cursor,
    part_type_id,
    name="Filtro de Óleo Motor R18",
    normalized_name=None,
    status="active",
):
    if normalized_name is None:
        normalized_name = norm_text(name)

    cursor.execute(
        """
        INSERT INTO catalog.parts (
            name,
            normalized_name,
            part_type_id,
            status
        )
        VALUES (%s, %s, %s, %s)
        RETURNING id
        """,
        (name, normalized_name, part_type_id, status),
    )
    return cursor.fetchone()["id"]


def create_cluster(cursor, part_id, name="Cluster Filtro", cluster_type="consolidated"):
    cursor.execute(
        """
        INSERT INTO catalog.clusters (
            part_id,
            name,
            cluster_type
        )
        VALUES (%s, %s, %s)
        RETURNING id
        """,
        (part_id, name, cluster_type),
    )
    return cursor.fetchone()["id"]


def create_code(cursor, manufacturer_id, code, normalized_code=None):
    if normalized_code is None:
        normalized_code = normalize_code(code)

    cursor.execute(
        """
        INSERT INTO discovery.codes (
            manufacturer_id,
            code,
            normalized_code
        )
        VALUES (%s, %s, %s)
        RETURNING id
        """,
        (manufacturer_id, code, normalized_code),
    )
    return cursor.fetchone()["id"]


def link_code_to_cluster(cursor, cluster_id, code_id):
    cursor.execute(
        """
        INSERT INTO catalog.cluster_codes (
            cluster_id,
            code_id
        )
        VALUES (%s, %s)
        """,
        (cluster_id, code_id),
    )


def test_get_search_by_code_returns_items(api_client, db_dict_cursor):
    manufacturer_id = create_manufacturer(db_dict_cursor, "Bosch Test API")
    part_type_id = create_part_type(db_dict_cursor)
    part_id = create_part(db_dict_cursor, part_type_id)
    cluster_id = create_cluster(db_dict_cursor, part_id)
    code_id = create_code(db_dict_cursor, manufacturer_id, "OC-1196")
    link_code_to_cluster(db_dict_cursor, cluster_id, code_id)

    response = api_client.get("/search/code/oc-1196")

    assert response.status_code == 200

    payload = response.json()
    assert payload["count"] == 1
    assert len(payload["items"]) == 1
    assert payload["items"][0]["code_id"] == code_id
    assert payload["items"][0]["part_id"] == part_id
    assert payload["items"][0]["cluster_id"] == cluster_id
    assert payload["items"][0]["manufacturer_name"] == "Bosch Test API"


def test_get_search_by_part_name_returns_items(api_client, db_dict_cursor):
    part_type_id = create_part_type(db_dict_cursor)
    part_id = create_part(
        db_dict_cursor,
        part_type_id,
        name="Filtro de Ar do Motor",
    )

    response = api_client.get("/search/part", params={"name": "filtro de ar"})

    assert response.status_code == 200

    payload = response.json()
    assert payload["count"] == 1
    assert payload["items"][0]["part_id"] == part_id
    assert payload["items"][0]["part_name"] == "Filtro de Ar do Motor"


def test_get_search_by_part_type_returns_items(api_client, db_dict_cursor):
    part_type_id = create_part_type(db_dict_cursor, name="Vela de Ignição")
    part_id = create_part(
        db_dict_cursor,
        part_type_id,
        name="Vela NGK Civic",
    )

    response = api_client.get("/search/part-type", params={"name": "vela de ignição"})

    assert response.status_code == 200

    payload = response.json()
    assert payload["count"] == 1
    assert payload["items"][0]["part_id"] == part_id
    assert payload["items"][0]["part_type_name"] == "Vela de Ignição"


def test_get_search_by_part_type_alias_returns_items(api_client, db_dict_cursor):
    part_type_id = create_part_type(db_dict_cursor, name="Pastilha de Freio")
    create_part_type_alias(db_dict_cursor, part_type_id, alias="Pastilha")
    part_id = create_part(
        db_dict_cursor,
        part_type_id,
        name="Pastilha Dianteira Civic",
    )

    response = api_client.get("/search/part-type-alias", params={"alias": "pastilha"})

    assert response.status_code == 200

    payload = response.json()
    assert payload["count"] == 1
    assert payload["items"][0]["part_id"] == part_id
    assert payload["items"][0]["alias"] == "Pastilha"


def test_get_search_equivalents_by_code_returns_items(api_client, db_dict_cursor):
    manufacturer_id_1 = create_manufacturer(db_dict_cursor, "Bosch API Eq")
    manufacturer_id_2 = create_manufacturer(db_dict_cursor, "Mahle API Eq")

    part_type_id = create_part_type(db_dict_cursor)
    part_id = create_part(db_dict_cursor, part_type_id)
    cluster_id = create_cluster(db_dict_cursor, part_id)

    source_code_id = create_code(db_dict_cursor, manufacturer_id_1, "0986-AF0051")
    equivalent_code_id = create_code(db_dict_cursor, manufacturer_id_2, "OC-1196")

    link_code_to_cluster(db_dict_cursor, cluster_id, source_code_id)
    link_code_to_cluster(db_dict_cursor, cluster_id, equivalent_code_id)

    response = api_client.get("/search/equivalents/0986-AF0051")

    assert response.status_code == 200

    payload = response.json()
    assert payload["count"] == 1
    assert payload["items"][0]["source_code_id"] == source_code_id
    assert payload["items"][0]["equivalent_code_id"] == equivalent_code_id
    assert payload["items"][0]["manufacturer_name"] == "Mahle API Eq"


def test_get_search_part_returns_400_for_blank_name(api_client):
    response = api_client.get("/search/part", params={"name": "   "})

    assert response.status_code == 400
    assert response.json()["detail"] == "Parâmetro 'name' não pode ser vazio."