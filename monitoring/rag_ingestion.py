from embedding_engine import create_embedding
from rag_repository import create_document, save_chunk


KNOWLEDGE_DOCUMENTS = [
    {
        "title": "SQL Server Blocking",
        "source": "AI_SQL_Monitor DBA Knowledge",
        "document_type": "SQL_SERVER",
        "content": """
SQL Server blocking occurs when one session holds a lock on a resource
and another session requires an incompatible lock.

A blocking situation should be investigated by identifying:

- blocked session
- blocking session
- database
- wait type
- wait duration
- SQL text
- login
- host
- application
- transaction state

A common wait type associated with lock blocking is LCK_M_IS.

The blocked session is not necessarily the root cause. The blocking session
or its transaction may be responsible for holding the resource.

A sleeping session can still block another session if it owns an open
transaction and continues to hold locks.

Before terminating a session, a DBA should investigate the transaction,
SQL statement, application, and business impact.
"""
    },
    {
        "title": "SQL Server Deadlocks",
        "source": "AI_SQL_Monitor DBA Knowledge",
        "document_type": "SQL_SERVER",
        "content": """
A SQL Server deadlock occurs when two or more sessions hold resources that
the other sessions need, creating a circular dependency.

SQL Server detects the deadlock and selects a victim transaction to terminate
so that the circular dependency can be broken.

Deadlock investigation should examine:

- victim process
- participating sessions
- SQL statements
- resources
- database
- transaction information
- lock modes
- resource owners
- resource waiters

The SQL Server system_health Extended Events session can contain
xml_deadlock_report events that provide detailed deadlock information.

Repeated deadlocks may indicate transaction ordering problems, long-running
transactions, missing indexes, excessive locking, or application concurrency
patterns.

The actual cause should be determined from the captured evidence rather
than assumed.
"""
    },
    {
        "title": "SQL Server Wait Statistics",
        "source": "AI_SQL_Monitor DBA Knowledge",
        "document_type": "SQL_SERVER",
        "content": """
SQL Server wait statistics provide information about where sessions spend
time waiting.

Wait types should be interpreted in context.

Lock-related waits such as LCK_M_IS can indicate that a session is waiting
for a lock held by another session.

A wait by itself does not prove that a performance problem exists.

Investigation should consider:

- wait duration
- frequency
- affected sessions
- SQL statements
- blocking relationships
- CPU
- I/O
- transaction behavior

Performance diagnosis should use multiple pieces of evidence rather than
relying on a single metric.
"""
    }
]


def ingest_documents():

    for document in KNOWLEDGE_DOCUMENTS:

        print(f"\nIngesting: {document['title']}")

        document_id = create_document(
            title=document["title"],
            source=document["source"],
            document_type=document["document_type"]
        )

        print(f"Document ID: {document_id}")

        chunk_text = document["content"].strip()

        embedding = create_embedding(chunk_text)

        chunk_id = save_chunk(
            document_id=document_id,
            chunk_text=chunk_text,
            embedding=embedding,
            metadata={
                "document_type": document["document_type"]
            }
        )

        print(f"Chunk ID: {chunk_id}")

    print("\nKnowledge ingestion completed.")


if __name__ == "__main__":
    ingest_documents()