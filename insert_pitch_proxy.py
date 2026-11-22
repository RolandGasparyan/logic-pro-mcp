#!/usr/bin/env python3
"""Insert Pitch Shifter on Stereo Out via Logic Pro MCP proxy, then set pitch to -2."""
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

    def call_mcp(tool, command, params=None):
        send({"jsonrpc":"2.0","id":nid(),"method":"tools/call","params":{"name":tool,"arguments":{"command":command,"params":params or {}}}})
        resp = q.get(timeout=30)
        texts = resp.get("result",{}).get("content",[])
        for t in texts:
            if t.get("type") == "text":
                try:
                    return json.loads(t["text"])
                except:
                    return {"raw": t["text"]}
        return resp

    # 1. Check health
    h = call_mcp("logic_system", "health")
    print(f"Health: logic_pro_running={h.get('logic_pro_running')}, track_count={h.get('cache',{}).get('track_count')}")

    # 2. Try insert Pitch Shifter on track 0 (test)
    r = call_mcp("logic_mixer", "insert_plugin", {"track":0,"slot":0,"plugin_name":"Pitch Shifter","confirmed":True})
    print(f"Insert track 0: state={r.get('state')}, success={r.get('success')}, observed={r.get('observed_plugin_name')}, rollback={r.get('rollback_attempted')}")

    proc.kill()

if __name__ == "__main__":
    main()
