# Contributing rules — full guidance

For filling and extending the CONTRIBUTING "Merge requests" section
beyond the shipped asset.

## Branch naming

`<type>/<short-slug>` with types mirroring the commit convention
(`feat/`, `fix/`, `docs/`, `chore/`). Consistent prefixes make branch
lists scannable and enable prefix-based automation later.

## Merge method and squash

GitLab sets both per project (Settings > Merge requests), readable via
`glab api projects/:fullpath` as `merge_method` and `squash_option`:

| `merge_method` | Meaning | History shape |
|---|---|---|
| `merge` | Merge commit | Full branch topology preserved |
| `rebase_merge` | Merge commit with semi-linear history | Every MR rebased first; merge commits remain |
| `ff` | Fast-forward only | Strictly linear; no merge commits |

`squash_option` is one of `never`, `always`, `default_on`, `default_off`.
Recommended default for review-oriented teams: `ff` (or `merge`) with
`squash_option: default_on` — one commit per MR whose message is the MR
title, which is why the CONTRIBUTING text asks for commit-quality MR
titles. State the project's actual settings in CONTRIBUTING; pick ONE
method and stop — mixed strategies make history unreadable.

## Draft workflow

`Draft:` title prefix marks work in progress; manage it with
`--draft`/`--ready` flags or the `/draft` and `/ready` quick actions,
never by editing the title. With "Pipelines must succeed" enabled, draft
MRs additionally cannot merge until marked ready.

## Approvals and CODEOWNERS (tier-gated)

- **Free**: approvals exist but are informational — anyone eligible can
  approve, nothing is enforced. The CONTRIBUTING text carries the review
  rules ("one maintainer approval before merge"), socially enforced.
- **Premium/Ultimate**: required approval rules (Settings > Merge
  requests > Approvals), prevent-author-approval, and CODEOWNERS
  enforcement. The CODEOWNERS file lives at `.gitlab/CODEOWNERS`,
  `docs/CODEOWNERS`, or the repo root (first found wins); on Free the
  file is inert — do not ship one as if it enforced anything.

## Review-size guidance

Reviewers do their best work under ~400 changed lines. Ask contributors
to split larger changes into stacked MRs; the reviewer's first question
on an oversized MR should be "can this split?", not a line-by-line
read.
