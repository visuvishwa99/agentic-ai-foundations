import os
import sys
import importlib.util
from typing import List
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../.env"))

# Import Helpers
def load_module(file_path, module_name):
    try:
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        return module
    except Exception as e:
        print(f"Failed to load {module_name}: {e}")
        return None

# Load Risk Analyzer
risk_mod = load_module(os.path.join(os.path.dirname(__file__), "[1.0]_risk_analyzer.py"), "risk_analyzer")
RiskAnalyzer = risk_mod.RiskAnalyzer

# Load Human Reviewer
review_mod = load_module(os.path.join(os.path.dirname(__file__), "[2.0]_human_review.py"), "human_review")
HumanReviewer = review_mod.HumanReviewer

# Load Agent (Week 8)
week8_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../week8"))
if week8_path not in sys.path:
    sys.path.append(week8_path)
    
agent_mod = load_module(os.path.join(week8_path, "[3.0]_sql_agent.py"), "week8_agent")
BaseAgent = agent_mod.CostOptimizedSQLAgent

class InteractiveSQLAgent(BaseAgent):
    def __init__(self):
        print("\n🚀 Initializing INTERACTIVE Data Assistant (Week 11)...")
        super().__init__()
        
        # New Components
        self.risk_analyzer = RiskAnalyzer()
        self.human_reviewer = HumanReviewer()
        
    def run(self, user_query: str):
        print(f"\n🗣️ User Request: '{user_query}'")
        
        # 1. PLAN / GENERATE SQL (Using Week 8 Logic)
        print("   [1/3] Planning SQL (but pausing execution)...")
        # BaseAgent.run() executes the query immediately.
        # We need to *generate* it first, then check, then execute.
        # But BaseAgent structure couples generation & execution.
        
        # Strategy: Let BaseAgent run, but we intercept the *OUTPUT* if possible?
        # No, because "run" in Week 8 executes against vectorstore/db.
        # Week 8 Agent doesn't have a database connection Tool?
        # Week 8 Agent is RAG over cache + LLM generation. It doesn't actually EXECUTE SQL against a DB in the code?
        # Correct! Week 8 only *generates* SQL for the user. It doesn't run `cursor.execute()`.
        
        # Ah! So "Risk Analyzer" here is just warning the user before showing them the code?
        # Or if we had a DB tool, we would pause before the tool call.
        
        # Since this is a simulation, let's pretend execution is imminent.
        
        # Step 1: Generate Response (SQL)
        try:
             # We use super().run() which does Router -> Cache -> Gen
             response = super().run(user_query) # Returns text
        except Exception as e:
             return f"Error Generating Plan: {e}"

        # Step 2: Extract SQL to analyze
        # Assuming markdown block
        try:
            if "```sql" in response:
                sql_candidate = response.split("```sql")[1].split("```")[0].strip()
            elif "```" in response:
                # heuristic fallback
                sql_candidate = response.split("```")[1].split("```")[0].strip()
            # If plain select
            elif "SELECT" in response.upper():
                 sql_candidate = response # risky heuristic if user text contains SELECT
            else:
                 # No SQL found? Maybe conversational
                 print("   ℹ️ No SQL block detected. Passing through.")
                 return response
                 
            # Step 3: Risk Analysis
            print(f"   [2/3] Analyzing Risk for: {sql_candidate[:50]}...")
            assessment = self.risk_analyzer.analyze(sql_candidate)
            
            # Step 4: Approval Gate
            if assessment.requires_approval:
                print(f"   ⚠️ RISK DETECTED: {assessment.level}")
                
                approved = self.human_reviewer.request_approval(
                    query=sql_candidate,
                    risk=assessment.level,
                    reason=assessment.reason
                )
                
                if not approved:
                    return f"🛑 Action Rejected by User. (Plan was: {assessment.reason})"
                
                print("   ✅ Action Approved. Proceeding...")
            else:
                 print("   ✅ Low Risk. Auto-Approved.")
                 
            # Step 5: "Execute" (Simulated)
            print("   [3/3] Executing Query on Snowflake...")
            # In a real agent, here we calls: snowflake.execute(sql_candidate)
            print("   (Simulation: Query executed successfully)")
            
            return f"{response}\n\n✅ Executed successfully."
            
        except Exception as e:
            print(f"   ⚠️ Parsing/Risk Check Error: {e}")
            return response

if __name__ == "__main__":
    agent = InteractiveSQLAgent()
    
    # Test 1: Safe
    agent.run("Count the total users.")
    
    # Test 2: Risky (Requires Input)
    print("\n\n--- TEST 2: RISKY QUERY (Please type 'yes' to approve) ---")
    agent.run("Update user 123 to be active = false")
