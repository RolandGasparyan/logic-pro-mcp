#!/usr/bin/env python3
"""Check available tracks and try set_plugin_param on track 0 to verify Scripter works."""
import subprocess, json, sys, threading, queue, os, shutil

def resolve_server():
    override = os.environ.get("LOGIC_PRO_MCP_BIN", "").strip()
    found = override or shutil.which("LogicProMCP") or os.path.expanduser("~/.local/bin/LogicProMCP")
    if not os.path.isfile(found):
        sys.exit(f"ERROR: LogicProMCP not found at {found}; set LOGIC_PRO_MCP_BIN")
    return found

MCP_SERVER = resolve_server()

def main():
    proc = subprocess.Popen([MCP_SERVER], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, env=os.environ.copy())
    rid = [0]
    def nid():
        rid[0] += 1; return rid[0]
    def send(msg):
        proc.stdin.write((json.dumps(msg) + "\n").encode()); proc.stdin.flush()
    def read_resp():
        line = b""
        while True:
            ch = proc.stdout.read(1)
            if not ch: return None
            line += ch
            if ch == b"\n":
                chunk, line = line, b""
                try: return json.loads(chunk.decode().strip())
                except ValueError: continue
    q = queue.Queue()
    threading.Thread(target=lambda: [q.put(r) for r in iter(read_resp, None)], daemon=True).start()

    send({"jsonrpc":"2.0","id":nid(),"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"proxy","version":"1.0"}}})
    q.get(timeout=15)
    send({"jsonrpc":"2.0","method":"notifications/initialized"})

    # Get regions to see available tracks
    send({"jsonrpc":"2.0","id":nid(),"method":"tools/call","params":{"name":"logic_project","arguments":{"command":"get_regions"}}})
    resp = q.get(timeout=15)
    text = resp.get("result",{}).get("content",[{}])[0].get("text","")
    print("=== REGIONS ===")
    print(text[:3000])

    # Try get_inventory on track 0
    send({"jsonrpc":"2.0","id":nid(),"method":"tools/call","params":{"name":"logic_plugins","arguments":{"command":"get_inventory","params":{"track":0}}}})
    resp2 = q.get(timeout=15)
    text2 = resp2.get("result",{}).get("content",[{}])[0].get("text","")
    print("\n=== TRACK 0 INVENTORY ===")
    print(text2[:2000])

    proc.kill()

if __name__ == "__main__":
    main()
