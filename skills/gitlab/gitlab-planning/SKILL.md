---
name: gitlab-planning
description: >
  Operates GitLab planning structures through the authenticated glab CLI
  and REST API, with each operation's tier floor marked: milestone
  lifecycle (create, edit, close, delete, list at project or group
  level), label lifecycle (create, rename, recolor, delete), iteration
  lookup, issue-board and board-list management, and epic lifecycle on
  Premium/Ultimate. Use when managing planning structures on gitlab.com
  or a self-managed instance — "create a milestone", "close the
  milestone", "set up the next release milestone", "list group
  milestones", "rename this label", "what iteration are we in", "create
  an issue board", "add a Doing column to the board", "reorder the board
  lists", "create an epic", "make this epic a child of that one", "close
  the epic", or "delete this board". Assigning a single issue to a
  milestone, iteration, or epic belongs to gitlab-issues.
license: Apache-2.0
---

# GitLab Planning

Manage the planning structures themselves: milestones, labels,
iterations, issue boards, and epics. Putting one issue into a milestone/
iteration/epic — or moving it between label-backed board lists, which is
relabeling — belongs to `gitlab-issues`; setting a milestone on an MR to
`gitlab-merge-requests`; attaching a milestone to a release to
`gitlab-releases`; read-only project research to `gitlab-repo-research`;
designing a label taxonomy to `gitlab-issue-conventions`. The GitLab Duo
MCP server has no tools for these structures — glab (with `glab api` for
gaps) is the only path, so the tables below have one column.

## Choose your path (do this first, once per session)

1. Run `glab auth status`. If it exits 0 and lists the target host, use
   glab as shown in every table below. For a self-managed host, check that
   host specifically: `glab auth status --hostname HOST`.
2. Otherwise stop and tell the user GitLab tooling is not set up. This skill
   pairs with `gitlab-tooling-setup`. If it is not installed, install it from
   https://github.com/ryan-minato/skills.git:

       npx skills add ryan-minato/skills --skill gitlab-tooling-setup

## Identify the host, project, and group

Run `git remote get-url origin`. The host is the part right after
`https://` or the `@` (GitLab is often self-managed — never assume
`gitlab.com`). The project path is everything after the host, with any
trailing `.git` stripped; GitLab paths can nest (`group/subgroup/project`
is one project — keep the full path). The group path is the project path
minus its last segment; group-level structures (group milestones,
iterations, epics, group boards, group labels) live there. If there is no
origin remote, or the user named a different project or group, use that
instead. Substitute the full path wherever the tables show `G/P` or
`GROUP` (URL-encode `/` as `%2F` inside `glab api` endpoint paths; inside
a checkout the `:fullpath` and `:group` placeholders do it for you).
Outside a checkout, pass `--hostname HOST` to `glab api` and
`GITLAB_HOST=HOST` for other command groups.

## Tiers and versions

Each section header below carries its tier floor. GitLab returns **404,
not 403, for features above the instance's tier or license** — on a 404
for a Premium row, report the tier requirement instead of retrying.
Probe the instance version with `glab api version` when a feature might
be too new for a self-managed host.

## Match the project's conventions (before any create)

Before creating anything, discover what the project already defines and
use it — never invent parallel structure:

| Artifact | How to check |
|---|---|
| Existing milestones (all states) | `glab milestone list -R G/P --state closed -F json` plus the active list — never create a near-duplicate |
| Existing labels, colors, scopes | `glab label list -R G/P -F json` — respect scoped-label prefixes (`type::`) and the palette in use |
| Existing boards and lists | `glab api projects/:fullpath/boards` — reuse list structure and naming |

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
action (for example `/close`). Milestone, board, list, epic, and label names and descriptions are visible to everyone who can see the project. Before ANY call that creates or edits such
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

The gate applies to milestone/epic/label create and edit and to board or
list create and rename; close, reopen, delete, reorder, and reads carry
no new text.

