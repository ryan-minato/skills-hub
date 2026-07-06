---
name: github-repo-research
description: >
  Read-only research over any GitHub repository, including repositories
  you cannot write to: reads issues, pull requests, CI check results,
  Actions runs and failed-job logs, and Discussions through one
  recommended path — GitHub MCP tools, gh commands, or a bundled REST
  script that works without authentication on public repositories. Use
  when investigating a repository — "what issues are open on that repo",
  "read the comments on that PR", "summarize issue #N of owner/repo",
  "what was decided in that discussion", "show recent workflow runs",
  "why did the nightly build fail", or "get the logs from that Actions
  run".
license: Apache-2.0
compatibility: >
  scripts/run_log_digest.py requires Python 3.9+ (stdlib only) and an
  authenticated gh CLI; scripts/rest_read.py requires Python 3.9+ (stdlib
  only) and outbound HTTPS to api.github.com and github.com.
---

# GitHub Repo Research

This skill is read-only: it never posts, edits, or changes anything, so it
has no publish gate — which is also why it works on repositories you have
no write access to. If the task turns into posting — commenting, filing an
issue, reviewing or fixing CI via a PR — switch to `github-issues` or
`github-pull-requests`. If GitHub tooling itself is missing or
misconfigured, that is `github-tooling-setup` work.

## Choose your path (do this first, once per session)

1. Look at the tools available in this session. If any tool name contains
   `issue_read`, `pull_request_read`, or a `github` MCP server prefix (for
   example `mcp__github__...`), the GitHub MCP server is connected: use the
   **MCP** column of every table below.
2. Otherwise run `gh auth status`. If it exits 0, use the **gh** column.
3. Otherwise, if the target repository is public, or a token is set in
   `GH_TOKEN`/`GITHUB_TOKEN` even though gh is missing, use the REST
   fallback: read [references/rest-fallback.md](references/rest-fallback.md)
   and run [scripts/rest_read.py](scripts/rest_read.py). Reads only.
4. Otherwise stop and tell the user GitHub tooling is not set up. This skill
   pairs with `github-tooling-setup`. If it is not installed, install it from
   https://github.com/ryan-minato/skills.git:

       npx skills add ryan-minato/skills --skill github-tooling-setup

5. Use one path for the whole task. Never mix MCP, gh, and REST in one
   operation.

## Identify the repository

Run `git remote get-url origin`. Take the part after `github.com/` or
`github.com:`, strip a trailing `.git`, and split on `/` to get `OWNER` and
`REPO`. If there is no `origin` remote, ask the user for them. Substitute
wherever the tables show `O/R` (gh: `-R O/R`; MCP: the `owner` and `repo`
parameters).

Research often targets a repository other than the current checkout: when
the user names one, that name is `O/R` and the git remote is only the
default.

## Issues (read-only)

| Task | MCP tool | gh |
|---|---|---|
| Read issue + comments | `issue_read` method=`get`, then method=`get_comments` | `gh issue view N -R O/R --comments` |
| List issues | `list_issues` (state open/closed) | `gh issue list -R O/R --state open --json number,title,labels,updatedAt` |
| Search issues | `search_issues` (query `repo:O/R is:open TEXT`) | `gh issue list -R O/R --search "TEXT label:bug"` |

## Pull requests (read-only)

| Task | MCP tool | gh |
|---|---|---|
| Read PR | `pull_request_read` method=`get` | `gh pr view N -R O/R --json number,title,state,isDraft,reviewDecision,url` |
| Read diff | `pull_request_read` method=`get_diff` | `gh pr diff N -R O/R` |
| Check results | `pull_request_read` method=`get_status` or `get_check_runs` | `gh pr checks N -R O/R` |
| Reviews + review comments | `pull_request_read` method=`get_reviews` / `get_review_comments` | `gh api repos/O/R/pulls/N/reviews` and `gh api repos/O/R/pulls/N/comments` |
| List PRs | `list_pull_requests` | `gh pr list -R O/R --state open --json number,title,headRefName,updatedAt` |
| Search PRs | `search_pull_requests` (query `repo:O/R TEXT`) | `gh pr list -R O/R --search "TEXT"` |

