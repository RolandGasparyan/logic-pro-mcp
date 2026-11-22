---
name: logic-workflow-plugins-stock-insert-gain-live-verified
description: >-
  Logic Pro MCP workflow "Live-Verified Gain Insert". Insert Logic's stock Gain plugin only after catalog lookup, explicit track/slot confirmation, empty-slot checks, and AX slot readback. Use when this recipe matches
  the session goal; load the full validated steps from logic-pro MCP before mutating.
---

# Live-Verified Gain Insert

**Workflow id:** `logic.workflow.plugins.stock_insert_gain_live_verified`

## Intent

Insert Logic's stock Gain plugin only after catalog lookup, explicit track/slot confirmation, empty-slot checks, and AX slot readback.

## Scope

Guarded mutation for the allowlisted stock Gain plugin; never replaces an occupied slot.

## How to run (honest)

1. Confirm Logic Pro MCP is connected (`logic_system` health or `logic://system/health`).
2. Read the full recipe: MCP resource `logic://workflow-skills/logic.workflow.plugins.stock_insert_gain_live_verified` or prompt `logic.workflow.plugins.stock_insert_gain_live_verified` via `prompts/get`.
3. Execute steps in order. Name explicit track/slot/path targets before writes.
4. Treat State B (uncertain) as not success; verify with the workflow's resources.

Catalog index: `logic://workflow-skills` · schema: `logic://workflow-skills/schema`
