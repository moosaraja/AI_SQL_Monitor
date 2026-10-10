from pg_connection import get_pg_connection
from psycopg2.extras import Json


def create_document(
    title,
    source=None,
    document_type=None
):
    connection = get_pg_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO rag_documents
            (
                title,
                source,
                document_type
            )
            VALUES (%s, %s, %s)
            RETURNING id;
            """,
            (
                title,
                source,
                document_type
            )
        )

        document_id = cursor.fetchone()[0]

        connection.commit()

        return document_id

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def save_chunk(
    document_id,
    chunk_text,
    embedding=None,
    metadata=None
):
    connection = get_pg_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO rag_chunks
            (
                document_id,
                chunk_text,
                embedding,
                metadata
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s
            )
            RETURNING id;
            """,
            (
                document_id,
                chunk_text,
                embedding,
                Json(metadata or {})
            )
        )

        chunk_id = cursor.fetchone()[0]

        connection.commit()

        return chunk_id

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()