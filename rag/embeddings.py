from sentence_transformers import SentenceTransformer

# Load the embedding model
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

print("Loading embedding model...")

model = SentenceTransformer(MODEL_NAME)


# Generate embeddings
def generate_embeddings(texts):

    embeddings = model.encode(
        texts,
        convert_to_numpy=True,
        normalize_embeddings=True
    )

    return embeddings


# Test embedding generation
if __name__ == "__main__":

    sample_texts = [
        "How can I get a refund?",
        "What is the refund procedure?",
        "How do I access my Ola account?"
    ]

    vectors = generate_embeddings(sample_texts)

    print("\n===== EMBEDDING RESULTS =====")

    print("Number of texts:", len(sample_texts))

    print("Embedding shape:", vectors.shape)

    print("First embedding:", vectors[0][:10])

    print("\nEmbedding generation successful!")