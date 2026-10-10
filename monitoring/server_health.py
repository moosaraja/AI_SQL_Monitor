from db_connection import get_connection


def get_server_health():
    connection = get_connection()

    try:
        cursor = connection.cursor()

        query = """
        SELECT
            SERVERPROPERTY('ServerName') AS server_name,
            SERVERPROPERTY('ProductVersion') AS product_version,
            SERVERPROPERTY('ProductLevel') AS product_level,
            SERVERPROPERTY('Edition') AS edition,
            DB_NAME() AS database_name;
        """

        cursor.execute(query)

        row = cursor.fetchone()

        return {
            "server": row.server_name,
            "product_version": row.product_version,
            "product_level": row.product_level,
            "edition": row.edition,
            "database": row.database_name
        }

    finally:
        connection.close()


if __name__ == "__main__":
    health = get_server_health()

    print(health)