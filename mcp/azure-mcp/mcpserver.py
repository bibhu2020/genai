#!/usr/bin/env python3
import shutil
import subprocess
import sys

def find_npx() -> str:
    """Locate the `npx` executable in PATH."""
    from shutil import which
    path = which("npx")
    if not path:
        sys.exit("ERROR: `npx` not found on PATH. Install Node.js (which includes npm/npx).")
    return path

def main():
    npx = find_npx()
    cmd = [
        npx, "-y", "@azure/mcp@latest", "server", "start",
        "--transport", "sse",        # use SSE transport
        "--port", "5008"
    ]
    print(f"Starting MCP server:\n  {' '.join(cmd)}\n")
    proc = subprocess.Popen(cmd)
    try:
        proc.wait()
    except KeyboardInterrupt:
        print("\nStopping MCP server...")
        proc.terminate()
        proc.wait()

if __name__ == "__main__":
    main()