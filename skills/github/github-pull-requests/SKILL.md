---
name: github-pull-requests
description: >
  Operates GitHub pull requests through one recommended path — GitHub MCP
  tools when the server is connected, exact gh commands otherwise: create,
  comment, close/reopen, draft/ready, merge, read PR state and diff, read
  CI check results and failed-job logs, and read or reply to review
  threads including Copilot code review, with a mandatory pre-publish
  review gate. Use when operating on a pull request — "open/create a PR",
  "comment on the PR", "did the checks pass", "why is CI red on my PR",
  "what did Copilot's review say", "reply to the review comments",
  "merge PR #N", or "mark the PR ready".
license: Apache-2.0
---

# GitHub Pull Requests

This skill operates pull requests: create, comment, read state and diff,
read check results, manage draft state, merge, and work with review
threads. For issue work use `github-issues`; for read-only research
across a repository (issues, PRs, Actions, Discussions — including repos
without write access) use `github-repo-research`; for authoring PR
templates and automation use `github-pr-conventions`; if GitHub tooling
is missing entirely, set it up with `github-tooling-setup`.

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
and the branch name. Creating a PR publishes every commit message and the
complete diff of `BASE...HEAD`, not just the description. Before ANY call
that creates or edits public content:

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

In this skill the gate applies to: create, comment, review submission, and
any edit that changes public text.

## Operations

| Task | MCP tool | gh command |
|---|---|---|
| Create PR | `create_pull_request` (base, head, title, body; optional draft, reviewers) | `gh pr create -R O/R --base BASE --head BRANCH --title "TITLE" --body-file BODY.md [--draft]` |
| Comment | `add_issue_comment` (PRs share issue numbering) | `gh pr comment N -R O/R --body-file COMMENT.md` |
| Read PR | `pull_request_read` method=`get` | `gh pr view N -R O/R --json number,title,state,isDraft,mergeable,reviewDecision,url` |
| Read diff | `pull_request_read` method=`get_diff` | `gh pr diff N -R O/R` |
| Check results | `pull_request_read` method=`get_status` (rollup) or `get_check_runs` | `gh pr checks N -R O/R` |
| Close / reopen | `update_pull_request` state=`closed`/`open` | `gh pr close N -R O/R` / `gh pr reopen N -R O/R` |
| Draft → ready | `update_pull_request` draft=false | `gh pr ready N -R O/R` |
| Merge | `merge_pull_request` (merge_method `squash`) | `gh pr merge N -R O/R --squash` |

The default merge method is squash, because linear history is the safer
default — deviate only when the project's convention says otherwise.
After create and comment operations, report the returned URL to the user.

- Read [references/checks-and-logs.md](references/checks-and-logs.md)
  when a check is failing and you need the logs.
- Read [references/reviews-and-copilot.md](references/reviews-and-copilot.md)
  when reading or replying to review threads, submitting a review, or
  requesting a Copilot code review.
- Read [references/pr-recipes.md](references/pr-recipes.md) when the task
  is not in the table above (update branch, reviewers, linked issues,
  revert).

## Gotchas

- MCP tool names have changed across github-mcp-server versions. If a tool
  named in a table is absent, list the github server's available tools and
  pick the same-purpose name; if none matches, fall back to the gh column.
- `gh pr checks` exits with code 8 while checks are still pending — that is
  not an error; wait and re-run, or use `--watch`.
- PRs and issues share one number space: that is why `add_issue_comment`
  comments on a PR, and why a bare `#N` can refer to either.
- A PR created from a fork needs `--head FORK_OWNER:BRANCH` (MCP: the same
  `owner:branch` form in the `head` parameter).
- Never dump a full CI log into context — full run logs can be megabytes.
  Follow the failed-only + tail rule in references/checks-and-logs.md.
