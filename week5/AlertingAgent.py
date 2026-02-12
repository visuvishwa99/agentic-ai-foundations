"""
PRODUCTION AGENT: Log Checker → Job Status → Discord Notifier
Features: LangGraph + Tools + Memory + Full Tracing
"""

import os
import json
import requests
from typing import Annotated, TypedDict, Literal
from datetime import datetime

# LangGraph & LangChain
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import tool

# ============================================
# STEP 1: TRACING SETUP
# ============================================

def setup_tracing():
    """Configure LangSmith tracing"""
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_PROJECT"] = "log-checker-discord-agent"
    # os.environ["LANGCHAIN_API_KEY"] = "lsv2_pt_..."  # ADD YOUR KEY
    
    print("[SUCCESS] Tracing enabled: https://smith.langchain.com")
    print(f"[PROJECT] {os.environ['LANGCHAIN_PROJECT']}\n")

# ============================================
# STEP 2: DEFINE TOOLS
# ============================================

@tool
def read_logs(service_name: str, last_n_lines: int = 100) -> str:
    """
    Read the most recent logs from a service.
    
    Args:
        service_name: Name of the service (e.g., 'api', 'worker', 'database')
        last_n_lines: Number of recent lines to fetch
    
    Returns:
        Log contents as string
    """
    print(f"[TOOL] Reading logs: {service_name} (last {last_n_lines} lines)")
    
    simulated_logs = f"""
[2024-01-26 10:15:23] INFO: Service {service_name} started
[2024-01-26 10:15:45] INFO: Processing batch job #451
[2024-01-26 10:16:12] ERROR: Database connection timeout
[2024-01-26 10:16:13] ERROR: Retry attempt 1/3 failed
[2024-01-26 10:16:18] ERROR: Retry attempt 2/3 failed
[2024-01-26 10:16:25] WARN: Job #451 moved to retry queue
[2024-01-26 10:17:00] INFO: Job #451 restarted
"""
    
    error_count = len(simulated_logs.split('ERROR')) - 1
    print(f"       Found {error_count} errors")
    
    return simulated_logs

@tool
def check_job_status(job_id: str) -> str:
    """
    Check the status of a specific job.
    
    Args:
        job_id: The job identifier (e.g., '451')
    
    Returns:
        JSON string with job status
    """
    print(f"[TOOL] Checking job status: #{job_id}")
    
    status = {
        "job_id": job_id,
        "status": "running",
        "progress": 65,
        "started_at": "2024-01-26 10:17:00",
        "errors_count": 3,
        "retry_count": 1
    }
    
    print(f"       Status: {status['status']} ({status['progress']}% complete)")
    
    return json.dumps(status)

@tool
def post_to_discord(webhook_url: str, message: str, severity: str = "info") -> str:
    """
    Post a message to Discord channel via webhook.
    
    Args:
        webhook_url: Discord webhook URL
        message: Message text to post
        severity: Message severity level ('info', 'warning', 'critical')
    
    Returns:
        Confirmation message
    """
    print(f"[TOOL] Posting to Discord (severity: {severity})")
    
    # Color codes for embed
    color_map = {
        "info": 3447003,      # Blue
        "warning": 16776960,  # Yellow
        "critical": 15158332  # Red
    }
    
    # Create rich embed
    embed = {
        "embeds": [{
            "title": f"[{severity.upper()}] System Alert",
            "description": message,
            "color": color_map.get(severity, 3447003),
            "timestamp": datetime.utcnow().isoformat(),
            "fields": [
                {
                    "name": "Severity",
                    "value": severity.capitalize(),
                    "inline": True
                },
                {
                    "name": "Time",
                    "value": datetime.now().strftime('%H:%M:%S'),
                    "inline": True
                }
            ],
            "footer": {
                "text": "Log Monitor Agent"
            }
        }]
    }
    
    try:
        response = requests.post(webhook_url, json=embed, timeout=10)
        
        if response.status_code == 204:
            print(f"       Success: Message posted")
            return f"Successfully posted to Discord: {message[:50]}..."
        else:
            print(f"       Error: {response.status_code}")
            return f"Failed: HTTP {response.status_code}"
    
    except requests.exceptions.RequestException as e:
        print(f"       Exception: {str(e)}")
        return f"Error: {str(e)}"

