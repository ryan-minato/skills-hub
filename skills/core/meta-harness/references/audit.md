# Auditing An Existing Harness

For repairing, slimming, modernizing, or de-conflicting a harness that
already exists. The inspection checklists in SKILL.md still apply; this file
adds the audit-specific sequence. An audit is not a license for a broad
rewrite — change what the findings justify.

## Sequence

1. Inventory every project-visible harness artifact: entrypoints, knowledge
   and reference files, project skills, registered tools, scripts,
   validation and CI configuration, framework configuration.
2. For each artifact, record how a future agent would find it, what triggers
   loading it, what its source of truth is, and how it is kept current. No
   discovery path means it is invisible; no source of truth usually means it
   has drifted.
3. Compare the harness against the current project: structure, commands,
   interfaces, workflow rules, validation. Follow entrypoint pointers first,
   the way a future agent would; use git history only to distinguish current
   conventions from abandoned ones.
4. Classify each issue: stale, duplicated, contradictory, invisible,
   missing, excessive for the project's actual needs, or orphaned (nothing
   triggers it).
5. Recommend a disposition per artifact using the decision rules below.

## What to look for

- Entrypoints past their length budget, or carrying detail that belongs
  behind a pointer.
- Paths, commands, and interface descriptions that no longer exist.
- The same rule stated differently in two places.
- Knowledge no pointer reaches; skills and workflow entries whose trigger
  never fires.
- Validation commands that do not run as documented.
- Speculative components serving no current need, and constraints thicker
  than the work justifies.
- Workflow automation the team never actually delegated.

## Decision rules

- Update: the artifact is needed but wrong.
- Reconnect: the artifact is correct but nothing reaches it — add a
  discovery pointer from the entrypoint, or from the file that should own
  it.
- Add: a needed component does not exist — design it through the main
  workflow's calibrate-and-build steps rather than patching it in ad hoc.
- Move: it is loaded too often for how rarely it applies — push it behind a
  narrower pointer.
- Merge: two artifacts are always read together and neither is large.
- Split: one artifact loads on every run but only part of it is always
  needed — keep that part and push the rest behind a conditional pointer.
  Prefer merging over splitting.
- Thin: valid but overweight — replace machinery with a pointer, a note, or
  a single command.
- Remove: clearly obsolete, duplicated, or unsupported. Ask before removing
  anything that looks maintained.
- Leave unchanged: accurate, reachable, proportionate.

For contradictory rules, the source of truth decides which copy survives:
keep the version that matches it, and update or remove the rest. When the
source or its ownership is unclear, ask the user instead of picking.

## Repair plan and verification

For each change, state the problem, the source of truth for the correction,
the exact artifact to update, whether a sync rule changes with it, and how
to verify. After applying:

- Entrypoint pointers reach every remaining artifact; no dangling links to
  deleted files.
- Documented validation commands run, or are explicitly marked as needing
  user setup.
- Sync rules mention every artifact whose source of truth changed.
- Each remaining thick component has a current lifecycle, risk, or workflow
  reason to stay thick.
