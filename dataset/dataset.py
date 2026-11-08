import random
import json
from collections import Counter

# ==========================================
# 1. DATASET CONFIGURATION
# ==========================================

SEED = 42
TOTAL_RECORDS = 50

random.seed(SEED)

# Category weights
categories = [
    "Billing",
    "Technical Issue",
    "Account Access",
    "Product Defect",
    "General Inquiry"
]

category_weights = [25, 25, 15, 10, 25]

# Status weights
statuses = [
    "Open",
    "In Progress",
    "Escalated",
    "Resolved",
    "Closed"
]

status_weights = [20, 25, 10, 30, 15]


# ==========================================
# 2. GENERATE SUPPORT TICKETS
# ==========================================

SUPPORT_TICKETS = []

generated_categories = random.choices(
    categories,
    weights=category_weights,
    k=TOTAL_RECORDS
)

generated_statuses = random.choices(
    statuses,
    weights=status_weights,
    k=TOTAL_RECORDS
)

generated_escalations = random.choices(
    [True, False],
    weights=[20, 80],
    k=TOTAL_RECORDS
)


for i in range(TOTAL_RECORDS):

    ticket = {
        "record_id": f"OLA-{1001 + i}",

        "category": generated_categories[i],

        "status": generated_statuses[i],

        "resolution_time_hours": random.randint(1, 72),

        "days_since_created": random.randint(0, 30),

        "escalated": generated_escalations[i],

        "amount_inr": random.randint(50, 5000)
    }

    SUPPORT_TICKETS.append(ticket)


# ==========================================
# 3. DATASET VALIDATION
# ==========================================

category_counts = Counter(
    ticket["category"] for ticket in SUPPORT_TICKETS
)

status_counts = Counter(
    ticket["status"] for ticket in SUPPORT_TICKETS
)

escalated_count = sum(
    ticket["escalated"] for ticket in SUPPORT_TICKETS
)

escalation_percentage = (
    escalated_count / TOTAL_RECORDS
) * 100


assert len(SUPPORT_TICKETS) >= 40

assert all(
    category_counts[category] >= 3
    for category in categories
)

assert all(
    status_counts[status] >= 1
    for status in statuses
)

assert 10 <= escalation_percentage <= 30


# ==========================================
# 4. DISPLAY RESULTS
# ==========================================

print("\n========== OLA SUPPORT TICKET DATASET ==========")

print(f"Total Records: {len(SUPPORT_TICKETS)}")
print(f"Random Seed: {SEED}")

print("\nCategory Distribution:")

for category, count in category_counts.items():
    print(f"{category}: {count}")

print("\nStatus Distribution:")

for status, count in status_counts.items():
    print(f"{status}: {count}")

print("\nEscalation Statistics:")

print(f"Escalated Tickets: {escalated_count}")

print(f"Escalation Percentage: {escalation_percentage}%")

print("\nFirst 5 Support Tickets:")

for ticket in SUPPORT_TICKETS[:5]:
    print(ticket)


# ==========================================
# 5. SAVE DATASET AS JSON
# ==========================================

with open("dataset/support_tickets.json", "w") as file:

    json.dump(
        SUPPORT_TICKETS,
        file,
        indent=4
    )

print("\nDataset successfully generated and saved!")