---
name: gitlab-repo-research
description: >
  Read-only research over any GitLab project on gitlab.com or a
  self-managed host, including projects you cannot write to: reads
  issues, merge requests, pipelines, jobs and failed-job logs, releases,
  tags, and project search through one recommended path — glab commands,
  the GitLab Duo MCP server's tools, or a bundled REST script that works
  unauthenticated on public projects and with a token on private ones.
  Use when investigating a GitLab project — "what issues are open on
  that project", "read the comments on that MR", "summarize issue #N of
  group/project", "what did the reviewers say", "show recent pipelines",
  "why did the nightly pipeline fail", "get the logs from that job", or
  "what changed in the latest release of group/project".
license: Apache-2.0
compatibility: >
  scripts/rest_read.py requires Python 3.9+ (stdlib only) and outbound
  HTTPS to the GitLab host; scripts/pipeline_log_digest.py requires
  Python 3.9+ (stdlib only) and an authenticated glab CLI.
---

# GitLab Repo Research

Read-only investigation of any GitLab project: issues, merge requests,
pipelines and their logs, releases and tags, and search — including
projects you have no write access to. Nothing here publishes, so no
review gate applies; the moment the task turns into posting or changing
anything, switch to the skill that owns the write — `gitlab-issues`,
`gitlab-merge-requests`, `gitlab-releases`, or `gitlab-planning`/
`gitlab-wiki` (whose reads live there too): the skill that owns a write
also owns the reads that immediately precede it.

## Choose your path (do this first, once per session)

1. Run `glab auth status`. If it exits 0 and lists the target host, use the
   **glab** column of every table below. For a self-managed host, check that
   host specifically: `glab auth status --hostname HOST`.
2. Otherwise, look at the tools available in this session. If a connected
   MCP server provides GitLab tools for the work this skill covers (each
   tool's description states its purpose; names vary across server
   versions), use the **MCP** column, picking the tool whose description
   matches the row's capability — but only for rows that name one. Rows
   marked `—` have no MCP tool, and an older self-managed instance may
   lack a capability entirely: for those tasks, tell the user glab is
   required.
3. Otherwise, if the target project is public, or a token is set in
   `GITLAB_TOKEN`/`GITLAB_ACCESS_TOKEN` even though glab is missing, use the
   REST fallback: read [references/rest-fallback.md](references/rest-fallback.md)
   and run [scripts/rest_read.py](scripts/rest_read.py) with `--host HOST`.
   Reads only.
4. Otherwise stop and tell the user GitLab tooling is not set up. This skill
   pairs with `gitlab-tooling-setup`. If it is not installed, install it from
   https://github.com/ryan-minato/skills.git:

       npx skills add ryan-minato/skills --skill gitlab-tooling-setup

5. Use one path for the whole task. Never mix glab, MCP, and REST in one
   operation.

## Identify the host and project

Run `git remote get-url origin`. The host is the part right after
`https://` or the `@` (GitLab is often self-managed — never assume
`gitlab.com`). The project path is everything after the host, with any
trailing `.git` stripped; GitLab paths can nest (`group/subgroup/project`
is one project — keep the full path). If there is no origin remote, or the
user named a different project, use that instead — research often targets
a project other than the current checkout, on any host. Substitute the
full path wherever the tables show `G/P` (glab: `-R G/P`; MCP: the
project identifier parameter). Inside the project's checkout, glab
resolves the host from the remote on its own; outside it, pass
`--hostname HOST` to `glab api`/`glab auth` and set `GITLAB_HOST=HOST`
for other command groups.

## Issues (read-only)

| Task | glab command | MCP capability (min GitLab) |
|---|---|---|
| Read issue + comments | `glab issue view N -R G/P --comments` | read an issue (18.4), then its comments (18.7) |
| List / filter issues | `glab issue list -R G/P [--closed] [-l bug] [--search "TEXT"]` | — |

## Merge requests (read-only)

