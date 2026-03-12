from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from typing import List, Optional

# 1. Define the Schema (The Contract)
# We want the LLM to fill this specific structure, not just chat.
class TicketExtraction(BaseModel):
    issue_summary: str = Field(description="A concise 1-sentence summary of the technical issue")
    priority: str = Field(description="Severity level: LOW, MEDIUM, HIGH, or CRITICAL")
    affected_systems: List[str] = Field(description="List of software components, databases, or tables mentioned")
    suggested_action: str = Field(description="A brief recommended next step based on the logs")

# 2. Setup the Parser
# This translates our Pydantic class into a format instructions string for the LLM
parser = JsonOutputParser(pydantic_object=TicketExtraction)

# 3. Setup the LLM (Ollama with JSON mode)
# 'format="json"' is CRITICAL here - it forces the model to only output valid JSON
llm = ChatOllama(
    model="qwen2.5-coder:1.5b",
    temperature=0,
    format="json"  
)

# 4. Create the Prompt
# We inject the parser's instructions so the model knows exactly what schema to follow
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a Data Engineering Support Agent. Extract structured info from logs.\n{format_instructions}"),
    ("human", "Here is the raw log:\n{query}")
])

# 5. Build the Chain
chain = prompt | llm | parser

def extract_structured_data(log_message: str):
    """
    Demonstrates Structured Output: Forcing a small model to produce valid JSON.
    """
    print(f"\n📄 Processing Log:\n'{log_message}'")
    print("   [1] Invoking LLM with JSON Schema enforcement...")
    
    try:
        # Run the chain
        result = chain.invoke({
            "query": log_message,
            "format_instructions": parser.get_format_instructions()
        })
        
        print("\n✅ Structured Output (Parsed JSON):")
        print(f"   PLEASE FIX:    {result['issue_summary']}")
        print(f"   PRIORITY:      {result['priority']}")
        print(f"   SYSTEMS:       {result['affected_systems']}")
        print(f"   SUGGESTION:    {result['suggested_action']}")
        return result
        
    except Exception as e:
        print(f"❌ Error parsing output: {e}")

if __name__ == "__main__":
    # Test Case 1: Database Failure
    log1 = """
    CRITICAL ALERT: Job 'daily_sales_load' failed at 03:00 AM. 
    Error: Connection refused to Snowflake instance 'sf_prod_01'. 
    Retried 3 times without success. The network logs show timeout exceptions.
    """
    extract_structured_data(log1)
    
    # Test Case 2: Data Quality Issue
    log2 = """
    Warning: The 'customer_email' column in the staging table contains 450 null values.
    This exceeds the threshold of 100. The pipeline continued but marked rows as invalid.
    """
    extract_structured_data(log2)
