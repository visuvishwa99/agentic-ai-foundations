# Multi-Agent Pipeline Monitor — Capstone Plan (Weeks 14–16+)

## Overview

| Aspect | Details |
|--------|---------|
| **Duration** | ~25 days (flexible — learning is the goal) |
| **AWS Cost** | ~$1–5 total |
| **Goal** | Production-grade multi-agent system monitoring a Lexia-style data pipeline |
| **Core Learning** | How multiple agents communicate, coordinate, and hand off work |
| **Output** | Portfolio project + demo video + interview talking points |

### Why Multi-Agent?

A single "god agent" with 15+ tools is the naive approach. It works for demos but breaks in production because:
- Context windows overflow when one agent holds everything
- Debugging is impossible — which "thought" caused the wrong action?
- You can't scale or swap parts independently

The multi-agent approach mirrors **microservice architecture** — each agent owns a domain, communicates through shared state, and can be developed/tested/replaced independently.

### The Data Engineer's Translation Table

| Data Engineering Concept | Multi-Agent Equivalent |
|:--|:--|
| Airflow DAG with tasks | LangGraph with agent nodes |
| XComs passing data between tasks | Shared state / message passing between agents |
| Sensor waiting for a file | Agent polling and handing off to next agent |
| Separate Glue jobs per stage | Specialized agent per pipeline responsibility |
| SNS/SQS between microservices | Agent-to-agent communication channels |
| BranchPythonOperator | Supervisor conditional routing |
| TriggerRule.ALL_SUCCESS | Fan-out/fan-in parallel execution |

---

## Architecture

### High-Level System Diagram

```
                    AWS (~$1-5 total)                         LOCAL (Free)
    ──────────────────────────────────────────    ─────────────────────────────────────

    ┌─────────────┐   ┌─────────────┐              ┌─────────────────────────────────┐
    │ SNS (FIFO)  │   │ SQS (FIFO)  │              │   Event Simulator               │
    │             │◀──│ + Filter    │◀─────────────│   (Python)                      │
    │ LE + pup│   │             │              │                                 │
    └──────┬──────┘   └──────┬──────┘              └─────────────────────────────────┘
           │                 │
           │                 ▼
           │          ┌─────────────┐
           │          │ EventBridge │
           │          │ Pipes       │
           │          └──────┬──────┘
           │                 │
           │                 ▼
           │          ┌─────────────┐
           │          │ Kinesis     │
           │          │ Firehose    │
           │          └──────┬──────┘
           │                 │
           │                 ▼
           │          ┌─────────────┐              ┌─────────────────────────────────┐
           │          │     S3      │─────────────▶│   PySpark (Docker)              │
           │          │ Partitioned │              │   - Reads S3                    │
           │          └─────────────┘              │   - Transforms JSON             │
           │                                       │   - Loads PostgreSQL            │
           │                                       └───────────────┬─────────────────┘
           │                                                       │
           │                                                       ▼
           │                                       ┌─────────────────────────────────┐
           │                                       │   PostgreSQL (Docker)           │
           │                                       │   - Replaces Redshift           │
           │                                       │   - Same schema + SPs           │
           │                                       └───────────────┬─────────────────┘
           │                                                       │
           ▼                                                       ▼
    ┌─────────────────────────────────────────────────────────────────────────────────┐
    │                                                                                 │
    │                        MULTI-AGENT MONITORING SYSTEM                             │
    │                                                                                 │
    │   ┌───────────────────────────────────────────────────────────────────────┐      │
    │   │                      SUPERVISOR AGENT                                 │      │
    │   │              (Orchestrator / Router / Planner)                        │      │
    │   │         Decides which agent(s) to invoke next                         │      │
    │   │         Reads shared state, determines workflow                       │      │
    │   └────────┬──────────────────┬──────────────────┬───────────────────────┘      │
    │            │                  │                  │                               │
    │            ▼                  ▼                  ▼                               │
    │   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                          │
    │   │  INGESTION   │  │  TRANSFORM   │  │   QUALITY    │                          │
    │   │    AGENT     │  │    AGENT     │  │    AGENT     │                          │
    │   │              │  │              │  │              │                          │
    │   │ Tools:       │  │ Tools:       │  │ Tools:       │                          │
    │   │ • get_sns    │  │ • run_spark  │  │ • query_pg   │                          │
    │   │ • get_sqs    │  │ • get_spark  │  │ • check_dq   │                          │
    │   │ • get_pipe   │  │   _status    │  │ • check_     │                          │
    │   │ • get_fire   │  │ • get_spark  │  │   freshness  │                          │
    │   │   hose       │  │   _metrics   │  │ • run_sp     │                          │
    │   │ • check_s3   │  │              │  │ • detect_    │                          │
    │   │ • check_     │  │              │  │   anomalies  │                          │
    │   │   errors     │  │              │  │              │                          │
    │   └──────┬───────┘  └──────┬───────┘  └──────┬───────┘                          │
    │          │                 │                  │                                  │
    │          └─────────────────┴──────────────────┘                                  │
    │                            │                                                     │
    │                            ▼                                                     │
    │                  ┌──────────────────┐                                             │
    │                  │  REPORTER AGENT  │                                             │
    │                  │                  │                                             │
    │                  │ • Summarizes all │                                             │
    │                  │   agent findings │                                             │
    │                  │ • Pattern memory │                                             │
    │                  │   (ChromaDB)     │                                             │
    │                  │ • LLM reasoning  │                                             │
    │                  │ • Alerts Slack/  │                                             │
    │                  │   Discord        │                                             │
    │                  │ • HITL gate for  │                                             │
    │                  │   critical acts  │                                             │
    │                  └──────────────────┘                                             │
    │                                                                                  │
    │   ┌──────────────────────────────────────────────────────────────────────────┐   │
    │   │                    SHARED INFRASTRUCTURE                                 │   │
    │   │  • Portable LLM Provider (Ollama / Claude API / AWS Bedrock)            │   │
    │   │  • Phoenix Tracing (observability across all agents)                     │   │
    │   │  • Pydantic Models (structured inter-agent communication)                │   │
    │   │  • Knowledge Graph (NetworkX — pipeline component lineage)               │   │
    │   └──────────────────────────────────────────────────────────────────────────┘   │
    │                                                                                  │
    └──────────────────────────────────────────────────────────────────────────────────┘
```

