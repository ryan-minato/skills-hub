---
name: gitlab-tooling-setup
description: >
  Installs and configures GitLab tooling for a coding agent: the glab CLI
  installed per OS and authenticated against gitlab.com or any self-managed
  host (--hostname, GITLAB_HOST/GL_HOST, token environment variables), and
  optionally the GitLab Duo MCP server at https://<gitlab-host>/api/v4/mcp
  (Premium/Ultimate, GitLab 18.6+) for whatever agent framework is hosting
  the session, then verifies both. Use when connecting an agent to GitLab —
  "set up glab", "install glab", "connect this agent to GitLab", "set up
  GitLab MCP", "glab auth failed", "authenticate to our self-managed
  GitLab", "GitLab tools not working" — or when another GitLab skill
  reports that tooling is not set up.
license: Apache-2.0
compatibility: >
  scripts/check_tooling.py requires Python 3.9+ (stdlib only). Network
  probes need outbound HTTPS to the GitLab host (--skip-network disables
  them).
---

# GitLab Tooling Setup

Install and configure what an agent needs to work with GitLab: the glab
CLI with authentication (the primary path for every GitLab skill), and
optionally the GitLab Duo MCP server for the framework hosting the
session. This skill sets up the harness; the day-to-day operations that
use it live in the `gitlab` catalog's skills. Work through the sections
in order; skip whatever the assessment shows is already in place.

## Determine the target host

GitLab is often self-managed — never assume `gitlab.com`. Resolve the
host, in order: the project's git remote (`git remote get-url origin` —
the part right after `https://` or the `@`), then the `GITLAB_HOST` or
`GL_HOST` environment variable, then ask the user. Use `gitlab.com` only
when all three yield nothing. Everything below writes this value as
`HOST`.

## Assess current state

1. Inspect the tools available in this session. If a connected MCP server
   provides GitLab tools (issue, merge-request, or pipeline capabilities —
   each tool's description states its purpose; names vary across server
   versions), the GitLab Duo MCP server is already connected.
2. Run [scripts/check_tooling.py](scripts/check_tooling.py):

   ```bash
   python3 scripts/check_tooling.py --hostname HOST
   ```

   It prints one JSON object to stdout: glab install/auth state for the
   resolved host, which token environment variables are set (names and
   booleans only, never values), the host variables' values, and HTTPS
   reachability of the host's REST and MCP endpoints (add
   `--skip-network` in offline environments). The script cannot see MCP
   session state — only your own tool list can answer whether the MCP
   server is connected.

Done when: both the tool-list answer and the script's JSON are recorded.

## Decide what to install

Take the first row that matches; each situation has one recommended path.

| Situation | Install |
|---|---|
| glab installed and authenticated for HOST | Nothing — skip to Verify (or to MCP if the user asked for it) |
| glab installed, not authenticated for HOST | Authenticate glab (below) |
| glab missing | Install glab, then authenticate |
| User explicitly wants MCP, and HOST is Premium/Ultimate with GitLab Duo, GitLab ≥ 18.6 | Additionally configure the Duo MCP server |
| MCP wanted but the tier/version requirements are unmet (the probe's MCP endpoint check returned 404) | glab only — tell the user why MCP is unavailable |

glab comes first because it is free, covers every operation, and works on
any tier and any reachable host; the MCP server is doubly gated (license
tier and per-tool GitLab version) and exposes only a subset of
operations.

## Install glab

Read [references/glab-cli.md](references/glab-cli.md) when glab is
missing or `glab auth status` fails.

## Authenticate glab

Two facts govern authentication:

- Agents authenticate through the `GITLAB_TOKEN` environment variable,
  paired with `GITLAB_HOST=HOST` for self-managed instances — without the
  host variable, a token-only setup silently targets gitlab.com.
- To persist credentials instead, feed the token to a non-interactive
  login: `printf %s "$GITLAB_TOKEN" | glab auth login --hostname HOST
  --stdin`. The flag-less `glab auth login` is an interactive OAuth flow
  for humans — direct the user to run it themselves; never start it in a
  non-interactive session.

glab stores credentials per host; `glab auth status` lists every
configured host.

## Configure the Duo MCP server (fetch-first)

Read [references/mcp-configs.md](references/mcp-configs.md), fetch the
official setup page it names, and follow the fetched instructions for the
framework hosting you. The endpoint is always
`https://HOST/api/v4/mcp`; authentication is OAuth 2.0 Dynamic Client
Registration (no token in the config). Only if the page cannot be
fetched, use the offline fallback section of that reference.

## Tokens

Read [references/tokens.md](references/tokens.md) when a personal access
token must be created or a token environment variable configured.

## Verify

MCP configuration is loaded at session startup — after any MCP config
change, the session must be restarted before the server's tools can
appear. Tell the user this explicitly. After the restart:

1. Re-run the Assess step (tool list + script).
2. Smoke test: on the glab path run `glab api user --hostname HOST` and
   confirm it returns your user; on the MCP path call the tool that
   reports the server's version or connectivity.

Done when: the probe reports authenticated AND one smoke call returns
the user or server version.

## Gotchas

- `GITLAB_TOKEN` overrides credentials stored by `glab auth login`; when
  glab acts as the wrong account, check that variable first.
- A token without `GITLAB_HOST`/`GL_HOST` targets gitlab.com — the
  classic self-managed failure is a valid token used against the wrong
  host.
- MCP config changes never take effect mid-session: looking for the new
  tools before restarting always shows nothing, even when the config is
  correct.
- The MCP server needs Premium/Ultimate with GitLab Duo enabled and
  GitLab ≥ 18.6, and individual tools have their own minimum versions
  (18.3–19.2) — a connected server on an older self-managed instance
  shows a partial tool list. That is expected; use glab for the missing
  operations.
- Token environment precedence in glab is `GITLAB_TOKEN` >
  `GITLAB_ACCESS_TOKEN` > `OAUTH_TOKEN` (plus `CI_JOB_TOKEN` inside
  GitLab CI jobs).
- `glab mcp serve` (glab's own experimental MCP server) is not the Duo
  MCP server and is not a path this catalog uses.
