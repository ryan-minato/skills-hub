# Knowledge File Skeletons

Copy the matching skeleton into a new knowledge file, fill the placeholders,
and delete sections without content. Every new file needs a when-to-read
pointer in the entrypoint.

## Goals

````markdown
# Goals

Load this when [precise trigger condition for goal, requirement, or
behavior work].

## Source Of Truth

[Name the maintained source, or state that this file is the source of truth.]

## Goals

- [Goal or requirement agents must preserve.]

## Non-Goals

- [Out-of-scope behavior or constraint.]

## Acceptance Signals

[How agents can verify the goal is still being met.]
````

## Plan

````markdown
# Plan

Load this when [precise trigger condition for planning or status work].

## Source Of Truth

[Name the maintained source, or state that this file is the source of truth.]

## Current Direction

- [Current planned work, milestone, or decision.]

## Open Questions

- [Question or dependency.]

## Exit Criteria

[How agents can tell the plan is complete or stale.]
````

## Quality

````markdown
# Quality Control

Load this when [precise trigger condition for quality, validation, or
review work].

## Source Of Truth

[Name the maintained source, or state that this file is the source of truth.]

## Quality Rules

- [Rule agents must follow.]

## Validation

| Check | Command |
|---|---|
| [What this validates] | `[command]` |

## Failure Guidance

[How agents should interpret common failures and what to inspect next.]
````

## Workflow

````markdown
# Workflow

Load this when [precise trigger condition for this workflow].

## Source Of Truth

[Name the maintained source, or state that this file is the source of truth.]

## Steps

1. [Step.]
2. [Step.]
3. [Verification or handoff step.]

## Human Handoff

[What remains human-owned, and what agents may do.]
````

## Reference Index

````markdown
# References

Load this when [precise trigger condition for consulting reference
material].

## Source Of Truth

[Name the maintained source, or state that this file is the source of truth.]

## Reference Index

| Topic | Read |
|---|---|
| [Trigger or topic] | [File, section, or reachable endpoint] |

## Local Notes

- [Short agent-facing note on how to use the referenced material.]
````
