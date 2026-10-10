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


def create_schema():
    connection = psycopg2.connect(**DB_CONFIG)

    try:
        cursor = connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS monitoring_snapshots (
                id BIGSERIAL PRIMARY KEY,

                collected_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

                server_name VARCHAR(255),

                database_name VARCHAR(255),

                snapshot JSONB NOT NULL
            );
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_monitoring_snapshots_collected_at
            ON monitoring_snapshots (collected_at);
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_monitoring_snapshots_server
            ON monitoring_snapshots (server_name);
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_monitoring_snapshots_snapshot
            ON monitoring_snapshots
            USING GIN (snapshot);
        """)

        connection.commit()

        print("PostgreSQL telemetry schema created successfully.")

    finally:
        connection.close()


if __name__ == "__main__":

    try:
        create_schema()

    except Exception as e:
        print("Schema creation failed:")
        print(e)