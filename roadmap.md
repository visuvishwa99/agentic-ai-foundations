
**Goal**: Transition from Data Engineering to Agentic AI Engineering with deep RAG expertise, MCP integration, and production-grade systems.

-----

## Phase 1: LLM & AI Foundations (Weeks 1-4)

### **Week 1 -- Transformer Architecture & LLM Fundamentals**

**Learn:**

- How LLMs work: tokenization, embeddings, transformer data flow
- Key LLM jargons: vectors, embeddings, softmax, logits, KV cache, backpropagation, cross-entropy loss, perplexity
- Attention mechanism (Q, K, V), multi-head attention, residual connections, LayerNorm

**Resources:**

- Karpathy's "Let's build GPT from scratch"
- Illustrated Transformer by Jay Alammar

**Content:**

- `Transformer Architecture.md`: Full architecture analysis with Mermaid diagram of data flow (Tokenization -> Embedding -> LayerNorm -> MultiHead Attention -> Residual -> FFN -> Output Head)
- `LLM Jargons.md`: 14 key concepts explained with examples (Vectors, Embeddings, ReLU, Softmax, Logits, KV Cache, MLP, Backpropagation, Dot Product, Cross-Entropy Loss, Perplexity, and more)

-----

### **Week 2 -- Prompt Engineering + Structured Outputs**

**Status:** Planned (no content yet)

**Learn:**

- Prompt design patterns: few-shot, ReAct, chain-of-thought, function calling
- **JSON mode and structured outputs**
- **Pydantic for output validation**

**Project:**

- Build an LLM-powered Databricks log analyzer
- Must return structured JSON output with Pydantic validation
- Add error handling for API failures

-----

### **Week 3 -- Embeddings & Retrieval**

**Learn:**

- Embeddings, cosine similarity, vector search
- Tools: FAISS, ChromaDB
- Semantic caching concepts
- RAG pipeline fundamentals

**Content:**

- `[1.1]_Cosine_Similarity.py`: Measuring semantic distance between text blocks
- `[1.2]_Embeddings.py`: Transforming text into high-dimensional vectors
- `[1.3]_vector.py`: Core vector representation logic
- `[2.1]_FAISS.py`: High-performance similarity search using Facebook AI Similarity Search
- `[2.2]_chromeDB.py`: Local vector storage using ChromaDB
- `[3.1]_semantic_cache.py`: Intercepts queries to reduce costs via semantic caching
- `[4.1]_capstone_RAG.py`: Complete "Talk to your Data" RAG pipeline using Ollama

**Tech Stack:** Python 3.10+, LangChain, sentence-transformers, Qwen 2.5 Coder (Ollama), ChromaDB, FAISS

-----

### **Week 4 -- Advanced Chunking & Document Parsing**

**Learn:**

- Chunking strategies: element-aware, table preservation, overlap
- Advanced document parsing with Unstructured.io and LlamaParse
- Chunk quality validation and scoring
- Contextual boosting for retrieval optimization

**Content:**

- `[0.1]_chunk_system.py`: Base chunking logic with validation and quality scoring
- `[0.0]_chunk_system.mmd`: Architecture diagram for chunking system
- `[1.1]_advancedchunkingsystem.py`: Element-aware chunking with table preservation and relevance boosting
- `[1.0]_advance_chunk.mmd`: Architecture diagram for advanced chunking

**Key Concepts:** Chunk size/overlap, Unstructured.io partitioning, sentence transformers, cosine similarity, top-K retrieval, relevance boosting, Markdown table formatting

-----

## Phase 2: Agentic Thinking & Tool Use (Weeks 5-8)

### **Week 5 -- Agentic Log Monitoring & Alerting**

**Learn:**

- What makes an "agent": reasoning loop, tool use, state
- LangGraph for cyclic graph workflows (Agent -> Tools -> Retry -> Agent)
- Tool binding (function calling): LLM decides which tool to call and with what arguments
- Agent state management with TypedDict
- Observability with LangSmith tracing

**Project:**

- Alerting Agent: reads logs -> checks job status -> posts to **Discord** via webhooks
- Cyclic graph architecture with retry logic and conditional edges
- Full trace visibility of agent reasoning

**Content:**

- `AlertingAgent.py`: Stateful monitoring agent using LangGraph with Discord alerting
- `AlertingAgent.mmd`: Architecture diagram

-----

### **Week 6 -- Memory & State + Testing Fundamentals**

**Learn:**

- Short-term (contextual) and long-term (vector) memory
- TF-IDF vectorization for semantic search of past failures
- Error classification and pattern recognition
- Agent testing with golden datasets

**Project:**

