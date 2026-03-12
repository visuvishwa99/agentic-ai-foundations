
import asyncio
import sys
import os

# Import MCP Client SDK
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Path to our server script
SERVER_SCRIPT = os.path.join(os.path.dirname(__file__), "[2.0]_mcp_server.py")

async def run_client():
    # define the server parameters (how to launch it)
    server_params = StdioServerParameters(
        command=sys.executable, # Use the current python interpreter
        args=[SERVER_SCRIPT], 
        env=None
    )

    print(f"[INFO] Connecting to MCP Server: {SERVER_SCRIPT}...")

    # Start the client connection context
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # 1. Initialize
            await session.initialize()
            print("[SUCCESS] Connected to Server!")

            # 2. List Resources
            print("\n[RESOURCES] Listing Resources:")
            try:
                resources = await session.list_resources()
                for res in resources.resources:
                    print(f" - {res.name} ({res.uri})")
            except Exception as e:
                print(f"Error listing resources: {e}")

            # 3. Read Resource content
            print("\n[READ] Reading Catalog Metadata:")
            try:
                # Note: In real usage, you'd pick a specific URI from the list
                content = await session.read_resource("catalog://metadata")
                print(f"Content Preview: {str(content.contents)[:100]}...")
            except Exception as e:
                print(f"Error reading resource: {e}")

            # 4. List Tools
            print("\n[TOOLS] Listing Tools:")
            try:
                tools = await session.list_tools()
                for tool in tools.tools:
                    print(f" - {tool.name}: {tool.description}")
            except Exception as e:
                print(f"Error listing tools: {e}")

            # 5. Call a Tool (Data Engineering Task)
            print("\n[EXECUTE] Calling Tool 'get_table_schema' for 'sales_transactions':")
            try:
                result = await session.call_tool("get_table_schema", arguments={"table_name": "sales_transactions"})
                
                # Print the tool output
                for content in result.content:
                    if content.type == "text":
                        print(content.text)
            except Exception as e:
                print(f"Error calling tool: {e}")

if __name__ == "__main__":
    asyncio.run(run_client())
