import os
from typing import Literal
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from lm_studio_backend import CHAT_MODEL, create_chat_model, parse_json_object

# Load settings from root .env file
# We look for .env in the parent directory (project root)
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../.env"))

# --- configuration ---
# Use the environment variable, default to 'qwen2.5-coder:1.5b' if missing
ROUTER_MODEL = os.getenv("ROUTER_MODEL", CHAT_MODEL)
MAIN_LLM = os.getenv("MAIN_LLM", CHAT_MODEL)
SMALL_LLM = os.getenv("SMALL_LLM", CHAT_MODEL)

# --- 1. Define Output Schema ---
class RouteDecision(BaseModel):
    complexity: Literal["SIMPLE", "COMPLEX"] = Field(
        description="SIMPLE: Basic lookups, definitions, formatting, or single-step tasks. COMPLEX: Reasoning, architectural design, debugging, or multi-step analysis."
    )
    reasoning: str = Field(description="Brief explanation of why this complexity was chosen.")

# --- 2. The Model Router Class ---
class ModelRouter:
    def __init__(self, model_name=ROUTER_MODEL):
        print(f"Initializing model router with {model_name}...")
        self.llm = create_chat_model(model_name)
        
        # The Cost-Saving Map
        # Routes dynamically based on .env configuration
        self.routing_table = {
            "SIMPLE": SMALL_LLM,      # Cheap / Fast Model
            "COMPLEX": MAIN_LLM       # Powerful / Reasoning Model
        }
        
        print(f"    API Routing Table:")
        print(f"      - SIMPLE  -> {self.routing_table['SIMPLE']}")
        print(f"      - COMPLEX -> {self.routing_table['COMPLEX']}")

    def classify(self, query: str) -> RouteDecision:
        """Determines the complexity of a query using a lightweight local LLM."""
        
        system_prompt = """You are a Budget Gatekeeper for a Data Engineering AI.
        Your goal is to save money by routing simple queries to cheaper models.
        
        CRITERIA:
        - SIMPLE: definitions, syntax questions, simple SQL, explaining standard concepts (e.g., "What is ETL?").
        - COMPLEX: designing pipelines, debugging errors, complex window functions, architectural advice.
        
        Return a JSON object with 'complexity' (SIMPLE/COMPLEX) and 'reasoning'."""
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "Query: {query}")
        ])
        
        chain = prompt | self.llm
        
        try:
            # Invoke local model
            response = chain.invoke({"query": query})
            # Parse JSON
            data = parse_json_object(str(response.content))
            return RouteDecision(**data)
        except Exception as e:
            print(f"   [WARN] Router Error: {e}. Defaulting to COMPLEX (Safe Mode).")
            return RouteDecision(complexity="COMPLEX", reasoning="Router failed, default safe choice.")

    def route_request(self, query: str):
        """Public method to get the recommended model for a query."""
        print(f"\n Analyzing Query: '{query}'")
        decision = self.classify(query)
        
        model_id = self.routing_table.get(decision.complexity, MAIN_LLM)
        
        print(f"   [OK] Classification: {decision.complexity}")
        print(f"    Reasoning:      {decision.reasoning}")
        print(f"    Routed To:      {model_id}")
        
        return model_id, decision

# --- 3. Main Execution Test ---
if __name__ == "__main__":
    # Initialize Router
    router = ModelRouter()
    
    # Test Cases
    test_queries = [
        "What is the difference between WHERE and HAVING?",
        "Design a streaming architecture using Kafka and Spark Structured Streaming for fraud detection.",
        "Convert this date '2023-01-01' to DD/MM/YYYY format.",
        "Why is my airflow task stuck in 'queued' state forever? Here are the logs...",
    ]
    
    print("-" * 50)
    print(" STARTING ROUTING TEST")
    print("-" * 50)
    
    for q in test_queries:
        router.route_request(q)
        print("-" * 30)
