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

1. Look at the tools available in this session. If a connected MCP server
   provides GitHub issue tools (each tool's description states its
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

- Issue forms in `.github/ISSUE_TEMPLATE/`: {{FORMS}}
- Label axes: {{LABEL_AXES}}
- Every new issue gets the matching form's labels: one `type/*` label
  plus `status/needs-triage`.
- Draft the body to mirror the matching form's section headings, in
  order, with real content under each; ask the user for any required
  answer you do not have.

## Pre-publish gate (mandatory)

Everything you send becomes public the moment the call succeeds. Before any
call that creates or edits public content, review the exact final text:

1. Prefer a clean-context subagent review when available; otherwise do the
   same deep review yourself against the final draft, not memory.
2. No secrets or credentials: tokens, keys, passwords, connection strings,
   internal URLs, cookies, or signing material.
3. No personal data beyond what the task needs: names, emails, phone
   numbers, addresses, account identifiers, screenshots.
4. No internal-only context: codenames, private hostnames, ticket links,
   unreleased plans, or private branch names.
5. No accidental unrelated content, and professional concise wording;
   English unless the project's conventions say otherwise.

If any check fails, fix the draft and re-check. Publish only after the full
text passes. Only the user may skip this gate, explicitly; note the skip in
your summary.

## Create an issue

Write the body to a file `BODY.md` first, mirroring the section headings
of the matching issue form; multi-line content never goes inline in a
shell command.

| Task | MCP capability | gh |
|---|---|---|
| Bug report | create an issue (owner/repo `{{OWNER_REPO}}`, labels `type/bug` + `status/needs-triage`, body from BODY.md) | `gh issue create -R {{OWNER_REPO}} --title "..." --body-file BODY.md --label type/bug --label status/needs-triage` |
| Feature request | create an issue (labels `type/feature` + `status/needs-triage`) | `gh issue create -R {{OWNER_REPO}} --title "..." --body-file BODY.md --label type/feature --label status/needs-triage` |

Done when: the issue exists, carries the matching form's labels, and its
URL is reported.

## Triage issues

Triage means: read each issue that is unlabeled or carries
`status/needs-triage`, apply exactly one `type/*` and one `priority/*`
label, and remove `status/needs-triage`.

| Task | MCP capability | gh |
|---|---|---|
| List untriaged issues | list issues filtered to label `status/needs-triage` | `gh issue list -R {{OWNER_REPO}} --label status/needs-triage` |
| Read issue N | read an issue | `gh issue view N -R {{OWNER_REPO}}` |
| Label issue N | update an issue's labels to the full final list (one `type/*`, one `priority/*`) | `gh issue edit N -R {{OWNER_REPO}} --add-label type/... --add-label priority/... --remove-label status/needs-triage` |

Done when: the issue carries exactly one `type/*` and one `priority/*`
label and no longer carries `status/needs-triage`.
