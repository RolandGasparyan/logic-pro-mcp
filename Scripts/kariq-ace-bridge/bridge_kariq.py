#!/usr/bin/env python3
"""Import KARIQ mix/vocals from Logic bounces into ACE Studio (macOS only).

Prefers ACE MCP (tool names evolve — match by substring) and falls back to
acestudio-cli verbs discovered from --help. Does not remix Logic.
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

DEFAULT_MCP = "/Applications/ACE Studio.app/Contents/Helpers/ace-mcp-server"
DEFAULT_CLI = "/Applications/ACE Studio.app/Contents/Helpers/acestudio-cli"
PROJECT_NAME = "KARIQ"
DEFAULT_TIMEOUT = 90.0
AUDIO_EXTS = {".aif", ".aiff", ".wav", ".flac", ".mp3", ".m4a", ".aac"}
MIDI_EXTS = {".mid", ".midi"}


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


def first_ok(results: list[Any]) -> Any:
    for out in results:
        if not (isinstance(out, dict) and out.get("error")):
            return out
    return results[-1] if results else {"error": True, "content": "no attempts"}


def ensure_bridge_cli(cli: Path) -> str:
    if not cli.exists():
        raise FileNotFoundError(cli)
    status = subprocess.run([str(cli), "app", "status"], capture_output=True, text=True, check=False)
    out = (status.stdout or "") + (status.stderr or "")
    if "bridge-ready" in out.lower():
        return out
    subprocess.run(["open", "-a", "ACE Studio"], check=False)
    for _ in range(30):
        time.sleep(2)
        status = subprocess.run([str(cli), "app", "status"], capture_output=True, text=True, check=False)
        out = (status.stdout or "") + (status.stderr or "")
        if "bridge-ready" in out.lower():
            return out
    raise RuntimeError(f"ACE Studio not bridge-ready:\n{out}")


def collect_media(work: Path) -> tuple[list[Path], list[Path]]:
    audio: list[Path] = []
    midi: list[Path] = []
    if not work.exists():
        return audio, midi
    for path in sorted(work.iterdir()):
        if not path.is_file():
            continue
        ext = path.suffix.lower()
        if ext in AUDIO_EXTS:
            audio.append(path)
        elif ext in MIDI_EXTS:
            midi.append(path)
    return audio, midi


def prefer_vocals(audio: list[Path]) -> Path | None:
    for path in audio:
        name = path.name.lower()
        if "vocal" in name or "vox" in name:
            return path
    return audio[0] if audio else None


def cli_try(cli: Path, args: list[str]) -> tuple[int, str]:
    result = subprocess.run([str(cli), *args], capture_output=True, text=True, check=False)
    text = ((result.stdout or "") + (result.stderr or "")).strip()
    print(f"cli {' '.join(args)} -> {result.returncode}\n{text[:1500]}")
    return result.returncode, text


def try_cli_import(cli: Path, path: Path) -> bool:
    for args in (
        ["file", "import", str(path)],
        ["import", "file", str(path)],
        ["import", str(path)],
        ["project", "import", str(path)],
    ):
        code, _ = cli_try(cli, args)
        if code == 0:
            return True
    return False


def try_cli_save(cli: Path, save_dir: Path) -> None:
    target = save_dir / PROJECT_NAME
    for args in (
        ["project", "save", "--path", str(target)],
        ["project", "save-as", str(target)],
        ["project", "save"],
        ["save", str(target)],
    ):
        code, _ = cli_try(cli, args)
        if code == 0:
            return


def import_via_mcp(
    proc: subprocess.Popen[str],
    rid: list[int],
    tool: str,
    path: Path,
    timeout_sec: float,
    extra: dict[str, Any] | None = None,
) -> Any:
    attempts: list[Any] = []
    bases = (
        {"path": str(path)},
        {"file": str(path)},
        {"file_path": str(path)},
        {"filepath": str(path)},
    )
    for base in bases:
        payload = dict(base)
        if extra:
            payload.update(extra)
        out = call_tool(proc, rid, tool, payload, timeout_sec)
        print(out)
        attempts.append(out)
        if not (isinstance(out, dict) and out.get("error")):
            return out
    return first_ok(attempts)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mcp", default=os.environ.get("ACE_MCP_SERVER", DEFAULT_MCP))
    parser.add_argument("--cli", default=os.environ.get("ACE_CLI", DEFAULT_CLI))
    parser.add_argument("--timeout-sec", type=float, default=DEFAULT_TIMEOUT)
    parser.add_argument(
        "--work-dir",
        default=str(Path.home() / "Music" / "ACE Studio" / "KARIQ-bridge"),
    )
    parser.add_argument(
        "--save-dir",
        default=str(Path.home() / "Music" / "ACE Studio" / "KARIQ"),
    )
    parser.add_argument("--tempo", type=float, default=None, help="BPM to apply if a tempo tool exists")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if sys.platform != "darwin" and not args.dry_run:
        print("ERROR: bridge_kariq.py must run on macOS with ACE Studio.", file=sys.stderr)
        return 2

    work = Path(args.work_dir)
    save_dir = Path(args.save_dir)
    work.mkdir(parents=True, exist_ok=True)
    save_dir.mkdir(parents=True, exist_ok=True)

    audio, midi = collect_media(work)
    print(f"work={work}")
    print(f"audio ({len(audio)}): {[p.name for p in audio]}")
    print(f"midi ({len(midi)}): {[p.name for p in midi]}")
    if args.dry_run:
        return 0
    if not audio and not midi:
        print(
            "ERROR: no KARIQ audio/MIDI in work dir. Copy bounces to "
            f"{work} (expected KARIQ-mix-final.aif / KARIQ-vocals-cleaned.aif).",
            file=sys.stderr,
        )
        return 1

    status = ensure_bridge_cli(Path(args.cli))
    print(status.strip())
    cli_try(Path(args.cli), ["project", "info", "--json"])
    cli_try(Path(args.cli), ["track", "list", "--json"])

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
    imported = 0
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
                    "clientInfo": {"name": "kariq-ace-bridge", "version": "1.0"},
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

        new_project = pick_tool(tools, "project_new", "new_project", "create_project", "project_create")
        set_tempo = pick_tool(tools, "set_tempo", "tempo_set", "project_set_tempo", "transport_set_tempo")
        import_file = pick_tool(
            tools,
            "import_audio",
            "audio_import",
            "import_file",
            "file_import",
            "project_import",
            "import_midi",
        )
        vocal_to_midi = pick_tool(
            tools,
            "vocal_to_midi",
            "vocal-to-midi",
            "voice_to_midi",
            "transcribe_vocal",
        )
        save_project = pick_tool(tools, "project_save_as", "save_as", "project_save", "save_project")
        project_info = pick_tool(tools, "project_info", "get_project", "app_status", "project_get")
        track_list = pick_tool(tools, "track_list", "list_tracks", "tracks_list", "get_tracks")

        if new_project:
            print(f"==> {new_project} {PROJECT_NAME}")
            for payload in (
                {"name": PROJECT_NAME},
                {"project": PROJECT_NAME},
                {"title": PROJECT_NAME},
                {},
            ):
                out = call_tool(proc, rid, new_project, payload, args.timeout_sec)
                print(out)
                if not (isinstance(out, dict) and out.get("error")):
                    break
        else:
            print("WARN: no new-project MCP tool; importing into the open ACE project")
            print("      (do not overwrite Acid Track v4 — save-as KARIQ before continuing if needed)")

        if args.tempo and set_tempo:
            print(f"==> {set_tempo} {args.tempo}")
            for payload in (
                {"tempo": args.tempo},
                {"bpm": args.tempo},
                {"value": args.tempo},
                {"tempo_bpm": args.tempo},
            ):
                out = call_tool(proc, rid, set_tempo, payload, args.timeout_sec)
                print(out)
                if not (isinstance(out, dict) and out.get("error")):
                    break
        elif args.tempo:
            cli_try(Path(args.cli), ["transport", "set-tempo", str(args.tempo)])
            cli_try(Path(args.cli), ["project", "set-tempo", str(args.tempo)])

        if import_file:
            for path in audio + midi:
                print(f"==> import {path.name}")
                out = import_via_mcp(proc, rid, import_file, path, args.timeout_sec)
                if not (isinstance(out, dict) and out.get("error")):
                    imported += 1
                else:
                    if try_cli_import(Path(args.cli), path):
                        imported += 1
        else:
            print("WARN: no import MCP tool; trying CLI")
            for path in audio + midi:
                if try_cli_import(Path(args.cli), path):
                    imported += 1

        lead = prefer_vocals(audio)
        if vocal_to_midi and lead:
            print(f"==> {vocal_to_midi} {lead.name}")
            import_via_mcp(
                proc,
                rid,
                vocal_to_midi,
                lead,
                max(args.timeout_sec, 180.0),
                extra={"lyrics": True},
            )
        elif lead:
            cli_try(Path(args.cli), ["generative", "vocal-to-midi", str(lead)])
            cli_try(Path(args.cli), ["vocal-to-midi", str(lead)])

        if save_project:
            target = str(save_dir / PROJECT_NAME)
            print(f"==> save {target}")
            for payload in (
                {"path": target},
                {"file": target},
                {"file_path": target},
                {"directory": str(save_dir), "name": PROJECT_NAME},
                {},
            ):
                out = call_tool(proc, rid, save_project, payload, args.timeout_sec)
                print(out)
                if not (isinstance(out, dict) and out.get("error")):
                    break
        else:
            try_cli_save(Path(args.cli), save_dir)

        if project_info:
            print("==> project info")
            print(call_tool(proc, rid, project_info, {}, args.timeout_sec))
        else:
            cli_try(Path(args.cli), ["project", "info", "--json"])
        if track_list:
            print("==> tracks")
            print(call_tool(proc, rid, track_list, {}, args.timeout_sec))
        else:
            cli_try(Path(args.cli), ["track", "list", "--json"])

        print(f"imported_ok={imported}/{len(audio) + len(midi)}")
        print("NEXT: ACE Bridge 2 in Logic — see Scripts/kariq-ace-bridge/ACE-BRIDGE-2.md")
        print("DONE" if imported else "PARTIAL")
        return 0 if imported else 1
    finally:
        proc.kill()


if __name__ == "__main__":
    raise SystemExit(main())
