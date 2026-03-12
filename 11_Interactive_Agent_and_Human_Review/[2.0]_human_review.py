import os
import sys

class HumanReviewer:
    def __init__(self):
        print("👤 Initializing Human Reviewer Interface...")
        
    def request_approval(self, query: str, risk: str, reason: str) -> bool:
        """
        Pauses execution and asks for user confirmation.
        Returns True if approved, False if rejected.
        """
        print("\n" + "="*50)
        print(f"🛑 CRITICAL ACTION REQUIRED")
        print(f"   Query:  {query}")
        print(f"   Risk:   {risk}")
        print(f"   Reason: {reason}")
        print("="*50)
        
        # Since we are running in a non-interactive environment (mostly),
        # we can simulate approval via a flag or mock it.
        # But let's write the real code for CLI usage:
        
        try:
            # Check for override flag (Environment Variable)
            override = os.getenv("AUTO_APPROVE_RISK", "FALSE")
            if override == "TRUE":
                print(f"   🤖 AUTO-APPROVED by Environment Policy.")
                return True
                
            response = input("   Do you approve this action? (yes/no): ").lower().strip()
            
            if response in ["yes", "y", "approve"]:
                print(f"   ✅ APPROVED by Human Operator.")
                return True
            else:
                print(f"   ❌ REJECTED by Human Operator.")
                return False
        except EOFError:
             # Handle non-interactive run (e.g., CI/CD or Agent background)
             print("   ⚠️ Non-interactive shell detected. Auto-Rejecting risky action.")
             return False

if __name__ == "__main__":
    reviewer = HumanReviewer()
    # Test (Simulate input if possible, else might fail or block)
    print("\n--- Test Mode: Auto-Reject expected if non-interactive ---")
    approved = reviewer.request_approval("DELETE FROM users", "HIGH", "Destructive Command")
    print(f"Result: {approved}")
