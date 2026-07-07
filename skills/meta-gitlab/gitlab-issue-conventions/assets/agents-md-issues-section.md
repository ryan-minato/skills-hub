## Filing and triaging issues

This section is the fallback deliverable for projects whose harness does
not load agent skills; it carries the same rules as the generated skill.

Issues in `{{PROJECT_PATH}}` (host: `{{GITLAB_HOST}}`) follow these
conventions:

- **Use the description templates** in `.gitlab/issue_templates/`
  ({{TEMPLATES}}): draft the body to mirror the matching template's
  section headings, in order, with real content under each. Do not
  append `/label` quick-action lines to a drafted body — pass labels
  with `-l`.
- **Labels**: scoped axes {{LABEL_AXES}}; apply only labels that already
  exist, at most one per axis. Every new issue gets one `type::*` plus
  `status::needs-triage`. Create with
  `glab issue create -R {{PROJECT_PATH}} -t "TITLE" -d "$(cat BODY.md)"
  -l "type::...,status::needs-triage" -y` (write the body to a file
  first; never inline multi-line text).
- **Triage**: for each issue carrying `status::needs-triage`, apply
  exactly one `type::*` and one `priority::*` and remove the status
  label (`glab issue update N -R {{PROJECT_PATH}} -l "..." -u
  "status::needs-triage"`).
- **Before publishing anything** (issue, comment, edit), review the
  exact final text: no secrets or tokens, no personal data beyond the
  task's needs, no internal-only context, no unintended quick actions
  (any body line starting with `/` can execute as one), professional and
  concise wording, English unless the project says otherwise. Fix and
  re-check before sending; only the user may skip this review,
  explicitly.
