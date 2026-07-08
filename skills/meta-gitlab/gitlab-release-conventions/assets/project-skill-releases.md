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

GitLab has no draft releases. Everything you send becomes visible the moment
the call succeeds — to the whole internet on public projects, and to every
member just as instantly on private or internal ones. Before create, review
the exact final content: tag name, release name, NOTES.md, and every asset.

1. Prefer a clean-context subagent review when available; otherwise do the
   same deep review yourself against the final draft, not memory.
2. No secrets or credentials: tokens, keys, passwords, connection strings,
   internal URLs, cookies, or signing material.
3. No personal data beyond what the task needs: names, emails, phone
   numbers, addresses, account identifiers, screenshots.
4. No internal-only context: codenames, private hostnames, ticket links,
   unreleased plans, or private branch names.
5. No unintended quick actions: a body line starting with `/` can execute
   as one (for example `/close`).
6. No accidental unrelated content, and professional concise wording;
   English unless the project's conventions say otherwise.

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
