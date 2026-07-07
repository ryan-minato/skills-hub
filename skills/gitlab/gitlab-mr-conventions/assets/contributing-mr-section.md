## Merge requests

- Branch from `{{DEFAULT_BRANCH}}` and name branches
  `{{BRANCH_PREFIX}}<short-slug>` (for example `feat/rate-limit-login`).
- Keep each MR small and single-purpose: one logical change per MR, and
  unrelated fixes in their own MRs. Small MRs get reviewed faster and
  reverted more safely.
- Fill in every section of the MR template. The `mr-checklist` CI job
  fails any MR that drops a required section or leaves the security
  checkbox unchecked.
- All pipeline jobs must be green before you request review; do not ask
  reviewers to look at a red pipeline.
- Use `Draft:` (the Mark as draft toggle) until the MR is ready for
  review.
- MRs are merged by {{MERGE_METHOD}} (squash: {{SQUASH_OPTION}}). Write
  the MR title so it works as the resulting commit message on
  `{{DEFAULT_BRANCH}}`.
- Review expectations: {{REVIEW_RESPONSE_EXPECTATION}} (for example
  "a maintainer responds within two business days; the reviewer merges
  once approved and green").
