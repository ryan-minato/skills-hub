# Using the repository's issue templates and forms

Load condition: `.github/ISSUE_TEMPLATE/` (or a bare
`.github/ISSUE_TEMPLATE.md`) exists and you are about to create an issue.

`gh issue create` and the MCP create capability both take a plain body —
neither applies a template for you in non-interactive use. You apply the
template by constructing the body to match it.

## 1. Inventory the templates

```bash
gh api repos/O/R/contents/.github/ISSUE_TEMPLATE -q '.[].name'
```

(or `ls .github/ISSUE_TEMPLATE/` in a local checkout). Files ending `.md`
are markdown templates; files ending `.yml`/`.yaml` except `config.yml`
are issue forms. `config.yml` may declare `blank_issues_enabled: false` —
then a template **must** be used — and `contact_links` that redirect some
reports elsewhere; honor both.

## 2. Pick the matching template

Read each candidate's frontmatter: `name` and `about` (markdown) or
`name` and `description` (form) say what it is for. Pick the one matching
the user's report type (bug, feature, ...). If several fit, ask the user.
If none fits and blank issues are enabled, draft a free-form body.

## 3. Draft the body against it

**Markdown template**: take the file's body below the frontmatter verbatim
as the scaffold and fill every section; delete only sections the template
itself marks optional. Apply frontmatter `labels`, `assignees`, and
`title` prefix to the create call (labels still must exist in the repo).

**Issue form (YAML)**: mirror the form's structure in markdown — for each
`body:` element of type `textarea` or `input`, emit its `label` as a
`### Heading` followed by the answer; for `dropdown`, the chosen option;
for `checkboxes`, a `- [x]` list. Skip `markdown` elements (display-only).
Respect `validations.required: true` — a required field with no answer
means asking the user, not omitting the heading. Apply top-level `labels`,
`assignees`, and `title` prefix to the create call.

This mirrors what the web form would submit, so triage automation keyed to
those headings keeps working.

## 4. Then continue in SKILL.md

The drafted body goes through the pre-publish gate and the normal create
row. Done when: the created issue's body renders every template section
with real content and no placeholder text remains.
