from db_connection import get_connection


def get_cpu_usage():
    connection = get_connection()

    try:
        cursor = connection.cursor()

        query = """
        SELECT
            instance_name,
            cntr_value
        FROM sys.dm_os_performance_counters
        WHERE object_name LIKE '%Resource Pool Stats%'
          AND counter_name = 'CPU usage %'
          AND instance_name = 'default';
        """

        cursor.execute(query)

        row = cursor.fetchone()

        if row is None:
            return {
                "metric": "sql_server_cpu",
                "value": None,
                "unit": "percent",
                "status": "not_available"
            }

        return {
            "metric": "sql_server_cpu",
            "value": row.cntr_value,
            "unit": "percent",
            "status": "ok"
        }

    finally:
        connection.close()


if __name__ == "__main__":
    cpu = get_cpu_usage()
    print(cpu)