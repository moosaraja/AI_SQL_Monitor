from pg_connection import get_pg_connection


def create_alert(
    snapshot_id,
    server_name,
    database_name,
    metric,
    severity,
    message
):

    connection = get_pg_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO alerts
            (
                server_name,
                database_name,
                metric,
                severity,
                message,
                status,
                snapshot_id
            )
            VALUES (%s, %s, %s, %s, %s, 'OPEN', %s)
            RETURNING id;
            """,
            (
                server_name,
                database_name,
                metric,
                severity,
                message,
                snapshot_id
            )
        )

        alert_id = cursor.fetchone()[0]

        connection.commit()

        return alert_id

    finally:
        connection.close()