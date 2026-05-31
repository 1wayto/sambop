# Install Sambop MCP in AI Tools

Sambop should support every major AI coding tool through either native MCP config, a stdio proxy, or generated instruction files.

## Universal flow

1. Login to Sambop with GitHub.
2. Get a Sambop MCP token.
3. Add Sambop MCP to your AI tool.
4. Clone a Sambop-enabled repo.
5. Ask your AI to read `README.md`, `SAMBOP.md`, and `AGENTS.md`.
6. Work through branches and PRs.

## Remote MCP shape

```json
{
  "mcpServers": {
    "sambop": {
      "url": "https://mcp.sambop.com/mcp",
      "headers": {
        "Authorization": "Bearer YOUR_SAMBOP_TOKEN"
      }
    }
  }
}
```

## Stdio proxy shape

```json
{
  "mcpServers": {
    "sambop": {
      "command": "npx",
      "args": ["-y", "@sambop/mcp-proxy"],
      "env": {
        "SAMBOP_TOKEN": "YOUR_SAMBOP_TOKEN"
      }
    }
  }
}
```

## Target tools

- Hermes Agent
- Claude Code
- Claude Desktop
- OpenAI Codex CLI
- GitHub Copilot / VS Code Copilot
- Cursor
- Google Antigravity
- Windsurf
- OpenCode
- Aider
- Cline / Roo Code
- Continue
- ChatGPT connectors
- Local Llama / Ollama agents
