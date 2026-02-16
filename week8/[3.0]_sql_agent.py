import os
import sys
import time
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Import custom modules
from dotenv import load_dotenv

# Load env variables
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../.env"))

# --- Dynamic Import for Bracketed Filenames ---
import importlib.util

def load_module(file_name, module_name):
    # Construct absolute path
    file_path = os.path.join(os.path.dirname(__file__), file_name)
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

# Load the Week 8 components
print("⚙️ Loading Week 8 Modules...")
router_mod = load_module("[1.0]_model_router.py", "model_router")
cache_mod = load_module("[2.0]_semantic_cache.py", "semantic_cache")
monitor_mod = load_module("[4.0]_cost_monitor.py", "cost_monitor")

# Extract Classes
ModelRouter = router_mod.ModelRouter
SemanticCache = cache_mod.SemanticCache
CostMonitor = monitor_mod.CostMonitor

class CostOptimizedSQLAgent:
    def __init__(self):
        print("\n🚀 Initializing Cost-Optimized Data Assistant...")
        self.router = ModelRouter()
        self.cache = SemanticCache()
        self.monitor = CostMonitor()
        self.token_buffer = [] # Store output history for analysis
        
    def generate_sql(self, query: str, model_name: str):
        """Generates SQL using the selected model."""
        start_time = time.time()
        
        # Initialize LLM
        # The router returns the exact model ID from .env (e.g., codellama:7b-instruct-q4_0)
        
        llm = ChatOllama(model=model_name, temperature=0, format="json")
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a SQL Expert. Return JSON with 'sql' and 'explanation' fields."),
            ("human", "Write a Snowflake SQL query for: {query}")
        ])
        
        chain = prompt | llm | StrOutputParser()
        
        try:
            response = chain.invoke({"query": query})
        except Exception as e:
            print(f"   ❌ LLM Error: {e}")
            return "Error Generating SQL"
            
        end_time = time.time()
        
        # Estimate usage & Cost
        input_len = len(query)
        output_len = len(response)
        
        # Simple token estimation
        in_tokens = input_len // 4
        out_tokens = output_len // 4
        
        self.monitor.track_request(model_name, in_tokens, out_tokens)
        
        return response

    def run(self, user_query: str):
        print(f"\nExample User Query: '{user_query}'")
        print("-" * 50)
        
        # 1. Semantic Cache Lookup
        # We need to construct cache key carefully
        cached_result = self.cache.get_cached_response(user_query)
        
        if cached_result:
            print(f"      ⚡ CACHE HIT! (Saved API Call)")
            # Log specific savings?
            return cached_result
        
        # 2. Model Routing
        print("   [Router] Analyzing Complexity...")
        model_id, decision = self.router.route_request(user_query)
        
        # 3. Execution Phase
        print(f"   [Execution] Running on {model_id}...")
        result = self.generate_sql(user_query, model_id)
        
        # 4. Update Cache
        self.cache.cache_response(user_query, result)
        
        print("\n✅ Final Result:")
        print(result[:200] + "..." if len(result) > 200 else result)
        return result

if __name__ == "__main__":
    agent = CostOptimizedSQLAgent()
    
    # 1. First Run: Expensive/Complex Query
    q1 = "Calculate the 7-day rolling active users from events table."
    agent.run(q1)
    
    # 2. Second Run: Simple Query
    q2 = "Select top 10 users."
    agent.run(q2)
    
    # 3. Third Run: Repeat Complex Query (Should HIT Cache)
    print("\n🔁 REPEATING QUERY (Expecting Cache Hit)...")
    agent.run(q1)
    
    # 4. Fourth Run: Semantically Similar (Should HIT Cache)
    print("\n🔁 ASKING SIMILAR QUERY (Expecting Semantic Cache Hit)...")
    q1_similar = "Compute rolling 7-day active user count from events."
    agent.run(q1_similar)
