# GitHub MCP server: per-framework configuration

## Fetch-first rule

The official per-host installation guides are the source of truth for
configuring the GitHub MCP server: they stay current as the server
evolves, while any copy embedded here would rot. Find the host below,
fetch its guide URL, and follow the fetched guide exactly.

How to fetch: use the WebFetch tool if this session has one; otherwise
run `curl -fsSL <url>`.

Use the offline fallback at the bottom of this file only when the guide
cannot be fetched.

## Official installation guides

Every URL follows the pattern
`https://raw.githubusercontent.com/github/github-mcp-server/main/docs/installation-guides/<file>`.

| Host | Official guide (raw URL) | Config it edits |
|---|---|---|
| Claude Code / Claude Desktop | https://raw.githubusercontent.com/github/github-mcp-server/main/docs/installation-guides/install-claude.md | `.mcp.json` / `claude mcp add` |
| Codex CLI | https://raw.githubusercontent.com/github/github-mcp-server/main/docs/installation-guides/install-codex.md | `~/.codex/config.toml` |
| Gemini CLI | https://raw.githubusercontent.com/github/github-mcp-server/main/docs/installation-guides/install-gemini-cli.md | `~/.gemini/settings.json` |
| OpenCode | https://raw.githubusercontent.com/github/github-mcp-server/main/docs/installation-guides/install-opencode.md | `opencode.json` |
| Antigravity | https://raw.githubusercontent.com/github/github-mcp-server/main/docs/installation-guides/install-antigravity.md | `~/.gemini/antigravity/mcp_config.json` (global), or the IDE's MCP panel |
| Cline | https://raw.githubusercontent.com/github/github-mcp-server/main/docs/installation-guides/install-cline.md | see guide |
| Roo Code | https://raw.githubusercontent.com/github/github-mcp-server/main/docs/installation-guides/install-roo-code.md | see guide |
| Cursor | https://raw.githubusercontent.com/github/github-mcp-server/main/docs/installation-guides/install-cursor.md | `.cursor/mcp.json` |
| Windsurf | https://raw.githubusercontent.com/github/github-mcp-server/main/docs/installation-guides/install-windsurf.md | see guide |
| Zed | https://raw.githubusercontent.com/github/github-mcp-server/main/docs/installation-guides/install-zed.md | see guide |
| Copilot CLI | https://raw.githubusercontent.com/github/github-mcp-server/main/docs/installation-guides/install-copilot-cli.md | see guide |
| Copilot in other IDEs | https://raw.githubusercontent.com/github/github-mcp-server/main/docs/installation-guides/install-other-copilot-ides.md | see guide |
| Xcode | https://raw.githubusercontent.com/github/github-mcp-server/main/docs/installation-guides/install-xcode.md | see guide |

Framework not listed → fetch the index and look for a new guide:
https://raw.githubusercontent.com/github/github-mcp-server/refs/heads/main/docs/installation-guides/README.md

Note: a workspace-level `.agents/mcp_config.json` is the
Antigravity/Gemini-family convention, not a universal standard — do not
copy it to other hosts.

## Offline fallback

Only when the guide cannot be fetched. These values match the upstream
docs at the time this skill was written.

### Remote server (HTTP)

- Endpoint: `https://api.githubcopilot.com/mcp/`
- Required header: `Authorization: Bearer YOUR_GITHUB_PAT`
- Per-toolset endpoints: `https://api.githubcopilot.com/mcp/x/{toolset}`
  (for example `.../mcp/x/issues`); append `/readonly` for the read-only
  variant of an endpoint.

Verified concrete example — Claude Code (2.1.1+):

```bash
claude mcp add-json github '{"type":"http","url":"https://api.githubcopilot.com/mcp/","headers":{"Authorization":"Bearer YOUR_GITHUB_PAT"}}'
claude mcp list
```

Replace `YOUR_GITHUB_PAT` with an environment-variable reference if the
host supports it (this catalog's convention: `GH_TOKEN`); never paste the
token value into a committed file.

### Local server (stdio) via docker

Configure the host to run this as the stdio server command:

```bash
docker run -i --rm -e GITHUB_PERSONAL_ACCESS_TOKEN ghcr.io/github/github-mcp-server
```

`GITHUB_PERSONAL_ACCESS_TOKEN` must be set (non-empty) in the environment
the host launches the command from — the server exits silently otherwise.

### Local server (stdio) via release binary

Download `github-mcp-server` for the OS/architecture from
https://github.com/github/github-mcp-server/releases, then configure the
host to run `github-mcp-server stdio` with `GITHUB_PERSONAL_ACCESS_TOKEN`
set in its environment.

### Local server options

- Toolset selection:
  `GITHUB_TOOLSETS=issues,pull_requests,actions,discussions,labels`
  (or `GITHUB_TOOLSETS=all`).
- Read-only mode: `GITHUB_READ_ONLY=1`.
- GitHub Enterprise: set `GITHUB_HOST` to the enterprise hostname.