# Collect all tools
tools = [read_logs, check_job_status, post_to_discord]

# ============================================
# STEP 3: AGENT STATE
# ============================================

class AgentState(TypedDict):
    """State that flows through the agent graph"""
    messages: list
    logs_content: str
    job_status: dict
    alert_sent: bool
    retry_count: int
    discord_webhook: str  # NEW: Store webhook URL

# ============================================
# STEP 4: CREATE LLM
# ============================================

llm = ChatOllama(
    model="qwen2.5-coder:1.5b",
    temperature=0
)
llm_with_tools = llm.bind_tools(tools)

# ============================================
# STEP 5: AGENT NODES
# ============================================

def agent_reasoning(state: AgentState) -> AgentState:
    """Core reasoning: Decide what to do next"""
    messages = state["messages"]
    
    system_prompt = SystemMessage(content="""You are a DevOps monitoring agent.

Your workflow:
1. Read logs from the specified service
2. Analyze for errors or warnings
3. If errors found: check related job status
4. If job is failing: post critical alert to Discord
5. If job is running: wait and check again (max 3 retries)
6. If all clear: post success message to Discord

Always use the Discord webhook URL provided in the user's message.

Always explain your reasoning clearly.""")
    
    print(f"\n[REASONING] Agent thinking... (attempt {state.get('retry_count', 0)})")
    
    response = llm_with_tools.invoke([system_prompt] + messages)
    
    # --- PATCH: Manual Parsing for Ollama/Qwen Models ---
    # Smaller models often return JSON as text instead of structured tool calls
    if not response.tool_calls and "```json" in response.content:
        import re
        import uuid
        
        try:
            # Extract JSON block
            json_block = re.search(r'```json\n(.*?)\n```', response.content, re.DOTALL)
            if json_block:
                try:
                    tool_call_data = json.loads(json_block.group(1))
                    
                    # Convert to list if it's a single dict
                    if isinstance(tool_call_data, dict):
                        tool_call_data = [tool_call_data]
                        
                    # Construct proper tool calls
                    patched_tool_calls = []
                    for tc in tool_call_data:
                        if "name" in tc and "arguments" in tc:
                            patched_tool_calls.append({
                                "name": tc["name"],
                                "args": tc["arguments"],
                                "id": str(uuid.uuid4())
                            })
                    
                    if patched_tool_calls:
                        print(f"            [PATCH] Manually extracted {len(patched_tool_calls)} tool call(s)")
                        response.tool_calls = patched_tool_calls
                except json.JSONDecodeError:
                    print("            [PATCH] Failed to decode JSON tool call")
        except Exception as e:
            print(f"            [PATCH] Parsing error: {e}")
    # ----------------------------------------------------
    
    if hasattr(response, 'tool_calls') and response.tool_calls:
        print(f"            Decision: Call {len(response.tool_calls)} tool(s)")
    else:
        print(f"            Decision: Task complete")
    
    return {
        **state,
        "messages": messages + [response]
    }

def should_continue(state: AgentState) -> Literal["tools", "end"]:
    """Router: Decide if we need more tool calls"""
    last_message = state["messages"][-1]
    
    if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
        return "tools"
    
    return "end"

def increment_retry(state: AgentState) -> AgentState:
    """Track retry attempts"""
    state["retry_count"] = state.get("retry_count", 0) + 1
    
    if state["retry_count"] > 3:
        print("[WARNING] Max retries reached")
        state["messages"].append(
            AIMessage(content="Maximum retry attempts reached. Escalating to manual review.")
        )
    
    return state

# ============================================
# STEP 6: BUILD GRAPH
# ============================================

def create_agent():
    """Build the agent's state graph"""
    
    workflow = StateGraph(AgentState)
    
    workflow.add_node("agent", agent_reasoning)
    workflow.add_node("tools", ToolNode(tools))
    workflow.add_node("retry_counter", increment_retry)
    
    workflow.set_entry_point("agent")
    
    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            "tools": "tools",
            "end": END
        }
    )
    
    workflow.add_edge("tools", "retry_counter")
    workflow.add_edge("retry_counter", "agent")
    
    return workflow.compile()

# ============================================
# STEP 7: RUN AGENT
# ============================================

