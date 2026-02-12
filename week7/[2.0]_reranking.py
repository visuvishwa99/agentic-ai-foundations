from sentence_transformers import CrossEncoder
from typing import List, Dict

# 1. Setup Mock Retrieval Results (Simulating Top-5 from Hybrid Search)
# Notice: some irrelevant docs are mixed in, and the "best" doc isn't first.
retrieved_docs = [
    {"id": 1, "content": "The marketing team has a weekly meeting on Fridays.", "source": "calendar_logs"},
    {"id": 2, "content": "Error ORA-12154 means the TNS listener could not resolve the service name.", "source": "oracle_docs"},
    {"id": 3, "content": "To fix connection issues, check your tnsnames.ora file and verify the host.", "source": "troubleshooting_guide"},
    {"id": 4, "content": "The cafeteria menu for today includes pizza and salad.", "source": "general_announcements"},
    {"id": 5, "content": "Check the firewall settings if you cannot connect to the database from the VPN.", "source": "network_admin"}
]

def implement_reranking(query: str):
    """
    Demonstrates Reranking: specific scoring of (Query, Document) pairs.
    Unlike Embeddings (Bi-Encoder) which are fast but approximate,
    Cross-Encoders are slower but much more accurate for final ranking.
    """
    print(f"\n🔍 Query: '{query}'")
    
    # --- Step 1: Initialize Cross-Encoder ---
    # We use a model specifically trained to score relevance
    print("   [1] Loading Cross-Encoder Model (ms-marco-MiniLM-L-6-v2)...")
    model = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
    
    # --- Step 2: Prepare Pairs ---
    # The model expects valid input as list of [query, doc_text] pairs
    pairs = [[query, doc["content"]] for doc in retrieved_docs]
    
    # --- Step 3: Score Pairs ---
    print("   [2] Scoring Query-Document Pairs...")
    scores = model.predict(pairs)
    
    # --- Step 4: Attach Scores & Sort ---
    ranked_docs = []
    for doc, score in zip(retrieved_docs, scores):
        doc["score"] = score
        ranked_docs.append(doc)
    
    # Sort by score descending (highest relevance first)
    ranked_docs = sorted(ranked_docs, key=lambda x: x["score"], reverse=True)
    
    # --- Step 5: Display Results ---
    print("\n✅ Reranked Results (Top 3):")
    for i, doc in enumerate(ranked_docs[:3]):
        print(f"   {i+1}. [Score: {doc['score']:.4f}] {doc['content']} (Source: {doc['source']})")

if __name__ == "__main__":
    # Scenario: Technical DB connectivity issue
    query = "How do I resolve Oracle connection failure?"
    implement_reranking(query)
