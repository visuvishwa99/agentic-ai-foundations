import os
import json
from datetime import datetime
from dotenv import load_dotenv

# Load env variables
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../.env"))

# Load Models from ENV
MAIN_LLM = os.getenv("MAIN_LLM", "codellama:7b-instruct-q4_0")
SMALL_LLM = os.getenv("SMALL_LLM", "qwen2.5-coder:1.5b")

# Pricing Configuration (Per 1M Tokens)
# simulating virtual API costs for our local models
# We use the variable names as keys to ensure dynamic matching
PRICING = {
    # Lightweight Model (Simple Tasks)
    SMALL_LLM: {"input": 0.20, "output": 0.60},
    
    # Heavyweight Model (Complex Tasks)
    MAIN_LLM: {"input": 1.00, "output": 3.00},
    
    "local": {"input": 0.00, "output": 0.00}
}
 
class CostMonitor:
    def __init__(self, budget_limit=5.00):
        self.budget_limit = float(os.getenv("BUDGET_LIMIT", budget_limit))
        self.total_cost = 0.0
        self.usage_log = []
        print(f"💰 Cost Monitor Initialized (Budget: ${self.budget_limit:.2f})")
 
    def track_request(self, model: str, input_tokens: int, output_tokens: int):
        """Calculates cost for a request and updates the ledger."""
        
        # Identify pricing tier
        # We match exact model names from .env first
        if model in PRICING:
            rates = PRICING[model]
        # Fallbacks for partial matches if needed (though exact match is better)
        elif SMALL_LLM in model:
             rates = PRICING[SMALL_LLM]
        elif MAIN_LLM in model:
             rates = PRICING[MAIN_LLM]
        else:
            rates = PRICING["local"]

        
        # Calculate Cost
        input_cost = (input_tokens / 1_000_000) * rates["input"]
        output_cost = (output_tokens / 1_000_000) * rates["output"]
        total_request_cost = input_cost + output_cost
        
        self.total_cost += total_request_cost
        
        # Log entry
        entry = {
            "timestamp": datetime.now().isoformat(),
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost": total_request_cost
        }
        self.usage_log.append(entry)
        
        # Print status
        print(f"   💸 Cost: ${total_request_cost:.6f} | Total: ${self.total_cost:.6f} | Budget Used: {(self.total_cost/self.budget_limit)*100:.1f}%")
        
        if self.total_cost > self.budget_limit:
            print("   🚨 ALERT: DAILY BUDGET EXCEEDED!")

    def get_report(self):
        return {
            "total_cost": self.total_cost,
            "budget_limit": self.budget_limit,
            "remaining_budget": self.budget_limit - self.total_cost,
            "total_requests": len(self.usage_log)
        }

# --- Test Execution ---
if __name__ == "__main__":
    monitor = CostMonitor()
    
    # Simulate some traffic
    print("\n--- Simulating Traffic ---")
    
    # 1. Cheap Request (Simple Logic)
    print(f"Request 1: Simple Logic ({SMALL_LLM})")
    monitor.track_request(SMALL_LLM, input_tokens=500, output_tokens=100)
    
    # 2. Expensive Request (Complex Logic)
    print(f"\nRequest 2: Complex Architecture ({MAIN_LLM})")
    monitor.track_request(MAIN_LLM, input_tokens=2000, output_tokens=800)
    
    # 3. Router Overhead (Local/Free)
    print("\nRequest 3: Local Router (Overhead)")
    monitor.track_request("local_router", input_tokens=150, output_tokens=10)
