import os
import sys
import importlib.util
from typing import List, Dict, Any, Optional
from langchain_core.tools import tool
from langchain_ollama import ChatOllama
from langchain_core.prompts import PromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from dotenv import load_dotenv

# Load Env
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../.env"))

# --- 1. Load Graph Builder (Dynamic Import) ---
def load_module(file_path, module_name):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

graph_mod_path = os.path.join(os.path.dirname(__file__), "[2.0]_graph_builder.py")
if not os.path.exists(graph_mod_path):
    print("❌ Graph Builder module not found. Run [2.0] first.")
    sys.exit(1)

graph_mod = load_module(graph_mod_path, "graph_builder")
GraphBuilder = graph_mod.GraphBuilder

# Initialize Graph
json_path = os.path.join(os.path.dirname(__file__), "graph_data.json")
builder = GraphBuilder(json_path)
if os.path.exists(json_path):
    builder.load_graph()
else:
    print("⚠️ Warning: graph_data.json not found. Tools will return empty results.")

# --- 2. Define Tools ---
@tool
def get_upstream_tables(table_name: str) -> str:
    """Finds source tables that the given table depends on."""
    try:
        deps = builder.get_upstream(table_name.strip())
        if not deps:
             return f"Table '{table_name}' has no upstream dependencies found."
        return f"SOURCES for '{table_name}': {', '.join(deps)}"
    except Exception as e:
        return f"Error: {e}"

@tool
def get_downstream_tables(table_name: str) -> str:
    """Finds tables that depend on the given table (Impact Analysis)."""
    try:
        deps = builder.get_downstream(table_name.strip())
        if not deps:
             return f"Table '{table_name}' has no downstream dependents found."
        return f"IMPACT analysis for '{table_name}': {', '.join(deps)}"
    except Exception as e:
        return f"Error: {e}"

# --- 3. Custom ReAct Agent Loop (Robust & Dependency-Free) ---
class ReActGraphAgent:
    def __init__(self, model_name: str, tools: List[Any]):
        self.llm = ChatOllama(model=model_name, temperature=0)
        self.tools = {t.name: t for t in tools}
        
        # Build System Prompt
        tool_descriptions = "\n".join([f"- {t.name}: {t.description}" for t in tools])
        tool_names = ", ".join(self.tools.keys())
        
        self.system_prompt = f"""You are a Graph RAG Assistant. You have access to a Knowledge Graph of the data warehouse.
        
        TOOLS AVAILABLE:
        {tool_descriptions}
        
        FORMAT:
        To solve a question, you can use a tool by outputting:
        Action: [tool_name]
        Action Input: [input_string]
        
        The user will reply with:
        Observation: [tool_result]
        
        When you have the answer, output:
        Final Answer: [your answer]
        
        RULES:
        1. Always look up dependencies if asked about lineage or impact.
        2. Use the exact tool name.
        3. Only use one action at a time.
        
        Begin!
        """

    def run(self, query: str):
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=f"Question: {query}")
        ]
        
        print(f"\n🤖 Processing: '{query}'")
        
        # Max steps to prevent infinite loops
        for step in range(8):
            # 1. Get LLM Response
            response = self.llm.invoke(messages)
            content = response.content
            
            # Print thought process (cleaning up newlines for display)
            thought = content.split("Action:")[0].strip()
            if thought:
                print(f"   💭 Thought: {thought[:100]}...")
            
            messages.append(AIMessage(content=content))
            
            # 2. Parse Action
            if "Final Answer:" in content:
                final_answer = content.split("Final Answer:")[1].strip()
                print(f"   ✅ Answer: {final_answer}")
                return final_answer
                
            if "Action:" in content and "Action Input:" in content:
                try:
                    action_part = content.split("Action:")[1].strip()
                    tool_name = action_part.split("Action Input:")[0].strip()
                    tool_input = action_part.split("Action Input:")[1].strip()
                    
                    # Execute Tool
                    if tool_name in self.tools:
                        print(f"   🛠️ Executing: {tool_name}('{tool_input}')")
                        observation = self.tools[tool_name].invoke(tool_input)
                    else:
                        observation = f"Error: Tool '{tool_name}' not found. Available: {list(self.tools.keys())}"
                        
                    print(f"   👀 Observation: {observation}")
                    
                    # Feed back to LLM
                    messages.append(HumanMessage(content=f"Observation: {observation}"))
                    
                except Exception as e:
                    print(f"   ⚠️ Parsing Error: {e}")
                    messages.append(HumanMessage(content=f"Error parsing action. strict format: Action: [name]\\nAction Input: [input]"))
            else:
                # LLM didn't follow format or is chatting
                print(f"   ⚠️ Model didn't output an action. Retrying...")
                messages.append(HumanMessage(content="Please use the format: Action: [tool] \n Action Input: [input] OR Final Answer: [answer]"))

        return "Agent Timeout"

# --- Main Execution ---
if __name__ == "__main__":
    # Use small model for speed, or main model for better reasoning
    model = os.getenv("SMALL_LLM", "qwen2.5-coder:1.5b")
    
    agent = ReActGraphAgent(model, [get_upstream_tables, get_downstream_tables])
    
    # Query 1
    agent.run("Where does fct_orders come from?")
    
    # Query 2
    agent.run("If I drop the raw_users table, what downstream tables will break?")
