---
name: computer-use
description: Codex-style computer use for Cursor — drive the real desktop by screenshot then mouse/keyboard. The agent reads a screenshot PNG, decides one action, runs the cua executor, and re-screenshots to verify. Use when the user says computer use, CUA, control my screen/mouse/keyboard, automate a GUI app, click/type on the desktop, or /cua.
---

# Computer Use (Cursor port of Codex CUA)

Port of OpenAI Codex Computer Use (`@oai/sky` full-desktop action space) onto Cursor primitives.

Codex CUA is a loop: **screenshot → model looks at the image → one action → screenshot again → repeat** until the on-screen goal is met. The model is the brain; a native helper is the hands. In Cursor **you are the brain** (you can read PNG screenshots), and `scripts/cua.ps1` is the hands. Same loop, rebuilt.

Only act on the user's own machine at their request. Never enter credentials, approve payments, or take destructive OS actions without explicit per-action confirmation.

## The executor

`scripts/cua.ps1` (Windows, PowerShell + .NET, zero install). Per-monitor DPI aware, so **screenshot pixels equal click coordinates** — a point you see at (x, y) in the screenshot is exactly where a click at (x, y) lands. One action per call.

Invoke each action as:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "<skill>/scripts/cua.ps1" <command> [flags]
```

Resolve `<skill>` to this skill's install folder (`~/.cursor/skills/computer-use`) as an absolute path.

## Action reference (mirrors Codex `@oai/sky` full-desktop)

| Codex action | cua.ps1 | Notes |
|---|---|---|
| `get_screenshot()` | `screenshot [-Path out.png] [-Raw]` | prints `screenshot <path> <w>x<h> origin <l>,<t>`; then Read that PNG. `-Raw` keeps the blue cursor in the shot; omit it so the cursor is hidden |
| `click({x,y,...})` | `click -X <x> -Y <y> [-Button left\|right\|middle] [-Count 1] [-Key "Ctrl"] [-Duration 0]` | `-Count 2` double-click; `-Key` holds a chord during the click |
| `move({x,y})` | `move -X <x> -Y <y>` | |
| `type_text({text})` | `type -Text "<text>"` | Unicode via SendInput; types into current focus |
| `press_key({key})` | `key -Key "<chord>"` | `+`-separated, e.g. `Ctrl+a`, `Super_L+r`, `Alt+F4`, `Return` |
| `scroll({direction,pixels,x,y})` | `scroll -Direction up\|down\|left\|right [-Pixels 300] [-X <x> -Y <y>]` | optional origin |
| `drag({path})` | `drag -DragPath "x1,y1 x2,y2 ..."` | presses at first point, visits the rest, releases |
| — | `overlay-start` / `overlay-stop` | show / hide the blue AI cursor (below) |
| — | `pos` / `size` | cursor position / virtual-screen size + origin |
| — | `find-window [-Title] [-ProcessName]` | best match (WeChat: title `微信`, process `Weixin,WeChatAppEx`) |
| — | `list-windows [-Title] [-ProcessName]` | dump candidate top-level windows for debugging |
| — | `focus-window [-Title] [-ProcessName]` | restore + foreground that window |
| — | `framehash [-Title] [-ProcessName] [-Region all\|full\|nav\|session\|chat\|composer] [-HashSize 16]` | window-crop + downsampled average hash; Node compares the hex |
| — | `screenshot [-Title] [-ProcessName]` | crop the shot to that window; `origin` is the window top-left |
| — | `resize-window [-Title] [-ProcessName] -Width <w> -Height <h>` | restore + resize that window (keeps position) |
| — | `scroll ... [-Count n]` | send n wheel EVENTS in one call (some apps clamp per-event distance) |
| — | `server` | resident mode: one command line per stdin line, replies end with `##end <code>`; `-Text` becomes `-TextB64`; saves the ~0.8s process startup per action |

## The blue AI cursor (live visual feedback)

Like Codex, the user can watch a blue cursor glide to each target and ripple on click, so they see what the agent is doing in real time.

- **Start it once** at the beginning of a computer-use session: `cua.ps1 overlay-start`.
- Every `click/move/scroll/drag/type/key` then moves the blue cursor and ripples automatically — no extra calls.
- **Stop it** when the task is done or on pause/abort: `cua.ps1 overlay-stop`.
- The overlay is click-through and top-most, so it never blocks real input. Normal `screenshot` auto-hides it (so you never see your own cursor); use `screenshot -Raw` only when you want to show the user where the cursor is.
- It is best-effort: if it is not running, every action still works exactly the same. Always `overlay-stop` at the end so it does not linger (it also self-exits after long inactivity).

Key names follow Codex's X-keysym style: `Return`, `Tab`, `space`, `Escape`, `BackSpace`, `Delete`, `Up/Down/Left/Right`, `Home/End`, `Prior`(PageUp)/`Next`(PageDown), `F1`–`F12`, modifiers `Control`/`Ctrl`/`Control_L`, `Alt`, `Shift`, `Super_L`/`Win`. Aliases like `Ctrl`, `Enter`, `Esc` are accepted.

## The loop (run this every step)

0. **Show the cursor** — once per session, `overlay-start` so the user can watch. `overlay-stop` when finished.
1. **Observe** — `screenshot`, then Read the PNG. Never act on a stale image; the screen may have changed.
2. **Locate** — find the target element in the screenshot; note its pixel (x, y). Prefer the visual center of the element.
3. **Act** — one `cua.ps1` action.
4. **Verify** — `screenshot` again and confirm the expected change (window opened, text appeared, selection moved). If it did not, diagnose from the new image, do not blindly repeat.
5. Repeat until the on-screen objective is satisfied, then report with the final screenshot.

Discipline:

- One action per turn-step, always followed by a fresh screenshot. This is what makes it reliable.
- After actions that change the UI (open menu/app, navigate), wait ~500–800 ms before the verifying screenshot so the UI settles.
- Coordinates are integers in screenshot pixel space, origin top-left of the screenshot. Multi-monitor: the screenshot spans all monitors; `origin` in the screenshot line is the virtual-screen offset the script already accounts for — keep using screenshot-relative (x, y).
- To type into a field, `click` it first to focus, then `type`.
- Global hotkeys go through `key` (e.g. `Super_L+r` Run dialog, `Alt+Tab` switch window, `Ctrl+s` save, `Alt+F4` close).

## Safety

- Confirm before: submitting forms with real consequences, sending messages, deleting, purchasing, entering passwords, or anything affecting other people or persistent state.
- Read-only navigation, screenshots, and moving the pointer need no confirmation.
- If a screenshot reveals sensitive content (passwords, tokens, private messages), do not transcribe it; describe only what is needed to proceed.
- `cua.ps1` inherits the user's existing Cursor command-approval settings; it adds no privileges.

## Combine with goal mode

For long autonomous GUI work ("keep operating this app until X"), run this loop **inside** the `codex-goal` skill: the goal file holds the objective and the completion audit ("prove X on screen with a screenshot"), and each wake does one observe→act→verify cycle. Computer use is the hands; goal mode is the persistence and the stop condition.

## Not yet ported

- macOS/Linux executors (the Codex native app also targets both; this port ships Windows first). The loop and SKILL are OS-agnostic — only `scripts/cua.ps1` is Windows.
- `drag_handle` (observe mid-drag before releasing) and audio capture from `@oai/sky` are omitted; `drag` covers the common case.
