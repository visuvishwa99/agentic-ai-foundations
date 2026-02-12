# Week 7: Structured Outputs & Advanced RAG Techniques ⭐ ENHANCED

## 🎯 Weekly Goals
1. **Learn Hybrid Search**: Combine BM25 (keyword) + Semantic Search (vector) for better retrieval.
2. **Master Reranking**: Use Cohere or Cross-Encoders to re-order top-k results for relevance.
3. **Query Enhancement**: Implement HyDE (Hypothetical Document Embeddings) and query decomposition.
4. **Structured Outputs**: Ensure all agent outputs are validated using Pydantic.

## 📘 Resources
- [Weaviate Hybrid Search](https://weaviate.io/developers/weaviate/search/hybrid)
- [Cohere Reranking Guide](https://docs.cohere.com/docs/reranking)
- [LangChain Reranker Integration](https://python.langchain.com/docs/integrations/retrievers/cohere-reranker/)

## ⚙️ Project: Advanced RAG Agent for Snowflake
We will build an agent that:
1. Queries a mock Snowflake database (or real if credentials provided).
2. Uses **Hybrid Search** to find relevant schemas/documentation.
3. Applies **Reranking** to select the best context.
4. Returns results as **Structured DataFrames** validated by Pydantic.

## 📂 Structure
- `[1.0]_hybrid_search.py`: Implementation of Hybrid Search (BM25 + Chroma/FAISS).
- `[2.0]_reranking.py`: Re-ranking retrieval results using Cross-Encoders/Cohere.
- `[3.0]_query_enhancement.py`: HyDE and Query Decomposition implementation.
- `[4.0]_structured_agent.py`: Final agent integrating all components with Pydantic validation.
- `week7_architecture.mmd`: Visual diagram of the Advanced RAG pipeline.

## 🏗️ Architecture Breakdown
This pipeline is designed for high-accuracy retrieval by combining multiple optimization layers.

### 1. Query Enhancement (Pre-processing)
Before searching, we optimize the user's question to improve recall.
- **HyDE (Hypothetical Document Embeddings)**: The LLM generates a "fake" answer, and we search for documents similar to that answer.
- **Query Decomposition**: Complex questions are broken into simpler sub-queries.
- **DE Equivalent**: Like **Query Optimization** in a database; rewriting a query for efficiency before execution.

### 1. Hybrid Search (The Search Engine)
**Implemented in:** `[1.0]_hybrid_search.py`
We run two search methods in parallel to capture both intent and keywords.
- **Vector Retriever (Semantic)**: Uses embeddings for conceptual matching (e.g., "AI" matches "Machine Learning").
- **BM25 Retriever (Keyword)**: Uses traditional frequency-based matching for exact terms (e.g., specific error codes).
- **DE Equivalent**: Like a multi-index scan using both a **B-Tree index** (exact) and a **GIN/Full-Text index** (content).

### 2. Reranking (The Quality Filter)
**Implemented in:** `[2.0]_reranking.py`
Standard retrieval often returns noisy results.
- **Cross-Encoder / Cohere**: Scores the actual relevance of each `(Query, Document)` pair to filter out the noise.
- **DE Equivalent**: Like applying a `RANK()` window function to filter for only the `Top-K` highest probability rows.

### 3. Generation & Validation (The Output)
**Implemented in:** `[3.0]_structured_output.py`
We enforce strict schemas on the LLM output.
- **Pydantic Validation**: Forces the LLM to output valid JSON matching our schema.
- **DE Equivalent**: Like a **Data Quality Check (Great Expectations)**; if the output violates the schema, we trigger a retry.

### 4. Advanced RAG Agent (The Orchestrator)
**Implemented in:** `[4.0]_rag_agent.py`
Combines all previous steps into a single autonomous pipeline.
- **Orchestration**: Manages the flow from Search -> Rerank -> Generate.
- **DE Equivalent**: Like an **Airflow DAG** that chains multiple tasks (Extract, Transform, Load) into a coherent workflow.


## 🛠️ Tech Stack
- **Framework**: LangChain / LangGraph
- **Vector DB**: ChromaDB / FAISS
- **Search**: BM25Retriever (Keyword), VectorStoreRetriever (Semantic)
- **Reranking**: HuggingFace CrossEncoder / Cohere
- **Validation**: Pydantic
