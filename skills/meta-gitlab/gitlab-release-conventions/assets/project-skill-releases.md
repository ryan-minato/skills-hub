---
name: {{PROJECT_NAME}}-releases
description: >
  Cuts releases for {{PROJECT_PATH}} on {{GITLAB_HOST}} following this
  project's versioning policy: {{TAG_FORMAT}} tags, notes reviewed
  before the release is created (GitLab has no drafts), and the
  project's milestone rule. Use when releasing this project — "cut a
  release", "release {{PROJECT_NAME}}", "tag a new version", "generate
  the changelog", or "publish the release".
---

# {{PROJECT_NAME}} releases

Cut releases in `{{PROJECT_PATH}}` (host: `{{GITLAB_HOST}}`) following
the conventions below. The policy source of truth is
{{POLICY_DOC_PATH}}. Run glab inside this project's checkout so it
targets the right host.

## This project's conventions

- Version bump: {{BUMP_RULE}}
- Tag format: `{{TAG_FORMAT}}` (regex `{{TAG_REGEX}}`); the tagged
  commit must be reachable from the default branch — CI rejects tags
  that break either rule.
- Release notes: {{NOTES_RULE}}
- Milestones: {{MILESTONE_RULE}}

## Pre-publish gate (mandatory)

GitLab has no draft releases — `glab release create` publishes the tag,
name, notes, and asset links the moment the call succeeds, so this gate
runs on the complete assembled release before create. Before that call,
review the exact final content (tag name, release name, NOTES.md, every
asset file or link):

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

## Cut a release

1. Pick the next version per the bump rule above; confirm it against
   `git tag --sort=-v:refname | head -5`.
2. Write the notes to `NOTES.md`: {{NOTES_RULE_SHORT}}.
3. Run the gate above over the assembled release — there is no draft to
   fix up afterwards.
4. Create:

       glab release create TAG -R {{PROJECT_PATH}} --name "NAME" \
         --notes-file NOTES.md {{EXTRA_CREATE_FLAGS}}

5. Report the release URL.

Done when: the URL is reported and `glab release view TAG -R
{{PROJECT_PATH}}` shows the expected notes and assets.
