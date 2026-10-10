from db_connection import get_connection


def get_active_requests():
    connection = get_connection()

    try:
        cursor = connection.cursor()

        query = """
        SELECT
            r.session_id,
            r.status,
            r.command,
            r.cpu_time,
            r.total_elapsed_time,
            r.reads,
            r.writes,
            r.logical_reads,
            r.wait_type,
            r.wait_time,
            r.blocking_session_id,
            DB_NAME(r.database_id) AS database_name,
            s.login_name,
            s.host_name,
            s.program_name,
            t.text AS sql_text
        FROM sys.dm_exec_requests r
        INNER JOIN sys.dm_exec_sessions s
            ON r.session_id = s.session_id
        CROSS APPLY sys.dm_exec_sql_text(r.sql_handle) t
        WHERE s.is_user_process = 1
        AND s.program_name <> 'Python'
        ORDER BY r.cpu_time DESC;
        """

        cursor.execute(query)

        rows = cursor.fetchall()

        requests = []

        for row in rows:
            requests.append({
                "session_id": row.session_id,
                "status": row.status,
                "command": row.command,
                "cpu_time_ms": row.cpu_time,
                "elapsed_time_ms": row.total_elapsed_time,
                "reads": row.reads,
                "writes": row.writes,
                "logical_reads": row.logical_reads,
                "wait_type": row.wait_type,
                "wait_time_ms": row.wait_time,
                "blocking_session_id": row.blocking_session_id,
                "database_name": row.database_name,
                "login_name": row.login_name,
                "host_name": row.host_name,
                "program_name": row.program_name,
                "sql_text": row.sql_text
            })

        return {
            "metric": "active_requests",
            "count": len(requests),
            "requests": requests,
            "status": "ok"
        }

    finally:
        connection.close()


if __name__ == "__main__":
    result = get_active_requests()

    print(f"Active request count: {result['count']}")

    for request in result["requests"]:
        print(request)