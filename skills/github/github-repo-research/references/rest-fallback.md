# REST fallback: reading without MCP or gh

This tier applies when step 3 of "Choose your path" selected it: the
GitHub MCP server is not connected and gh is not authenticated, but the
target repository is public — or a token sits in `GH_TOKEN`/`GITHUB_TOKEN`
without gh being installed. Everything here is read-only; publishing is
impossible on this tier by design.

All reads go through one bundled script,
[scripts/rest_read.py](scripts/rest_read.py) (Python 3.9+ stdlib). It
projects responses down to the fields research needs so raw API objects do
not flood the context (`--raw` returns the full payload), and it never
prints token values.

## Task → invocation

| Task | Command |
|---|---|
| List issues | `python3 scripts/rest_read.py issues --repo O/R [--state all]` |
| Read issue + comments | `python3 scripts/rest_read.py issue --repo O/R --number N --comments` |
| List labels | `python3 scripts/rest_read.py labels --repo O/R` |
| List PRs | `python3 scripts/rest_read.py prs --repo O/R [--state all]` |
| Read PR | `python3 scripts/rest_read.py pr --repo O/R --number N` |
| PR diff | `python3 scripts/rest_read.py pr --repo O/R --number N --diff` |
| PR changed files | `python3 scripts/rest_read.py pr --repo O/R --number N --files` |
| PR reviews | `python3 scripts/rest_read.py pr --repo O/R --number N --reviews` |
| PR review comments | `python3 scripts/rest_read.py pr --repo O/R --number N --comments` |
| PR check results | `python3 scripts/rest_read.py pr --repo O/R --number N --checks` |
| List workflow runs | `python3 scripts/rest_read.py runs --repo O/R [--limit 20]` |
| Inspect one run | `python3 scripts/rest_read.py run --repo O/R --run-id ID` |
| A run's jobs | `python3 scripts/rest_read.py jobs --repo O/R --run-id ID` |
| Failed jobs + log tails | `python3 scripts/rest_read.py run-failures --repo O/R --run-id ID [--tail 50]` |
| Search issues/PRs | `python3 scripts/rest_read.py search --repo O/R --query "repo:O/R is:issue TEXT"` |
| List releases | `python3 scripts/rest_read.py releases --repo O/R [--limit 20]` |
| Read one release | `python3 scripts/rest_read.py releases --repo O/R --tag TAG` (or `--latest`) |
| List tags | `python3 scripts/rest_read.py tags --repo O/R` |
| List discussions | `python3 scripts/rest_read.py discussions --repo O/R` |
| Read one discussion | `python3 scripts/rest_read.py discussion --repo O/R --number N` |

Exit codes: 0 = read succeeded, 1 = network/HTTP failure (rate-limit
exhaustion is reported with its reset time), 2 = bad arguments.

## What a token changes (optional, picked up automatically)

The script uses `GH_TOKEN` (then `GITHUB_TOKEN`) when set:

- Rate limit rises from 60 requests/hour per IP to 5,000/hour
  (search: from 10/minute to 30/minute).
- Discussions upgrade from best-effort engines to full-fidelity GraphQL
  (the output's `engine` field says which one served the request).
- Actions **log text** becomes readable; without a token GitHub answers
  403 for log downloads even on public repositories, and `run-failures`
  reports the failed jobs and step names only.

## Tokenless limits (public repositories)

- Discussions list: the public Atom feed — latest ~25 discussions, no
  category filter. One discussion: text extracted from the HTML page
  (`engine: html-besteffort`; authorship and threading are not
  preserved). If GitHub changes its markup the script exits 1 and names
  the alternatives.
- Stay frugal with calls: 60/hour disappears quickly. Prefer one targeted
  read over broad listing, and stop when the script reports the limit.
