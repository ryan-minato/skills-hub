---
name: great-skill-writer
description: >
  Write and improve Agent Skills that behave predictably — spec-compliant
  frontmatter, trigger-accurate descriptions, purposeful completion criteria,
  references split by branching condition, and non-interactive
  scripts. Use when creating a skill (even from a bare "make a skill for X"),
  when reviewing, pruning, or refactoring an existing skill, or when diagnosing
  a skill that misfires — wrong triggers, premature completion, or never-loaded
  references.
license: Apache-2.0
compatibility: Validation step requires uv (runs scripts/lint_skill.py).
---

# Great Skill Writer

A skill exists to extend an agent's capability, to wrangle determinism out
of a stochastic system, or both: supplying context the agent doesn't yet
have pushes the boundary of what it can do; restricting output makes how it
does it **predictable** — the same _process_ every run, consistent
high-quality output rather than identical output. Every rule below is a
lever on one or the other.

## Route by task

- Creating a new skill → run the workflow below.
- Improving, reviewing, or pruning an existing skill, or diagnosing one that
  misbehaved → read [references/failure-modes.md](references/failure-modes.md) when you start, then finish with steps 6–7 below.
- Read [references/spec.md](references/spec.md) when a spec constraint is uncertain or a lint finding is unclear.
- Read [references/glossary.md](references/glossary.md) when a term used here needs its full definition.

## Rules that apply on every branch

### Value: add what the agent lacks

A skill earns its load in two ways, separately or together: **context
provision** — supplying what the agent doesn't already have (project-specific
conventions, non-obvious procedures, exact APIs) — and **output restriction** —
reducing output variance with the instruction patterns below. Skip
explanations of standard concepts. Teach the approach, not one worked
instance — instructions must survive task variations. Give one default per
decision, alternatives in a single sentence: presented equal options make
agents choose inconsistently, the opposite of predictability. Calibrate
specificity to fragility: fragile or ordered operations get prescriptive
steps; where several approaches are valid, explain why, not what. Write for
agents, not humans: concise and directive, no pleasantries. And "the agent"
is not one model: a distributed skill runs on models of unequal capability
across different harnesses, so make every model-relative judgement — what
the agent lacks, what counts as standard, the no-op verdict — against the
least capable model the skill is meant to support, not the model at hand.
Write to the floor: a stronger model tolerates restriction it doesn't need;
a weaker one breaks without it.

### Instruction patterns

The restriction toolkit — use each where it applies, none by obligation:

- **Gotchas** — non-obvious domain facts the agent would get wrong
  by reasonable assumption (naming inconsistencies, soft deletes,
  endpoints that lie). Add one only when a correction reveals a reusable
  failure mode; general advice ("validate inputs") adds no signal.
- **Checklists** — for multi-step workflows with dependencies or validation
  gates.
- **Validation loops** — do → validate → fix → repeat; a validator whose
  errors state what is wrong and how to fix it lets the agent self-correct
  without a round-trip.
- **Plan-validate-execute** — for batch or destructive operations: produce a
  structured plan, validate it against a source of truth, then execute.
  Never skip the validation.
- **Templates (assets)** — only for intentionally fixed or stable-pattern
  material the agent copies or lightly edits. Templates constrain output
  diversity: content needing task-specific judgment, broad rewriting, or
  flexible organization becomes instructions on the hierarchy instead, never
  an asset.

### Descriptions

The description is the only text the agent reads before activating, so it
does two jobs: state the capability (third person, action verbs, domain
keywords) and list the triggers. Every character is permanent context load —
prune it harder than the body:

- Front-load the skill's leading word; never open with filler ("This skill
  helps…").
- One trigger per branch. Synonyms renaming the same branch are duplication;
  collapse them. Do include indirect phrasings — what a user says without
  naming the domain.
- Cut identity that's already in the body; keep triggers.

### Invocation

Default to model-invoked: keep the description visible so the agent (and
other skills) can reach it, and accept the context load it costs. Make a
skill user-invoked only when it should never fire except by the human typing
its name — then the human pays cognitive load as the index that remembers
it. The switch is host-specific (Claude Code: `disable-model-invocation:
true`), not part of the Agent Skills spec — read the portability section of
[references/spec.md](references/spec.md) when setting it or any other
non-spec field.

### Information hierarchy

Rank every piece of content by how immediately the agent needs it:

