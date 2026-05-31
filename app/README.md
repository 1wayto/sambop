# Sambop Placeholder Server

This dependency-free Python server runs the temporary Sambop landing page, GitHub login placeholder, and minimal MCP JSON-RPC tools from the Hermes playground.

## Run locally

```bash
SAMBOP_PORT=8788 python3 app/server.py
```

## Placeholder endpoints

- `GET /` — landing page
- `GET /login/github` — redirects to GitHub when OAuth env is configured; otherwise returns a placeholder response
- `GET /mcp` — lists placeholder MCP tools
- `POST /mcp` — supports `initialize`, `tools/list`, and `tools/call`
- `GET /api/projects` — placeholder project list
- `GET /api/skills` — placeholder skill list
- `POST /oauth/register` — placeholder public-client dynamic registration response

## Environment

```bash
SAMBOP_HOST=127.0.0.1
SAMBOP_PORT=8788
SAMBOP_PUBLIC_BASE_URL=https://sambop.com
SAMBOP_GITHUB_CLIENT_ID=...
SAMBOP_GITHUB_CLIENT_SECRET=...
```
