from sentence_transformers import SentenceTransformer
from langchain_ollama import OllamaLLM
import numpy as np

# --- STEP 1: INITIALIZATION ---
# We initialize the embedding model to convert text into numerical vectors
# and the LLM to generate responses when we have a cache miss.

# 'all-MiniLM-L6-v2' is a lightweight model that converts sentences into 384-dimensional vectors
embed_model = SentenceTransformer('all-MiniLM-L6-v2')


# Initialize the Ollama LLM (Qwen 1.5b)
llm = OllamaLLM(model="qwen2.5-coder:1.5b")

# --- STEP 2: SEMANTIC CACHE DATA STRUCTURE ---
# Instead of a simple key-value pair, we store the queries, their embeddings, and responses.
# This allows us to perform "Semantic Search" on our previous queries.
cache = {
    "queries": [],     # Original text of the query
    "embeddings": [],  # Numerical representation (vector) of the query
    "responses": []    # The LLM's answer to that query
}

# --- STEP 3: SIMILARITY CALCULATION ---
# This function measures the 'distance' between two vectors.
# A higher score (closer to 1.0) means the meanings are very similar.
def cosine_similarity(v1, v2):
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))


# --- STEP 4: CACHE LOGIC FUNCTIONS ---

def get_cached_response(query, threshold=0.85):
    """
    Check if a semantically similar query already exists in the cache.
    Threshold: 0.85 means the queries must be at least 85% similar in meaning.
    """
    if not cache["embeddings"]:
        return None
    
    # Convert the new query into a vector
    query_emb = embed_model.encode(query)
    
    # Compare against every query we've seen before
    for i, cached_emb in enumerate(cache["embeddings"]):
        similarity = cosine_similarity(query_emb, cached_emb)
        print(f"  Debug: Similarity with '{cache['queries'][i]}' is {similarity:.3f}")
        
        # If similarity is high enough, we reuse the old response!
        if similarity > threshold:
            print(f"✓ Cache hit! Similarity: {similarity:.3f}")
            print(f"  Original query: {cache['queries'][i]}")
            return cache["responses"][i]
    
    return None

def cache_response(query, response):
    """Stores the query, its vector embedding, and the AI response in our cache."""
    query_emb = embed_model.encode(query)
    cache["queries"].append(query)
    cache["embeddings"].append(query_emb)
    cache["responses"].append(response)


# --- STEP 5: TESTING THE SEMANTIC CACHING ---
# We test with queries that are phrased differently but mean the same thing.

queries = [
    "What is machine learning?",
    "Can you explain machine learning?",  # Similar (should result in a Cache Hit)
    "How to make pasta?"                   # Different (should result in a Cache Miss)
]

for query in queries:
    print(f"\nQuery: {query}")
    
    # 1. First, check if we already 'know' the answer semantically
    cached = get_cached_response(query)
    
    if cached:
        # If found, use the cached version (saves time and computation)
        print(f"Response (cached): {cached[:100]}...")
    else:
        # If not found, call the LLM and then store the result
        print("✗ Cache miss. Calling LLM...")
        response = llm.invoke(query)
        cache_response(query, response)
        print(f"Response (new): {response[:100]}...")
