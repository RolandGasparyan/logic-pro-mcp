---
name: logic-workflow-project-audit-cleanup-plan
description: >-
  Logic Pro MCP workflow "Project Audit And Cleanup Plan". Inspect a messy Logic session, identify deterministic risks, and produce a serializable cleanup plan before any mutation. Use when this recipe matches
  the session goal; load the full validated steps from logic-pro MCP before mutating.
---

# Project Audit And Cleanup Plan

**Workflow id:** `logic.workflow.project.audit_cleanup_plan`

## Intent

Inspect a messy Logic session, identify deterministic risks, and produce a serializable cleanup plan before any mutation.

## Scope

Read-only audit and planning; no cleanup step is executed by this workflow.

## How to run (honest)

1. Confirm Logic Pro MCP is connected (`logic_system` health or `logic://system/health`).
2. Read the full recipe: MCP resource `logic://workflow-skills/logic.workflow.project.audit_cleanup_plan` or prompt `logic.workflow.project.audit_cleanup_plan` via `prompts/get`.
3. Execute steps in order. Name explicit track/slot/path targets before writes.
4. Treat State B (uncertain) as not success; verify with the workflow's resources.

Catalog index: `logic://workflow-skills` · schema: `logic://workflow-skills/schema`
