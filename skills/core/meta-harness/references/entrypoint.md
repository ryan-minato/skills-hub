# The Entrypoint

The entrypoint is the file coding agents always read, so it is the discovery
root: every harness rule must be stated in it or reachable from it.

## Choose the file

Default to AGENTS.md. When some of the team uses Claude Code, add a
CLAUDE.md whose only content is a reference to AGENTS.md, so both stay
consistent. Write rules directly in CLAUDE.md only when the team explicitly
uses Claude Code exclusively. Frameworks differ in how they treat the
entrypoint, but AGENTS.md is the widely recognized shared convention.

## What belongs in it

- The project's purpose, in a sentence or two.
- An architecture-level project map — unless another discoverable
  architecture document already provides one. Keep it at the level of
  directories and modules; a map that changes on routine file additions is
  too detailed.
- Core conventions that apply to most tasks.
- When-to-read-what pointers for every knowledge and reference file, since
  nothing else reveals those files exist.
- Validation commands, and the approval or safety boundaries that apply to
  most tasks.
- The keep-current rule, or a pointer to whatever mechanism owns it.

## Length budget

The entrypoint is a map, not a manual. Aim for about 100 lines; when it
grows past that, move detail into knowledge files, references, or skills and
leave a pointer. At L1 the budget relaxes to about 200 lines, because an L1
harness has few other files — rules that a larger harness would push into
knowledge files have nowhere to go but inline.

Two limits on that compression: rules every agent must always see stay in
the entrypoint no matter what, since content behind a pointer is only loaded
when the pointer's condition fires; and an oversized entrypoint is not a
harmless archive — it is loaded into every session and crowds out working
context.

## Use the skeleton

Copy `assets/agents-md-skeleton.md` (path relative to this skill's root),
fill only the sections backed by current facts or explicit user decisions, and
delete every section that does not serve the project. An empty or
speculative section teaches agents to distrust the file.
