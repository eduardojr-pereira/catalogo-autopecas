"""
fitment_service.py

Serviços de consulta de fitment do catálogo automotivo.

Responsável por:
- buscar peças por veículo
- buscar peças por motor
- buscar fitment por filtros comerciais

Observação importante:
A modelagem de veículos foi refatorada para usar:

vehicle_brands -> vehicle_models -> vehicles

Por isso este módulo passa a consultar a estrutura oficial de marca e modelo,
usando fallback para brand_text e model_text apenas como apoio de transição.

Enquanto a camada formal de publicação ainda não existe, o filtro
`only_published=True` continua usando `catalog.parts.status = 'active'`
como aproximação de catálogo visível.
"""

from typing import Any


def _rows_to_dicts(cursor) -> list[dict[str, Any]]:
    """
    Converte o resultado do cursor em lista de dicionários.

    Isso facilita o consumo pelos testes, serviços e futura API.
    """
    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    return [dict(zip(columns, row)) for row in rows]


def find_parts_by_vehicle_id(
    cursor,
    vehicle_id: int,
    part_type_id: int | None = None,
    only_published: bool = False
) -> list[dict[str, Any]]:
    """
    Busca peças aplicáveis a um veículo.

    Estratégia:
    1. traz aplicações derivadas dos motores ligados ao veículo
    2. traz aplicações cadastradas diretamente no veículo
    3. une os dois conjuntos com UNION

    A consulta já usa a nova estrutura:
    vehicles -> vehicle_models -> vehicle_brands
    """
    query = """
        SELECT DISTINCT *
        FROM (

            -- aplicações encontradas via motor do veículo
            SELECT
                v.id AS vehicle_id,
                vb.id AS brand_id,
                vb.name AS brand_name,
                vm.id AS model_id,
                vm.name AS model_name,
                v.brand_text,
                v.model_text,
                v.model_year,
                v.version,
                v.body_type,
                v.fuel_type,
                p.id AS part_id,
                p.name AS part_name,
                p.normalized_name,
                p.status AS part_status,
                pt.id AS part_type_id,
                pt.name AS part_type_name,
                c.id AS cluster_id,
                c.cluster_type,
                a.id AS application_id,
                a.position,
                a.position_type_id,
                a.side,
                a.side_type_id,
                a.notes,
                a.source,
                a.confidence_score
            FROM reference.vehicles v
            LEFT JOIN reference.vehicle_models vm
              ON vm.id = v.model_id
            LEFT JOIN reference.vehicle_brands vb
              ON vb.id = vm.brand_id
            JOIN reference.vehicle_motors veh_mot
              ON veh_mot.vehicle_id = v.id
            JOIN catalog.applications a
              ON a.motor_id = veh_mot.motor_id
            JOIN catalog.clusters c
              ON c.id = a.cluster_id
            JOIN catalog.parts p
              ON p.id = c.part_id
            JOIN reference.part_types pt
              ON pt.id = p.part_type_id
            WHERE v.id = %s

            UNION

            -- aplicações cadastradas diretamente no veículo
            SELECT
                v.id AS vehicle_id,
                vb.id AS brand_id,
                vb.name AS brand_name,
                vm.id AS model_id,
                vm.name AS model_name,
                v.brand_text,
                v.model_text,
                v.model_year,
                v.version,
                v.body_type,
                v.fuel_type,
                p.id AS part_id,
                p.name AS part_name,
                p.normalized_name,
                p.status AS part_status,
                pt.id AS part_type_id,
                pt.name AS part_type_name,
                c.id AS cluster_id,
                c.cluster_type,
                a.id AS application_id,
                a.position,
                a.position_type_id,
                a.side,
                a.side_type_id,
                a.notes,
                a.source,
                a.confidence_score
            FROM reference.vehicles v
            LEFT JOIN reference.vehicle_models vm
              ON vm.id = v.model_id
            LEFT JOIN reference.vehicle_brands vb
              ON vb.id = vm.brand_id
            JOIN catalog.applications a
              ON a.vehicle_id = v.id
            JOIN catalog.clusters c
              ON c.id = a.cluster_id
            JOIN catalog.parts p
              ON p.id = c.part_id
            JOIN reference.part_types pt
              ON pt.id = p.part_type_id
            WHERE v.id = %s

        ) fitment_result
        WHERE 1 = 1
    """

    # o vehicle_id aparece duas vezes por causa do UNION
    params: list[Any] = [vehicle_id, vehicle_id]

    # filtro opcional por tipo de peça
    if part_type_id is not None:
        query += " AND part_type_id = %s"
        params.append(part_type_id)

    # por enquanto consideramos "active" como equivalente a publicado
    if only_published:
        query += " AND part_status = 'active'"

    query += """
        ORDER BY
            part_type_name,
            part_name,
            confidence_score DESC,
            cluster_id
    """

    cursor.execute(query, tuple(params))
    return _rows_to_dicts(cursor)


