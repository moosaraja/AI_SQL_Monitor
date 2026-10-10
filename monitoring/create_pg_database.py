import os
import psycopg2
from dotenv import load_dotenv


load_dotenv()


DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "postgres",
    "user": "postgres",
    "password": os.environ.get("PG_DB_PASSWORD", "")
}

TARGET_DATABASE = "ai_sql_monitor"


def create_database():
    connection = psycopg2.connect(**DB_CONFIG)

    try:
        connection.autocommit = True

        cursor = connection.cursor()

        cursor.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s",
            (TARGET_DATABASE,)
        )

        exists = cursor.fetchone()

        if exists:
            print(f"Database '{TARGET_DATABASE}' already exists.")
        else:
            cursor.execute(
                f'CREATE DATABASE "{TARGET_DATABASE}"'
            )
            print(f"Database '{TARGET_DATABASE}' created successfully.")

        cursor.close()

    finally:
        connection.close()


if __name__ == "__main__":
    try:
        create_database()
    except Exception as e:
        print("Database creation failed:")
        print(e)