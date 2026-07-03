---
name: meta-harness
description: >
  Design, audit, and improve agent harnesses: the environment, constraints,
  tools, and accessible knowledge that make coding agents match user
  expectations in a project. Use when setting up agent instructions, creating
  or restructuring AGENTS.md or CLAUDE.md, deciding how much structure (tests,
  linting, CI, architecture docs) a project needs for agent-driven work,
  making project knowledge discoverable to agents, adding project skills,
  designing sync or maintenance mechanisms, calibrating agent autonomy and
  approval boundaries, or diagnosing why agents keep missing project
  conventions.
license: Apache-2.0
---

# Meta-Harness

A harness is everything agent-visible that helps agents meet user
expectations: the environment they run in, the constraints on what they
produce, the tools they can call, and the knowledge they can reach. A harness
works in two directions. It first expands what agents can do — through the
environment, information, and tools — and then narrows the wide space of
possible implementations back to a maintainable, cost-appropriate range —
through target, implementation, quality, workflow, and repository-safety
constraints.

This skill is a design aid. It may exist only in one user's library, so every
rule future agents must follow has to land in the project's own harness:
repository files, project skills, registered tools, or reachable endpoints.
Nothing durable may live only in this conversation.

## Core Rules

- Agent-visible means version-controlled files plus anything reachable over
  the internet or through registered tools. Conversation threads, chat
  messages, and unwritten team habits are invisible to future agents: if
  information matters, encode it somewhere accessible or it does not exist.
- Inspect discoverable facts before asking the user. Ask only about team
  decisions, access boundaries, and facts the project cannot show.
- Build only components that a current, concrete need justifies.
- Default to a single agent, and avoid designing a self-evolving harness
  unless the user asks for one.
- Workflow rules (commits, merges, reviews, tickets, notifications) are team
  decisions. Record what the team decided; never invent automation.
- When the user has made a design decision, record it in the harness and
  work within it instead of reopening it.

## Workflow

### 1. Route by task

- Read [references/audit.md](references/audit.md) when the task is auditing,
  repairing, slimming, or de-conflicting an existing harness.
- Read [references/advanced-autonomy.md](references/advanced-autonomy.md) when
  the user asks for self-evolution, persistent memory, unattended operation,
  autonomous task routing, or multiple agent roles.
- Otherwise — creating a harness or extending one — continue below.

### 2. Inspect the project

Read enough to avoid guessing. Project facts:

- Layout: monorepo, multi-repo, or a single self-contained codebase. If the
  project seems to depend on sibling repositories, ask the user rather than
  assume.
- Technology stack, and the project's goal — the end state it aims for.
- Architecture skeleton: file layout and major modules, not every file.
- Development, test, and deployment environments, and how isolated they are.
- Error tolerance: the cost of a bug or unexpected behavior escaping.
- Lifecycle: one-off script, exploratory experiment, reproducible experiment,
  analysis prioritizing readability, long-lived service, or a shared library
  at the far end of stability.
- Deployment plan, CI approach, code style (naming, comments, paradigm, and
  which languages are used where), and version-control workflow (branching
  model, merge style, commit-message format and language).

Team facts — these drive workflow and autonomy decisions:

- Team size, and the information-security context: fully trusted internal
  team, internal with external members, or open source (team-led or
  community-driven). What counts as confidential changes accordingly.
- Division of labor, and how code review happens.
- Agent involvement: Q&A and review only, command assistance, agent-driven
  implementation, or autonomous evolution.
- Approval flow — how finished work gets integrated — and where the team
  communicates, so agents know how findings reach humans.

Done when: each fact above is either gathered from the project or on the
question list for the user.

### 3. Choose the maturity level

| Level | Harness | Division of labor |
|---|---|---|
| L0 | None; prompts only | Engineers write the code; agents answer questions |
| L1 | Entrypoint file plus a linter and/or tests | Agents handle moderately complex tasks; engineers still write most code |
| L2 | L1 plus automated tests, CI, and optional workflow rules — a working feedback loop | Engineers plan and approve; agents produce most of the code |
| L3 | L2 plus self-maintenance: entropy management, autonomous task intake, persistent memory | Mostly unattended; engineers design the environment, plan architecture, and control quality |
| L4 | L3 split across multiple agent roles with managed context boundaries | Engineers only control quality and design the environment |

Build to L2 at most by default: L3 and L4 lack uniform framework support and
carry real risk. Design them through
[references/advanced-autonomy.md](references/advanced-autonomy.md) when the
user asks — or propose the upgrade first when the evidence strongly supports
it. Do not upgrade to look robust or downgrade just to stay lightweight.

