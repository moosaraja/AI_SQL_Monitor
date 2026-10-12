import json
from datetime import datetime, timedelta, timezone
from db_connection import get_connection


def get_query_store_top_cpu(
    database="Vehicle",
    hours=24,
    limit=10
):
    """Return historical CPU-intensive queries from Query Store."""

    limit = int(limit)
    hours = float(hours)

    if not 1 <= limit <= 100:
        raise ValueError("limit must be between 1 and 100")

    if not 0 < hours <= 720:
        raise ValueError("hours must be between 0 and 720")

    # Query Store interval timestamps are datetimeoffset.
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)

    connection = get_connection()

    try:
        cursor = connection.cursor()

        # USE cannot be parameterized. Validate the database
        # against sys.databases before quoting its identifier.
        cursor.execute(
            "SELECT name FROM sys.databases WHERE name = ?",
            database
        )

        if cursor.fetchone() is None:
            raise ValueError(f"Database not found: {database}")

        quoted_db = "[" + database.replace("]", "]]") + "]"
        cursor.execute(f"USE {quoted_db}")

        query = """
        SELECT TOP (?)
            DB_NAME() AS database_name,
            q.query_id,
            p.plan_id,
            SUM(rs.count_executions) AS execution_count,

            CAST(
                SUM(
                    rs.avg_cpu_time * rs.count_executions
                ) / 1000.0 AS FLOAT
            ) AS total_cpu_ms,

            CAST(
                SUM(
                    rs.avg_cpu_time * rs.count_executions
                ) / NULLIF(SUM(rs.count_executions), 0)
                / 1000.0 AS FLOAT
            ) AS avg_cpu_ms,

            CAST(
                SUM(
                    rs.avg_duration * rs.count_executions
                ) / NULLIF(SUM(rs.count_executions), 0)
                / 1000.0 AS FLOAT
            ) AS avg_duration_ms,

            CAST(
                SUM(
                    rs.avg_logical_io_reads * rs.count_executions
                ) AS FLOAT
            ) AS total_logical_reads,

            CONVERT(
            VARCHAR(33),
            MAX(rs.last_execution_time),
            127
             ) AS last_execution_time,

            qt.query_sql_text AS sql_text

        FROM sys.query_store_query_text AS qt
        JOIN sys.query_store_query AS q
            ON qt.query_text_id = q.query_text_id
        JOIN sys.query_store_plan AS p
            ON q.query_id = p.query_id
        JOIN sys.query_store_runtime_stats AS rs
            ON p.plan_id = rs.plan_id
        JOIN sys.query_store_runtime_stats_interval AS i
            ON rs.runtime_stats_interval_id =
               i.runtime_stats_interval_id

        WHERE i.end_time >= ?
          AND rs.execution_type = 0

        GROUP BY
            q.query_id,
            p.plan_id,
            qt.query_sql_text

        ORDER BY total_cpu_ms DESC;
        """

        cursor.execute(query, limit, cutoff)

        columns = [col[0] for col in cursor.description]

        return [
            dict(zip(columns, row))
            for row in cursor.fetchall()
        ]

    finally:
        connection.close()


if __name__ == "__main__":
    print(json.dumps(
        get_query_store_top_cpu(
            database="Vehicle",
            hours=24,
            limit=10
        ),
        indent=2,
        default=str
    ))