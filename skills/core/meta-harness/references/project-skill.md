# Project Skills

A project skill is a progressively loaded working manual for one recurring
procedure in this project. It beats a document when the procedure is
repeated, fragile, order-sensitive, or too branchy to state inline.

## When a skill is warranted

Create one when entrypoint text or a knowledge file is not enough:

- The procedure has several ordered steps that must not be improvised.
- Agents keep needing the same non-obvious instructions across sessions.
- Mistakes are expensive or hard to detect afterwards.
- The trigger is clearly describable, so the skill loads exactly when
  relevant.

Do not create one for a one-off task, for stable background knowledge (that
is a knowledge file), or for a short rule that belongs in the entrypoint.

## Authoring

Start from `assets/project-skill-skeleton.md` (path relative to this
skill's root).

- Scope the skill to one coherent unit of work; split unrelated triggers
  into separate skills.
- Write the description around the user's intent and the project condition
  that should trigger it, not around internal filenames.
- Put the steps needed on most invocations in the body. Split content into
  skill-local references only for a substantial branch that many
  invocations skip, and give each reference a precise load condition.
- Add assets only for structural skeletons or snippets the agent copies.
- Record project-specific failure modes as gotchas.

Do not pour broad goals, architecture, or team workflow into a skill; those
belong in the entrypoint and knowledge files. A skill carries only what its
procedure needs.

## Discoverability and upkeep

Most frameworks inject skill descriptions automatically; the skill still has
to be discoverable without this meta skill present. If the framework does
not reliably announce project skills, point to their location from the
entrypoint.

Every project skill needs an update trigger: a project-visible rule saying
when the skill must be revised (its commands, paths, or procedure changed).
A skill without an update path goes stale silently, and agents follow stale
skills with confidence.
