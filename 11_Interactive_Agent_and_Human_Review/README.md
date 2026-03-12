# Week 11: Human-in-the-Loop Patterns

## Weekly Goals
1.  **Approval Workflow**: Build a system that pauses for human confirmation before executing "risky" actions.
2.  **Feedback Loop**: Capture user feedback (Thumbs Up/Down) to improve future responses.
3.  **Interactive Agent**: Move from "Fire-and-Forget" to "Propose-and-Review".

## Resources
- [LangGraph Human-in-the-loop](https://python.langchain.com/docs/langgraph/guides/human_in_the_loop)
- [Streamlit Documentation](https://docs.streamlit.io/) (for UI)

## Architecture: The Interactive SQL Agent

### 1. The Proposer (Risk Analyzer)
**Implemented in:** `[1.0]_risk_analyzer.py`
-   **Role**: Analyzes the generated SQL query.
-   **Logic**:
    -   `SELECT` = Low Risk (Auto-Run)
    -   `UPDATE` / `INSERT` = Medium Risk (Require Approval)
    -   `DROP` / `DELETE` = High Risk (Block or require Manager Approval)

### 2. The Reviewer (Human Interface)
**Implemented in:** `[2.0]_human_review.py`
-   **Role**: Simulates a UI (CLI/Streamlit) where the user sees the plan and types "yes/no".
-   **State**: The agent *pauses* execution and waits for input.

### 3. The Interactive Agent
**Implemented in:** `[3.0]_interactive_agent.py`
-   **Orchestrator**: Combines the SQL Agent (from Week 8) with the Risk Analyzer and Reviewer.
-   **Flow**:
    1.  User Asks -> Agent Plans SQL.
    2.  Risk Analyzer Checks SQL.
    3.  If Risky -> Pause & Ask User.
    4.  If Approved -> Execute & Learn.

## Jargon Buster

| Term | Simple Definition | Technical Context | DE Equivalent |
| :--- | :--- | :--- | :--- |
| **Human-in-the-loop (HITL)** | A human checking the work before it goes live. | Interupting the agent's execution graph to wait for input. | **Pull Request Review** / **Production Deployment Gate** |
| **Active Learning** | The AI getting smarter from your corrections. | Storing "Bad Plan -> User Correction" pairs for fine-tuning/few-shot prompts. | **Data Quality Feedback Loop** |
| **Steerability** | How easily you can guide the AI mid-task. | Providing hints ("No, filter by region") during execution. | **Interactive Debugging** |

## Experiments and Deliverables
-   [ ] **Risk Engine**: Classify SQL queries accurately (Low/Medium/High).
-   [ ] **Approval Flow**: Agent pauses on `UPDATE` query until you type "approve".
-   [ ] **Feedback Store**: log successful vs rejected queries to a JSON file.

## How to Run

### Run the Interactive Agent
This script pauses for human approval on high-risk operations.
```bash
python week11/[3.0]_interactive_agent.py
```

### Test Risk Analysis
Validate how queries are classified by risk level.
```bash
python week11/[1.0]_risk_analyzer.py
```
