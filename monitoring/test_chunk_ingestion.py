from text_chunker import TextChunker
from rag_repository import create_document, save_chunk


DOCUMENT_TITLE = "SQL Server Blocking"
DOCUMENT_SOURCE = "AI_SQL_Monitor DBA Knowledge"
DOCUMENT_TYPE = "SQL_SERVER"


DOCUMENT_TEXT = """
SQL Server blocking occurs when one session holds a lock
on a resource and another session requires an incompatible lock.

A blocking situation should be investigated by identifying
the blocked session, blocking session, database, wait type,
wait duration, SQL text, login, host, application and
transaction state.

A common wait type associated with lock blocking is LCK_M_IS.

The blocked session is not necessarily the root cause.
The blocking session or its transaction may be responsible
for holding the resource.

A sleeping session can still block another session if it
owns an open transaction and continues to hold locks.

Before terminating a session, a DBA should investigate
the transaction, SQL statement, application and business impact.
"""


def main():

    print("\nCreating RAG document...")

    document_id = create_document(
        title=DOCUMENT_TITLE,
        source=DOCUMENT_SOURCE,
        document_type=DOCUMENT_TYPE
    )

    print(f"Document created: {document_id}")

    chunker = TextChunker(maxlen=500)

    chunks = list(
        chunker.chunk(DOCUMENT_TEXT)
    )

    print(f"Chunks created: {len(chunks)}")

    for index, chunk_text in enumerate(chunks, start=1):

        chunk_id = save_chunk(
            document_id=document_id,
            chunk_text=chunk_text,
            embedding=None,
            metadata={
                "document_type": DOCUMENT_TYPE,
                "chunk_number": index
            }
        )

        print(f"Chunk {index} saved. ID: {chunk_id}")

    print("\nChunk ingestion completed.")


if __name__ == "__main__":
    main()