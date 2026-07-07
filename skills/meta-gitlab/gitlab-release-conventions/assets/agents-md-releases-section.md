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
- **Milestones**: {{MILESTONE_RULE}}
- **Flow (no drafts on GitLab)**: review the exact assembled content
  *before* creating — tag name, release name, NOTES.md, every asset: no
  secrets or tokens, no personal data beyond the task's needs, no
  internal-only context, no unintended quick actions (lines starting
  with `/`), professional concise wording. Only after everything
  passes: `glab release create TAG -R {{PROJECT_PATH}} --name "NAME"
  --notes-file NOTES.md {{EXTRA_CREATE_FLAGS}}`, then report the
  release URL. Only the user may skip the review, explicitly.
