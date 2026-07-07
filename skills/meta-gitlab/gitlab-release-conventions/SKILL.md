---
name: gitlab-release-conventions
description: >
  Authors a GitLab project's release conventions: a SemVer versioning
  policy (mapped to commit types when the project uses Conventional
  Commits), a tag-naming rule enforced by a tokenless CI check in tag
  pipelines, a .gitlab/changelog_config.yml that maps Changelog trailer
  values to release-notes categories, a milestone-per-release policy
  with the auto-close decision recorded, and a generated project-level
  agent skill for cutting releases — with an AGENTS.md section as the
  fallback deliverable. Defaults to Free-tier mechanisms on gitlab.com
  or self-managed. Use when standardizing releases on GitLab — "define
  our versioning policy", "set up changelog generation", "configure
  changelog_config.yml", "standardize tag names", "link milestones to
  releases", or "create a skill for cutting releases in this repo".
license: Apache-2.0
---

# GitLab Release Conventions

Author the files that define how a GitLab project versions, tags, and
announces releases: a versioning policy, a tag-format CI check, the
changelog-generation configuration, a notes template, a milestone
policy, and a project-level skill (or AGENTS.md section) that teaches
agents to cut releases the way this project expects. This skill writes
local files — only its outputs land in the project. Cutting an actual
release belongs to `gitlab-releases`; the `Changelog:` trailer habit the
changelog config consumes to `gitlab-commit-conventions`; milestone
lifecycle to `gitlab-planning`.

## Assess the project first

Before authoring anything, inventory what the project already has:
derive `HOST` and `PROJECT_PATH` from `git remote get-url origin` (never
assume gitlab.com); existing tags (`git tag --sort=-v:refname | head
-20` — prefix, semver shape, prerelease habits); existing releases and
their notes style (`glab release list -R PROJECT_PATH`,
`glab release view`); an existing `.gitlab/changelog_config.yml`;
whether commits carry `Changelog:` trailers (the analyzer in
`gitlab-commit-conventions` reports this — without the trailer habit,
generated changelogs come out empty); milestone usage
(`glab milestone list -R PROJECT_PATH`); existing jobs in
`.gitlab-ci.yml` (name collisions); `AGENTS.md` / `CLAUDE.md` for
recorded conventions; and where project skills live — use
`.claude/skills/` if it exists, else `.agents/skills/` if it exists,
else plan to create `.agents/skills/`. Never invent structure parallel
to what the project already defines: build on what exists, or get the
user's explicit approval to replace it.
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

## Versioning and tag policy

