---
name: gitlab-issues
description: >
  Operates GitLab issues through one recommended path — exact glab
  commands, with the GitLab Duo MCP server's issue tools as the annotated
  alternative where the capability exists: create, comment, close and
  reopen, edit labels, assignees and milestone, read details and comments,
  list issues and labels — always discovering the project's description
  templates, labels, and milestones before creating anything, on
  gitlab.com or any self-managed host, with a mandatory pre-publish review
  gate. Use when working with GitLab issues — "file an issue", "open an
  issue", "create an issue", "comment on issue #N", "close this issue",
  "reopen the issue", "what does issue #N say", "list open bugs", "label
  this issue", "assign this issue", or "add the issue to the milestone".
license: Apache-2.0
---

# GitLab Issues

Operate GitLab issues in any project: create, comment, close or reopen,
edit labels, assignees, and milestone, read details and comments, list
issues and labels. This skill covers issue operations only: merge-request
work belongs to `gitlab-merge-requests`; milestone, iteration, board,
epic, and label lifecycle to `gitlab-planning`; read-only research across
a project to `gitlab-repo-research`; authoring issue templates or a label
taxonomy to `gitlab-issue-conventions`.

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
wherever the tables show `G/P` (glab: `-R G/P`; MCP: the project
identifier parameter). Inside the project's checkout, glab resolves the
host from the remote on its own; outside it, pass `--hostname HOST` to
`glab api`/`glab auth` and set `GITLAB_HOST=HOST` for other command
groups.

## Match the project's conventions (before any create)

Before creating anything, discover what the project already defines and
use it — never invent parallel structure:

| Artifact | How to check |
|---|---|
| Description templates | List `.gitlab/issue_templates/` (locally, or `glab api "projects/:fullpath/repository/tree?path=.gitlab/issue_templates"`); if one matches the report type, use its body as the scaffold and fill every section — templates may deliberately embed quick actions, keep them |
| Labels | `glab label list -R G/P` — apply only labels that already exist (an unknown `-l NAME` silently creates a label) |
| Open milestones | `glab milestone list -R G/P` — assign only existing milestones |

If a project-level convention skill or an AGENTS.md conventions section
covers this task, follow it over this skill's defaults.
Done when: each artifact was checked and the draft uses the project's
existing structures (or the user approved new ones).

## Authoring defaults

Write all published text — titles, bodies, comments, notes — as
professional, concise prose. Default to English unless the user or the
project's own conventions call for another language. State facts and
requests directly; no filler, and no emojis unless the project's existing
content uses them. The project's templates and conventions win over these
defaults.

## Pre-publish gate (mandatory)

Everything you send becomes visible the moment the call succeeds — to the
whole internet on public projects, and to every member just as instantly on
private or internal ones: title, body, every comment, labels, commit
messages, the full diff, attachment contents, and the branch name. A line
starting with `/` in any body or comment can execute as a GitLab quick
action (for example `/close`). Before ANY call that creates or edits such
content:

1. Prefer a clean-context subagent review when one is available and the
   surface is not trivial. Give it only the exact final text or files under
   review, with no extra intent or reassurance.
2. Otherwise review the exact final text yourself. For short text fully
   visible in context, inspect it directly. For attachments, screenshots,
   generated bodies, long notes, or content too large to inspect reliably
   inline, write the exact outgoing content to a scratch directory and
   review those files from disk.
3. Check every artifact for secrets or credentials, personal data, internal
   identifiers or URLs, unintended quick actions, accidental unrelated
   content, and wording a maintainer would regret publishing. Any finding
   means `SAFE TO PUBLISH: NO`.
4. Publish only after the verdict is exactly `SAFE TO PUBLISH: YES`. On
   `NO`, fix every finding and review the exact final content again. Never
   edit-and-publish without re-review.

Never publish unreviewed content. Only the user may skip this gate,
explicitly; record the skip in your summary.
Done when: a `SAFE TO PUBLISH: YES` verdict exists for the exact content
being sent.

The gate applies to create, comment, and any edit that changes public text
or metadata (title, description, labels, assignees, milestone). Pure reads
and lists carry no new content and skip it.

## Operations

Use the column chosen above. Send multi-line text through a file, never an
inline shell string: write the body to a file first, then pass it with
`-d "$(cat BODY.md)"` or `-m "$(cat COMMENT.md)"` (glab has no
`--body-file`; command substitution does not re-expand file contents).

| Task | glab command | MCP capability (min GitLab) |
|---|---|---|
| Create issue | `glab issue create -R G/P -t "TITLE" -d "$(cat BODY.md)" [-l LABEL] [-a USER] [-m "MILESTONE"] -y` | create an issue (18.4) |
| Comment | `glab issue note N -R G/P -m "$(cat COMMENT.md)"` | comment on an issue/work item (18.7) |
| Close | `glab issue close N -R G/P` | — |
| Reopen | `glab issue reopen N -R G/P` | — |
| Read issue + comments | `glab issue view N -R G/P --comments` | read an issue (18.4), then its comments (18.7) |
| List issues | `glab issue list -R G/P` (open by default; `--closed`, `--all`) | — |
| List available labels | `glab label list -R G/P -F json` | search labels (18.9) |
| Edit labels/assignees/title | `glab issue update N -R G/P [-l NEW] [-u OLD] [-a +USER] [-t "T"]` | — |
| Set / clear milestone | `glab issue update N -R G/P -m "TITLE"` (`-m ""` clears) | — |

After any create or comment, the response contains the new item's URL;
always report that URL to the user.
Done when: the URL is reported.

Read [references/issue-recipes.md](references/issue-recipes.md) when the
task is not a row in the table above (confidential issues, due date and
weight, iteration or epic assignment, lock discussion, linked issues, move
to another project, search and filters).

## Gotchas

- Issues and merge requests have **separate iid number spaces** in
  GitLab: `#42` and `!42` are different objects, and `glab issue`
  commands cannot touch an MR.
- A body or comment line starting with `/` executes as a quick action
  with your permissions (`/close`, `/label ~bug`, `/move`) — never let
  one through unintended (the review gate checks), but they are also the
  supported way to do things glab lacks flags for (see the recipes).
- glab prompts for confirmation on create — `-y` is mandatory in
  non-interactive sessions, and always pass `-d`: omitting it opens an
  editor and hangs the session.
- Output flags are inconsistent across commands: `glab issue list` uses
  `-O/--output text|json`, while `glab issue view` and `glab label list`
  use `-F/--output text|json`. Check `--help` before assuming.
- GitLab has no close *reason*; closing is unqualified. State filter
  values elsewhere are `opened`/`closed`, but `glab issue list` uses the
  `--closed`/`--all` flags instead.
- On `glab issue update`, `-a USER` **replaces** all assignees; prefix
  with `+` to add (`-a +USER`) or `!`/`-` to remove.
- Unknown label names never error, but the two mechanisms disagree:
  `-l NAME` via glab/API silently **creates** a new project label, while
  a `/label ~NAME` quick action silently **ignores** it. The conventions
  section above exists so neither surprises you.
