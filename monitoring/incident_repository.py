from pg_connection import get_pg_connection


def find_open_incident(
    server_name,
    database_name,
    metric
):

    connection = get_pg_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                id,
                severity,
                status,
                occurrence_count
            FROM incidents
            WHERE server_name = %s
              AND database_name = %s
              AND metric = %s
              AND status = 'OPEN'
            ORDER BY created_at DESC
            LIMIT 1;
            """,
            (
                server_name,
                database_name,
                metric
            )
        )

        return cursor.fetchone()

    finally:
        connection.close()

def get_incident(incident_id):

    connection = get_pg_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                id,
                server_name,
                database_name,
                metric,
                severity,
                status,
                message,
                first_snapshot_id,
                last_snapshot_id,
                occurrence_count,
                created_at,
                last_seen_at,
                resolved_at
            FROM incidents
            WHERE id = %s;
            """,
            (
                incident_id,
            )
        )

        row = cursor.fetchone()

        if not row:
            return None

        columns = [
            "id",
            "server_name",
            "database_name",
            "metric",
            "severity",
            "status",
            "message",
            "first_snapshot_id",
            "last_snapshot_id",
            "occurrence_count",
            "created_at",
            "last_seen_at",
            "resolved_at"
        ]

        return dict(
            zip(
                columns,
                row
            )
        )

    finally:

        connection.close()


def create_incident(
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
            INSERT INTO incidents
            (
                server_name,
                database_name,
                metric,
                severity,
                status,
                message,
                first_snapshot_id,
                last_snapshot_id,
                occurrence_count
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                'OPEN',
                %s,
                %s,
                %s,
                1
            )
            RETURNING id;
            """,
            (
                server_name,
                database_name,
                metric,
                severity,
                message,
                snapshot_id,
                snapshot_id
            )
        )

        incident_id = cursor.fetchone()[0]

        connection.commit()

        return incident_id

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def update_incident(
    incident_id,
    snapshot_id,
    severity,
    message
):

    connection = get_pg_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            UPDATE incidents
            SET
                last_snapshot_id = %s,
                severity = %s,
                message = %s,
                occurrence_count = occurrence_count + 1,
                last_seen_at = NOW()
            WHERE id = %s
              AND status = 'OPEN';
            """,
            (
                snapshot_id,
                severity,
                message,
                incident_id
            )
        )

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def resolve_incident(incident_id, snapshot_id):

    connection = get_pg_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            UPDATE incidents
            SET
                status = 'RESOLVED',
                resolved_at = NOW(),
                last_snapshot_id = %s
            WHERE id = %s
              AND status = 'OPEN';
            """,
            (
                snapshot_id,
                incident_id
            )
        )

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()