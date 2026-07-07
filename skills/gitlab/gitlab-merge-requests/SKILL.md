---
name: gitlab-merge-requests
description: >
  Operates GitLab merge requests through one recommended path — exact
  glab commands, with GitLab Duo MCP tools as the annotated alternative
  where they exist: create, comment, close/reopen, draft/ready, approve,
  merge with squash and auto-merge handling, read MR state and diff,
  read pipeline status and failed-job logs, and read, reply to, and
  resolve discussion threads — on gitlab.com or any self-managed host,
  with a mandatory pre-publish review gate. Use when operating on a
  merge request — "open/create an MR", "create a merge request",
  "comment on the MR", "did the pipeline pass", "why is the pipeline red
  on my MR", "approve MR !N", "reply to the review comments", "merge MR
  !N", "resolve the discussion", or "mark the MR ready".
license: Apache-2.0
---

# GitLab Merge Requests

Operate merge requests in any project: create, comment, close or reopen,
switch draft/ready, approve, merge, read state, diffs, pipeline results,
and discussion threads. This skill covers MR operations only: issue work
belongs to `gitlab-issues`, read-only research across a project to
`gitlab-repo-research`, MR templates and contributing rules to
`gitlab-mr-conventions`, and setting up missing GitLab tooling to
`gitlab-tooling-setup`.

## Choose your path (do this first, once per session)

1. Run `glab auth status`. If it exits 0 and lists the target host, use the
   **glab** column of every table below. For a self-managed host, check that
   host specifically: `glab auth status --hostname HOST`.
2. Otherwise, look at the tools available in this session. If any tool name
   contains `create_issue`, `get_merge_request`, or a `gitlab` MCP server
   prefix (for example `mcp__gitlab__...`), the GitLab MCP server is
   connected: use the **MCP** column — but only for rows that show an MCP
   tool. Rows marked `—` have no MCP tool, and a self-managed instance older
   than a tool's minimum version lacks that tool: for those tasks, tell the
   user glab is required.
3. Otherwise stop and tell the user GitLab tooling is not set up. This skill
   pairs with `gitlab-tooling-setup`. If it is not installed, install it from
   https://github.com/ryan-minato/skills.git:

       npx skills add ryan-minato/skills --skill gitlab-tooling-setup

4. Use one column for the whole task. Never mix glab and MCP in one
   operation.

## Identify the host and project

Run `git remote get-url origin`. The host is the part right after
`https://` or the `@` (GitLab is often self-managed — never assume
`gitlab.com`). The project path is everything after the host, with any
trailing `.git` stripped; GitLab paths can nest (`group/subgroup/project`
is one project — keep the full path). If there is no origin remote, or the
user named a different project, use that instead. Substitute the full path
wherever the tables show `G/P` (glab: `-R G/P`; MCP: the project `id`
parameter). Inside the project's checkout, glab resolves the host from the
remote on its own; outside it, pass `--hostname HOST` to `glab api`/`glab
auth` and set `GITLAB_HOST=HOST` for other command groups.

## Pre-publish gate (mandatory)

Everything you send becomes visible the moment the call succeeds — to the
whole internet on public projects, and to every member just as instantly
on private or internal ones: title, body, every comment, labels, commit
messages, the full diff, attachment contents, and the branch name.
Creating an MR publishes every commit message and the complete diff of
`TARGET...SOURCE`, not just the description. A line starting with `/` in
any body or comment can execute as a GitLab quick action (for example
`/close`). Before ANY call that creates or edits such content:

1. Write the exact outgoing content to files in a scratch directory
   (title, body, each comment; for MRs also `git log TARGET..SOURCE
   --format=full > commits.txt` and `git diff TARGET...SOURCE >
   diff.patch`; copy attachments in).
2. Run the review procedure in references/publish-review.md over that
   directory. Read that file every time — do not review from memory.
3. Publish only after the verdict is exactly `SAFE TO PUBLISH: YES`. On
   `NO`, fix every finding, rebuild the files, review again. Never
   edit-and-publish without re-review.

