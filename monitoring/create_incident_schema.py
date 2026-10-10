from pg_connection import get_pg_connection


def create_incident_schema():

    connection = get_pg_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS incidents (

                id BIGSERIAL PRIMARY KEY,

                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

                resolved_at TIMESTAMPTZ,

                server_name VARCHAR(255) NOT NULL,

                database_name VARCHAR(255),

                metric VARCHAR(100) NOT NULL,

                severity VARCHAR(20) NOT NULL,

                status VARCHAR(20) NOT NULL DEFAULT 'OPEN',

                message TEXT NOT NULL,

                first_snapshot_id BIGINT,

                last_snapshot_id BIGINT,

                occurrence_count INTEGER NOT NULL DEFAULT 1,

                CONSTRAINT fk_incident_first_snapshot
                    FOREIGN KEY (first_snapshot_id)
                    REFERENCES monitoring_snapshots(id),

                CONSTRAINT fk_incident_last_snapshot
                    FOREIGN KEY (last_snapshot_id)
                    REFERENCES monitoring_snapshots(id)
            );
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_incidents_status
            ON incidents (status);
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_incidents_metric_status
            ON incidents (metric, status);
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_incidents_created_at
            ON incidents (created_at);
        """)

        connection.commit()

        print("Incident schema created successfully.")

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


if __name__ == "__main__":

    try:
        create_incident_schema()

    except Exception as e:
        print("Incident schema creation failed:")
        print(e)