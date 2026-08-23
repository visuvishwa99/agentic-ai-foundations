"""MCP v2 client for the synthetic data-catalog revision server."""

from __future__ import annotations

import asyncio
import importlib.util
from pathlib import Path

from mcp import Client


SERVER_SCRIPT = Path(__file__).resolve().parent / "[2.0]_mcp_server.py"


def load_server():
    """Load the sibling MCP server despite its lesson-numbered filename."""
    spec = importlib.util.spec_from_file_location("revision_data_catalog_server", SERVER_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load MCP server: {SERVER_SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.server


async def run_client() -> dict[str, object]:
    """Discover and exercise the synthetic MCP server through an MCP client."""
    server = load_server()
    print(f"[INFO] Connecting to MCP Server: {SERVER_SCRIPT}")

    async with Client(server) as client:
        tools = await client.list_tools()
        resources = await client.list_resources()
        resource_contents = await client.read_resource("catalog://metadata")
        schema_result = await client.call_tool(
            "get_table_schema",
            {"table_name": "sales_transactions"},
        )

    tool_names = [tool.name for tool in tools.tools]
    resource_uris = [str(resource.uri) for resource in resources.resources]
    schema_text = "\n".join(
        block.text for block in schema_result.content if hasattr(block, "text")
    )

    print("[SUCCESS] Connected to Server")
    print(f"[TOOLS] {', '.join(tool_names)}")
    print(f"[RESOURCES] {', '.join(resource_uris)}")
    print(f"[CATALOG PREVIEW] {str(resource_contents)[:100]}...")
    print(f"[SCHEMA]\n{schema_text}")

    return {
        "tools": tool_names,
        "resources": resource_uris,
        "schema": schema_text,
    }


if __name__ == "__main__":
    asyncio.run(run_client())
