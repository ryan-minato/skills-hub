---
name: github-releases
description: >
  Operates GitHub releases and their tags through a draft-first flow:
  create the release as a draft, generate or author the notes, upload
  assets, run the review gate, then publish — plus edit, prerelease and
  latest handling, tag creation and cleanup, and reading existing
  releases. Use when cutting or managing a release — "create a release",
  "tag v1.2.0 and release it", "draft the release notes", "generate a
  changelog for the release", "upload this binary to the release",
  "publish the draft", "mark it as a prerelease", or "delete the
  release". Reading releases of a repository you are only researching
  belongs to github-repo-research; versioning and tag-naming policy to
  github-release-conventions.
license: Apache-2.0
compatibility: >
  scripts/next_version.py requires Python 3.9+ (stdlib only); reading
  local tags requires git in the repository checkout.
---

# GitHub Releases

Cut and manage releases: pick the next version, draft the release with
generated or hand-written notes, attach assets, publish, edit, or delete.
This skill owns releases and their tags. Reading releases of a repository
under investigation belongs to `github-repo-research`; the versioning and
tag-naming *policy* (and `.github/release.yml` authoring) to
`github-release-conventions`; milestones to `github-planning`.

## Choose your path (do this first, once per session)

1. Look at the tools available in this session. If a connected MCP server
   provides GitHub tools for the work this skill covers (each tool's
   description states its purpose; names vary across server versions), use
   the **MCP** column of every table below, picking the tool whose
   description matches the row's capability.
   The MCP column applies only to rows that name a capability; rows marked
   `—` have no MCP tool — those rows use the gh column instead: check
   `gh auth status` before running one, and if gh is not authenticated,
   stop and tell the user that row needs gh. Every release **write** is a
   `—` row: MCP covers reads only.
2. Otherwise run `gh auth status`. If it exits 0, use the **gh** column.
3. Otherwise stop and tell the user GitHub tooling is not set up. This skill
   pairs with `github-tooling-setup`. If it is not installed, install it from
   https://github.com/ryan-minato/skills.git:

       npx skills add ryan-minato/skills --skill github-tooling-setup

4. Use one column per row — rows marked `—` are the one sanctioned switch
   to gh on the MCP path. Within a single operation, never mix MCP and gh.

## Identify the repository

Run `git remote get-url origin`. The owner/repo pair is the path right
after the host, with any trailing `.git` stripped. If there is no origin
remote, or the user named a different repository, use that instead.
Substitute the pair wherever the tables show `O/R` (gh: `-R O/R`; MCP: the
owner and repo parameters).

## Match the project's conventions (before any create)

Before creating anything, discover what the repository already defines and
use it — never invent parallel structure:

| Artifact | How to check |
|---|---|
| Tag scheme | `git tag --sort=-v:refname | head -20` — prefix (`v` or none), semver shape, prerelease suffixes |
| Prior notes style | `gh release view -R O/R --json tagName,body -q .body` (latest release) — heading structure, categories, tone |
| Notes config | `.github/release.yml` present? → generated notes are the project's default |
| Release policy | a project-level release skill, an AGENTS.md release section, or a versioning-policy doc — binding when present |
| Matching milestone | `gh api "repos/O/R/milestones?state=open" -q '.[].title'` — a milestone titled like the version should be closed as part of the release |

If a project-level convention skill or an AGENTS.md conventions section
covers this task, follow it over this skill's defaults.
Done when: the version string and tag name follow the existing scheme (or
the user approved a new one), and the notes plan matches the project's
style.

## Authoring defaults

Write all published text — titles, bodies, comments, notes — as
professional, concise prose. Default to English unless the user or the
project's own conventions call for another language. State facts and
requests directly; no filler, and no emojis unless the project's existing
content uses them. The project's templates and conventions win over these
defaults.

## Pre-publish gate (mandatory)

Everything you send becomes public the moment the call succeeds: title, body,
every comment, labels, commit messages, the full diff, attachment contents,
and the branch name. Publishing a release publishes the notes, the tag, and
every asset, and notifies watchers — the draft step exists so this gate
always runs before the release goes live. Before ANY call that creates or
edits public content:

1. Prefer a clean-context subagent review when one is available. Give it only
   the exact final release text or files under review, with no extra intent
   or reassurance.
2. Otherwise review the exact final release yourself. Short release names,
   tags, and comments may be inspected directly. Long notes, generated
   notes, attachments, screenshots, assets, or content too large to inspect
   reliably inline must be written to a scratch directory and reviewed from
   disk.
