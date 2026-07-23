# Failure modes — diagnose and fix an existing skill

Load this when improving, reviewing, or pruning a skill, or when a skill
misbehaved in a session. Start from the observed symptom, confirm the cause
in the skill's text, apply the fix, then re-run the pruning passes and the
review checklist below on the result.

## Symptom index

| Observed symptom | Likely failure | Section |
|---|---|---|
| Skill never triggers, or only when named explicitly | Weak description | [Wrong or missing triggers](#wrong-or-missing-triggers) |
| Skill fires on unrelated tasks | Over-broad description | [Wrong or missing triggers](#wrong-or-missing-triggers) |
| Agent quits a step early, skips verification, rushes to the end | Premature completion | [Premature completion](#premature-completion) |
| Agent does shallow work inside a step (reads one file, samples instead of covering) | Thin legwork | [Thin legwork](#thin-legwork) |
| Agent never opens a reference file it needed | Weak context pointer | [Never-loaded references](#never-loaded-references) |
| Agent behaves differently run to run on the same task | Any of the above | work the whole index |
| Skill is hard to edit; instructions contradict each other | Duplication or sediment | [Duplication](#duplication), [Sediment](#sediment) |
| Skill is long but every line looks legitimate | Sprawl | [Sprawl](#sprawl) |
| Instructions that visibly change nothing | No-op | [No-op](#no-op) |

## Wrong or missing triggers

The description is the only text read before activation, so trigger failures
are always description failures.

- **Never triggers**: the description lacks the words the user actually says.
  Rewrite the trigger clauses with the leading words from your real prompts,
  and add indirect phrasings that don't name the domain.
- **Triggers wrongly**: the description claims territory it doesn't own —
  generic verbs ("helps with documents") or synonym-stuffed trigger lists.
  Cut to one trigger per branch; make the capability sentence specific enough
  to exclude neighbours.
- **Two skills both fire**: their descriptions overlap. Either merge the
  skills or re-cut the boundary so each description names territory the other
  doesn't.

## Premature completion

Ending the current step before it is genuinely done — attention slips to
_being done_. Needs steps to occur; a skill with no steps that quits early is
thin legwork instead.

Confirm: find the step the agent rushed and inspect its boundary. If a
completion criterion exists but you cannot tell done from not-done by reading
it, neither could the agent.

Fix, strictly in this order:

1. **Add or sharpen a completion criterion** — cheap and local when the step
   has a meaningful boundary. Replace vague bounds ("understanding reached")
   with checkable ones ("every call site listed with file and line"). Where
   thoroughness matters, make it exhaustive ("every modified model accounted
   for", not "produce a change list").
2. **Hide the post-completion steps** — only if the criterion is irreducibly
   fuzzy _and_ you observed the rush. Split the sequence so the tempting
   later steps live in a second skill or a subagent dispatch. Hiding only
   works across a real context boundary; an inline call leaves the later
   steps in context and clears nothing.

## Thin legwork

The agent does shallow work inside a step even though it runs the step to
completion: reads one file where it should sweep, samples where it should
cover.

Fix: raise the demand. Either strengthen the completion criterion's
exhaustiveness ("every rule applied to every changed file") or plant a
stronger leading word (_relentless_, _exhaustive_) where the work is
specified. This works on flat reference too — "every rule applied" binds a
rule list just as "every step done" binds a sequence.

## Never-loaded references

A reference file the agent needed but never opened. The pointer's wording,
not its target, decides reach.

Fix, in order:

1. **Sharpen the pointer wording**: state the exact condition — "Read
   `references/api-errors.md` when the API returns a non-200 status", never
   "see references/ for details".
2. **Inline the material** — only if sharpened wording still fails and the
   material is must-have on most runs. Then it was mis-ranked on the
   hierarchy, not mis-pointed.

Also check the reverse: a reference loaded on every run belongs in SKILL.md
(its condition is "always", which is no condition).

## Duplication

The same meaning in more than one place. Costs maintenance, costs tokens, and
inflates the meaning's prominence past its real rank. Distinguish it from a
leading word: a leading word repeats a _token_ on purpose; duplication repeats
a _meaning_ by accident.

Fix: pick the single source of truth (the place ranked correctly on the
hierarchy), collapse the others into a pointer to it or delete them. In
descriptions, synonym triggers for one branch are duplication — keep one
trigger per branch.

## Sediment

Stale layers that settle because adding feels safe and removing feels risky:
instructions for tools that changed, caveats for bugs long fixed, examples of
formats no longer used.

Fix: run the relevance pass (below) dated against the current behaviour of
the world the skill describes. When in doubt whether a line is stale, test
the skill without it.

## Sprawl

Too long, even when every line is live and unique. The agent wades through
more before it can act, and attention thins across the excess.

Fix with the information hierarchy, in order of preference:

1. Disclose reference that only some branches need into `references/` files
   behind conditional pointers.
2. Split by branch: if two invocation cases share little content, they are
   two skills.
3. Split by sequence: if a long step run tempts rushing, cut it at the point
   where the remaining steps can run in a fresh context.

## No-op

A line the model already obeys by default — you pay load to say nothing. The
test: does this line change behaviour versus the default? Model-relative:
settle disagreements by running the skill — including on the weaker models
it is meant to support — not by debate.

Fix: delete the whole sentence, don't trim words from it. A weak leading word
is a no-op (_be thorough_ when the agent is already thorough-ish); the fix is
a stronger word (_relentless_), not a different technique.

## The three pruning passes

Run all three over any skill you touched, in this order:

1. **Deduplicate**: every meaning has exactly one home. For each rule or fact
   stated twice, keep the copy ranked correctly on the hierarchy and delete
   or pointer-ise the rest.
2. **Relevance**: for every line, ask "does this still bear on what the skill
   does?" Delete exposition, disclosed-branch leakage, and stale material.
3. **No-op hunt**: sentence by sentence, not line by line — ask "does this
   sentence change behaviour versus the defaults of the weaker models the
   skill is meant to support?" Delete whole sentences that fail. Be
   aggressive: most prose that fails should go, not be rewritten.

Done when: a further deletion would change agent behaviour.

## Review checklist

Apply every item; report each as pass or fail with the offending line.

- [ ] Description: third person, capability sentence first, one trigger per
      branch, covers indirect phrasings, no body identity restated.
- [ ] Invocation mode matches use: model-invoked only if the agent (or
      another skill) must reach it on its own.
- [ ] Steps that benefit from an explicit boundary have a checkable
      completion criterion; criteria are exhaustive where thoroughness
      matters, and low-value criteria are omitted.
- [ ] Every reference pointer states a precise load condition; no
      "see references/".
- [ ] Inline content is needed by every branch; branch-specific content is
      disclosed.
- [ ] Each concept's definition, rules, and caveats are co-located under one
      heading.
- [ ] Every asset is intentionally fixed or stable-pattern material the agent
      copies or emits; none holds content that should be generated flexibly.
- [ ] No asset wraps its copied material in surrounding how-to-use
      documentation; inline placeholders and fill-comments are fine, but prose
      framing when and how to use the asset lives in SKILL.md or a reference.
- [ ] No meaning has two homes; no sentence fails the no-op test; no stale
      lines.
- [ ] Spec-mechanical checks pass (run the bundled linter; consult the spec
      reference on any unclear finding).
