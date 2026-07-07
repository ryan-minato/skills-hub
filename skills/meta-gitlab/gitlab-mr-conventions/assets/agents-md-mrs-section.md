## Opening and reviewing merge requests

This section is the fallback deliverable for projects whose harness does
not load agent skills; it carries the same rules as the generated skill.

Merge requests in `{{PROJECT_PATH}}` (host: `{{GITLAB_HOST}}`) follow
these conventions:

- **Target branch**: every MR targets `{{DEFAULT_BRANCH}}` unless stated
  otherwise. Merge method: {{MERGE_METHOD}}; squash: {{SQUASH_OPTION}}.
- **Description**: must contain every template section, each filled in:
  {{TEMPLATE_HEADINGS}}. Write it to a file and create with
  `glab mr create -R {{PROJECT_PATH}} -s BRANCH -b {{DEFAULT_BRANCH}}
  -t "TITLE" -d "$(cat BODY.md)" -y` (never inline multi-line text;
  never `--fill` — it publishes unreviewed generated content).
- **Before creating or editing an MR**, review the exact final content —
  including `git log {{DEFAULT_BRANCH}}..BRANCH` and
  `git diff {{DEFAULT_BRANCH}}...BRANCH`, since an MR publishes every
  commit message and the complete diff: no secrets or tokens, no
  personal data beyond the task's needs, no internal-only context, no
  unintended quick actions (any line starting with `/` can execute as
  one), professional and concise wording, English unless the project
  says otherwise. Fix and re-check before sending; only the user may
  skip this review, explicitly.
- **Reviews**: read the diff (`glab mr diff N -R {{PROJECT_PATH}}`) and
  pipeline state (`glab ci get --merge-request N -R {{PROJECT_PATH}}`)
  before writing; comment with
  `glab mr note N -R {{PROJECT_PATH}} -m "$(cat REVIEW.md)"`.
