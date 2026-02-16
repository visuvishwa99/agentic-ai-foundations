
import asyncio
import json
import logging
import os
from datetime import datetime

# Import MCP SDK
from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server

# Configure logging
logging.basicConfig(filename="server.log", level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger("mcp_server")

# Initialize the server
server = Server("data-catalog-server")

# Define our mock data source
CATALOG_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/catalog_metadata.json"))

def load_catalog():
    """Helper to load the mock catalog"""
    if not os.path.exists(CATALOG_PATH):
        return {"error": "Catalog file not found"}
    with open(CATALOG_PATH, "r") as f:
        return json.load(f)

# ---------------------------------------------------------------------
# Resource Handlers
# Resources are like "Files" the LLM can read
# ---------------------------------------------------------------------

@server.list_resources()
async def handle_list_resources() -> list[types.Resource]:
    """List available resources (our catalog file)"""
    return [
        types.Resource(
            uri="catalog://metadata",
            name="Data Catalog Metadata",
            description="The full JSON schema of our simulated Data Warehouse",
            mimeType="application/json",
        )
    ]

@server.read_resource()
async def handle_read_resource(uri: str) -> str | bytes:
    """Allow the LLM to read the full catalog"""
    logger.info(f"Read request for URI: '{uri}' (type: {type(uri)})")
    if str(uri) == "catalog://metadata":
        catalog = load_catalog()
        return json.dumps(catalog, indent=2)
    raise ValueError(f"Resource not found: {uri}")

# ---------------------------------------------------------------------
# Tool Handlers
# Tools are functions the LLM can call
# ---------------------------------------------------------------------

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List tools available to the LLM"""
    return [
        types.Tool(
            name="get_table_schema",
            description="Get the schema (columns, types) for a specific table",
            inputSchema={
                "type": "object",
                "properties": {
                    "table_name": {"type": "string", "description": "Name of the table (e.g., 'sales_transactions')"}
                },
                "required": ["table_name"],
            },
        ),
        types.Tool(
            name="query_sample_data",
            description="Get 5 sample rows from a table",
            inputSchema={
                "type": "object",
                "properties": {
                    "table_name": {"type": "string", "description": "Name of the table"}
                },
                "required": ["table_name"],
            },
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict | None) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Handle actual tool execution"""
    if not arguments:
        return [types.TextContent(type="text", text="Missing arguments")]
    
    table_name = arguments.get("table_name")
    catalog = load_catalog()
    table = next((t for t in catalog.get("tables", []) if t["name"] == table_name), None)

    if not table:
        return [types.TextContent(type="text", text=f"Table '{table_name}' not found in catalog.")]

    if name == "get_table_schema":
        # Format the schema nicely
        schema_str = f"Schema for {table_name}:\n"
        for col in table["columns"]:
            schema_str += f"- {col['name']} ({col['type']}): {col['description']}\n"
        return [types.TextContent(type="text", text=schema_str)]

    elif name == "query_sample_data":
        # Mocking some sample data dynamically
        return [types.TextContent(type="text", text=f"Sample Data for {table_name}:\n[Row 1, Row 2, Row 3] (Mock data)")]

    raise ValueError(f"Tool not found: {name}")

# ---------------------------------------------------------------------
# Main Enty Point
# ---------------------------------------------------------------------

async def main():
    # Run the server using stdin/stdout streams
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="data-catalog",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())
