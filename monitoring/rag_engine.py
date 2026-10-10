from pg_connection import get_pg_connection
from embedding_engine import create_embedding


def retrieve_relevant_knowledge(
    query,
    limit=3
):
    query_embedding = create_embedding(query)

    connection = get_pg_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                id,
                document_id,
                chunk_text,
                metadata,
                embedding <=> %s::vector AS distance
            FROM rag_chunks
            WHERE embedding IS NOT NULL
            ORDER BY embedding <=> %s::vector
            LIMIT %s;
            """,
            (
                query_embedding,
                query_embedding,
                limit
            )
        )

        rows = cursor.fetchall()

        results = []

        for row in rows:
            results.append({
                "id": row[0],
                "document_id": row[1],
                "chunk_text": row[2],
                "metadata": row[3],
                "distance": row[4]
            })

        return results

    finally:
        connection.close()