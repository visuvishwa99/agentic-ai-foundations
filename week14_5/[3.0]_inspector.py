import os
import sys
import subprocess
import shutil

# Path to the server script
SERVER_SCRIPT = os.path.join(os.path.dirname(__file__), "[2.0]_mcp_server.py")

def main():
    # Check if npx is available
    if not shutil.which("npx"):
        print("[ERROR] Error: 'npx' is not installed or not in PATH.")
        print("   The MCP Inspector requires Node.js and npx.")
        print("   Please install Node.js from https://nodejs.org/")
        return

    # Use the current python interpreter
    python_exe = sys.executable
    
    # Construct the command
    # npx @modelcontextprotocol/inspector <command> <args>
    cmd = [
        "npx",
        "-y",
        "@modelcontextprotocol/inspector",
        python_exe,
        SERVER_SCRIPT
    ]
    
    print(f"[INFO] Launching MCP Inspector...")
    print(f"   Target Server: {SERVER_SCRIPT}")
    print(f"   Command: {' '.join(cmd)}")
    print("\n   Press Ctrl+C to stop the inspector.\n")

    try:
        # Run the inspector
        # On Windows shell=True might be needed for npx dependent on environment, 
        # but shutil.which found it, so subprocess might work directly if it's an exe/cmd.
        # Often npx is npx.cmd on windows.
        
        # We'll try running it directly.
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\n[STOP] Inspector stopped.")
    except Exception as e:
        print(f"\n[ERROR] Failed to run inspector: {e}")
        # Fallback instruction
        print("\nTry running this manually in your terminal:")
        print(f"npx -y @modelcontextprotocol/inspector {python_exe} \"{SERVER_SCRIPT}\"")

if __name__ == "__main__":
    main()
