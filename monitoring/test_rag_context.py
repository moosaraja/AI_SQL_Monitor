from rag_engine import retrieve_relevant_knowledge
from rag_context import build_rag_context


def main():

    query = (
        "SQL Server blocking with LCK_M_IS "
        "wait type and blocked session investigation"
    )

    print(f"\nQuery:\n{query}")

    results = retrieve_relevant_knowledge(
        query,
        limit=2
    )

    print(f"\nRetrieved chunks: {len(results)}")

    context = build_rag_context(results)

    print("\n========== RAG CONTEXT ==========\n")
    print(context)
    print("\n=================================\n")


if __name__ == "__main__":
    main()