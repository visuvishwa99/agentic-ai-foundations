import os
import json
from typing import List, Optional
from pydantic import BaseModel, Field
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

# Load env variables (for model selection)
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../.env"))

# Use SMALL_LLM (Qwen) because it's usually better at JSON/Syntax than CodeLlama Instruct for simple extraction tasks
MODEL_NAME = os.getenv("SMALL_LLM", "qwen2.5-coder:1.5b")

# --- 1. Define Output Structure for reference ---
class LineageNode(BaseModel):
    table_name: str
    source_tables: List[str]
    operation_type: str

# --- 2. The Extraction Logic ---
class LineageMapper:
    def __init__(self):
        print(f"🕸️ Lineage Mapper: Using model '{MODEL_NAME}'")
        self.llm = ChatOllama(model=MODEL_NAME, format="json", temperature=0)

    def extract_lineage(self, sql_content: str) -> Optional[dict]:
        """Uses LLM to parse SQL and find dependencies."""
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a SQL Parser. Return JSON with 'table_name' (target table) and 'source_tables' (list of tables read from).
            Example:
            SQL: CREATE TABLE users AS SELECT * FROM raw_users
            JSON: {{"table_name": "users", "source_tables": ["raw_users"], "operation_type": "CREATE"}}
            """),
            ("human", "SQL Code:\n{sql}\n\nReturn JSON:")
        ])
        
        chain = prompt | self.llm
        
        try:
            response = chain.invoke({"sql": sql_content})
            content = response.content
            print(f"   🤖 LLM Response (First 50 chars): {content[:50]}...")
            
            # Basic cleanup if markdown blocks exist
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
                
            data = json.loads(content)
            return data
        except Exception as e:
            print(f"   ⚠️ Parsing Error: {e}")
            print(f"   📝 Processed Content Attempted: {content}")
            return None

    def process_directory(self, sql_dir: str, output_file: str):
        if not os.path.exists(sql_dir):
            print(f"❌ Directory not found: {sql_dir}")
            return

        print(f"\n📂 Scanning directory: {sql_dir}")
        graph_data = {"nodes": [], "edges": []}
        
        # 1. Iterate files
        for filename in os.listdir(sql_dir):
            if filename.endswith(".sql"):
                filepath = os.path.join(sql_dir, filename)
                print(f"   📄 Processing {filename}...")
                
                with open(filepath, "r") as f:
                    sql_content = f.read()
                
                # 2. Extract Lineage
                node_data = self.extract_lineage(sql_content)
                
                if node_data and "table_name" in node_data:
                    target = node_data["table_name"].lower()
                    sources = [s.lower() for s in node_data.get("source_tables", [])]
                    
                    print(f"      ✅ Target: {target}")
                    print(f"      🔗 Sources: {sources}")
                    
                    # Add Target Node
                    if target not in [n["id"] for n in graph_data["nodes"]]:
                        graph_data["nodes"].append({"id": target, "type": "table"})
                        
                    # Add Source Nodes
                    for source in sources:
                        if source not in [n["id"] for n in graph_data["nodes"]]:
                            graph_data["nodes"].append({"id": source, "type": "table"})
                        
                        # Add Edge
                        # Check existance to avoid dupes? json extraction list check is simpler
                        edge = {"source": source, "target": target}
                        if edge not in graph_data["edges"]:
                            graph_data["edges"].append(edge)
                            
        # 3. Save Output
        with open(output_file, "w") as f:
            json.dump(graph_data, f, indent=2)
        print(f"\n💾 Graph Data saved to: {output_file}")

if __name__ == "__main__":
    mapper = LineageMapper()
    
    base_dir = os.path.dirname(__file__)
    sql_folder = os.path.join(base_dir, "sql")
    output_json = os.path.join(base_dir, "graph_data.json")
    
    mapper.process_directory(sql_folder, output_json)
