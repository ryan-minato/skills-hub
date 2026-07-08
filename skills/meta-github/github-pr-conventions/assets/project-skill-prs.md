---
name: {{REPO_NAME}}-prs
description: >
  Opens and reviews pull requests in {{OWNER_REPO}} following this
  repository's conventions: base branch {{DEFAULT_BRANCH}},
  {{MERGE_METHOD}} merges, the required PR template sections, and the
  repository's label scheme. Use when working with pull requests in this
  repository — "open a PR", "create a pull request", "review PR #N",
  "check the PR checks", "is the PR green", or "submit a review".
---

# {{REPO_NAME}} pull requests

Open and review pull requests in `{{OWNER_REPO}}` following the
conventions below.

## Choose your path (do this first, once per session)

1. Look at the tools available in this session. If a connected MCP server
   provides GitHub pull-request tools (each tool's description states its
   purpose; names vary across server versions), use the **MCP** column of
   every table below, picking the tool whose description matches the
   row's capability.
2. Otherwise run `gh auth status`. If it exits 0, use the **gh** column.
3. Otherwise stop and tell the user GitHub tooling is not set up; the
   `github-tooling-setup` skill installs it, from
   https://github.com/ryan-minato/skills.git:

       npx skills add ryan-minato/skills --skill github-tooling-setup

4. Use one column for the whole task. Never mix MCP and gh in one
   operation.

## This repository's conventions

- Base branch: every PR targets `{{DEFAULT_BRANCH}}` unless the user says
  otherwise.
- Merge method: {{MERGE_METHOD}}.
- The PR body must contain every template section, each filled in:
  {{TEMPLATE_HEADINGS}}.
- Labels follow the prefixes {{LABEL_PREFIXES}}. Path-based labels are
  applied automatically by the labeler workflow; do not add those by hand.

## Pre-publish gate (mandatory)

Everything you send becomes public the moment the call succeeds — and
creating a PR publishes every commit message and the complete diff of
`{{DEFAULT_BRANCH}}...HEAD`, not just the description. Before any call
that creates or edits public content, review the exact final content: title,
body, comments or review text, `git log {{DEFAULT_BRANCH}}..HEAD
--format=full`, and `git diff {{DEFAULT_BRANCH}}...HEAD`.

1. Prefer a clean-context subagent review when available; otherwise do the
   same deep review yourself against the final draft, not memory.
2. No secrets or credentials: tokens, keys, passwords, connection strings,
   internal URLs, cookies, or signing material.
3. No personal data beyond what the task needs: names, emails, phone
   numbers, addresses, account identifiers, screenshots.
4. No internal-only context: codenames, private hostnames, ticket links,
   unreleased plans, or private branch names.
5. No accidental unrelated files or generated churn in the diff, and
   professional concise wording; English unless the project's conventions
   say otherwise.

If any check fails, fix the draft — or the branch, when the finding is in
the diff — and re-check. Publish only after the full text passes. Only the
user may skip this gate, explicitly; note the skip in your summary.

## Create a pull request

Write the PR body to a scratch file `BODY.md` first, containing every
template section listed above with real content under each; never pass
multi-line content as an inline shell string.

| Task | MCP capability | gh command |
|---|---|---|
| Create PR | create a pull request (base `{{DEFAULT_BRANCH}}`, head BRANCH, title, body from BODY.md) | `gh pr create -R {{OWNER_REPO}} --base {{DEFAULT_BRANCH}} --head BRANCH --title "TITLE" --body-file BODY.md` |

Done when: the new PR's URL is reported to the user and its checks have
been triggered.

## Review a pull request

Write any review text to a scratch file `REVIEW.md` first.

| Task | MCP capability | gh command |
|---|---|---|
| Read the diff | read a PR's diff | `gh pr diff N -R {{OWNER_REPO}}` |
| Check CI status | read a PR's status rollup | `gh pr checks N -R {{OWNER_REPO}}` |
| Submit review | author a PR review in its immediate-submit form (comment event, body from REVIEW.md) | `gh pr review N -R {{OWNER_REPO}} --comment --body-file REVIEW.md` |

Done when: the review is visible on the PR and its URL is reported.