def find_parts_by_motor_id(
    cursor,
    motor_id: int,
    part_type_id: int | None = None,
    only_published: bool = False
) -> list[dict[str, Any]]:
    """
    Busca peças aplicáveis diretamente a um motor.

    Embora a consulta seja centrada no motor, ela já retorna contexto
    suficiente do catálogo para uso em API e testes.
    """
    query = """
        SELECT DISTINCT
            m.id AS motor_id,
            m.code AS motor_code,
            m.description AS motor_description,
            m.displacement,
            m.fuel_type,
            p.id AS part_id,
            p.name AS part_name,
            p.normalized_name,
            p.status AS part_status,
            pt.id AS part_type_id,
            pt.name AS part_type_name,
            c.id AS cluster_id,
            c.cluster_type,
            a.id AS application_id,
            a.position,
            a.position_type_id,
            a.side,
            a.side_type_id,
            a.notes,
            a.source,
            a.confidence_score
        FROM reference.motors m
        JOIN catalog.applications a
          ON a.motor_id = m.id
        JOIN catalog.clusters c
          ON c.id = a.cluster_id
        JOIN catalog.parts p
          ON p.id = c.part_id
        JOIN reference.part_types pt
          ON pt.id = p.part_type_id
        WHERE m.id = %s
    """

    params: list[Any] = [motor_id]

    # filtro opcional por tipo de peça
    if part_type_id is not None:
        query += " AND pt.id = %s"
        params.append(part_type_id)

    # por enquanto consideramos "active" como equivalente a publicado
    if only_published:
        query += " AND p.status = 'active'"

    query += """
        ORDER BY
            pt.name,
            p.name,
            a.confidence_score DESC,
            c.id
    """

    cursor.execute(query, tuple(params))
    return _rows_to_dicts(cursor)


