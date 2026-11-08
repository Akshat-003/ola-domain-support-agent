from rag.retrieval import retrieve_documents
from rag.config import SIMILARITY_THRESHOLD, MOCK_LLM
from rag.grounding import validate_groundedness


def generate_answer(question):

    results = retrieve_documents(
        question,
        "sentence_chunks",
        top_k=3
    )

    if not results:
        return "I could not find relevant information in my knowledge base."

    best_similarity = results[0]["similarity"]

    print("Top similarity:", round(best_similarity, 4))

    if best_similarity < SIMILARITY_THRESHOLD:
        return (
            "I'm sorry, but I couldn't find reliable information "
            "about this question in my support knowledge base."
        )

    context = "\n".join(
        result["text"] for result in results
    )

    if MOCK_LLM:
        answer = (
            "Based on the support knowledge base:\n\n"
            + context
        )
    else:
        answer = "MOCK_LLM is disabled."

    is_grounded = validate_groundedness(answer, context)

    if not is_grounded:
        return (
            "I cannot provide an answer because the response "
            "could not be verified against the knowledge base."
        )

    return answer


# Temporary demonstration code
if __name__ == "__main__":

    test_questions = [
        # 5 in-scope questions
        "How can I request a refund?",
        "What are the customer support working hours?",
        "How are high priority tickets escalated?",
        "How should repeat customer complaints be handled?",
        "How are customers informed during service outages?",

        # 1 out-of-scope question
        "Who won the latest cricket match?"
    ]

    for index, question in enumerate(test_questions, start=1):

        print("\n" + "=" * 60)
        print(f"TEST {index}")
        print("QUESTION:", question)

        answer = generate_answer(question)

        print("\nANSWER:")
        print(answer)
        print("=" * 60)