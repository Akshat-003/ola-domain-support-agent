import chromadb
from pathlib import Path

from rag.embeddings import generate_embeddings


# Use the same absolute database path as vector_store.py
PROJECT_ROOT = Path(__file__).resolve().parent.parent
CHROMA_DIRECTORY = PROJECT_ROOT / "chroma_db"

client = chromadb.PersistentClient(
    path=str(CHROMA_DIRECTORY)
)


def retrieve_documents(query, collection_name, top_k=3):

    # Validate inputs
    if not isinstance(query, str) or not query.strip():
        raise ValueError("Query cannot be empty.")

    if top_k < 1:
        raise ValueError("top_k must be at least 1.")

    # Get the selected collection
    collection = client.get_collection(name=collection_name)

    if collection.count() == 0:
        return []

    # Convert the question into an embedding
    query_embedding = generate_embeddings([query])

    # Search for the most relevant chunks
    results = collection.query(
        query_embeddings=query_embedding.tolist(),
        n_results=min(top_k, collection.count())
    )

    retrieved_documents = []

    if not results["documents"] or not results["documents"][0]:
        return []

    for i, document in enumerate(results["documents"][0]):

        distance = results["distances"][0][i]

        # For cosine distance, similarity = 1 - distance
        similarity = 1 - distance

        metadata = results["metadatas"][0][i] or {}

        retrieved_documents.append({
            "text": document,
            "document_id": metadata.get("document_id", "unknown"),
            "similarity": round(similarity, 4)
        })

    return retrieved_documents


if __name__ == "__main__":

    question = "How can a customer request a refund?"

    print("\n===== FIXED-SIZE RETRIEVAL =====")

    fixed_results = retrieve_documents(
        question,
        "fixed_size_chunks"
    )

    for result in fixed_results:
        print("\nDocument:", result["document_id"])
        print("Similarity:", result["similarity"])
        print("Content:", result["text"])

    print("\n===== SENTENCE-BASED RETRIEVAL =====")

    sentence_results = retrieve_documents(
        question,
        "sentence_chunks"
    )

    for result in sentence_results:
        print("\nDocument:", result["document_id"])
        print("Similarity:", result["similarity"])
        print("Content:", result["text"])