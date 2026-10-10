import os
import psycopg2
from dotenv import load_dotenv


load_dotenv()


DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "ai_sql_monitor",
    "user": "postgres",
    "password": os.environ.get("PG_DB_PASSWORD", "")
}


def get_pg_connection():
    return psycopg2.connect(**DB_CONFIG)


if __name__ == "__main__":

    try:
        connection = get_pg_connection()

        print("Connected to PostgreSQL successfully!")

        connection.close()

    except Exception as e:
        print("PostgreSQL connection failed:")
        print(e)