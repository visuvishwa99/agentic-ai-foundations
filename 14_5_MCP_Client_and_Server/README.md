# Week 14.5: MCP client and server

This started as a small MCP v1 example. By the time I reopened it, the Python SDK had moved to v2 and the old decorators no longer loaded. I kept the example small while migrating it: one resource, two tools, and one client that proves the pieces can talk to each other.

The data is synthetic. Nothing connects to a real warehouse.

## Files

- `[2.0]_mcp_server.py` exposes one catalog resource and two tools with the MCP Python SDK v2.
- `[1.0]_mcp_client.py` connects to the server, lists what is available, reads the catalog, and calls `get_table_schema`.
- `data/catalog_metadata.json` is the small catalog fixture used by both examples.
- `[3.0]_inspector.py` starts the MCP Inspector through `npx`.

The server exposes:

- `catalog://metadata`
- `get_table_schema`
- `query_sample_data`

`query_sample_data` returns labeled mock rows. It does not execute SQL.

## Install

From the repository root:

```bash
pip install -r 14_5_MCP_Client_and_Server/requirements.txt
```

The dependency stays on MCP v2:

```text
mcp>=2,<3
```

The original version used the v1 low-level decorators. `pip install mcp` now installs v2, so the server uses `MCPServer` and the client uses the v2 `Client` API.

## Run the client

```bash
python "14_5_MCP_Client_and_Server/[1.0]_mcp_client.py"
```

The client should print both tool names, the catalog resource URI, and the schema for `sales_transactions`.

## Use the Inspector

```bash
python "14_5_MCP_Client_and_Server/[3.0]_inspector.py"
```

The Inspector needs Node.js and `npx`.

Running `[2.0]_mcp_server.py` directly starts a stdio server and waits for an MCP client. That is expected.

## Things I tend to forget

- Can the client discover the resource and both tools?
- Does `get_table_schema` reject an unknown table cleanly?
- Is every returned value clearly labeled as synthetic?
- Am I testing through an MCP client instead of calling only the Python function?
