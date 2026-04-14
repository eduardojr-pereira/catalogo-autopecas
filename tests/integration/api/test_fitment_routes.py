"""
test_fitment_routes.py

Testes de integração HTTP para as rotas de fitment.
"""

from src.shared.utils import normalize_text


def norm_text(value: str) -> str:
    """
    Normaliza texto para persistência de dados de teste.
    """
    return normalize_text(value).upper()


def create_brand(cursor, name="Honda", external_source="test", external_code="brand-honda"):
    cursor.execute(
        """
        INSERT INTO reference.vehicle_brands (
            name,
            normalized_name,
            external_source,
            external_code
        )
        VALUES (%s, %s, %s, %s)
        RETURNING id
        """,
        (name, norm_text(name), external_source, external_code),
    )
    return cursor.fetchone()["id"]


def create_model(
    cursor,
    brand_id,
    name="Civic",
    external_source="test",
    external_code="model-civic",
):
    cursor.execute(
        """
        INSERT INTO reference.vehicle_models (
            brand_id,
            name,
            normalized_name,
            external_source,
            external_code
        )
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id
        """,
        (brand_id, name, norm_text(name), external_source, external_code),
    )
    return cursor.fetchone()["id"]


def create_vehicle(
    cursor,
    brand_id,
    model_id,
    year=2010,
    version_name="LXS 1.8",
    market="BR",
    external_source="test",
    external_code="vehicle-civic-2010-lxs",
):
    cursor.execute(
        """
        INSERT INTO reference.vehicles (
            brand_id,
            model_id,
            brand_text,
            model_text,
            model_year,
            version_name,
            market,
            external_source,
            external_code
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
        """,
        (
            brand_id,
            model_id,
            "Honda",
            "Civic",
            year,
            version_name,
            market,
            external_source,
            external_code,
        ),
    )
    return cursor.fetchone()["id"]


def create_motor(cursor, code="R18_TEST"):
    cursor.execute(
        """
        INSERT INTO reference.motors (
            code,
            description,
            displacement
        )
        VALUES (%s, %s, %s)
        RETURNING id
        """,
        (code, "Motor Honda R18", 1.8),
    )
    return cursor.fetchone()["id"]


def create_vehicle_motor_link(cursor, vehicle_id, motor_id):
    cursor.execute(
        """
        INSERT INTO reference.vehicle_motors (
            vehicle_id,
            motor_id
        )
        VALUES (%s, %s)
        """,
        (vehicle_id, motor_id),
    )


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


def create_application_motor(cursor, cluster_id, motor_id):
    cursor.execute(
        """
        INSERT INTO catalog.applications (
            cluster_id,
            motor_id,
            confidence_score
        )
        VALUES (%s, %s, %s)
        RETURNING id
        """,
        (cluster_id, motor_id, 0.95),
    )
    return cursor.fetchone()["id"]


def test_get_fitment_by_vehicle_returns_items(api_client, db_dict_cursor):
    brand_id = create_brand(db_dict_cursor)
    model_id = create_model(db_dict_cursor, brand_id)
    vehicle_id = create_vehicle(db_dict_cursor, brand_id, model_id)

    motor_id = create_motor(db_dict_cursor)
    create_vehicle_motor_link(db_dict_cursor, vehicle_id, motor_id)

    part_type_id = create_part_type(db_dict_cursor)
    part_id = create_part(db_dict_cursor, part_type_id)
    cluster_id = create_cluster(db_dict_cursor, part_id)

    create_application_motor(db_dict_cursor, cluster_id, motor_id)

    response = api_client.get(f"/fitment/vehicle/{vehicle_id}")

    assert response.status_code == 200

    payload = response.json()
    assert payload["count"] >= 1
    assert payload["items"][0]["vehicle_id"] == vehicle_id
    assert payload["items"][0]["part_id"] == part_id
    assert payload["items"][0]["part_name"] == "Filtro de Óleo Motor R18"


def test_get_fitment_by_motor_returns_items(api_client, db_dict_cursor):
    motor_id = create_motor(db_dict_cursor)

    part_type_id = create_part_type(db_dict_cursor)
    part_id = create_part(db_dict_cursor, part_type_id)
    cluster_id = create_cluster(db_dict_cursor, part_id)

    create_application_motor(db_dict_cursor, cluster_id, motor_id)

    response = api_client.get(f"/fitment/motor/{motor_id}")

    assert response.status_code == 200

    payload = response.json()
    assert payload["count"] >= 1
    assert payload["items"][0]["motor_id"] == motor_id
    assert payload["items"][0]["part_id"] == part_id
    assert payload["items"][0]["part_name"] == "Filtro de Óleo Motor R18"


def test_get_fitment_search_returns_items(api_client, db_dict_cursor):
    brand_id = create_brand(
        db_dict_cursor,
        name="Honda",
        external_code="brand-honda-fitment",
    )
    model_id = create_model(
        db_dict_cursor,
        brand_id,
        name="Civic",
        external_code="model-civic-fitment",
    )
    vehicle_id = create_vehicle(
        db_dict_cursor,
        brand_id,
        model_id,
        year=2010,
        version_name="LXS 1.8",
        external_code="vehicle-civic-2010-fitment",
    )

    motor_id = create_motor(db_dict_cursor, code="R18_TEST_FITMENT")
    create_vehicle_motor_link(db_dict_cursor, vehicle_id, motor_id)

    part_type_id = create_part_type(db_dict_cursor, name="Filtro de Óleo")
    part_id = create_part(db_dict_cursor, part_type_id)
    cluster_id = create_cluster(db_dict_cursor, part_id)

    create_application_motor(db_dict_cursor, cluster_id, motor_id)

    response = api_client.get(
        "/fitment/search",
        params={
            "brand": "Honda",
            "model": "Civic",
            "model_year": 2010,
        },
    )

    assert response.status_code == 200

    payload = response.json()
    assert payload["count"] >= 1
    assert payload["items"][0]["vehicle_id"] == vehicle_id
    assert payload["items"][0]["part_id"] == part_id
    assert payload["items"][0]["part_name"] == "Filtro de Óleo Motor R18"


def test_get_fitment_search_returns_400_for_blank_brand(api_client):
    response = api_client.get(
        "/fitment/search",
        params={
            "brand": "   ",
            "model": "Civic",
            "model_year": 2010,
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Parâmetro 'brand' não pode ser vazio."


def test_get_fitment_search_returns_400_for_blank_model(api_client):
    response = api_client.get(
        "/fitment/search",
        params={
            "brand": "Honda",
            "model": "   ",
            "model_year": 2010,
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Parâmetro 'model' não pode ser vazio."