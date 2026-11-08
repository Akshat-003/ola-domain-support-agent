import chromadb

from pathlib import Path

from rag.chunking import (
    create_all_chunks,
    fixed_size_chunking,
    sentence_based_chunking
)

from rag.embeddings import generate_embeddings


# ==========================================
# 1. CHROMADB CLIENT
# ==========================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

CHROMA_DIRECTORY = PROJECT_ROOT / "chroma_db"

client = chromadb.PersistentClient(
    path=str(CHROMA_DIRECTORY)
)


# ==========================================
# 2. CREATE COLLECTION
# ==========================================

def create_collection(collection_name):

    try:
        client.delete_collection(collection_name)
    except Exception:
        pass

    return client.create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"}
    )


# ==========================================
# 3. STORE CHUNKS
# ==========================================

def store_chunks(collection, chunks):

    if not chunks:
        return

    texts = [chunk["text"] for chunk in chunks]

    ids = [chunk["chunk_id"] for chunk in chunks]

    metadatas = [
        {"document_id": chunk["document_id"]}
        for chunk in chunks
    ]

    embeddings = generate_embeddings(texts)

    collection.add(
        ids=ids,
        documents=texts,
        metadatas=metadatas,
        embeddings=embeddings.tolist()
    )

    print(f"Stored {len(chunks)} chunks in: {collection.name}")


# ==========================================
# 4. CHECK DOCUMENT DUPLICATES
# ==========================================

def document_exists(collection, document_id):

    existing = collection.get(
        where={"document_id": document_id},
        limit=1
    )

    return bool(existing["ids"])


# ==========================================
# 5. ADD ONE NEW DOCUMENT
# ==========================================

def add_document_to_vector_store(document_id, text):

    if not isinstance(document_id, str) or not document_id.strip():
        raise ValueError("Document ID cannot be empty.")

    if not isinstance(text, str) or not text.strip():
        raise ValueError("Document text cannot be empty.")

    if document_id != document_id.strip():
        raise ValueError("Document ID cannot contain surrounding spaces.")

    if not all(
        character.isalnum() or character in "_-"
        for character in document_id
    ):
        raise ValueError("Document ID contains invalid characters.")

    fixed_collection = client.get_collection(
        "fixed_size_chunks"
    )

    sentence_collection = client.get_collection(
        "sentence_chunks"
    )

    # Check both collections before insertion.
    if document_exists(fixed_collection, document_id):
        raise ValueError("Document already exists in fixed-size collection.")

    if document_exists(sentence_collection, document_id):
        raise ValueError("Document already exists in sentence-based collection.")

    # Generate fixed-size chunks.
    fixed_results = fixed_size_chunking(text)

    fixed_chunks = []

    for index, chunk in enumerate(fixed_results):

        fixed_chunks.append({
            "chunk_id": f"{document_id}_fixed_{index}",
            "document_id": document_id,
            "text": chunk
        })

    # Generate sentence-based chunks.
    sentence_results = sentence_based_chunking(text)

    sentence_chunks = []

    for index, chunk in enumerate(sentence_results):

        sentence_chunks.append({
            "chunk_id": f"{document_id}_sentence_{index}",
            "document_id": document_id,
            "text": chunk
        })

    if not fixed_chunks or not sentence_chunks:
        raise ValueError("Document did not produce valid chunks.")

    # Insert into both collections with rollback protection.
    try:

        store_chunks(fixed_collection, fixed_chunks)

        store_chunks(sentence_collection, sentence_chunks)

    except Exception:

        # Remove inserted chunks if either insertion fails.
        fixed_collection.delete(
            where={"document_id": document_id}
        )

        sentence_collection.delete(
            where={"document_id": document_id}
        )

        raise

    return {
        "document_id": document_id,
        "fixed_chunks_added": len(fixed_chunks),
        "sentence_chunks_added": len(sentence_chunks),
        "message": "Document added successfully."
    }


# ==========================================
# 6. BUILD COMPLETE VECTOR DATABASE
# ==========================================

def build_vector_store():

    fixed_chunks, sentence_chunks = create_all_chunks()

    fixed_collection = create_collection(
        "fixed_size_chunks"
    )

    sentence_collection = create_collection(
        "sentence_chunks"
    )

    store_chunks(fixed_collection, fixed_chunks)

    store_chunks(sentence_collection, sentence_chunks)

    print("\n===== VECTOR STORE RESULTS =====")

    print("Fixed-size collection:", fixed_collection.count())

    print("Sentence-based collection:", sentence_collection.count())


if __name__ == "__main__":

    build_vector_store()