---
name: github-release-conventions
description: >
  Authors a repository's release conventions: a SemVer versioning policy
  (mapped to commit types when the repo uses Conventional Commits), a
  tag-naming rule enforced by a first-party-only CI check, a
  .github/release.yml that keys generated release notes to the label
  taxonomy, a release-notes template, and a generated project-level agent
  skill for cutting releases — with an AGENTS.md section as the fallback
  deliverable. Use when standardizing releases — "define our versioning
  policy", "set up release notes categories", "standardize tag names",
  "create a release checklist", or "create a skill for cutting releases
  in this repo".
license: Apache-2.0
---

# GitHub Release Conventions

Author the files that define how a repository versions, tags, and
announces releases: a versioning policy, a tag-format CI check, the
generated-notes configuration, a notes template, and a project-level
skill (or AGENTS.md section) that teaches agents to cut releases the way
this repository expects. This skill writes local files — only its outputs
land in the repository. Cutting an actual release belongs to
`github-releases`; the label taxonomy that release notes categorize by to
`github-issue-conventions`; commit-message rules to
`github-commit-conventions`.

## Assess the project first

Before authoring anything, inventory what the repository already has:
existing tags (`git tag --sort=-v:refname | head -20` — prefix, semver
shape, prerelease habits), existing releases and their notes style
(`gh release list -R O/R --limit 5`, `gh release view -R O/R`), an
existing `.github/release.yml`, whether the label taxonomy exists
(`gh label list -R O/R` — release-notes categories key on labels),
whether commit messages follow Conventional Commits (type-mapped bump
rules only work then), existing release automation in
`.github/workflows/`, `AGENTS.md` / `CLAUDE.md` for recorded
conventions, and where project skills live — use `.claude/skills/` if it
exists, else `.agents/skills/` if it exists, else plan to create
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
other artifacts (templates, configs, workflows, validators) ship regardless
of this choice.

## Versioning and tag policy

Copy [assets/versioning-policy.md](assets/versioning-policy.md) to
`docs/versioning-policy.md` (or the project's docs location) and settle
every `{{...}}` placeholder **with the user**: SemVer is the default;
when `github-commit-conventions` is in place, keep the bump table keyed
to commit types (breaking → major, feat → minor, else patch), otherwise
replace it with the manual bump rule; fix the tag format (default
`vMAJOR.MINOR.PATCH`, regex `^v[0-9]+\.[0-9]+\.[0-9]+(-[0-9A-Za-z]+\.[0-9]+)?$`)
and record whether tags must be annotated or signed.

Done when: the policy doc has no `{{...}}` left and matches the tag
scheme the assessment found (or the user approved the change).

## Notes configuration

Copy [assets/release-config.yml](assets/release-config.yml) to
`.github/release.yml` and map its `categories:` labels to the labels the
repository actually has — every referenced label must exist, or PRs fall
into the catch-all silently (the same silent-drop hazard as issue
forms). When the label taxonomy is missing, run
`github-issue-conventions` first — this file keys on it. Also copy
[assets/release-notes-template.md](assets/release-notes-template.md)
next to the policy doc for the hand-written-notes path.

Read [references/release-yml-schema.md](references/release-yml-schema.md)
when editing the config beyond the shipped categories.

Done when: every label in `.github/release.yml` exists in the
repository.

## Tag check in CI

Copy [assets/workflow-tag-check.yml](assets/workflow-tag-check.yml) to
`.github/workflows/tag-check.yml` and set both its trigger pattern and
its regex to the policy's tag format (the trigger polices release tags
only, so convenience tags like `latest` are not failed). It runs on tag pushes, validates the tag name, and verifies the
tagged commit is reachable from the default branch — a wrong-format or
off-branch tag fails the run with a fix-it message before anyone
releases from it. First-party actions only; the checks are plain `run:`
steps.

Done when: the workflow parses and its regex equals the policy doc's.

## Generate the project-level skill

For the default deliverable, copy
[assets/project-skill-releases.md](assets/project-skill-releases.md) to
`<skills-dir>/<repo-name>-releases/SKILL.md` and fill every
`{{PLACEHOLDER}}`:

| Placeholder | Fill with |
|---|---|
| `{{REPO_NAME}}` / `{{OWNER_REPO}}` | From the origin remote |
| `{{POLICY_DOC_PATH}}` | Where the versioning policy doc was installed |
| `{{TAG_FORMAT}}` / `{{TAG_REGEX}}` | From the policy doc |
| `{{BUMP_RULE}}` | The policy doc's bump rule, one sentence |
| `{{NOTES_RULE}}` | The notes rule (generated via release.yml, or the template path) |
| `{{NOTES_RULE_SHORT}}` | The same as one imperative clause |
| `{{EXTRA_CREATE_FLAGS}}` | Extra `gh release create` flags the policy implies (for example `--verify-tag` for annotated tags), or empty |

The template pre-wires the draft-first flow from `github-releases`, the
repository's tag rule, and the condensed pre-publish gate. For the
AGENTS.md fallback, copy
[assets/agents-md-releases-section.md](assets/agents-md-releases-section.md)
into the project's `AGENTS.md` and fill the same placeholders (it uses a
subset).
Refinement beyond the template pairs with `great-skill-writer`
(`npx skills add ryan-minato/skills --skill great-skill-writer`).

Done when: the generated deliverable contains no `{{...}}` placeholder
and (for a skill) its frontmatter `name` matches its directory name.

## Deliver

Everything this skill wrote is local files — nothing is published yet. Hand
the changes to the project's normal git flow (branch, commit, review); that
flow, not this skill, publishes them and carries its own review gates.
Done when: the user has the list of every file created or changed, one line
each on what it does, and any follow-up steps (labels to create first, the
first tag to watch the check on).

## Gotchas

- `.github/release.yml` affects only `--generate-notes` and web-generated
  notes — it does not validate tags, gate releases, or touch manual
  notes.
- Categories match by PR **labels**, never by commit messages — an
  unlabeled PR lands in the `*` catch-all category regardless of its
  commit types.
- The order of `categories:` entries is the order sections render in;
  the `*` exclude catch-all must come last or it swallows later
  categories.
- The tag-check workflow validates tags after they are pushed; it cannot
  prevent the push. Pair it with the generated skill (which picks
  compliant names up front) rather than relying on CI alone.
- Policy documents take effect socially — the CI tag check is the only
  hard enforcement this skill ships; say so to the user rather than
  implying more.
- When both this skill and `github-issue-conventions` run, run
  issue-conventions first: release.yml categories key on its label
  taxonomy.
