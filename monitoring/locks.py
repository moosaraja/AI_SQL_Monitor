from db_connection import get_connection


def get_locks():
    connection = get_connection()

    try:
        cursor = connection.cursor()

        query = """
        SELECT
            tl.request_session_id AS session_id,
            tl.resource_type,
            tl.resource_database_id,
            DB_NAME(tl.resource_database_id) AS database_name,
            tl.request_mode,
            tl.request_status,
            st.transaction_id,
            st.open_transaction_count
        FROM sys.dm_tran_locks tl

        LEFT JOIN sys.dm_tran_session_transactions st
            ON tl.request_session_id = st.session_id

        WHERE tl.request_session_id <> @@SPID

        ORDER BY
            tl.request_session_id,
            tl.request_status DESC;
        """

        cursor.execute(query)

        rows = cursor.fetchall()

        locks = []

        for row in rows:
            locks.append({
                "session_id": row.session_id,
                "resource_type": row.resource_type,
                "database_name": row.database_name,
                "request_mode": row.request_mode,
                "request_status": row.request_status,
                "transaction_id": row.transaction_id,
                "open_transaction_count": row.open_transaction_count
            })

        return {
            "metric": "locks",
            "count": len(locks),
            "locks": locks,
            "status": "ok"
        }

    finally:
        connection.close()


if __name__ == "__main__":

    result = get_locks()

    print(f"Lock count: {result['count']}")

    for lock in result["locks"]:
        print(lock)