### Multi-Agent Communication Patterns (What You'll Learn)

| Pattern | How It Works | DE Equivalent | When Used |
|:--|:--|:--|:--|
| **Supervisor Routing** | Supervisor reads state, decides which agent runs next | `BranchPythonOperator` in Airflow | Default — most requests |
| **Sequential Handoff** | Agent A → Agent B → Agent C, each adds to shared state | Tasks in a linear DAG passing XComs | Full pipeline health check |
| **Parallel Fan-out/Fan-in** | Supervisor kicks off A + B + C simultaneously, waits for all | `TriggerRule.ALL_SUCCESS` | Urgent "check everything now" |
| **Event-driven** | S3 file lands → triggers Ingestion Agent → cascades | Airflow S3Sensor → downstream tasks | Real-time monitoring mode |

---

## Portable LLM Provider Design

A production system should never be locked to one LLM. You'll build an abstraction layer that lets you swap between providers with a single config change.

### Architecture

```python
# config.yaml
llm:
  provider: "ollama"          # Options: "ollama", "anthropic", "bedrock"
  model: "llama3.1:8b"        # Provider-specific model name
  fallback_provider: "anthropic"
  fallback_model: "claude-sonnet-4-20250514"
  temperature: 0.1
  max_tokens: 2000
```

### Provider Abstraction

```python
# agent/llm_provider.py
from abc import ABC, abstractmethod

class LLMProvider(ABC):
    """Base class — every provider implements this interface."""

    @abstractmethod
    def chat(self, messages: list[dict], tools: list[dict] = None) -> dict:
        """Send messages, get response. Handles tool calling."""
        pass

    @abstractmethod
    def get_model_name(self) -> str:
        pass

class OllamaProvider(LLMProvider):
    """Local inference via Ollama. Free, private, but slower."""
    def __init__(self, model: str = "llama3.1:8b"):
        self.model = model
        # Uses langchain_ollama.ChatOllama under the hood

class AnthropicProvider(LLMProvider):
    """Claude API. Best reasoning, costs money."""
    def __init__(self, model: str = "claude-sonnet-4-20250514"):
        self.model = model
        # Uses langchain_anthropic.ChatAnthropic

class BedrockProvider(LLMProvider):
    """AWS Bedrock. Enterprise-ready, uses IAM auth."""
    def __init__(self, model: str = "anthropic.claude-sonnet-4-20250514-v1:0"):
        self.model = model
        # Uses langchain_aws.ChatBedrock

class LLMFactory:
    """Factory pattern — create provider from config."""

    @staticmethod
    def create(config: dict) -> LLMProvider:
        provider = config["provider"]
        if provider == "ollama":
            return OllamaProvider(config["model"])
        elif provider == "anthropic":
            return AnthropicProvider(config["model"])
        elif provider == "bedrock":
            return BedrockProvider(config["model"])
        else:
            raise ValueError(f"Unknown provider: {provider}")
```

### Why This Matters (Interview Talking Point)

> "We designed the LLM layer as a portable abstraction. During development, we use Ollama locally for free iteration. For the demo, we switch to Claude for stronger reasoning. In a production AWS environment, we'd use Bedrock for IAM-native auth and compliance. One config change, zero code changes."

---

## AWS Services (Complete — Nothing Removed)

Every service from the original plan is preserved:

| Service | Purpose | Free Tier? |
|:--|:--|:--|
| **SNS (FIFO)** | `dev-uni-student-lobo-pos-progress.fifo`, `dev-uni-student-pup-progress.fifo` | Yes |
| **SQS (FIFO)** | `dev-research-le.fifo`, `dev-research-pup.fifo` with subscription filters | Yes |
| **EventBridge Pipes** | `dev_to_research_pipe`, `dev_to_research_pup_pipe` | ~$0.04 |
| **Kinesis Firehose** | `dev_to_research_firehose`, `dev_to_research_pup_firehose` | ~$0.03 |
| **S3** | `dev-lexia-research-dataimport` (partitioned by version/date/hour) | ~$0.02 |
| **CloudWatch** | Metrics + alarms ($5 cost threshold) | Free (basic) |
| **IAM** | Minimal permission roles | Free |
| **CloudFormation** | One-click infrastructure setup + teardown | Free |

### Local Services (Docker)

| Service | Purpose | Replaces |
|:--|:--|:--|
| **PostgreSQL** | Data warehouse with Lexia schema + stored procedures | Redshift |
| **PySpark** | ETL jobs reading S3, loading PostgreSQL | AWS Glue |
| **Ollama** | Local LLM inference for agent reasoning | N/A (new) |
| **ChromaDB** | Pattern memory vector store | N/A (new) |
| **Phoenix** | Observability / tracing across all agents | N/A (new) |

