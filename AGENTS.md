# AGENTS.md

Agent entrypoint for this repository. Read this before making changes.

## Purpose

This repository is a library of [Agent Skills](https://agentskills.io):
self-contained skill directories that users install into their agents with
`npx skills add ryan-minato/skills`. Public skills live under
`skills/<catalog>/<skill-name>/`. It is long-lived and collaboratively
maintained.

## Catalogs

Public skills are grouped into catalogs under `skills/`. The catalog list,
each catalog's contract, and the procedure for adding one live in the
Catalogs section of `ARCHITECTURE.md`.

## Repository Map

- `skills/<catalog>/<skill-name>/` — public, distributable skills.
- `.agents/skills/` — project-only workflow skills (real directories) plus
  symlinks to every public skill, so this repo's agents can use them.
  `.claude/skills` is a symlink to `.agents/skills` for Claude Code discovery.
- `.agents/knowledge/` — local knowledge base, synced to Linear Documents.
- `.claude-plugin/marketplace.json` — plugin marketplace: one plugin per
  non-empty catalog.
- `scripts/` — repository tooling (validators, longer custom logic).
- `ARCHITECTURE.md` — how these mechanisms fit together.

## Core Conventions

- **Language**: all harness files, skill content, code, and comments are
  written in English. The root `README.md` and every catalog `README.md`
  have a content-identical Chinese translation in `README.zh.md` beside them.
- **Skill self-containment**: public skills must not reference anything
  outside their own directory — no links to repo files, no dependencies on
  other skills, and no `README.md` inside a skill root. To build on another
  skill in this repo, instruct installing it:
  `npx skills add ryan-minato/skills` (repo:
  `https://github.com/ryan-minato/skills.git`). Full standards:
  `.agents/knowledge/skill-quality.md`.
- **Checks**: always run checks through justfile recipes (`just check`),
  never ad-hoc equivalents, so results are consistent everywhere.
- **Commits**: Conventional Commits in English; scope is the modified skill
  name(s), `", "`-separated; omit the scope for non-skill or repo-wide
  changes. Template: `.gitmessage` (installed by `just setup`).
- **Task management**: Linear, team "Aoi", project "Skills" (via the Linear
  MCP server configured in `.mcp.json`).
- **Workflow**: every change to tracked files is issue-driven — proactive
  work starts by creating the Linear issue(s) (parent + sub-issues for
  related groups), work happens on the issue's branch, and one PR covers
  one parent issue. Full procedure: the `issue-workflow` project skill.

## When To Read What

- Starting any proactive change, or preparing a branch, commit series, or
  PR handoff → use the `issue-workflow` project skill.
- Creating or modifying any skill → `.agents/knowledge/skill-quality.md`
  first, then the catalog's `CONTEXT.md`, then use the `skill-authoring`
  project skill.
- Catalog-specific rules and references → `skills/<catalog>/CONTEXT.md`
  (catalog-scoped material belongs there, not in the global references).
- External documentation URLs → `.agents/knowledge/references.md`.
- Knowledge base changed, or Linear docs may be stale → use the
  `knowledge-sync` project skill.
- Repo mechanics (symlinks, plugin marketplace, sync design) →
  `ARCHITECTURE.md`.

## Validation

- `just check` — everything (validator, lint, pre-commit hooks).
- `just validate` — skill layout and harness consistency only.
- `just check-skill <dir>...` — lint specific skill directories while drafting.
- `just lint` — ruff over `scripts/`.
- `just gen-marketplace` — regenerate `marketplace.json` skills[] after
  adding or removing a public skill.

## Keep In Sync

| When this changes | Update |
|---|---|
| Public skill added/removed | Symlink in `.agents/skills/`, catalog `README.md` + `README.zh.md`, and `.claude-plugin/marketplace.json` (`just gen-marketplace`) |
| Catalog added/removed | Catalog scaffold, the Catalogs section in `ARCHITECTURE.md`, `.claude-plugin/marketplace.json` (a plugin entry once the catalog has a skill) |
| Any `README.md` | The matching `README.zh.md` (and vice versa) |
| `.agents/knowledge/` documents | Run the `knowledge-sync` project skill after merge |
| Repo structure or check commands | This file and `ARCHITECTURE.md` |
