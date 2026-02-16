import re
import os
from pydantic import BaseModel, Field
from typing import Literal

# Load env in case needed (for LLM)
from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../.env"))

class RiskAssessment(BaseModel):
    level: Literal["LOW", "MEDIUM", "HIGH"]
    reason: str
    requires_approval: bool

class RiskAnalyzer:
    def __init__(self):
        print("🚦 Initializing SQL Risk Analyzer...")
        
        # Keywords
        self.high_risk_keywords = [
            "DROP", "DELETE", "TRUNCATE", "ALTER", "GRANT", "REVOKE"
        ]
        self.medium_risk_keywords = [
            "UPDATE", "INSERT", "CREATE", "REPLACE"
        ]
        
    def analyze(self, sql_query: str) -> RiskAssessment:
        """Classifies SQL query risk based on keywords."""
        sql_upper = sql_query.upper().strip()
        
        # 1. High Risk Check (Destructive DDL/DML)
        for keyword in self.high_risk_keywords:
            if re.search(r"\b" + re.escape(keyword) + r"\b", sql_upper):
                return RiskAssessment(
                    level="HIGH",
                    reason=f"Contains destructive command: {keyword}",
                    requires_approval=True
                )
                
        # 2. Medium Risk Check (Data Modification)
        for keyword in self.medium_risk_keywords:
             if re.search(r"\b" + re.escape(keyword) + r"\b", sql_upper):
                return RiskAssessment(
                    level="MEDIUM",
                    reason=f"Modifies data schema or content: {keyword}",
                    requires_approval=True
                )
                
        # 3. Low Risk (Read-Only)
        return RiskAssessment(
            level="LOW",
            reason="Read-only SELECT query",
            requires_approval=False
        )

if __name__ == "__main__":
    analyzer = RiskAnalyzer()
    
    queries = [
        "SELECT * FROM users",
        "UPDATE users SET name='Alice' WHERE id=1",
        "DROP TABLE vital_records",
        "INSERT INTO logs VALUES (1, 'test')"
    ]
    
    print(f"\n🧪 Running Risk Tests:")
    for q in queries:
        result = analyzer.analyze(q)
        icon = "🟢" if result.level == "LOW" else "🟠" if result.level == "MEDIUM" else "🔴"
        print(f"{icon} Query: '{q}'")
        print(f"   Level: {result.level} | Approval: {result.requires_approval} | Reason: {result.reason}\n")
