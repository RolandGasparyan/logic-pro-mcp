---
name: logic-pro-mcp-install
description: >-
  Installs and verifies Logic Pro MCP per logicpromcp.com install (Homebrew binary,
  Cursor mcp.json, permissions, doctor). Use when setting up Logic Pro MCP in Cursor,
  fixing a red MCP indicator, or after reinstalling the server.
---

# Logic Pro MCP install (Cursor)

Follow [logicpromcp.com/#install](https://logicpromcp.com/#install) and [docs/CURSOR.md](docs/CURSOR.md). Logic Pro MCP runs on **macOS only**; Cloud Agent Linux VMs cannot host `LogicProMCP`.

## One-shot on your Mac

```bash
brew tap MongLong0214/logic-pro-mcp https://github.com/MongLong0214/logic-pro-mcp
brew trust monglong0214/logic-pro-mcp
brew install logic-pro-mcp
bash Scripts/mac-full-mcp-connect.sh
bash Scripts/install-cursor-skills.sh
```

## Cursor MCP registration

Merge into `~/.cursor/mcp.json` or this repo's `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "logic-pro": {
      "type": "stdio",
      "command": "LogicProMCP",
      "args": []
    }
  }
}
```

Enable **logic-pro** under Cursor → Customize → MCP. Grant **Cursor** Accessibility, Logic Pro Automation, System Events Automation, and Input Monitoring (Cursor spawns the child process).

## Verify

```bash
LogicProMCP --check-permissions
LogicProMCP doctor --profile core --client cursor
```

Success means Customize shows **logic-pro** enabled with tools listed, and Doctor has no unresolved **required** check for the cursor profile. Discovery is not proof of a verified Logic write.

## Workflow recipes after connect

Read `logic://workflow-skills` or use the generated skills under `.cursor/skills/logic-workflow-*`.