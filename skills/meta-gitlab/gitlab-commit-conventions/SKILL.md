---
name: gitlab-commit-conventions
description: >
  Authors a GitLab project's commit conventions: a Conventional-Commits
  rule set tailored from the project's actual git history and including
  the Changelog trailer that powers GitLab changelog generation, a
  dependency-free Python validator committed into the repo, a tokenless
  CI job that validates every commit in merge request pipelines, and a
  generated project-level agent skill for writing compliant messages —
  with an AGENTS.md section as the fallback deliverable. Works on
  gitlab.com and self-managed instances; push-rule enforcement is marked
  Premium. Use when standardizing commit messages on GitLab — "set up
  conventional commits", "enforce commit format in CI", "add Changelog
  trailers", "define our commit types", or "create a skill for writing
  commits in this repo".
license: Apache-2.0
compatibility: >
  scripts/analyze_history.py and the shipped assets/check_commits.py
  require Python 3.9+ (stdlib only) and git.
---

# GitLab Commit Conventions

Author the files that define how a GitLab project's commit messages are
written and enforced: a convention document grounded in the history the
project already has, a validator that ships *into* the repository, a
tokenless CI job that runs it on every merge request, and a project-level
skill (or AGENTS.md section) that teaches agents to write compliant
messages. The convention includes the **`Changelog:` Git trailer** by
default — it is what `glab changelog generate` and
`gitlab-release-conventions` build on. This skill writes local files —
only its outputs land in the project. Day-to-day MR operations belong to
`gitlab-merge-requests`; release and tag policy to
`gitlab-release-conventions`.

## Assess the project first

Before authoring anything, inventory what the project already has: run
[scripts/analyze_history.py](scripts/analyze_history.py) —

```bash
python3 scripts/analyze_history.py --max 500
```

— which prints one JSON object: how many recent titles already follow a
`type:` prefix or gitmoji style, the type and scope frequencies, subject
lengths, and the trailer keys in use (a `Changelog` row here means the
project already feeds changelog generation). Also check: commit rules
already stated in `CONTRIBUTING.md` / `AGENTS.md` / `CLAUDE.md`, a
`.gitmessage` template, existing jobs in `.gitlab-ci.yml` (name
collisions; whether jobs run as classic branch pipelines — no
`rules:`/`workflow:` keys — which the CI section below cares about),
whether the project squash-merges (`glab api projects/:fullpath` →
`squash_option`), and where project skills live — use `.claude/skills/`
if it exists, else `.agents/skills/` if it exists, else plan to create
`.agents/skills/`. Never invent structure parallel to what the project
already defines: build on what exists, or get the user's explicit
approval to replace it.
Done when: the inventory is written down and each deliverable below is
marked "new", "extends existing", or "replaces (approved)".

## Choose the deliverable

The default deliverable for workflow guidance is a **project-level agent
skill** in the skills directory found during assessment. When the project's
harness does not support skills, or the user prefers documentation, deliver
an `AGENTS.md` section (create the file if missing) or a standalone doc
instead. Ask the user once, before generating, and record the choice. All
other artifacts (templates, configs, CI jobs, validators) ship regardless
of this choice.

## Define the convention

