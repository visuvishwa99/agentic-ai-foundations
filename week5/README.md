# Week 5: Agentic Log Monitoring & Alerting

This directory contains a production-grade **Agentic Workflow** designed to autonomously monitor system logs, verify job statuses, and send real-time alerts via Discord.

## 📄 Scripts Overview

### `AlertingAgent.py`
This script implements a **Stateful Monitoring Agent** using **LangGraph**. Unlike simple scripts that run once from top to bottom, this agent operates in a loop: it reads logs, "thinks" about the severity, checks job health, and decides whether to alert or retry.

**Key Features:**
-   **Cyclic Graph Architecture:** Built with LangGraph to allow retries and multi-step reasoning.
-   **Tool Use (Function Calling):** The LLM has access to real tools: `read_logs`, `check_job_status`, and `post_to_discord`.
-   **Resilience:** Includes a retry counter to handle transient failures before escalating.
-   **Observability:** Integrated with **LangSmith** for full trace visibility of the agent's "thought process."

## 🏗️ Architecture Breakdown

### 1. Cyclic Graph (The Orchestration)
**Implemented in:** `AlertingAgent.py`
Unlike linear pipelines, agents often need to revisit previous steps based on tool outputs.
- **LangGraph**: Manages the state and transitions between nodes (Reasoning → Tool Execution → Condition → Reasoning).
- **DE Equivalent**: Like **Airflow or Dagster** managing a complex DAG with conditional branches (`BranchPythonOperator`) and retries.

### 2. Tool Binding (The Connectivity)
**Implemented in:** `AlertingAgent.py`
The LLM is connected to external systems to perform actions.
- **Function Calling**: The model decides *which* tool to use and *what* arguments to pass.
- **DE Equivalent**: Like a **Service Connection (Hook)** in Airflow that allows a DAG to securely connect to Snowflake, S3, or Slack.

### 3. Agent State (The Persistence)
**Implemented in:** `AlertingAgent.py`
A shared memory object that stores the context of the current run.
- **TypedDict State**: Captures `log_content`, `job_id`, and `retry_count`.
- **DE Equivalent**: Like **XComs** in Airflow or **Context** in Dagster; used to pass metadata between different tasks in a pipeline.

### 4. Router Logic (The Control Flow)
**Implemented in:** `AlertingAgent.py`
Determines whether to continue looping or terminate the run.
- **Conditional Edges**: Logic checks if the LLM called a tool or if it finalizes the response.
- **DE Equivalent**: Like a **CASE statement** in SQL or an `if-else` block in an Airflow `PythonOperator` that determines the downstream task.


---

## 📚 Jargons & Concepts

If you're moving from simple Chains to Agents, here are the key concepts used in this system:

### 1. LangGraph
1.  **Simple definition:** A library for building stateful, multi-actor applications with LLMs (Deepmind's "State Machine" for AI).
2.  **Technical context:** Used here to define the cyclic flow (`Agent -> Tools -> Retry -> Agent`), allowing the system to "loop" until the monitoring task is fully resolved.
3.  **Visual comparison:**
    *   **Linear Chain:** A -> B -> C (Run once)
    *   **LangGraph:** A <-> B (Loop until condition met)

### 2. Tools (Function Calling)
1.  **Simple definition:** Giving the AI "hands" to interact with the world (run code, call APIs).
2.  **Technical context:** Instead of just generating text, the LLM outputs a special signal to run `read_logs(service='api')`. The system runs the function and gives the result back to the AI.
3.  **Visual comparison:** *RAG* gives the AI **knowledge** (eyes); *Tools* give the AI **action capabilities** (hands).

### 3. Agent State (State Schema)
1.  **Simple definition:** The agent's "short-term memory" or clipboard that travels with it through the workflow.
2.  **Technical context:** Defined as a `TypedDict`. It persists variables like `retry_count` and `job_status` as the agent moves between "Reasoning" and "Acting" nodes.
3.  **Visual comparison:** *Prompt History* stores just the chat text; *State Schema* stores structured program variables.

### 4. Webhooks (Discord)
1.  **Simple definition:** A "digital doorbell" that lets one app instantly notify another.
2.  **Technical context:** Used to push rich-text alerts (with color-coding for severity) directly to a Discord channel without needing a bot to constantly "checks" for updates.

### 5. LangSmith Tracing
1.  **Simple definition:** A debugger/X-ray for your AI agent.
2.  **Technical context:** Because agents loop and call tools multiple times, it's hard to follow what happened. Tracing visualizes every decision, tool input, and output in a web dashboard.
