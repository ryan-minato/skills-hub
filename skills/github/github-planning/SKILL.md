---
name: github-planning
description: >
  Operates GitHub planning structures: milestone lifecycle (create, edit,
  close, delete, list — via the REST API, since gh has no milestone
  command), label lifecycle (create, rename, recolor, delete, clone), and
  Projects v2 through gh project — create and edit projects, link
  repositories, add issues and PRs as items, set Status and other fields —
  with the required project token scope handled up front and a bundled ID
  resolver for item edits. Use when managing planning structures — "create
  a milestone", "close the milestone", "rename this label", "create a
  project board", "add this issue to the project", "move it to In
  Progress", "set the iteration", "what's on the board", or "archive the
  project item". Assigning a milestone or labels to one issue or PR belongs
  to github-issues / github-pull-requests.
license: Apache-2.0
compatibility: >
  scripts/project_fields.py requires Python 3.9+ (stdlib only) and an
  authenticated gh CLI with the project token scope.
---

# GitHub Planning

Manage the structures work is planned with: milestones, labels, and
Projects v2 (projects, items, fields). This skill owns the lifecycle of
those structures and all project-item operations; putting one issue or PR
*into* a milestone or label belongs to `github-issues` /
`github-pull-requests`, cutting releases to `github-releases`, and
designing a label taxonomy to `github-issue-conventions`.

## Choose your path (do this first, once per session)

1. Look at the tools available in this session. If a connected MCP server
   provides GitHub tools for the work this skill covers (each tool's
   description states its purpose; names vary across server versions), use
   the **MCP** column of every table below, picking the tool whose
   description matches the row's capability.
   The MCP column applies only to rows that name a capability; rows marked
   `—` have no MCP tool — those rows use the gh column instead: check
   `gh auth status` before running one, and if gh is not authenticated,
   stop and tell the user that row needs gh.
2. Otherwise run `gh auth status`. If it exits 0, use the **gh** column.
3. Otherwise stop and tell the user GitHub tooling is not set up. This skill
   pairs with `github-tooling-setup`. If it is not installed, install it from
   https://github.com/ryan-minato/skills.git:

       npx skills add ryan-minato/skills --skill github-tooling-setup

4. Use one column per row — rows marked `—` are the one sanctioned switch
   to gh on the MCP path. Within a single operation, never mix MCP and gh.

## Identify the repository

Run `git remote get-url origin`. The owner/repo pair is the path right
after the host, with any trailing `.git` stripped. If there is no origin
remote, or the user named a different repository, use that instead.
Substitute the pair wherever the tables show `O/R` (gh: `-R O/R`; MCP: the
owner and repo parameters).

Projects v2 hang off an **owner** (a user or an organization), not a
repository. `OWNER` below is that account (`@me` for your own), and a
project is addressed as `OWNER` + project `NUMBER` from `gh project list`.

## Token scope check (before any Projects v2 operation)

`gh project` needs the `project` token scope. Run `gh auth status` and
look for `project` in the token scopes; if it is missing, run
`gh auth refresh -s project` and complete the browser prompt.
Done when: `gh auth status` lists the `project` scope. Milestone and label
operations need no extra scope — skip this section for them.

## Match the project's conventions (before any create)

Before creating anything, discover what the repository already defines and
use it — never invent parallel structure:

| Artifact | How to check |
|---|---|
| Existing milestones (all states) | `gh api "repos/O/R/milestones?state=all" -q '.[] | .title'` — never create a near-duplicate of a closed or open one |
| Existing labels and their colors | `gh label list -R O/R --json name,color,description`, or the MCP tool that lists repository labels |
| Existing projects and their fields | `gh project list --owner OWNER`, then `gh project field-list NUMBER --owner OWNER` — reuse the existing Status option names |

If a project-level convention skill or an AGENTS.md conventions section
covers this task, follow it over this skill's defaults.
Done when: each artifact was checked and the draft uses the repository's
existing structures (or the user approved new ones).

## Authoring defaults

Write all published text — titles, bodies, comments, notes — as
professional, concise prose. Default to English unless the user or the
project's own conventions call for another language. State facts and
requests directly; no filler, and no emojis unless the project's existing
content uses them. The project's templates and conventions win over these
defaults.

## Pre-publish gate (mandatory)

Everything you send becomes public the moment the call succeeds: title, body,
every comment, labels, commit messages, the full diff, attachment contents,
and the branch name. Milestone titles and descriptions, project names, and label names are visible to everyone who can see the repository. Before ANY call that creates or edits public content:

1. Prefer a clean-context subagent review when one is available and the
   surface is not trivial. Give it only the exact final text or files under
   review, with no extra intent or reassurance.
2. Otherwise review the exact final text yourself. For short text fully
   visible in context, inspect it directly. For attachments, screenshots,
   generated bodies, long notes, or content too large to inspect reliably
   inline, write the exact outgoing content to a scratch directory and
   review those files from disk.
3. Check every artifact for secrets or credentials, personal data, internal
   identifiers or URLs, accidental unrelated content, and wording a
   maintainer would regret publishing. Any finding means
   `SAFE TO PUBLISH: NO`.
