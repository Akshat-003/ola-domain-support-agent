import json
from pathlib import Path

DATASET_PATH = Path("dataset/support_tickets.json")

# Escalation threshold based on the synthetic dataset distribution
ESCALATION_THRESHOLD = 0.60


def load_tickets():
    with open(DATASET_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


def calculate_escalation_score(ticket):

    recency_score = ticket["days_since_created"] / 30

    escalation_score = (
        0.6 * int(ticket["escalated"])
        + 0.4 * recency_score
    )

    return round(escalation_score, 3)


def check_support_ticket_status(record_id):

    tickets = load_tickets()

    for ticket in tickets:

        if ticket["record_id"] == record_id:

            score = calculate_escalation_score(ticket)

            escalation_priority = (
                "High"
                if score >= ESCALATION_THRESHOLD
                else "Normal"
            )

            return {
                "record_id": ticket["record_id"],
                "status": ticket["status"],
                "resolution_time_hours": ticket["resolution_time_hours"],
                "escalation_score": score,
                "escalation_priority": escalation_priority
            }

    return {
        "error": f"Ticket {record_id} was not found."
    }


def analyze_escalation_distribution():

    tickets = load_tickets()

    scores = [
        calculate_escalation_score(ticket)
        for ticket in tickets
    ]

    high_priority = sum(
        score >= ESCALATION_THRESHOLD
        for score in scores
    )

    normal_priority = len(scores) - high_priority

    print("\n===== ESCALATION SCORE DISTRIBUTION =====")
    print("Total tickets:", len(scores))
    print("Minimum score:", min(scores))
    print("Maximum score:", max(scores))
    print("Average score:", round(sum(scores) / len(scores), 3))
    print("Escalation threshold:", ESCALATION_THRESHOLD)
    print("High priority tickets:", high_priority)
    print("Normal priority tickets:", normal_priority)


# Temporary testing code
if __name__ == "__main__":

    print("===== TICKET LOOKUP TEST =====")

    tickets = load_tickets()

    for ticket in tickets[:2]:

        result = check_support_ticket_status(
            ticket["record_id"]
        )

        print("\nTicket information:")
        print(json.dumps(result, indent=4))

    analyze_escalation_distribution()