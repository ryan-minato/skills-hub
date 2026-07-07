# Projects v2 via GraphQL

Load condition: the task has no `gh project` subcommand. Everything here
is `gh api graphql` (gh path; there is no MCP capability for Projects).
IDs (`PROJECT_ID`, `FIELD_ID`, `ITEM_ID`, option ids) come from
`scripts/project_fields.py` or the `--format json` output of the list
commands.

## Query items with their field values

`gh project item-list` returns every field; for large projects, query only
what you need and page with `after`:

```bash
gh api graphql -f query='
query($project: ID!, $cursor: String) {
  node(id: $project) {
    ... on ProjectV2 {
      items(first: 50, after: $cursor) {
        pageInfo { hasNextPage endCursor }
        nodes {
          id
          content { ... on Issue { number title url state } }
          fieldValueByName(name: "Status") {
            ... on ProjectV2ItemFieldSingleSelectValue { name }
          }
        }
      }
    }
  }
}' -f project=PROJECT_ID
```

## Create a draft item

`gh project item-create NUMBER --owner OWNER --title "T" --body "B"` does
this on the CLI; the GraphQL form, when you already hold the project id:

```bash
gh api graphql -f query='
mutation($project: ID!, $title: String!, $body: String) {
  addProjectV2DraftIssue(input: {projectId: $project, title: $title, body: $body}) {
    projectItem { id }
  }
}' -f project=PROJECT_ID -f title="TITLE" -f body="BODY"
```

Draft titles and bodies are visible to everyone who can see the project —
the pre-publish gate applies.

## Convert a draft item to a real issue

No CLI subcommand. `REPO_ID` is `gh repo view O/R --json id -q .id`; the
draft's `DraftIssue` id is `content.id` in the item-list JSON (not the
item id):

```bash
gh api graphql -f query='
mutation($draft: ID!, $repo: ID!) {
  convertProjectV2DraftIssueItemToIssue(input: {itemId: $draft, repositoryId: $repo}) {
    item { id content { ... on Issue { url } } }
  }
}' -f draft=ITEM_ID -f repo=REPO_ID
```

Conversion files a public issue in that repository — gate first.

## Remove an item from the project

`gh project item-delete NUMBER --owner OWNER --id ITEM_ID` covers this on
the CLI; unlike item-archive it removes the item permanently (the
underlying issue/PR is untouched). Prefer archive unless the user asked
for removal.

## Iteration ids

`gh project field-list NUMBER --owner OWNER --format json` includes, for
an iteration field, `configuration.iterations` — each with `id`,
`title`, and `startDate`. Those `id` values feed `item-edit
--iteration-id`. Past iterations move to `configuration.completedIterations`.
