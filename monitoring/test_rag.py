from rag_engine import retrieve_relevant_knowledge


def main():

    query = "Why is my SQL Server session blocked?"

    print(f"\nQuery: {query}\n")

    results = retrieve_relevant_knowledge(
        query,
        limit=2
    )

    for result in results:

        print("=" * 60)

        print(f"Chunk ID: {result['id']}")
        print(f"Distance: {result['distance']}")

        print("\nChunk text:")
        print(result["chunk_text"])


if __name__ == "__main__":
    main()