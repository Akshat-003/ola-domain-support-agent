import re


# Permanent configuration
GROUNDING_THRESHOLD = 0.50


def normalize_text(text):
    """Convert text to lowercase and remove punctuation."""
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)
    return text


def validate_groundedness(answer, context):
    """
    Check whether the answer is supported by the retrieved context.

    Returns:
        True: Answer passes the word-overlap threshold.
        False: Answer is empty or does not pass the threshold.
    """

    if not answer or not context:
        print("\n===== GROUNDEDNESS CHECK =====")
        print("Groundedness score: 0.0")
        print("Result: REFUSED - Missing answer or context")
        return False

    answer_words = set(normalize_text(answer).split())
    context_words = set(normalize_text(context).split())

    if not answer_words:
        return False

    matching_words = answer_words.intersection(context_words)

    score = len(matching_words) / len(answer_words)

    print("\n===== GROUNDEDNESS CHECK =====")
    print("Matching words:", len(matching_words))
    print("Total answer words:", len(answer_words))
    print("Groundedness score:", round(score, 4))

    is_grounded = score >= GROUNDING_THRESHOLD

    if is_grounded:
        print("Result: GROUNDED")
    else:
        print("Result: REFUSED - Insufficient context support")

    return is_grounded


# Temporary testing code
if __name__ == "__main__":

    context = (
        "Customers may request a refund for eligible payment failures "
        "and duplicate deductions."
    )

    answer = ( 
        "Customers may request a refund for eligible payment failures "
    "and duplicate deductions."
)
    

    result = validate_groundedness(answer, context)

    print("Grounded:", result)