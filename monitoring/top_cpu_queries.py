import json
from db_connection import get_connection


def get_top_cpu_queries(limit=10):
    """Return top CPU-consuming cached query statements."""

    limit = int(limit)
    if not 1 <= limit <= 100:
        raise ValueError("limit must be between 1 and 100")

    query = """
    SELECT TOP (?)
        st.dbid AS sql_text_dbid,
        plan_db.database_id AS plan_dbid,
        DB_NAME(plan_db.database_id) AS plan_database,
        CASE
        WHEN COALESCE(st.dbid, plan_db.database_id) = 32767
        THEN 'mssqlsystemresource'
        ELSE DB_NAME(
        COALESCE(st.dbid, plan_db.database_id)
        )
        END AS database_name,
        qs.execution_count,
        CAST(qs.total_worker_time / 1000.0 AS FLOAT)
            AS total_cpu_ms,
        CAST(qs.last_worker_time / 1000.0 AS FLOAT)
            AS last_cpu_ms,
        CAST(qs.total_elapsed_time / 1000.0 AS FLOAT)
            AS total_duration_ms,
        qs.total_logical_reads,
        qs.creation_time AS plan_cached_at,
        qs.last_execution_time,
        SUBSTRING(
            st.text,
            (qs.statement_start_offset / 2) + 1,
            (
                (
                    CASE
                        WHEN qs.statement_end_offset = -1
                        THEN DATALENGTH(st.text)
                        ELSE qs.statement_end_offset
                    END - qs.statement_start_offset
                ) / 2
            ) + 1
        ) AS sql_text
    FROM sys.dm_exec_query_stats AS qs
    CROSS APPLY sys.dm_exec_sql_text(qs.sql_handle) AS st
    OUTER APPLY (
    SELECT CONVERT(INT, pa.value) AS database_id
    FROM sys.dm_exec_plan_attributes(qs.plan_handle) AS pa
    WHERE pa.attribute = 'dbid'
    ) AS plan_db
    ORDER BY qs.total_worker_time DESC;
    """

    connection = get_connection()

    try:
        cursor = connection.cursor()
        cursor.execute(query, limit)

        columns = [col[0] for col in cursor.description]

        return [
            dict(zip(columns, row))
            for row in cursor.fetchall()
        ]
    finally:
        connection.close()


if __name__ == "__main__":
    print(json.dumps(
        get_top_cpu_queries(),
        indent=2,
        default=str
    ))