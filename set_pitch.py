#!/usr/bin/env python3
"""Call logic_mixer.set_plugin_param to set Pitch Shifter pitch to -2 on track 12 (Knock A)."""
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

    # Initialize
    send({"jsonrpc":"2.0","id":nid(),"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"proxy","version":"1.0"}}})
    init = q.get(timeout=15)
    print(f"Init: {json.dumps(init.get('result',{}).get('serverInfo',{}))}", file=sys.stderr)
    send({"jsonrpc":"2.0","method":"notifications/initialized"})

    # Call set_plugin_param: track 12, insert 0, param 0, value -2.0
    send({"jsonrpc":"2.0","id":nid(),"method":"tools/call","params":{"name":"logic_mixer","arguments":{"command":"set_plugin_param","params":{"track":int(os.environ.get("PITCH_TRACK","12")),"insert":0,"param":0,"value":float(os.environ.get("PITCH_VALUE","0.4167"))}}}})
    resp = q.get(timeout=30)
    print(json.dumps(resp, indent=2))
    proc.kill()

if __name__ == "__main__":
    main()
