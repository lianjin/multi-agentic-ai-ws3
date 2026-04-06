from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END

from state import State
from agents import orchestrator
from nodes import (
    human_node,
    participant_node,
    summarizer_node,
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
    # After human input, orchestrator start routing
    builder.add_edge("human", "orchestrator")

    def automation_routing(state: State):
        # if volley_msg_left > 0, go to participant; otherwise, go to summarizer
        if state.get("volley_msg_left", 0) > 0:
            return "participant"
        # if no more volleys left, go to summarizer
        return "summarizer"

    # After human input, route to orchestrator, which will decide whether to go to participant or summarizer based on volley count
    builder.add_conditional_edges(
        "orchestrator",
        automation_routing,  # use the new routing function
        {"participant": "participant", "summarizer": "summarizer"},
    )

    # After participant speaks, back to orchestrator for next turn or summarization
    builder.add_edge("participant", "orchestrator")

    # Summarizer ends the graph
    builder.add_edge("summarizer", END)

    return builder.compile()


def main():
    print("=== SMART CITY EMERGENCY RESPONSE TEAM ===")
    print("Report an incident to engage the response team.\n")
    print("Team on standby:")
    print(
        "  - Field Dispatcher: real-time data acquisition and incident prioritization"
    )
    print("  - Traffic Controller: road condition analysis and response planning")
    print("  - Safety Analyst: final assessment and recommendations\n")

    graph = build_graph()

    print(graph.get_graph().draw_ascii())

    initial_state = State(messages=[], volley_msg_left=0, next_speaker=None)

    try:
        graph.invoke(initial_state)
    except KeyboardInterrupt:
        print("\n\nSession interrupted. Stay safe!")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        print("Ending session...")


if __name__ == "__main__":
    main()
