import json
import re
from pathlib import Path


# Get the project root directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Store conversation history inside the transcripts folder
MEMORY_DIR = PROJECT_ROOT / "transcripts"
MEMORY_DIR.mkdir(parents=True, exist_ok=True)


def get_memory_path(thread_id):

    # Validate conversation ID
    if not isinstance(thread_id, str):
        raise ValueError("Thread ID must be a string.")

    if not re.fullmatch(r"[a-zA-Z0-9_-]{1,64}", thread_id):
        raise ValueError(
            "Invalid thread ID. Use only letters, numbers, underscores, and hyphens."
        )

    return MEMORY_DIR / f"{thread_id}.json"


def save_message(thread_id, role, message):

    file_path = get_memory_path(thread_id)

    if role not in ("user", "assistant"):
        raise ValueError("Role must be 'user' or 'assistant'.")

    # Check that the message can be stored as JSON
    try:
        json.dumps(message)
    except (TypeError, ValueError):
        raise ValueError("Message must contain JSON-serializable data.")

    if file_path.exists():

        with open(file_path, "r", encoding="utf-8") as file:
            history = json.load(file)

        if not isinstance(history, list):
            raise ValueError("Conversation history must be a JSON list.")

    else:
        history = []

    history.append({
        "role": role,
        "message": message
    })

    # Write safely using a temporary file
    temporary_path = file_path.with_suffix(".tmp")

    with open(temporary_path, "w", encoding="utf-8") as file:
        json.dump(history, file, indent=4, ensure_ascii=False)

    temporary_path.replace(file_path)


def load_history(thread_id):

    file_path = get_memory_path(thread_id)

    if not file_path.exists():
        return []

    with open(file_path, "r", encoding="utf-8") as file:
        history = json.load(file)

    if not isinstance(history, list):
        raise ValueError("Conversation history must be a JSON list.")

    return history


def reset_conversation(thread_id):

    file_path = get_memory_path(thread_id)

    if file_path.exists():
        file_path.unlink()

    return "Conversation reset successfully."


if __name__ == "__main__":

    thread_id = "memory_audit_test"

    print("===== MEMORY TEST =====")

    save_message(
        thread_id,
        "user",
        "What is my ticket status?"
    )

    save_message(
        thread_id,
        "assistant",
        "Your ticket is In Progress."
    )

    print("\nCONVERSATION HISTORY:")
    print(json.dumps(load_history(thread_id), indent=4))

    print("\n===== INVALID THREAD ID TEST =====")

    try:
        load_history("../outside_folder")
    except ValueError as error:
        print("Unsafe thread ID rejected:", error)

    print("\n===== RESET TEST =====")

    print(reset_conversation(thread_id))
    print("History after reset:", load_history(thread_id))

    print("\nMEMORY TEST COMPLETED!")