---

## Day-by-Day Schedule

### Phase 1: Multi-Agent Foundations (Week 14) — 9 Days

The goal of this phase is to **learn multi-agent patterns** using simple examples before wiring them to real infrastructure.

---

#### Day 1: LangGraph Multi-Agent Fundamentals

**Goal**: Understand how LangGraph wires multiple agents together through shared state.

**Learn:**
- LangGraph StateGraph with multiple nodes (each node = an agent)
- Shared state as the communication channel between agents
- Conditional edges (how the Supervisor routes work)

**Resources:**
- LangGraph multi-agent supervisor tutorial: https://langchain-ai.github.io/langgraph/tutorials/multi_agent/agent_supervisor/
- LangGraph multi-agent collaboration: https://langchain-ai.github.io/langgraph/tutorials/multi_agent/multi-agent-collaboration/

**Build:**
- Simple 3-agent demo (no real tools yet):
  - Agent A: "Checks ingestion" (returns hardcoded status)
  - Agent B: "Checks transforms" (returns hardcoded status)
  - Supervisor: Reads state, decides who runs next
- All agents share a single `PipelineState` TypedDict

**Deliverable:** `week14/[1.0]_multi_agent_basics.py`

**Jargon Buster:**

| Term | Simple Definition | Technical Context | DE Equivalent |
|:--|:--|:--|:--|
| **Shared State** | A single dict that all agents read from and write to | `TypedDict` passed through the graph | **XComs** in Airflow |
| **Supervisor** | The agent that decides which other agent runs next | Conditional routing based on state | **BranchPythonOperator** |
| **Node** | A single agent in the graph | A function that takes state, returns updated state | **Task** in an Airflow DAG |
| **Conditional Edge** | "If X, go to Agent A; if Y, go to Agent B" | `add_conditional_edges()` in LangGraph | **Trigger Rules** in Airflow |

---

#### Day 2: Shared State Design + Pydantic Models

**Goal**: Design the structured communication protocol between agents.

**Learn:**
- Pydantic models for type-safe inter-agent messages
- How to structure shared state so agents don't step on each other
- Operator.add for accumulating messages in state

**Build:**
- Pydantic models for every agent's output:
  - `IngestionReport` — SNS counts, SQS metrics, filter analysis, Firehose status, S3 partitions
  - `TransformReport` — Spark job status, rows processed, duration, errors
  - `QualityReport` — data freshness, row counts, null rates, duplicate counts, SP results
  - `PipelineHealthSummary` — combined assessment from Reporter
  - `AlertPayload` — severity, message, channel, recommended action
- Shared `PipelineState` TypedDict incorporating all models

**Deliverable:** `week14/[2.0]_state_models.py`

**Why This Matters:**
Without structured contracts between agents, you get string soup. One agent returns `"SNS looks fine"` and the next agent has to parse natural language. Pydantic models are the API contracts between your agents — same reason microservices use OpenAPI specs.

---

#### Day 3: Portable LLM Provider

**Goal**: Build the abstraction layer so reasoning works on Ollama, Claude, or Bedrock.

**Learn:**
- LangChain's `ChatOllama`, `ChatAnthropic`, `ChatBedrock` interfaces
- Factory pattern for provider selection
- Config-driven model selection (YAML)
- Fallback logic: if Ollama is slow/fails, auto-switch to Claude

**Build:**
- `LLMProvider` abstract base class
- `OllamaProvider`, `AnthropicProvider`, `BedrockProvider` implementations
- `LLMFactory.create(config)` factory
- `config.yaml` with provider settings
- Test: same prompt, same output format, three different providers

**Deliverable:** `agent/llm_provider.py`, `config.yaml`

**Test It:**
```bash
# Test with Ollama (free, local)
python agent/llm_provider.py --provider ollama --prompt "Summarize this pipeline status"

# Test with Claude (better reasoning)
python agent/llm_provider.py --provider anthropic --prompt "Summarize this pipeline status"

# Test with Bedrock (AWS-native)
python agent/llm_provider.py --provider bedrock --prompt "Summarize this pipeline status"
```

---

#### Day 4: Supervisor Agent with Routing Logic

**Goal**: Build the Supervisor that intelligently routes work to specialist agents.

**Learn:**
- How to give the Supervisor LLM context about available agents
- Routing strategies: sequential, parallel, targeted
- How the Supervisor reads state to decide what's been done vs. what's needed

**Build:**
- Supervisor Agent with tool-calling to select next agent
- Three routing modes:
  1. **Full Check**: Sequential → Ingestion → Transform → Quality → Reporter
  2. **Targeted**: User asks "Is S3 partitioning OK?" → Only Ingestion Agent
  3. **Emergency**: Parallel → All agents simultaneously → Reporter
- Supervisor prompt that explains each specialist's capabilities

**Deliverable:** `week14/[3.0]_supervisor_agent.py`

**Key Code Concept:**
```python
def supervisor_node(state: PipelineState) -> PipelineState:
    """Supervisor uses LLM to decide which agent to invoke next."""
    
    system_prompt = """You are a pipeline monitoring supervisor.
    Available agents:
    - ingestion_agent: Monitors SNS, SQS, EventBridge Pipes, Firehose, S3
    - transform_agent: Monitors Spark/Glue jobs, ETL status
    - quality_agent: Checks PostgreSQL/Redshift data quality, freshness, stored procedures
    - reporter: Summarizes all findings, sends alerts
    
    Based on the current state, decide which agent should work next.
    If all agents have reported, route to 'reporter'.
    If the task is urgent, you may route to 'PARALLEL_ALL'.
    
    Respond with exactly one of: ingestion_agent, transform_agent, quality_agent, reporter, FINISH
    """
    
    # LLM decides based on what's already in state
    response = llm.invoke([SystemMessage(system_prompt), HumanMessage(str(state))])
    return {"next_agent": response.content.strip()}
```

