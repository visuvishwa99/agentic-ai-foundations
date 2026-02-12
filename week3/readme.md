# AI Engineering - Week 3: Embeddings & Retrieval

This project explores the foundations of modern AI applications, focusing on how text is represented as vectors (embeddings) and how those vectors are used for semantic search, caching, and Retrieval-Augmented Generation (RAG).

## 🗺️ System Architecture
The following diagram illustrates the workflow from user query to cached results or a full RAG pipeline:

```mermaid
[Refer to week3_architecture.mmd]
```

## 🚀 Key Components (Sorted)

### 1. Vector Foundations
- **`[1.1]_Cosine_Similarity.py`**: Measuring the semantic distance between two blocks of text.
- **`[1.2]_Embeddings.py`**: Transforming text into high-dimensional numerical arrays.
- **`[1.3]_vector.py`**: Core logic for vector representation.

### 2. Vector Databases
- **`[2.1]_FAISS.py`**: High-performance similarity search using Facebook AI Similarity Search.
- **`[2.2]_chromeDB.py`**: Implementing local vector storage using ChromaDB.

### 3. Semantic Caching
- **`[3.1]_semantic_cache.py`**: Intercepts queries to reduce costs and latency by reusing similar previous answers.

### 4. Capstone: RAG Pipeline
- **`[4.1]_capstone_RAG.py`**: A complete "Talk to your Data" implementation using Ollama and retrieved context.

## 🛠️ Tech Stack
- **Language**: Python 3.10+
- **Frameworks**: LangChain, sentence-transformers
- **Models**: Qwen 2.5 Coder (via Ollama)
- **Vector DB**: ChromaDB, FAISS

## 📦 Installation
```bash
pip install -r requirements.txt
```