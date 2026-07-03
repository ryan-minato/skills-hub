# Sync And Entropy Management

Mechanisms that keep a harness true to the project it describes. Everything
here must end up project-visible: future agents must be able to find when
the mechanism runs, what it updates, and how it verifies, without this meta
skill.

Through L2, keeping the harness current is driven by the source of truth:
when a visible file, command, interface, or workflow rule changes, dependent
harness content gets updated in the same change. Repeated agent failures may
justify findings and recommendations to the user, but not automatic edits to
knowledge or references — that is an advanced-autonomy capability (see
[advanced-autonomy.md](advanced-autonomy.md)).

## Choose the lightest mechanism

- One inline sentence or a short mapping table in the entrypoint: the
  default. Enough when the things likely to go stale fit a few rows. The
  entrypoint skeleton carries the table shape.
- A workflow entry (a section in the entrypoint or a workflow document):
  when one sync concern is recurring and its steps are linear but too long
  to inline. Each entry names the triggering change, the source of truth,
  the dependent artifacts, the update steps, and a verification step.
- A dedicated sync project skill: when one consistency concern is frequent,
  fragile, or branchy, or spans several artifacts that must be compared and
  updated together. One skill per concern — a generic "sync everything"
  skill has no precise trigger and loads for nothing.

Never install two mechanisms for the same concern. If a sync skill owns a
concern, the entrypoint's sync table must not also list it; duplicated rules
drift apart and contradict each other.

Copy the matching shape from `assets/maintenance-skeletons.md` (path
relative to this skill's root) when creating a workflow entry or a sync
skill.

## Entropy management

Even a well-synced harness accumulates entropy in long-lived projects:
technical debt of the harness itself, built from many small, individually
reasonable changes. Watch for:

- Stale paths, dead commands, and references to removed code.
- Duplicated or contradictory rules that grew in different places.
- Content no pointer reaches anymore, and skills or workflow entries whose
  trigger never fires.
- An entrypoint that has crept past its length budget.
- Constraints thicker than the project still justifies.

For a long-lived project, install a cleanup mechanism — a workflow entry for
a linear periodic review, or a project skill when the review is recurring
and branchy (shapes in the same skeletons file). It scans for the list
above, checks documentation against the implementation, and reports
keep/update/remove recommendations.

## Safety

- Report findings before destructive edits. Delete harness content only
  when local evidence is current and unambiguous, or the user approves.
- Cleanup prompted by an agent failure reports the failure pattern and a
  recommendation first; it does not silently rewrite guidance.
- A mechanism that edits knowledge based on failure history needs the
  controls in [advanced-autonomy.md](advanced-autonomy.md); do not build it
  into an ordinary harness.
