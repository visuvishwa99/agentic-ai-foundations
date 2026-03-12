import os
import sys
import phoenix as px
from openinference.instrumentation.langchain import LangChainInstrumentor
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
import pandas as pd
import time

# Helper Load Agent
import importlib.util
week8_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../week8"))
if week8_path not in sys.path:
    sys.path.append(week8_path)

def load_agent():
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
    print("🚀 Stimulating Traffic for Dashboard Analysis...")
    
    # Launch App (Persistent or New)
    session = px.launch_app()
    
    # Setup Tracing
    tracer_provider = TracerProvider()
    tracer_provider.add_span_processor(SimpleSpanProcessor(OTLPSpanExporter("http://127.0.0.1:6006/v1/traces")))
    trace.set_tracer_provider(tracer_provider)
    LangChainInstrumentor().instrument()
    
    # Run Batch Traffic
    agent_cls = load_agent()
    if agent_cls:
        agent = agent_cls()
        
        # diverse queries to form clusters
        topic_a = ["How many users?", "Count custom_users", "Total users in db", "User count please"]
        topic_b = ["Show me sales", "Revenue report", "Total income", "Sales by region"]
        topic_c = ["Drop table users", "Delete data", "Remove all records"] # Risky
        
        all_queries = topic_a + topic_b + topic_c
        
        print(f"🧪 Sending {len(all_queries)} queries...")
        for q in all_queries:
            try:
                print(f"   Running: {q}")
                agent.run(q)
            except:
                pass
                
        # Wait for spans to arrive
        time.sleep(2)
        
        # Analyze via Session API
        try:
             spans_df = px.active_session().get_spans_dataframe()
             if not spans_df.empty:
                 print("\n📊 Dashboard Analytics:")
                 print(f"   Total Spans Captured: {len(spans_df)}")
                 print(f"   Unique Trace IDs: {spans_df['trace_id'].nunique()}")
                 
                 # Check for errors
                 errors = spans_df[spans_df['status_code'] == 'ERROR']
                 print(f"   Error Count: {len(errors)}")
                 
                 print(f"\n✨ View Clusters in UI: {session.url}")
                 print("   Navigate to 'Clusters' tab to see topic grouping!")
             else:
                 print("⚠️ No spans captured yet. Check UI manually.")
                 
        except Exception as e:
             print(f"⚠️ Could not analyze local spans (might be async): {e}")

        # Keep server running
        print("\n(Press Ctrl+C to stop dashboard)")
        while True:
            time.sleep(1)
