---
name: github-issues
description: >
  Operates GitHub issues through one recommended path — the connected GitHub
  MCP server's issue tools when available, exact gh commands otherwise:
  create, comment, close and reopen, edit labels, assignees and milestone,
  read details and comments, list issues and labels — always discovering the
  repository's issue templates, labels, and milestones before creating
  anything, with a mandatory pre-publish review gate. Use when working with
  GitHub issues — "file an issue", "open an issue", "create an issue",
  "comment on issue #N", "close this issue", "reopen the issue", "what does
  issue #N say", "list open bugs", "label this issue", "assign this issue",
  or "add the issue to the milestone".
license: Apache-2.0
---

# GitHub Issues

Operate GitHub issues in any repository: create, comment, close or reopen,
edit labels, assignees, and milestone, read details and comments, list
issues and labels. This skill covers issue operations only: pull-request
work belongs to `github-pull-requests`; milestone, label, and project-board
lifecycle to `github-planning`; read-only research across a repository to
`github-repo-research`; authoring issue templates or a label taxonomy to
`github-issue-conventions`.

## Choose your path (do this first, once per session)

1. Look at the tools available in this session. If a connected MCP server
   provides GitHub tools for the work this skill covers (each tool's
   description states its purpose; names vary across server versions), use
   the **MCP** column of every table below, picking the tool whose
   description matches the row's capability.
2. Otherwise run `gh auth status`. If it exits 0, use the **gh** column.
3. Otherwise stop and tell the user GitHub tooling is not set up. This skill
   pairs with `github-tooling-setup`. If it is not installed, install it from
   https://github.com/ryan-minato/skills.git:

       npx skills add ryan-minato/skills --skill github-tooling-setup

4. Use one column for the whole task. Never mix MCP and gh in one operation.

## Identify the repository

Run `git remote get-url origin`. The owner/repo pair is the path right
after the host, with any trailing `.git` stripped. If there is no origin
remote, or the user named a different repository, use that instead.
Substitute the pair wherever the tables show `O/R` (gh: `-R O/R`; MCP: the
owner and repo parameters).

## Match the project's conventions (before any create)

Before creating anything, discover what the repository already defines and
use it — never invent parallel structure:

| Artifact | How to check |
|---|---|
| Issue templates and forms | List `.github/ISSUE_TEMPLATE/` (locally, or `gh api repos/O/R/contents/.github/ISSUE_TEMPLATE`); a bare `.github/ISSUE_TEMPLATE.md` also counts. If any exist, read [references/use-issue-forms.md](references/use-issue-forms.md) and draft the body against the matching template |
| Labels | `gh label list -R O/R`, or the MCP tool that lists repository labels — apply only labels that already exist |
| Open milestones | `gh api repos/O/R/milestones -q '.[].title'` — assign only existing milestones |

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
and the branch name. Before ANY call that creates or edits public content:

1. Write the exact outgoing content to files in a scratch directory (title,
   body, each comment; for PRs also `git log BASE..HEAD --format=full >
   commits.txt` and `git diff BASE...HEAD > diff.patch`; copy attachments in).
2. Run the review procedure in references/publish-review.md over that
   directory. Read that file every time — do not review from memory.
3. Publish only after the verdict is exactly `SAFE TO PUBLISH: YES`. On `NO`,
   fix every finding, rebuild the files, review again. Never edit-and-publish
   without re-review.

Never publish unreviewed content. Only the user may skip this gate,
explicitly; record the skip in your summary.
Done when: a `SAFE TO PUBLISH: YES` verdict exists for the exact content
being sent.

The gate applies to create, comment, and any edit that changes public text
or metadata (title, body, labels, assignees, milestone). Pure reads and
lists carry no new content and skip it.

## Operations

Use the column chosen above. Send multi-line bodies through a file, never
an inline shell string: write the body to a file first, then pass that file
with `--body-file FILE` (gh) or fill the MCP body parameter from the file.

| Task | MCP capability | gh command |
|---|---|---|
| Create issue | create an issue (title, body, labels, assignees) | `gh issue create -R O/R --title "TITLE" --body-file BODY.md [--label L] [--assignee U] [--milestone "M"]` |
| Comment | comment on an issue | `gh issue comment N -R O/R --body-file COMMENT.md` |
| Close | update an issue to closed, with a state reason | `gh issue close N -R O/R --reason completed` (or `--reason "not planned"`) |
| Reopen | update an issue to open | `gh issue reopen N -R O/R` |
| Read issue + comments | read an issue, then its comments | `gh issue view N -R O/R --comments` |
| Read labels on an issue | read an issue's labels | `gh issue view N -R O/R --json labels` |
| List issues | list issues (state open/closed) | `gh issue list -R O/R --state open --json number,title,labels,updatedAt` |
| List available labels | list repository labels | `gh label list -R O/R --json name,description,color` |
| Edit labels/assignees/title | update an issue's metadata | `gh issue edit N -R O/R --add-label L --remove-label M --add-assignee U --title "T"` |
| Set / clear milestone | update an issue's milestone | `gh issue edit N -R O/R --milestone "TITLE"` / `--remove-milestone` |

After any create or comment, the response contains the new item's URL;
always report that URL to the user.
Done when: the URL is reported.

Read [references/issue-recipes.md](references/issue-recipes.md) when the
task is not a row in the table above (pin/lock/transfer, sub-issues,
search).

## Gotchas

- If no available MCP tool's description matches a row's capability, that
  capability is missing from the connected server — use the gh column for
  that row instead of guessing.
- The close reason is `completed` or `not planned`: gh takes it quoted,
  with the space (`--reason "not planned"`); the MCP update takes its
  state-reason value in underscore form (`not_planned`).
- A "not found" error for an issue number can mean the number belongs to a
  pull request — issues and PRs share one number space in a repository.
- Labels and milestones passed at create time must already exist in the
  repository; otherwise the call fails. The conventions section above
  exists so this never surprises you.
- gh `--json` field names are camelCase (`updatedAt`, not `updated_at`).
- `gh issue create` ignores issue templates in non-interactive mode — the
  template must be applied by drafting the body against it (see
  [references/use-issue-forms.md](references/use-issue-forms.md)).
