---
name: {{PROJECT_NAME}}-issues
description: >
  Files and triages issues in {{PROJECT_PATH}} on {{GITLAB_HOST}} using
  this project's description templates and label taxonomy. Use when
  creating, labeling, or triaging an issue in this project — "file a
  bug", "report a bug in {{PROJECT_NAME}}", "request a feature", "triage
  new issues", or "label this issue".
---

# {{PROJECT_NAME}} Issues

Create and triage issues in `{{PROJECT_PATH}}` (host: `{{GITLAB_HOST}}`)
following this project's conventions.

## Choose your path (do this first, once per session)

1. Run `glab auth status --hostname {{GITLAB_HOST}}`. If it exits 0, use
   the glab commands below (run them inside this project's checkout so
   glab targets the right host).
2. Otherwise stop and tell the user GitLab tooling is not set up. This
   skill pairs with `gitlab-tooling-setup`. If it is not installed,
   install it from https://github.com/ryan-minato/skills.git:

       npx skills add ryan-minato/skills --skill gitlab-tooling-setup

## This project's conventions

- Description templates in `.gitlab/issue_templates/`: {{TEMPLATES}}
- Label axes: {{LABEL_AXES}}
- Every new issue gets exactly one `type::*` label plus
  `status::needs-triage`; each axis carries at most one label per issue.

## Pre-publish gate (mandatory)

Everything you send becomes visible the moment the call succeeds — to the
whole internet on public projects, and to every member just as instantly on
private or internal ones. Before any call that creates or edits such
content, review the exact final text:

1. No secrets: tokens, keys, passwords, connection strings, internal URLs.
2. No personal data beyond what the task needs.
3. No internal-only context: codenames, private hostnames, unreleased plans.
4. No unintended quick actions: a body line starting with `/` can execute
   as one (for example `/close`).
5. Professional, concise wording; English unless the project's conventions
   say otherwise.

If any check fails, fix the draft and re-check. Publish only after the full
text passes. Only the user may skip this gate, explicitly; note the skip in
your summary.

## Create an issue

Write the body to `BODY.md` first, mirroring the section headings of the
matching template in `.gitlab/issue_templates/`; multi-line content never
goes inline in a shell command. Do not append `/label` quick-action
lines to the body — pass labels with `-l`.

| Task | glab command |
|---|---|
| Bug report | `glab issue create -R {{PROJECT_PATH}} -t "TITLE" -d "$(cat BODY.md)" -l "type::bug,status::needs-triage" -y` |
| Feature request | `glab issue create -R {{PROJECT_PATH}} -t "TITLE" -d "$(cat BODY.md)" -l "type::feature,status::needs-triage" -y` |

Done when: the issue URL is reported and the issue carries one `type::*`
label plus `status::needs-triage`.

## Triage issues

Triage means: read each issue carrying `status::needs-triage`, apply
exactly one `type::*` and one `priority::*` label, and remove
`status::needs-triage`.

| Task | glab command |
|---|---|
| List untriaged issues | `glab issue list -R {{PROJECT_PATH}} -l "status::needs-triage"` |
| Read issue N | `glab issue view N -R {{PROJECT_PATH}}` |
| Label issue N | `glab issue update N -R {{PROJECT_PATH}} -l "type::...,priority::..." -u "status::needs-triage"` |

Done when: the issue carries exactly one `type::*` and one `priority::*`
label and no longer carries `status::needs-triage`.
