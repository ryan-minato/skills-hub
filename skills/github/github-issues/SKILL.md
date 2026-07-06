---
name: github-issues
description: >
  Operates GitHub issues through one recommended path — GitHub MCP tools
  when the server is connected, exact gh commands otherwise: create,
  comment, close and reopen, edit labels and assignees, read details and
  comments, list issues and labels — with a mandatory pre-publish review
  gate before anything is posted. Use when working with GitHub issues —
  "file an issue", "open an issue", "create an issue", "comment on issue
  #N", "close this issue", "reopen the issue", "what does issue #N say",
  "list open bugs", "label this issue", or "assign this issue".
license: Apache-2.0
---

# GitHub Issues

Operate GitHub issues in any repository: create, comment, close or reopen,
edit labels and assignees, read details and comments, list issues and
labels. This skill covers issue operations only: pull request work belongs
to `github-pull-requests`, read-only research across a repository
(issues, PRs, Actions, Discussions) to `github-repo-research`, authoring
issue templates or a label
taxonomy to `github-issue-conventions`, and setting up missing GitHub
tooling to `github-tooling-setup`.

## Choose your path (do this first, once per session)

1. Look at the tools available in this session. If any tool name contains
   `issue_read`, `pull_request_read`, or a `github` MCP server prefix (for
   example `mcp__github__...`), the GitHub MCP server is connected: use the
   **MCP** column of every table below.
2. Otherwise run `gh auth status`. If it exits 0, use the **gh** column.
3. Otherwise stop and tell the user GitHub tooling is not set up. This skill
   pairs with `github-tooling-setup`. If it is not installed, install it from
   https://github.com/ryan-minato/skills.git:

       npx skills add ryan-minato/skills --skill github-tooling-setup

4. Use one column for the whole task. Never mix MCP and gh in one operation.

## Identify the repository

Run `git remote get-url origin`. Take the part after `github.com/` or
`github.com:`, strip a trailing `.git`, and split on `/` to get `OWNER` and
`REPO`. If there is no `origin` remote, ask the user for them. Substitute
wherever the tables show `O/R` (gh: `-R O/R`; MCP: the `owner` and `repo`
parameters).

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
or metadata (title, body, labels, assignees, milestone).

## Operations

Use the column chosen above. Send multi-line bodies through a file, never
an inline shell string: write the body to a file first, then pass that file
with `--body-file FILE` (gh) or put the file's contents into the `body`
parameter (MCP).

| Task | MCP tool | gh command |
|---|---|---|
| Create issue | `issue_write` method=`create` (title, body, labels, assignees) | `gh issue create -R O/R --title "TITLE" --body-file BODY.md [--label L] [--assignee U]` |
| Comment | `add_issue_comment` (issue_number, body) | `gh issue comment N -R O/R --body-file COMMENT.md` |
| Close | `issue_write` method=`update`, state=`closed` (state_reason `completed` / `not_planned`) | `gh issue close N -R O/R --reason completed` (or `--reason "not planned"`) |
| Reopen | `issue_write` method=`update`, state=`open` | `gh issue reopen N -R O/R` |
| Read issue + comments | `issue_read` method=`get`, then method=`get_comments` | `gh issue view N -R O/R --comments` |
| Read labels on an issue | `issue_read` method=`get_labels` | `gh issue view N -R O/R --json labels` |
| List issues | `list_issues` (state open/closed) | `gh issue list -R O/R --state open --json number,title,labels,updatedAt` |
| List available labels | `list_label` | `gh label list -R O/R --json name,description,color` |
| Edit labels/assignees/title | `issue_write` method=`update` | `gh issue edit N -R O/R --add-label L --remove-label M --add-assignee U --title "T"` |

After any create or comment, the response contains the new item's URL;
always report that URL to the user.
Done when: the URL is reported.

Read [references/issue-recipes.md](references/issue-recipes.md) when the
task is not a row in the table above (pin/lock/transfer, sub-issues,
milestones, search).

## Gotchas

- MCP tool names have changed across github-mcp-server versions. If a tool
  named in a table is absent, list the github server's available tools and
  pick the same-purpose name; if none matches, fall back to the gh column.
- The close reason is `completed` or `not planned`: gh takes it quoted,
  with the space (`--reason "not planned"`), while the MCP `state_reason`
  parameter uses the underscore form `not_planned`.
- A "not found" error for an issue number can mean the number belongs to a
  pull request — issues and PRs share one number space in a repository.
- Labels passed at create time must already exist in the repository;
  otherwise the create fails. List available labels first when unsure.
- gh `--json` field names are camelCase (`updatedAt`, not `updated_at`).
