# Agentic AI Foundations

I started this repo while trying to connect the LLM material I was learning to the data engineering work I already knew. It gradually became my scratchpad for examples worth running more than once.

Each folder is its own exercise. Some are rough, and quite a few use fixtures or local services. I kept them small because I usually come back here to refresh one idea, not to run a complete platform.

## What is here

- `01_LLM_concepts` contains my notes on transformers and common LLM terms.
- `03_Vector_DBs_and_Embeddings` and `04_Document_Chunking` cover embeddings, vector search, caching, and chunking.
- `05_Alerting_Agent` is my first LangGraph tool-and-retry example.
- `06_DataOps_Memory_Agent` stores sample pipeline failures and looks for repeated patterns.
- `07_Advanced_RAG_and_Search` covers hybrid search, reranking, and structured output.
- `08_Model_Routing_and_SQL_Agent` combines model routing, an embedding cache, SQL generation, and a made-up cost ledger.
- `09_Secure_Agent_and_Guards` through `13_Observable_Agent_and_Dashboard` are later exercises around guards, lineage, human review, evaluation, and traces.
- `14_Agent_API_and_Docker` wraps an agent in a local API.
- `14_5_MCP_Client_and_Server` is a small MCP v2 client/server example built around a synthetic catalog.

`roadmap.md` has the original week-by-week learning plan. I keep it as history, so some planned items are broader than the code that exists today.

## Local models

I originally ran the local-model lessons with Ollama. When I came back to Week 8, I moved that folder to LM Studio and left the earlier lessons alone. That gives me both integrations to compare.

My current LM Studio setup loads:

- `qwen2.5-coder-1.5b-instruct` for chat and SQL generation
- `text-embedding-nomic-embed-text-v1.5` for embeddings

I run the LM Studio server on port `1234` and check it with:

```bash
curl http://127.0.0.1:1234/v1/models
```

`.env.example` contains the model names and local URL I use now.

## Python setup

I use Python 3.11 and keep the environment inside the repo:

```bash
uv venv .venv --python 3.11
```

The repository-wide dependency file is convenient but large:

```bash
uv pip install --python .venv/Scripts/python.exe -r all_requirements.txt
```

The Week 8 and MCP folders also have smaller requirement files when I only want to revise those parts.

## Tests

The default pytest run covers the deterministic repository checks and the DataOps memory tests:

```bash
.venv/Scripts/python.exe -m pytest -q
```

The local-model examples still need LM Studio or Ollama running, depending on the folder. Tests that need Phoenix, LangSmith, or another optional service should be run separately after that service is configured.

## How I use this repo

I normally pick one folder, run the smallest script, and change an input. If I cannot explain why the output changed, I am not done revising it.