- DataOps Memory Agent: remembers pipeline failures, detects patterns, generates remediation suggestions
- Vector-based semantic memory with TF-IDF embeddings
- Error classification into 6+ types (schema, timeout, data quality, permission, connection, resource)
- Test suite with 10 golden test cases (96.7% overall accuracy)

**Content:**

- `dataops_memory_agent.py`: Core agent with vector memory, classification, pattern detection, and suggestion engine
- `demo_agent.py`: Interactive demo with 4 scenarios (schema drift, data quality crisis, performance degradation, weekly report)
- `test_agent.py`: Golden dataset test suite (100% classification, 90% pattern detection)
- `generate_metrics.py`: Metrics generation for analysis
- `dashboard.html`: Visual dashboard
- `DataOpsMemoryAgent.mmd`: Architecture diagram

-----

### **Week 7 -- Structured Outputs & Advanced RAG Techniques**

**Learn:**

- **Hybrid search**: BM25 (keyword-based, fast) + Semantic Search (vector-based)
- **Reranking**: Cross-encoders and Cohere for re-ordering top-K results
- **Query enhancement**: HyDE (Hypothetical Document Embeddings), query decomposition
- Pydantic for structured agent output validation

**Resources:**

- Weaviate hybrid search docs
- Cohere reranking guide

**Project:**

- Advanced RAG Agent for Snowflake with hybrid search, reranking, and structured DataFrames

**Content:**

- `[1.0]_hybrid_search.py`: BM25 + Chroma/FAISS hybrid search implementation
- `[2.0]_reranking.py`: Cross-encoder/Cohere re-ranking of retrieval results
- `[3.0]_structured_output.py`: Pydantic-validated structured outputs
- `[4.0]_rag_agent.py`: Final agent integrating all components
- `week7_architecture.mmd`: Advanced RAG pipeline diagram

-----

### **Week 8 -- Cost Management & Optimization**

**Learn:**

- Calculate cost per agent run (tokens x price)
- Semantic caching (Redis, LangChain cache)
- Model routing: dynamically select cheap vs premium models based on query complexity
- Token budgets and monitoring alerts

**Project:**

- "Data Assistant Agent": natural language -> SQL -> Snowflake -> insights
- Model router (Budget Gatekeeper), semantic cache, SQL agent, cost monitor

**Content:**

- `[1.0]_model_router.py`: Complexity-based model routing (cheap model for simple queries, premium for complex)
- `[2.0]_semantic_cache.py`: Vector-based semantic caching to reduce redundant API calls
- `[3.0]_sql_agent.py`: Core SQL agent translating natural language to SQL
- `[4.0]_cost_monitor.py`: Token usage tracking, cost calculation, and budget alerts
- `week8_architecture.mmd`: Cost-optimized architecture diagram

**Deliverable:** Cost optimization report (target: >50% reduction via caching + routing)

-----

## Phase 3: Data-Aware Agents with Safety (Weeks 9-12)

### **Week 9 -- Guardrails & Safety**

**Learn:**

- Prompt injection attacks and defenses
- NeMo Guardrails, Guardrails AI, OWASP Top 10 for LLMs
- PII detection and data masking
- Input guard (pre-LLM) and output guard (post-LLM) patterns

**Project:**

- Secure SQL Agent with layered guardrails
- Input guard: blocks jailbreaks, masks PII
- Output guard: rejects destructive SQL (DROP, TRUNCATE), validates syntax

**Content:**

- `[1.0]_input_guard.py`: Input inspection for jailbreak attempts, malicious intent, PII
- `[2.0]_output_guard.py`: SQL/code inspection for destructive commands and authorized schemas
- `[3.0]_secure_agent.py`: Integrated secure agent workflow
- `week9_architecture.mmd`: Secure agent architecture diagram

-----

### **Week 10 -- Data Integration & Graph RAG**

**Learn:**

- Graph RAG: structural understanding beyond vector similarity
- Knowledge graphs from documents: nodes (tables, columns), edges (SELECTS_FROM, JOINS_WITH, LOADS_INTO)
- Data lineage mapping and dependency tracking
- NetworkX for lightweight graph modeling

**Resources:**

- Microsoft GraphRAG paper
- Neo4j + LangChain integration

**Project:**

- Graph RAG Agent: "Which upstream table affects this dashboard?"
- LLM-powered entity extraction from SQL/dbt files
- Visual lineage graph generation

**Content:**

- `[1.0]_lineage_mapper.py`: LLM-based entity extraction from SQL/dbt (nodes and edges)
- `[2.0]_graph_builder.py`: Directed graph (DAG) construction with NetworkX
- `[3.0]_graph_agent.py`: Agent with graph traversal tool for upstream/downstream dependency queries
- `lineage_graph.html`: Visual graph output
- `graph_data.json`: Graph data store
- `sql/`: Sample SQL files for lineage extraction
- `week10_architecture.mmd`: Lineage agent architecture diagram

