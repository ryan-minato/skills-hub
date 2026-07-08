## Cutting releases

This section is the fallback deliverable for projects whose harness does
not load agent skills; it carries the same rules as the generated skill.
The policy source of truth is {{POLICY_DOC_PATH}}.

- **Version bump**: {{BUMP_RULE}}
- **Tag format**: `{{TAG_FORMAT}}` (regex `{{TAG_REGEX}}`); the tagged
  commit must be reachable from the default branch — CI rejects
  violations.
- **Notes**: {{NOTES_RULE}} Write them to `NOTES.md` before creating
  anything.
- **Flow (draft-first)**: create the draft
  (`gh release create TAG -R {{OWNER_REPO}} --draft --title "TITLE"
  --notes-file NOTES.md`), then review the exact assembled content — preferably with a clean-context
  subagent — tag name, title, NOTES.md, every asset: no secrets or
  credentials, no personal data beyond the task's needs, no
  internal-only context, no accidental unrelated content, professional
  concise wording. Only after everything passes:
  `gh release edit TAG -R {{OWNER_REPO}} --draft=false`, and report the
  release URL. Only the user may skip the review, explicitly.
