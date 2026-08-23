from __future__ import annotations

import asyncio
import importlib.util
import json
import sys
import types
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
WEEK8_DIRECTORY = "08_Model_Routing_and_SQL_Agent"


@pytest.mark.parametrize(
    "relative_path",
    [
        "09_Secure_Agent_and_Guards/[3.0]_secure_agent.py",
        "11_Interactive_Agent_and_Human_Review/[3.0]_interactive_agent.py",
        "13_Observable_Agent_and_Dashboard/[1.0]_observable_agent.py",
        "13_Observable_Agent_and_Dashboard/[2.0]_regression_test.py",
        "13_Observable_Agent_and_Dashboard/[3.0]_dashboard.py",
        "14_Agent_API_and_Docker/[1.0]_agent_api.py",
    ],
)
def test_week8_consumers_reference_existing_module(relative_path: str) -> None:
    source_path = ROOT / relative_path
    source = source_path.read_text(encoding="utf-8")

    assert "../week8" not in source
    assert WEEK8_DIRECTORY in source
    assert (ROOT / WEEK8_DIRECTORY / "[3.0]_sql_agent.py").is_file()


def load_metrics_module():
    dependency = types.ModuleType("dataops_memory_agent")
    dependency.DataOpsMemoryAgent = object
    dependency.PipelineFailure = object
    original = sys.modules.get("dataops_memory_agent")
    sys.modules["dataops_memory_agent"] = dependency
    try:
        module_path = ROOT / "06_DataOps_Memory_Agent/generate_metrics.py"
        spec = importlib.util.spec_from_file_location("revision_metrics", module_path)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    finally:
        if original is None:
            sys.modules.pop("dataops_memory_agent", None)
        else:
            sys.modules["dataops_memory_agent"] = original


class EmptyAgent:
    def get_memory_stats(self) -> dict:
        return {
            "total_failures_in_memory": 0,
            "recent_failures_count": 0,
            "error_type_distribution": {},
        }


def test_metrics_report_fails_below_threshold_suggestion_quality() -> None:
    metrics = load_metrics_module()
    report = metrics.generate_metrics_report(
        EmptyAgent(),
        {
            "classification_accuracy": 100.0,
            "pattern_accuracy": 90.0,
            "suggestion_quality": 79.0,
            "overall_score": 89.0,
        },
    )

    assert "Target: 80%+ Suggestion Quality       Status: FAIL" in report


def test_write_reports_uses_requested_output_directory(tmp_path: Path) -> None:
    metrics = load_metrics_module()

    text_path, html_path = metrics.write_reports(
        tmp_path,
        "revision metrics",
        "<html>revision dashboard</html>",
    )

    assert text_path == tmp_path / "metrics_report.txt"
    assert html_path == tmp_path / "dashboard.html"
    assert text_path.read_text(encoding="utf-8") == "revision metrics"
    assert html_path.read_text(encoding="utf-8") == "<html>revision dashboard</html>"


def test_dashboard_labels_synthetic_threshold_evidence() -> None:
    metrics = load_metrics_module()
    dashboard = metrics.generate_html_dashboard(
        EmptyAgent(),
        {
            "classification_accuracy": 100.0,
            "pattern_accuracy": 90.0,
            "suggestion_quality": 100.0,
            "overall_score": 96.7,
        },
    )

    assert "MEETS SYNTHETIC TEST THRESHOLD" in dashboard
    assert "PRODUCTION READY" not in dashboard


def test_mcp_catalog_fixture_is_module_local() -> None:
    fixture_path = ROOT / "14_5_MCP_Client_and_Server/data/catalog_metadata.json"

    assert fixture_path.is_file()
    fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
    assert {table["name"] for table in fixture["tables"]} == {
        "sales_transactions",
        "customer_profiles",
    }


def test_mcp_v2_server_discovers_and_invokes_revision_tools() -> None:
    module_path = ROOT / "14_5_MCP_Client_and_Server/[2.0]_mcp_server.py"
    spec = importlib.util.spec_from_file_location("revision_mcp_server", module_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    async def exercise_server() -> None:
        tools = await module.server.list_tools()
        resources = await module.server.list_resources()
        result = await module.server.call_tool(
            "get_table_schema",
            {"table_name": "sales_transactions"},
        )

        assert {tool.name for tool in tools} == {
            "get_table_schema",
            "query_sample_data",
        }
        assert {str(resource.uri) for resource in resources} == {"catalog://metadata"}
        assert "transaction_id" in str(result)

    asyncio.run(exercise_server())


def test_mcp_v2_client_discovers_revision_server() -> None:
    module_path = ROOT / "14_5_MCP_Client_and_Server/[1.0]_mcp_client.py"
    spec = importlib.util.spec_from_file_location("revision_mcp_client", module_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    summary = asyncio.run(module.run_client())

    assert summary["tools"] == ["get_table_schema", "query_sample_data"]
    assert summary["resources"] == ["catalog://metadata"]
    assert "transaction_id" in summary["schema"]


def load_lm_studio_backend():
    module_path = ROOT / "08_Model_Routing_and_SQL_Agent/lm_studio_backend.py"
    spec = importlib.util.spec_from_file_location("revision_lm_studio_backend", module_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_lm_studio_json_parser_accepts_fenced_qwen_response() -> None:
    backend = load_lm_studio_backend()

    parsed = backend.parse_json_object(
        '```json\n{"complexity":"SIMPLE","reasoning":"revision smoke test"}\n```'
    )

    assert parsed == {
        "complexity": "SIMPLE",
        "reasoning": "revision smoke test",
    }


@pytest.mark.parametrize(
    "relative_path",
    [
        "08_Model_Routing_and_SQL_Agent/[1.0]_model_router.py",
        "08_Model_Routing_and_SQL_Agent/[2.0]_semantic_cache.py",
        "08_Model_Routing_and_SQL_Agent/[3.0]_sql_agent.py",
        "08_Model_Routing_and_SQL_Agent/[4.0]_cost_monitor.py",
    ],
)
def test_week8_modules_use_shared_lm_studio_backend(relative_path: str) -> None:
    source = (ROOT / relative_path).read_text(encoding="utf-8")

    assert "langchain_ollama" not in source
    assert "lm_studio_backend" in source


def test_alerting_optional_services_are_environment_gated() -> None:
    source = (ROOT / "05_Alerting_Agent/AlertingAgent.py").read_text(encoding="utf-8")

    assert 'os.getenv("LANGCHAIN_API_KEY")' in source
    assert 'os.getenv("DISCORD_WEBHOOK_URL", "")' in source
    assert "YOUR_WEBHOOK_ID" not in source
