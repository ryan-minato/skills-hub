# Issue automation recipes (first-party actions only)

Load condition: adding issue automation beyond the shipped labeler
workflow.

All recipes use first-party actions (`actions/*`, `github/*`) because
workflow code runs with the repository's permissions. Any label a
workflow applies or filters on must already exist in the repository.

## Stale issues (actions/stale)

Add a `status/stale` label to the taxonomy and sync it first, then:

```yaml
name: Stale issues
on:
  schedule:
    - cron: "17 3 * * *"
permissions:
  issues: write
jobs:
  stale:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/stale@v10
        with:
          days-before-issue-stale: 60
          days-before-issue-close: 14
          stale-issue-label: status/stale
          exempt-issue-labels: status/blocked,status/help-wanted
          stale-issue-message: >
            This issue has had no activity for 60 days and will be closed
            in 14 more unless it is updated.
          days-before-pr-stale: -1
          days-before-pr-close: -1
```

The `-1` settings keep the workflow issue-only.

## Form-completeness check (actions/github-script)

Issue forms render each answered field as an `### <label>` heading, so a
script can verify required sections on submission (they go missing when a
write-access user files a blank issue). Workflow scaffold: trigger
`on: issues: types: [opened]`, `permissions: issues: write`, one
`ubuntu-latest` job with this single step:

```yaml
      - uses: actions/github-script@v7
        with:
          script: |
            const required = ["### Steps to reproduce", "### Expected behavior"];
            const body = context.payload.issue.body || "";
            const missing = required.filter((h) => !body.includes(h));
            if (missing.length === 0) return;
            await github.rest.issues.createComment({
              ...context.repo,
              issue_number: context.issue.number,
              body: `This issue is missing required sections: ${missing.join(", ")}. Please edit it to add them.`,
            });
            await github.rest.issues.addLabels({
              ...context.repo,
              issue_number: context.issue.number,
              labels: ["status/needs-triage"],
            });
```

Keep the `required` list aligned with the field labels of the forms
actually shipped in `.github/ISSUE_TEMPLATE/`.

## Auto-assign round-robin (actions/github-script)

Same scaffold as the completeness check, with this step instead
(replace the usernames with real maintainers agreed with the user):

```yaml
      - uses: actions/github-script@v7
        with:
          script: |
            const assignees = ["alice-maintainer", "bob-maintainer"];
            const pick = assignees[context.issue.number % assignees.length];
            await github.rest.issues.addAssignees({
              ...context.repo,
              issue_number: context.issue.number,
              assignees: [pick],
            });
```

## Third-party actions

Marketplace actions outside `actions/*` and `github/*` run with the same
repository permissions as first-party ones. Add one only on explicit user
opt-in, and pin it to a full commit SHA rather than a tag.
