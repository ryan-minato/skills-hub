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

Everything you send becomes visible the moment the call succeeds — to
the whole internet on a public project, to every member on a private
one: title, body, every comment, labels. A line starting with `/`
executes as a GitLab quick action (`/close`, `/label`). Before ANY call
that creates or edits such content:

1. Write the exact outgoing content to files in a scratch directory
   (title, body, each comment).
2. Run the review procedure below over that directory.
3. Publish only after the verdict is exactly `SAFE TO PUBLISH: YES`. On
   `NO`, fix every finding, rebuild the files, review again. Never
   edit-and-publish without re-review.

Never publish unreviewed content. Only the user may skip this gate,
explicitly; record the skip in your summary.

### Review procedure

1. If you can dispatch a subagent with its own clean context, send it
   exactly this, with `<DIR>` replaced: "Review the files in <DIR> before
   they are published on GitLab. Check for secrets/tokens/keys, PII
   (placeholders like name@example.com are fine), internal hostnames,
   URLs, or codenames, lines starting with / that would execute as quick
   actions, and wording a maintainer would regret. Report each finding as
   file, masked excerpt, required fix. Your last output line must be
   exactly SAFE TO PUBLISH: YES or SAFE TO PUBLISH: NO."
2. Otherwise, re-read every file in the directory from disk and apply the
   same checklist yourself, judging only what the files contain, and note
   that the review was not clean-context.
3. Treat any last line other than `SAFE TO PUBLISH: YES` as NO.

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