Never publish unreviewed content. Only the user may skip this gate,
explicitly; record the skip in your summary.
Done when: a `SAFE TO PUBLISH: YES` verdict exists for the exact content
being sent.

## Operations

Use the column chosen above. Send multi-line text through a file, never an
inline shell string: `-d "$(cat BODY.md)"` / `-m "$(cat COMMENT.md)"`.
Never use `--fill` — it publishes generated content that never went
through the gate.

| Task | glab command | MCP tool (min GitLab) |
|---|---|---|
| Create MR | `glab mr create -R G/P -s BRANCH -b TARGET -t "TITLE" -d "$(cat BODY.md)" [--draft] -y` | `create_merge_request` (18.5) |
| Comment | `glab mr note N -R G/P -m "$(cat COMMENT.md)"` | `create_merge_request_note` (19.2) |
| Read MR | `glab mr view N -R G/P` (`-F json` for fields) | `get_merge_request` (18.4) |
| Read comments/threads | `glab mr view N -R G/P --comments` (`--unresolved` filters) | `get_merge_request_notes` (19.2) |
| Read diff | `glab mr diff N -R G/P` | `get_merge_request_diffs` (18.4) |
| Pipeline status | `glab ci get --merge-request N -R G/P` | `get_merge_request_pipelines` (18.4) |
| Close / reopen | `glab mr close N -R G/P` / `glab mr reopen N -R G/P` | — |
| Draft → ready | `glab mr update N -R G/P --ready` | — |
| Approve / revoke approval | `glab mr approve N -R G/P` / `glab mr revoke N -R G/P` | — |
| Merge | `glab mr merge N -R G/P --squash --yes` | — |

After any create or comment, report the returned URL to the user.
Done when: the URL is reported.

**Merge semantics.** `glab mr merge` has `--auto-merge` on by default:
with a running pipeline the command sets the MR to merge when checks pass
and returns immediately — report that as "set to auto-merge", not
"merged". Pass `--auto-merge=false` only when the user wants an immediate
merge regardless of pipeline state. `--squash` follows this catalog's
default of linear history; drop it when the project's convention says
otherwise.

Read [references/pipeline-logs.md](references/pipeline-logs.md) when a
pipeline on the MR is failing and you need to see why.
Read [references/discussions-and-approvals.md](references/discussions-and-approvals.md)
when replying to or resolving a discussion thread, commenting on a diff
line, or working with approval state.
Read [references/mr-recipes.md](references/mr-recipes.md) when the task
is not a row above (rebase, checkout, target-branch change, reviewers,
linked issues, squash/remove-source options, milestone).

## Gotchas

- Issues and merge requests have **separate iid number spaces**: `!42`
  and `#42` are different objects. A "not found" on an MR number may
  mean the number belongs to an issue.
- Draft state is a `Draft:` title prefix under the hood — manage it with
  `--draft` (create/update) and `--ready` (update), never by editing the
  title yourself.
- `glab ci trace` follows a *running* job's log indefinitely and will
  hang a non-interactive session — trace only finished jobs, or use the
  procedure in references/pipeline-logs.md.
- Never dump a full job trace into context; failed pipelines are read
  through the tail procedure in references/pipeline-logs.md.
- `glab mr note` subcommands (`create`, `resolve`, ...) are marked
  experimental and may change between glab versions; the bare
  `glab mr note N -m` comment form is stable. If a subcommand is missing,
  run `glab mr note --help` and use the `glab api` fallback in
  references/discussions-and-approvals.md.
- `glab mr view` and `glab mr list` both use `-F/--output json`, unlike
  `glab issue list` (`-O`) — check `--help` before assuming output flags.
- Approving requires approvals to be enabled on the project; *required*
  approval rules are Premium, but the approve/revoke buttons exist on
  Free. A 404 on approval endpoints usually means a tier gate, not a
  wrong path.
- Merging is blocked while the MR is draft, discussions are unresolved
  (when the project requires resolution), or a required pipeline is red
  — the error names the blocker; fix that instead of retrying.
