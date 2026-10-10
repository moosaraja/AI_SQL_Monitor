from pg_connection import get_pg_connection
from embedding_engine import create_embedding


def get_chunks_without_embeddings():
    connection = get_pg_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                id,
                chunk_text
            FROM rag_chunks
            WHERE id =2
            ORDER BY id;
            """
        )

        return cursor.fetchall()

    finally:
        connection.close()


def save_embedding(chunk_id, embedding):
    connection = get_pg_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            UPDATE rag_chunks
            SET embedding = %s
            WHERE id = %s;
            """,
            (
                embedding,
                chunk_id
            )
        )

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def main():

    print("\nFinding chunks without embeddings...\n")

    chunks = get_chunks_without_embeddings()

    print(f"Chunks found: {len(chunks)}")

    for chunk_id, chunk_text in chunks:

        print(f"\nCreating embedding for chunk {chunk_id}...")

        embedding = create_embedding(chunk_text)

        print(f"Vector length: {len(embedding)}")

        save_embedding(
            chunk_id,
            embedding
        )

        print(f"Embedding saved for chunk {chunk_id}")

    print("\nEmbedding generation completed.")


if __name__ == "__main__":
    main()