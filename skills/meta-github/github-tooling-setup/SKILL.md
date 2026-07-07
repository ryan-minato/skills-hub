---
name: github-tooling-setup
description: >
  Installs and configures GitHub tooling for a coding agent: the GitHub
  MCP server (remote HTTP or local stdio) for whatever agent framework is
  hosting the session, using the official per-host install guides fetched
  at runtime, plus gh CLI installation and authentication per OS, then
  verifies both. Use when connecting an agent to GitHub — "set up GitHub
  MCP", "install gh", "connect this agent to GitHub", "gh auth failed",
  "GitHub tools not working" — or when another GitHub skill reports that
  tooling is not set up.
license: Apache-2.0
compatibility: >
  scripts/check_tooling.py requires Python 3.9+ (stdlib only). Network
  probes need outbound HTTPS (--skip-network disables them).
---

# GitHub Tooling Setup

Install and configure what an agent needs to work with GitHub: the GitHub
MCP server for the framework hosting the session, and the gh CLI with
authentication. Work through the sections in order; skip whatever the
assessment shows is already in place.

## Assess current state

1. Inspect the tools available in this session. If any tool name contains
   `issue_read`, `pull_request_read`, or a `github` MCP server prefix
   (for example `mcp__github__...`), the GitHub MCP server is already
   connected.
2. Run [scripts/check_tooling.py](scripts/check_tooling.py):

   ```bash
   python3 scripts/check_tooling.py
   ```

   It prints one JSON object to stdout: gh install/auth state, docker
   availability, which token environment variables are set (names and
   booleans only, never values), and HTTPS reachability of the GitHub
   endpoints (add `--skip-network` in offline environments). The script
   cannot see MCP session state — only your own tool list can answer
   whether the MCP server is connected.

Done when: both the tool-list answer and the script's JSON are recorded.

## Decide what to install

Take the first row that matches; each situation has one recommended path.

| Situation | Install |
|---|---|
| MCP server already connected (tool-list check above) | Nothing — skip to Verify |
| Host supports remote MCP with an `Authorization` header, and a PAT is acceptable | Remote HTTP server |
| Otherwise, or org policy / air-gapped network rules out the remote endpoint | Local stdio server via docker (recommended by upstream) |
| Local server needed but docker is unavailable | Local stdio via the release binary |
| Framework cannot use MCP at all | gh CLI only |

Reason the PAT question decides: full remote OAuth support is rare among
hosts — most use a PAT in a header or a local server.

## Configure the MCP server (fetch-first)

Read [references/framework-configs.md](references/framework-configs.md),
find the row for the framework hosting you, fetch its official
installation-guide URL, and follow the fetched guide. The guides are the
source of truth and stay current as the server evolves. Only if the guide
cannot be fetched, use the offline fallback section at the bottom of that
reference.

## Install and authenticate gh

Read [references/gh-cli.md](references/gh-cli.md) when gh is missing or
`gh auth status` fails. Two facts govern authentication:

- Agents authenticate through the `GH_TOKEN` environment variable.
- `gh auth login` is an interactive flow for humans — direct the user to
  run it themselves; never start it in a non-interactive session.

## Tokens

Read [references/tokens.md](references/tokens.md) when a personal access
token must be created or a token environment variable configured.

## Verify

MCP configuration is loaded at session startup — after any MCP config
change, the session must be restarted before the server's tools can
appear. Tell the user this explicitly. After the restart:

1. Re-run the Assess step (tool list + script).
2. Smoke test: on the MCP path call the `get_me` tool; on the gh path
   run `gh api user -q .login`.

Done when: the probe reports authenticated AND one smoke call returns
the login.

## Gotchas

- MCP config changes never take effect mid-session: looking for the new
  tools before restarting always shows nothing, even when the config is
  correct.
- The remote server rejects unauthenticated requests — a bare URL entry
  fails until an `Authorization` header (or host-managed OAuth) is added.
- The docker stdio server exits silently when the token variable is empty
  — pass `-e GITHUB_PERSONAL_ACCESS_TOKEN` with a value actually set in
  the host environment.
- Default toolsets are context, issues, pull_requests, repos, and users —
  the discussions, actions, and labels toolsets must be enabled via
  `GITHUB_TOOLSETS` (local) or a per-toolset URL (remote).
- `GH_TOKEN` overrides credentials stored by `gh auth login`; when gh
  acts as the wrong account, check that variable first.
- MCP tool names have changed across github-mcp-server versions. If a tool
  named in a table is absent, list the github server's available tools and
  pick the same-purpose name; if none matches, fall back to the gh column.
