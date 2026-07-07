# Iterations and cadences (Premium)

Iterations belong to **iteration cadences** at group level. A cadence
either auto-schedules its iterations (GitLab creates and rolls them on a
fixed duration) or is manual. There is no REST or glab write surface —
creating and editing cadences and manual iterations is GraphQL only.

Run mutations through `glab api graphql`, with the query in a file:

```bash
glab api graphql -f query=@mutation.graphql
```

## Create a cadence

```graphql
mutation {
  iterationCadenceCreate(input: {
    groupPath: "GROUP",
    title: "Sprint cadence",
    automatic: true,
    active: true,
    startDate: "2026-07-06",
    durationInWeeks: 2,
    iterationsInAdvance: 4
  }) {
    iterationCadence { id title }
    errors
  }
}
```

`automatic: false` creates a manual cadence whose iterations you add
yourself. `iterationCadenceUpdate` and `iterationCadenceDestroy` take the
cadence's global id (`gid://gitlab/Iterations::Cadence/N`).

## Create an iteration (manual cadences only)

```graphql
mutation {
  iterationCreate(input: {
    groupPath: "GROUP",
    iterationsCadenceId: "gid://gitlab/Iterations::Cadence/N",
    title: "Sprint 12",
    startDate: "2026-07-06",
    dueDate: "2026-07-17"
  }) {
    iteration { id webUrl }
    errors
  }
}
```

Adding iterations to an **automatic** cadence is rejected — the cadence
owns the schedule.

## Why listed iterations have null titles

Auto-scheduled iterations are unnamed by design; clients are expected to
render them by date range. When matching "the current sprint", filter by
`state=current` or by dates, never by title.
