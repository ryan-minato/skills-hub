# GitLab tokens: creation and wiring

## Create the token

Personal access tokens are created at
`https://HOST/-/user_settings/personal_access_tokens` — the user must do
this in their browser; an agent cannot create a PAT.

Recommended scopes, smallest that works:

- `read_api` — research-only work (reading issues, MRs, pipelines).
- `api` — any write work (creating issues/MRs, comments, labels, wiki
  pages).
- add `write_repository` only when glab must push over HTTPS (for
  example the wiki git path).

Scoped alternatives where the instance allows them: a **project access
token** or **group access token** limits blast radius to one project or
group (project/group access tokens are Free on self-managed instances,
Premium on gitlab.com — a dedicated bot user's PAT is the gitlab.com
Free alternative).

## Which variable each consumer reads

| Consumer | Variable |
|---|---|
| glab CLI | `GITLAB_TOKEN` (then `GITLAB_ACCESS_TOKEN`, then `OAUTH_TOKEN`), plus `GITLAB_HOST`/`GL_HOST` for the instance |
| REST fallback scripts in this catalog | `GITLAB_TOKEN` (then `GITLAB_ACCESS_TOKEN`), sent as the `PRIVATE-TOKEN` header |
| Duo MCP server | none — OAuth Dynamic Client Registration, no PAT wiring |

`GITLAB_TOKEN` is the convention because glab reads it natively and every
script in this catalog reuses it, so one variable covers all paths.

## Storage rules

- Store token values in environment variables or the OS keychain only —
  never in committed files.
- A token value must never appear in a config checked into git. Configs
  reference an environment variable using the syntax the host supports;
  the value stays in the environment.
- Set an expiry on every PAT and prefer per-project tokens for
  long-lived automation.
