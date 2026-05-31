# Sambop MCP Placeholder

The first public MCP surface is intentionally small while GitHub OAuth and real orchestration are built.

## Endpoint

```text
https://sambop.com/mcp
```

## Initial tools

- `list_projects` — list public Sambop projects
- `list_skills` — list reusable skills from solved projects
- `install_skill` — return install guidance for a skill/platform
- `get_login_url` — return GitHub login URL or placeholder setup state

## Example JSON-RPC calls

Initialize:

```bash
curl -s https://sambop.com/mcp \
  -H 'content-type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}'
```

List tools:

```bash
curl -s https://sambop.com/mcp \
  -H 'content-type: application/json' \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/list"}'
```

Call a tool:

```bash
curl -s https://sambop.com/mcp \
  -H 'content-type: application/json' \
  -d '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"list_projects","arguments":{}}}'
```
