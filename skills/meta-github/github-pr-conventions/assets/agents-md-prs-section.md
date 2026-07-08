## Opening and reviewing pull requests

This section is the fallback deliverable for projects whose harness does
not load agent skills; it carries the same rules as the generated skill.

Pull requests in `{{OWNER_REPO}}` follow these conventions:

- **Base branch**: every PR targets `{{DEFAULT_BRANCH}}` unless stated
  otherwise. Merge method: {{MERGE_METHOD}}.
- **Body**: the PR body must contain every template section, each filled
  in: {{TEMPLATE_HEADINGS}}. Write the body to a file and pass it with
  `gh pr create -R {{OWNER_REPO}} --base {{DEFAULT_BRANCH}}
  --head BRANCH --title "TITLE" --body-file BODY.md` (never inline
  multi-line text).
- **Labels** follow the prefixes {{LABEL_PREFIXES}}; path-based labels
  are applied by the labeler workflow — do not add those by hand.
- **Before creating or editing a PR**, review the exact final content — preferably with a clean-context
  subagent — including `git log {{DEFAULT_BRANCH}}..HEAD` and
  `git diff {{DEFAULT_BRANCH}}...HEAD`, since a PR publishes every
  commit message and the complete diff: no secrets or credentials, no
  personal data beyond the task's needs, no internal-only context, no
  accidental unrelated files or generated churn, professional concise
  wording, English unless the project says otherwise. Fix the draft or
  branch and re-check before sending; only the user may skip this review,
  explicitly.
- **Reviews**: read the diff (`gh pr diff N -R {{OWNER_REPO}}`) and CI
  status (`gh pr checks N -R {{OWNER_REPO}}`) before writing; submit
  with `gh pr review N -R {{OWNER_REPO}} --comment --body-file
  REVIEW.md`.