4. Publish only after the verdict is exactly `SAFE TO PUBLISH: YES`. On
   `NO`, fix every finding and review the exact final content again. Never
   edit-and-publish without re-review.

Never publish unreviewed content. Only the user may skip this gate,
explicitly; record the skip in your summary.
Done when: a `SAFE TO PUBLISH: YES` verdict exists for the exact content
being sent.

The gate applies to creating or editing titles, descriptions, and names
(milestones, labels, projects, fields). Closing, deleting, reordering,
item moves, and reads carry no new text and skip it.

## Milestones

Milestones are addressed by their `number` (from the list row). Due dates
are ISO timestamps (`2026-08-01T00:00:00Z`).

| Task | MCP capability | gh command |
|---|---|---|
| List | — | `gh api "repos/O/R/milestones?state=all" -q '.[] | {number, title, state, due_on}'` |
| Create | — | `gh api -X POST repos/O/R/milestones -f title="T" [-f description="D"] [-f due_on="YYYY-MM-DDT00:00:00Z"]` |
| Edit | — | `gh api -X PATCH repos/O/R/milestones/NUMBER -f title="T"` (same fields as create) |
| Close / reopen | — | `gh api -X PATCH repos/O/R/milestones/NUMBER -f state=closed` (or `open`) |
| Delete | — | `gh api -X DELETE repos/O/R/milestones/NUMBER` — see the gotcha; confirm with the user first |

Read [references/milestone-recipes.md](references/milestone-recipes.md)
when resolving a milestone by title, listing with sorting, or bulk-moving
issues between milestones.

## Labels

| Task | MCP capability | gh command |
|---|---|---|
| List | list repository labels | `gh label list -R O/R --json name,color,description` |
| Create | create a label | `gh label create NAME -R O/R --color HEX --description "D"` |
| Rename / recolor / redescribe | update a label | `gh label edit NAME -R O/R [--name NEW] [--color HEX] [--description "D"]` |
| Delete | — | `gh label delete NAME -R O/R --yes` — labels are removed from every issue and PR carrying them; confirm with the user first |
| Copy a repo's labels into O/R | — | `gh label clone SOURCE_OWNER/SOURCE_REPO -R O/R` |

## Projects v2

All rows are gh-only (`—` throughout for MCP). `NUMBER` comes from
`gh project list --owner OWNER`.

| Task | gh command |
|---|---|
| List projects | `gh project list --owner OWNER` |
| View a project | `gh project view NUMBER --owner OWNER` |
| Create | `gh project create --owner OWNER --title "T"` |
| Edit title/description | `gh project edit NUMBER --owner OWNER --title "T"` |
| Close / delete | `gh project close NUMBER --owner OWNER` / `gh project delete NUMBER --owner OWNER` (delete: confirm with the user first) |
| Link to a repository | `gh project link NUMBER --owner OWNER --repo O/R` |
| Add an issue/PR as item | `gh project item-add NUMBER --owner OWNER --url URL` |
| List items | `gh project item-list NUMBER --owner OWNER --format json` |
| List fields (and Status options) | `gh project field-list NUMBER --owner OWNER --format json` |
| Create a field | `gh project field-create NUMBER --owner OWNER --name "N" --data-type SINGLE_SELECT --single-select-options "A,B"` (also `TEXT`, `NUMBER`, `DATE`) |
| Edit an item's field (move on the board) | resolve IDs with the script below, then `gh project item-edit --id ITEM_ID --project-id PROJECT_ID --field-id FIELD_ID --single-select-option-id OPTION_ID` (or `--text`/`--number`/`--date`/`--iteration-id`, or `--clear`) |
| Archive an item | `gh project item-archive NUMBER --owner OWNER --id ITEM_ID` |

`item-edit` takes GraphQL node IDs, not numbers. Resolve them in one call:

    python3 scripts/project_fields.py --owner OWNER --number N \
        --field "Status" --option "In Progress" --item-url ISSUE_URL

which prints `{project_id, field_id, option_id, item_id}` ready to paste
into `item-edit`. Setting the Status field is how an item moves between
board columns.
Done when: the edited item shows the new value in
`gh project item-list ... --format json`.

Read [references/projects-graphql.md](references/projects-graphql.md) when
the task has no `gh project` subcommand (draft-issue conversion, filtered
item queries, iteration ids).

## Gotchas

- gh has no `milestone` command group — the REST rows above are the only
  gh path; there is no MCP capability for milestones either.
- Deleting a milestone silently detaches every issue and PR assigned to
  it; closing preserves history. Prefer close; delete only on explicit
  user confirmation.
- Renaming a label updates it everywhere it is applied; deleting removes
  it from every issue/PR. Rename beats delete-and-recreate.
- The `project` scope error surfaces as "your token has not been granted
  the required scopes" — run the token scope check section, then retry.
- `--owner` takes a user login, an org name, or `@me`; forgetting it makes
  gh guess from the current repository, which often picks the wrong owner.
- One `item-edit` invocation updates exactly one field; loop for several
  fields.
- Iteration fields are set by `--iteration-id`, not by name — the ids are
  in the field-list JSON (`configuration.iterations`).
