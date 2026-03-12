import os
from typing import List, Dict
from langchain_community.retrievers import BM25Retriever
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from sentence_transformers import CrossEncoder
from pydantic import BaseModel, Field

# --- configuration ---
EMBEDDING_MODEL = "qwen2.5-coder:1.5b"
LLM_MODEL = "qwen2.5-coder:1.5b"
RERANKER_MODEL = 'cross-encoder/ms-marco-MiniLM-L-6-v2'

# --- 1. Define Structured Output Schema ---
class RAGResponse(BaseModel):
    answer: str = Field(description="The direct answer to the user's question based on the context.")
    sources: List[str] = Field(description="List of source names used to answer the question.")
    confidence: str = Field(description="Confidence level: HIGH, MEDIUM, or LOW based on context relevance.")

# --- 2. Helper Class: Simple Ensemble Retriever (from 1.0) ---
class SimpleEnsembleRetriever:
    def __init__(self, retrievers, weights=None):
        self.retrievers = retrievers
        self.weights = weights

    def invoke(self, query: str) -> List[Document]:
        all_docs = []
        for retriever in self.retrievers:
            all_docs.extend(retriever.invoke(query))
        
        # Deduplicate
        unique_docs = []
        seen = set()
        for doc in all_docs:
            if doc.page_content not in seen:
                unique_docs.append(doc)
                seen.add(doc.page_content)
        return unique_docs

# --- 3. The RAG Agent Class ---
class AdvancedRAGAgent:
    def __init__(self, docs: List[Document]):
        print("🚀 Initializing Advanced RAG Agent...")
        
        # A. Hybrid Search Setup
        print("   [1/4] Building Search Indexes (BM25 + FAISS)...")
        self.bm25 = BM25Retriever.from_documents(docs)
        self.bm25.k = 5
        
        self.embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)
        self.vectorstore = FAISS.from_documents(docs, self.embeddings)
        self.faiss = self.vectorstore.as_retriever(search_kwargs={"k": 5})
        
        self.hybrid_retriever = SimpleEnsembleRetriever([self.bm25, self.faiss])
        
        # B. Reranker Setup
        print(f"   [2/4] Loading Reranker ({RERANKER_MODEL})...")
        self.reranker = CrossEncoder(RERANKER_MODEL)
        
        # C. Identification & Generation Setup
        print(f"   [3/4] Connecting to LLM ({LLM_MODEL})...")
        self.parser = JsonOutputParser(pydantic_object=RAGResponse)
        self.llm = ChatOllama(model=LLM_MODEL, format="json", temperature=0)
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful Data Engineering Assistant. Answer strictly based on the provided context.\n{format_instructions}"),
            ("human", "Context:\n{context}\n\nQuestion: {question}")
        ])
        
        self.chain = self.prompt | self.llm | self.parser
        print("   [4/4] Agent Ready!")

    def run(self, query: str):
        print(f"\n🔎 Processing: '{query}'")
        
        # 1. Retrieval (Hybrid)
        print("   Step 1: Hybrid Retrieval...")
        initial_docs = self.hybrid_retriever.invoke(query)
        print(f"           Found {len(initial_docs)} candidates.")
        
        # 2. Reranking
        print("   Step 2: Cross-Encoder Reranking...")
        pairs = [[query, doc.page_content] for doc in initial_docs]
        scores = self.reranker.predict(pairs)
        
        # Attach scores and sort
        ranked_docs = sorted(zip(initial_docs, scores), key=lambda x: x[1], reverse=True)
        top_docs = [doc for doc, score in ranked_docs if score > 0.0][:3] # Filter low relevance
        print(f"           Selected top {len(top_docs)} relevant context chunks.")
        
        # 3. Context Construction
        context_text = "\n\n".join([f"[Source: {d.metadata.get('source', 'unknown')}] {d.page_content}" for d in top_docs])
        
        if not top_docs:
            print("   ⚠️ No relevant context found. Returning fallback.")
            return {"answer": "I couldn't find relevant information in the knowledge base.", "sources": [], "confidence": "LOW"}

        # 4. Generation
        print("   Step 3: Generating Structured Answer...")
        try:
            response = self.chain.invoke({
                "context": context_text,
                "question": query,
                "format_instructions": self.parser.get_format_instructions()
            })
            return response
        except Exception as e:
            return {"answer": f"Generation Error: {str(e)}", "sources": [], "confidence": "LOW"}

# --- 4. Main Execution ---
if __name__ == "__main__":
    # Sample Knowledge Base
    docs = [
        Document(page_content="To reset the Airflow metadata DB, use `airflow db reset`. This deletes all history.", metadata={"source": "airflow_docs"}),
        Document(page_content="The 'orders' table in Snowflake is partitioned by date. Use the partition key in WHERE clauses.", metadata={"source": "data_catalog"}),
        Document(page_content="Error 503 Service Unavailable often indicates the API rate limit was exceeded.", metadata={"source": "api_logs"}),
        Document(page_content="The team standup is at 10 AM daily in Zoom room 4.", metadata={"source": "calendar"}),
        Document(page_content="Use 't3.medium' logs for the dev environment to save costs.", metadata={"source": "infra_guide"}),
    ]
    
    agent = AdvancedRAGAgent(docs)
    
    # Test Queries
    queries = [
        "How do I optimize queries on the orders table?",
        "What should I do if I get a 503 error?",
        "How do I completely wipe the Airflow database?"
    ]
    
    for q in queries:
        result = agent.run(q)
        print("\n🤖 AGENT RESPONSE:")
        print(f"   Answer:     {result['answer']}")
        print(f"   Sources:    {result['sources']}")
        print(f"   Confidence: {result['confidence']}")
        print("-" * 50)