Copy [assets/versioning-policy.md](assets/versioning-policy.md) to
`docs/versioning-policy.md` (or the project's docs location) and settle
every `{{...}}` placeholder **with the user**: SemVer is the default;
when `gitlab-commit-conventions` is in place, keep the bump table keyed
to commit types (breaking → major, feat → minor, else patch), otherwise
replace it with the manual bump rule; fix the tag format (default
`vMAJOR.MINOR.PATCH`, regex `^v[0-9]+\.[0-9]+\.[0-9]+(-[0-9A-Za-z]+\.[0-9]+)?$`)
and record whether tags must be annotated (`--tag-message` on create) or
signed (created locally and pushed).

Done when: the policy doc has no `{{...}}` left and matches the tag
scheme the assessment found (or the user approved the change).

## Changelog configuration

Copy [assets/changelog-config.yml](assets/changelog-config.yml) to
`.gitlab/changelog_config.yml`. Its `categories:` keys are `Changelog:`
trailer **values** (case-sensitive); the mapped text is the rendered
section heading. Commits without the trailer are excluded from generated
changelogs entirely — when the project does not yet have the trailer
habit, run `gitlab-commit-conventions` first, or record the
manual-notes path as the project default instead. Also copy
[assets/release-notes-template.md](assets/release-notes-template.md)
next to the policy doc for the hand-written-notes path.

Read
[references/changelog-config-schema.md](references/changelog-config-schema.md)
when editing the config beyond the shipped categories.

Done when: the config's categories match the trailer values the
convention actually uses (or the manual path is recorded).

## Milestone policy

Record in the policy doc whether each release gets a milestone titled
exactly like the version. When it does: `glab release create
--milestone "vX.Y.Z"` associates it and **closes it by default** — the
policy records whether that auto-close is wanted or the generated skill
must pass `--no-close-milestone`. Milestone lifecycle itself belongs to
`gitlab-planning`.

## Tag check in CI

Copy the job in [assets/tag-check-job.yml](assets/tag-check-job.yml)
into `.gitlab-ci.yml` and align both its `rules:` tag pattern and its
`TAG_REGEX` with the policy (the rule polices release tags only, so
convenience tags like `latest` are not failed). The job runs in tag
pipelines, is tokenless, validates the tag name, and verifies the
tagged commit is reachable from the default branch. Validate the edited
`.gitlab-ci.yml` with `glab ci lint` when glab is authenticated.

Done when: the job is in `.gitlab-ci.yml`, parses, and its regex equals
the policy doc's.

## Generate the project-level skill

For the default deliverable, copy
[assets/project-skill-releases.md](assets/project-skill-releases.md) to
`<skills-dir>/<project-name>-releases/SKILL.md` and fill every
`{{PLACEHOLDER}}`:

| Placeholder | Fill with |
|---|---|
| `{{PROJECT_NAME}}` | Project name, lowercase, hyphens only |
| `{{PROJECT_PATH}}` / `{{GITLAB_HOST}}` | From the origin remote |
| `{{POLICY_DOC_PATH}}` | Where the versioning policy doc was installed |
| `{{TAG_FORMAT}}` / `{{TAG_REGEX}}` | From the policy doc |
| `{{BUMP_RULE}}` | The policy doc's bump rule, one sentence |
| `{{NOTES_RULE}}` | The notes rule (glab changelog generate, or the template path) |
| `{{NOTES_RULE_SHORT}}` | The same as one imperative clause |
| `{{MILESTONE_RULE}}` | The milestone policy, incl. the auto-close decision |
| `{{EXTRA_CREATE_FLAGS}}` | Extra `glab release create` flags the policy implies (`--tag-message` for annotated tags, `--no-close-milestone`), or empty |

For the AGENTS.md fallback, copy
[assets/agents-md-releases-section.md](assets/agents-md-releases-section.md)
into the project's `AGENTS.md` and fill the same placeholders (it uses a
subset). Refinement beyond the template pairs with `great-skill-writer`
(`npx skills add ryan-minato/skills --skill great-skill-writer`).

Done when: the generated deliverable contains no `{{...}}` placeholder
and (for a skill) its frontmatter `name` matches its directory name.

## Deliver

Everything this skill wrote is local files — nothing is published yet. Hand
the changes to the project's normal git flow (branch, commit, review); that
flow, not this skill, publishes them and carries its own review gates.
Done when: the user has the list of every file created or changed, one line
each on what it does, and any follow-up steps (the trailer habit to adopt
first, the first tag to watch the check on).

## Gotchas

- `changelog_config.yml` affects only changelog **generation** (`glab
  changelog generate` and the REST changelog endpoint) — the release
  description is still whatever gets passed to `glab release create`.
- Trailer values match `categories:` keys case-sensitively — a commit
  with `Changelog: Added` lands nowhere when the key is `added`.
- GitLab has no draft releases: nothing this skill configures changes
  the fact that `glab release create` publishes immediately — the
  generated skill's gate runs before create, and CI must never create
  releases with unreviewed notes.
- The tag check validates tags after they are pushed; it cannot prevent
  the push. Pair it with the generated skill (which picks compliant
  names up front) rather than relying on CI alone.
- Policy documents take effect socially — the CI tag check is the only
  hard enforcement this skill ships; say so to the user rather than
  implying more.
- When both this skill and `gitlab-commit-conventions` run, run
  commit-conventions first: the changelog config consumes the trailer
  habit it establishes.
