# Automation recipes

Details for customizing the shipped workflows and adding more PR
automation. The first-party-only policy applies here too: `actions/*` and
`github/*` actions only, anything else needs explicit user opt-in.

## actions/labeler config syntax (v6)

`.github/labeler.yml` maps label names to match rules. Every top-level key
must be an existing repository label. v6 uses the syntax introduced in v5:

```yaml
label-name:
  - changed-files:
      # Label if ANY changed file matches ANY of these globs.
      - any-glob-to-any-file: ['src/**', 'lib/**']
      # Label only if EVERY changed file matches EVERY of these globs.
      - all-globs-to-all-files: ['docs/**']
  # Regex lists against branch names (anchored patterns recommended).
  - head-branch: ['^feat/', '^feature/']
  - base-branch: ['^release/']
```

- Multiple entries under one label are OR'ed: any matching entry applies
  the label. To AND conditions, nest them under an `all:` key.
- `any-glob-to-any-file` is the permissive matcher (typical for area
  labels); `all-globs-to-all-files` is the strict one (label only when the
  whole PR is inside a path).
- `sync-labels: true` removes a label the config once applied when the PR
  no longer matches (for example after a force-push drops the docs
  change). The shipped workflow uses `false` so manually added labels are
  never fought over; turn it on only if labels must strictly mirror paths.

## Checklist workflow variants

Add these to the existing `actions/github-script@v7` script in
`.github/workflows/pr-checklist.yml`, after the heading check.

Require a linked issue in the PR body:

```javascript
if (!/(close[sd]?|fix(e[sd])?|resolve[sd]?) #\d+/i.test(body)) {
  core.setFailed('PR body must link its issue, for example "Closes #123".');
  return;
}
```

Semantic PR title validation — pairs with squash merges, where the PR
title becomes the commit message on the default branch:

```javascript
const title = context.payload.pull_request.title || '';
const semantic = /^(feat|fix|docs|chore|refactor|perf|test|build|ci)(\(.+\))?!?: .+/;
if (!semantic.test(title)) {
  core.setFailed('PR title must follow Conventional Commits, for example "feat(auth): add rate limit".');
  return;
}
```

The popular marketplace action for semantic PR titles is third-party;
prefer the inline script above, and use that action only on explicit
user opt-in.

## Stale PR handling

`actions/stale@v10`, scoped to PRs only so issue lifecycle stays with the
issue-conventions tooling:

```yaml
name: Stale PRs
on:
  schedule:
    - cron: '17 3 * * *'
permissions:
  pull-requests: write
jobs:
  stale:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/stale@v10
        with:
          days-before-pr-stale: 30
          days-before-pr-close: 14
          stale-pr-label: stale
          exempt-pr-labels: pinned,security
          days-before-issue-stale: -1   # PRs only; leave issues alone
```
