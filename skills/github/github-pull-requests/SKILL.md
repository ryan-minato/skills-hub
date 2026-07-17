---
name: github-pull-requests
description: >
  GitHub pull request operations — open, comment on, monitor, and merge PRs. Use when
  the request names a PR — "open a PR", "comment on the PR", "merge #N", "mark it
  ready" — or a GitHub PR URL is the material at hand; when submitting a finished
  branch for review or getting changes merged without saying PR; when checking a PR's
  CI ("did the checks pass", "why is CI red") or reading its failed-job logs; when
  reading or replying to review threads, including Copilot code review; or when
  editing one PR's labels or milestone. Authoring PR templates and review automation
  belongs to github-pr-conventions; investigating PRs of a repository you are not
  contributing to belongs to github-repo-research; GitLab merge requests to
  gitlab-merge-requests.
license: Apache-2.0
---

# GitHub Pull Requests

Operate pull requests: create, comment, read state and diff, read check
results and failed-job logs, manage draft state, edit metadata, merge, and
work with review threads including Copilot code review. For issue work use
`github-issues`; for milestone, label, and project-board lifecycle use
`github-planning`; for read-only research across a repository use
`github-repo-research`; for authoring PR templates and automation use
`github-pr-conventions`.

## Choose your path (do this first, once per session)

1. Look at the tools available in this session. If a connected MCP server
   provides GitHub tools for the work this skill covers (each tool's
   description states its purpose; names vary across server versions), use
   the **MCP** column of every table below, picking the tool whose
   description matches the row's capability.
2. Otherwise run `gh auth status`. If it exits 0, use the **gh** column.
3. Otherwise stop and tell the user GitHub tooling is not set up. This skill
   pairs with `github-tooling-setup`. If it is not installed, install it from
   https://github.com/ryan-minato/skills.git:

       npx skills add ryan-minato/skills --skill github-tooling-setup

4. Use one column for the whole task. Never mix MCP and gh in one operation.

## Identify the repository

Run `git remote get-url origin`. The owner/repo pair is the path right
after the host, with any trailing `.git` stripped. If there is no origin
remote, or the user named a different repository, use that instead.
Substitute the pair wherever the tables show `O/R` (gh: `-R O/R`; MCP: the
owner and repo parameters).

## Match the project's conventions (before any create)

Before creating anything, discover what the repository already defines and
use it — never invent parallel structure:

| Artifact | How to check |
|---|---|
| PR template(s) | `.github/PULL_REQUEST_TEMPLATE.md` (also `PULL_REQUEST_TEMPLATE.md` at root or in `docs/`), or multiple under `.github/PULL_REQUEST_TEMPLATE/` — if one exists, the PR body follows its structure section by section |
| Contributing rules | `CONTRIBUTING.md` (root, `.github/`, or `docs/`) — PR titling, base-branch, and review rules stated there are binding |
| Labels | `gh label list -R O/R`, or the MCP tool that lists repository labels |
| Open milestones | `gh api repos/O/R/milestones -q '.[].title'` |

If a project-level convention skill or an AGENTS.md conventions section
covers this task, follow it over this skill's defaults.
Done when: each artifact was checked and the draft uses the repository's
existing structures (or the user approved new ones).

## Authoring defaults

Write all published text — titles, bodies, comments, notes — as
professional, concise prose. Default to English unless the user or the
project's own conventions call for another language. State facts and
requests directly; no filler, and no emojis unless the project's existing
content uses them. The project's templates and conventions win over these
defaults.

## Pre-publish gate (mandatory)

Everything you send becomes public the moment the call succeeds: title, body,
every comment, labels, commit messages, the full diff, attachment contents,
and the branch name. Creating a PR publishes every commit message and the
complete diff of `BASE...HEAD`, not just the description. Before ANY call
that creates or edits public content:

1. Write the exact outgoing content to a scratch directory: title, body,
   each comment or review body, `git log BASE..HEAD --format=full >
   commits.txt`, `git diff BASE...HEAD > diff.patch`, and any attachments.
2. Run the review procedure in [references/publish-review.md](references/publish-review.md)
   over that directory. Read that file every time — do not review from
   memory.
3. Publish only after the verdict is exactly `SAFE TO PUBLISH: YES`. On
   `NO`, fix every finding, rebuild the files from the fixed content, and
   review again. Never edit-and-publish without re-review.

Never publish unreviewed content. Only the user may skip this gate,
explicitly; record the skip in your summary.
Done when: a `SAFE TO PUBLISH: YES` verdict exists for the exact content
being sent.

In this skill the gate applies to: create, comment, review submission and
replies, and any edit that changes public text or metadata. Pure reads,
draft/ready flips, and merges of already-reviewed PRs carry no new content
and skip it.

## Operations

Use the column chosen above. Send multi-line bodies through a file, never
an inline shell string (`--body-file FILE` for gh; fill the MCP body
parameter from the file).

| Task | MCP capability | gh command |
|---|---|---|
| Create PR | create a pull request (base, head, title, body; optional draft, reviewers) | `gh pr create -R O/R --base BASE --head BRANCH --title "TITLE" --body-file BODY.md [--draft]` |
| Comment | comment on an issue or PR (PRs share issue numbering) | `gh pr comment N -R O/R --body-file COMMENT.md` |
| Read PR | read PR details | `gh pr view N -R O/R --json number,title,state,isDraft,mergeable,reviewDecision,url` |
| Read diff | read a PR's diff | `gh pr diff N -R O/R` |
| Check results | read a PR's status rollup or check runs | `gh pr checks N -R O/R` |
| Close / reopen | update a PR's state | `gh pr close N -R O/R` / `gh pr reopen N -R O/R` |
| Draft → ready | update a PR's draft flag | `gh pr ready N -R O/R` |
| Edit labels / milestone | update a PR's metadata | `gh pr edit N -R O/R --add-label L --remove-label M --milestone "TITLE"` |
| Merge | merge a PR with an explicit method | `gh pr merge N -R O/R --squash` |

The default merge method is squash, because linear history is the safer
default — deviate only when the project's convention says otherwise.
After create and comment operations, report the returned URL to the user.
Done when: the URL is reported.

- Read [references/checks-and-logs.md](references/checks-and-logs.md)
  when a check is failing and you need the logs.
- Read [references/reviews-and-copilot.md](references/reviews-and-copilot.md)
  when reading or replying to review threads, submitting a review, or
  requesting a Copilot code review.
- Read [references/pr-recipes.md](references/pr-recipes.md) when the task
  is not in the table above (update branch, reviewers, linked issues,
  revert, checkout).

## Gotchas

- If no available MCP tool's description matches a row's capability, that
  capability is missing from the connected server — use the gh column for
  that row instead of guessing.
- `gh pr checks` exits with code 8 while checks are still pending — that is
  not an error; wait and re-run, or use `--watch`.
- PRs and issues share one number space: the issue-comment capability
  comments on a PR, and a bare `#N` can refer to either.
- A PR created from a fork needs `--head FORK_OWNER:BRANCH` (MCP: the same
  `owner:branch` form in the head parameter).
- Labels and milestones set on a PR must already exist in the repository —
  the conventions section above exists so this never surprises you.
- Never dump a full CI log into context — full run logs can be megabytes.
  Follow the failed-only + tail rule in references/checks-and-logs.md.
