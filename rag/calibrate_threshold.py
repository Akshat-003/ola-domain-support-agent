from rag.retrieval import retrieve_documents

# Three in-scope questions and two out-of-scope questions
test_queries = [
    {
        "question": "How can I request a refund?",
        "type": "IN-SCOPE"
    },
    {
        "question": "What are the customer support working hours?",
        "type": "IN-SCOPE"
    },
    {
        "question": "How are urgent complaints escalated?",
        "type": "IN-SCOPE"
    },
    {
        "question": "Who won the latest cricket match?",
        "type": "OUT-OF-SCOPE"
    },
    {
        "question": "Explain how photosynthesis works.",
        "type": "OUT-OF-SCOPE"
    }
]


if __name__ == "__main__":

    print("===== NO-ANSWER THRESHOLD CALIBRATION =====")

    scores = {
        "IN-SCOPE": [],
        "OUT-OF-SCOPE": []
    }

    for item in test_queries:

        question = item["question"]
        query_type = item["type"]

        results = retrieve_documents(
            question,
            "sentence_chunks",
            top_k=1
        )

        similarity = results[0]["similarity"]

        scores[query_type].append(similarity)

        print("\nQuestion:", question)
        print("Type:", query_type)
        print("Top-1 similarity:", similarity)

    print("\n========== SCORE SUMMARY ==========")

    print("In-scope scores:", scores["IN-SCOPE"])
    print("Out-of-scope scores:", scores["OUT-OF-SCOPE"])

    average_in = sum(scores["IN-SCOPE"]) / len(scores["IN-SCOPE"])
    average_out = sum(scores["OUT-OF-SCOPE"]) / len(scores["OUT-OF-SCOPE"])

    print("\nAverage in-scope similarity:", round(average_in, 4))
    print("Average out-of-scope similarity:", round(average_out, 4))