1. **Steps** — ordered actions in SKILL.md. Add a completion criterion when a
   step needs a meaningful boundary: the work is prone to premature
   completion, thoroughness matters, or the result has an observable success
   condition. Make it _checkable_ (the agent can tell done from not-done) and,
   where thoroughness matters, _exhaustive_ ("every modified model accounted
   for", not "produce a change list"). Omit it when it would not change how
   the agent executes or judges the step. A demanding criterion can also drive
   legwork in flat reference: "every rule applied" binds a rule list just as
   "every step done" binds a sequence.
2. **In-file reference** — rules and facts in SKILL.md, consulted on demand.
   A flat peer-set (every rule of a review on one rung) is fine.
3. **Disclosed reference** — a `references/` file behind a context pointer,
   loaded only when the pointer fires.

Branching decides the split: inline what every branch needs, disclose what
only some branches reach. The pointer's _wording_ decides reach — "Read
`references/api-errors.md` when the API returns a non-200 status", never
"see references/ for details". If a must-have pointer fires unreliably,
sharpen its wording first; inline only if that fails. Within a rung,
co-locate: a concept's definition, rules, and caveats under one heading, not
scattered.

### Leading words

A leading word is a compact concept already in the model's pretraining that
the agent thinks with while running the skill (_lesson_, _fog of war_,
_tracer bullets_). Priors differ across models — a niche concept anchors one
model and recruits nothing on another — so a multi-model skill prefers
widely-attested words. In the body it anchors execution; in the description it
anchors invocation — especially when the same word lives in your prompts and
docs. Hunt for restatements to collapse: "fast, deterministic, low-overhead"
→ a _tight_ loop; "a loop you believe in" → the loop goes _red_. A word too
weak to beat the default is a no-op (_be thorough_); the fix is a stronger
word (_relentless_), not more sentences.

### Granularity

Each split spends one of the two loads, so split only when the cut earns it:

- **By invocation** — split off a model-invoked skill when a distinct leading
  word should trigger it on its own, or another skill must reach it. The new
  always-loaded description is the price.
- **By sequence** — split a run of steps when the visible later steps tempt
  the agent to rush the current one. Hiding works only across a real context
  boundary (a hand-off or subagent dispatch).

### Pruning

Three passes over anything you wrote or touched:

1. **Deduplicate** — each meaning keeps a single source of truth; collapse or
   pointer-ise the other copies.
2. **Relevance** — delete lines that no longer bear on what the skill does.
3. **No-op hunt** — sentence by sentence: does this sentence change behaviour
   versus the defaults of the weaker models the skill is meant to support?
   Delete whole sentences that fail; most should go, not be rewritten.

## Create a new skill

1. **Define.** Write down: the task covered (one coherent work unit — too
   narrow and it conflicts with other loaded skills, too broad and it
   triggers unreliably), the trigger list including indirect phrasings, what
   the agent lacks that makes the skill necessary, and the invocation mode.
   If the agent already handles the task well bare, stop — the skill adds no
   value.
   Done when: all four answers are written and the value answer is non-empty.
2. **Scaffold.** Copy [assets/skill-template.md](assets/skill-template.md) to
   `<skill-name>/SKILL.md`. Name: lowercase `a-z0-9` with single hyphens,
   ≤64 chars, exactly equal to the directory name. Create `scripts/`,
   `references/`, `assets/` only when a file goes in.
3. **Describe.** Write the frontmatter description per the rules above.
   Done when: it is third person, opens on the leading word, has one trigger
   per branch plus indirect phrasings, and restates nothing from the body.
4. **Write the body.** Steps first; add `Done when: <criterion>` only where a
   checkable boundary improves execution reliability. Then add in-file
   reference, applying the instruction patterns above where they fit; then
   disclose branch-specific material into `references/` files, each linked at
   first mention with a precise load condition.
   Done when: every included completion criterion is checkable and every
   reference file is linked with a condition.
5. **Bundle scripts** — only if the same logic would be regenerated
   identically every run (validators, parsers, formatters); generate inline
   for one-off logic. Every script: no interactive prompts (they hang in
   non-interactive shells — take input via flags), `--help` with a usage
   example, data to stdout (JSON preferred) and diagnostics to stderr, exit
   codes 0 success / 1 error / 2 bad arguments, idempotent (agents retry),
   errors that state what is wrong and how to fix it, pinned dependency
   versions, output over ~10,000 characters defaulting to a summary with
   `--full` or `--output FILE` (harnesses may silently truncate stdout), a
   `compatibility` frontmatter line naming the runtime the scripts require
   (a host may lack uv, Deno, or Bun — SKILL.md-only skills need no such
   line), and a relative markdown link in SKILL.md at first mention.
   Read [references/scripts-python.md](references/scripts-python.md) when writing Python, or [references/scripts-typescript.md](references/scripts-typescript.md) when writing for Deno or Bun.
   Done when: each script meets every rule in this step's list.
6. **Prune.** Run the three passes on your draft — including the description.
   Done when: a further deletion would change behaviour on a model the skill
   is meant to support.
7. **Validate.** Run [`scripts/lint_skill.py`](scripts/lint_skill.py):
   `uv run scripts/lint_skill.py --skill <skill-dir>`. Fix every error;
   for each warning, apply it or state why it doesn't apply.
   Done when: exit code is 0 and every remaining warning has a stated reason.

## Improve or diagnose an existing skill

Locate the observed symptom in [references/failure-modes.md](references/failure-modes.md) when you begin — it maps
symptoms (never triggers, fires wrongly, rushes steps, shallow work, ignored
references, bloat) to causes and ordered fixes. Apply the fix, then run steps
6–7 above on the result.