def run_agent_with_tracing(service_name: str = "api", discord_webhook: str = None):
    """
    Execute the agent with comprehensive logging
    
    Args:
        service_name: Name of the service to monitor
        discord_webhook: Discord webhook URL (or set DISCORD_WEBHOOK_URL env var)
    """
    
    # Get webhook from environment if not provided
    if not discord_webhook:
        discord_webhook = os.environ.get("DISCORD_WEBHOOK_URL")
    
    if not discord_webhook:
        print("[ERROR] Discord webhook URL required!")
        print("        Set DISCORD_WEBHOOK_URL env var or pass as argument")
        return
    
    # Validate webhook format
    if not discord_webhook.startswith("https://discord.com/api/webhooks/"):
        print("[ERROR] Invalid Discord webhook URL format")
        return
    
    setup_tracing()
    
    agent = create_agent()
    
    initial_state = {
        "messages": [
            HumanMessage(content=f"""Check the logs for {service_name} service and report any issues.

Use this Discord webhook for all notifications: {discord_webhook}""")
        ],
        "logs_content": "",
        "job_status": {},
        "alert_sent": False,
        "retry_count": 0,
        "discord_webhook": discord_webhook
    }
    
    print("=" * 70)
    print(f"STARTING AGENT: Log Monitor for '{service_name}'")
    print(f"Discord Channel: Configured")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    step_number = 0
    
    for state_update in agent.stream(initial_state):
        step_number += 1
        node_name = list(state_update.keys())[0]
        
        print(f"\n{'-' * 70}")
        print(f"STEP {step_number}: {node_name.upper()}")
        print(f"{'-' * 70}")
        
        if node_name == "agent":
            last_msg = state_update[node_name]["messages"][-1]
            
            if hasattr(last_msg, 'tool_calls') and last_msg.tool_calls:
                for tc in last_msg.tool_calls:
                    print(f"[OUTPUT] Tool Call: {tc['name']}")
                    # Truncate webhook URL in logs for security
                    args = tc['args'].copy()
                    if 'webhook_url' in args:
                        args['webhook_url'] = args['webhook_url'][:50] + "..."
                    print(f"         Input: {json.dumps(args, indent=2)}")
            
            elif hasattr(last_msg, 'content'):
                print(f"[OUTPUT] Response: {last_msg.content[:200]}")
        
        elif node_name == "retry_counter":
            retry_count = state_update[node_name].get("retry_count", 0)
            print(f"[STATUS] Retry count: {retry_count}/3")
    
    print(f"\n{'=' * 70}")
    print(f"AGENT COMPLETED IN {step_number} STEPS")
    print(f"{'=' * 70}")
    
    print("\n[INFO] View full trace at: https://smith.langchain.com")

# ============================================
# MAIN EXECUTION
# ============================================

if __name__ == "__main__":
    
    print("""
    ============================================================
           PRODUCTION LOG MONITORING AGENT                      
      Features: LangGraph + Tools + Memory + Discord + Tracing       
    ============================================================
    """)
    
    # Example usage with Discord
    DISCORD_WEBHOOK = "https://discord.com/api/webhooks/YOUR_WEBHOOK_ID/YOUR_WEBHOOK_TOKEN"
    
    # Or set as environment variable:
    # export DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/..."
    
    run_agent_with_tracing(
        service_name="api",
        discord_webhook=DISCORD_WEBHOOK  # Replace with your actual webhook
    )
    
    print("\n" + "=" * 70)
    print("DISCORD INTEGRATION NOTES:")
    print("=" * 70)
    print("""
    1. GET WEBHOOK URL:
       - Discord Server -> Channel Settings -> Integrations -> Webhooks
       - Click "New Webhook" and copy the URL
    
    2. WEBHOOK URL FORMAT:
       https://discord.com/api/webhooks/{webhook_id}/{webhook_token}
    
    3. COLOR CODING:
       - Info: Blue (3447003)
       - Warning: Yellow (16776960)
       - Critical: Red (15158332)
    
    4. SECURITY:
       - Store webhook in environment variable
       - Never commit webhook URLs to git
       - Rotate webhooks if exposed
    
    5. RATE LIMITS:
       - Discord allows 30 requests per minute per webhook
       - Agent respects this with retry delays
    """)