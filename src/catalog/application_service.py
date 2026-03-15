"""
application_service.py

Responsável por registrar aplicações de peças em motores e veículos.
"""


def insert_application(
    cursor,
    cluster_id: int,
    motor_id: int = None,
    vehicle_id: int = None,
    position: str = None,
    side: str = None,
    notes: str = None,
    source: str = None,
    confidence_score: float = 0.500
):
    """
    Cria uma aplicação para um cluster de peça.

    Regras:
    - pode existir por motor
    - pode existir por veículo
    - pode existir por ambos
    """
    if motor_id is None and vehicle_id is None:
        raise ValueError("Ao menos motor_id ou vehicle_id deve ser informado.")

    cursor.execute("""
        INSERT INTO catalog.applications (
            cluster_id,
            motor_id,
            vehicle_id,
            position,
            side,
            notes,
            source,
            confidence_score
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
    """, (
        cluster_id,
        motor_id,
        vehicle_id,
        position,
        side,
        notes,
        source,
        confidence_score
    ))

    return cursor.fetchone()[0]