Copy [assets/commit-conventions.md](assets/commit-conventions.md) to
`docs/commit-conventions.md` (or the project's docs location) and settle
every `{{...}}` placeholder **with the user**, informed by the analyzer
report: keep the types the history actually uses, add missing standard
ones deliberately, decide whether scopes are required and from what set,
fix the subject length limit, and decide the `Changelog:` trailer rule —
the default is "every user-facing commit carries `Changelog: <category>`",
because that single habit is what makes `glab changelog generate` work
downstream.

Done when: the convention doc has no `{{...}}` left and the user has
approved the types table, scope rule, and trailer rule.

## Install the validator

Copy [assets/check_commits.py](assets/check_commits.py) to
`scripts/check_commits.py` in the target repository and edit its `CONFIG`
block (top of file) to match the convention doc exactly: types, scope
rule, subject cap. The validator is python3-stdlib-only, so it runs on
any CI runner and any contributor machine with no installation.

Smoke-test it against the project's own recent history:

```bash
python3 scripts/check_commits.py --range HEAD~20..HEAD || true
```

Findings on historical commits are expected when the convention is new —
the CI job below validates only new MR commits, never history.

Done when: the validator exits 0 on a compliant test message
(`python3 scripts/check_commits.py --message "feat: add x"`) and reports
findings, not a crash, on the history sample.

## CI validation

Copy the job in [assets/commit-check-job.yml](assets/commit-check-job.yml)
into the project's pipeline config — `.gitlab-ci.yml`, or a file it
`include:`s (job `rules:` are evaluated the same either way; create
`.gitlab-ci.yml` with just this job if the project has none). The job runs
in merge request pipelines (Free),
is tokenless (safe on fork MRs — never add secrets to it), sets
`GIT_DEPTH: "0"` so the merge base is present, and validates
`$CI_MERGE_REQUEST_DIFF_BASE_SHA..$CI_COMMIT_SHA` with the committed
validator. If the assessment found classic branch pipelines, adding an
MR-event job can spawn duplicate pipelines — resolve that with the user
the same way `gitlab-mr-conventions` does. If the project squash-merges,
read [references/rule-customization.md](references/rule-customization.md)
for the MR-title variant.

Validate the edited `.gitlab-ci.yml` with `glab ci lint` when glab is
authenticated for the host.

Done when: the job is in `.gitlab-ci.yml`, the YAML parses (or `glab ci
lint` passes), and it references the validator path it was actually
installed at.

## Generate the project-level skill

For the default deliverable, copy
[assets/project-skill-commits.md](assets/project-skill-commits.md) to
`<skills-dir>/<project-name>-commits/SKILL.md` and fill every
`{{PLACEHOLDER}}`:

| Placeholder | Fill with |
|---|---|
| `{{PROJECT_NAME}}` | Project name, lowercase, hyphens only |
| `{{CONVENTION_DOC_PATH}}` | Where the convention doc was installed |
| `{{TYPES_TABLE}}` | The convention doc's type → use-for table |
| `{{TYPES_LIST}}` | The same types as one comma-separated line |
| `{{SCOPE_RULE}}` | The scope rule sentence from the convention doc |
| `{{TRAILER_RULE}}` | The Changelog-trailer rule sentence |
| `{{SUBJECT_MAX}}` / `{{BODY_LINE_MAX}}` | The limits set in CONFIG |

For the AGENTS.md fallback, copy
[assets/agents-md-commits-section.md](assets/agents-md-commits-section.md)
into the project's `AGENTS.md` and fill the same placeholders (it uses
the list form, not the table). Refinement beyond the template pairs with
`great-skill-writer`
(`npx skills add ryan-minato/skills --skill great-skill-writer`).

Done when: the generated deliverable contains no `{{...}}` placeholder
and (for a skill) its frontmatter `name` matches its directory name.

## Deliver

Everything this skill wrote is local files — nothing is published yet. Hand
the changes to the project's normal git flow (branch, commit, review); that
flow, not this skill, publishes them and carries its own review gates.
Done when: the user has the list of every file created or changed, one line
each on what it does, and any follow-up steps ("Pipelines must succeed" to
enable, the first MR to watch the job on).

## Gotchas

- `GIT_DEPTH: "0"` on the job is load-bearing: GitLab's default shallow
  clone may not contain the merge base, so the range cannot resolve and
  git fails the job with "bad object" — not a silent pass.
- `$CI_MERGE_REQUEST_DIFF_BASE_SHA` (and the other `CI_MERGE_REQUEST_*`
  variables) exist only in merge request pipelines — the job's `rules:`
  keeps it out of branch and tag pipelines, where the range would be
  empty.
- Merge, revert, and `fixup!`/`squash!` commits are exempted by pattern
  in the validator — hand-tightening the regexes to catch them again
  breaks normal GitLab merge flows.
- Validate only the MR range. Running the validator over all history as
  a blocking job makes the convention retroactive and every MR red.
- In squash-merge projects the **MR title** becomes the squash commit's
  subject by default — validate it too (the variant in
  references/rule-customization.md), or the enforced range disappears at
  merge time.
- The validator and the convention doc drift independently — the CONFIG
  block is the enforced truth; when the user changes the doc, change
  CONFIG in the same commit.
- CI validation is advisory until Settings > Merge requests > "Pipelines
  must succeed" is on (Free); hard server-side enforcement is a Premium
  push rule — see
  [references/push-rules-premium.md](references/push-rules-premium.md).
