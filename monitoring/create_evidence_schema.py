from pg_connection import get_pg_connection


def create_evidence_schema():

    connection = get_pg_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS incident_evidence (

                id BIGSERIAL PRIMARY KEY,

                incident_id BIGINT NOT NULL,

                snapshot_id BIGINT NOT NULL,

                captured_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

                evidence_type VARCHAR(50) NOT NULL,

                severity VARCHAR(20),

                database_name VARCHAR(255),

                session_id INTEGER,

                blocking_session_id INTEGER,

                wait_type VARCHAR(100),

                wait_time_ms BIGINT,

                cpu_time_ms BIGINT,

                elapsed_time_ms BIGINT,

                reads BIGINT,

                writes BIGINT,

                logical_reads BIGINT,

                login_name VARCHAR(255),

                host_name VARCHAR(255),

                program_name VARCHAR(255),

                sql_text TEXT,

                evidence_data JSONB,

                CONSTRAINT fk_evidence_incident
                    FOREIGN KEY (incident_id)
                    REFERENCES incidents(id)
                    ON DELETE CASCADE,

                CONSTRAINT fk_evidence_snapshot
                    FOREIGN KEY (snapshot_id)
                    REFERENCES monitoring_snapshots(id)
            );
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_incident_evidence_incident
            ON incident_evidence (incident_id);
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_incident_evidence_snapshot
            ON incident_evidence (snapshot_id);
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_incident_evidence_type
            ON incident_evidence (evidence_type);
        """)

        connection.commit()

        print("Incident evidence schema created successfully.")

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


if __name__ == "__main__":

    try:
        create_evidence_schema()

    except Exception as e:
        print("Incident evidence schema creation failed:")
        print(e)