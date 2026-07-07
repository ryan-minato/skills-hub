---
name: gitlab-issue-conventions
description: >
  Authors a GitLab project's issue conventions: description templates in
  .gitlab/issue_templates/ with embedded quick actions, a Default.md
  fallback template, a scoped-label taxonomy (type::, priority::,
  status::) applied by an idempotent sync script, and a generated
  project-level agent skill for filing and triaging issues in that
  project. Works on gitlab.com and self-managed instances alike,
  defaulting to Free-tier mechanisms. Use when standardizing how a
  GitLab project's issues are filed and triaged — "add issue templates",
  "set up description templates", "define our labels", "set up scoped
  labels", "standardize issues", "automate issue triage in GitLab", or
  "create a skill for filing issues in this repo".
license: Apache-2.0
compatibility: >
  scripts/sync_labels.py requires Python 3.9+ (stdlib only) and a glab
  CLI authenticated against the target host.
---

# GitLab Issue Conventions

Author the files that define how a GitLab project's issues are filed,
labeled, and triaged: description templates, a label taxonomy, template
automation, and a project-level skill that teaches agents in that
project to follow all of it. This skill writes local files; day-to-day
issue operations belong to `gitlab-issues`, MR conventions to
`gitlab-mr-conventions`, and glab setup to `gitlab-tooling-setup`.

## Assess the project first

Inventory what already exists before writing anything:

1. Derive `HOST` and the full `PROJECT_PATH` from
   `git remote get-url origin` (host = the part right after `https://`
   or the `@`; path = the rest minus `.git` — GitLab paths can nest,
   keep `group/subgroup/project` whole). Never assume gitlab.com.
2. `.gitlab/issue_templates/` — existing templates, including a
   `Default.md` (any casing).
3. Existing labels: `glab label list -F json -P 100` (run inside the
   checkout so glab targets the right host). The listing includes
   **inherited group labels** the project endpoints cannot edit — note
   which are which.
4. `.gitlab-ci.yml` — existing scheduled jobs (for the automation
   section).
5. The project's agent-skills directory: use `.claude/skills/` if it
   exists, else `.agents/skills/` if it exists, else create
   `.agents/skills/`.

Done when: an inventory of existing templates, labels (own vs
inherited), CI schedules, and the chosen skills directory is written
down.

## Description templates

Copy [assets/issue-template-bug.md](assets/issue-template-bug.md),
[assets/issue-template-feature.md](assets/issue-template-feature.md),
and [assets/issue-template-default.md](assets/issue-template-default.md)
to `.gitlab/issue_templates/Bug.md`, `.gitlab/issue_templates/Feature.md`,
and `.gitlab/issue_templates/Default.md`; then edit the prompts to fit
the project. GitLab templates are plain markdown — no forms schema, no
required fields; prompts live in HTML comments, and the trailing
quick-action lines (`/label ~"type::bug" ~"status::needs-triage"`) are
what applies labels on submission.

A `/label` naming a label that does not exist is **silently ignored** —
sync the taxonomy (next section) before or together with the templates.

Read [references/template-authoring.md](references/template-authoring.md)
when authoring or editing a template beyond the shipped assets, or
configuring default templates.

Done when: the templates exist and every label their quick actions name
appears in the taxonomy.

## Label taxonomy

Start from [assets/labels.json](assets/labels.json) — twelve labels on
three scoped axes (`type::`, `priority::`, `status::`) — and adjust
names, colors, and descriptions to the project with the user. The `::`
scope gives native one-per-axis exclusivity on Premium/Ultimate; on Free
the same names work as plain labels (the generated project skill
enforces one-per-axis manually), and upgrade cleanly later.

Apply it with [scripts/sync_labels.py](scripts/sync_labels.py): plan
first, validate, then execute.

```bash
python3 scripts/sync_labels.py --file labels.json --project GROUP/SUB/NAME --host HOST          # plan only
python3 scripts/sync_labels.py --file labels.json --project GROUP/SUB/NAME --host HOST --apply  # execute
```

The plan (JSON on stdout in both modes) lists create / update / in-sync,
reports inherited group labels it will never touch, and lists prune
candidates — project labels absent from the file. Pass `--prune` with
`--apply` only when the user explicitly asks: deletion strips the label
from every issue carrying it. Re-running after apply yields an all-in-
sync plan. `--group GROUP` syncs a group-level taxonomy instead.

## Generate the project-level skill

Copy [assets/project-skill-issues.md](assets/project-skill-issues.md) to
`<skills-dir>/<project-name>-issues/SKILL.md` (the directory chosen
during assessment) and fill every `{{PLACEHOLDER}}`: `{{PROJECT_NAME}}`,
`{{PROJECT_PATH}}`, and `{{GITLAB_HOST}}` from the origin remote,
`{{TEMPLATES}}` with the template files and their display names,
`{{LABEL_AXES}}` with the axes actually synced. The template pre-wires
the project's templates, its taxonomy, the glab-first path check against
the right host, the embedded pre-publish gate with inline review
procedure, and a triage table. For refinement beyond the template this
pairs with `great-skill-writer`. If it is not installed, install it from
https://github.com/ryan-minato/skills.git:

    npx skills add ryan-minato/skills --skill great-skill-writer

Done when: the generated SKILL.md contains no `{{...}}` placeholder and
its frontmatter `name` matches its directory name.

## Automation

The templates' quick actions **are** the primary automation: they apply
the taxonomy at submission time with zero infrastructure, on any tier
and any host. GitLab has no issue-event pipelines, so there is no
GitLab-native equivalent of an issue-labeler workflow to ship.

Read [references/automation-recipes.md](references/automation-recipes.md)
when the user wants more (a scheduled triage sweep for unlabeled issues,
stale handling) — those need an API token with tier-dependent options,
spelled out there.

## Deliver

The new files are local until committed and pushed through the project's
normal git/MR flow — pushing is what publishes them, and that flow
carries its own review gates. The one action this skill itself performs
against the server is the label sync `--apply`, covered by the
plan-first dry run plus the user's agreement on `labels.json`.

Done when: templates + label plan (applied or handed to the user) +
generated project skill all exist locally, and the templates render as
intended markdown.

## Gotchas

- Templates and `Default.md` take effect only from the **default
  branch**; a feature branch shows nothing.
- Label colors REQUIRE the leading `#` (`#d73a4a`) in GitLab's API and
  glab — the bare `d73a4a` form GitHub uses is rejected.
- `glab label edit` identifies labels by numeric `--label-id`, not name
  — use the sync script rather than hand edits.
- Quick actions: one per line, executed with the submitter's
  permissions; unknown labels silently ignored; users can delete the
  lines before submitting — they are defaults, not enforcement.
- Scoped-label exclusivity (and the two-tone rendering) is
  Premium/Ultimate; Free shows plain labels literally named
  `type::bug`, which still sort and filter fine.
- Label lists include ancestor-group labels (`is_project_label: false`);
  the project endpoints cannot edit or delete them — group-level
  changes go through the group (or the script's `--group` mode with
  group permissions).
