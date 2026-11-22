---
name: logic-workflow-composition-session-plan
description: >-
  Logic Pro MCP workflow "Planning-Only Composition Session Plan". Turn a natural-language musical prompt into a structured, non-mutating Logic session plan. Use when this recipe matches
  the session goal; load the full validated steps from logic-pro MCP before mutating.
---

# Planning-Only Composition Session Plan

**Workflow id:** `logic.workflow.composition.session_plan`

## Intent

Turn a natural-language musical prompt into a structured, non-mutating Logic session plan.

## Scope

Dry-run resource read only; proposes later MCP steps but never executes tools.

## How to run (honest)

1. Confirm Logic Pro MCP is connected (`logic_system` health or `logic://system/health`).
2. Read the full recipe: MCP resource `logic://workflow-skills/logic.workflow.composition.session_plan` or prompt `logic.workflow.composition.session_plan` via `prompts/get`.
3. Execute steps in order. Name explicit track/slot/path targets before writes.
4. Treat State B (uncertain) as not success; verify with the workflow's resources.

Catalog index: `logic://workflow-skills` · schema: `logic://workflow-skills/schema`
