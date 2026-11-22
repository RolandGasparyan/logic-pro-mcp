#!/usr/bin/env python3
"""Import Acid Track v4 MIDI into ACE Studio via ace-mcp-server (macOS only).

Run on ROLAND's Mac Studio with ACE Studio open and bridge-ready.
Prefers ACE MCP over guessing acestudio-cli verbs; falls back to CLI when needed.
"""

from __future__ import annotations

import argparse
import json
import os
import select
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
SPECS = ROOT / "v4-layer-specs.json"
DEFAULT_MCP = "/Applications/ACE Studio.app/Contents/Helpers/ace-mcp-server"
DEFAULT_CLI = "/Applications/ACE Studio.app/Contents/Helpers/acestudio-cli"
DEFAULT_TIMEOUT = 60.0
PROJECT_NAME = "Acid Track v4"
TEMPO = 127.0


def load_layers() -> list[dict[str, Any]]:
    return json.loads(SPECS.read_text(encoding="utf-8"))


def read_response(proc: subprocess.Popen[str], request_id: int, timeout_sec: float) -> dict[str, Any]:
    if proc.stdout is None:
        raise RuntimeError("MCP stdout pipe is not available")
    deadline = time.monotonic() + timeout_sec
    while time.monotonic() < deadline:
        remaining = max(0.0, deadline - time.monotonic())
        ready, _, _ = select.select([proc.stdout], [], [], remaining)
        if not ready:
            continue
        line = proc.stdout.readline()
        if line == "":
            raise RuntimeError(f"MCP exited before response id {request_id}")
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        if obj.get("id") == request_id:
            return obj
    raise TimeoutError(f"Timed out after {timeout_sec:.1f}s waiting for response id {request_id}")


def send(proc: subprocess.Popen[str], request: dict[str, Any], timeout_sec: float) -> dict[str, Any]:
    assert proc.stdin is not None
    proc.stdin.write(json.dumps(request, separators=(",", ":")) + "\n")
    proc.stdin.flush()
    return read_response(proc, int(request["id"]), timeout_sec)


def tool_payload(response: dict[str, Any]) -> Any:
    result = response.get("result") or {}
    if result.get("isError"):
        return {"error": True, "content": result.get("content")}
    content = result.get("content") or []
    if not content:
        return result
    text = content[0].get("text", "")
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {"raw": text}


def call_tool(
    proc: subprocess.Popen[str],
    rid: list[int],
    name: str,
    arguments: dict[str, Any],
    timeout_sec: float,
) -> Any:
    rid[0] += 1
    resp = send(
        proc,
        {
            "jsonrpc": "2.0",
            "id": rid[0],
            "method": "tools/call",
            "params": {"name": name, "arguments": arguments},
        },
        timeout_sec,
    )
    return tool_payload(resp)


def list_tools(proc: subprocess.Popen[str], rid: list[int], timeout_sec: float) -> list[dict[str, Any]]:
    rid[0] += 1
    resp = send(
        proc,
        {"jsonrpc": "2.0", "id": rid[0], "method": "tools/list", "params": {}},
        timeout_sec,
    )
    return list((resp.get("result") or {}).get("tools") or [])


def pick_tool(tools: list[dict[str, Any]], *needles: str) -> str | None:
    names = [t.get("name", "") for t in tools]
    lowered = {n.lower(): n for n in names}
    for needle in needles:
        n = needle.lower()
        if n in lowered:
            return lowered[n]
        for name in names:
            if n in name.lower():
                return name
    return None


