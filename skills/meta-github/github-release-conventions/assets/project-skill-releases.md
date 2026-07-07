---
name: {{REPO_NAME}}-releases
description: >
  Cuts releases for {{OWNER_REPO}} following this repository's
  versioning policy: {{TAG_FORMAT}} tags, a draft-first flow with a
  review gate before publishing, and the repository's release-notes
  convention. Use when releasing this repository — "cut a release",
  "release {{REPO_NAME}}", "tag a new version", "draft the release
  notes", or "publish the draft".
---

# {{REPO_NAME}} releases

Cut releases in `{{OWNER_REPO}}` following the conventions below. The
policy source of truth is {{POLICY_DOC_PATH}}.

## This repository's conventions

- Version bump: {{BUMP_RULE}}
- Tag format: `{{TAG_FORMAT}}` (regex `{{TAG_REGEX}}`); the tagged
  commit must be reachable from the default branch — CI rejects tags
  that break either rule.
- Release notes: {{NOTES_RULE}}

## Pre-publish gate (mandatory)

Publishing a release publishes the notes, the tag, and every asset, and
notifies watchers — the draft step exists so this gate always runs
before the release goes live. Before `--draft=false`, review the exact
final content (tag name, release title, NOTES.md, every asset file):

1. No secrets: tokens, keys, passwords, connection strings, internal URLs.
2. No personal data beyond what the task needs.
3. No internal-only context: codenames, private hostnames, unreleased plans.
4. Professional, concise wording; English unless the project's conventions
   say otherwise.

If any check fails, fix the draft and re-check. Publish only after the
full text passes. Only the user may skip this gate, explicitly; note
the skip in your summary.

## Cut a release

1. Pick the next version per the bump rule above; confirm it against
   `git tag --sort=-v:refname | head -5`.
2. Write the notes to `NOTES.md`: {{NOTES_RULE_SHORT}}.
3. Create the draft:

       gh release create TAG -R {{OWNER_REPO}} --draft --title "TITLE" \
         --notes-file NOTES.md {{EXTRA_CREATE_FLAGS}}

4. Run the gate above over the assembled draft.
5. Publish: `gh release edit TAG -R {{OWNER_REPO}} --draft=false`.
6. Report the release URL.

Done when: the URL is reported and
`gh release view TAG -R {{OWNER_REPO}} --json isDraft` shows `false`.
