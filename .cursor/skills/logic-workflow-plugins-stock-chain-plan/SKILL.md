---
name: logic-workflow-plugins-stock-chain-plan
description: >-
  Logic Pro MCP workflow "Stock Plugin Chain Planning". Plan stock plugin chains from verified catalog metadata without claiming insertion success. Use when this recipe matches
  the session goal; load the full validated steps from logic-pro MCP before mutating.
---

# Stock Plugin Chain Planning

**Workflow id:** `logic.workflow.plugins.stock_chain_plan`

## Intent

Plan stock plugin chains from verified catalog metadata without claiming insertion success.

## Scope

Planning-only in this release; no plugin insertion is executed.

## How to run (honest)

1. Confirm Logic Pro MCP is connected (`logic_system` health or `logic://system/health`).
2. Read the full recipe: MCP resource `logic://workflow-skills/logic.workflow.plugins.stock_chain_plan` or prompt `logic.workflow.plugins.stock_chain_plan` via `prompts/get`.
3. Execute steps in order. Name explicit track/slot/path targets before writes.
4. Treat State B (uncertain) as not success; verify with the workflow's resources.

Catalog index: `logic://workflow-skills` · schema: `logic://workflow-skills/schema`
