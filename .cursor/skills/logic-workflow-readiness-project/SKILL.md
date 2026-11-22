---
name: logic-workflow-readiness-project
description: >-
  Logic Pro MCP workflow "Project Readiness Check". Confirm Logic Pro, MCP resources, project state, tracks, transport, and mixer provenance before creative work. Use when this recipe matches
  the session goal; load the full validated steps from logic-pro MCP before mutating.
---

# Project Readiness Check

**Workflow id:** `logic.workflow.readiness.project`

## Intent

Confirm Logic Pro, MCP resources, project state, tracks, transport, and mixer provenance before creative work.

## Scope

Read-only diagnostics; does not mutate project state.

## How to run (honest)

1. Confirm Logic Pro MCP is connected (`logic_system` health or `logic://system/health`).
2. Read the full recipe: MCP resource `logic://workflow-skills/logic.workflow.readiness.project` or prompt `logic.workflow.readiness.project` via `prompts/get`.
3. Execute steps in order. Name explicit track/slot/path targets before writes.
4. Treat State B (uncertain) as not success; verify with the workflow's resources.

Catalog index: `logic://workflow-skills` · schema: `logic://workflow-skills/schema`
