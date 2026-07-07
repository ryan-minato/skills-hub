---
name: gitlab-mr-conventions
description: >
  Authors a GitLab project's merge-request conventions: a Default.md MR
  description template, a CONTRIBUTING merge-request rules section, a
  tokenless CI checklist-validation job that runs in merge request
  pipelines, and a generated project-level agent skill for opening and
  reviewing MRs in that project — with an AGENTS.md section as the
  fallback deliverable. Defaults to Free-tier mechanisms and
  works on gitlab.com and self-managed instances; Premium-only features
  (CODEOWNERS enforcement, required approvals) are marked as such. Use
  when standardizing how a GitLab project handles merge requests — "add
  an MR template", "merge request template", "enforce an MR checklist",
  "validate MR descriptions in CI", "document our review process",
  "standardize merge requests", or "create a skill for opening MRs in
  this repo".
license: Apache-2.0
---

# GitLab MR Conventions

Author the files that define how a GitLab project handles merge
requests: an MR description template, contributing rules, CI checklist
validation, and a project-level skill that teaches agents in that
project to follow all of it. This skill writes local files — only its
outputs land in the project. Day-to-day MR operations belong to
`gitlab-merge-requests`; issue templates and labels to
`gitlab-issue-conventions`; commit and release policy to
`gitlab-commit-conventions` / `gitlab-release-conventions`.

## Assess the project first

Before authoring anything, inventory what the project already has:
derive `HOST` and the full `PROJECT_PATH` from `git remote get-url
origin` (host = the part right after `https://` or the `@`; path = the
rest minus `.git`, kept whole — never assume gitlab.com);
`.gitlab/merge_request_templates/` (existing templates, especially a
`Default.md` in any casing — adapt rather than replace);
`CONTRIBUTING.md` (root or `docs/`); `.gitlab-ci.yml`, specifically
whether its jobs run as classic branch pipelines (no
`rules:`/`workflow:` keys — this decides how the checklist job
integrates); merge settings from inside the checkout (`glab api
projects/:fullpath` → `default_branch`, `merge_method`,
`squash_option`); `AGENTS.md` / `CLAUDE.md` for recorded conventions;
and where project skills live — use `.claude/skills/` if it exists, else
`.agents/skills/` if it exists, else plan to create `.agents/skills/`.
Never invent structure parallel to what the project already defines:
build on what exists, or get the user's explicit approval to replace it.
Done when: the inventory is written down and each deliverable below is
marked "new", "extends existing", or "replaces (approved)".

## Choose the deliverable

The default deliverable for workflow guidance is a **project-level agent
skill** in the skills directory found during assessment. When the project's
harness does not support skills, or the user prefers documentation, deliver
an `AGENTS.md` section (create the file if missing) or a standalone doc
instead. Ask the user once, before generating, and record the choice. All
other artifacts (templates, configs, CI jobs, validators) ship regardless
of this choice.

## MR description template

Copy [assets/mr-template-default.md](assets/mr-template-default.md) to
`.gitlab/merge_request_templates/Default.md` and adjust the prompts.
`Default.md` auto-populates every new MR (GitLab ≥ 14.8, Free) — no URL
parameter or chooser needed; additional named templates in the same
directory appear in the template dropdown. Keep the headings exactly in
sync with the checklist job's heading list (next section) — renaming one
silently breaks the check.

Done when: the template exists and its headings match the checklist
job's list.

## CONTRIBUTING merge-request rules

Copy or append
[assets/contributing-mr-section.md](assets/contributing-mr-section.md)
into `CONTRIBUTING.md` and fill `{{DEFAULT_BRANCH}}`,
`{{BRANCH_PREFIX}}`, `{{MERGE_METHOD}}`, `{{SQUASH_OPTION}}`, and
`{{REVIEW_RESPONSE_EXPECTATION}}` from the assessment. Read
[references/contributing-rules.md](references/contributing-rules.md)
for the full guidance behind each rule (merge-method trade-offs, draft
workflow, approvals and CODEOWNERS with their tier gates).

## Checklist validation in CI

