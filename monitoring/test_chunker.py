from text_chunker import TextChunker


text = """
SQL Server blocking happens when one session holds a lock
that another session needs. The blocked session has to wait
until the blocking session releases the lock.

Blocking can cause query performance problems, application
timeouts, and increased resource usage.
"""


chunker = TextChunker(maxlen=100)

chunks = chunker.chunk(text)

for i, chunk in enumerate(chunks, start=1):
    print(f"\n--- Chunk {i} ---")
    print(chunk)
    print(f"Length: {len(chunk)}")