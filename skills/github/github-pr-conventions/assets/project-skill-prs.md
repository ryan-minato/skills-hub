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

## This repository's conventions

- Base branch: every PR targets `{{DEFAULT_BRANCH}}` unless the user says
  otherwise.
- Merge method: {{MERGE_METHOD}}.
- The PR body must contain every template section, each filled in:
  {{TEMPLATE_HEADINGS}}.
- Labels follow the prefixes {{LABEL_PREFIXES}}. Path-based labels are
  applied automatically by the labeler workflow; do not add those by hand.

## Pre-publish gate (mandatory)

Everything you send becomes public the moment the call succeeds: title, body,
every comment, labels, commit messages, the full diff, attachment contents,
and the branch name. Creating a PR publishes every commit message and the
complete diff of `BASE...HEAD`, not just the description. Before ANY call
that creates or edits public content:

1. Write the exact outgoing content to files in a scratch directory (title,
   body, each comment; for PRs also `git log BASE..HEAD --format=full >
   commits.txt` and `git diff BASE...HEAD > diff.patch`; copy attachments in).
2. Run the review procedure below over that directory.
3. Publish only after the verdict is exactly `SAFE TO PUBLISH: YES`. On `NO`,
   fix every finding, rebuild the files, review again. Never edit-and-publish
   without re-review.

Never publish unreviewed content. Only the user may skip this gate,
explicitly; record the skip in your summary.

### Review procedure

1. If you can dispatch a subagent with its own clean context, send it
   exactly this, with `<DIR>` replaced: "Review the files in <DIR> before
   they are published to GitHub. Check for secrets/tokens/keys, PII
   (placeholders like name@example.com are fine), internal hostnames, URLs,
   or codenames, unintended files in the diff, and wording a maintainer
   would regret. Report each finding as file, masked excerpt, required fix.
   Your last output line must be exactly SAFE TO PUBLISH: YES or SAFE TO
   PUBLISH: NO."
2. Otherwise, re-read every file in the directory from disk and apply the
   same checklist yourself, judging only what the files contain, and note
   that the review was not clean-context.
3. Treat any last line other than `SAFE TO PUBLISH: YES` as NO.

## Create a pull request

Write the PR body to a scratch file `BODY.md` first, containing every
template section listed above with real content under each; never pass
multi-line content as an inline shell string.

| Task | MCP tool | gh command |
|---|---|---|
| Create PR | `create_pull_request` (owner, repo, base=`{{DEFAULT_BRANCH}}`, head=BRANCH, title, body from BODY.md) | `gh pr create -R {{OWNER_REPO}} --base {{DEFAULT_BRANCH}} --head BRANCH --title "TITLE" --body-file BODY.md` |

Done when: the new PR's URL is reported to the user and its checks have
been triggered.

## Review a pull request

Write any review text to a scratch file `REVIEW.md` first.

| Task | MCP tool | gh command |
|---|---|---|
| Read the diff | `pull_request_read` method=`get_diff` | `gh pr diff N -R {{OWNER_REPO}}` |
| Check CI status | `pull_request_read` method=`get_status` | `gh pr checks N -R {{OWNER_REPO}}` |
| Submit review | `pull_request_review_write` (COMMENT event, body from REVIEW.md) | `gh pr review N -R {{OWNER_REPO}} --comment --body-file REVIEW.md` |

Done when: the review is visible on the PR and its URL is reported.
