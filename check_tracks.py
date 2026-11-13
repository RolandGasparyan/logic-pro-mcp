#!/usr/bin/env python3
"""Check available tracks and try set_plugin_param on track 0 to verify Scripter works."""
import subprocess, json, sys, threading, queue, os

MCP_SERVER = "/Users/rolandgasparyan/.local/bin/LogicProMCP"

def main():
    proc = subprocess.Popen([MCP_SERVER], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=os.environ.copy())
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
                try: return json.loads(line.decode().strip())
                except: continue
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