3. Check every artifact for secrets or credentials, personal data, internal
   identifiers or URLs, accidental unrelated content, and wording a
   maintainer would regret publishing. Any finding means
   `SAFE TO PUBLISH: NO`.
4. Publish only after the verdict is exactly `SAFE TO PUBLISH: YES`. On
   `NO`, fix every finding and review the exact final content again. Never
   edit-and-publish without re-review.

Never publish unreviewed content. Only the user may skip this gate,
explicitly; record the skip in your summary.
Done when: a `SAFE TO PUBLISH: YES` verdict exists for the exact content
being sent.

In this skill the gate runs once on the assembled draft — title, notes
file, tag name, and the asset file list — before `--draft=false`. Draft
creation itself is low-exposure (drafts are visible to collaborators
only), but genuinely sensitive content must not even enter a draft.

## Create a release (draft-first)

1. **Pick the version.** Follow the project's policy; mechanical bumps:
   `python3 scripts/next_version.py --bump patch` (or `minor`/`major`;
   `--pre rc` for a prerelease; `--latest vX.Y.Z` when local tags are not
   the source of truth). The output is `TAG` below.
2. **Decide tag creation.** Default: let GitHub create the tag —
   `--target BRANCH` pins what it points at. If the project requires
   annotated or signed tags: `git tag -a TAG -m "MSG"` (or `-s`), `git
   push origin TAG`, then add `--verify-tag` to the create call.
3. **Write the notes** to `NOTES.md` per the decision table below.
4. **Create the draft** (assets optional, `path#Display label` form):

       gh release create TAG -R O/R --draft --title "TITLE" \
         --notes-file NOTES.md [--target BRANCH] [--prerelease] \
         [--verify-tag] [ASSET_FILES...]

5. **Run the gate** over title, NOTES.md, tag name, and the asset list.
6. **Publish:** `gh release edit TAG -R O/R --draft=false [--latest]`.
7. Close the matching milestone if one exists (`github-planning` owns the
   how); report the release URL.

Done when: the release URL is reported and `gh release view TAG -R O/R
--json isDraft` shows `false`.

## Notes

| Situation | Path |
|---|---|
| `.github/release.yml` exists, or the user wants generated notes | Add `--generate-notes` to the create call (with `--notes-start-tag PREV` for a non-adjacent range); to curate before the gate, generate into the draft, copy the body into NOTES.md, edit, then `gh release edit TAG --notes-file NOTES.md` |
| Hand-written notes | Compose NOTES.md from `git log PREV..HEAD --oneline` grouped by kind, matching the prior notes style found above |
| Notes from an annotated tag message | `--notes-from-tag` on the create call |

Read [references/notes-generation.md](references/notes-generation.md)
when generating notes (release.yml categories, start tags, the REST
preview endpoint).

## Read, list, edit, delete

| Task | MCP capability | gh command |
|---|---|---|
| List releases | list releases | `gh release list -R O/R --limit 20` |
| Read one / latest | read a release by tag / the latest release | `gh release view TAG -R O/R` (omit `TAG` for latest) |
| Edit title/notes/flags | — | `gh release edit TAG -R O/R [--title "T"] [--notes-file NOTES.md] [--prerelease] [--latest]` (gate on text changes) |
| Upload / replace assets | — | `gh release upload TAG FILE... -R O/R [--clobber]` |
| Delete an asset | — | `gh release delete-asset TAG ASSET_NAME -R O/R --yes` |
| Delete a release | — | `gh release delete TAG -R O/R --yes [--cleanup-tag]` — confirm with the user first |

Read [references/release-recipes.md](references/release-recipes.md) for
the long tail (discussion category, releasing from a non-default branch,
checksums, republishing).

## Gotchas

- `gh release create` without an existing tag creates a **lightweight**
  tag at `--target` (default branch tip by default). Projects requiring
  annotated/signed tags must create the tag with git first (step 2) —
  `--verify-tag` makes gh abort if it is missing.
- Deleting a release does **not** delete its tag unless `--cleanup-tag`;
  a leftover tag makes a later re-create reuse the old commit.
- `--latest` is not automatic for the highest semver: GitHub marks the
  most recently *published* non-prerelease as latest unless `--latest` is
  set explicitly.
- Generated-notes categories come from `.github/release.yml`, which keys
  on PR **labels** — unlabeled PRs fall into the catch-all category.
  Authoring that file belongs to `github-release-conventions`.
- A draft release's URL becomes invalid after publish (the final URL uses
  the tag) — report the post-publish URL, not the draft's.
- Prereleases (`--prerelease`) never become "latest" and are hidden from
  the latest-release API — users on `releases/latest` will not see them.
