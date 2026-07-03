# Sync And Entropy Skeletons

Copy the shape that matches the chosen mechanism. Workflow sections paste
into the entrypoint or a workflow document; skill skeletons become a project
skill's SKILL.md.

## Sync workflow section

````markdown
## [Sync Concern]

Run this when [source-of-truth change].

**Source of truth:** [file, command, tool, or reachable endpoint]
**Dependent artifacts:** [files, sections, skills, or endpoints]

1. Inspect the source of truth.
2. Update each dependent artifact to reflect it.
3. Remove stale or duplicate instructions from [locations].
4. Verify links, commands, and trigger descriptions still hold.

Unclear ownership or conflicting sources require user confirmation before
editing.
````

## Sync project skill

````markdown
---
name: [concern]-sync
description: >
  Keep [dependent harness artifacts] aligned with [source of truth]. Use
  when [the specific files, endpoints, commands, or conventions] change.
---

# [Concern] Sync

## Source Of Truth

[Identify the maintained source.]

## Dependent Artifacts

- [Harness file, skill, workflow entry, or reachable endpoint.]

## Workflow

1. Inspect the source of truth.
2. Compare each dependent artifact against it.
3. Update stale or missing content.
4. Remove duplicated or conflicting guidance.
5. Verify links, commands, and validation paths.

## Gotchas

- [Non-obvious drift mode for this concern.]
````

## Entropy review workflow section

````markdown
## Harness Entropy Review

Run this [periodic trigger, release trigger, or on repeated drift
findings].

1. Check entrypoints for stale paths, sections past the length budget, and
   missing pointers.
2. Check that every referenced file, skill, and endpoint still exists and
   is still reachable.
3. Check for duplicated or contradictory rules across harness files.
4. Check for components nothing triggers anymore, and constraints thicker
   than current work justifies.
5. Report keep/update/remove findings before editing anything uncertain.
6. After changes, verify links, length budgets, and validation commands.
````

## Entropy review project skill

````markdown
---
name: harness-entropy-review
description: >
  Find stale, duplicated, contradictory, invisible, or excessive harness
  content. Use when reviewing harness health in a long-lived project, after
  repeated drift findings, or before a major harness cleanup.
---

# Harness Entropy Review

## Scan Scope

- [Entrypoints.]
- [Knowledge files or reachable endpoints.]
- [Project skills.]
- [Workflow and validation guidance.]

## Workflow

1. Identify stale references, invalid paths, and dead commands.
2. Identify duplicated or contradictory instructions.
3. Identify content no pointer reaches.
4. Identify components without a trigger, and constraints without a current
   justification.
5. Report findings with keep/update/remove recommendations.
6. Apply only approved, source-backed, unambiguous changes.
7. Verify links, length budgets, and validation commands.

## Gotchas

- Prefer reporting an uncertain removal over deleting a possibly valid
  constraint.
````
