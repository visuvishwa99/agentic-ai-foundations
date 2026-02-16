import re

class OutputGuard:
    def __init__(self):
        print("🛡️ Initializing Output Guard (SQL Validator)...")
        # Define forbidden commands (Keywords that should NOT appear in generated SQL)
        self.forbidden_commands = [
            "DROP", "DELETE", "TRUNCATE", "ALTER", "GRANT", "REVOKE", 
            "INSERT", "UPDATE", "CREATE", "REPLACE"
        ]
        
    def validate_sql(self, sql: str):
        """
        Checks if the generated SQL is safe to execute.
        Returns: (is_safe: bool, reason: str)
        """
        if not sql:
             return False, "SQL is empty"

        print(f"\n🔍 Validating SQL: '{sql}'")
        
        sql_upper = sql.upper()
        
        # 1. Check for Destructive Commands using Regex (Whole Word Match)
        for cmd in self.forbidden_commands:
            # \b matches word boundary to avoid false positives like 'updated_at' matching 'UPDATE'
            if re.search(r'\b' + cmd + r'\b', sql_upper):
                print(f"   🚨 BLOCKED: Contains forbidden command '{cmd}'")
                return False, f"SQL contains forbidden command: {cmd}"
        
        # 2. Check for unexpected length (too short)
        if len(sql.strip()) < 10:
             print("   ⚠️ REJECTED: SQL too short/empty.")
             return False, "SQL too short"

        # 3. Check for multiple statements (basic check for semicolon injection)
        # We only allow one statement generally.
        if sql.count(";") > 1:
             print("   ⚠️ REJECTED: Multiple SQL statements detected.")
             return False, "Multiple statements not allowed"

        print("   ✅ SQL Safe to Execute.")
        return True, "Safe"

# --- Test Execution ---
if __name__ == "__main__":
    guard = OutputGuard()
    
    # Test 1: Safe Select
    guard.validate_sql("SELECT * FROM users WHERE id = 1;")
    
    # Test 2: Destructive Command
    guard.validate_sql("DROP TABLE users;")
    
    # Test 3: Injection Attempt (Multiple Statements)
    guard.validate_sql("SELECT * FROM users; DELETE FROM orders;")
    
    # Test 4: False Positive Check (Should pass)
    guard.validate_sql("SELECT updated_at FROM logs WHERE status = 'DROPPED';")
