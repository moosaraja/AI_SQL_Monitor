
from pg_connection import get_pg_connection
from embedding_engine import create_embedding


def search_chunks_for_embeddings(EmbeddedChunk):

    connection = get_pg_connection()

    try:
        cursor = connection.cursor()

        # Convert embedding list to pgvector format
        vector_string = "[" + ",".join(map(str, EmbeddedChunk)) + "]"

        cursor.execute(
            """
            SELECT
                chunk_text,
                embedding <=> %s::vector AS distance
            FROM rag_chunks
            WHERE embedding IS NOT NULL
            ORDER BY embedding <=> %s::vector
            LIMIT 1;
            """,
            (vector_string, vector_string)
        )

        # Return only the closest matching row
        return cursor.fetchone()

    finally:
        connection.close()


def main():

    user_input = input(
        "Enter the word to search the closest match: "
    )

    # Convert search text to embedding
    EmbeddedChunk = create_embedding(user_input)

    # Search the closest matching chunk
    closestvalue = search_chunks_for_embeddings(EmbeddedChunk)

    print("\nClosest chunk:")

    if closestvalue:

        chunk_text, distance = closestvalue

        print(chunk_text)
        print(f"\nDistance: {distance:.4f}")

    else:
        print("No matching records found.")

    print("=" * 60)


if __name__ == "__main__":
    main()
