# Layer Calibration

Per-layer guidance for a full harness design or a recalibration. The
thickness scale is the one in SKILL.md: omitted, light, medium, thick.

## Environment

The development and CI environments decide how much autonomy agents can
safely be given, so choose the isolation level first:

- Fully isolated (container or virtual machine holding everything the agent
  touches): agents can run with minimal or no approval. Secrets stay outside
  the agent's reach, a broken environment is rebuilt rather than repaired,
  and the user reviews only the produced changes.
- Sandboxed host (agents read beyond the workspace but cannot write outside
  it): agents can decide for themselves when to escalate for approval.
- Unisolated host: require per-command approval, because agents can damage
  the host or reach confidential data.

Prefer an isolated, reproducible development environment when the stack
allows one; fall back to the host only when the project genuinely depends on
host-specific resources. Record in the harness only the boundaries agents
must respect: how to enter and verify the environment, what is out of
bounds, and what needs approval.

## Target constraints

Target constraints give agents a durable understanding of what the project
is for, which keeps effort pointed in one direction across many sessions and
shapes implementation style. Every project needs at least a written goal
statement. Beyond that, match the constraint form to what the project
exposes: code consumed by other code needs its public interface defined;
a service needs its API behavior defined; user-facing software needs user
stories, expected behavior, or visual references. Do not add contract forms
for surfaces the project does not have.

## Implementation constraints

Language, paradigm, module architecture, and dependency direction. Thicker
constraints make output more controllable and maintainable but shrink the
agent's freedom to explore, so calibrate by how settled the requirements
are, how complex the structure is, and how long the code must live:

- One-off or exploratory work: nearly none. Users care about the result, not
  the design; prescribing architecture there is over-engineering.
- Clear requirements, complex structure, or a long maintenance horizon:
  document architecture and module boundaries, and enforce dependency
  direction where tooling allows.

When the user has already made design decisions, record them here and treat
them as fixed.

## Quality constraints

Linters, formatters, style documents, tests, and review gates narrow output
variance without shrinking the agent's exploration freedom — but they are
not free: creating them costs tokens, and every future change pays tokens to
satisfy them. Calibrate by error cost, maintenance horizon, and how much the
language already guarantees:

- Strong static or compile-time checking reduces the need for a thick
  custom quality layer; lean on the language first.
- Long-lived or error-intolerant projects justify thick tests to prevent
  regressions; decide the test granularity deliberately — per-component unit
  tests, tests for key components only, scenario tests, or a smoke test —
  rather than defaulting to maximal coverage.
- Custom checks must fail with messages that explain what failed, why it
  matters, and the likely fix. A check agents cannot self-correct against
  just burns tokens.

## Workflow constraints

How commits are made, how branches merge, how review is requested, and how
tickets are created, planned, and closed. These pair with workflow tools to
automate code evolution, and they are team decisions: record what the team
has decided, and leave everything undecided out. An agent must not invent a
workflow the team never agreed to.

## Information tools

Reference documents, external links, documentation endpoints, and similar
sources expand what agents can know, but every read costs tokens. Design for
progressive loading: a short pointer with a precise condition (in the
entrypoint, a knowledge file, or a skill) that tells agents when the source
is worth reading, instead of inlining or preloading the content.

## Workflow tools

Documents, skills, or registered tools that let agents operate the team's
ticket system, review flow, or messaging. Add one only when the team has
delegated that action to agents and access is authorized; otherwise document
the human handoff instead. Every workflow tool needs a matching workflow
constraint that says how the team expects it to be used.

## Capability tools

Tools that let agents exercise and observe the system while developing:
driving the running software end to end, capturing its state, reading logs
and metrics, or querying telemetry. Add the ones the current development and
validation work actually needs; each unused tool is description noise in
every session.

## Repository safety

This layer keeps secrets and private data out of the repository: scanning
hooks, commit rules, and guidance on what may never be committed. Calibrate
by leak risk and collaboration boundary — what counts as confidential in a
trusted internal team differs from an open-source project. Security of the
code itself (input validation, dependency vulnerabilities) is not this
layer; it belongs to quality constraints, especially tests.
