# Advanced Autonomy (L3 And L4)

Read this when the user asks for capabilities above L2 on the maturity
ladder in SKILL.md — a self-maintaining harness, persistent memory,
unattended operation, autonomous task routing, failure-driven knowledge
updates, or multiple agent roles — or when project evidence makes such an
upgrade worth proposing. Treat every precondition below
as missing until verified; when any is missing, design the best single-agent
L0–L2 harness instead and document what must change before upgrading.

## Preconditions for L3

- Isolation and approval boundaries that make unattended operation safe.
- Durable memory in a location agents can read and write across sessions.
- Validation strong enough to catch harness drift, not just code defects.
- Explicit rules for what agents may change without review, with approval
  and rollback paths for everything else.
- An audit mechanism: what changed, why, triggered by what.

Ask the user before granting agents authority to change their own harness
or write to external systems; these are decisions no evidence in the
repository can substitute for.

## Failure-driven feedback loops

At L3, agent failures may feed harness improvement — under controls:

- A failed run produces findings first; nothing edits guidance directly
  from a failure.
- Each proposed update cites the failure pattern, the checked source of
  truth, and how the fix was verified.
- Updates land through the approval path above, and the audit trail records
  them.

## Preconditions for L4

- The agent framework actually supports coordinated multiple roles.
- The project is complex enough that separated contexts beat one shared
  context; splitting roles reduces cache hits and multiplies token use, so
  the isolation must earn its cost.
- Role boundaries are clear and non-overlapping — divide by context needs,
  not by mirroring the human org chart.
- Review of cross-role output is defined and, unless the user decides
  otherwise, human-owned.

## What the project harness must record

Advanced autonomy cannot depend on this skill being available. The project's
own harness must state:

- The autonomy boundaries: what agents decide, what needs approval, which
  workflow actions agents may initiate.
- Where durable memory lives and how it is read and written.
- How tasks are routed, validated, and audited.
- How self-maintenance changes are reviewed and rolled back.
- How to stop or downgrade the autonomy — a visible fallback path to
  supervised operation.

## Plan output

An advanced-autonomy plan states, beyond the step-5 plan in SKILL.md: the
target level and why L2 is insufficient, the isolation and approval model,
the durable memory design, role responsibilities (L4), the
validation-and-audit design, the feedback-loop rules, the delegated
workflow actions, and the rollback and human-review points.
