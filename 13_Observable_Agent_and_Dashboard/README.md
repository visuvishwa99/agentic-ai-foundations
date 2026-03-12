# Week 13: LLMOps and Observability

## Weekly Goals
1.  **Observability**: Trace 100% of agent steps (Input, Tool Usage, Output, Latency).
2.  **Evaluation Pipeline**: Run a regression test suite on every change.
3.  **Dashboards**: Visualize Token Usage, Error Rates, and Latency over time.
4.  **A/B Testing**: Compare two prompt versions (e.g., "Concise" vs "Detailed").

## Resources
- [Phoenix (Arize AI)](https://docs.arize.com/phoenix/) - *Open Source Observability*
- [LangSmith](https://smith.langchain.com/) - *Hosted Tracing*
- [DeepEval](https://github.com/confident-ai/deepeval) - *Unit Testing for LLMs*

## Architecture: The Observable Agent

### 1. The Instrumented Agent
**Implemented in:** `[1.0]_observable_agent.py`
-   **Features**:
    -   Wraps the standard SQL Agent (Week 8) with **OpenInference** tracers.
    -   Exports traces to a local Phoenix server.
    -   Logs explicit metadata (user_id, session_id, environment).

### 2. The Evaluation Suite (Regression Test)
**Implemented in:** `[2.0]_regression_test.py`
-   **Role**: Runs a set of "Golden Questions" against the agent.
-   **Metrics**:
    -   **Relevance**: Did it answer the question?
    -   **Correctness**: Is the SQL valid?
    -   **Latency**: How long did it take?
-   **Output**: A pass/fail report for CI/CD.

### 3. The Dashboard Launcher
**Implemented in:** `[3.0]_dashboard.py`
-   **Role**: Starts a local Phoenix server to visualize the traces.
-   **Views**:
    -   Cluster analysis of user queries (What are people asking?).
    -   Error deep-dives (Why did 5% of queries fail?).

## Jargon Buster

| Term | Simple Definition | Technical Context | DE Equivalent |
| :--- | :--- | :--- | :--- |
| **Tracing** | Recording every step of a request (A -> B -> C). | Distributed Tracing (OpenTelemetry). | **Spark/Airflow Task Logs** |
| **Span** | A single unit of work (e.g., "Call LLM" or "Run Tool"). | A segment in a Trace. | **Stage in a Spark Job** |
| **Evaluation (Eval)** | Checking if the answer is good. | Reference-free or Reference-based grading. | **Data Quality Checks (Great Expectations)** |
| **Hallucination** | The LLM making up facts. | Factuality Metric < 0.5. | **Data Corruption** |

## Experiments and Deliverables
-   [ ] **Setup Phoenix**: Install and run the local observability server.
-   [ ] **Trace 10 Queries**: Run the agent and see the "thought process" in the UI.
-   [ ] **Run Eval Suite**: Execute 5 test cases and see the "Pass/Fail" report.

## How to Run

### Start the Observability Dashboard
This launches the local Phoenix server for trace visualization.
```bash
python week13/[3.0]_dashboard.py
```

### Run the Observable Agent
Launch the agent with instrumentation active.
```bash
python week13/[1.0]_observable_agent.py
```

### Run Regression Tests
Execute the performance and correctness test suite.
```bash
python week13/[2.0]_regression_test.py
```
