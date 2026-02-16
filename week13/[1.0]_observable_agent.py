import os
import sys
import phoenix as px
from openinference.instrumentation.langchain import LangChainInstrumentor
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor

# Import Week 8 Agent Logic (Dynamic Import)
import importlib.util
week8_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../week8"))
if week8_path not in sys.path:
    sys.path.append(week8_path)

def load_agent_module():
    try:
        spec = importlib.util.spec_from_file_location("week8_agent", os.path.join(week8_path, "[3.0]_sql_agent.py"))
        module = importlib.util.module_from_spec(spec)
        sys.modules["week8_agent"] = module
        spec.loader.exec_module(module)
        return module.CostOptimizedSQLAgent
    except Exception as e:
        print(f"Error loading Week 8 agent: {e}")
        return None

if __name__ == "__main__":
    print("🚀 Launching Phoenix Observability Server...")
    # Launch Phoenix (Standard Local Mode)
    session = px.launch_app()
    print(f"🕵️  Phoenix UI: {session.url}")

    # Setup OpenTelemetry Tracer (to send spans to Phoenix)
    # Phoenix usually listens on http://127.0.0.1:6006/v1/traces
    endpoint = "http://127.0.0.1:6006/v1/traces"
    tracer_provider = TracerProvider()
    tracer_provider.add_span_processor(SimpleSpanProcessor(OTLPSpanExporter(endpoint)))
    trace.set_tracer_provider(tracer_provider) # Set Global

    # Instrument LangChain
    LangChainInstrumentor().instrument()

    # Initialize Agent
    AgentClass = load_agent_module()
    if AgentClass:
        print("🤖 Initializing Observable SQL Agent...")
        agent = AgentClass()
        
        # Metadata-Rich Context (Simulated)
        # Note: OpenInference captures generic spans. Custom attributes can be added via context.
        
        queries = [
            "How many users are in the system?",
            "What is the most expensive product?",
            "Show me the schema for orders.",
            "Generate a report of sales by region."
        ]
        
        print("\n🧪 Running Traced Queries:")
        for i, q in enumerate(queries):
            print(f"\n📝 [{i+1}/{len(queries)}] Question: {q}")
            try:
                # Execution is automatically traced!
                response = agent.run(q)
                print(f"✅ Answer: {response[:100].replace(chr(10), ' ')}...")
            except Exception as e:
                print(f"❌ Error: {e}")
        
        print(f"\n📊 View Traces at: {session.url}")
        print("   (Use Ctrl+C to stop server)")
        
        # Keep alive
        try:
             # Just wait
             import time
             while True:
                 time.sleep(1)
        except KeyboardInterrupt:
             print("\n👋 Stopping Phoenix...")
