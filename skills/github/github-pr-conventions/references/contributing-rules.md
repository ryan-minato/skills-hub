# Contributing rules for pull requests

Deeper guidance to adapt into `CONTRIBUTING.md` when the shipped
"Pull requests" section is not enough. Pick one convention per topic and
write it down as a rule; listing alternatives in CONTRIBUTING.md moves
the argument into every PR.

## Branch naming

Recommended default: `<type>/<short-slug>`, where `<type>` mirrors
conventional-commit types (`feat`, `fix`, `docs`, `chore`, `refactor`,
`perf`, `test`, `build`, `ci`) and the slug is two to five lowercase,
hyphenated words:

    feat/rate-limit-login
    fix/null-avatar-crash
    docs/api-error-codes

This scheme sorts related work together, states intent before the diff is
opened, and pairs naturally with squash merges whose commit titles use the
same types. Deviate only if the team already uses another scheme
consistently (for example `<username>/<slug>`) — consistency beats the
specific format.

## Merge strategy

Enable exactly one merge method in the repository settings and state it in
CONTRIBUTING.md; offering several makes history style depend on who clicked
the button.

- **Squash — the recommended default.** One commit per PR keeps the default
  branch linear and makes every change revertable as a single unit. The
  PR's internal commits are discarded, so the PR title must be written to
  stand alone as the final commit message.
- **Rebase.** Preserves each commit from the PR without merge noise, which
  suits stacked-PR workflows where every commit is independently
  meaningful. It demands that contributors keep every intermediate commit
  clean and buildable, which most teams do not enforce.
- **Merge commit.** Records the exact integration point and keeps full
  branch history, which release trains merging long-lived branches need.
  It makes history non-linear, so `git log` and `git bisect` get harder to
  read.

Deviate from squash only for stacked-PR workflows (rebase) or release
trains (merge commits).

## Review expectations

Write down three things so contributors know what happens after they open
a PR:

- What reviewers check: correctness of the change, tests that would catch
  a regression, documentation for changed behavior, and that the diff
  contains only the stated change — not style preferences a formatter
  could enforce.
- Response-time norm: a placeholder to fill per team, for example
  "a maintainer responds within {{REVIEW_RESPONSE_DAYS}} business days".
  An explicit norm prevents both silent staleness and hourly pings.
- Who merges: the recommended default is that the reviewer merges once the
  PR is approved and green — the author may have local follow-ups pending,
  and the reviewer's merge confirms nothing was left unresolved.

## Draft pull requests

Open a PR as a draft when the branch is pushed before the work is
review-ready: CI runs and the direction is visible, but nobody is asked to
spend review time yet. Mark it "Ready for review" only when every template
section is filled and checks are green; reviewers should be able to treat
a non-draft PR as a request for their time.

## Keeping PRs reviewable

Aim for at most roughly 400 changed lines per PR — beyond that, review
quality drops measurably and turnaround stretches. Split larger work into
a sequence of PRs that each stand alone (refactor first, behavior change
second), and put mechanical churn such as renames, moves, and formatting
in their own PRs so reviewers can skim them separately from logic changes.
