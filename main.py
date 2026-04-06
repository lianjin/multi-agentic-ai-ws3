from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END

from state import State
from agents import orchestrator
from nodes import (
    human_node,
    check_exit_condition,
    orchestrator_routing,
    participant_node,
    summarizer_node
)


load_dotenv(override=True)  # Override, so it would use your local .env file




def build_graph():
    """
    Build the LangGraph workflow.
    """

    builder = StateGraph(State)

    # Add nodes
    builder.add_node("human", human_node)
    builder.add_node("orchestrator", orchestrator)
    builder.add_node("participant", participant_node)
    builder.add_node("summarizer", summarizer_node)

    # Entry point
    builder.add_edge(START, "human")

    # After human input, check for exit or continue
    builder.add_conditional_edges("human", check_exit_condition, {
        "summarizer": "summarizer",
        "orchestrator": "orchestrator"
    })

    # After orchestrator, route to participant or back to human
    builder.add_conditional_edges("orchestrator", orchestrator_routing, {
        "participant": "participant",
        "human": "human"
    })

    # After participant speaks, return to orchestrator for next turn
    builder.add_edge("participant", "orchestrator")

    # Summarizer ends the graph
    builder.add_edge("summarizer", END)

    return builder.compile()


def main():
    print("=== SMART CITY EMERGENCY RESPONSE TEAM ===")
    print("Report an incident to engage the response team. Type 'exit' to close the session.\n")
    print("Team on standby:")
    print("  - Field Dispatcher: real-time data acquisition and incident prioritization")
    print("  - Traffic Controller: road condition analysis and response planning")
    print("  - Safety Analyst: final assessment and recommendations\n")

    graph = build_graph()

    print(graph.get_graph().draw_ascii())

    initial_state = State(
        messages=[],
        volley_msg_left=0,
        next_speaker=None
    )

    try:
        graph.invoke(initial_state)
    except KeyboardInterrupt:
        print("\n\nSession interrupted. Stay safe!")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        print("Ending session...")


if __name__ == "__main__":
    main()
