# Discussions via gh (GraphQL)

gh has no first-class `gh discussion` command, so every Discussions read
goes through `gh api graphql`. Each block below is complete and
copy-paste ready: replace `O`/`R` (and `NUMBER`/`TEXT`) with real values.
Pass variables with `-F` and the query with `-f query='...'`.

Keep the field sets as small as the task allows — every field you select
comes back in the response and lands in agent context.

## List recent discussions

The 20 most recently updated discussions, newest first.

```bash
gh api graphql -F owner='O' -F name='R' -f query='
query($owner: String!, $name: String!) {
  repository(owner: $owner, name: $name) {
    discussions(first: 20, orderBy: {field: UPDATED_AT, direction: DESC}) {
      nodes {
        number
        title
        category { name }
        author { login }
        updatedAt
        url
      }
    }
  }
}'
```

## List discussion categories

Category ids and names, needed to interpret or filter listings.

```bash
gh api graphql -F owner='O' -F name='R' -f query='
query($owner: String!, $name: String!) {
  repository(owner: $owner, name: $name) {
    discussionCategories(first: 25) {
      nodes { id name description }
    }
  }
}'
```

## Read one discussion (with comments)

Full body plus the first 30 comments of discussion NUMBER.

```bash
gh api graphql -F owner='O' -F name='R' -F number=NUMBER -f query='
query($owner: String!, $name: String!, $number: Int!) {
  repository(owner: $owner, name: $name) {
    discussion(number: $number) {
      title
      body
      author { login }
      category { name }
      url
      comments(first: 30) {
        nodes { author { login } body createdAt }
      }
    }
  }
}'
```

## Paginated listing (more than 100 items)

For `--paginate` to work, the query must declare `$endCursor: String`,
pass it as `after: $endCursor`, and select
`pageInfo { hasNextPage endCursor }`; gh then follows the cursor until
the last page.

```bash
gh api graphql --paginate -F owner='O' -F name='R' -f query='
query($owner: String!, $name: String!, $endCursor: String) {
  repository(owner: $owner, name: $name) {
    discussions(first: 100, after: $endCursor,
                orderBy: {field: UPDATED_AT, direction: DESC}) {
      nodes { number title updatedAt url }
      pageInfo { hasNextPage endCursor }
    }
  }
}'
```

## Search discussions

Full-text search scoped to one repository; TEXT is the search phrase.

```bash
gh api graphql -f query='
query {
  search(query: "repo:O/R TEXT", type: DISCUSSION, first: 20) {
    nodes {
      ... on Discussion { number title url }
    }
  }
}'
```
