from sentence_transformers import SentenceTransformer
from rag_repository import search_similar_chunks



MODEL_NAME = "all-MiniLM-L6-v2"

_model = None


def get_embedding_model():
    global _model

    if _model is None:
        print(f"Loading embedding model: {MODEL_NAME}")
        _model = SentenceTransformer(MODEL_NAME)

    return _model


def create_embedding(text):
    model = get_embedding_model()

    embedding = model.encode(
        text,
        normalize_embeddings=True
    )

    return embedding.tolist()

if __name__ == "__main__":


    query = """
        blocking
        """

    embedding = create_embedding(query)

    results = search_similar_chunks(
        embedding,
        limit=2
    )

    for index, result in enumerate(results, start=1):
    
            print(f"Result {index}")
            print(f"Title      : {result['title']}")
            print(f"Similarity : {result['similarity']:.4f}")
            print(f"Content    :")
            print(result["chunk_text"])
            print("\n---------------------------------\n")
    

    