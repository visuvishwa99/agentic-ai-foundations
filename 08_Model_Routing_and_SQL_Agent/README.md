# Week 8: model routing, semantic cache, and SQL generation

I came back to this folder because I wanted routing and semantic caching to run in the same example. The router classifies the question first. The selected local model generates Snowflake SQL, and the cache stores that answer by meaning. I also kept a made-up token cost so I can test the budget logic without calling a paid API.

The SQL agent generates SQL. It does not connect to Snowflake or execute the query.

## Files

- `[1.0]_model_router.py` asks a small local model to classify a question as `SIMPLE` or `COMPLEX`.
- `[2.0]_semantic_cache.py` creates embeddings in LM Studio and stores them in an in-memory FAISS index.
- `[3.0]_sql_agent.py` ties the router, cache, SQL prompt, and cost monitor together.
- `[4.0]_cost_monitor.py` uses a synthetic price table. The numbers are for the exercise, not actual LM Studio costs.
- `lm_studio_backend.py` holds the shared chat and embedding clients.

## Setup

Start the LM Studio local server on port `1234` and load:

- `qwen2.5-coder-1.5b-instruct`
- `text-embedding-nomic-embed-text-v1.5`

Check the server:

```bash
curl http://127.0.0.1:1234/v1/models
```

Create the environment and install the packages:

```bash
uv venv .venv --python 3.11
uv pip install --python .venv/Scripts/python.exe -r 08_Model_Routing_and_SQL_Agent/requirements.txt
```

Copy `.env.example` to `.env` if I want to override the defaults.

## Run one part at a time

Router:

```bash
.venv/Scripts/python.exe "08_Model_Routing_and_SQL_Agent/[1.0]_model_router.py"
```

Semantic cache:

```bash
.venv/Scripts/python.exe "08_Model_Routing_and_SQL_Agent/[2.0]_semantic_cache.py"
```

Full SQL-agent exercise:

```bash
.venv/Scripts/python.exe "08_Model_Routing_and_SQL_Agent/[3.0]_sql_agent.py"
```

## Things I tend to forget

- A small model can classify a question incorrectly. The fallback route also chooses `COMPLEX` when parsing or inference fails.
- FAISS returns a distance, so lower scores are closer matches.
- `CACHE_THRESHOLD` changes how aggressively the cache reuses an answer.
- The cost monitor estimates tokens from string length. It is not a billing report.
- Generated SQL still needs validation before anyone executes it.
