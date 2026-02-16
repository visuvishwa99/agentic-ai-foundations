import os
import sys
import phoenix as px
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from openinference.instrumentation.langchain import LangChainInstrumentor
import pytest

# Load Agent Class (Reuse Week 8 Logic)
import importlib.util
week8_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../week8"))
if week8_path not in sys.path:
    sys.path.append(week8_path)

def load_agent_factory():
    try:
        spec = importlib.util.spec_from_file_location("week8_agent", os.path.join(week8_path, "[3.0]_sql_agent.py"))
        module = importlib.util.module_from_spec(spec)
        sys.modules["week8_agent"] = module
        spec.loader.exec_module(module)
        return module.CostOptimizedSQLAgent
    except Exception as e:
        print(f"Error loading Week 8 agent: {e}")
        return None

AgentClass = load_agent_factory()

# Setup Instrumentation (Only once per process)
if not trace.get_tracer_provider():
    # Setup Tracer
    tracer_provider = TracerProvider()
    # SimpleSpanProcessor sends spans immediately
    tracer_provider.add_span_processor(SimpleSpanProcessor(OTLPSpanExporter("http://127.0.0.1:6006/v1/traces")))
    trace.set_tracer_provider(tracer_provider)
    LangChainInstrumentor().instrument()

# Test Cases
class TestAgentCapabilities:
    @pytest.fixture(scope="module")
    def agent(self):
        # Setup Phoenix for test session
        px.launch_app() # Ensure server is running for traces
        return AgentClass()

    def test_basic_select(self, agent):
        """Verify simple SELECT query generation."""
        query = "Show me the top 5 users by creation date."
        response = agent.run(query)
        assert len(response) > 10
        assert "SELECT" in response or "Table" in response # Basic check
        print(f"\n[PASS] SELECT Generation: {response[:50]}...")

    def test_schema_awareness(self, agent):
        """Verify agent knows about schema objects."""
        query = "What columns are in the users table?"
        response = agent.run(query)
        # Assuming schema context is present
        # Week 8 agent uses Semantic Cache + Router. If cache miss -> complex query.
        assert "users" in response.lower()
        print(f"\n[PASS] Schema Awareness: {response[:50]}...")

    def test_complex_aggregation(self, agent):
        """Verify aggregation logic."""
        query = "Calculate the average order value per country."
        response = agent.run(query)
        assert "AVG" in response or "average" in response.lower()
        print(f"\n[PASS] Aggregation: {response[:50]}...")

if __name__ == "__main__":
    # Run tests programmatically
    print("🧪 Starting Automated Regression Suite...")
    # This invokes pytest on this file
    sys.exit(pytest.main(["-v", __file__]))
