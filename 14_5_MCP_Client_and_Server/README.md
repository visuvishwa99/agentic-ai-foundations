# Week 14.5: Model Context Protocol (MCP)

**Goal**: Build context-aware agents that can dynamically access your data stack (files, databases, tools) using Anthropic's Model Context Protocol (MCP).

## Weekly Goals
1.  **Understand MCP**: Protocol architecture (Client, Host, Server).
2.  **Build a Server**: Create a custom MCP server to expose local files or database schemas.
3.  **Integrate Client**: Connect an LLM agent (LangChain) to your MCP server.
4.  **Productionize**: Use MCP for code-aware data agents.

## Resources
- [Official MCP Documentation](https://modelcontextprotocol.io) - *Start here*
- [Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [Smithery.ai](https://smithery.ai) - *Catalog of MCP servers*

## Architecture: The Code-Aware Data Agent

### 1. The MCP Client (Agent) - **Entry Point**
**Implemented in:** `[1.0]_mcp_client.py`
-   **Role**: The "Brain" that uses the server.
-   **Tech**: LangChain `MCPClient`, Anthropic API.
-   **Flow**:
    1.  User asks: "Why did the sales job fail?"
    2.  Agent lists files -> finds `sales_job.py`.
    3.  Agent reads logs -> finds error.
    4.  Agent proposes fix.

### 2. The MCP Server - **Backend**
**Implemented in:** `[2.0]_mcp_server.py`
-   **Role**: Exposes tools and resources to the agent.
-   **Tech**: `mcp` Python SDK, `FastAPI` (for SSE) or `stdio`.
-   **Capabilities**:
    -   `list_files`: Read local project structure.
    -   `read_file`: Get file content.
    -   `query_db`: Execute valid SQL.

### 3. Configuration & Testing
**Implemented in:** `[3.0]_inspector.py` or straight text config.
-   **Debugging**: Use the [MCP Inspector](https://github.com/modelcontextprotocol/inspector) to test server availability.

## Jargon Buster

| Term | Simple Definition | Technical Context | DE Equivalent |
| :--- | :--- | :--- | :--- |
| **MCP** | USB-C for AI apps. | Standard protocol for tool/context exchange. | **ODBC/JDBC Driver** |
| **Resource** | Data the AI can read. | File contents, database rows, logs. | **Read-Only View** |
| **Tool** | Functions the AI can call. | `execute_query(sql)`, `api_post()`. | **Stored Procedure** |
| **Prompt** | Pre-defined templates. | "Review this PR", "Debug this error". | **Jinja Template** |
| **Transport** | How they talk. | `stdio` (pipe) or `SSE` (HTTP). | **TCP/IP or Pipe** |

## Experiments & Deliverables
-   [ ] **Simple Server**: Build a "File System" MCP server.
-   [ ] **Connect Claude**: Configure Claude Desktop to use your server.
-   [ ] **Agent Client**: Build a python script that queries your server.

## How to Run

### Option 1: Run the Automated Client (Recommended)
This script simulates an agent. It automatically launches the server and performs a sequence of tasks (Listing resources, reading catalog, querying data).
```bash
python 14_5_MCP_Client_and_Server/[1.0]_mcp_client.py
```

### Option 2: Run the Interactive Inspector (Debugging)
This launches a web UI where you can manually click buttons to test your server's tools and resources.
```bash
python 14_5_MCP_Client_and_Server/[3.0]_inspector.py
```
*Note: This requires Node.js/npx installed.*

### [IMPORTANT]
**Do NOT run `[2.0]_mcp_server.py` directly.**
It uses `stdio` communication and will just hang waiting for a machine to talk to it. It is meant to be launched *by* the client or inspector.
