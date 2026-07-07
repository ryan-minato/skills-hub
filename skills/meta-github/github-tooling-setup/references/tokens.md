# GitHub tokens: creation and wiring

## Create the token

Tokens are created at https://github.com/settings/personal-access-tokens
— the user must do this in their browser; an agent cannot create a PAT.

Recommended: a **fine-grained PAT**, scoped to the specific repositories
the agent works on, granting only the permissions the task needs:

- Issues: read/write for issue and milestone work.
- Pull requests: read/write for PR work.
- Contents: read (write when pushing commits, tags, or releases).
- Actions: read, when workflow runs or logs are inspected.
- Discussions: read, for research tasks.
- Projects: read/write when the agent manages Projects v2 boards.

Fallback: a **classic PAT** with the `repo` scope; add `read:org` when
org or team data is needed, and `project` when the agent manages
Projects v2 boards (for OAuth logins, `gh auth refresh -s project` adds
the same scope). Use a classic PAT only where fine-grained PATs are not
accepted.

## Which variable each consumer reads

| Consumer | Variable |
|---|---|
| gh CLI | `GH_TOKEN` (or `GITHUB_TOKEN`) |
| Local github-mcp-server (docker or binary) | `GITHUB_PERSONAL_ACCESS_TOKEN` |
| Remote server `Authorization` header | whichever variable the host config references — this catalog's convention is `GH_TOKEN`, the same variable gh reads |

`GH_TOKEN` is the convention because it also works as a user-level
Codespaces secret: secret names must not start with `GITHUB_`, so
`GITHUB_PAT`-style names cannot be injected that way, and `GITHUB_TOKEN`
collides with the narrower token Codespaces and Actions inject
automatically.

## Storage rules

- Store token values in environment variables or the OS keychain only —
  never in committed files.
- A token value must never appear in a config checked into git. Configs
  reference an environment variable using the syntax the host supports
  (the fetched install guide shows it); the value stays in the
  environment.
