from db_connection import get_connection


def get_memory_status():
    connection = get_connection()

    try:
        cursor = connection.cursor()

        query = """
        SELECT
            total_physical_memory_kb,
            available_physical_memory_kb,
            total_page_file_kb,
            available_page_file_kb,
            system_memory_state_desc
        FROM sys.dm_os_sys_memory;
        """

        cursor.execute(query)

        row = cursor.fetchone()

        if row is None:
            return {
                "metric": "memory",
                "status": "not_available"
            }
        else:

            total_memory_gb = row.total_physical_memory_kb / 1024 / 1024
            available_memory_gb = row.available_physical_memory_kb / 1024 / 1024
            used_memory_gb = total_memory_gb - available_memory_gb

            return {
                "metric": "memory",
                "total_physical_memory_gb": round(total_memory_gb, 2),
                "available_physical_memory_gb": round(available_memory_gb, 2),
                "used_physical_memory_gb": round(used_memory_gb, 2),
                "memory_state": row.system_memory_state_desc,
                "status": "ok"
            }

    finally:
        connection.close()


if __name__ == "__main__":
    memory = get_memory_status()
    print(memory)