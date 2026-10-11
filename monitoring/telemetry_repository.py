from pg_connection import get_pg_connection
import json


def save_snapshot(snapshot):

    connection = get_pg_connection()

    try:
        cursor = connection.cursor()

        server_name = snapshot.get("server_health", {}).get("server")
        database_name = snapshot.get("server_health", {}).get("database")

        cursor.execute(
            """
            INSERT INTO monitoring_snapshots
            (
                server_name,
                database_name,
                snapshot
            )
            VALUES (%s, %s, %s::jsonb)
            RETURNING id
            """,
            (
                server_name,
                database_name,
                json.dumps(snapshot, default=str)
            )
        )

        snapshot_id = cursor.fetchone()[0]

        connection.commit()

        return snapshot_id

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def get_last_snapshot_time(server_name):
    """Return most recent persisted snapshot time (timezone-aware)."""
    connection = get_pg_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT MAX(collected_at)
                FROM monitoring_snapshots
                WHERE server_name = %s
                """,
                (server_name,)
            )
            return cursor.fetchone()[0]
    finally:
        connection.close()
