import re
from pathlib import Path


# =====================================
# CONFIGURATION
# =====================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

KB_DIRECTORY = PROJECT_ROOT / "knowledge_base"

CHUNK_SIZE = 500
CHUNK_OVERLAP = 100
SENTENCES_PER_CHUNK = 3


# =====================================
# LOAD DOCUMENTS
# =====================================

def load_documents():

    if not KB_DIRECTORY.exists():
        raise FileNotFoundError(
            f"Knowledge base directory not found: {KB_DIRECTORY}"
        )

    documents = []

    for file_path in sorted(KB_DIRECTORY.glob("*.txt")):

        text = file_path.read_text(encoding="utf-8").strip()

        if not text:
            raise ValueError(
                f"Knowledge-base document is empty: {file_path.name}"
            )

        documents.append({
            "document_id": file_path.stem,
            "text": text
        })

    if not documents:
        raise ValueError("No knowledge-base documents found.")

    return documents


# =====================================
# STRATEGY 1:
# FIXED-SIZE CHUNKING WITH OVERLAP
# =====================================

def fixed_size_chunking(text):

    if not isinstance(text, str):
        raise TypeError("Document text must be a string.")

    if CHUNK_SIZE <= 0:
        raise ValueError("CHUNK_SIZE must be greater than zero.")

    if CHUNK_OVERLAP < 0 or CHUNK_OVERLAP >= CHUNK_SIZE:
        raise ValueError(
            "CHUNK_OVERLAP must be non-negative and smaller than CHUNK_SIZE."
        )

    text = text.strip()

    if not text:
        return []

    chunks = []

    start = 0

    while start < len(text):

        end = min(start + CHUNK_SIZE, len(text))

        chunk_text = text[start:end].strip()

        if chunk_text:
            chunks.append(chunk_text)

        if end == len(text):
            break

        start = end - CHUNK_OVERLAP

    return chunks


# =====================================
# STRATEGY 2:
# SENTENCE-BASED CHUNKING
# =====================================

def sentence_based_chunking(text):

    if not isinstance(text, str):
        raise TypeError("Document text must be a string.")

    text = text.strip()

    if not text:
        return []

    sentences = re.split(
        r'(?<=[.!?])\s+',
        text
    )

    sentences = [
        sentence.strip()
        for sentence in sentences
        if sentence.strip()
    ]

    chunks = []

    for i in range(0, len(sentences), SENTENCES_PER_CHUNK):

        chunk = " ".join(
            sentences[i:i + SENTENCES_PER_CHUNK]
        )

        chunks.append(chunk)

    return chunks


# =====================================
# GENERATE BOTH TYPES OF CHUNKS
# =====================================

def create_all_chunks():

    documents = load_documents()

    fixed_chunks = []

    sentence_chunks = []

    for document in documents:

        doc_id = document["document_id"]

        text = document["text"]

        # Fixed-size chunks

        fixed_results = fixed_size_chunking(text)

        for index, chunk in enumerate(fixed_results):

            fixed_chunks.append({
                "chunk_id": f"{doc_id}_fixed_{index}",
                "document_id": doc_id,
                "text": chunk
            })

        # Sentence-based chunks

        sentence_results = sentence_based_chunking(text)

        for index, chunk in enumerate(sentence_results):

            sentence_chunks.append({
                "chunk_id": f"{doc_id}_sentence_{index}",
                "document_id": doc_id,
                "text": chunk
            })

    return fixed_chunks, sentence_chunks


# =====================================
# TEST THE CHUNKING SYSTEM
# =====================================

if __name__ == "__main__":

    documents = load_documents()

    fixed, sentence = create_all_chunks()

    print("\n===== OLA RAG CHUNKING RESULTS =====")

    print("Total documents:", len(documents))

    print("Fixed-size chunks:", len(fixed))

    print("Sentence-based chunks:", len(sentence))

    print("\nFixed-size example:")
    print(fixed[0])

    print("\nSentence-based example:")
    print(sentence[0])

    print("\nChunking completed successfully!")