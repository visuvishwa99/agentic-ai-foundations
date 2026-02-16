import langchain
import langchain_community
print(f"LangChain Version: {langchain.__version__}")
try:
    import langchain.agents
    print("langchain.agents successfully imported")
    print("Agents Attributes:", [x for x in dir(langchain.agents) if "Agent" in x or "initialize" in x])
except Exception as e:
    print(f"Error importing langchain.agents: {e}")

try:
    from langchain.agents import initialize_agent
    print("initialize_agent OK")
except Exception as e:
    print(f"initialize_agent FAILED: {e}")

try:
    from langchain.agents import AgentExecutor
    print("AgentExecutor OK")
except Exception as e:
    print(f"AgentExecutor FAILED: {e}")
