# Week 7: hybrid retrieval and structured output

This folder separates a RAG pipeline into search, reranking, output validation, and orchestration examples.

## Files

- `[1.0]_hybrid_search.py` combines BM25 scores with embedding search.
- `[2.0]_reranking.py` reranks retrieved documents.
- `[3.0]_structured_output.py` parses model output with Pydantic.
- `[4.0]_rag_agent.py` combines the earlier steps.

The examples use small fixtures and local models. References to Snowflake describe the intended use case; the code does not query a Snowflake account.

## Run

```bash
python "07_Advanced_RAG_and_Search/[1.0]_hybrid_search.py"
python "07_Advanced_RAG_and_Search/[4.0]_rag_agent.py"
```

## Notes for revision

Hybrid search needs an explicit score-normalization rule because BM25 and vector scores are not naturally comparable. Reranking should be evaluated separately from first-stage retrieval.
