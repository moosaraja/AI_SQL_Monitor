import psutil

from db_connection import get_connection


def get_cpu_usage():

    connection = get_connection()

    try:
        cursor = connection.cursor()

        # Identify the SQL Server process
        cursor.execute("""
            SELECT CONVERT(
                int,
                SERVERPROPERTY('ProcessID')
            )
        """)

        row = cursor.fetchone()

        if row is None or row[0] is None:
            raise RuntimeError(
                "Unable to identify SQL Server process"
            )

        sql_pid = int(row[0])

    finally:
        connection.close()

    # Read SQL Server CPU utilization
    process = psutil.Process(sql_pid)

    # Measures CPU activity over a 1-second interval
    process_cpu = process.cpu_percent(interval=1.0)

    logical_cpus = psutil.cpu_count(logical=True)

    if not logical_cpus:
        raise RuntimeError(
            "Unable to determine logical CPU count"
        )

    # Normalize to the total host CPU capacity
    cpu_percent = process_cpu / logical_cpus

    cpu_percent = round(
        max(0.0, min(100.0, cpu_percent)),
        2
    )

    return {
        "metric": "sql_server_cpu",
        "value": cpu_percent,
        "unit": "percent",
        "status": "ok"
    }


if __name__ == "__main__":

    print(get_cpu_usage())