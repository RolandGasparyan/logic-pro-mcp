---
name: logic-workflow-mixer-gain-staging-prep
description: >-
  Logic Pro MCP workflow "Gain Staging And Mixer Prep". Prepare safe gain-staging recommendations using mixer provenance and explicit target verification. Use when this recipe matches
  the session goal; load the full validated steps from logic-pro MCP before mutating.
---

# Gain Staging And Mixer Prep

**Workflow id:** `logic.workflow.mixer.gain_staging_prep`

## Intent

Prepare safe gain-staging recommendations using mixer provenance and explicit target verification.

## Scope

May call mixer writes only when target and readback conditions are explicit.

## How to run (honest)

1. Confirm Logic Pro MCP is connected (`logic_system` health or `logic://system/health`).
2. Read the full recipe: MCP resource `logic://workflow-skills/logic.workflow.mixer.gain_staging_prep` or prompt `logic.workflow.mixer.gain_staging_prep` via `prompts/get`.
3. Execute steps in order. Name explicit track/slot/path targets before writes.
4. Treat State B (uncertain) as not success; verify with the workflow's resources.

Catalog index: `logic://workflow-skills` · schema: `logic://workflow-skills/schema`
