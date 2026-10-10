from db_connection import get_connection


def get_user_sessions():
    connection = get_connection()

    try:
        cursor = connection.cursor()

        query = """
        SELECT
            session_id,
            login_name,
            host_name,
            program_name,
            status,
            database_id,
            login_time
        FROM sys.dm_exec_sessions
        WHERE is_user_process = 1
        ORDER BY session_id;
        """

        cursor.execute(query)

        rows = cursor.fetchall()

        sessions = []

        for row in rows:
            sessions.append({
                "session_id": row.session_id,
                "login_name": row.login_name,
                "host_name": row.host_name,
                "program_name": row.program_name,
                "status": row.status,
                "database_id": row.database_id,
                "login_time": str(row.login_time)
            })

        return {
            "metric": "user_sessions",
            "count": len(sessions),
            "sessions": sessions,
            "status": "ok"
        }

    finally:
        connection.close()


if __name__ == "__main__":
    result = get_user_sessions()

    print(f"User session count: {result['count']}")

    for session in result["sessions"]:
        print(session)