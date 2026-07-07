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
.claude-plugin/marketplace.json  Plugin marketplace (one plugin per catalog)
scripts/                         Repository tooling
justfile                         Canonical check recipes
.gitmessage                      Commit message template
```

## Catalogs

Public skills are grouped into catalogs under `skills/`:

- `core` — skills recommended for global (user-level) installation.
- `devcontainer` — Dev Container authoring skills: developing Features,
  creating Templates, and prebuilding images.
- `engineering` — general programming methodology skills; not tied to a
  specific language or framework.
- `github` — GitHub collaboration workflow skills: MCP-first issue/PR/
  Discussions/Actions operations and conventions authoring, with embedded
  pre-publish review.
- `gitlab` — GitLab collaboration workflow skills: glab-first issue/MR/
  pipeline operations, planning and wiki, and conventions authoring — on
  gitlab.com or self-managed hosts, with embedded pre-publish review.
- `ops` — general workflow operations, not invoked directly by users.

Adding a catalog requires: the catalog scaffold (`README.md`, `README.zh.md`,
`CONTEXT.md`), an entry in this list, and — once it has a skill — a plugin
entry in `.claude-plugin/marketplace.json`. `scripts/validate_skills.py`
cross-checks this list against the directories in `skills/`.

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

## Plugin Marketplace

`.claude-plugin/marketplace.json` publishes the repo as a Claude Code
**plugin marketplace**: one plugin per non-empty catalog. Each entry uses a
marketplace-root `source` (`"./"`) and a `skills` array that **enumerates the
catalog's skill directories** (`./skills/<catalog>/<skill>`). Those exact
paths do double duty: Claude Code loads each as a single skill (and with a
marketplace-root source the explicit list *replaces* the default scan, so a
plugin loads only its own catalog), and the `npx skills add` picker groups
skills under the catalog name by matching each path to a discovered skill.
No skill files move. The empty `ops` catalog is omitted until it has a skill;
project-only skills live in `.agents/skills/` (marked `metadata.internal:
true`) and are excluded.

`scripts/gen_marketplace.py` (via `just gen-marketplace`) regenerates the
`skills` arrays from the catalogs on disk, and the validator fails if any
plugin's list drifts from its catalog — so the lists are never hand-edited.

Users add the marketplace once, then install catalogs individually:

```
/plugin marketplace add ryan-minato/skills
/plugin install <catalog>@ryan-minato-skills
```

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
