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

Everything you send becomes visible the moment the call succeeds — to
the whole internet on a public project, to every member on a private
one: title, description, every comment, labels, commit messages, the
full diff. Creating an MR publishes every commit message and the
complete diff of `{{DEFAULT_BRANCH}}...BRANCH`, not just the
description. A line starting with `/` executes as a GitLab quick action.
Before ANY call that creates or edits such content:

1. Write the exact outgoing content to files in a scratch directory
   (title, description, each comment; also `git log
   {{DEFAULT_BRANCH}}..BRANCH --format=full > commits.txt` and `git diff
   {{DEFAULT_BRANCH}}...BRANCH > diff.patch`).
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
   URLs, or codenames, unintended files in the diff, lines starting with
   / that would execute as quick actions, and wording a maintainer would
   regret. Report each finding as file, masked excerpt, required fix.
   Your last output line must be exactly SAFE TO PUBLISH: YES or SAFE TO
   PUBLISH: NO."
2. Otherwise, re-read every file in the directory from disk and apply the
   same checklist yourself, judging only what the files contain, and note
   that the review was not clean-context.
3. Treat any last line other than `SAFE TO PUBLISH: YES` as NO.

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
