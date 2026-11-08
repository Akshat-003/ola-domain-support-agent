import json
import statistics
from pathlib import Path
from contextlib import redirect_stdout
from io import StringIO

from rag.retrieval import retrieve_documents
from rag.generation import generate_answer
from rag.grounding import validate_groundedness


# Project paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_FILE = PROJECT_ROOT / "evaluations" / "rag_triad_results.json"

COLLECTION_NAME = "sentence_chunks"
TOP_K = 3

REFUSAL_TEXT = "couldn't find reliable information"


# 15 evaluation queries:
# 12 in-scope queries covering all 12 knowledge documents.
# 3 out-of-scope queries.

EVALUATION_QUERIES = [

    {
        "question": "How are support tickets assigned different priority levels?",
        "expected_document": "ticket_priority",
        "keywords": ["priority", "ticket", "urgent"]
    },
    {
        "question": "What is the expected resolution time for different ticket severities?",
        "expected_document": "sla_policy",
        "keywords": ["resolution", "hours", "severity"]
    },
    {
        "question": "When should a support ticket be escalated?",
        "expected_document": "escalation_matrix",
        "keywords": ["escalation", "escalate", "team"]
    },
    {
        "question": "What are the rules for customer refunds?",
        "expected_document": "refund_policy",
        "keywords": ["refund", "payment", "eligible"]
    },
    {
        "question": "Which communication channels can customers use to contact support?",
        "expected_document": "communication_policy",
        "keywords": ["communication", "support", "customer"]
    },
    {
        "question": "What are the customer support working hours and holiday rules?",
        "expected_document": "business_hours",
        "keywords": ["business", "hours", "holiday"]
    },
    {
        "question": "How should repeated customer complaints be handled?",
        "expected_document": "repeat_complaints",
        "keywords": ["repeat", "complaints", "customer"]
    },
    {
        "question": "When can customers receive service credits?",
        "expected_document": "service_credit",
        "keywords": ["service", "credit", "customer"]
    },
    {
        "question": "How does the support team collect customer feedback?",
        "expected_document": "feedback_process",
        "keywords": ["feedback", "customer", "survey"]
    },
    {
        "question": "How should VIP customers be handled?",
        "expected_document": "vip_handling",
        "keywords": ["vip", "priority", "customer"]
    },
    {
        "question": "How should customers be informed about service outages?",
        "expected_document": "outage_protocol",
        "keywords": ["outage", "service", "communication"]
    },
    {
        "question": "How long should customer support ticket data be retained?",
        "expected_document": "data_retention",
        "keywords": ["data", "retention", "records"]
    },

    # Out-of-scope queries
    {
        "question": "Who won the latest international cricket match?",
        "expected_document": None,
        "keywords": []
    },
    {
        "question": "Explain the process of photosynthesis in plants.",
        "expected_document": None,
        "keywords": []
    },
    {
        "question": "What is the capital city of Japan?",
        "expected_document": None,
        "keywords": []
    }
]


def calculate_context_relevance(results, expected_document):

    if expected_document is None:
        # Out-of-scope queries should not retrieve
        # documents from the support knowledge base.
        return 1.0 if not results else 0.0

    # Remove duplicate document IDs.
    unique_documents = list(dict.fromkeys(
        result["document_id"] for result in results
    ))

    # Check whether the expected document appears
    # in the retrieved document list.
    relevant_documents = sum(
        1 for document_id in unique_documents
        if document_id == expected_document
    )

    # Use unique documents as the denominator.
    if not unique_documents:
        return 0.0

    return round(
        relevant_documents / len(unique_documents), 4
    )

def calculate_answer_relevance(answer, keywords, is_out_of_scope):

    answer_lower = answer.lower()

    if is_out_of_scope:
        # A refusal is the expected relevant response
        # for an out-of-scope question.
        return 1.0 if REFUSAL_TEXT.lower() in answer_lower else 0.0

    if not keywords:
        return 0.0

    matched_keywords = sum(
        1 for keyword in keywords
        if keyword.lower() in answer_lower
    )

    return round(matched_keywords / len(keywords), 4)


def evaluate_query(query_data):

    question = query_data["question"]
    expected_document = query_data["expected_document"]
    keywords = query_data["keywords"]

    # Retrieve context for evaluation.
    with redirect_stdout(StringIO()):
        results = retrieve_documents(
            question,
            COLLECTION_NAME,
            top_k=TOP_K
        )

    # Generate the actual system answer.
    with redirect_stdout(StringIO()):
        answer = generate_answer(question)

    # Context relevance score.
    context_score = calculate_context_relevance(
        results,
        expected_document
    )

    # Groundedness score.
    is_out_of_scope = expected_document is None

    if is_out_of_scope and REFUSAL_TEXT.lower() in answer.lower():
        # A correct refusal makes no unsupported factual claim.
        groundedness_score = 1.0
    else:
        with redirect_stdout(StringIO()):
            grounded = validate_groundedness(
                answer,
                "\n".join(result["text"] for result in results)
            )

        groundedness_score = 1.0 if grounded else 0.0

    # Answer relevance score.
    answer_score = calculate_answer_relevance(
        answer,
        keywords,
        is_out_of_scope
    )

    return {
        "question": question,
        "expected_document": expected_document,
        "retrieved_documents": [
            result["document_id"] for result in results
        ],
        "answer": answer,
        "context_relevance": context_score,
        "groundedness": groundedness_score,
        "answer_relevance": answer_score
    }


def main():

    print("\n========== RAG TRIAD EVALUATION ==========")

    results = []

    for index, query in enumerate(EVALUATION_QUERIES, start=1):

        result = evaluate_query(query)
        results.append(result)

        print(f"\nQuery {index}/15")
        print("Question:", result["question"])
        print("Retrieved:", result["retrieved_documents"])
        print("Context Relevance:", result["context_relevance"])
        print("Groundedness:", result["groundedness"])
        print("Answer Relevance:", result["answer_relevance"])

    # Calculate average scores.
    average_scores = {
        "context_relevance": round(
            statistics.mean(r["context_relevance"] for r in results), 4
        ),
        "groundedness": round(
            statistics.mean(r["groundedness"] for r in results), 4
        ),
        "answer_relevance": round(
            statistics.mean(r["answer_relevance"] for r in results), 4
        )
    }

    report = {
        "evaluation_type": "Deterministic MOCK_LLM RAG Triad Evaluation",
        "total_queries": len(results),
        "in_scope_queries": 12,
        "out_of_scope_queries": 3,
        "average_scores": average_scores,
        "query_results": results
    }

    # Save evaluation results as JSON.
    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(report, file, indent=4, ensure_ascii=False)

    print("\n========== FINAL AVERAGE SCORES ==========")
    print("Context Relevance:", average_scores["context_relevance"])
    print("Groundedness:", average_scores["groundedness"])
    print("Answer Relevance:", average_scores["answer_relevance"])

    print("\nTotal queries evaluated:", len(results))
    print("Report saved at:", OUTPUT_FILE)


if __name__ == "__main__":
    main()