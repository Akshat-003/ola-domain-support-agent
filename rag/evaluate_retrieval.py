import chromadb
from rag.retrieval import retrieve_documents


# Connect to the existing ChromaDB database.
client = chromadb.PersistentClient(path="chroma_db")


# Five evaluation queries and their expected relevant documents.
test_queries = [
    {
        "question": "How can a customer request a refund?",
        "relevant_docs": ["refund_policy"]
    },
    {
        "question": "What are the response times for different ticket severities?",
        "relevant_docs": ["sla_policy"]
    },
    {
        "question": "How are urgent customer complaints escalated?",
        "relevant_docs": ["escalation_matrix"]
    },
    {
        "question": "What are the company's customer support working hours?",
        "relevant_docs": ["business_hours"]
    },
    {
        "question": "How does the company handle repeated complaints?",
        "relevant_docs": ["repeat_complaints"]
    }
]


def evaluate_collection(collection_name):

    total_precision = 0
    total_recall = 0

    # Find how many chunks exist in this collection.
    collection = client.get_collection(name=collection_name)
    total_chunks = collection.count()

    print(f"\n========== {collection_name} ==========")
    print("Total available chunks:", total_chunks)

    for item in test_queries:

        question = item["question"]
        relevant_docs = set(item["relevant_docs"])

        # Retrieve all available chunks.
        results = retrieve_documents(
            question,
            collection_name,
            top_k=total_chunks
        )

        # Map chunks to parent documents.
        # Remove duplicates while preserving retrieval ranking.
        all_unique_docs = list(dict.fromkeys(
            result["document_id"] for result in results
        ))

        # Select the top 3 unique parent documents.
        retrieved_docs = all_unique_docs[:3]

        retrieved_relevant_docs = (
            set(retrieved_docs) & relevant_docs
        )

        relevant_count = len(retrieved_relevant_docs)

        # Precision@3 uses the number of retrieved unique documents.
        precision = (
            relevant_count / len(retrieved_docs)
            if retrieved_docs else 0
        )

        # Recall@3 measures how many relevant documents were retrieved.
        recall = (
            relevant_count / len(relevant_docs)
            if relevant_docs else 0
        )

        total_precision += precision
        total_recall += recall

        print("\nQuestion:", question)
        print("Retrieved top 3 unique documents:", retrieved_docs)
        print("Relevant documents:", sorted(relevant_docs))

        print(
            f"Precision@3: {relevant_count}/"
            f"{len(retrieved_docs)} = {precision:.3f}"
        )

        print(
            f"Recall@3: {relevant_count}/"
            f"{len(relevant_docs)} = {recall:.3f}"
        )

    number_of_queries = len(test_queries)

    average_precision = total_precision / number_of_queries
    average_recall = total_recall / number_of_queries

    print("\n---------- FINAL RESULTS ----------")
    print(f"Average Precision@3: {average_precision:.3f}")
    print(f"Average Recall@3: {average_recall:.3f}")

    return average_precision, average_recall


# Temporary demonstration code.
# This section runs only when this file is executed directly.
if __name__ == "__main__":

    fixed_results = evaluate_collection("fixed_size_chunks")

    sentence_results = evaluate_collection("sentence_chunks")

    print("\n========== FINAL COMPARISON ==========")

    print("Fixed-size chunking:")
    print("Precision:", round(fixed_results[0], 3))
    print("Recall:", round(fixed_results[1], 3))

    print("\nSentence-based chunking:")
    print("Precision:", round(sentence_results[0], 3))
    print("Recall:", round(sentence_results[1], 3))