-----

### **Week 11 -- Human-in-the-Loop Patterns**

**Learn:**

- Approval workflows (agent proposes -> human confirms -> executes)
- Risk-based classification: SELECT (auto-run), UPDATE/INSERT (require approval), DROP/DELETE (block)
- Feedback loops for model improvements

**Project:**

- Interactive SQL Agent with risk-based approval gates
- Extends Week 8 SQL Agent with Risk Analyzer and Human Review

**Content:**

- `[1.0]_risk_analyzer.py`: SQL risk classification (Low/Medium/High)
- `[2.0]_human_review.py`: Simulated human approval interface (CLI/Streamlit)
- `[3.0]_interactive_agent.py`: Orchestrator combining SQL Agent + Risk Analyzer + Reviewer
- `week11_architecture.mmd`: Interactive agent architecture diagram

-----

### **Week 12 -- Self-Evaluation & Red Team Week**

**Learn:**

- Red teaming: adversarial testing of AI agents
- Self-correction loops (generate -> self-critique -> regenerate)
- Common agent failures: hallucination, tool errors, context overflow, infinite loops

**Project:**

- Red team attack suite and automated evaluation
- Self-correcting agent with safety check loop

**Content:**

- `[1.0]_red_teamer.py`: Automatic adversarial prompt generation
- `[2.0]_evaluator.py`: Attack scoring (refusal rate, safety score)
- `[3.0]_self_correcting_agent.py`: Response -> critique -> regenerate pipeline
- `week12_architecture.mmd`: Resilient agent architecture diagram

-----

## Phase 4: Production Systems & Advanced Topics (Weeks 13-14.5)

### **Week 13 -- LLMOps & Observability**

**Learn:**

- Observability: trace 100% of agent steps (input, tool usage, output, latency)
- Evaluation pipelines: regression testing with golden questions
- Dashboards: Token usage, error rates, latency
- A/B testing for prompts

**Resources:**

- Phoenix (Arize AI) - Open source observability
- LangSmith - Hosted tracing
- DeepEval - Unit testing for LLMs

**Content:**

- `[1.0]_observable_agent.py`: SQL agent wrapped with OpenInference tracers, exports to Phoenix
- `[2.0]_regression_test.py`: Golden question test suite (relevance, correctness, latency)
- `[3.0]_dashboard.py`: Local Phoenix server for trace visualization and cluster analysis
- `week13_architecture.mmd`: Observable agent architecture diagram

-----

### **Week 14 -- Serving & API Deployment**

**Learn:**

- API layer with FastAPI (Pydantic models, async endpoints, Swagger UI)
- Concurrency: handling multiple requests without blocking
- Basic API key authentication
- Dockerization for production deployment

**Project:**

- Agent Microservice: wrapping the Observable Agent (Week 13) in an HTTP API

**Content:**

- `[1.0]_agent_api.py`: FastAPI server with `POST /chat` endpoint, Swagger docs, background logging
- `[2.0]_api_client.py`: Client simulator for concurrency testing
- `[3.0]_docker_example.md`: Dockerfile instructions for container deployment
- `week14_architecture.mmd`: Agent microservice architecture diagram

-----

### **Week 14.5 -- Model Context Protocol (MCP)**

**What is MCP?**

- Anthropic's protocol for connecting AI systems to external context
- Enables agents to access files, repos, databases, APIs dynamically
- Think of it as "USB-C for AI apps" (standardized tool/context exchange)

**Learn:**

- MCP fundamentals and architecture (Client, Host, Server)
- Transport mechanisms: `stdio` (pipe) and `SSE` (HTTP)
- Integration with Claude Desktop, Cursor IDE

**Resources:**

