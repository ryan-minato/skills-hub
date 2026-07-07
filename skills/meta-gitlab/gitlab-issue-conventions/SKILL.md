---
name: gitlab-issue-conventions
description: >
  Authors a GitLab project's issue conventions: description templates in
  .gitlab/issue_templates/ with embedded quick actions, a Default.md
  fallback template, a scoped-label taxonomy (type::, priority::,
  status::) applied by an idempotent sync script, and a generated
  project-level agent skill for filing and triaging issues in that
  project — with an AGENTS.md section as the fallback deliverable. Works
  on gitlab.com and self-managed instances alike, defaulting to Free-tier
  mechanisms. Use when standardizing how a GitLab project's issues are
  filed and triaged — "add issue templates", "set up description
  templates", "define our labels", "set up scoped labels", "standardize
  issues", "automate issue triage in GitLab", or "create a skill for
  filing issues in this repo".
license: Apache-2.0
compatibility: >
  scripts/sync_labels.py requires Python 3.9+ (stdlib only) and a glab
  CLI authenticated against the target host.
---

# GitLab Issue Conventions

Author the files that define how a GitLab project's issues are filed,
labeled, and triaged: description templates, a scoped-label taxonomy,
template automation, and a project-level skill (or AGENTS.md section)
that teaches agents in that project to follow all of it. This skill
writes local files — only its outputs land in the project. Day-to-day
issue operations belong to `gitlab-issues`; MR conventions to
`gitlab-mr-conventions`; commit and release policy to
`gitlab-commit-conventions` / `gitlab-release-conventions`.

## Assess the project first

Before authoring anything, inventory what the project already has:
derive `HOST` and the full `PROJECT_PATH` from `git remote get-url
origin` (host = the part right after `https://` or the `@`; path = the
rest minus `.git`, nesting kept whole — never assume gitlab.com);
`.gitlab/issue_templates/` (existing templates including a `Default.md`
in any casing); existing labels via `glab label list -F json -P 100` run
inside the checkout — the listing includes **inherited group labels**
the project endpoints cannot edit, note which are which; `.gitlab-ci.yml`
scheduled jobs (for the automation section); `AGENTS.md` / `CLAUDE.md`
for recorded conventions; and where project skills live — use
`.claude/skills/` if it exists, else `.agents/skills/` if it exists, else
plan to create `.agents/skills/`. Never invent structure parallel to what
the project already defines: build on what exists, or get the user's
explicit approval to replace it.
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

## Automation

The templates' quick actions **are** the primary automation: they apply
the taxonomy at submission time with zero infrastructure, on any tier
and any host. GitLab has no issue-event pipelines, so there is no
GitLab-native equivalent of an issue-labeler workflow to ship.

Read [references/automation-recipes.md](references/automation-recipes.md)
when the user wants more (a scheduled triage sweep for unlabeled issues,
stale handling) — those need an API token with tier-dependent options,
spelled out there.

## Generate the project-level skill

For the default deliverable, copy
[assets/project-skill-issues.md](assets/project-skill-issues.md) to
`<skills-dir>/<project-name>-issues/SKILL.md` and fill every
`{{PLACEHOLDER}}`:

| Placeholder | Fill with |
|---|---|
| `{{PROJECT_NAME}}` | Project name, lowercase, hyphens only |
| `{{PROJECT_PATH}}` / `{{GITLAB_HOST}}` | From the origin remote |
| `{{TEMPLATES}}` | The template files and their display names |
| `{{LABEL_AXES}}` | The axes actually synced |

For the AGENTS.md fallback, copy
[assets/agents-md-issues-section.md](assets/agents-md-issues-section.md)
into the project's `AGENTS.md` (create the file if missing) and fill the
same placeholders. For refinement beyond the template this pairs with
`great-skill-writer`. If it is not installed, install it from
https://github.com/ryan-minato/skills.git:

    npx skills add ryan-minato/skills --skill great-skill-writer

Done when: the generated deliverable contains no `{{...}}` placeholder
and (for a skill) its frontmatter `name` matches its directory name.

## Deliver

Everything this skill wrote is local files — nothing is published yet. Hand
the changes to the project's normal git flow (branch, commit, review); that
flow, not this skill, publishes them and carries its own review gates.
Done when: the user has the list of every file created or changed, one line
each on what it does, and any follow-up steps (label sync to run, the
default branch merge that activates the templates).

The one action this skill performs against the server itself is the label
sync `--apply` — covered by the plan-first dry run plus the user's
agreement on `labels.json`.

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
