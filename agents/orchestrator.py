from utils import debug

# Sequential coordination order for the Emergency Response Team
RESPONSE_SEQUENCE = ["field_dispatcher", "traffic_controller", "safety_analyst"]


def orchestrator(state):
    """
    Select next responder based on sequential coordination order.
    Manages volley control and updates state accordingly.

    Coordination order: Field Dispatcher -> Traffic Controller -> Safety Analyst

    Updates state with:
    - next_speaker: Selected role ID or "human"
    - volley_msg_left: Decremented counter

    Returns: Updated state
    """

    debug(state)
    volley_left = state.get("volley_msg_left", 0)
    debug(f"Volley messages left: {volley_left}", "ORCHESTRATOR")

    if volley_left <= 0:
        debug("No volleys left, returning to human", "ORCHESTRATOR")
        return {"next_speaker": "human", "volley_msg_left": 0}

    messages = state.get("messages", [])

    # Determine which role spoke last to advance the sequence
    last_role = None
    for msg in reversed(messages):
        name = msg.get("name", "")
        for role_id, role_name in [
            ("field_dispatcher", "Field Dispatcher"),
            ("traffic_controller", "Traffic Controller"),
            ("safety_analyst", "Safety Analyst"),
        ]:
            if name == role_name:
                last_role = role_id
                break
        if last_role:
            break

    # Advance to next role in sequence
    if last_role is None or last_role not in RESPONSE_SEQUENCE:
        selected_speaker = RESPONSE_SEQUENCE[0]
    else:
        current_index = RESPONSE_SEQUENCE.index(last_role)
        next_index = (current_index + 1) % len(RESPONSE_SEQUENCE)
        selected_speaker = RESPONSE_SEQUENCE[next_index]

    debug(
        f"Sequential selection: {selected_speaker} (volley {volley_left} -> {volley_left - 1})",
        "ORCHESTRATOR",
    )

    # Return only the updates (LangGraph will merge with existing state)
    return {"next_speaker": selected_speaker, "volley_msg_left": volley_left - 1}