Reading reviews and threads is research; replying to them is publishing
and belongs to `github-pull-requests`.

## Discussions

| Task | MCP tool | gh |
|---|---|---|
| List discussions | `list_discussions` (`orderBy: UPDATED_AT`, `direction: DESC` — direction is required whenever orderBy is given) | see [references/discussions-gh.md](references/discussions-gh.md) |
| Read one discussion | `get_discussion` (`discussionNumber`) | see references/discussions-gh.md |
| Read its comments | `get_discussion_comments` | see references/discussions-gh.md |
| List categories | `list_discussion_categories` | see references/discussions-gh.md |

gh has no first-class discussions command (the gh team declined to add
one). On the gh path, read
[references/discussions-gh.md](references/discussions-gh.md) whenever the
task involves Discussions — it contains complete copy-paste GraphQL
queries for every row above, plus pagination and search.

## Actions

| Task | MCP tool | gh |
|---|---|---|
| List workflow runs | `actions_list` method=`list_workflow_runs` | `gh run list -R O/R --limit 20 --json databaseId,displayTitle,workflowName,headBranch,status,conclusion,createdAt` |
| Inspect one run | `actions_get` method=`get_workflow_run` | `gh run view RUN_ID -R O/R` |
| List a run's jobs | `actions_list` method=`list_workflow_jobs` | `gh run view RUN_ID -R O/R --json jobs` |
| Failed-log excerpt | `get_job_logs` (`run_id: RUN_ID`, `failed_only: true`, `tail_lines: 100`, `return_content: true`) | [scripts/run_log_digest.py](scripts/run_log_digest.py): `python3 scripts/run_log_digest.py --repo O/R --run-id RUN_ID [--tail 50]` |

NEVER run bare `gh run view --log` or fetch full logs: run logs can be
megabytes and will flood the context. Always request failed-only output
with a tail limit — on the gh path the digest script enforces exactly
that, printing one JSON object with the run's status, its failed jobs,
each job's failed steps, and the last lines of each failed job's log.

Done when (for a "why did it fail" task): the failing job and step are
named and the relevant error lines are quoted.

Read [references/actions-recipes.md](references/actions-recipes.md) when
the task needs artifacts, run timing/usage, or filtered run listings
beyond the table above.

## Gotchas

- MCP tool names have changed across github-mcp-server versions. If a tool
  named in a table is absent, list the github server's available tools and
  pick the same-purpose name; if none matches, fall back to the gh column.
- The `discussions` and `actions` toolsets are not in the GitHub MCP
  server's default set. If those tools are missing while other github
  tools exist, the toolset must be enabled — local server: the
  `GITHUB_TOOLSETS` environment variable; remote server: the per-toolset
  URL such as `https://api.githubcopilot.com/mcp/x/discussions`.
  Configuring that belongs to `github-tooling-setup`.
- The REST tier can only read. Unauthenticated clients get 60 requests
  per hour per IP (search: 10 per minute); the script reports exhaustion
  with the reset time — stop and tell the user rather than retrying. A
  token in `GH_TOKEN`/`GITHUB_TOKEN` raises the limit to 5,000/hour.
- Tokenless Discussions are best-effort: the list comes from the public
  Atom feed (latest ~25, no category filter) and a single discussion is
  text extracted from the HTML page, which can break if GitHub changes
  its markup. A token upgrades both to full-fidelity GraphQL.
- On the REST tier, Actions **log text** requires a token even for public
  repositories (GitHub answers 403 "Must have admin rights"); without one,
  `run-failures` still names the failed jobs and steps from the jobs API.
- `gh run list` shows GitHub Actions workflow runs only; check runs
  reported by external CI apps do not appear there.
- Discussion numbers are per-repository and not shared with issue/PR
  numbers: `discussionNumber` 42 and issue #42 are unrelated items.