---

#### Day 5: Ingestion Agent (SNS → SQS → Pipes → Firehose → S3)

**Goal**: Build the specialist that owns the first half of the pipeline.

**Tools to build:**

| Tool | Purpose | AWS API |
|:--|:--|:--|
| `get_sns_metrics` | Messages published per topic | CloudWatch GetMetricData |
| `get_sqs_metrics` | Messages received, filtered, in-flight | CloudWatch GetMetricData |
| `get_sqs_filter_analysis` | Detect new event types being filtered out | SQS + sampling |
| `get_pipe_metrics` | EventBridge Pipe invocations, failures, throttles | CloudWatch GetMetricData |
| `get_firehose_metrics` | Incoming records, delivery success rate | CloudWatch GetMetricData |
| `check_firehose_errors` | Scan S3 error prefix for failed deliveries | S3 ListObjects |
| `check_s3_partitions` | Validate partitions exist for expected hours | S3 ListObjects |

**Agent behavior:**
- Receives task from Supervisor via shared state
- Runs tools to gather metrics
- Writes structured `IngestionReport` (Pydantic) back to shared state
- Flags anomalies: missing partitions, error folder growth, filter drift

**Deliverable:** `agent/tools/aws_tools.py`, `agent/ingestion_agent.py`

---

#### Day 6: Transform Agent (Spark/Glue Jobs)

**Goal**: Build the specialist that monitors ETL processing.

**Tools to build:**

| Tool | Purpose | Method |
|:--|:--|:--|
| `run_spark_job` | Trigger local PySpark ETL | subprocess / Docker exec |
| `get_spark_job_status` | Check if job succeeded/failed | Log parsing |
| `get_spark_metrics` | Rows read, rows written, duration | Log parsing |

