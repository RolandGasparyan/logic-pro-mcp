#!/usr/bin/env python3
"""Balance Logic Pro mix faders and pitch-correct vocal tracks via LogicProMCP.

Run on macOS only with Logic Pro open and frontmost. Does not open projects.

Usage:
  python3 Scripts/mac_balance_mix_tune_vocals.py [--dry-run]
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional


REPO_ROOT = Path(__file__).resolve().parents[1]
BINARY = os.environ.get(
    "LOGIC_PRO_MCP_BIN",
    os.environ.get("LOGIC_PRO_MCP_BINARY", str(Path.home() / ".local/bin/LogicProMCP")),
)
TIMEOUT = float(os.environ.get("LOGIC_PRO_MCP_TIMEOUT", "45"))

VOCAL_RE = re.compile(
    r"vocal|vox|voice|singer|sing|lead|backing|choir|pripev|dbl|harm|ace|rap",
    re.I,
)
DRUM_RE = re.compile(r"drum|kick|snare|hat|perc|clap|909|808|tom", re.I)
BASS_RE = re.compile(r"bass|sub|808|303|low\s*end", re.I)
AIR_RE = re.compile(r"pad|string|brass|wood|wind|air|fx|noise|reverb|delay|synth|chord|acid|stab", re.I)


@dataclass(frozen=True)
class LevelIntent:
    volume: float
    pan: float = 0.0


def classify_track(name: str) -> LevelIntent:
    n = name.strip() or "Track"
    if VOCAL_RE.search(n):
        return LevelIntent(0.80, 0.0)
    if DRUM_RE.search(n):
        return LevelIntent(0.74, 0.0)
    if BASS_RE.search(n):
        return LevelIntent(0.73, 0.0)
    if AIR_RE.search(n):
        return LevelIntent(0.62, -0.12 if hash(n) % 2 else 0.12)
    return LevelIntent(0.68, 0.0)


class MCPClient:
    def __init__(self, binary: str) -> None:
        self._stderr_dir = tempfile.TemporaryDirectory()
        self._stderr_file = open(Path(self._stderr_dir.name) / "stderr.log", "w", encoding="utf-8")
        self.proc = subprocess.Popen(
            [binary],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=self._stderr_file,
            env=os.environ.copy(),
        )
        self._lock = threading.Lock()
        self._next_id = 1

    def close(self) -> None:
        try:
            self.proc.kill()
        except OSError:
            pass
        self._stderr_file.close()
        self._stderr_dir.cleanup()

    def _read_line(self) -> Optional[Dict[str, Any]]:
        line = b""
        while True:
            ch = self.proc.stdout.read(1)
            if not ch:
                return None
            line += ch
            if ch == b"\n":
                try:
                    return json.loads(line.decode().strip())
                except json.JSONDecodeError:
                    continue

    def send(self, msg: Dict[str, Any], timeout: float = TIMEOUT) -> Optional[Dict[str, Any]]:
        data = (json.dumps(msg) + "\n").encode()
        with self._lock:
            assert self.proc.stdin is not None
            self.proc.stdin.write(data)
            self.proc.stdin.flush()
        deadline = time.time() + timeout
        while time.time() < deadline:
            resp = self._read_line()
            if resp is None:
                return None
            if resp.get("id") == msg.get("id"):
                return resp
        return None

    def notify(self, msg: Dict[str, Any]) -> None:
        data = (json.dumps(msg) + "\n").encode()
        with self._lock:
            assert self.proc.stdin is not None
            self.proc.stdin.write(data)
            self.proc.stdin.flush()

    def next_id(self) -> int:
        rid = self._next_id
        self._next_id += 1
        return rid


def log(event: str, **fields: Any) -> None:
    payload = {"event": event, **fields}
    print(json.dumps(payload, sort_keys=True), flush=True)


def die(message: str, code: int = 1) -> None:
    log("fatal", message=message)
    raise SystemExit(code)


def response_text(response: Optional[Dict[str, Any]], key: str = "content") -> str:
    if not isinstance(response, dict):
        return ""
    try:
        entries = response["result"][key]
    except (KeyError, TypeError):
        return ""
    if not isinstance(entries, list):
        return ""
    for entry in entries:
        if isinstance(entry, dict) and entry.get("type") == "text":
            return str(entry.get("text", ""))
    return ""


def tool_json(response: Optional[Dict[str, Any]]) -> Any:
    text = response_text(response)
    if not text:
        return None
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {"raw": text}


def resource_json(response: Optional[Dict[str, Any]]) -> Any:
    if not isinstance(response, dict) or "error" in response:
        return None
    contents = response.get("result", {}).get("contents")
    if not isinstance(contents, list) or not contents:
        return None
    text = contents[0].get("text")
    if not isinstance(text, str):
        return None
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        return None
    return parsed.get("data", parsed)


def initialize(client: MCPClient) -> None:
    resp = client.send(
        {
            "jsonrpc": "2.0",
            "id": client.next_id(),
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "mac-balance-mix-tune", "version": "1.0"},
            },
        },
        timeout=30,
    )
    if not isinstance(resp, dict) or "result" not in resp:
        die("LogicProMCP initialize failed")
    client.notify({"jsonrpc": "2.0", "method": "notifications/initialized"})
    time.sleep(1.0)


def call_tool(
    client: MCPClient,
    tool: str,
    command: str,
    params: Optional[Dict[str, Any]] = None,
) -> Optional[Dict[str, Any]]:
    arguments: Dict[str, Any] = {"command": command}
    if params is not None:
        arguments["params"] = params
    return client.send(
        {
            "jsonrpc": "2.0",
            "id": client.next_id(),
            "method": "tools/call",
            "params": {"name": tool, "arguments": arguments},
        }
    )


def read_resource(client: MCPClient, uri: str) -> Optional[Dict[str, Any]]:
    return client.send(
        {
            "jsonrpc": "2.0",
            "id": client.next_id(),
            "method": "resources/read",
            "params": {"uri": uri},
        }
    )


def wait_tracks(client: MCPClient) -> List[Dict[str, Any]]:
    deadline = time.time() + 20
    while time.time() < deadline:
        data = resource_json(read_resource(client, "logic://tracks"))
        if isinstance(data, list) and data:
            return data
        time.sleep(1.0)
    die("logic://tracks not available — open a Logic project and bring Logic frontmost")


def track_index(track: Dict[str, Any], fallback: int) -> int:
    for key in ("index", "id", "track_index"):
        raw = track.get(key)
        if isinstance(raw, int):
            return raw
    return fallback


def track_name(track: Dict[str, Any]) -> str:
    for key in ("name", "track_name", "title"):
        raw = track.get(key)
        if isinstance(raw, str) and raw.strip():
            return raw.strip()
    return f"Track {track_index(track, 0)}"


def is_vocal_track(name: str, track: Dict[str, Any]) -> bool:
    if VOCAL_RE.search(name):
        return True
    kind = str(track.get("type", "") or track.get("track_type", "")).lower()
    return "audio" in kind and bool(VOCAL_RE.search(name))


def success_state(payload: Any) -> bool:
    if not isinstance(payload, dict):
        return False
    state = str(payload.get("state", "")).upper()
    if state in {"A", "SUCCESS", "VERIFIED"}:
        return True
    return payload.get("success") is True


def unlock_automation(client: MCPClient, index: int, dry_run: bool) -> None:
    payload = {"index": index, "mode": "off"}
    if dry_run:
        log("automation_skip_dry_run", track=index, mode="off")
        return
    resp = call_tool(client, "logic_tracks", "set_automation", payload)
    log("automation_off", track=index, result=tool_json(resp))


def set_fader(client: MCPClient, index: int, intent: LevelIntent, dry_run: bool) -> None:
    if dry_run:
        log("mix_skip_dry_run", track=index, volume=intent.volume, pan=intent.pan)
        return
    vol = call_tool(
        client,
        "logic_mixer",
        "set_volume",
        {"track": index, "value": intent.volume},
    )
    pan = call_tool(
        client,
        "logic_mixer",
        "set_pan",
        {"track": index, "value": max(-1.0, min(1.0, intent.pan))},
    )
    log(
        "mix_level",
        track=index,
        volume=intent.volume,
        pan=intent.pan,
        volume_result=tool_json(vol),
        pan_result=tool_json(pan),
    )


def first_empty_slot(client: MCPClient, index: int) -> int:
    inv = tool_json(call_tool(client, "logic_plugins", "get_inventory", {"track": index}))
    if not isinstance(inv, dict):
        return 0
    plugins = inv.get("plugins") or inv.get("inserts") or []
    if not isinstance(plugins, list):
        return 0
    occupied = {
        int(p.get("slot", p.get("index", -1)))
        for p in plugins
        if isinstance(p, dict) and isinstance(p.get("slot", p.get("index")), int)
    }
    for slot in range(0, 16):
        if slot not in occupied:
            return slot
    return 0


def insert_stock(
    client: MCPClient,
    index: int,
    plugin_name: str,
    dry_run: bool,
) -> bool:
    slot = first_empty_slot(client, index)
    if dry_run:
        log("insert_skip_dry_run", track=index, plugin=plugin_name, slot=slot)
        return True
    resp = call_tool(
        client,
        "logic_mixer",
        "insert_plugin",
        {
            "track": index,
            "slot": slot,
            "plugin_name": plugin_name,
            "confirmed": True,
        },
    )
    payload = tool_json(resp)
    log("insert_plugin", track=index, plugin=plugin_name, slot=slot, result=payload)
    return success_state(payload)


def tune_vocal_chain(client: MCPClient, index: int, dry_run: bool) -> None:
    # Pitch Correction (realtime autotune). Flex Pitch blob edits are UI-only per MCP scope.
    insert_stock(client, index, "Pitch Correction", dry_run)
    insert_stock(client, index, "Compressor", dry_run)
    insert_stock(client, index, "Channel EQ", dry_run)
    if dry_run:
        return
    # Gentle correction amount when Scripter param path is available (0..1 normalized).
    tune = call_tool(
        client,
        "logic_mixer",
        "set_plugin_param",
        {"track": index, "insert": 0, "param": 0, "value": 0.72},
    )
    log("pitch_correction_param", track=index, result=tool_json(tune))


def apply_flex_pitch_ui_hint() -> None:
    """Optional AppleScript nudge: enable Flex Pitch on selected audio regions."""
    script = r'''
tell application "Logic Pro" to activate
delay 0.2
tell application "System Events"
    tell process "Logic Pro"
        set frontmost to true
        try
            click menu item "Show Flex" of menu "Flex" of menu item "Flex" of menu "Track" of menu bar 1
        end try
    end tell
end tell
'''
    try:
        subprocess.run(["osascript", "-e", script], capture_output=True, text=True, timeout=12, check=False)
        log("flex_pitch_ui_hint", status="osascript_sent")
    except (subprocess.TimeoutExpired, OSError) as err:
        log("flex_pitch_ui_hint", status="skipped", error=str(err))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if sys.platform != "darwin":
        die(f"macOS only (got {sys.platform})")

    if not os.path.isfile(BINARY) and not os.access(BINARY, os.X_OK):
        which = subprocess.run(["which", "LogicProMCP"], capture_output=True, text=True).stdout.strip()
        if which:
            os.environ["LOGIC_PRO_MCP_BIN"] = which
        else:
            die(f"LogicProMCP not found at {BINARY}")

    binary = os.environ.get("LOGIC_PRO_MCP_BIN", BINARY)
    client = MCPClient(binary)
    try:
        initialize(client)
        health = tool_json(call_tool(client, "logic_system", "health", {}))
        log("health", payload=health)
        call_tool(client, "logic_system", "refresh_cache", {})
        tracks = wait_tracks(client)
        project = resource_json(read_resource(client, "logic://project/info"))
        log("project", payload=project)

        vocal_indexes: List[int] = []
        for i, track in enumerate(tracks):
            if not isinstance(track, dict):
                continue
            idx = track_index(track, i)
            name = track_name(track)
            intent = classify_track(name)
            unlock_automation(client, idx, args.dry_run)
            set_fader(client, idx, intent, args.dry_run)
            if is_vocal_track(name, track):
                vocal_indexes.append(idx)
                tune_vocal_chain(client, idx, args.dry_run)

        if vocal_indexes and not args.dry_run:
            apply_flex_pitch_ui_hint()

        if not args.dry_run:
            save = tool_json(call_tool(client, "logic_project", "save", {}))
            log("save", result=save)

        log(
            "done",
            track_count=len(tracks),
            vocal_tracks=vocal_indexes,
            dry_run=args.dry_run,
        )
    finally:
        client.close()


if __name__ == "__main__":
    main()