from pg_connection import get_pg_connection
from psycopg2.extras import RealDictCursor


def get_recent_incidents(limit=100):
    connection = get_pg_connection()

    try:
        with connection.cursor(
            cursor_factory=RealDictCursor
        ) as cursor:
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
                    occurrence_count,
                    created_at,
                    last_seen_at,
                    resolved_at
                FROM incidents
                ORDER BY created_at DESC, id DESC
                LIMIT %s;
                """,
                (limit,)
            )

            return [dict(row) for row in cursor.fetchall()]

    finally:
        connection.close()


def get_incident_summary():
    connection = get_pg_connection()

    try:
        with connection.cursor(
            cursor_factory=RealDictCursor
        ) as cursor:
            cursor.execute(
                """
                SELECT
                    COUNT(*) AS total,
                    COUNT(*) FILTER (
                        WHERE status = 'OPEN'
                    ) AS open_count,
                    COUNT(*) FILTER (
                        WHERE status = 'RESOLVED'
                    ) AS resolved_count,
                    COUNT(*) FILTER (
                        WHERE severity = 'CRITICAL'
                          AND status = 'OPEN'
                    ) AS critical_open
                FROM incidents;
                """
            )

            return dict(cursor.fetchone())

    finally:
        connection.close()


def get_latest_server_health():
    connection = get_pg_connection()

    try:
        with connection.cursor(
            cursor_factory=RealDictCursor
        ) as cursor:
            cursor.execute(
                """
                SELECT
                    id,
                    server_name,
                    database_name,
                    snapshot
                FROM monitoring_snapshots
                WHERE snapshot ? 'cpu'
                  AND snapshot ? 'memory'
                  AND snapshot ? 'sessions'
                ORDER BY id DESC
                LIMIT 1;
                """
            )

            row = cursor.fetchone()
            return dict(row) if row else None

    finally:
        connection.close()


def get_health_history(limit=60):
    connection = get_pg_connection()

    try:
        with connection.cursor(
            cursor_factory=RealDictCursor
        ) as cursor:

            cursor.execute(
                """
                SELECT
                    id,
                    collected_at,
                    snapshot->'cpu' AS cpu,
                    snapshot->'memory' AS memory
                FROM monitoring_snapshots
                WHERE snapshot ? 'cpu'
                  AND snapshot ? 'memory'
                ORDER BY id DESC
                LIMIT %s;
                """,
                (limit,)
            )

            rows = cursor.fetchall()

            return [dict(row) for row in reversed(rows)]

    finally:
        connection.close()

def get_recent_cpu_values(server_name, limit=3):
    connection = get_pg_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT (snapshot->'cpu'->>'value')::float
                FROM monitoring_snapshots
                WHERE server_name = %s
                AND snapshot->'cpu'->>'value' IS NOT NULL
                ORDER BY id DESC
                LIMIT %s;
                """,
                (server_name, limit)
            )

            rows = cursor.fetchall()

            return [
                row[0]
                for row in reversed(rows)
            ]

    finally:
        connection.close()