- Anthropic MCP documentation: <https://modelcontextprotocol.io>
- MCP Python SDK: <https://github.com/modelcontextprotocol/python-sdk>
- [Smithery.ai](http://Smithery.ai) MCP catalog

**Content:**

- `[1.0]_mcp_client.py`: Automated agent client that launches server and performs tasks (list resources, read catalog, query data)
- `[2.0]_mcp_server.py`: Custom MCP server exposing tools (`list_files`, `read_file`, `query_db`) via `stdio`
- `[3.0]_inspector.py`: MCP Inspector for debugging server availability (requires Node.js)
- `week14_5_architecture.mmd`: MCP architecture diagram

**Note:** `[2.0]_mcp_server.py` uses `stdio` communication and should NOT be run directly. It is launched by the client or inspector.

-----

## Phase 5: Capstone (Weeks 15-16) -- Planned

### **Week 15 -- Streaming Data & Production Integration**

**Status:** Planned (no content yet)

**Learn:**

- Kafka integration with agents
- Real-time data processing
- **Optional**: Fine-tuning basics (when to use vs RAG)

**Project:**

- Streaming Log Analyzer: listens to error topics -> summarizes -> alerts
- Compare RAG vs fine-tuning for your use case

-----

### **Week 16 -- Capstone Project**

**Status:** Planned (no content yet)

**Build: Production Agentic DataOps Platform**

**Core Features:**

- Monitors Kafka / Snowflake / Databricks jobs
- Detects anomalies or delays
- Queries metadata via **Graph RAG** and **MCP**
- Understands data lineage
- Triggers remediation (restart, alert, Jira ticket)

**Production Requirements:**

- Full observability (traces, logs, metrics)
- Guardrails (refuses destructive actions)
- Human-in-the-loop for critical decisions
- Cost tracking and optimization
- Comprehensive testing suite (RAGAS)
- Structured outputs with Pydantic validation
- Error handling and recovery
- **MCP integration** for contextual awareness
- **Graph RAG** for lineage queries
- Deployed on AWS/Databricks with CI/CD

**Deliverables:**

1. GitHub repo with documentation
1. Architecture diagram (include MCP and Graph RAG)
1. Demo video (10 minutes)
1. Cost analysis and performance metrics
1. Blog post: "Building a Production Agentic DataOps Platform"

-----

## Tech Stack

|**Area**            |**Tools**                                   |
|--------------------|-------------------------------------------|
|**LLMs**            |OpenAI GPT-4o, Claude 3.5, Llama 3.1 (local), Qwen 2.5 Coder (Ollama)|
|**Frameworks**      |LangGraph, LangChain, LlamaIndex           |
|**Memory**          |ChromaDB, FAISS, pgvector, Redis            |
|**Data**            |Databricks, Snowflake, Kafka               |
|**Document Parsing**|Unstructured.io, LlamaParse, Docling       |
|**Graph**           |Neo4j, NetworkX (Graph RAG)                |
|**MCP**             |Anthropic MCP SDK, custom servers          |
|**Validation**      |Pydantic, JSON Schema                      |
|**Safety**          |Guardrails AI, NeMo Guardrails             |
|**Testing**         |RAGAS, TruLens, DeepEval, pytest           |
|**Observability**   |LangSmith, Phoenix (Arize), Langfuse       |
|**Deployment**      |FastAPI, Docker, AWS Lambda/ECS/Bedrock    |
|**Orchestration**   |Airflow, Prefect                           |
|**Monitoring**      |Arize AI, Weights & Biases                 |
|**Versioning**      |GitHub, MLflow                             |

-----

## Additional Learning Resources

### **For Document Parsing (Week 4):**

- [Unstructured.io](http://Unstructured.io) docs: <https://unstructured.io>
- LlamaParse tutorials: <https://docs.llamaindex.ai/en/stable/module_guides/loading/simpledirectoryreader.html>

### **For Graph RAG (Week 10):**

- Microsoft GraphRAG: <https://github.com/microsoft/graphrag>
- Neo4j + LangChain: <https://neo4j.com/labs/genai-ecosystem/langchain/>

### **For MCP (Week 14.5):**

- Official docs: <https://modelcontextprotocol.io>
- MCP servers catalog: <https://smithery.ai>
- Building MCP servers: <https://github.com/anthropics/mcp/tree/main/examples>

### **For Hybrid Search (Week 7):**

- Weaviate hybrid search: <https://weaviate.io/developers/weaviate/search/hybrid>
- Cohere reranking: <https://docs.cohere.com/docs/reranking>

-----

## Progress Summary

| Week | Topic | Status |
|------|-------|--------|
| 1  | Transformer Architecture & LLM Fundamentals | Done |
| 2  | Prompt Engineering + Structured Outputs | Planned |
| 3  | Embeddings & Retrieval | Done |
| 4  | Advanced Chunking & Document Parsing | Done |
| 5  | Agentic Log Monitoring & Alerting | Done |
| 6  | Memory & State + Testing Fundamentals | Done |
| 7  | Structured Outputs & Advanced RAG | Done |
| 8  | Cost Management & Optimization | Done |
| 9  | Guardrails & Safety | Done |
| 10 | Data Integration & Graph RAG | Done |
| 11 | Human-in-the-Loop Patterns | Done |
| 12 | Self-Evaluation & Red Team Week | Done |
| 13 | LLMOps & Observability | Done |
| 14 | Serving & API Deployment | Done |
| 14.5 | Model Context Protocol (MCP) | Done |
| 15 | Streaming Data & Production Integration | Planned |
| 16 | Capstone Project | Planned |
