## Pull requests

- Branch from `{{DEFAULT_BRANCH}}` and name branches
  `{{BRANCH_PREFIX}}<short-slug>` (for example `feat/rate-limit-login`).
- Keep each PR small and single-purpose: one logical change per PR, and
  unrelated fixes in their own PRs. Small PRs get reviewed faster and
  reverted more safely.
- Fill in every section of the PR template. The checklist workflow fails
  any PR that drops a required section or leaves the security checkbox
  unchecked.
- All CI checks must be green before you request review; do not ask
  reviewers to look at a red build.
- PRs are merged by {{MERGE_METHOD}}. Write the PR title so it works as
  the resulting commit message on `{{DEFAULT_BRANCH}}`.
- Review expectations: {{REVIEW_RESPONSE_EXPECTATION}} (for example
  "a maintainer responds within two business days; the reviewer merges
  once approved and green").
