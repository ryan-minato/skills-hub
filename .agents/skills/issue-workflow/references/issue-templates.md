# Issue and Comment Templates

Templates for Linear issues and milestone comments created by the
`issue-workflow` skill. Fill every placeholder; drop a section only when it
is genuinely empty (say so rather than leaving it blank). All content is
written in English.

## Label mapping

Choose the label from the dominant change intent, mirroring the
conventional-commit type the work will produce:

| Commit type(s) | Label |
|---|---|
| `feat` | Feature |
| `fix` | Bug |
| `refactor`, `perf` | Improvement |
| `docs` | Docs |
| `chore`, `ci`, `build`, `test` | Chore |

A distributable skill is installed behavior, even when its source is Markdown.
Classify a new capability as `feat`, a behavior-preserving restructure as
`refactor`, and a correction to wrong, misleading, overly restrictive, or
overly permissive behavior as `fix`. Test `fix` first: correction takes
precedence even when the result is an improvement. Use `docs` only for
supporting documentation that does not change the installed skill, then choose
the issue label from the resulting type.

A parent issue takes the label of its overall intent; sub-issues are
labelled individually by their own intent.

## Parent issue

Title: short imperative summary of the overall change.

```markdown
## Goal

<What the group of changes achieves, in one or two sentences.>

## Context

<Why this is needed now: the gap, bug report, or request behind it.>

## Scope

**In:**
- <Deliverable or area covered.>

**Out:**
- <Adjacent work explicitly not covered.>

## Sub-issues

- [ ] <Sub-issue title, one per independently completable unit>

## Acceptance criteria

- <Observable condition that must hold when the PR merges.>
```

Keep the Sub-issues checklist in sync as sub-issues are added or completed.

## Sub-issue

Title: short imperative summary of the unit.

```markdown
## Goal

<What this unit delivers.>

## Steps

1. <Ordered step.>

## Done criteria

- <Condition that lets this sub-issue be closed independently.>
```

## Standalone issue

For a single coherent change with no sub-issues.

```markdown
## Goal

<What the change achieves.>

## Context

<Why it is needed.>

## Steps

1. <Ordered step.>

## Acceptance criteria

- <Observable condition that must hold when the PR merges.>
```

## Milestone comment

Posted on the issue owning the completed scope (see SKILL.md step 3).

```markdown
**Done:**
- <What was completed, with file paths where useful.>

**Remaining:**
- <What is still open in this issue's scope, or "Nothing".>

**Deviations & notes:**
- <Departures from the plan, discoveries, follow-ups filed — or "None".>
```
