#!/usr/bin/env python3
"""Direct stdio proxy to the ACE Studio MCP server — bypasses Cursor's cached error state."""
import subprocess
import json
import sys
import threading
import queue
import os

MCP_SERVER = "/Applications/ACE Studio.app/Contents/Helpers/ace-mcp-server"

def main():
    proc = subprocess.Popen(
        [MCP_SERVER],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=os.environ.copy(),
    )

    request_id = 0
    def next_id():
        nonlocal request_id
        request_id += 1
        return request_id

    def send(msg):
        data = json.dumps(msg) + "\n"
        proc.stdin.write(data.encode())
        proc.stdin.flush()
        print(f">>> {json.dumps(msg)}", file=sys.stderr)

    def read_response():
        """Read a single JSON-RPC response from stdout."""
        line = b""
        while True:
            ch = proc.stdout.read(1)
            if not ch:
                return None
            line += ch
            if ch == b"\n":
                try:
                    return json.loads(line.decode().strip())
                except json.JSONDecodeError:
                    continue

    def read_thread(q):
        while True:
            resp = read_response()
            if resp is None:
                break
            q.put(resp)

    resp_queue = queue.Queue()
    t = threading.Thread(target=read_thread, args=(resp_queue,), daemon=True)
    t.start()

    # --- Initialize ---
    send({
        "jsonrpc": "2.0",
        "id": next_id(),
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "proxy", "version": "1.0"}
        }
    })

    # Read initialize response (may include notifications before it)
    init_resp = None
    deadline_import = 0
    while init_resp is None and deadline_import < 50:
        try:
            msg = resp_queue.get(timeout=1.0)
            if "result" in msg or "error" in msg:
                init_resp = msg
                print(f"<<< {json.dumps(msg)}", file=sys.stderr)
            else:
                print(f"<<< (notif) {json.dumps(msg)}", file=sys.stderr)
        except queue.Empty:
            deadline_import += 1

    if init_resp is None:
        print("ERROR: No initialize response", file=sys.stderr)
        # Check stderr
        stderr_data = proc.stderr.read1(4096) if hasattr(proc.stderr, 'read1') else b""
        print(f"STDERR: {stderr_data.decode(errors='replace')}", file=sys.stderr)
        proc.kill()
        sys.exit(1)

    if "error" in init_resp:
        print(f"INITIALIZE ERROR: {json.dumps(init_resp['error'])}", file=sys.stderr)
        proc.kill()
        sys.exit(1)

    print(f"INITIALIZED: {json.dumps(init_resp.get('result', {}))}", file=sys.stderr)

    # Send initialized notification
    send({"jsonrpc": "2.0", "method": "notifications/initialized"})

    # --- List tools ---
    send({"jsonrpc": "2.0", "id": next_id(), "method": "tools/list"})

    tools_resp = None
    deadline = 0
    while tools_resp is None and deadline < 30:
        try:
            msg = resp_queue.get(timeout=1.0)
            if "result" in msg or "error" in msg:
                tools_resp = msg
                print(f"<<< {json.dumps(msg)[:2000]}", file=sys.stderr)
            else:
                print(f"<<< (notif) {json.dumps(msg)[:500]}", file=sys.stderr)
        except queue.Empty:
            deadline += 1

    if tools_resp is None:
        print("ERROR: No tools/list response", file=sys.stderr)
        proc.kill()
        sys.exit(1)

    tools = tools_resp.get("result", {}).get("tools", [])
    print(f"\n=== AVAILABLE TOOLS ({len(tools)}) ===", file=sys.stderr)
    for tool in tools:
        print(f"  - {tool['name']}: {tool.get('description', '')[:100]}", file=sys.stderr)

    # Output tools as JSON to stdout for parsing
    print(json.dumps({"tools": tools, "init": init_resp.get("result", {})}))

    proc.kill()

if __name__ == "__main__":
    main()
