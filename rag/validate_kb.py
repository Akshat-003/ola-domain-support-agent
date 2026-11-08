from pathlib import Path
import re

KB_DIR = Path("knowledge_base")

required_files = [
    "ticket_priority.txt",
    "sla_policy.txt",
    "escalation_matrix.txt",
    "refund_policy.txt",
    "communication_policy.txt",
    "business_hours.txt",
    "repeat_complaints.txt",
    "service_credit.txt",
    "feedback_process.txt",
    "vip_handling.txt",
    "outage_protocol.txt",
    "data_retention.txt"
]

print("\n===== KNOWLEDGE BASE VALIDATION =====\n")

all_valid = True

for filename in required_files:

    file_path = KB_DIR / filename

    if not file_path.exists():
        print(f"❌ Missing: {filename}")
        all_valid = False
        continue

    text = file_path.read_text(encoding="utf-8").strip()

    sentences = [
        s for s in re.split(r'(?<=[.!?])\s+', text)
        if s.strip()
    ]

    count = len(sentences)

    if 2 <= count <= 5:
        print(f"✅ {filename}: {count} sentences")
    else:
        print(f"❌ {filename}: {count} sentences")
        all_valid = False

print("\n====================================")

if all_valid:
    print("SUCCESS: All 12 documents are valid!")
else:
    print("ERROR: Please check the documents.")