def find_fitment_by_vehicle_filters(
    cursor,
    brand: str,
    model: str,
    model_year: int,
    part_type_name: str | None = None,
    version: str | None = None,
    only_published: bool = False
) -> list[dict[str, Any]]:
    """
    Busca fitment usando filtros comerciais de veículo.

    Exemplo de uso:
    - Honda Civic 2010
    - Honda Civic 2010 filtro de óleo

    Estratégia:
    - usa preferencialmente a estrutura oficial de marca e modelo
    - mantém fallback para brand_text e model_text durante a transição
    """
    query = """
        SELECT DISTINCT *
        FROM (

            -- aplicações encontradas via motor do veículo
            SELECT
                v.id AS vehicle_id,
                vb.id AS brand_id,
                vb.name AS brand_name,
                vm.id AS model_id,
                vm.name AS model_name,
                v.brand_text,
                v.model_text,
                v.model_year,
                v.version,
                v.body_type,
                v.fuel_type,
                p.id AS part_id,
                p.name AS part_name,
                p.status AS part_status,
                pt.id AS part_type_id,
                pt.name AS part_type_name,
                c.id AS cluster_id,
                a.id AS application_id,
                a.position,
                a.position_type_id,
                a.side,
                a.side_type_id,
                a.notes,
                a.source,
                a.confidence_score
            FROM reference.vehicles v
            LEFT JOIN reference.vehicle_models vm
              ON vm.id = v.model_id
            LEFT JOIN reference.vehicle_brands vb
              ON vb.id = vm.brand_id
            JOIN reference.vehicle_motors veh_mot
              ON veh_mot.vehicle_id = v.id
            JOIN catalog.applications a
              ON a.motor_id = veh_mot.motor_id
            JOIN catalog.clusters c
              ON c.id = a.cluster_id
            JOIN catalog.parts p
              ON p.id = c.part_id
            JOIN reference.part_types pt
              ON pt.id = p.part_type_id
            WHERE
                (
                    (vb.name IS NOT NULL AND UPPER(vb.name) = UPPER(%s))
                    OR
                    (vb.name IS NULL AND UPPER(COALESCE(v.brand_text, '')) = UPPER(%s))
                )
                AND
                (
                    (vm.name IS NOT NULL AND UPPER(vm.name) = UPPER(%s))
                    OR
                    (vm.name IS NULL AND UPPER(COALESCE(v.model_text, '')) = UPPER(%s))
                )
                AND v.model_year = %s

            UNION

            -- aplicações cadastradas diretamente no veículo
            SELECT
                v.id AS vehicle_id,
                vb.id AS brand_id,
                vb.name AS brand_name,
                vm.id AS model_id,
                vm.name AS model_name,
                v.brand_text,
                v.model_text,
                v.model_year,
                v.version,
                v.body_type,
                v.fuel_type,
                p.id AS part_id,
                p.name AS part_name,
                p.status AS part_status,
                pt.id AS part_type_id,
                pt.name AS part_type_name,
                c.id AS cluster_id,
                a.id AS application_id,
                a.position,
                a.position_type_id,
                a.side,
                a.side_type_id,
                a.notes,
                a.source,
                a.confidence_score
            FROM reference.vehicles v
            LEFT JOIN reference.vehicle_models vm
              ON vm.id = v.model_id
            LEFT JOIN reference.vehicle_brands vb
              ON vb.id = vm.brand_id
            JOIN catalog.applications a
              ON a.vehicle_id = v.id
            JOIN catalog.clusters c
              ON c.id = a.cluster_id
            JOIN catalog.parts p
              ON p.id = c.part_id
            JOIN reference.part_types pt
              ON pt.id = p.part_type_id
            WHERE
                (
                    (vb.name IS NOT NULL AND UPPER(vb.name) = UPPER(%s))
                    OR
                    (vb.name IS NULL AND UPPER(COALESCE(v.brand_text, '')) = UPPER(%s))
                )
                AND
                (
                    (vm.name IS NOT NULL AND UPPER(vm.name) = UPPER(%s))
                    OR
                    (vm.name IS NULL AND UPPER(COALESCE(v.model_text, '')) = UPPER(%s))
                )
                AND v.model_year = %s

        ) fitment_result
        WHERE 1 = 1
    """

    # os filtros base aparecem duas vezes por causa do UNION
    # e marca/modelo são passados em duplicidade por causa do fallback
    params: list[Any] = [
        brand, brand, model, model, model_year,
        brand, brand, model, model, model_year,
    ]

    # filtra versão somente quando informada
    if version is not None:
        query += " AND UPPER(COALESCE(version, '')) = UPPER(%s)"
        params.append(version)

    # filtra tipo de peça somente quando informado
    if part_type_name is not None:
        query += " AND UPPER(part_type_name) = UPPER(%s)"
        params.append(part_type_name)

    # por enquanto consideramos "active" como equivalente a publicado
    if only_published:
        query += " AND part_status = 'active'"

    query += """
        ORDER BY
            part_type_name,
            part_name,
            confidence_score DESC
    """

    cursor.execute(query, tuple(params))
    return _rows_to_dicts(cursor)