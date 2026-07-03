# Architecture

How this repository's mechanisms fit together. For day-to-day conventions,
start at [AGENTS.md](AGENTS.md). This file is repo-only documentation and is
not part of the Linear-synced knowledge base.

## Layout

```
skills/<catalog>/<skill-name>/   Public, distributable skills
  <catalog>/README.md            What the catalog is for + skill table (EN)
  <catalog>/README.zh.md         Content-identical Chinese translation
  <catalog>/CONTEXT.md           Catalog-scoped rules and reference URLs
.agents/
  skills/                        Skills visible to this repo's agents
  knowledge/                     Local knowledge base (synced to Linear)
.claude/skills -> ../.agents/skills
.claude-plugin/plugin.json       Public skill list (plugin manifest)
scripts/                         Repository tooling
justfile                         Canonical check recipes
.gitmessage                      Commit message template
```

## Skill Visibility (symlink mechanism)

`.agents/skills/` is the canonical directory agents scan for this repo's
usable skills (the cross-client convention from the Agent Skills spec). It
contains two kinds of entries:

- **Project-only workflow skills** (`issue-workflow`, `knowledge-sync`,
  `skill-authoring`):
  real directories, created directly here. They serve this repo's own
  workflows, are never distributed, and may reference repo paths.
- **Symlinks to public skills**: every `skills/<catalog>/<name>/` gets a
  relative symlink `.agents/skills/<name> -> ../../skills/<catalog>/<name>`,
  so the repo can dogfood the skills it publishes.

Claude Code only scans `.claude/skills/` for project skills, so
`.claude/skills` is a directory symlink to `.agents/skills`. Other clients
(Codex, Copilot, and anything following the spec) scan `.agents/skills/`
directly.

`scripts/validate_skills.py` (via `just validate` and pre-commit) enforces
that symlinks exist, don't dangle, and point to the right targets.

## Public Skill List (plugin manifest)

`.claude-plugin/plugin.json` declares the catalog directories in its
`skills` array. Everything under those paths is public; project-only skills
live in `.agents/skills/` and are therefore excluded by construction. Users
install skills either as a Claude Code plugin or per-skill with
`npx skills add ryan-minato/skills`.

Because installed skills are copied out of this repo, public skills must be
fully self-contained (rules in `.agents/knowledge/skill-quality.md`).

## Knowledge Base Sync

`.agents/knowledge/*.md` is the local, git-tracked knowledge base. Each file
maps to one Linear Document in project "Skills" (team "Aoi"). The
`knowledge-sync` project skill performs the on-demand sync.

Source of truth: **the knowledge files on origin's latest default branch**.
The sync always pushes that version to Linear; edits made directly in Linear
are overwritten. Working-tree edits become authoritative only once merged to
the default branch.

## Quality Gates

- `just check` = `validate` (skill layout/consistency) + `lint` (ruff over
  `scripts/`) + `pre-commit run --all-files` (whitespace, secrets scanning,
  ruff, validator).
- pre-commit hooks are installed by `just setup` (run automatically by the
  devcontainer's `postCreateCommand`), which also sets the `.gitmessage`
  commit template.
- CI runs secret scanning only (`.github/workflows/secret.yml`); other
  checks are local by design.

Longer custom logic belongs in `scripts/`, not inline in justfile recipes or
hooks.
