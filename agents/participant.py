from tools import singapore_time, singapore_weather, singapore_traffic
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from utils import debug
import re


# Role configurations for Smart City Emergency Response Team
PERSONAS = {
    "field_dispatcher": {
        "name": "Field Dispatcher",
        "role": "Field Dispatcher",
        "backstory": "Experienced emergency dispatcher responsible for obtaining real-time data and determining incident priority",
        "personality": "Decisive, methodical, calm under pressure, data-driven",
        "speech_style": "Clear and concise professional language, uses operational terminology, focuses on facts and urgency",
        "tools": ["traffic"],
    },
    "traffic_controller": {
        "name": "Traffic Controller",
        "role": "Traffic Controller",
        "backstory": "Senior traffic management specialist responsible for analyzing road conditions and formulating response plans",
        "personality": "Analytical, systematic, proactive, expert in traffic flow and road management",
        "speech_style": "Structured professional language, uses traffic management terminology, presents clear action plans",
        "tools": ["weather"],
    },
    "safety_analyst": {
        "name": "Safety Analyst",
        "role": "Safety Analyst",
        "backstory": "Chief safety analyst responsible for synthesizing all field information and producing the final comprehensive assessment report",
        "personality": "Thorough, precise, big-picture thinker, expert at synthesizing complex information",
        "speech_style": "Formal report-style language, structured and comprehensive, highlights risks and recommendations",
        "tools": ["time"],
    },
}


def execute_tool(tool_name):
    """
    Execute a specific tool and return its output.
    Returns Tool output as string
    """
    tool_name = tool_name.lower().strip()
    if tool_name == "time":
        return singapore_time()
    elif tool_name == "weather":
        return singapore_weather()
    elif tool_name == "traffic":
        return singapore_traffic()
    else:
        return f"Unknown tool: {tool_name}"


def participant(persona_id, state) -> dict:
    """
    Generate response for a team role using ReAct workflow with real tool calling.

    Args:
        persona_id: One of "field_dispatcher", "traffic_controller", "safety_analyst"
        state: Current conversation state

    Returns:
        Dict with message updates for state
    """
    if persona_id not in PERSONAS:
        return {
            "messages": [
                {"role": "assistant", "content": f"Unknown role: {persona_id}"}
            ]
        }

    persona = PERSONAS[persona_id]
    debug(f"\n=== {persona['name']} is analyzing... ===")

    # Get recent conversation for context
    messages = state.get("messages", [])
    conversation_text = ""
    for msg in messages:
        conversation_text += f"{msg.get('content', '')}\n"

    # Tool descriptions mapping
    tool_descriptions = {
        "time": "Returns current time in Singapore",
        "weather": "Returns current weather conditions in Singapore",
        "traffic": "Returns real-time traffic incidents in Singapore",
    }

    # Build available actions list based on role's tools
    available_actions = ""
    for tool in persona["tools"]:
        available_actions += f"\n\n{tool}:\n{tool_descriptions[tool]}"

    # System prompt for ReAct
    system_prompt = f"""You are the {persona['role']} of the Smart City Emergency Response Team.
Background: {persona['backstory']}
Personality: {persona['personality']}
Communication style: {persona['speech_style']}

You are responding to an emergency situation as part of a coordinated team response.

You run in a loop of Thought, Action, Observation.
At the end of the loop you output a Message.

Use Thought to describe your analysis of the situation.
Use Action to run one of the actions available to you.
Observation will be the result of running those actions.

Possible actions are:

{available_actions}

You only have access to the tools/actions listed above. Do not call tools that you do not have access to.

------

Example session:

Thought: I need to check current traffic conditions to assess the situation
Action: traffic

You will be called again with:
Observation: [Actual data returned after you call the tool]

You must never try to guess or fabricate data. Rely on the Observation for actual data. You MUST NOT answer with fabricated data.

You then continue thinking or output:
Message: [Your professional response in role]

IMPORTANT:
- You can use multiple actions by continuing the loop
- You must not be providing Observation in your response. Observation is a result from tool, not for you to respond.
- Once you have enough information, output Message: followed by your response
- Keep your Message focused and professional, covering your area of responsibility
"""

    # Internal loop for ReAct
    max_iterations = 5  # Prevent infinite loops
    internal_context = f"Incident report:\n{conversation_text}\n\nProvide your assessment as {persona['name']}.\n"

    for iteration in range(max_iterations):
        user_prompt = internal_context
        debug(f"Iteration {iteration + 1}/{max_iterations}")

        try:
            llm = ChatOpenAI(model="gpt-4o-mini", temperature=1)
            response = llm.invoke(
                [
                    SystemMessage(content=system_prompt),
                    HumanMessage(content=user_prompt),
                ]
            )
            content = response.content.strip()
            debug(f"LLM Response:\n{content}\n")

            # Check if the response contains Message:
            if "Message:" in content:
                # Extract the message
                message_match = re.search(r"Message:\s*(.*)", content, re.DOTALL)
                if message_match:
                    final_message = message_match.group(1).strip()
                    debug(f"Final Message: {final_message}")
                    debug(f"=== End of {persona['name']}'s analysis ===\n")

                    # Return the message to state
                    return {
                        "messages": [
                            {
                                "role": "assistant",
                                "name": persona["name"],
                                "content": f"\n[{persona['name']}]: {final_message}\n\n",
                            }
                        ]
                    }

            # Check if the response contains Action:
            if "Action:" in content:
                # Extract the action
                action_match = re.search(r"Action:\s*(\w+)", content)
                if action_match:
                    tool_name = action_match.group(1)
                    debug(f"Executing tool: {tool_name}")

                    # Execute the tool
                    observation = execute_tool(tool_name)
                    debug(f"Observation: {observation}")
                    debug("")  # Empty line for readability

                    # Add observation to internal context
                    internal_context += f"\n{content}\n\nObservation: {observation}\n"
                    continue

            # If we get here without action or message, add to context and continue
            internal_context += f"\n{content}\n"

        except Exception as e:
            print(f"Error during LLM processing: {e}")
            # Fallback response if LLM fails
            return {
                "messages": [
                    {
                        "role": "assistant",
                        "name": persona["name"],
                        "content": f"[{persona['name']}]: Unable to retrieve data at this time. Awaiting reconnection.",
                    }
                ]
            }

    # If we exhausted iterations without getting a Message, provide default
    return {
        "messages": [
            {
                "role": "assistant",
                "name": persona["name"],
                "content": f"[{persona['name']}]: Assessment pending — awaiting additional data.",
            }
        ]
    }
