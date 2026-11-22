---
name: logic-workflow-arrangement-marker-plan
description: >-
  Logic Pro MCP workflow "Arrangement Marker Plan". Plan and verify marker positions without relying on stale parser assumptions. Use when this recipe matches
  the session goal; load the full validated steps from logic-pro MCP before mutating.
---

# Arrangement Marker Plan

**Workflow id:** `logic.workflow.arrangement.marker_plan`

## Intent

Plan and verify marker positions without relying on stale parser assumptions.

## Scope

Read-first marker planning; mutation remains guarded and optional.

## How to run (honest)

1. Confirm Logic Pro MCP is connected (`logic_system` health or `logic://system/health`).
2. Read the full recipe: MCP resource `logic://workflow-skills/logic.workflow.arrangement.marker_plan` or prompt `logic.workflow.arrangement.marker_plan` via `prompts/get`.
3. Execute steps in order. Name explicit track/slot/path targets before writes.
4. Treat State B (uncertain) as not success; verify with the workflow's resources.

Catalog index: `logic://workflow-skills` · schema: `logic://workflow-skills/schema`
