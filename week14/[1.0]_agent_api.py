import os
import sys
import uvicorn
import asyncio
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
import uuid
import importlib.util

# 1. Setup FastAPI
app = FastAPI(
    title="Observable SQL Agent API",
    description="Week 14 Microservice wrapping the Week 13 Agent",
    version="1.0.0"
)

# 2. Load Agent Logic (Dynamic Import from Week 13)
# We assume [1.0]_observable_agent.py in Week 13 has the setup logic.
# However, Week 13 script launches Phoenix inline. We want just the Agent Class.
# Ideally, we reuse the Week 8 Agent class directly but wrap it with OpenTelemetry.

week8_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../week8"))
if week8_path not in sys.path:
    sys.path.append(week8_path)

def load_agent():
    try:
        spec = importlib.util.spec_from_file_location("week8_agent", os.path.join(week8_path, "[3.0]_sql_agent.py"))
        module = importlib.util.module_from_spec(spec)
        sys.modules["week8_agent"] = module
        spec.loader.exec_module(module)
        return module.CostOptimizedSQLAgent()
    except Exception as e:
        print(f"[ERROR] Failed to load agent: {e}")
        return None

# Global Agent Instance (Loaded on Startup)
agent_instance = None

@app.on_event("startup")
async def startup_event():
    global agent_instance
    print("[INFO] Startup: Loading Agent Model...")
    agent_instance = load_agent()
    # Note: OpenTelemetry instrumentation should happen at the process level
    # We assume 'opentelemetry-instrument' command or manual setup was done.
    if agent_instance:
        print("[INFO] Agent Loaded Successfully.")
    else:
        print("[ERROR] Agent Failed to Load.")

# 3. Define Request/Response Models
class QueryRequest(BaseModel):
    query: str = Field(..., example="How many users are active?")
    user_id: Optional[str] = Field("anonymous", example="user_123")

class QueryResponse(BaseModel):
    response: str
    trace_id: str
    status: str

# 4. Define Endpoints
@app.get("/health")
async def health_check():
    return {"status": "healthy", "agent_loaded": agent_instance is not None}

@app.post("/chat", response_model=QueryResponse)
async def chat_endpoint(request: QueryRequest, background_tasks: BackgroundTasks):
    """
    Main Chat Endpoint.
    - query: User's SQL/Data question.
    - Returns: Agent's answer.
    """
    if not agent_instance:
        raise HTTPException(status_code=503, detail="Agent not initialized")

    print(f"[INFO] Received Query from {request.user_id}: {request.query}")
    
    # Generate a Trace ID (Mocking it here, usually injected by OTel)
    trace_id = str(uuid.uuid4())
    
    try:
        # Run Agent (This is synchronous blocking call! In prod, run in threadpool)
        # Using asyncio.to_thread prevents blocking the main event loop
        response_text = await asyncio.to_thread(agent_instance.run, request.query)
        
        return QueryResponse(
            response=response_text,
            trace_id=trace_id,
            status="success"
        )
            
    except Exception as e:
        print(f"[ERROR] Agent Execution Failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    # Dev Server
    uvicorn.run(app, host="127.0.0.1", port=8000)
