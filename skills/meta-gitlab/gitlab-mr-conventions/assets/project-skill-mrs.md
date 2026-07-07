---
name: {{PROJECT_NAME}}-mrs
description: >
  Opens and reviews merge requests in {{PROJECT_PATH}} on {{GITLAB_HOST}}
  following this project's conventions: target branch {{DEFAULT_BRANCH}},
  {{MERGE_METHOD}} merges (squash: {{SQUASH_OPTION}}), and the required
  MR template sections. Use when working with merge requests in this
  project — "open an MR", "create a merge request", "review MR !N", "is
  the pipeline green", or "submit a review".
---

# {{PROJECT_NAME}} merge requests

Open and review merge requests in `{{PROJECT_PATH}}` (host:
`{{GITLAB_HOST}}`) following the conventions below.

## Choose your path (do this first, once per session)

1. Run `glab auth status --hostname {{GITLAB_HOST}}`. If it exits 0, use
   the glab commands below (run them inside this project's checkout so
   glab targets the right host).
2. Otherwise stop and tell the user GitLab tooling is not set up. This
   skill pairs with `gitlab-tooling-setup`. If it is not installed,
   install it from https://github.com/ryan-minato/skills.git:

       npx skills add ryan-minato/skills --skill gitlab-tooling-setup

## This project's conventions

- Target branch: every MR targets `{{DEFAULT_BRANCH}}` unless the user
  says otherwise.
- Merge method: {{MERGE_METHOD}}; squash: {{SQUASH_OPTION}}.
- The MR description must contain every template section, each filled
  in: {{TEMPLATE_HEADINGS}}. The `mr-checklist` CI job fails the MR
  otherwise.
- Use `--draft` until the MR is ready for review.

## Pre-publish gate (mandatory)

Everything you send becomes visible the moment the call succeeds — to the
whole internet on public projects, and to every member just as instantly on
private or internal ones — and creating an MR publishes every commit
message and the complete diff of `{{DEFAULT_BRANCH}}...BRANCH`, not just
the description. Before any call that creates or edits such content,
review the exact final text (for an MR: title, description,
`git log {{DEFAULT_BRANCH}}..BRANCH --format=full`, and
`git diff {{DEFAULT_BRANCH}}...BRANCH`):

1. No secrets: tokens, keys, passwords, connection strings, internal URLs.
2. No personal data beyond what the task needs.
3. No internal-only context: codenames, private hostnames, unreleased plans.
4. No unintended quick actions: a body line starting with `/` can execute
   as one (for example `/close`).
5. Professional, concise wording; English unless the project's conventions
   say otherwise.

If any check fails, fix the draft — or the branch, when the finding is in
the diff — and re-check. Publish only after the full text passes. Only the
user may skip this gate, explicitly; note the skip in your summary.

## Create a merge request

Write the description to a scratch file `BODY.md` first, containing
every template section listed above with real content under each; never
pass multi-line content as an inline shell string, and never use
`--fill`.

| Task | glab command |
|---|---|
| Create MR | `glab mr create -R {{PROJECT_PATH}} -s BRANCH -b {{DEFAULT_BRANCH}} -t "TITLE" -d "$(cat BODY.md)" [--draft] -y` |
| Mark ready | `glab mr update N -R {{PROJECT_PATH}} --ready` |

Done when: the new MR's URL is reported and its pipeline has been
triggered.

## Review a merge request

Write any review text to a scratch file `REVIEW.md` first.

| Task | glab command |
|---|---|
| Read the diff | `glab mr diff N -R {{PROJECT_PATH}}` |
| Pipeline status | `glab ci get --merge-request N -R {{PROJECT_PATH}}` |
| Comment review | `glab mr note N -R {{PROJECT_PATH}} -m "$(cat REVIEW.md)"` |
| Approve | `glab mr approve N -R {{PROJECT_PATH}}` |

Done when: the review is visible on the MR and its URL is reported.
