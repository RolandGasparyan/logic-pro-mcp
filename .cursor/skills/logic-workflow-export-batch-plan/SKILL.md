---
name: logic-workflow-export-batch-plan
description: >-
  Logic Pro MCP workflow "Batch Export Manifest Plan". Generate a dry-run batch export manifest before any Logic project is opened, bounced, or closed. Use when this recipe matches
  the session goal; load the full validated steps from logic-pro MCP before mutating.
---

# Batch Export Manifest Plan

**Workflow id:** `logic.workflow.export.batch_plan`

## Intent

Generate a dry-run batch export manifest before any Logic project is opened, bounced, or closed.

## Scope

Read-only planning; returns expected artifact paths, verification gates, and blocked execution steps.

## How to run (honest)

1. Confirm Logic Pro MCP is connected (`logic_system` health or `logic://system/health`).
2. Read the full recipe: MCP resource `logic://workflow-skills/logic.workflow.export.batch_plan` or prompt `logic.workflow.export.batch_plan` via `prompts/get`.
3. Execute steps in order. Name explicit track/slot/path targets before writes.
4. Treat State B (uncertain) as not success; verify with the workflow's resources.

Catalog index: `logic://workflow-skills` · schema: `logic://workflow-skills/schema`
