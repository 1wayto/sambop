# Sambop with Hermes Agent

Hermes can connect to a remote Sambop MCP server using its `mcp_servers` config.

Example:

```yaml
mcp_servers:
  sambop:
    url: "https://mcp.sambop.com/mcp"
    headers:
      Authorization: "Bearer YOUR_SAMBOP_TOKEN"
```

Restart Hermes after changing MCP config.
