#!/usr/bin/env python3
"""Call logic_mixer.set_plugin_param to set Pitch Shifter pitch to -2 on track 12 (Knock A)."""
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

    # Initialize
    send({"jsonrpc":"2.0","id":nid(),"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"proxy","version":"1.0"}}})
    init = q.get(timeout=15)
    print(f"Init: {json.dumps(init.get('result',{}).get('serverInfo',{}))}", file=sys.stderr)
    send({"jsonrpc":"2.0","method":"notifications/initialized"})

    # Call set_plugin_param: track 12, insert 0, param 0, value -2.0
    send({"jsonrpc":"2.0","id":nid(),"method":"tools/call","params":{"name":"logic_mixer","arguments":{"command":"set_plugin_param","params":{"track":12,"insert":0,"param":0,"value":0.4167}}}})
    resp = q.get(timeout=30)
    print(json.dumps(resp, indent=2))
    proc.kill()

if __name__ == "__main__":
    main()
