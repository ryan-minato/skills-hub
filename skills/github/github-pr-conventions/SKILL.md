---
name: github-pr-conventions
description: >
  Authors a repository's pull-request conventions: a PR template, a
  CONTRIBUTING pull-request rules section, path-based auto-labeling and
  checklist-validation workflows built from first-party actions only, and
  a generated project-level agent skill for opening and reviewing PRs in
  that repository. Use when standardizing how a repository handles pull
  requests — "add a PR template", "enforce a PR checklist", "auto-label
  PRs", "document our review process", "standardize pull requests", or
  "create a skill for opening PRs in this repo".
license: Apache-2.0
---

# GitHub PR Conventions

Author a repository's pull-request conventions: template, contributing
rules, automation workflows, and a project-level skill that teaches agents
to open and review PRs the way this repository expects. This skill authors
local files only: day-to-day PR operations belong to
`github-pull-requests`, issue templates and label taxonomy to
`github-issue-conventions`, and setting up missing GitHub tooling to
`github-tooling-setup`.

## Assess the repository first

Before writing anything, record what already exists:

1. Existing PR template: check `.github/pull_request_template.md`, a root
   `pull_request_template.md`, `docs/pull_request_template.md`, and a
   `.github/PULL_REQUEST_TEMPLATE/` directory. If one exists, adapt it —
   do not replace it wholesale without asking.
2. `CONTRIBUTING.md` (root or `.github/`), and existing workflows in
   `.github/workflows/` (avoid file-name collisions with the workflows
   added below).
3. Base branch and allowed merge methods. Derive `O/R` from
   `git remote get-url origin` (the part after `github.com/` or
   `github.com:`, minus a trailing `.git`), then run:

       gh repo view --json defaultBranchRef,mergeCommitAllowed,squashMergeAllowed,rebaseMergeAllowed -R O/R

4. The agent-skills directory for the generated skill: use
   `.claude/skills/` if it exists, else `.agents/skills/`, else create
   `.agents/skills/`.

Done when: existing conventions and the chosen skills directory are
written down.

## PR template

Copy [assets/pull-request-template.md](assets/pull-request-template.md)
to `.github/pull_request_template.md`. Adapt the section contents with the
user, but keep the exact heading names in sync with the
checklist-validation workflow below — the workflow greps the PR body for
those headings, so a renamed heading makes every PR fail validation until
the workflow's heading list is updated to match.

If the repository genuinely has distinct PR kinds (for example release PRs
versus regular changes), put one file per kind in
`.github/PULL_REQUEST_TEMPLATE/<name>.md` and select one with
`?template=<name>.md` appended to the compare URL; otherwise ship the
single default template.

## CONTRIBUTING pull-request rules

Copy [assets/contributing-pr-section.md](assets/contributing-pr-section.md)
into `CONTRIBUTING.md`: append the section if the file exists, otherwise
create the file with it. Fill the `{{...}}` placeholders from the
assessment above. Read
[references/contributing-rules.md](references/contributing-rules.md) when
the user wants full contributing guidance (branch naming, merge strategy,
review expectations) beyond the shipped section.

## Generate the project-level skill

Copy [assets/project-skill-prs.md](assets/project-skill-prs.md) to
`<skills-dir>/<repo-name>-prs/SKILL.md` and fill every `{{PLACEHOLDER}}`:

| Placeholder | Fill with |
|---|---|
| `{{REPO_NAME}}` | Repository name, lowercase, hyphens only |
| `{{OWNER_REPO}}` | `O/R` from the assessment |
| `{{DEFAULT_BRANCH}}` | Default branch from `gh repo view` |
| `{{MERGE_METHOD}}` | The repository's merge method (for example squash) |
| `{{TEMPLATE_HEADINGS}}` | The exact headings shipped in the PR template |
| `{{LABEL_PREFIXES}}` | Label prefixes in use (for example `area/`) |

Verify no `{{` remains in the generated file. Refinement beyond the
template pairs with `great-skill-writer` — if it is not installed, install
it from https://github.com/ryan-minato/skills.git:
`npx skills add ryan-minato/skills --skill great-skill-writer`.

## Automation

Copy three files:

| Asset | Destination |
|---|---|
| [assets/labeler-config.yml](assets/labeler-config.yml) | `.github/labeler.yml` |
| [assets/workflow-pr-labeler.yml](assets/workflow-pr-labeler.yml) | `.github/workflows/pr-labeler.yml` |
| [assets/workflow-pr-checklist.yml](assets/workflow-pr-checklist.yml) | `.github/workflows/pr-checklist.yml` |

Use first-party actions only (`actions/*`, `github/*`): workflows run
with repository permissions, so every third-party action is a
supply-chain decision — add one only on explicit user opt-in. Every label
key in `.github/labeler.yml` must already exist in the repository; create
missing ones before the first PR triggers the workflow.
`.github/labeler.yml` is the PR labeler's config; the issue labeler
(`github-issue-conventions`) uses `.github/issue-labeler.yml` — do not
merge the two files. Read
[references/automation-recipes.md](references/automation-recipes.md) when
customizing the labeler config syntax or adding more automation (title
validation, linked-issue enforcement, stale-PR handling).

## Deliver

Everything this skill writes stays local until it is committed and pushed
through the repository's normal git/PR flow, which carries its own review
gates — this skill publishes nothing itself.

Done when: the PR template, the CONTRIBUTING section, the generated
project skill, `.github/labeler.yml`, and both workflow files exist
locally, the YAML files parse, and no `{{PLACEHOLDER}}` remains in
generated output.

## Gotchas

- PR templates only take effect once merged to the default branch —
  testing from a feature branch shows nothing on new PRs.
- Template changes do not affect already-open PRs; a PR's body is
  snapshotted from the template at creation time.
- `actions/labeler` requires the `pull_request_target` trigger to label
  fork PRs (plain `pull_request` gets a read-only token on forks). That
  workflow must never check out or run PR code, and its permissions stay
  minimal — it runs with repository permissions.
- labeler v6 keeps the v5 config syntax (`any-glob-to-any-file` and
  friends); older v4-era configs with bare glob lists do not work.
- Renaming a heading in the PR template silently breaks the checklist
  workflow until its heading list is updated to match.