## Milestones (all tiers)

glab addresses milestones by numeric id — find it with the list row
first. `--group GROUP` switches any row to group level (`--project` and
`--group` are mutually exclusive).

| Task | Command |
|---|---|
| List | `glab milestone list -R G/P [--state active\|closed] -F json` |
| Find id by title | `glab milestone list -R G/P --title "TITLE" -F json` |
| View one | `glab milestone get ID -R G/P` |
| Create | `glab milestone create -R G/P --title "TITLE" [--description "$(cat DESC.md)"] [--start-date 2026-07-01] [--due-date 2026-09-30]` |
| Edit | `glab milestone edit ID -R G/P [--title "T"] [--due-date ...]` |
| Close / reactivate | `glab milestone edit ID -R G/P --state close` (or `--state activate`) |
| Delete | `glab milestone delete ID -R G/P` |

Edits are partial: only the fields you pass change; omitted fields keep
their values. Report the milestone's `web_url` from the JSON response.
Done when: the URL is reported.

## Labels (all tiers)

glab has `label list` and `label create` only; rename, recolor, and
delete go through the REST endpoints. `LABEL_ID` is the numeric `id` in
the list output. Group labels use `groups/GROUP/labels` endpoints and are
inherited by every project below the group — edit them at group level
only with the user's explicit confirmation.

| Task | Command |
|---|---|
| List (with ids) | `glab label list -R G/P -F json` |
| Create | `glab label create -R G/P --name "NAME" --color "#5843AD" --description "D"` |
| Rename / recolor / redescribe | `glab api --method PUT projects/:fullpath/labels/LABEL_ID [-f new_name="N"] [-f color="#HEX"] [-f description="D"]` |
| Delete | `glab api --method DELETE projects/:fullpath/labels/LABEL_ID` — removed from every issue and MR carrying it; confirm with the user first |

Renaming a label updates it everywhere it is applied — rename beats
delete-and-recreate. Scoped labels (`scope::value`) are plain labels with
`::` in the name; their mutual exclusion is enforced by GitLab on
assignment (enforcement is Premium, the naming works everywhere).

## Iterations (Premium; read-only)

List with `glab iteration list -R G/P -F json` (`-g GROUP` for the
group's; state filter via `glab api "groups/GROUP/iterations?state=current"`).
Iterations cannot be created or edited through REST or glab — cadences
manage them. Read
[references/iterations-and-cadences.md](references/iterations-and-cadences.md)
when asked to create, edit, or schedule an iteration or cadence.

## Issue boards (Free; scoping and non-label lists Premium)

Board and list management lives entirely in
[references/boards.md](references/boards.md) — read it for any board
task: the Free operations table (create/rename/delete boards, label
lists, reordering), Premium scoping and non-label lists, group boards,
and epic boards. Moving an issue between label-backed lists is
relabeling the issue — that belongs to `gitlab-issues`.

## Epics (Premium/Ultimate; group-level)

Epic lifecycle lives entirely in
[references/epics-work-items.md](references/epics-work-items.md) — read
it for any epic task: the deprecated-but-stable REST operations table
(list, view, create, edit, close, labels, parent/child, delete) and the
experimental work-items successor path for instances where the legacy
endpoints return 404 or the user asks for work items, tasks, objectives,
or key results.

## Gotchas

- Deleting a milestone silently detaches every issue, MR, and epic that
  referenced it — closing (`edit --state close`) is almost always what
  the user actually wants; confirm before deleting.
- Group-inherited labels cannot be edited through the project endpoints —
  a 404 on `projects/.../labels/ID` for a label you can see usually means
  it lives at group level.
- 404 ≠ wrong path: for iterations, epics, and board scoping it usually
  means the tier gate (Free instance) — say so instead of retrying.
- `glab milestone` and `glab work-items` are recent command groups; if a
  subcommand is missing, update glab (`glab check-update`) instead of
  hunting for alternate spellings.
