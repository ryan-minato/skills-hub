## Filing and triaging issues

This section is the fallback deliverable for projects whose harness does
not load agent skills; it carries the same rules as the generated skill.

Issues in `{{OWNER_REPO}}` follow these conventions:

- **Use the issue forms** in `.github/ISSUE_TEMPLATE/` ({{FORMS}}).
  Non-interactive creation does not apply a form automatically: draft the
  body to mirror the matching form's section headings, in order, with
  real content under each.
- **Labels**: apply only labels that already exist ({{LABEL_AXES}}).
  Every new issue gets the matching form's labels — one `type/*` plus
  `status/needs-triage`. Create with
  `gh issue create -R {{OWNER_REPO}} --title "..." --body-file BODY.md
  --label type/... --label status/needs-triage` (write the body to a
  file first; never inline multi-line text).
- **Triage**: for each issue carrying `status/needs-triage`, apply
  exactly one `type/*` and one `priority/*` label and remove
  `status/needs-triage`
  (`gh issue edit N -R {{OWNER_REPO}} --add-label ... --remove-label
  status/needs-triage`).
- **Before publishing anything** (issue, comment, edit), review the exact final text directly, preferably with a clean-context
  subagent when the surface is not trivial: no secrets or credentials, no
  personal data beyond the task's needs, no internal-only context
  (codenames, private hostnames, ticket links, unreleased plans), no
  accidental unrelated content, professional concise wording, English
  unless the project says otherwise. Fix and re-check before sending;
  only the user may skip this review, explicitly.
