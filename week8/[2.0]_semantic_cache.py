import os
import time
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

# Load env
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../.env"))

EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "qwen2.5-coder:1.5b")
CACHE_THRESHOLD = float(os.getenv("CACHE_THRESHOLD", "0.35"))

class SemanticCache:
    def __init__(self, threshold: float = CACHE_THRESHOLD):
        print(f"🧠 Initializing Semantic Cache (Model: {EMBEDDING_MODEL}, Threshold: {threshold})...")
        try:
            self.embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)
        except Exception as e:
            print(f"❌ Error initializing embeddings: {e}")
            raise
            
        self.vectorstore = None
        self.threshold = threshold
        
    def get_cached_response(self, query: str) -> Optional[str]:
        """
        Check if a similar query exists in the cache.
        Returns the cached response if similarity score < threshold.
        """
        if not self.vectorstore:
            return None
        
        # Search for the 1 nearest neighbor
        # Note: FAISS default metric is L2 distance (lower is better)
        try:
            results = self.vectorstore.similarity_search_with_score(query, k=1)
        except Exception as e:
            print(f"⚠️ Cache lookup failed: {e}")
            return None
        
        if not results:
            return None
            
        best_doc, score = results[0]
        cached_query = best_doc.page_content
        cached_response = best_doc.metadata.get("response")
        
        print(f"      🔍 Cache Search: '{cached_query}' (Score: {score:.4f})")
        
        # Check threshold
        if score < self.threshold:
            print(f"      ✅ CACHE HIT! (Saved API Call)")
            return cached_response
        
        print(f"      ❌ CACHE MISS (Distance {score:.4f} > {self.threshold})")
        return None

    def cache_response(self, query: str, response: str):
        """Stores a new query-response pair in the vector store."""
        print(f"      💾 Caching new result...")
        doc = Document(page_content=query, metadata={"response": response})
        
        if self.vectorstore is None:
            self.vectorstore = FAISS.from_documents([doc], self.embeddings)
        else:
            self.vectorstore.add_documents([doc])

# --- Test Execution ---
if __name__ == "__main__":
    cache = SemanticCache()
    
    # 1. First Ask
    q1 = "How do I optimize Snowflake costs?"
    resp1 = "Use auto-suspend and resource monitors to control credit usage."
    
    print(f"\nUser: {q1}")
    if not cache.get_cached_response(q1):
        print("   (Generating Response...)")
        cache.cache_response(q1, resp1)
    
    # 2. Ask Similar Question
    q2 = "What is the best way to reduce spending in Snowflake?"
    print(f"\nUser: {q2}")
    cached = cache.get_cached_response(q2)
    
    if cached:
        print(f"   🤖 Agent: {cached}")
    else:
        print("   (Generating Response...)")
