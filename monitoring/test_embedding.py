from embedding_engine import create_embedding


TEXT = """
SQL Server blocking occurs when one session holds
a lock and another session requires an incompatible lock.
"""


def main():

    print("\nCreating embedding...\n")

    embedding = create_embedding(TEXT)

    print(f"Embedding created.")
    print(f"Vector length: {len(embedding)}")

    print("\nFirst 10 values:")
    print(embedding[:10])


if __name__ == "__main__":
    main()