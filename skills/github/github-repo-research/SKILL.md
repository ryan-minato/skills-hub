---
name: github-repo-research
description: >
  Read-only research over any GitHub repository, including ones you cannot write to —
  issues, PRs, CI runs and logs, Discussions, releases, and tags. Use when
  investigating a repository — "what issues are open on that repo", "summarize issue
  #N of owner/repo", "what was decided in that discussion"; when asking whether a bug
  was already reported or fixed upstream; when evaluating a dependency or third-party
  project before adopting or upgrading it; when diagnosing a CI failure from run
  history or failed-job logs ("why did the nightly build fail"); when checking what
  changed in a release of a repository you only observe; or when a GitHub URL is
  pasted to read or summarize. Any write — commenting, filing, merging, releasing —
  belongs to github-issues, github-pull-requests, or github-releases, which also own
  the reads immediately preceding it; GitLab projects to gitlab-repo-research.
license: Apache-2.0
compatibility: >
  scripts/run_log_digest.py requires Python 3.9+ (stdlib only) and an
  authenticated gh CLI; scripts/rest_read.py requires Python 3.9+ (stdlib
  only) and outbound HTTPS to api.github.com and github.com.
---

# GitHub Repo Research

This skill is read-only: it never posts, edits, or changes anything, so it
has no publish gate — which is also why it works on repositories you have
no write access to. If the task turns into a write — commenting, filing an
issue, reviewing or fixing CI via a PR, cutting or editing a release —
switch to `github-issues`, `github-pull-requests`, or `github-releases`:
the skill that owns a write also owns the reads that immediately precede
it.

## Choose your path (do this first, once per session)

1. Look at the tools available in this session. If a connected MCP server
   provides GitHub tools for the work this skill covers (each tool's
   description states its purpose; names vary across server versions), use
   the **MCP** column of every table below, picking the tool whose
   description matches the row's capability.
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

Run `git remote get-url origin`. The owner/repo pair is the path right
after the host, with any trailing `.git` stripped. If there is no origin
remote, or the user named a different repository, use that instead.
Substitute the pair wherever the tables show `O/R` (gh: `-R O/R`; MCP: the
owner and repo parameters).

Research often targets a repository other than the current checkout: when
the user names one, that name is `O/R` and the git remote is only the
default.

## Issues (read-only)

| Task | MCP capability | gh |
|---|---|---|
| Read issue + comments | read an issue, then its comments | `gh issue view N -R O/R --comments` |
| List issues | list issues (state open/closed) | `gh issue list -R O/R --state open --json number,title,labels,updatedAt` |
| Search issues | search issues (query `repo:O/R is:open TEXT`) | `gh issue list -R O/R --search "TEXT label:bug"` |

## Pull requests (read-only)

| Task | MCP capability | gh |
|---|---|---|
| Read PR | read PR details | `gh pr view N -R O/R --json number,title,state,isDraft,reviewDecision,url` |
| Read diff | read a PR's diff | `gh pr diff N -R O/R` |
| Check results | read a PR's status rollup or check runs | `gh pr checks N -R O/R` |
| Reviews + review comments | read a PR's reviews / review comments | `gh api repos/O/R/pulls/N/reviews` and `gh api repos/O/R/pulls/N/comments` |
| List PRs | list pull requests | `gh pr list -R O/R --state open --json number,title,headRefName,updatedAt` |
| Search PRs | search pull requests (query `repo:O/R TEXT`) | `gh pr list -R O/R --search "TEXT"` |

Reading reviews and threads is research; replying to them is publishing
and belongs to `github-pull-requests`.

## Discussions

| Task | MCP capability | gh |
|---|---|---|
| List discussions | list discussions (when ordering, the direction parameter is required too) | see [references/discussions-gh.md](references/discussions-gh.md) |
| Read one discussion | read a discussion by number | see references/discussions-gh.md |
| Read its comments | read a discussion's comments | see references/discussions-gh.md |
| List categories | list discussion categories | see references/discussions-gh.md |

gh has no first-class discussions command (the gh team declined to add
one). On the gh path, read
[references/discussions-gh.md](references/discussions-gh.md) whenever the
task involves Discussions — it contains complete copy-paste GraphQL
queries for every row above, plus pagination and search.

## Actions

| Task | MCP capability | gh |
|---|---|---|
| List workflow runs | list workflow runs | `gh run list -R O/R --limit 20 --json databaseId,displayTitle,workflowName,headBranch,status,conclusion,createdAt` |
| Inspect one run | read one workflow run | `gh run view RUN_ID -R O/R` |
| List a run's jobs | list a run's jobs | `gh run view RUN_ID -R O/R --json jobs` |
| Failed-log excerpt | read job logs, failed-only, with a tail limit (about 100 lines) | [scripts/run_log_digest.py](scripts/run_log_digest.py): `python3 scripts/run_log_digest.py --repo O/R --run-id RUN_ID [--tail 50]` |

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

## Releases and tags (read-only)

| Task | MCP capability | gh |
|---|---|---|
| List releases | list releases | `gh release list -R O/R --limit 20` |
| Read one release | read a release by tag, or the latest release | `gh release view TAG -R O/R` (omit `TAG` for the latest) |
| List tags | list a repository's tags | `gh api repos/O/R/tags --jq '.[].name'` |

On the REST tier: `python3 scripts/rest_read.py releases --repo O/R`
(`--tag TAG` or `--latest` for one), and `python3 scripts/rest_read.py
tags --repo O/R`. Reading releases here is research; creating, editing, or
publishing one belongs to `github-releases`.

## Gotchas

- If no available MCP tool's description matches a row's capability, that
  capability is missing from the connected server — use the gh column for
  that row instead of guessing.
- The GitHub MCP server groups tools into optional toolsets, and the
  Discussions and Actions groups are not in its default set. If those
  capabilities are missing while other GitHub tools exist, the toolset
  must be enabled on the server side — configuring that belongs to
  `github-tooling-setup`.
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
  numbers: discussion 42 and issue #42 are unrelated items.
- Draft releases are invisible to anyone without push access — a release
  the user mentions but the tools cannot see is usually still a draft.
