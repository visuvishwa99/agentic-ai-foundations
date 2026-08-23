# Week 3: embeddings and retrieval

This folder is where I worked through vectors before moving into larger RAG examples. The scripts are independent exercises rather than one application.

## Files

- `[1.1]_Cosine_Similarity.py` compares text with cosine similarity.
- `[1.2]_Embeddings.py` creates embeddings.
- `[1.3]_vector.py` combines an embedding model with a local LLM.
- `[2.1]_FAISS.py` uses a local FAISS index.
- `[2.2]_chromeDB.py` stores vectors in ChromaDB. The filename has the original typo and is kept to avoid breaking old notes.
- `[3.1]_semantic_cache.py` reuses an answer when a new question is close enough to a cached question.
- `[4.1]_capstone_RAG.py` retrieves context and sends it to a local model.

The older examples use Ollama and `qwen2.5-coder:1.5b`. They have not been moved to the LM Studio backend used in Week 8.

## Run

Install the repository dependencies, start Ollama, then run one script from the repository root:

```bash
python "03_Vector_DBs_and_Embeddings/[2.1]_FAISS.py"
python "03_Vector_DBs_and_Embeddings/[3.1]_semantic_cache.py"
python "03_Vector_DBs_and_Embeddings/[4.1]_capstone_RAG.py"
```

## Notes for revision

Cosine similarity and L2 distance move in opposite directions: higher cosine similarity is closer, while lower L2 distance is closer. Cache thresholds only make sense when the distance metric is known.
