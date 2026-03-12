import chromadb
from langchain_ollama import OllamaLLM

# --- STEP 1: VECTOR STORAGE (ChromaDB) ---
# ChromaDB is a vector database used to store and retrieve data based on meaning (embeddings) 
# rather than just keywords.
client = chromadb.Client() 
collection = client.create_collection("knowledge_base")

# Data Indexing: Add documents to the 'knowledge_base' collection.
# These will be converted into 'embeddings' (numerical representations of meaning).
docs = [
    "Python is excellent for data science and machine learning",
    "JavaScript powers modern web applications",
    "SQL is used for database queries",
    "Docker containers help deploy applications"
]

collection.add(
    documents=docs,
    metadatas=[
        {"category": "programming", "language": "python"},
        {"category": "programming", "language": "javascript"},
        {"category": "database", "language": "sql"},
        {"category": "devops", "tool": "docker"}
    ],
    ids=[f"doc{i}" for i in range(len(docs))]
)

# --- STEP 2: SEMANTIC SEARCH ---
# We query the database. Instead of looking for exact words, it finds documents 
# with the closest semantic meaning to our question.
# Converts your question into a vector/embedding (numerical representation of meaning)
# Compares this vector against all stored document vectors
# Returns documents with closest semantic similarity, not exact word matches
# Works on meaning understanding, not keyword matching
results = collection.query(
    query_texts=["How to work with docker?"],
    n_results=2
)

print("Retrieved documents from ChromaDB:")
for doc in results["documents"][0]:
    print(f"- {doc}")

# --- STEP 3: INTEGRATION WITH LLM (Retrieval-Augmented Generation / RAG) ---
# This step takes the specific information retrieved from ChromaDB and provides it to the LLM.
# This ensures the AI answers using our "Knowledge Base" instead of just general knowledge.

# Initialize the Ollama LLM with a smaller model to fit in available RAM
llm = OllamaLLM(model="qwen2.5-coder:1.5b")

# Combine the retrieved documents into a single 'context' string
context = "\n".join(results["documents"][0])

# Construct the prompt: Give the AI the context AND the question
prompt = f"Context:\n{context}\n\nQuestion: how to install docker as newbie?\nAnswer:"

# Get the final answer from the AI
response = llm.invoke(prompt)
print(f"\nAI Answer (informed by database context):\n{response}")