Done when: a level is chosen and the step-2 evidence supporting it is
written down for the plan.

### 4. Calibrate the layers

Rate each layer omitted, light, medium, or thick. Omit a layer no current
need justifies; use light when a sentence or a pointer suffices; use medium
when the layer needs a dedicated file, check, or tool; go thick only when
enforcement or rich tooling pays for its cost.

Layers that expand capability:

| Layer | Covers | Calibrate by |
|---|---|---|
| Environment | Development and CI environments | Isolation: the more isolated the environment, the more autonomy agents can safely get; weak isolation demands per-command approval |
| Information tools | Reference docs, external links, documentation endpoints | Reading costs tokens — load progressively through pointers with precise conditions |
| Workflow tools | Access to ticket systems, review flows, team messaging | Only what the team has delegated to agents |
| Capability tools | Ways to run, exercise, and observe the system under development (end-to-end driving, logs, telemetry) | Current development and validation needs only |

Layers that narrow the implementation space:

| Layer | Covers | Calibrate by |
|---|---|---|
| Target constraints | Goal statement, exposed interface or API behavior, user stories, visual references | Every project needs at least a goal statement; add contract detail matching what the project exposes |
| Implementation constraints | Language, paradigm, module architecture, dependency direction | Requirement clarity, structural complexity, maintenance horizon; keep thin for exploratory work |
| Quality constraints | Linters, formatters, style docs, tests, review gates | Error cost, maintenance horizon, and how much the language's static checking already guarantees; these cost tokens to create and to satisfy |
| Workflow constraints | Commit, merge, review, and ticket rules | Team decisions only |
| Repository safety | Keeping secrets and private data out of the repository | Leak risk and collaboration boundary; security of the code itself belongs to quality constraints and tests |

Read [references/layers.md](references/layers.md) when designing a full
harness or recalibrating several layers; skip it for a single targeted
artifact change.

Done when: every layer has a rating and a reason.

### 5. Present the plan

Before creating anything, show the user:

- the files to create or change, grouped by harness layer;
- the chosen maturity level and the evidence for it;
- each layer's thickness, and why a thicker option was not chosen where that
  is non-obvious;
- which workflow actions are delegated to agents versus kept by humans;
- assumptions made, and decisions still needed from the user.

Done when: the user has seen all of the above before any file is created.

### 6. Build

AGENTS.md is the entrypoint, and every harness component must be reachable
from it. Skills and registered tools announce themselves through their own
descriptions; scripts, linters, and other commands only need their usage
documented; reference and knowledge files are the one category that needs an
explicit discovery pointer (a when-to-read rule in the entrypoint), because
nothing else reveals they exist.

Route by what is being built:

- Entrypoint (AGENTS.md, CLAUDE.md) — read
  [references/entrypoint.md](references/entrypoint.md) when creating or
  restructuring it.
- Read [references/knowledge.md](references/knowledge.md) when building
  knowledge or reference files, local or on a remote backend.
- Read [references/project-skill.md](references/project-skill.md) when a
  repeated procedure is fragile, order-sensitive, or too branchy for a
  document and should become a project skill.
- Project scripts and task runners: implement them, then document the
  invocation in the entrypoint's validation or workflow section.
- Tests, CI, commit hooks, and editor configuration: implement them per the
  quality and repository-safety decisions from step 4. Custom checks must
  fail with messages that say what failed, why it matters, and the likely
  fix, so agents can self-correct.
- Agent framework configuration (sandboxing, approvals, behavior) where the
  framework provides it. Framework lifecycle hooks are powerful but
  framework-specific: rely on them only when the whole team uses one
  framework.

Done when: every planned component exists and is reachable from the
entrypoint.

### 7. Install the keep-current mechanism

Stale harness content is worse than none, so every durable harness states
how it stays current, inside the project where future agents can see it. For
a light harness one sentence in the entrypoint is enough: when a command,
structure, or convention changes, update the harness content that mentions
it. Read [references/maintenance.md](references/maintenance.md) when sync
spans several artifacts or a long-lived project needs periodic entropy
cleanup. Updating knowledge from agent failure history is an
advanced-autonomy capability; do not wire it into an ordinary harness.

Done when: a keep-current rule exists in a project-visible file.

### 8. Verify

- Future agents can reach every rule from the entrypoint without this skill
  or this conversation.
- Local links resolve, and documented commands run.
- The entrypoint stays within its length budget.
- The keep-current rule exists in project-visible form.

## Gotchas

- In generated harness documents, write direct instructions under plain
  headings; do not coin names for principles.
- Name categories, not products: harness guidance that enumerates specific
  tools goes stale and biases agents against equivalent alternatives.
