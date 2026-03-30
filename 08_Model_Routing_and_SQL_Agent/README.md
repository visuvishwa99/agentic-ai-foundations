# Week 8: Cost Management and Optimization

## Weekly Goals
1.  **Cost Tracking**: Calculate precise cost per agent run (Tokens × Price).
2.  **Semantic Caching**: Implement caching (Redis/LangChain) to reduce redundant API calls.
3.  **Model Routing**: Dynamically select models (e.g., `${MAIN_LLM}` for complex tasks, `${SMALL_LLM}` for simple ones).
4.  **Budgeting**: Set up token budgets and monitoring alerts.

## Resources
- [OpenAI Pricing](https://openai.com/pricing)
- [LangChain Caching](https://python.langchain.com/docs/integrations/llms/llm_caching)
- [LiteLLM Proxy](https://docs.litellm.ai/docs/proxy/quick_start) for cost tracking.

## Architecture: The Cost-Optimized Data Assistant

### 1. The "Budget Gatekeeper" (Router)
**Implemented in:** `[1.0]_model_router.py`
This component analyzes the complexity of the user query. If it's a simple lookup, it routes to a cheaper model (defined as `${SMALL_LLM}`). If it requires complex reasoning or SQL generation, it uses the premium model (defined as `${MAIN_LLM}`).
*   **DE Equivalent**: Like a **Load Balancer** or **Query Optimizer** that routes simple queries to a read-replica and heavy queries to the primary warehouse.

### 2. Semantic Cache (The "Memory")
**Implemented in:** `[2.0]_semantic_cache.py`
Before sending a request to *any* LLM, we check our vector database (Redis/Chroma) for similar past queries. If a match is found (above a similarity threshold), we return the cached response immediately.
*   **Technical Context**: Embeddings represent the *meaning* of the query. We check if we've answered a similar *meaning* before, not just an exact string match.
*   **DE Equivalent**: Like **Result Set Caching** in Snowflake or a **Materialized View** in a database.

### 3. The SQL Agent (The "Worker")
**Implemented in:** `[3.0]_sql_agent.py`
The core agent that translates natural language into SQL, executes it against Snowflake/DuckDB, and returns the results.
*   **DE Equivalent**: Like an **Ad-hoc Query Runner** or **BI Tool**.

### 4. Cost Monitor (The "Accountant")
**Implemented in:** `[4.0]_cost_monitor.py`
Tracks token usage for every call, calculates the cost based on the model used, and logs it. It alerts if the daily budget is exceeded.
*   **DE Equivalent**: Like **FinOps Dashboard** or **Snowflake Resource Monitor**.

## Jargon Buster

| Term | Simple Definition | Technical Context | DE Equivalent |
| :--- | :--- | :--- | :--- |
| **Semantic Caching** | Storing answers by meaning, not just keywords. | Uses vector embeddings to find "similar" questions to reuse old answers. | **Materialized View** / **Result Cache** |
| **Model Routing** | Sending easy work to cheap interns, hard work to experts. | Logic to classify query complexity and select the appropriate LLM. | **Workload Management (WLM)** queues |
| **Token Budget** | A daily spending limit for your AI. | Hard limits on token usage to prevent runaway costs/loops. | **Resource Quota** / **Compute Cap** |
| **Zero-Shot Classification** | Categorizing text without training examples. | Used by the router to decide "Simple" vs "Complex". | **Rule-based Tagging** |

## Experiments and Deliverables
-   [ ] **Baseline Run**: Measure cost of 50 queries using only `${MAIN_LLM}`.
-   [ ] **Optimized Run**: Run the same 50 queries with Caching + Routing enabled.
-   [ ] **Report**: Compare costs (Target: >50% reduction).

## How to Run

### Run the SQL Agent
This script launches the main agent with Model Routing and Semantic Caching.
```bash
python 08_Model_Routing_and_SQL_Agent/[3.0]_sql_agent.py
```

### Test Semantic Cache
Validate caching performance and cost savings.
```bash
python 08_Model_Routing_and_SQL_Agent/[2.0]_semantic_cache.py
```
