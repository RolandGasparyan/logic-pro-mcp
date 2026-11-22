---
name: logic-workflow-bounce-readiness
description: >-
  Logic Pro MCP workflow "Bounce Readiness Checklist". Check project state before manual bounce/export. Use when this recipe matches
  the session goal; load the full validated steps from logic-pro MCP before mutating.
---

# Bounce Readiness Checklist

**Workflow id:** `logic.workflow.bounce.readiness`

## Intent

Check project state before manual bounce/export.

## Scope

Read-only checklist; export remains manual unless a future tool explicitly supports it.

## How to run (honest)

1. Confirm Logic Pro MCP is connected (`logic_system` health or `logic://system/health`).
2. Read the full recipe: MCP resource `logic://workflow-skills/logic.workflow.bounce.readiness` or prompt `logic.workflow.bounce.readiness` via `prompts/get`.
3. Execute steps in order. Name explicit track/slot/path targets before writes.
4. Treat State B (uncertain) as not success; verify with the workflow's resources.

Catalog index: `logic://workflow-skills` · schema: `logic://workflow-skills/schema`