**Agent behavior:**
- Receives task from Supervisor
- Can trigger Spark jobs if new S3 data detected (reads Ingestion Agent's report from state)
- Writes structured `TransformReport` back to shared state
- Flags: job succeeded but 0 rows, excessive duration, Spark errors

**Deliverable:** `agent/tools/spark_tools.py`, `agent/transform_agent.py`

---

#### Day 7: Quality Agent (PostgreSQL/Redshift)

**Goal**: Build the specialist that validates the final data warehouse layer.

**Tools to build:**

| Tool | Purpose | Method |
|:--|:--|:--|
| `query_postgres_freshness` | `MAX(load_timestamp)` per table | SQL query |
| `query_postgres_counts` | Row counts by date/partition | SQL query |
| `check_data_quality` | Null rates, duplicate detection, value ranges | SQL query |
| `call_stored_procedure` | Run `sp_le_student_unit_round_attempt_inc_load` | SQL execute |
| `detect_anomalies` | Compare today's counts vs 7-day average | SQL query |

**Agent behavior:**
- Reads Transform Agent's report from state (knows which tables were loaded)
- Validates data quality downstream
- Writes structured `QualityReport` back to shared state
- Flags: stale data, unexpected nulls, count anomalies, SP failures

**Deliverable:** `agent/tools/postgres_tools.py`, `agent/quality_agent.py`

---

#### Day 8: Reporter Agent (Summary + Alerting + HITL)

**Goal**: Build the agent that synthesizes all findings and takes action.

**Capabilities:**
- Reads all three reports from shared state
- Uses LLM reasoning to determine root cause across the full pipeline
- Determines alert severity: CRITICAL / WARNING / INFO
- Human-in-the-loop gate: if severity is CRITICAL, pauses for human approval before alerting
- Sends alerts via Slack webhook and/or Discord webhook
- Deduplication: doesn't spam the same error repeatedly

**HITL Pattern (from Week 11):**
```python
def reporter_node(state: PipelineState) -> PipelineState:
    # ... synthesize findings ...
    
    if alert.severity == "CRITICAL":
        # Pause execution — wait for human approval
        # In LangGraph, this uses interrupt_before or a checkpoint
        return {"pending_approval": True, "proposed_alert": alert.dict()}
    else:
        # Auto-send for WARNING and INFO
        send_alert(alert)
        return {"alert_sent": True, "final_summary": summary}
```

**Deliverable:** `agent/reporter_agent.py`, `agent/alerting.py`

---

#### Day 9: Wire All Agents into LangGraph + Test Communication

**Goal**: Assemble the full multi-agent graph and test all communication patterns.

**Build:**
- Complete `monitor_agent.py` with LangGraph StateGraph
- Wire: Supervisor → conditional edges → all 4 specialist agents
- Implement all 3 routing patterns:
  1. **Sequential**: Supervisor → Ingestion → Transform → Quality → Reporter
  2. **Targeted**: Supervisor → (one agent) → Reporter
  3. **Parallel**: Supervisor → [Ingestion + Transform + Quality] → Reporter

**Test scenarios (with mock data):**

| Scenario | Expected Flow | Expected Result |
|:--|:--|:--|
| "Full health check" | Sequential: all 4 agents | Complete summary |
| "Check S3 partitions" | Targeted: Ingestion only → Reporter | Partition status |
| "Something is broken, check everything NOW" | Parallel: all 3 → Reporter | Fast combined report |
| "Why is Redshift stale?" | Supervisor decides: Quality → Transform → Reporter | Root cause chain |

**Deliverable:** `agent/monitor_agent.py`, `tests/test_agent_communication.py`

---

### Phase 2: Real Infrastructure (Week 15) — 8 Days

Now connect the agents to real AWS services and local Docker environment.

---

#### Day 10: AWS Infrastructure (CloudFormation)

**Goal**: One-click setup of all AWS services.

**CloudFormation creates:**
- SNS Topics (FIFO): `dev-uni-student-lobo-pos-progress.fifo`, `dev-uni-student-pup-progress.fifo`
- SQS Queues (FIFO): `dev-research-le.fifo`, `dev-research-pup.fifo`
- SQS Subscription Filters (matching Lexia production filters)
- EventBridge Pipes: `dev_to_research_pipe`, `dev_to_research_pup_pipe`
- Kinesis Firehose: `dev_to_research_firehose`, `dev_to_research_pup_firehose`
- S3 Bucket: `dev-lexia-research-dataimport` (with lifecycle rules)
- IAM Roles with least-privilege permissions
- CloudWatch Alarms ($5 cost threshold)

**Commands:**
```bash
aws cloudformation deploy \
  --template-file infrastructure/template.yaml \
  --stack-name lexia-dev-pipeline \
  --capabilities CAPABILITY_IAM

# Verify
aws sns list-topics
aws sqs list-queues
aws s3 ls
```

**Deliverable:** `infrastructure/template.yaml`

---

#### Day 11: Local Docker Environment

**Goal**: PySpark + PostgreSQL + Ollama + ChromaDB + Phoenix

**docker-compose.yml creates:**

| Container | Port | Purpose |
|:--|:--|:--|
| `postgres` | 5432 | Redshift replacement with Lexia schema + stored procedures |
| `spark` | — | Glue replacement (PySpark ETL jobs) |
| `ollama` | 11434 | Local LLM inference |
| `chromadb` | 8000 | Pattern memory vector store |
| `phoenix` | 6006 | Observability dashboard |

**Init scripts:**
- `init-postgres.sql`: Creates `sns` schema, `ardw` tables, stored procedures matching Lexia production
- Shared Docker network for agent ↔ service communication

**Commands:**
```bash
docker-compose up -d
docker-compose ps

# Verify PostgreSQL
docker exec -it postgres psql -U lexia -d ardw -c "\dt sns.*"

# Verify Ollama
curl http://localhost:11434/api/tags

# Verify Phoenix
open http://localhost:6006
```

**Deliverable:** `docker-compose.yml`, `infrastructure/init-postgres.sql`

---

#### Day 12: Event Simulator + End-to-End Data Flow

**Goal**: Generate realistic events and verify they flow through the full pipeline.

**Simulator features:**
- Generates Lexia English events: `ActivityCompleted`, `LevelCompleted`, `UnitCompleted`, `PlacementCompleted`
- Generates pup events: `Boosted`, `SteppedUpToStandard`, `AssessmentCompleted`
- Configurable rate (events per minute)
- Configurable error rate (malformed events for testing)
- Matches exact Lexia event schema (JSON payloads)

**End-to-end test flow:**
```
Simulator → SNS → SQS (filtered) → EventBridge Pipes → Firehose → S3 (partitioned)
    ↓
PySpark reads S3 → transforms → loads PostgreSQL
    ↓
Stored procedures run incremental load
```

**Verification:**
```bash
# Publish 100 events
python simulator/event_simulator.py --mode batch --count 100

# Check S3 partitions
aws s3 ls s3://dev-lexia-research-dataimport/version=1.0.0/ --recursive

# Check error folder
aws s3 ls s3://dev-lexia-research-dataimport/ell_round_errors/

# Check PostgreSQL
docker exec -it postgres psql -U lexia -d ardw -c "SELECT COUNT(*) FROM sns.le_student_unit_round_attempt"
```

**Deliverable:** `simulator/event_simulator.py`, `simulator/sample_events.json`

---

#### Day 13: Spark ETL Jobs (Local Glue Replacement)

**Goal**: PySpark jobs that replicate Lexia's Glue processing.

**Jobs:**
- `etl_lexia_english.py`: Reads S3 JSON → flattens → loads `sns.le_*` tables
- `etl_pup.py`: Reads S3 JSON → flattens → loads `sns.pup_*` tables

**Spark job features:**
- Reads from S3 with partition pruning
- Schema validation before load
- Error handling with logging
- Writes metrics (rows processed, duration) to stdout for agent parsing

**Deliverable:** `spark_jobs/etl_lexia_english.py`, `spark_jobs/etl_pup.py`

---

#### Day 14-15: Connect Agents to Real Tools

**Goal**: Replace mock data with real AWS API calls and real SQL queries.

**Ingestion Agent tools → real AWS:**
- `get_sns_metrics` → `boto3.client('cloudwatch').get_metric_data()`
- `get_sqs_metrics` → `boto3.client('cloudwatch').get_metric_data()`
- `check_s3_partitions` → `boto3.client('s3').list_objects_v2()`
- `check_firehose_errors` → `boto3.client('s3').list_objects_v2(Prefix='ell_round_errors/')`

**Transform Agent tools → real Spark:**
- `run_spark_job` → `docker exec spark spark-submit ...`
- `get_spark_job_status` → parse exit code + log output

**Quality Agent tools → real PostgreSQL:**
- `query_postgres_freshness` → `psycopg2` connection, `SELECT MAX(load_timestamp)`
- `check_data_quality` → parameterized SQL queries
- `call_stored_procedure` → `cursor.callproc('sp_le_student_unit_round_attempt_inc_load')`

**Deliverable:** Updated `agent/tools/aws_tools.py`, `agent/tools/spark_tools.py`, `agent/tools/postgres_tools.py`

---

#### Day 16-17: Failure Injection + Agent Team Response

**Goal**: Simulate real failures and verify the agent team detects and diagnoses them.

**Failure scenarios to test:**

| # | Failure | How to Simulate | Expected Agent Response |
|:--|:--|:--|:--|
| 1 | **Silent Glue failure** | Spark job succeeds but processes 0 rows (empty S3 partition) | Transform Agent flags 0 rows → Reporter alerts WARNING |
| 2 | **SQS filter drift** | Publish event with new type not in filter policy | Ingestion Agent detects SNS count > SQS count → Reporter alerts WARNING |
| 3 | **Firehose error accumulation** | Publish malformed JSON events | Ingestion Agent finds objects in error prefix → Reporter alerts CRITICAL |
| 4 | **Missing S3 partitions** | Skip an hour of event publishing | Ingestion Agent detects gap in partition sequence → Reporter alerts WARNING |
| 5 | **Data quality degradation** | Insert rows with NULL required fields | Quality Agent detects null rate spike → Reporter alerts WARNING |
| 6 | **End-to-end count mismatch** | SNS says 1000, PostgreSQL says 950 | All agents contribute counts → Reporter correlates, identifies where 50 were lost |
| 7 | **Stale data** | Don't run Spark job for 6+ hours | Quality Agent detects old `MAX(load_timestamp)` → Supervisor routes to Transform Agent to check Spark → Reporter combines |

**Deliverable:** `tests/test_failure_scenarios.py`, `simulator/failure_injector.py`

---

### Phase 3: Intelligence + Production Polish (Week 16) — 10 Days

---

#### Day 18-19: Pattern Memory (ChromaDB — Not TF-IDF)

**Goal**: Agents remember past incidents and find similar historical patterns.

**Why ChromaDB instead of TF-IDF:**
You already learned proper embeddings in Week 3 and hybrid search in Week 7. TF-IDF is a regression. Use what you've built.

**Pattern Memory features:**
- Stores every incident as an embedding in ChromaDB
- Each record includes: error type, affected components, root cause, resolution, timestamp
- When a new incident occurs, searches for top-3 similar past incidents
- Returns: "This looks similar to incident X from 3 days ago, which was caused by Y and resolved by Z"
- Tracks occurrence count — recurring patterns get escalated

**Integration:**
- Reporter Agent queries pattern memory before generating summary
- Adds "historical context" section to alerts
- Over time, builds institutional knowledge of pipeline behavior

**Deliverable:** `agent/pattern_memory.py`

---

#### Day 20: Knowledge Graph (Pipeline Lineage)

**Goal**: Build a graph that agents query for root cause analysis.

**Graph structure (NetworkX):**
```
SNS_LE_Topic → SQS_LE_Queue → EventBridge_Pipe_LE → Firehose_LE → S3_LE_Partition
    → Spark_ETL_LE → PostgreSQL_le_student_unit_round_attempt → SP_inc_load

SNS_PUP_Topic → SQS_PUP_Queue → EventBridge_Pipe_PUP → Firehose_PUP → S3_PUP_Partition
    → Spark_ETL_PUP → PostgreSQL_pup_tables → SP_pup_load
```

**Agent usage:**
- Quality Agent detects stale data in table X
- Queries graph: "What are the upstream dependencies of table X?"
- Returns: `Spark_ETL_LE → S3_LE_Partition → Firehose_LE → EventBridge_Pipe_LE → SQS_LE_Queue → SNS_LE_Topic`
- Supervisor now knows to route to Ingestion Agent to check SNS/SQS, then Transform Agent to check Spark

**Deliverable:** `agent/knowledge_graph.py`

**Interview talking point:**
> "When the Quality Agent detects stale data, it doesn't just alert. It queries the pipeline knowledge graph to trace upstream dependencies, then the Supervisor routes work to the right specialist agents to diagnose where the break occurred. It's automated root cause analysis."

---

#### Day 21: Observability (Phoenix Tracing Across All Agents)

**Goal**: See the full multi-agent decision chain in a single trace.

**Setup:**
- Phoenix tracing wraps every agent node
- Each agent's tool calls are individual spans within the trace
- Supervisor routing decisions are traced
- LLM calls show input/output/tokens/latency

**What you'll see in Phoenix:**
```
Trace: "Full Health Check" (12.3s total)
├── Supervisor (0.8s) → decided: sequential
├── Ingestion Agent (3.2s)
│   ├── get_sns_metrics (0.4s)
│   ├── get_sqs_metrics (0.3s)
│   ├── check_s3_partitions (0.6s)
│   └── LLM reasoning (1.9s) → "5 events filtered, partition gap at hour 14"
├── Supervisor (0.5s) → next: transform_agent
├── Transform Agent (2.1s)
│   ├── get_spark_job_status (0.3s)
│   └── LLM reasoning (1.8s) → "Last job: 0 rows processed"
├── Supervisor (0.4s) → next: quality_agent
├── Quality Agent (2.8s)
│   ├── query_postgres_freshness (0.2s)
│   ├── check_data_quality (0.5s)
│   └── LLM reasoning (2.1s) → "Data is 6 hours stale"
├── Supervisor (0.3s) → next: reporter
└── Reporter Agent (2.2s)
    ├── pattern_memory_search (0.3s)
    ├── knowledge_graph_query (0.1s)
    └── LLM reasoning (1.8s) → CRITICAL alert generated
```

**Deliverable:** `agent/observability.py`, Phoenix dashboard screenshots

---

#### Day 22: Cost Tracking Per Agent Run

**Goal**: Know exactly how much each monitoring run costs.

**Track:**
- Tokens used per agent (input + output)
- Cost per provider (Ollama = $0, Claude = calculated, Bedrock = calculated)
- Total cost per monitoring run
- Daily/weekly cost aggregation
- Alert if daily cost exceeds budget

**Integration:**
- Each LLM call logs tokens to a cost tracker
- Reporter includes cost summary in its output
- Pydantic model: `CostReport(total_tokens, total_cost, cost_by_agent, provider_used)`

**Deliverable:** `agent/cost_tracker.py`

---

#### Day 23: End-to-End Integration Testing

**Goal**: Run the complete system and validate all scenarios work.

**Test suite:**

| Test | Method | Pass Criteria |
|:--|:--|:--|
| Full health check (happy path) | All agents report, no issues | Summary says "all healthy" |
| Silent failure detection | Inject 0-row Spark job | Transform Agent flags it |
| Filter drift detection | Publish unknown event type | Ingestion Agent detects count mismatch |
| Root cause tracing | Stale PostgreSQL data | Knowledge graph traces to S3 gap |
| Pattern memory recall | Repeat a known failure | Reporter references past incident |
| HITL gate | Trigger CRITICAL alert | System pauses for approval |
| Provider fallback | Kill Ollama mid-run | Falls back to Claude API |
| Cost tracking | Run 10 monitoring cycles | Cost report is accurate |

**Deliverable:** `tests/test_integration.py`

---

#### Day 24: Documentation + Architecture Diagrams

**Goal**: Portfolio-ready documentation.

**README.md includes:**
- Problem statement (Lexia pipeline blind spots)
- Multi-agent architecture diagram (the one from this plan)
- How agents communicate (3 patterns with diagrams)
- Portable LLM provider explanation
- Setup instructions (AWS + Docker)
- Demo walkthrough with screenshots
- Cost analysis
- Interview talking points

**Additional docs:**
- `docs/ARCHITECTURE.md` — detailed system design
- `docs/AGENT_COMMUNICATION.md` — how shared state works with code examples
- `docs/INTERVIEW_GUIDE.md` — questions and answers you can expect
- `docs/BUSINESS_VALUE.md` — why this matters to employers

**Mermaid diagrams:**
- High-level system diagram
- Agent communication flow (supervisor routing)
- Knowledge graph visualization
- Phoenix trace timeline
- Data lineage graph

**Deliverable:** `README.md`, `docs/` folder

---

#### Day 25: Demo Video + AWS Cleanup

**Goal**: Record a compelling demo and tear down AWS to save costs.

**Demo video (10-12 minutes):**

| Time | Section | Content |
|:--|:--|:--|
| 0:00–1:00 | Problem | "Silent failures in data pipelines — monitoring only catches hard failures" |
| 1:00–2:30 | Architecture | Walk through multi-agent design, explain why agents vs monolith |
| 2:30–4:00 | Agent Communication | Show the 3 patterns: sequential, targeted, parallel |
| 4:00–5:30 | Live Demo: Happy Path | Full health check — all agents report, everything healthy |
| 5:30–7:00 | Live Demo: Failure | Inject silent failure → watch agents detect, diagnose, alert |
| 7:00–8:00 | Pattern Memory | Same failure again → Reporter references past incident |
| 8:00–9:00 | Observability | Show Phoenix trace — see the full agent decision chain |
| 9:00–10:00 | Portable LLM | Switch from Ollama to Claude mid-demo — same results, better reasoning |
| 10:00–11:00 | Knowledge Graph | Show how Quality Agent traces upstream via the graph |
| 11:00–12:00 | Business Value | "Catches issues within minutes, not the next morning" |

**AWS Cleanup:**
```bash
# Delete AWS stack
aws cloudformation delete-stack --stack-name lexia-dev-pipeline

# Verify deletion
aws cloudformation describe-stacks --stack-name lexia-dev-pipeline
# Should return "Stack does not exist"

# Stop local Docker
docker-compose down -v
```

**Deliverable:** 10-12 minute demo video

---

## Directory Structure

```
multi-agent-capstone/
├── README.md
├── config.yaml                         # LLM provider config (Ollama/Claude/Bedrock)
├── docker-compose.yml
│
├── infrastructure/
│   ├── template.yaml                   # CloudFormation (all AWS services)
│   ├── init-postgres.sql               # Redshift schema + stored procedures
│   └── cleanup.sh                      # Delete AWS resources
│
├── simulator/
│   ├── event_simulator.py              # Generate Lexia English + pup events
│   ├── failure_injector.py             # Simulate specific failure modes
│   └── sample_events.json              # Example payloads
│
├── spark_jobs/
│   ├── etl_lexia_english.py            # Local Glue replacement (LE events)
│   └── etl_pup.py                  # Local Glue replacement (pup events)
│
├── agent/
│   ├── llm_provider.py                 # Portable LLM (Ollama/Claude/Bedrock)
│   ├── state_models.py                 # Pydantic models for inter-agent communication
│   ├── monitor_agent.py                # Main LangGraph multi-agent orchestrator
│   ├── supervisor_agent.py             # Supervisor routing logic
│   ├── ingestion_agent.py              # SNS/SQS/Pipes/Firehose/S3 specialist
│   ├── transform_agent.py              # Spark/Glue specialist
│   ├── quality_agent.py                # PostgreSQL/Redshift specialist
│   ├── reporter_agent.py              # Summary + alerting + HITL
│   ├── pattern_memory.py               # ChromaDB-based incident memory
│   ├── knowledge_graph.py              # NetworkX pipeline lineage graph
│   ├── alerting.py                     # Slack/Discord webhook integration
│   ├── cost_tracker.py                 # Token usage + cost per run
│   ├── observability.py                # Phoenix tracing setup
│   └── tools/
│       ├── aws_tools.py                # SNS, SQS, Firehose, S3, CloudWatch
│       ├── spark_tools.py              # PySpark job management
│       └── postgres_tools.py           # PostgreSQL queries + stored procedures
│
├── docs/
│   ├── ARCHITECTURE.md                 # Detailed system design
│   ├── AGENT_COMMUNICATION.md          # How agents talk to each other
│   ├── INTERVIEW_GUIDE.md              # Q&A prep
│   ├── BUSINESS_VALUE.md               # Why this matters
│   └── diagrams/
│       ├── system_overview.mmd         # High-level architecture
│       ├── agent_communication.mmd     # Supervisor routing flow
│       ├── knowledge_graph.mmd         # Pipeline lineage
│       └── phoenix_trace.mmd           # Observability timeline
│
└── tests/
    ├── test_agent_communication.py     # Unit tests for inter-agent messaging
    ├── test_tools.py                   # Unit tests for individual tools
    ├── test_failure_scenarios.py        # Integration tests for failure detection
    └── test_integration.py             # Full end-to-end test suite
```

---

## Cost Summary

| Item | Cost |
|:--|:--|
| SNS (free tier) | $0 |
| SQS (free tier) | $0 |
| EventBridge Pipes (~100K invocations) | ~$0.04 |
| Kinesis Firehose (~1 GB) | ~$0.03 |
| S3 (~1 GB) | ~$0.02 |
| CloudWatch (basic) | $0 |
| Local Docker (PostgreSQL, Spark, Ollama, ChromaDB, Phoenix) | $0 |
| Claude API (demo + testing, ~50 calls) | ~$1-3 |
| **Total** | **< $5 for entire project** |

---

## Skills Checklist (From Roadmap)

Every skill from your 16-week roadmap is represented:

| Roadmap Requirement | Where in Capstone |
|:--|:--|
| ✅ Multi-step agentic systems | 4 agents + Supervisor orchestration |
| ✅ Guardrails (refuses destructive actions) | Quality Agent won't execute DROP/DELETE |
| ✅ Human-in-the-loop | Reporter Agent HITL gate for CRITICAL alerts |
| ✅ Cost tracking and optimization | Cost tracker per agent run |
| ✅ Structured outputs (Pydantic) | All inter-agent communication is Pydantic models |
| ✅ Testing suite | Golden dataset + integration tests |
| ✅ Observability (traces, logs, metrics) | Phoenix tracing across all agents |
| ✅ Error handling and recovery | Provider fallback, retry logic |
| ✅ Graph RAG for lineage | NetworkX knowledge graph for root cause tracing |
| ✅ Deploy on AWS with Docker | CloudFormation + docker-compose |
| ✅ Pattern memory | ChromaDB-based incident memory |
| ✅ Tool use + function calling | Each agent has specialized tools |
| ✅ LLM reasoning | Every agent uses LLM for analysis |
| ✅ Portable providers | Ollama / Claude / Bedrock abstraction |

---

## Interview Talking Points

### The Problem
> "At Lexia, we had a 6-stage event pipeline: SNS → SQS → EventBridge Pipes → Kinesis Firehose → S3 → Glue → Redshift. The existing monitoring only caught hard failures. But we had blind spots: Glue jobs that succeeded with 0 rows, SQS filters silently dropping new event types, Firehose errors accumulating unnoticed."

### Why Multi-Agent (Not a Single Agent)
> "A single agent with 15 tools hits context window limits and is impossible to debug. I designed a multi-agent system inspired by microservice architecture: each agent owns a domain — Ingestion, Transform, Quality — and communicates through typed Pydantic models via shared state. A Supervisor agent routes work using three patterns: sequential for full checks, targeted for specific questions, and parallel for emergencies."

### How Agents Communicate
> "The agents don't call each other directly. They share a typed state object — like XComs in Airflow. The Ingestion Agent writes an IngestionReport, the Transform Agent reads it and writes a TransformReport, and the Reporter reads everything to synthesize. The Supervisor uses LLM reasoning to decide which agent works next based on what's already been checked."

### Portable LLM Design
> "The LLM layer is provider-agnostic. We use Ollama locally for free development iteration, Claude API for stronger reasoning in demos, and the system supports AWS Bedrock for production deployment with IAM-native auth. One config change, zero code changes."

### The Impact
> "The agent team catches issues that individual monitoring misses. When PostgreSQL data goes stale, the Quality Agent detects it, queries the pipeline knowledge graph to trace upstream, and the Supervisor automatically routes the Ingestion and Transform agents to diagnose where the break occurred. Instead of discovering missing data the next morning, the team gets a contextualized alert within minutes — with root cause analysis and recommended actions."