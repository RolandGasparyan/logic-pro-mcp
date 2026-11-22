---
name: logic-workflow-midi-idea-sketch
description: >-
  Logic Pro MCP workflow "MIDI Idea Sketch". Create or import a small MIDI idea only after the target track and project state are explicit. Use when this recipe matches
  the session goal; load the full validated steps from logic-pro MCP before mutating.
---

# MIDI Idea Sketch

**Workflow id:** `logic.workflow.midi.idea_sketch`

## Intent

Create or import a small MIDI idea only after the target track and project state are explicit.

## Scope

May write MIDI to a caller-specified target after confirmation; never guesses track 0.

## How to run (honest)

1. Confirm Logic Pro MCP is connected (`logic_system` health or `logic://system/health`).
2. Read the full recipe: MCP resource `logic://workflow-skills/logic.workflow.midi.idea_sketch` or prompt `logic.workflow.midi.idea_sketch` via `prompts/get`.
3. Execute steps in order. Name explicit track/slot/path targets before writes.
4. Treat State B (uncertain) as not success; verify with the workflow's resources.

Catalog index: `logic://workflow-skills` · schema: `logic://workflow-skills/schema`
