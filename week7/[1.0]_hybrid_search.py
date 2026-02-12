import os
from typing import List
from langchain_community.retrievers import BM25Retriever
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings
from langchain_core.documents import Document

# Custom Ensemble Implementation (Simulates langchain.retrievers.EnsembleRetriever)
# Why? To avoid import issues with changing langchain package structures.
class SimpleEnsembleRetriever:
    def __init__(self, retrievers, weights=None):
        self.retrievers = retrievers
        self.weights = weights

    def invoke(self, query: str) -> List[Document]:
        """
        Executes all retrievers and merges results using a simple round-robin + deduplication strategy.
        Real production systems use Reciprocal Rank Fusion (RRF).
        """
        all_docs = []
        for retriever in self.retrievers:
            all_docs.extend(retriever.invoke(query))
            
        # Deduplicate by page_content
        unique_docs = []
        seen_content = set()
        
        for doc in all_docs:
            if doc.page_content not in seen_content:
                unique_docs.append(doc)
                seen_content.add(doc.page_content)
                
        return unique_docs[:4]  # Return top 4 unique results

# 1. Setup Sample Data
sample_docs = [
    Document(
        page_content="FACT_SALES table contains daily transactional data including revenue, units sold, and store_id.",
        metadata={"source": "snowflake_catalog", "type": "table_definition"}
    ),
    Document(
        page_content="DIM_CUSTOMER includes PII data: customer_name, email, and loyalty_tier. Join on customer_key.",
        metadata={"source": "snowflake_catalog", "type": "table_definition"}
    ),
    Document(
        page_content="The ETL job 'load_crunchtime_daily' failed yesterday due to a schema mismatch in the source S3 bucket.",
        metadata={"source": "airflow_logs", "type": "error_log"}
    ),
    Document(
        page_content="Use 'loyalty_tier' column in DIM_CUSTOMER to calculate regional discounts in the SALES_SUMMARY view.",
        metadata={"source": "dbt_docs", "type": "transformation_logic"}
    ),
    Document(
        page_content="Connection error ORA-12154 TNS:could not resolve the connect identifier specified for Oracle source.",
        metadata={"source": "ingestion_service", "type": "error_log"}
    )
]

def implement_hybrid_search(query: str):
    """
    Demonstrates Hybrid Search: BM25 (Keywords) + FAISS (Semantics)
    """
    print(f"\n🔍 Processing Query: '{query}'")
    
    # --- Step 1: Initialize Keyword Retriever (BM25) ---
    print("   [1] Running Keyword Search (BM25)...")
    bm25_retriever = BM25Retriever.from_documents(sample_docs)
    bm25_retriever.k = 2
    
    # --- Step 2: Initialize Vector Retriever (FAISS) ---
    print("   [2] Running Semantic Search (Vector)...")
    embeddings = OllamaEmbeddings(model="qwen2.5-coder:1.5b")
    vectorstore = FAISS.from_documents(sample_docs, embeddings)
    faiss_retriever = vectorstore.as_retriever(search_kwargs={"k": 2})
    
    # --- Step 3: Ensemble (Hybrid) ---
    print("   [3] Merging Results...")
    hybrid_retriever = SimpleEnsembleRetriever(
        retrievers=[bm25_retriever, faiss_retriever], 
        weights=[0.5, 0.5]
    )
    
    # --- Step 4: Execute ---
    results = hybrid_retriever.invoke(query)
    
    print(f"\n✅ Found {len(results)} relevant documents:")
    for i, doc in enumerate(results):
        print(f"   {i+1}. {doc.page_content[:80]}... (Source: {doc.metadata['source']})")

if __name__ == "__main__":
    # Test 1: Keyword heavy
    implement_hybrid_search("Tell me about ORA-12154 error")
    
    # Test 2: Semantic heavy
    implement_hybrid_search("How do I identify a specific user?")
    
    # Test 3: Mixed
    implement_hybrid_search("What happened to the sales warehouse pipeline?")
