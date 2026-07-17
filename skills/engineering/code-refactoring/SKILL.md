---
name: code-refactoring
description: >
  Code refactoring methodology — restructures existing code in small
  behavior-preserving steps, verified by tests after every step. Use when
  refactoring, restructuring, or cleaning up working code without changing
  what it does; when code must be reshaped before a feature or bug fix can
  land safely; when a function, class, or module has grown long, duplicated,
  or tangled — "clean this up", "break this apart", "untangle this", "make
  this readable"; when every small change forces edits in many places; when
  deciding whether, when, or how far to refactor; or when choosing which
  named refactoring technique fixes a structural problem. Not for adding
  features or fixing bugs (keep those separate from restructuring), for
  performance tuning, or for ground-up rewrites.
---

# Code Refactoring

A discipline for improving the internal structure of existing code without
changing its observable behavior. The payoff is economic, not aesthetic:
well-structured code makes the next change faster and less error-prone.
Everything below exists to protect one invariant — **the code keeps working
the whole time**.

## What refactoring is

Refactoring is a series of small structural changes, each too small to be
worth breaking anything, composed into a large improvement. Between steps the
code compiles and passes its tests. If the code is broken for more than a few
minutes, what is happening is not refactoring — it is a rewrite wearing the
wrong name, and it forfeits the ability to stop at any moment with working
code.

"Observable behavior" means behavior any caller or user relies on. Internal
interfaces may change (that is often the point), but given the same inputs
the system produces the same outputs and side effects afterward.

## Two modes, never mixed

At any moment you are doing exactly one of two things:

- **Changing behavior** — adding a feature, fixing a bug. Structure stays as
  it is.
- **Changing structure** — refactoring. Behavior stays as it is; tests are
  not modified except where an interface they touch was deliberately renamed
  or moved.

Switch between modes as often as needed, but switch consciously and keep the
two in separate commits, because a reviewer must be able to skim a
structure-only diff and a behavior diff demands close reading — mixing them
makes both unreviewable.

If refactoring exposes a pre-existing bug, do not silently fix it mid-step.
Preserve the current behavior through the refactoring, report the bug, and
fix it afterward as an explicit behavior change (or file it if it is out of
scope).

## The safety loop

1. **Start green.** Run the tests before touching anything. If they fail
   now, you cannot tell later whether you broke something.
2. **Take the smallest step you can.** One rename, one extraction, one moved
   statement. Small steps feel slow but are faster overall because nothing
   ever needs debugging.
3. **Test after every step.** The tests must be quick enough that running
   them every few minutes feels cheap; if they are not, run the focused
   subset that covers the code being changed.
4. **Checkpoint every green state** — a commit, or your tool's equivalent —
   so there is always a known-good state seconds away.
5. **On red, revert to the last green state and take a smaller step.** Never
   debug forward through a broken refactoring; the whole point of small
   steps is that rolling back costs almost nothing.

Take bigger steps only while they keep succeeding; the moment one breaks,
drop back to baby steps.

## When to refactor

- **Preparatory** — the highest-value moment is right before a change. If
  the change is hard, first restructure so it becomes easy, then make the
  easy change. Budget for the restructuring as part of the change itself.
- **For comprehension** — when you must decode what code does, move that
  hard-won understanding into the code: rename things, extract pieces.
  Clearer code then reveals design issues you could not see before.
- **Litter-pickup** — leave code a little better than you found it. Small
  improvements compound; ones too large for the moment go on a note, not in
  the way of the current task.
- **Rule of three** — tolerate a duplication once, wince the second time,
  refactor the third.

Most refactoring is opportunistic — woven into feature and fix work, not a
separate scheduled activity. Do not refactor when the code is ugly but never
needs to be touched or understood; when rewriting from scratch is genuinely
cheaper (a judgment call — probe before deciding); or when a tiny urgent
change should not wait on a large restructuring — ship it, then restructure.

## No tests? Fix that first

A missing safety net changes the plan, not the principle:

1. Write characterization tests around the code you intend to change: capture
   its current input→output behavior, bugs included, as the baseline.
2. If the code resists testing, create the seams needed to attach tests using
   the smallest, most mechanical transformations available — this is the one
   permitted exception to "refactor only under test", so keep it minimal.
3. Until coverage exists, restrict yourself to transformations your tooling
   can perform mechanically (automated renames and extractions), which are
   safe without tests.

## Diagnosing and executing

Both reference files open with an index table, so a lookup never requires
reading the whole file: consult the index, pick the row, then read only the
matching entry — every entry sits under its own heading.

- When deciding what is structurally wrong or which technique fixes a
  symptom, consult the index table at the top of
  [references/smells.md](references/smells.md); open a smell's `## <Name>`
  entry only when the index row leaves the match or the remedy unclear.
- When a technique is chosen and its safe step sequence is not obvious,
  locate its `### <Name>` heading in
  [references/techniques.md](references/techniques.md) and read that entry
  alone; consult the index at its top only when still choosing between
  related techniques (a purpose group or an inverse pair).

## Special contexts

- **Published interfaces** (callers you cannot edit): never change them in
  place. Add the new interface, forward the old one to it, deprecate the old
  one, and remove it only when callers have migrated — possibly never.
- **Performance**: refactor for clarity first, even if it costs a little
  speed; then optimize the clear version guided by measurement. Most code is
  not on the hot path, so tuning without a profile wastes effort on the
  wrong lines.
- **Persistent data schemas**: change them by parallel change
  (expand–contract): add the new field or shape alongside the old, write to
  both, migrate readers one by one, then retire the old — each stage
  releasable and reversible on its own.
- **Restructurings too large for one sitting**: keep the system working
  throughout. Introduce an abstraction over the old structure, migrate
  callers to it incrementally, then swap the implementation underneath. The
  codebase never holds a half-broken state, even if the effort spans weeks.
- **Integration**: refactoring makes many small edits across the codebase,
  which long-lived branches turn into merge conflicts. Integrate frequently
  — and time cross-cutting renames to land when they conflict with the least
  in-flight work.

## Scope and reporting discipline

Refactor what the task needs and what you touch along the way — not the
whole codebase. Keep each diff small enough to review in one pass. When
reporting, state what was restructured and why, confirm behavior parity with
test results, and list anything deliberately left for later.
