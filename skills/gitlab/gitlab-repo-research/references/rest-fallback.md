# REST fallback — reading without glab

Used only when step 3 of "Choose your path" selected it: glab is absent,
and the project is public or a token is set in
`GITLAB_TOKEN`/`GITLAB_ACCESS_TOKEN`. Everything is read-only.

[scripts/rest_read.py](scripts/rest_read.py) (Python 3.9+, stdlib only)
talks to the GitLab REST API v4 directly. It picks the token up from the
environment automatically and sends it as the `PRIVATE-TOKEN` header;
token values are never printed. `--host` (or `GITLAB_HOST`/`GL_HOST`)
selects the instance — it defaults to gitlab.com only when nothing else
is set.

Output is a compact field projection by default; add `--raw` for the
full API payload. `--help` lists every subcommand and flag.

## Task → invocation

`--project G/P` and `--host HOST` follow the subcommand.

| Task | Invocation |
|---|---|
| List/filter issues | `python3 scripts/rest_read.py issues --project G/P --host HOST [--state closed] [--labels bug] [--search "TEXT"]` |
| Read issue + comments | `python3 scripts/rest_read.py issue --project G/P --host HOST --number N --comments` |
| List labels | `python3 scripts/rest_read.py labels --project G/P --host HOST` |
| List/filter MRs | `python3 scripts/rest_read.py mrs --project G/P --host HOST [--state merged]` |
| Read MR | `python3 scripts/rest_read.py mr --project G/P --host HOST --number N` |
| MR diff / commits / notes / approvals / pipelines | same, plus exactly one of `--diff` `--commits` `--notes` `--approvals` `--pipelines` |
| List pipelines | `python3 scripts/rest_read.py pipelines --project G/P --host HOST [--status failed]` |
| Pipeline jobs | `python3 scripts/rest_read.py jobs --project G/P --host HOST --pipeline-id ID` |
| Failed-job log tails | `python3 scripts/rest_read.py pipeline-failures --project G/P --host HOST --pipeline-id ID [--tail 50]` |
| Search | `python3 scripts/rest_read.py search --scope issues --query "TEXT" --host HOST [--group GROUP]` |
| List releases | `python3 scripts/rest_read.py releases --project G/P --host HOST [--limit 20]` |
| Read one release | `python3 scripts/rest_read.py releases --project G/P --host HOST --tag TAG` (or `--latest`) |
| List tags | `python3 scripts/rest_read.py tags --project G/P --host HOST` |

## What a token changes

- Private and internal projects become readable.
- Rate limits rise substantially (unauthenticated gitlab.com is heavily
  limited; the script surfaces `Retry-After` on 429 — stop, don't
  retry).
- Issue/MR **notes**, **labels**, the **search** API, and **job traces**
  become readable — gitlab.com now auth-gates these even on public
  projects (the script reports each as a clean 401 diagnostic, or
  per-job `log_error` data in `pipeline-failures`).

## Tokenless limits

Public projects only, and only part of their surface: issue and MR
lists/details, diffs, commits, approvals, pipelines, and job listings
work; comments, labels, search, and traces need a token on gitlab.com
(a self-managed instance may be more permissive — its admin decides).
Low rate limits throughout.
