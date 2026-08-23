"""Synthetic data-catalog MCP server for revision exercises."""

from __future__ import annotations

import json
from pathlib import Path

from mcp.server import MCPServer


server = MCPServer(
    name="data-catalog-server",
    version="0.2.0",
    instructions=(
        "Use the catalog resource and tools to inspect the synthetic warehouse. "
        "All returned records and schemas are learning fixtures."
    ),
)

CATALOG_PATH = Path(__file__).resolve().parent / "data" / "catalog_metadata.json"


def load_catalog() -> dict:
    """Load the module-local synthetic catalog fixture."""
    if not CATALOG_PATH.is_file():
        raise FileNotFoundError(f"Synthetic catalog fixture not found: {CATALOG_PATH}")
    return json.loads(CATALOG_PATH.read_text(encoding="utf-8"))


def find_table(table_name: str) -> dict | None:
    """Return one table definition by exact synthetic catalog name."""
    catalog = load_catalog()
    return next(
        (table for table in catalog.get("tables", []) if table["name"] == table_name),
        None,
    )


@server.resource(
    "catalog://metadata",
    name="Data Catalog Metadata",
    description="JSON schema for the synthetic data warehouse",
    mime_type="application/json",
)
def catalog_metadata() -> str:
    """Return the complete synthetic catalog as formatted JSON."""
    return json.dumps(load_catalog(), indent=2)


@server.tool()
def get_table_schema(table_name: str) -> str:
    """Return column names, types, and descriptions for a synthetic table."""
    table = find_table(table_name)
    if table is None:
        return f"Table '{table_name}' not found in synthetic catalog."

    columns = "\n".join(
        f"- {column['name']} ({column['type']}): {column['description']}"
        for column in table["columns"]
    )
    return f"Schema for {table_name}:\n{columns}"


@server.tool()
def query_sample_data(table_name: str) -> str:
    """Return a clearly labeled mock sample for a synthetic catalog table."""
    if find_table(table_name) is None:
        return f"Table '{table_name}' not found in synthetic catalog."
    return (
        f"Synthetic sample data for {table_name}:\n"
        "[Row 1, Row 2, Row 3] (mock values; no database query executed)"
    )


if __name__ == "__main__":
    server.run(transport="stdio")