Copy the job in [assets/mr-checklist-job.yml](assets/mr-checklist-job.yml)
**directly into `.gitlab-ci.yml`** (create the file with just this job
if absent) — GitLab ignores merge-request-pipeline rules that exist only
inside `include:`d files. The job runs in merge request pipelines
(Free), validates `$CI_MERGE_REQUEST_DESCRIPTION` with POSIX shell only
(no token, no external image — safe on fork MRs), checks every required
heading, requires the security checkbox to be present AND ticked, and
fails closed when the description is truncated past the CI-variable
limit.

Two integration decisions:

- **Duplicate pipelines**: if the assessment found classic branch
  pipelines, adding an MR-event job makes every push to an MR branch
  spawn two pipelines. Offer the `workflow:rules` switch-over block in
  [references/automation-recipes.md](references/automation-recipes.md)
  — it changes when every job runs, so apply it only with the user's
  explicit agreement.
- **Making it blocking**: the failing job blocks merges only when
  Settings > Merge requests > "Pipelines must succeed" is enabled
  (Free). Tell the user to flip it; the skill cannot do it for them
  without project settings access.

Validate the edited `.gitlab-ci.yml` with `glab ci lint` when glab is
authenticated for the host.

Done when: the job is in `.gitlab-ci.yml`, the YAML parses (or `glab ci
lint` passes), and the heading list matches the template.

## Generate the project-level skill

For the default deliverable, copy
[assets/project-skill-mrs.md](assets/project-skill-mrs.md) to
`<skills-dir>/<project-name>-mrs/SKILL.md` and fill every
`{{PLACEHOLDER}}`:

| Placeholder | Fill with |
|---|---|
| `{{PROJECT_NAME}}` | Project name, lowercase, hyphens only |
| `{{PROJECT_PATH}}` / `{{GITLAB_HOST}}` | From the origin remote |
| `{{DEFAULT_BRANCH}}` / `{{MERGE_METHOD}}` / `{{SQUASH_OPTION}}` | From the assessment |
| `{{TEMPLATE_HEADINGS}}` | The exact headings shipped in the MR template |

For the AGENTS.md fallback, copy
[assets/agents-md-mrs-section.md](assets/agents-md-mrs-section.md) into
the project's `AGENTS.md` (create the file if missing) and fill the same
placeholders. The skill template pre-wires the host-checked glab path,
the project's conventions, the condensed pre-publish gate, and
create/review tables. For refinement beyond the template this pairs with
`great-skill-writer`. If it is not installed, install it from
https://github.com/ryan-minato/skills.git:

    npx skills add ryan-minato/skills --skill great-skill-writer

Done when: the generated deliverable contains no `{{...}}` placeholder
and (for a skill) its frontmatter `name` matches its directory name.

## Automation beyond the checklist

Read [references/automation-recipes.md](references/automation-recipes.md)
when the user wants more: linked-issue or title checks inside the same
job (tokenless), path-based auto-labeling (token required, tier notes
inside), stale-MR sweeps, or the duplicate-pipeline switch-over.

## Deliver

Everything this skill wrote is local files — nothing is published yet. Hand
the changes to the project's normal git flow (branch, commit, review); that
flow, not this skill, publishes them and carries its own review gates.
Done when: the user has the list of every file created or changed, one line
each on what it does, and any follow-up steps ("Pipelines must succeed" to
enable, the first MR to watch the checklist job on).

## Gotchas

- MR-pipeline rules count only when written directly in
  `.gitlab-ci.yml`; rules inside `include:`d files do not enable merge
  request pipelines.
- `$CI_MERGE_REQUEST_DESCRIPTION` is capped (2700 characters, GitLab
  ≥ 16.7, with `$CI_MERGE_REQUEST_DESCRIPTION_IS_TRUNCATED` set when
  cut); the job fails closed on truncation — keep the template compact.
  On older instances the variable is simply shorter-lived history: the
  truncation flag is unset, which the job treats as not-truncated.
- Template changes affect only new MRs (the description is snapshotted
  at creation) and only take effect from the default branch.
- Renaming a template heading without updating the job's heading list
  silently breaks validation — they must move together.
- The checklist job blocks merges only with "Pipelines must succeed"
  enabled; otherwise it is advisory red.
- Fork MRs run the MR pipeline in the fork's context: the shipped job is
  tokenless by design — never add secrets to it.
- CODEOWNERS and required approval rules are Premium/Ultimate; on Free
  the CODEOWNERS file is inert and approvals are optional — CONTRIBUTING
  text carries the review rules there.