def ensure_bridge_cli(cli: Path) -> None:
    if not cli.exists():
        raise FileNotFoundError(cli)
    status = subprocess.run([str(cli), "app", "status"], capture_output=True, text=True, check=False)
    out = (status.stdout or "") + (status.stderr or "")
    if "bridge-ready" not in out.lower():
        subprocess.run(["open", "-a", "ACE Studio"], check=False)
        for _ in range(30):
            time.sleep(2)
            status = subprocess.run([str(cli), "app", "status"], capture_output=True, text=True, check=False)
            out = (status.stdout or "") + (status.stderr or "")
            if "bridge-ready" in out.lower():
                return
        raise RuntimeError(f"ACE Studio not bridge-ready:\n{out}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mcp", default=os.environ.get("ACE_MCP_SERVER", DEFAULT_MCP))
    parser.add_argument("--cli", default=os.environ.get("ACE_CLI", DEFAULT_CLI))
    parser.add_argument("--timeout-sec", type=float, default=DEFAULT_TIMEOUT)
    parser.add_argument("--save-dir", default=str(Path.home() / "Music" / "ACE Studio" / "Acid Track v4"))
    parser.add_argument("--dry-run", action="store_true", help="List MCP tools and exit")
    args = parser.parse_args()

    if sys.platform != "darwin" and not args.dry_run:
        print("ERROR: import_v4_ace_mcp.py must run on macOS with ACE Studio.", file=sys.stderr)
        return 2

    layers = load_layers()
    midi_paths = []
    for layer in layers:
        path = ROOT / layer["artifact_midi_path"]
        if not path.exists():
            print(f"ERROR: missing {path}", file=sys.stderr)
            return 1
        midi_paths.append((layer["name"], path))

    ensure_bridge_cli(Path(args.cli))

    proc = subprocess.Popen(
        [args.mcp],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
        env=os.environ.copy(),
    )
    rid = [0]
    try:
        rid[0] += 1
        init = send(
            proc,
            {
                "jsonrpc": "2.0",
                "id": rid[0],
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "acid-v4-ace-import", "version": "1.0"},
                },
            },
            args.timeout_sec,
        )
        if "error" in init:
            print(f"initialize error: {init['error']}", file=sys.stderr)
            return 1
        assert proc.stdin is not None
        proc.stdin.write(json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}) + "\n")
        proc.stdin.flush()

        tools = list_tools(proc, rid, args.timeout_sec)
        print(f"=== ACE MCP tools ({len(tools)}) ===")
        for tool in tools:
            print(f"  - {tool.get('name')}")

        if args.dry_run:
            return 0

        # Heuristic tool picks — ACE MCP names evolve; match by substring.
        new_project = pick_tool(tools, "project_new", "new_project", "create_project", "project_create")
        set_tempo = pick_tool(tools, "set_tempo", "tempo_set", "project_set_tempo", "transport_set_tempo")
        import_midi = pick_tool(tools, "import_midi", "midi_import", "file_import", "import_file", "project_import")
        rename_track = pick_tool(tools, "rename_track", "track_rename", "set_track_name")
        save_project = pick_tool(tools, "project_save_as", "save_as", "project_save", "save_project")
        project_info = pick_tool(tools, "project_info", "get_project", "app_status", "project_get")
        track_list = pick_tool(tools, "track_list", "list_tracks", "tracks_list", "get_tracks")

        save_dir = Path(args.save_dir)
        save_dir.mkdir(parents=True, exist_ok=True)

        if new_project:
            print(f"==> {new_project}")
            print(call_tool(proc, rid, new_project, {"name": PROJECT_NAME}, args.timeout_sec))
        else:
            print("WARN: no new-project MCP tool; using whatever project is open")

        if set_tempo:
            print(f"==> {set_tempo} {TEMPO}")
            for args_try in (
                {"tempo": TEMPO},
                {"bpm": TEMPO},
                {"value": TEMPO},
                {"tempo_bpm": TEMPO},
            ):
                out = call_tool(proc, rid, set_tempo, args_try, args.timeout_sec)
                print(out)
                if not (isinstance(out, dict) and out.get("error")):
                    break
        else:
            print("WARN: no set-tempo MCP tool")

        if not import_midi:
            print("ERROR: no import-midi MCP tool found", file=sys.stderr)
            return 1

        for name, path in midi_paths:
            print(f"==> import {name} <- {path}")
            out = None
            for args_try in (
                {"path": str(path)},
                {"file": str(path)},
                {"file_path": str(path)},
                {"path": str(path), "name": name},
            ):
                out = call_tool(proc, rid, import_midi, args_try, args.timeout_sec)
                print(out)
                if not (isinstance(out, dict) and out.get("error")):
                    break
            if rename_track:
                for args_try in (
                    {"name": name},
                    {"track_name": name},
                    {"new_name": name},
                ):
                    r = call_tool(proc, rid, rename_track, args_try, args.timeout_sec)
                    if not (isinstance(r, dict) and r.get("error")):
                        print(r)
                        break

        if save_project:
            target = str(save_dir / f"{PROJECT_NAME}.ace")
            print(f"==> save {target}")
            for args_try in (
                {"path": target},
                {"file": target},
                {"file_path": target},
                {"directory": str(save_dir), "name": PROJECT_NAME},
                {},
            ):
                out = call_tool(proc, rid, save_project, args_try, args.timeout_sec)
                print(out)
                if not (isinstance(out, dict) and out.get("error")):
                    break

        if project_info:
            print("==> project info")
            print(call_tool(proc, rid, project_info, {}, args.timeout_sec))
        if track_list:
            print("==> tracks")
            print(call_tool(proc, rid, track_list, {}, args.timeout_sec))

        print("DONE")
        return 0
    finally:
        proc.kill()


if __name__ == "__main__":
    raise SystemExit(main())
