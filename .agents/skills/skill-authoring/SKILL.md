---
name: skill-authoring
description: End-to-end workflow for creating or modifying a skill in this repository — scaffolding, symlinks, marketplace manifest, catalog READMEs, validation, and commit. Use when asked to "create a skill", "add a skill to a catalog", "move a skill", "remove a skill", or when modifying any skill under skills/ or .agents/skills/.
---

# Skill Authoring

Project-only workflow skill for this repository. Follow it whenever a skill
is created, modified, moved, or removed.

## Define the skill first

Answer these before creating any files; they decide whether the skill is
worth building and where it belongs:

1. What task does the skill cover? Is it one coherent unit of work (not a
   grab-bag, not a sliver of a larger workflow)?
2. When should it trigger — including indirect phrasings a user might say
   without naming the domain?
3. What does the agent lack without it? If the agent already handles the
   task well, do not build the skill.

## Before writing anything

1. Read `.agents/knowledge/skill-quality.md` — the quality bar every skill
   must meet (scoping, structure, spec limits, self-containment,
   description/body standards, instruction patterns, progressive
   disclosure, script rules).
2. Decide where the skill lives:
   - **Public skill** (distributable): `skills/<catalog>/<skill-name>/`.
     Pick the catalog from the list in `ARCHITECTURE.md` (Catalogs section)
     and read that catalog's `CONTEXT.md` for catalog-specific requirements.
   - **Project-only workflow skill** (serves this repo itself):
     `.agents/skills/<skill-name>/` as a real directory.

## Creating a public skill

1. Scaffold `skills/<catalog>/<skill-name>/SKILL.md` with `name` (must equal
   the directory name) and `description` frontmatter. Add `scripts/`,
   `references/`, or `assets/` only when a file is going into them. No
   README.md in the skill root; content in English; nothing may reference
   paths outside the skill directory. While drafting, lint the skill in
   isolation:

   ```bash
   just check-skill skills/<catalog>/<skill-name>
   ```

2. Symlink it into the agent-visible directory (relative link, from repo
   root):

   ```bash
   ln -s ../../skills/<catalog>/<skill-name> .agents/skills/<skill-name>
   ```

3. A new catalog's **first** skill needs a plugin entry in
   `.claude-plugin/marketplace.json`
   (`{ "name": "<catalog>", "source": "./", "skills": ["./skills/<catalog>"] }`);
   adding a skill to an already-published catalog needs no marketplace change.
4. Add the skill to the catalog's `README.md` **and** `README.zh.md` tables.

## Creating a project-only skill

1. Create `.agents/skills/<skill-name>/SKILL.md` (real directory, no
   symlink, never listed in marketplace.json or catalog READMEs).
2. Repo path references are allowed here, but all other quality standards
   still apply.

## Removing or moving a skill

Remove/update the symlink in `.agents/skills/`, the catalog README.md +
README.zh.md entries, and `.claude-plugin/marketplace.json` if the catalog
became empty (remove its entry) or was renamed. The validator catches
anything missed.

## Finish

1. Walk the "Checklist before committing" in
   `.agents/knowledge/skill-quality.md`.
2. Run `just check` (repo-wide validation, including symlinks, the
   marketplace manifest, and catalog consistency) and fix everything it
   reports; warnings deserve a look even though they don't fail.
3. Commit using the repository convention (`.gitmessage`): Conventional
   Commits, scope = the skill name, e.g.
   `feat(<skill-name>): add <skill-name> skill`.
