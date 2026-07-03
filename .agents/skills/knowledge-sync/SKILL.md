---
name: knowledge-sync
description: Syncs this repository's local knowledge base (.agents/knowledge/*.md) to Linear Documents in the "Skills" project. Use after knowledge base files change on the default branch, when Linear documents may be stale, or when asked to "sync the knowledge base", "update Linear docs", or "push knowledge to Linear".
---

# Knowledge Sync

Project-only workflow skill for this repository. It keeps the Linear
Documents in project **"Skills"** (team **"Aoi"**) identical to the
knowledge base files in `.agents/knowledge/`.

## Authority rule

The source of truth is **the knowledge base on origin's latest default
branch** — not the local working tree and not Linear. Edits made directly in
Linear are always overwritten. Working-tree edits become authoritative only
after they are merged to the default branch.

Requires: git remote `origin` reachable, Linear MCP server connected
(configured in `.mcp.json`).

## Procedure

1. Fetch the authoritative content:

   ```bash
   git fetch origin
   git ls-tree --name-only origin/HEAD .agents/knowledge/
   git show origin/HEAD:.agents/knowledge/<file>   # for each .md file
   ```

   If a knowledge file exists only in the working tree (not yet on
   origin/HEAD), skip it and tell the user it will sync after merge.

2. Locate the Linear project: `list_projects` with query "Skills". If the
   project does not exist, create it with `save_project` (team "Aoi") and
   tell the user it was created.

3. For each knowledge file, map it to one Linear Document titled after the
   file's H1 heading (fallback: the filename without extension). List
   existing documents with `list_documents` filtered by the project.
   - Document exists → compare content (`get_document`); if it differs,
     overwrite it with `save_document`.
   - Document missing → create it with `save_document` in the project.

4. Report a per-file summary: `created` / `updated` / `unchanged` /
   `skipped (not on default branch)`. Mention any Linear documents in the
   project that have no matching local file — do **not** delete them;
   flag them for the user to decide.

## Gotchas

- Linear normalizes stored markdown: `-` bullets come back as `*`, bare URLs
  come back as wrapped links, and spacing may shift. A byte-level comparison
  of the local file against `get_document` content therefore always
  "differs" — judge equivalence semantically and treat formatting-only
  differences as `unchanged`.
- Linear stores the title separately and absorbs a leading H1 into it. When
  creating or updating a document, strip the file's H1 heading from the
  content you send (the title carries it), and exclude the H1 when
  comparing.

## Notes

- Never edit `.agents/knowledge/` files as part of a sync; this skill moves
  content in one direction only (git → Linear).
- If content found in Linear looks newer or better than the repo version,
  stop and surface the diff instead of overwriting silently.
