---
name: {{REPO_NAME}}-issues
description: >
  Files and triages issues in {{OWNER_REPO}} using this repository's
  issue forms and label taxonomy. Use when creating, labeling, or
  triaging an issue in this repository — "file a bug", "report a bug in
  {{REPO_NAME}}", "request a feature", "triage new issues", or "label
  this issue".
---

# {{REPO_NAME}} Issues

Create and triage issues in `{{OWNER_REPO}}` following this repository's
conventions.

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

- Issue forms in `.github/ISSUE_TEMPLATE/`: {{FORMS}}
- Label axes: {{LABEL_AXES}}
- Every new issue gets the matching form's labels: one `type/*` label
  plus `status/needs-triage`.

## Pre-publish gate (mandatory)

Everything you send becomes public the moment the call succeeds: title, body,
every comment, labels, commit messages, the full diff, attachment contents,
and the branch name. Before ANY call
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

## Create an issue

Write the body to a file `BODY.md` first, mirroring the section headings
of the matching issue form; multi-line content never goes inline in a
shell command.

| Task | MCP | gh |
|---|---|---|
| Bug report | `issue_write` method=`create`, owner/repo from `{{OWNER_REPO}}`, labels `["type/bug", "status/needs-triage"]`, body from `BODY.md` | `gh issue create -R {{OWNER_REPO}} --title "..." --body-file BODY.md --label type/bug --label status/needs-triage` |
| Feature request | `issue_write` method=`create`, owner/repo from `{{OWNER_REPO}}`, labels `["type/feature", "status/needs-triage"]`, body from `BODY.md` | `gh issue create -R {{OWNER_REPO}} --title "..." --body-file BODY.md --label type/feature --label status/needs-triage` |

Done when: the issue exists and carries the labels of the matching form.

## Triage issues

Triage means: read each issue that is unlabeled or carries
`status/needs-triage`, apply exactly one `type/*` and one `priority/*`
label, and remove `status/needs-triage`.

| Task | MCP | gh |
|---|---|---|
| List untriaged issues | `list_issues` with labels `["status/needs-triage"]` | `gh issue list -R {{OWNER_REPO}} --label status/needs-triage` |
| Read issue N | `issue_read` method=`get`, issue_number N | `gh issue view N -R {{OWNER_REPO}}` |
| Label issue N | `issue_write` method=`update`, labels set to the full final list (one `type/*`, one `priority/*`) | `gh issue edit N -R {{OWNER_REPO}} --add-label type/... --add-label priority/... --remove-label status/needs-triage` |

Done when: the issue carries exactly one `type/*` and one `priority/*`
label and no longer carries `status/needs-triage`.
