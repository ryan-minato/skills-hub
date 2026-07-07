# Description templates — authoring beyond the shipped assets

## Naming and discovery

- Templates are markdown files in `.gitlab/issue_templates/`; the
  filename minus `.md` is the name shown in the issue form's "Choose a
  template" dropdown (`Bug.md` → "Bug").
- `Default.md` (filename is case-insensitive) pre-fills issues opened
  without choosing a template — GitLab ≥ 14.8, Free tier. It is this
  catalog's replacement for GitHub's `config.yml` blank-issue handling.
- Templates take effect only from the **default branch**; a feature
  branch shows nothing until merged.
- There is no forms schema and no required-field enforcement: prompts
  live in HTML comments (`<!-- ... -->`), which the web UI shows in the
  editor but drops from the rendered issue if left unedited. "Required"
  is convention plus the generated project skill's instructions, not a
  platform guarantee.

## Precedence of defaults (when several exist)

A Premium/Ultimate project can also set a default template in Settings
(Description templates), and groups/instances can host shared template
repositories. Precedence: the settings-based default wins over
`Default.md`; project templates and inherited group/instance templates
all appear in the dropdown. On Free self-managed instances, per-project
`.gitlab/issue_templates/` files — what this skill ships — are the whole
mechanism.

## Prefilling via URL

Link a specific template:

```
https://HOST/GROUP/PROJECT/-/issues/new?issuable_template=Bug
```

## Quick actions inside templates

Trailing quick-action lines execute when the issue is submitted, with
the submitter's permissions. Rules:

- One action per line, each on its own line, nothing else on the line.
- `/label ~"name"` with a label that does not exist is silently ignored
  — sync the taxonomy before shipping templates that reference it.
- Free-tier actions safe for templates: `/label`, `/assign`,
  `/milestone`, `/due`. Premium-gated: `/epic`, `/iteration`, `/weight`
  — they no-op on Free instances, so include them only for
  Premium-confirmed projects.
- Users who edit the template text before submitting can delete the
  lines; quick actions are a default, not enforcement.
