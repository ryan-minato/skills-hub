---
name: gitlab-planning
description: >
  Operates GitLab planning structures through the authenticated glab CLI
  and REST API, with each operation's tier floor marked: milestone
  lifecycle (create, edit, close, delete, list at project or group
  level), iteration lookup, issue-board and board-list management, and
  epic lifecycle on Premium/Ultimate. Use when managing planning
  structures on gitlab.com or a self-managed instance — "create a
  milestone", "close the milestone", "set up the next release
  milestone", "list group milestones", "what iteration are we in",
  "create an issue board", "add a Doing column to the board", "reorder
  the board lists", "create an epic", "make this epic a child of that
  one", "close the epic", or "delete this board". Assigning a single
  issue to a milestone, iteration, or epic belongs to gitlab-issues.
license: Apache-2.0
---

# GitLab Planning

Manage the planning structures themselves: milestones, iterations, issue
boards, and epics. Putting one issue into a milestone/iteration/epic
belongs to `gitlab-issues`; setting a milestone on an MR to
`gitlab-merge-requests`; read-only project research to
`gitlab-repo-research`; tooling setup to `gitlab-tooling-setup`. The
GitLab Duo MCP server has no tools for milestones, iterations, boards,
or epics — glab is the only path, so the tables below have one column.

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
iterations, epics, group boards) live there. If there is no origin
remote, or the user named a different project or group, use that instead.
Substitute the full path wherever the tables show `G/P` or `GROUP`
(URL-encode `/` as `%2F` inside `glab api` endpoint paths; inside a
checkout the `:fullpath` and `:group` placeholders do it for you).
Outside a checkout, pass `--hostname HOST` to `glab api` and
`GITLAB_HOST=HOST` for other command groups.

## Tiers and versions

Each section header below carries its tier floor. GitLab returns **404,
not 403, for features above the instance's tier or license** — on a 404
for a Premium row, report the tier requirement instead of retrying.
Probe the instance version with `glab api version` when a feature might
be too new for a self-managed host.

## Pre-publish gate (mandatory)

Everything you send becomes visible the moment the call succeeds — to the
whole internet on public projects, and to every member just as instantly
on private or internal ones: title, body, every comment, labels, commit
messages, the full diff, attachment contents, and the branch name.
Milestone, epic, and board titles and descriptions are visible to
everyone who can view the project or group. A line starting with `/` in
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

The gate applies to milestone/epic create and edit and to board or list
create and rename; close, reopen, delete, reorder, and reads carry no new
text.

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

Report the milestone's `web_url` from the JSON response.
Done when: the URL is reported.

## Iterations (Premium; read-only)

```bash
glab iteration list -R G/P -F json        # project's iterations
glab iteration list -g GROUP -F json      # group's iterations
glab api "groups/GROUP/iterations?state=current"   # state filter
```

Iterations cannot be created or edited through REST or glab — cadences
manage them. Read
[references/iterations-and-cadences.md](references/iterations-and-cadences.md)
when asked to create, edit, or schedule an iteration or cadence.

## Issue boards (Free; scoping and non-label lists Premium)

No glab command group exists for boards — every row is `glab api`.
Multiple boards per **project** are Free.

| Task | Command |
|---|---|
| List boards | `glab api projects/:fullpath/boards` |
| View a board's lists | `glab api projects/:fullpath/boards/BID/lists` |
| Create board | `glab api --method POST projects/:fullpath/boards -f name="NAME"` |
| Rename board | `glab api --method PUT projects/:fullpath/boards/BID -f name="NAME"` |
| Delete board | `glab api --method DELETE projects/:fullpath/boards/BID` |
| Add a label list | `glab api --method POST projects/:fullpath/boards/BID/lists -F label_id=LABEL_ID` |
| Reorder a list | `glab api --method PUT projects/:fullpath/boards/BID/lists/LID -F position=N` |
| Delete a list | `glab api --method DELETE projects/:fullpath/boards/BID/lists/LID` |

A label list takes the numeric `label_id` — look it up with
`glab api projects/:fullpath/labels`. Read
[references/boards-premium.md](references/boards-premium.md) when
scoping a board (milestone/assignee/weight/labels), creating an
assignee, milestone, or iteration list, creating or deleting a **group**
board, or reading epic boards.

## Epics (Premium/Ultimate; group-level)

The Epics REST API is deprecated since GitLab 17.0 (removal planned for
the unreleased API v5) but remains the stable, complete path on every
currently supported version; the successor work-items surface is still
experimental. Epic descriptions go through files (`-F description=@FILE`).

| Task | Command |
|---|---|
| List | `glab api "groups/GROUP/epics?state=opened"` |
| View | `glab api groups/GROUP/epics/IID` |
| Create | `glab api --method POST groups/GROUP/epics -f title="TITLE" -F description=@EPIC.md` |
| Edit | `glab api --method PUT groups/GROUP/epics/IID [-f title="T"] [-F description=@EPIC.md]` |
| Close / reopen | `glab api --method PUT groups/GROUP/epics/IID -f state_event=close` (or `reopen`) |
| Add / remove labels | `-f add_labels=a,b` / `-f remove_labels=c` on the PUT |
| Set parent epic | `glab api --method PUT groups/GROUP/epics/IID -F parent_id=EPIC_ID` |
| Delete | `glab api --method DELETE groups/GROUP/epics/IID` |

`parent_id` takes the parent's global epic `id`, not its `iid` (the view
row shows both). Read
[references/epics-work-items.md](references/epics-work-items.md) when
the epics endpoints return 404 on a licensed instance (a newer GitLab
with legacy epics removed) or when the user asks for work items, tasks,
objectives, or key results.

## Gotchas

- Deleting a milestone silently detaches every issue, MR, and epic that
  referenced it — closing (`edit --state close`) is almost always what
  the user actually wants; confirm before deleting.
- Only the fields you pass to `glab milestone edit` change; omitted
  fields keep their values.
- On a board update, the scope parameters (`labels`, `assignee_id`,
  `milestone_id`, `weight`) are mutually exclusive — one per request.
- 404 ≠ wrong path: for iterations, epics, and board scoping it usually
  means the tier gate (Free instance) — say so instead of retrying.
- Iterations auto-created by a cadence have `null` titles — identify
  them by date range.
- `glab milestone` and `glab work-items` are recent command groups; if a
  subcommand is missing, update glab (`glab check-update`) instead of
  hunting for alternate spellings.
