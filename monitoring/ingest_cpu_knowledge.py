from pathlib import Path

from rag_repository import create_document, save_chunk
from embedding_engine import create_embedding
from text_chunker import TextChunker

KNOWLEDGE_FILE = (
    Path(__file__).resolve().parent.parent
    / "knowledge"
    / "sql_server_cpu.md"
)

text = KNOWLEDGE_FILE.read_text(encoding="utf-8")

document_id = create_document(
    title="SQL Server High CPU Troubleshooting",
    source=str(KNOWLEDGE_FILE),
    document_type="DBA_KNOWLEDGE"
)

chunker = TextChunker(maxlen=500)

for index, chunk in enumerate(chunker.chunk(text), start=1):

    embedding = create_embedding(chunk)

    save_chunk(
        document_id=document_id,
        chunk_text=chunk,
        embedding=embedding,
        metadata={
            "topic": "sql_server_cpu",
            "chunk_number": index
        }
    )

    print(f"Saved CPU knowledge chunk {index}")

print(f"CPU knowledge document created: {document_id}")