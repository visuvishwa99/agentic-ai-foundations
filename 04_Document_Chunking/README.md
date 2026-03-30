# Week 4: Advanced Chunking and Document Parsing

This directory contains scripts demonstrating advanced techniques for document processing and retrieval-augmented generation (RAG).

## Scripts Overview

### `advancedchunkingsystem.py`
This script demonstrates an **Enhanced Chunking Strategy** that goes beyond simple text splitting. It uses structured parsing to handle different document elements (like tables and images) uniquely, ensuring that context is preserved where it matters most.

**Key Features:**
- **Element-Aware Chunking:** Intelligently handles Tables, Images, and Narrative Text.
- **Table Preservation:** Converts tables to Markdown to maintain their semantic structure for better RAG performance.
- **Contextual Retrieval:** Uses sentence embeddings to find relevant chunks and applies "boosts" to specific types (like tables) when the query asks for data.

## Architecture Breakdown

### 1. Advanced Parsing (Multi-Modal Ingestion)
**Implemented in:** `[1.1]_advancedchunkingsystem.py`
Instead of treating a document as an blob of text, we identify its constituent parts.
- **LlamaParse/Unstructured**: Extracts specialized elements like **Tables**, **Headers**, and **Images**.
- **DE Equivalent**: Like an **ETL Ingestion Framework** that handles different source formats (Parquet, Avro, JSON) and extracts structured schemas from them.

### 2. Element-Aware Chunking (Transformation)
**Implemented in:** `[0.1]_chunk_system.py`
We apply different rules based on the element type.
- **Table Handling**: Tables are converted to Markdown/JSON to preserve row-column relationships.
- **Narrative Text**: Chunks are split at sentence boundaries to maintain context.
- **DE Equivalent**: Like **Data Partitioning** where you split data into partitions (e.g., by Date or Region) to optimize query performance and maintain logical grouping.

### 3. Chunk Validation & Scoring (Quality Assurance)
**Implemented in:** `[0.1]_chunk_system.py`
We evaluate the quality of our segments before indexing.
- **Chunk Quality Engine**: Measures if a chunk has enough information or if it's just "noise."
- **DE Equivalent**: Like **Data Quality Hooks (DQ Checks)** that validate schema integrity and business rules before data reaches the warehouse.

### 4. Contextual Boosting (Retrieval Optimization)
**Implemented in:** `[1.1]_advancedchunkingsystem.py`
We help the system find the *right* kind of data.
- **Relevance Boosting**: If a query looks for numerical data, we boost the score of "Table" elements.
- **DE Equivalent**: Like a **Predicated Pushdown** or **Index HINT** that tells the database engine to prioritize specific partitions for faster data retrieval.


---

## 📚 Jargons & Concepts

If you're new to the world of LLMs and RAG, here are the key terms used in this system:

### 1. Chunking
The process of breaking down a large document into smaller, manageable pieces (chunks). LLMs have a "context window" (limit on how much they can read at once), so we must feed them small pieces of relevant information.

### 2. Chunk Size & Overlap
*   **Chunk Size:** The maximum number of characters or tokens in a single chunk (e.g., 512).
*   **Overlap:** A small portion of text from the end of one chunk that is repeated at the start of the next. This ensures that context isn't "cut off" in the middle of a sentence.

### 3. Unstructured.io
A popular library used to "partition" raw documents (PDFs, Word docs, etc.) into structured elements like **Titles**, **NarrativeText**, **ListItems**, and **Tables**. Instead of seeing just a wall of text, the system knows *what* each piece is.

### 4. Embeddings
A way to represent text as a long list of numbers (a vector). These numbers capture the **meaning** of the text. Similar meanings result in similar numbers.

### 5. Sentence Transformers
The specific type of AI model used to create these embeddings. The script uses `all-MiniLM-L6-v2`, which is a fast, efficient model for comparing short sentences.

### 6. Cosine Similarity
A mathematical formula used to measure how "close" two embeddings are in a multi-dimensional space. A high cosine similarity score (closer to 1.0) means the meanings of the two pieces of text are very similar.

### 7. Top-K Retrieval
When searching for an answer, "Top-K" refers to the number of most relevant chunks returned. If `top_k=3`, the system pulls the 3 chunks with the highest similarity scores.

### 8. Relevance Boosting
The practice of artificially increasing the similarity score of certain chunks based on rules. For example, if a user asks "How many sales...", the system adds a 20% "boost" to any **Table** chunks, assuming the answer is likely inside a table.

### 9. Markdown Table
A text-based format for tables (e.g., `| Header |`). This format is much easier for AI models to "read" and understand compared to raw CSV or JSON data.

## How to Run

### Option 1: Run the Advanced Chunking System (Recommended)
This script demonstrates element-aware chunking and contextual boosting.
```bash
python 04_Document_Chunking/[1.1]_advancedchunkingsystem.py
```

### Option 2: Run the Base Chunking Logic
Test the core chunking and validation functions.
```bash
python 04_Document_Chunking/[0.1]_chunk_system.py
```
