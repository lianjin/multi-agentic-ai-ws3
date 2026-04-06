from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage


def summarizer(state) -> str:
    """
    Generate final assessment report using LLM when session ends.

    Args:
        state: Current conversation state with messages

    Returns:
        Formatted assessment report string
    """
    messages = state.get("messages", [])

    if not messages:
        return "No incident data to summarize."

    # Extract conversation text
    conversation_text = ""
    for msg in messages:
        # Messages are now always dicts
        conversation_text += f"{msg.get('content', '')}\n"

    if not conversation_text.strip():
        return "No incident content to summarize."

    # System prompt for summarization
    system_prompt = """You are the reporting system for the Smart City Emergency Response Team.

Generate a concise final assessment report that captures:
1. Incident summary and current status
2. Key findings from the Field Dispatcher (traffic data and priority)
3. Road condition analysis and response plan from the Traffic Controller
4. Final safety assessment and recommendations from the Safety Analyst
5. Overall risk level and suggested next actions

Format your report in a clear, structured way suitable for an emergency operations log.
Keep it professional and actionable."""

    user_prompt = f"""Here is the emergency response team session:

{conversation_text}

Please provide the final assessment report for this incident."""

    try:
        # Call LLM
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=1)

        response = llm.invoke(
            [SystemMessage(content=system_prompt), HumanMessage(content=user_prompt)]
        )

        if isinstance(response.content, list):
            summary = " ".join(str(item) for item in response.content).strip()
        else:
            summary = str(response.content).strip()

        # Format with header
        return f"=== SMART CITY EMERGENCY RESPONSE — FINAL ASSESSMENT REPORT ===\n\n{summary}"

    except Exception as e:
        # Fallback to basic summary if LLM fails
        return f"""=== SMART CITY EMERGENCY RESPONSE — FINAL ASSESSMENT REPORT ===

Total messages: {len(messages)}

Unable to generate detailed report at this time.
The session has been logged for review."""