| Task | glab command | MCP capability (min GitLab) |
|---|---|---|
| Read MR | `glab mr view N -R G/P` (`-F json` for fields) | read MR details (18.4) |
| Read threads | `glab mr view N -R G/P --comments` (`--unresolved` filters) | read MR comments and threads (19.2) |
| Read diff | `glab mr diff N -R G/P` | read MR diffs (18.4) |
| Read commits | `glab api "projects/:fullpath/merge_requests/N/commits"` | read MR commits (18.4) |
| Who approved | `glab mr approvers N -R G/P` | — |
| List / filter MRs | `glab mr list -R G/P [--merged] [--search "TEXT"]` | — |

Reading threads is research; replying or resolving is publishing and
belongs to `gitlab-merge-requests`.

## Pipelines and jobs

Never fetch a full job trace unbounded — logs run to megabytes and flood
the context. The digest script and the tail procedure exist for exactly
this.

| Task | glab command | MCP capability (min GitLab) |
|---|---|---|
| List pipelines | `glab ci list -R G/P -F json [-s failed]` | list pipelines (18.10) |
| Inspect one pipeline + jobs | `glab ci get -R G/P -p ID -d -F json` | read a pipeline's jobs (18.4) |
| Failed-log digest | `python3 scripts/pipeline_log_digest.py --repo G/P --pipeline-id ID [--tail 50] [--hostname HOST]` | read a job log (19.1) — no tail parameter; prefer the digest |

[scripts/pipeline_log_digest.py](scripts/pipeline_log_digest.py) prints
one JSON object: pipeline status plus, per failed job, its stage,
failure reason, and the ANSI-stripped last N trace lines.
Done when: each failed job's error lines are quoted, not the whole log.

Read [references/pipeline-recipes.md](references/pipeline-recipes.md)
when the user explicitly asks to retry, cancel, or run a pipeline, lint
CI config, or download artifacts (the only writes in this skill, all
user-initiated).

## Releases and tags (read-only)

| Task | glab command | MCP capability (min GitLab) |
|---|---|---|
| List releases | `glab release list -R G/P` | — |
| Read one release | `glab release view TAG -R G/P` (omit `TAG` for the latest) | — |
| List tags | `glab api "projects/:fullpath/repository/tags"` | — |

On the REST tier: `python3 scripts/rest_read.py releases --project G/P`
(`--tag TAG` or `--latest` for one), and `python3 scripts/rest_read.py
tags --project G/P`. Reading releases here is research; creating,
editing, or deleting one belongs to `gitlab-releases`.

## Search

GitLab has no Discussions forum; instance-, group-, and project-wide
search covers the discovery ground instead.

| Task | glab command | MCP capability (min GitLab) |
|---|---|---|
| Search in one project | `glab issue list -R G/P --search "TEXT"` / `glab mr list -R G/P --search "TEXT"` | instance/group/project search (18.4) |
| Search across the instance or a group | `glab api "search?scope=issues&search=TEXT"` | instance/group/project search (18.4) |

Read [references/search-recipes.md](references/search-recipes.md) when
the search needs other scopes (projects, milestones, commits, code),
group scoping, or the Duo semantic code search.

## Gotchas

- Unauthenticated REST on gitlab.com is rate-limited: on HTTP 429 the
  script reports the `Retry-After` value — stop and tell the user;
  never hammer retries. Self-managed limits are whatever the admin set.
- Job traces on private projects always need a token; even on public
  projects, trace access may require membership — the digest script
  reports per-job access errors as data.
- Nested project paths must be URL-encoded in REST endpoints
  (`group/sub/project` → `group%2Fsub%2Fproject`); the script does this,
  hand-built `glab api` calls must do it themselves (or use
  `:fullpath` inside a checkout).
- Issue and MR iids are per-project and independent — `#42` and `!42`
  are unrelated objects.
- `glab ci list` shows GitLab CI pipelines only; statuses posted by
  external CI systems live on commits, not here.
- An `upcoming_release` (future `released_at`) shows an "Upcoming"
  badge and is not yet the latest release — check the field before
  calling something "released".
