# PR recipes

Operations not covered by the main table in SKILL.md. Use the column (MCP
or gh) chosen in "Choose your path"; `O/R` and `N` come from "Identify
the repository".

## Update the PR branch with its base

Brings the PR branch up to date with `BASE` when GitHub reports it is
behind.

- MCP: the capability that updates a PR's branch from its base.
- gh: `gh pr update-branch N -R O/R`

## Add or remove human reviewers

- MCP: the PR-update capability's reviewers parameter.
- gh: `gh pr edit N -R O/R --add-reviewer USER --remove-reviewer USER2`

## Link issues

Write `Closes #N` (one line per issue) in the PR body and update the body
via the gate + body file — there is no separate linking API worth using.
Editing the body changes public text, so the Pre-publish gate applies.

## Edit title or body

- MCP: the PR-update capability (title, body).
- gh: `gh pr edit N -R O/R --title "T" --body-file BODY.md`

Both change public text — the Pre-publish gate applies, and the body must
keep following the repository's PR template.

## Revert a merged PR

gh only (no MCP capability): `gh pr revert N -R O/R`. This creates a
revert PR; report its URL to the user.

## Check out a PR locally

`gh pr checkout N -R O/R` — a read-only convenience for inspecting the
changes with local tools before commenting or reviewing.
