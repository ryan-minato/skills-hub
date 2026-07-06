---
name: github-issue-conventions
description: >
  Authors a repository's issue conventions: GitHub issue forms plus
  config.yml, a baseline label taxonomy applied by an idempotent sync
  script, first-party-only Actions automation for issue labeling, and a
  generated project-level agent skill for filing and triaging issues in
  that repository. Use when standardizing how a repo's issues are filed
  and triaged — "add issue templates", "set up issue forms", "define our
  labels", "standardize issues", "automate issue triage", or "create a
  skill for filing issues in this repo".
license: Apache-2.0
compatibility: >
  scripts/sync_labels.py requires Python 3.9+ (stdlib only) and an
  authenticated gh CLI.
---

# GitHub Issue Conventions

Author the files that define how a repository's issues are filed, labeled,
and triaged: issue forms, a label taxonomy, labeling automation, and a
project-level skill that teaches agents in that repository to follow all
of it. This skill writes local files; day-to-day issue operations belong
to `github-issues`, PR conventions to `github-pr-conventions`, and MCP/gh
setup to `github-tooling-setup`.

## Assess the repository first

Inventory what already exists before writing anything:

1. `.github/ISSUE_TEMPLATE/` — existing issue forms, legacy `.md`
   templates, and `config.yml`.
2. Existing labels: derive `O/R` from `git remote get-url origin` (the
   part after `github.com/` or `github.com:`, minus a trailing `.git`),
   then `gh label list -R O/R --json name,color,description`. If only the
   GitHub MCP server is available, use its `list_label` tool instead.
3. `.github/workflows/` — existing issue automation.
4. The project's agent-skills directory: use `.claude/skills/` if it
   exists, else `.agents/skills/` if it exists, else create
   `.agents/skills/`.

Done when: an inventory of existing templates, labels, workflows, and the
chosen skills directory is written down.

## Issue forms

Copy [assets/issue-form-bug.yml](assets/issue-form-bug.yml) and
[assets/issue-form-feature.yml](assets/issue-form-feature.yml) to
`.github/ISSUE_TEMPLATE/bug.yml` and `.github/ISSUE_TEMPLATE/feature.yml`,
and [assets/issue-template-config.yml](assets/issue-template-config.yml)
to `.github/ISSUE_TEMPLATE/config.yml`; then edit the placeholders
(project name, contact links, labels) to fit the repository.

Every label a form references must exist in the repository, or GitHub
silently drops it — sync the label taxonomy (next section) before or
together with the forms.

Read [references/issue-forms-schema.md](references/issue-forms-schema.md)
when authoring or editing a form beyond the shipped assets.

Done when: each form file parses as YAML and references only labels
present in the taxonomy.

## Label taxonomy

Start from [assets/labels.json](assets/labels.json) — twelve labels on
three axes (`type/*`, `priority/*`, `status/*`) — and adjust names,
colors, and descriptions to the repository with the user.

Apply it with [scripts/sync_labels.py](scripts/sync_labels.py): plan
first, validate, then execute.

```bash
python3 scripts/sync_labels.py --file labels.json --repo O/R          # plan only, changes nothing
python3 scripts/sync_labels.py --file labels.json --repo O/R --apply  # execute the plan
```

The plan (JSON on stdout in both modes) lists create / update / skip and
reports prune candidates — labels present in the repo but absent from the
file. Pass `--prune` together with `--apply` to delete those, and only
when the user explicitly asks: deletion strips the label from every issue
that carries it. The script is idempotent; re-running after apply yields
all-skip.

If only MCP is available (no gh), apply the printed plan one label at a
time with the `label_write` tool (method `create` or `update`), or hand
the plan to the user.

## Generate the project-level skill

Copy [assets/project-skill-issues.md](assets/project-skill-issues.md) to
`<skills-dir>/<repo-name>-issues/SKILL.md` (the skills directory chosen
during assessment) and fill every `{{PLACEHOLDER}}`: `{{REPO_NAME}}` and
`{{OWNER_REPO}}` from the origin remote, `{{FORMS}}` with the form files
and their display names, `{{LABEL_AXES}}` with the axes actually synced.
The template pre-wires the repository's issue forms, its label taxonomy,
the choose-your-path block, the embedded pre-publish gate with inline
review procedure, and a triage table. For refinement beyond the template
this pairs with `great-skill-writer`. If it is not installed, install it
from https://github.com/ryan-minato/skills.git:

    npx skills add ryan-minato/skills --skill great-skill-writer

Done when: the generated SKILL.md contains no `{{...}}` placeholder and
its frontmatter `name` matches its directory name.

## Automation

Copy [assets/workflow-issue-labeler.yml](assets/workflow-issue-labeler.yml)
to `.github/workflows/issue-labeler.yml` and its configuration
[assets/issue-labeler-config.yml](assets/issue-labeler-config.yml) to
`.github/issue-labeler.yml` — NOT `.github/labeler.yml`, which belongs to
the PR labeler (`actions/labeler`); a collision breaks both.

Shipped automation uses first-party actions only (`github/*` or
`actions/*`) because workflow code runs with the repository's
permissions; add a third-party action only on explicit user opt-in.

Read [references/automation-recipes.md](references/automation-recipes.md)
when adding automation beyond the shipped labeler (stale handling,
auto-assign, form-completeness checks).

## Deliver

The new files are local until committed and pushed through the project's
normal git/PR flow — pushing is what publishes them, and that flow
carries its own review gates.

Done when: forms + config.yml + label plan (applied or handed to the
user) + generated project skill + labeler workflow and config all exist
locally and parse.

## Gotchas

- Issue forms and `config.yml` take effect only after they are merged to
  the repository's default branch; a feature branch shows nothing.
- `blank_issues_enabled: false` still shows a blank-issue option to users
  with write access; it only removes it for outside contributors.
- Issue-form `labels:` are applied without validation — a label that does
  not exist in the repository is dropped silently, with no error anywhere.
- Label colors are 6-digit hex WITHOUT `#` in gh and API contexts
  (`--color d73a4a`); the leading `#` shown in GitHub's web UI is not
  accepted there.
- MCP tool names have changed across github-mcp-server versions. If a tool
  named in a table is absent, list the github server's available tools and
  pick the same-purpose name; if none matches, fall back to the gh column.
