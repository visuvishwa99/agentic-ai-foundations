# Revision map

This file replaces the original week-by-week plan. That plan was useful when I started, but it mixed finished exercises, ideas, and production goals as if they were the same thing.

## Foundation notes

- `01_LLM_concepts`: transformer flow and terminology
- `03_Vector_DBs_and_Embeddings`: vectors, FAISS, ChromaDB, semantic cache, basic RAG
- `04_Document_Chunking`: chunk size, overlap, element-aware parsing, table handling

## Agent exercises

- `05_Alerting_Agent`: LangGraph state, tools, retries, optional Discord notification
- `06_DataOps_Memory_Agent`: failure memory, TF-IDF retrieval, deterministic classification tests
- `07_Advanced_RAG_and_Search`: BM25, vector search, reranking, structured output
- `08_Model_Routing_and_SQL_Agent`: LM Studio model routing, embeddings, FAISS cache, SQL generation
- `09_Secure_Agent_and_Guards`: PII masking and basic input/output checks
- `10_Graph_Agent_and_Lineage`: SQL lineage fixture, NetworkX graph, upstream/downstream traversal
- `11_Interactive_Agent_and_Human_Review`: risk labels and terminal approval
- `12_Self_Correcting_Agent_and_Eval`: adversarial prompts, simple evaluator, retry loop
- `13_Observable_Agent_and_Dashboard`: optional Phoenix tracing and model checks
- `14_Agent_API_and_Docker`: local FastAPI wrapper
- `14_5_MCP_Client_and_Server`: MCP Python SDK v2 client/server with a synthetic catalog

## Current local setup

Week 8 uses LM Studio:

```text
qwen2.5-coder-1.5b-instruct
text-embedding-nomic-embed-text-v1.5
```

Older lessons still use Ollama. I have not migrated them because comparing the two integrations is useful when I revise the code.

## Gaps worth revisiting

- Replace SQL keyword filters with parser-based validation and a read-only execution role.
- Separate deterministic unit tests from live model and service checks.
- Add module-specific requirement files when I revisit older folders.
- Test retrieval changes against a fixed dataset instead of judging a few examples by eye.
- Remove more dynamic-import coupling between weeks.

I am not treating these as a delivery roadmap. They are reminders for the next revision session.
