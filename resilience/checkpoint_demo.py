import sqlite3
from typing import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.sqlite import SqliteSaver


# Shared state of the workflow
class SupportState(TypedDict):
    message: str
    step_results: list[str]


# Node 1
def receive_request(state: SupportState):
    print("Executing Node 1: Receive Request")

    return {
        "step_results": state["step_results"] + ["Request received"]
    }


# Node 2
def analyze_request(state: SupportState):
    print("Executing Node 2: Analyze Request")

    return {
        "step_results": state["step_results"] + ["Request analyzed"]
    }


# Node 3
def prepare_response(state: SupportState):
    print("Executing Node 3: Prepare Response")

    return {
        "step_results": state["step_results"] + ["Response prepared"]
    }


def main():

    # Create SQLite database connection
    connection = sqlite3.connect(
        "resilience/checkpoints.sqlite",
        check_same_thread=False
    )

    checkpointer = SqliteSaver(connection)
    checkpointer.setup()

    # Build graph
    builder = StateGraph(SupportState)

    builder.add_node("receive_request", receive_request)
    builder.add_node("analyze_request", analyze_request)
    builder.add_node("prepare_response", prepare_response)

    builder.add_edge(START, "receive_request")
    builder.add_edge("receive_request", "analyze_request")
    builder.add_edge("analyze_request", "prepare_response")
    builder.add_edge("prepare_response", END)

    # Interrupt before Node 3
    graph = builder.compile(
        checkpointer=checkpointer,
        interrupt_before=["prepare_response"]
    )

    config = {
        "configurable": {
            "thread_id": "ola_support_001"
        }
    }

    print("\n--- FIRST EXECUTION ---")

    first_result = graph.invoke(
        {
            "message": "Check my support ticket",
            "step_results": []
        },
        config
    )

    print("\nSaved State:")
    print(first_result)

    print("\n--- RESUMING WORKFLOW ---")

    # Resume the same thread
    final_result = graph.invoke(None, config)

    print("\nFinal State:")
    print(final_result)

    connection.close()


if __name__ == "__main__":
    main()