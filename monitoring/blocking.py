from db_connection import get_connection


def get_blocking_requests():
    connection = get_connection()

    try:
        cursor = connection.cursor()

        query = """
        SELECT
            r.session_id AS blocked_session_id,
            r.blocking_session_id,

            r.status,
            r.wait_type,
            r.wait_time,
            r.cpu_time,
            r.total_elapsed_time,
            r.reads,
            r.writes,
            r.logical_reads,

            DB_NAME(r.database_id) AS database_name,

            blocked.login_name AS blocked_login,
            blocked.host_name AS blocked_host,
            blocked.program_name AS blocked_program,

            blocked_sql.text AS blocked_sql_text,

            blocker.status AS blocker_status,
            blocker.login_name AS blocker_login,
            blocker.host_name AS blocker_host,
            blocker.program_name AS blocker_program

        FROM sys.dm_exec_requests r

        INNER JOIN sys.dm_exec_sessions blocked
            ON r.session_id = blocked.session_id

        LEFT JOIN sys.dm_exec_sessions blocker
            ON r.blocking_session_id = blocker.session_id

        OUTER APPLY sys.dm_exec_sql_text(r.sql_handle) blocked_sql

        WHERE r.blocking_session_id <> 0
          AND blocked.is_user_process = 1

        ORDER BY r.wait_time DESC;
        """

        cursor.execute(query)

        rows = cursor.fetchall()

        blocking_requests = []

        for row in rows:

            blocking_requests.append({
                "blocked_session": {
                    "session_id": row.blocked_session_id,
                    "login_name": row.blocked_login,
                    "host_name": row.blocked_host,
                    "program_name": row.blocked_program,
                    "status": row.status,
                    "wait_type": row.wait_type,
                    "wait_time_ms": row.wait_time,
                    "cpu_time_ms": row.cpu_time,
                    "elapsed_time_ms": row.total_elapsed_time,
                    "reads": row.reads,
                    "writes": row.writes,
                    "logical_reads": row.logical_reads,
                    "sql_text": row.blocked_sql_text
                },

                "blocking_session": {
                    "session_id": row.blocking_session_id,
                    "login_name": row.blocker_login,
                    "host_name": row.blocker_host,
                    "program_name": row.blocker_program,
                    "status": row.blocker_status
                },

                "database_name": row.database_name
            })

        return {
            "metric": "blocking",
            "count": len(blocking_requests),
            "blocking_requests": blocking_requests,
            "status": "ok"
        }

    finally:
        connection.close()


if __name__ == "__main__":

    result = get_blocking_requests()

    print(f"Blocking request count: {result['count']}")

    for blocking in result["blocking_requests"]:

        print("\n--- BLOCKING EVENT ---")

        print("Database:", blocking["database_name"])

        print(
            "Blocked session:",
            blocking["blocked_session"]["session_id"]
        )

        print(
            "Blocking session:",
            blocking["blocking_session"]["session_id"]
        )

        print(
            "Wait type:",
            blocking["blocked_session"]["wait_type"]
        )

        print(
            "Wait time:",
            blocking["blocked_session"]["wait_time_ms"],
            "ms"
        )

        print(
            "Blocked SQL:",
            blocking["blocked_session"]["sql_text"]
        )

        print(
            "Blocker login:",
            blocking["blocking_session"]["login_name"]
        )

        print(
            "Blocker program:",
            blocking["blocking_session"]["program_name"]
        )

        print(
            "Blocker status:",
            blocking["blocking_session"]["status"]
        )