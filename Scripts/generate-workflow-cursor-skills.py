#!/usr/bin/env python3
"""Generate Cursor agent SKILL.md files from WorkflowSkillCatalog.swift."""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CATALOG = REPO / "Sources/LogicProMCP/Workflows/WorkflowSkillCatalog.swift"
OUT_ROOT = REPO / ".cursor/skills"


def slug(workflow_id: str) -> str:
    return workflow_id.replace(".", "-").replace("_", "-")


def parse_workflows(text: str) -> list[dict[str, str]]:
    pattern = re.compile(
        r"makeWorkflow\(\s*"
        r'id:\s*"([^"]+)",\s*'
        r'title:\s*"([^"]+)",\s*'
        r'intent:\s*"([^"]+)",\s*'
        r'scope:\s*"([^"]+)",',
        re.MULTILINE,
    )
    workflows = []
    for m in pattern.finditer(text):
        workflows.append(
            {
                "id": m.group(1),
                "title": m.group(2),
                "intent": m.group(3),
                "scope": m.group(4),
            }
        )
    return workflows


def render_skill(w: dict[str, str]) -> str:
    name = slug(w["id"])
    uri = f"logic://workflow-skills/{w['id']}"
    return f"""---
name: {name}
description: >-
  Logic Pro MCP workflow "{w['title']}". {w['intent']} Use when this recipe matches
  the session goal; load the full validated steps from logic-pro MCP before mutating.
---

# {w["title"]}

**Workflow id:** `{w["id"]}`

## Intent

{w["intent"]}

## Scope

{w["scope"]}

## How to run (honest)

1. Confirm Logic Pro MCP is connected (`logic_system` health or `logic://system/health`).
2. Read the full recipe: MCP resource `{uri}` or prompt `{w["id"]}` via `prompts/get`.
3. Execute steps in order. Name explicit track/slot/path targets before writes.
4. Treat State B (uncertain) as not success; verify with the workflow's resources.

Catalog index: `logic://workflow-skills` · schema: `logic://workflow-skills/schema`
"""


def main() -> int:
    if not CATALOG.is_file():
        print(f"Missing catalog: {CATALOG}", file=sys.stderr)
        return 1
    text = CATALOG.read_text(encoding="utf-8")
    workflows = parse_workflows(text)
    if not workflows:
        print("No workflows parsed from WorkflowSkillCatalog.swift", file=sys.stderr)
        return 1
    for w in workflows:
        dest = OUT_ROOT / slug(w["id"])
        dest.mkdir(parents=True, exist_ok=True)
        (dest / "SKILL.md").write_text(render_skill(w), encoding="utf-8")
        print(dest / "SKILL.md")
    print(f"Wrote {len(workflows)} workflow skills under {OUT_ROOT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())