# Multi-Agent AI System: Smart City Emergency Response Team

## 1. Project Overview
This project implements a coordinated **Multi-Agent AI System** designed to manage urban emergencies in Singapore. By simulating a professional emergency operations center, the system automates the workflow from initial incident reporting to final safety assessment.

Unlike a standard chatbot, this system employs a **Sequential Orchestration** mechanism. It guides the conversation through three specialized AI agents, each possessing unique personas and restricted tool access to ensure a structured and professional response to high-pressure scenarios like flash floods or major traffic accidents.

### Objective
To demonstrate how multiple autonomous agents can collaborate to solve complex, real-world problems by sharing state and delegating tasks based on expertise.

---

## 2. Agentic AI Architecture
The system is built on **LangGraph**, utilizing a state-driven directed acyclic graph (DAG) to manage the flow of information.

### Agent Personas & Capabilities
| Agent | Role & Responsibility | Tool Access |
| :--- | :--- | :--- |
| **Field Dispatcher** | Initial incident verification and priority determination. | `singapore_traffic` |
| **Traffic Controller** | Analyzing road conditions and formulating diversion plans. | `singapore_weather` |
| **Safety Analyst** | Synthesizing all data into a comprehensive risk assessment. | `singapore_time` |

### Coordination Mechanism
* **Sequential Flow**: The system follows a predefined `RESPONSE_SEQUENCE`: Dispatcher $\rightarrow$ Traffic Controller $\rightarrow$ Safety Analyst.
* **ReAct Logic**: Each agent operates within a **Thought-Action-Observation** loop, ensuring they only provide information based on actual tool outputs rather than hallucinated data.
* **State Management**: A shared `State` object tracks the `messages` history and a `volley_msg_left` counter to manage the conversation lifecycle.



---

## 3. Technical Requirements
* **Framework**: LangGraph, LangChain
* **LLM**: OpenAI `gpt-4o-mini` (configured with `temperature=1`)
* **Environment**: Python 3.10+
* **External APIs**: 
    * **LTA DataMall**: For real-time traffic incidents.
    * **Data.gov.sg**: For real-time weather (temperature, rainfall, etc.).

---

## 4. Setup Instructions
### Step 1: Install Dependencies
```bash
uv sync
```

### Step 2: Configure Environment Variables
You must set your API keys as environment variables.
```bash
fill the environment variables according to .env.example
```

### Step 3: Run the System
```bash
uv run python main.py
```

---

## 5. Implementation Details
* **Tool Access Control**: Implemented via a `PERSONAS` configuration map. The `participant` function dynamically restricts which tools the LLM can "see" and "call" based on the active `persona_id`.
* **Stateful Summarization**: Once the coordination sequence is complete, a specialized `summarizer` node processes the entire message history to generate a structured "Final Assessment Report".

---

## 6. Project Demo
**Example Input**: *"There is a major accident on the PIE near Eunos exit, and it's raining heavily."*

**Expected Output**:
1.  **Dispatcher**: Fetches real-time traffic data from LTA.
2.  **Controller**: Checks NEA weather stations for rainfall intensity.
3.  **Analyst**: Checks the time (peak hour vs. off-peak) and issues a risk rating.
4.  **Summary**: A formal Emergency Response Report.