def build_rag_context(results):
    """
    Convert retrieved RAG chunks into a text context
    that can later be supplied to the LLM.
    """

    if not results:
        return "No relevant DBA knowledge was found."

    context_parts = []

    for index, result in enumerate(results, start=1):

        context_parts.append(
            f"""
Knowledge Source {index}

Chunk ID: {result["id"]}
Similarity Distance: {result["distance"]}

{result["chunk_text"]}
"""
        )

    return "\n".join(context_parts)