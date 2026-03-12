import chromadb
from sentence_transformers import SentenceTransformer
from langchain_ollama import OllamaLLM

"""
LangChain Framework

LangChain: A popular Python framework for building applications with Large Language Models (LLMs)
Purpose: Provides standardized interfaces to work with different AI models
Benefit: Write code once, switch between different LLM providers easily

Ollama Integration

Ollama: A tool that lets you run large language models locally on your computer
langchain_ollama: A connector package that bridges LangChain with Ollama
OllamaLLM: The specific class that handles communication with local Ollama models
"""

# --- STEP 1: INITIALIZATION ---
# We set up the core components for our RAG (Retrieval-Augmented Generation) system.
# 1. Embedding Model: Converts text into numbers (vectors) the AI can compare.
# 2. LLM: The brain that generates the final human-like answer.
# 3. Vector DB: ChromaDB will store our "knowledge" and allow us to search it.

embed_model = SentenceTransformer('all-MiniLM-L6-v2')
llm = OllamaLLM(model="qwen2.5-coder:1.5b")
client = chromadb.Client()
collection = client.create_collection("rag_demo")

# --- STEP 2: BUILDING THE KNOWLEDGE BASE ---
# We add private or specific data to our vector database. 
# This is data the AI might not know from its general training.

knowledge = [
    "Python was created by Guido van Rossum in 1991",
    "Python is an interpreted, high-level programming language",
    "Python supports multiple programming paradigms",
    "Machine learning libraries: TensorFlow, PyTorch, scikit-learn",
    "FastAPI is a modern Python web framework"
]

# When we add documents, ChromaDB automatically converts them into vectors.
collection.add(
    documents=knowledge,
    ids=[f"k{i}" for i in range(len(knowledge))]
)

# --- STEP 3: THE RAG FUNCTION (Retrieve + Generate) ---
# This is the heart of the system. It follows two phases:
# Phase A (Retrieve): Find the most relevant facts from the database.
# Phase B (Generate): Send those facts to the AI to help it answer.

def rag_query(question, n_results=3):
    """Retrieves relevant context and passes it to the LLM."""
    
    # 1. RETRIEVAL PHASE
    # Search the vector database for the top 'N' most relevant snippets.
    results = collection.query(
        query_texts=[question],
        n_results=n_results
    )
    
    # Combine the found snippets into a single context block
    context = "\n".join(results["documents"][0])
    print(f"--- DEBUG: Retrieved Context ---\n{context}\n------------------------------")
    
    # 2. GENERATION PHASE
    # We "stuff" the context into the prompt so the AI knows the facts.
    prompt = f"""Use the following pieces of context to answer the question at the end.
If you don't know the answer based on the context, just say that you don't know.

Context:
{context}

Question: {question}

Answer:"""
    
    # The AI reads the context and provides an informed response
    response = llm.invoke(prompt)
    return response

# --- STEP 4: RUNNING THE RAG PIPELINE ---
# We test our system with specific questions to see if it uses our knowledge base.

questions = [
    "Who created Python?",
    "What ML libraries are available in Python?",
    "Is Python interpreted or compiled?"
]

for q in questions:
    print(f"\n{'='*60}")
    print(f"USER QUESTION: {q}")
    print(f"{'='*60}")
    
    answer = rag_query(q)
    print(f"\nAI RESPONSE:\n{answer}")
