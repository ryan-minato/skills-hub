# Issue forms and template-chooser schema

Load condition: authoring or editing an issue form beyond the shipped
assets, or editing `.github/ISSUE_TEMPLATE/config.yml`.

Source of truth:
<https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/syntax-for-issue-forms>

## File placement

Issue forms are YAML files in `.github/ISSUE_TEMPLATE/` on the default
branch. Every `.yml`/`.yaml` file there except `config.yml` is treated as
a form and appears in the template chooser.

## Top-level keys

| Key | Required | Meaning |
|---|---|---|
| `name` | yes | Name shown in the chooser; must be unique across all templates in the repository (forms and legacy `.md` alike). |
| `description` | yes | Subtitle shown in the chooser. |
| `body` | yes | Array of form elements (below); must contain at least one non-`markdown` element. |
| `title` | no | Default issue title, e.g. `"[Bug]: "`. |
| `labels` | no | Labels applied on submission (YAML list or comma-separated string). Each label must already exist in the repository. |
| `assignees` | no | Usernames auto-assigned on submission. |
| `projects` | no | Projects (`OWNER/NUMBER`) the issue is added to; requires the submitter to have write access, silently skipped otherwise. |
| `type` | no | Organization-level issue type applied on submission. |

## Body elements

Every element has a `type`, an optional `id` (unique within the form;
letters, digits, `-`, `_` only — the field's key in the submitted data),
an `attributes` map, and — where noted — a `validations` map with
`required: true|false`.

| `type` | `attributes` | `validations` |
|---|---|---|
| `markdown` | `value` (required) — display-only text, not part of the submitted issue body. | none |
| `input` | `label` (required), `description`, `placeholder`, `value` (prefill). Single line. | `required` |
| `textarea` | `label` (required), `description`, `placeholder`, `value`, `render` (language name; wraps the response in a code block of that language). | `required` |
| `dropdown` | `label` (required), `description`, `options` (required; unique strings), `multiple` (allow multi-select), `default` (index into `options`; incompatible with `required`). | `required` |
| `checkboxes` | `label` (required), `description`, `options` — array of `{label, required}`; `required: true` on an option blocks submission until it is checked. | per-option `required` |

Notes:

- `label` values must be unique across the form's elements; if two match,
  give both elements distinct `id`s.
- Multi-line `value` and `placeholder` strings need YAML block scalars
  (`|` or `>`), or the form fails to parse and falls back to a blank
  issue.
- In the submitted issue, every answered element is rendered as an
  `### <label>` heading followed by the response — this is what
  body-scanning automation (completeness checks, regex labelers) sees.

## config.yml

Controls the template chooser. Lives at
`.github/ISSUE_TEMPLATE/config.yml`:

```yaml
blank_issues_enabled: false
contact_links:
  - name: Product support
    url: https://support.example.com
    about: Contact support for account or billing questions.
```

- `blank_issues_enabled` defaults to `true`. Setting `false` removes the
  blank-issue option for outside contributors; users with write access
  still see it.
- Each `contact_links` entry requires all of `name` (unique across
  entries), `url` (`http`/`https` only), and `about`. Links render at the
  bottom of the chooser and lead away from the issue flow.

## Legacy .md templates

Markdown templates in `.github/ISSUE_TEMPLATE/*.md` use YAML frontmatter
(`name`, `about`, `title`, `labels`, `assignees`) above a free-form body.
They cannot mark fields required or validate anything, so never use them
for new work; when touching an existing legacy template for any other
reason, migrate it to a form in the same change. A legacy template and a
form must not share the same `name` — the chooser requires unique names.
