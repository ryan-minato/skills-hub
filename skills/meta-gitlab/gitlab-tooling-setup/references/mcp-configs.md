# GitLab Duo MCP server: client configuration

## Fetch first

The official setup page is the source of truth and carries per-client
sections (Claude Code, Claude Desktop, Cursor, VS Code, Zed, and more):

<https://docs.gitlab.com/user/gitlab_duo/model_context_protocol/mcp_server/>

Fetch it, find the section for the framework hosting this session, and
follow it exactly. Use the offline fallback below only when the page
cannot be fetched.

## Facts that hold for every client

- Endpoint: `https://HOST/api/v4/mcp` — always the instance's own host,
  never a third-party URL.
- Requirements: GitLab ≥ 18.6, Premium or Ultimate, GitLab Duo enabled
  (Beta feature).
- Authentication: OAuth 2.0 Dynamic Client Registration. The client
  registers itself on first connection and opens a browser approval —
  no token is stored in the config file.
- Transport: HTTP is recommended (no local dependencies). Clients that
  only speak stdio go through the `mcp-remote` proxy (requires
  Node.js 20+).

## Offline fallback

### HTTP transport (recommended)

Claude Code:

```bash
claude mcp add --transport http GitLab https://HOST/api/v4/mcp
```

Generic JSON shape used by most HTTP-capable clients:

```json
{
  "mcpServers": {
    "GitLab": {
      "type": "http",
      "url": "https://HOST/api/v4/mcp"
    }
  }
}
```

### stdio transport via mcp-remote

For clients without native HTTP MCP support:

```json
{
  "mcpServers": {
    "GitLab": {
      "command": "npx",
      "args": ["-y", "mcp-remote@latest", "https://HOST/api/v4/mcp"]
    }
  }
}
```

Prefer pinning: replace `@latest` with the version you verified
(`npm view mcp-remote version`) so rebuilds stay deterministic.

## After configuring

The session must be restarted before the server's tools appear. First
call to any tool triggers the OAuth browser approval; the user completes
it once per client.
