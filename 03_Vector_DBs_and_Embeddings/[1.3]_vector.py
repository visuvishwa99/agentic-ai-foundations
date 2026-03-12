from langchain_ollama import OllamaLLM
from sentence_transformers import SentenceTransformer
import numpy as np
from numpy.linalg import norm

# --- STEP 1: INITIALIZATION ---
# Load models for embedding generation and local LLM logic.
embed_model = SentenceTransformer('all-MiniLM-L6-v2')
llm = OllamaLLM(model="qwen2.5-coder:1.5b")

# --- STEP 2: SIMILARITY LOGIC ---
# Standard math function to calculate semantic "closeness" between vectors.
def cosine_similarity(a, b):
    return np.dot(a, b) / (norm(a) * norm(b))

# --- STEP 3: PREPARE AND INDEX DATA ---
docs = [
    "Python is a programming language used for web development",
    "Machine learning is a subset of artificial intelligence",
    "Pasta carbonara is an Italian dish made with eggs and cheese",
    "JavaScript is used for frontend web development"
]

# Convert all library documents to vectors
doc_embeddings = [embed_model.encode(doc) for doc in docs]

# --- STEP 4: RETRIEVAL ---
# When a question is asked, we find the most relevant pieces of information.
query = "How to do web development?"
query_emb = embed_model.encode(query)

# Calculate similarity between query and every doc
similarities = [cosine_similarity(query_emb, doc_emb) for doc_emb in doc_embeddings]

# Get the indices of the Top 2 most similar documents
top_indices = np.argsort(similarities)[-2:][::-1]
top_docs = [docs[i] for i in top_indices]

print("--- RETRIEVED CONTEXT ---")
for i, doc in enumerate(top_docs):
    print(f"{i+1}. {doc} (Score: {similarities[top_indices[i]]:.3f})")

# --- STEP 5: GENERATION ---
# Feed the found information into the LLM to get a grounded answer.
context = "\n".join(top_docs)
prompt = f"""Use this context to answer the question.
Context:
{context}

Question: {query}
Answer:"""

response = llm.invoke(prompt)
print(f"\nAI RESPONSE:\n{response}")
