from pg_connection import get_pg_connection


def create_alert_schema():

    connection = get_pg_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alerts (

                id BIGSERIAL PRIMARY KEY,

                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

                server_name VARCHAR(255),

                database_name VARCHAR(255),

                metric VARCHAR(100) NOT NULL,

                severity VARCHAR(20) NOT NULL,

                message TEXT NOT NULL,

                status VARCHAR(20) NOT NULL DEFAULT 'OPEN',

                snapshot_id BIGINT,

                CONSTRAINT fk_alert_snapshot
                    FOREIGN KEY (snapshot_id)
                    REFERENCES monitoring_snapshots(id)
            );
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_alerts_created_at
            ON alerts (created_at);
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_alerts_status
            ON alerts (status);
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_alerts_severity
            ON alerts (severity);
        """)

        connection.commit()

        print("Alert schema created successfully.")

    finally:
        connection.close()


if __name__ == "__main__":

    try:
        create_alert_schema()

    except Exception as e:
        print("Alert schema creation failed:")
        print(e)