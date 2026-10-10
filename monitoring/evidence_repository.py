import psycopg2
from psycopg2.extras import Json
from pg_connection import get_pg_connection


def save_evidence(
    incident_id,
    snapshot_id,
    evidence_type,
    evidence,
    severity=None
):
    connection = get_pg_connection()

    try:
        cursor = connection.cursor()

        # Blocking evidence uses blocked_session_id.
        # Other evidence types may use session_id.
        session_id = evidence.get(
            "session_id",
            evidence.get("blocked_session_id")
        )

        cursor.execute(
            """
            INSERT INTO incident_evidence
            (
                incident_id,
                snapshot_id,
                evidence_type,
                severity,
                database_name,
                session_id,
                blocking_session_id,
                wait_type,
                wait_time_ms,
                cpu_time_ms,
                elapsed_time_ms,
                reads,
                writes,
                logical_reads,
                login_name,
                host_name,
                program_name,
                sql_text,
                evidence_data
            )
            VALUES
            (
                %(incident_id)s,
                %(snapshot_id)s,
                %(evidence_type)s,
                %(severity)s,
                %(database_name)s,
                %(session_id)s,
                %(blocking_session_id)s,
                %(wait_type)s,
                %(wait_time_ms)s,
                %(cpu_time_ms)s,
                %(elapsed_time_ms)s,
                %(reads)s,
                %(writes)s,
                %(logical_reads)s,
                %(login_name)s,
                %(host_name)s,
                %(program_name)s,
                %(sql_text)s,
                %(evidence_data)s
            )
            """,
            {
                "incident_id": incident_id,
                "snapshot_id": snapshot_id,
                "evidence_type": evidence_type,
                "severity": severity,
                "database_name": evidence.get("database_name"),
                "session_id": session_id,
                "blocking_session_id": evidence.get(
                    "blocking_session_id"
                ),
                "wait_type": evidence.get("wait_type"),
                "wait_time_ms": evidence.get("wait_time_ms"),
                "cpu_time_ms": evidence.get("cpu_time_ms"),
                "elapsed_time_ms": evidence.get("elapsed_time_ms"),
                "reads": evidence.get("reads"),
                "writes": evidence.get("writes"),
                "logical_reads": evidence.get("logical_reads"),
                "login_name": evidence.get("login_name"),
                "host_name": evidence.get("host_name"),
                "program_name": evidence.get("program_name"),
                "sql_text": evidence.get("sql_text"),
                "evidence_data": Json(evidence)
            }
        )

        connection.commit()

        return cursor.rowcount

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def get_incident_evidence(incident_id):
    connection = get_pg_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                id,
                incident_id,
                snapshot_id,
                captured_at,
                evidence_type,
                severity,
                database_name,
                session_id,
                blocking_session_id,
                wait_type,
                wait_time_ms,
                cpu_time_ms,
                elapsed_time_ms,
                reads,
                writes,
                logical_reads,
                login_name,
                host_name,
                program_name,
                sql_text,
                evidence_data
            FROM incident_evidence
            WHERE incident_id = %s
            ORDER BY captured_at;
            """,
            (incident_id,)
        )

        rows = cursor.fetchall()

        columns = [
            "id",
            "incident_id",
            "snapshot_id",
            "captured_at",
            "evidence_type",
            "severity",
            "database_name",
            "session_id",
            "blocking_session_id",
            "wait_type",
            "wait_time_ms",
            "cpu_time_ms",
            "elapsed_time_ms",
            "reads",
            "writes",
            "logical_reads",
            "login_name",
            "host_name",
            "program_name",
            "sql_text",
            "evidence_data"
        ]

        result = []

        for row in rows:
            result.append(dict(zip(columns, row)))

        return result

    finally:
        connection.close()

def evidence_event_exists(event_id):
    connection = get_pg_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT 1
            FROM incident_evidence
            WHERE evidence_type = 'DEADLOCK'
              AND evidence_data->>'event_id' = %s
            LIMIT 1;
            """,
            (event_id,)
        )

        return cursor.fetchone() is not None

    finally:
        connection.close()  