---
name: gitlab-releases
description: >
  Operates GitLab releases and their tags through the glab CLI on
  gitlab.com or any self-managed host: create a release with reviewed
  notes in one shot (GitLab has no draft releases), generate notes from
  Changelog commit trailers with glab changelog, create annotated tags,
  associate milestones, upload and link assets, and list, view, edit, or
  delete releases. Use when cutting or managing a release — "create a
  release", "tag v1.2.0 and release it", "generate the changelog",
  "attach the milestone to the release", "upload this binary to the
  release", or "delete the release". Reading releases of a project you
  are only researching belongs to gitlab-repo-research; versioning and
  tag policy to gitlab-release-conventions.
license: Apache-2.0
compatibility: >
  scripts/next_version.py requires Python 3.9+ (stdlib only); reading
  local tags requires git in the repository checkout.
---

# GitLab Releases

Cut and manage releases: pick the next version, assemble and review the
notes, create the release with its tag, milestones, and assets in one
call, then edit or clean up. This skill owns releases and their tags.
Reading releases of a project under investigation belongs to
`gitlab-repo-research`; the versioning and tag-naming *policy* (and
`.gitlab/changelog_config.yml` authoring) to `gitlab-release-conventions`;
milestone lifecycle to `gitlab-planning`. The GitLab Duo MCP server has
no release tools — glab (with `glab api` for gaps) is the only path, so
the tables below have one column.

## Choose your path (do this first, once per session)

1. Run `glab auth status`. If it exits 0 and lists the target host, use
   glab as shown in every table below. For a self-managed host, check that
   host specifically: `glab auth status --hostname HOST`.
2. Otherwise stop and tell the user GitLab tooling is not set up. This skill
   pairs with `gitlab-tooling-setup`. If it is not installed, install it from
   https://github.com/ryan-minato/skills.git:

       npx skills add ryan-minato/skills --skill gitlab-tooling-setup

## Identify the host and project

Run `git remote get-url origin`. The host is the part right after
`https://` or the `@` (GitLab is often self-managed — never assume
`gitlab.com`). The project path is everything after the host, with any
trailing `.git` stripped; GitLab paths can nest (`group/subgroup/project`
is one project — keep the full path). If there is no origin remote, or the
user named a different project, use that instead. Substitute the full path
wherever the tables show `G/P` (`-R G/P`; URL-encode `/` as `%2F` inside
`glab api` endpoint paths, or use `:fullpath` inside a checkout). Outside
a checkout, pass `--hostname HOST` to `glab api`/`glab auth` and set
`GITLAB_HOST=HOST` for other command groups.

## Match the project's conventions (before any create)

Before creating anything, discover what the project already defines and
use it — never invent parallel structure:

| Artifact | How to check |
|---|---|
| Tag scheme | `git tag --sort=-v:refname | head -20` — prefix (`v` or none), semver shape, prerelease suffixes |
| Prior notes style | `glab release view -R G/P` (latest) — heading structure, categories, tone |
| Changelog config | `.gitlab/changelog_config.yml` present and commits carry `Changelog:` trailers? → generated notes are the project's default |
| Release policy | a project-level release skill, an AGENTS.md release section, or a versioning-policy doc — binding when present |
| Matching milestone | `glab milestone list -R G/P` — a milestone titled like the version is associated (and auto-closed) at create time |

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

Everything you send becomes visible the moment the call succeeds — to the
whole internet on public projects, and to every member just as instantly on
private or internal ones: title, body, every comment, labels, commit
messages, the full diff, attachment contents, and the branch name. GitLab
has no draft releases — creating a release publishes the tag, name, notes,
and asset links the moment the call succeeds, so this gate runs on the
complete assembled release before create. Before ANY call that creates or
edits such content:

1. Prefer a clean-context subagent review when one is available. Give it only
   the exact final release text or files under review, with no extra intent
   or reassurance.
2. Otherwise review the exact final release yourself. Short release names,
   tags, and comments may be inspected directly. Long notes, generated
   notes, attachments, screenshots, assets, or content too large to inspect
   reliably inline must be written to a scratch directory and reviewed from
   disk.
3. Check every artifact for secrets or credentials, personal data, internal
   identifiers or URLs, unintended quick actions, accidental unrelated
   content, and wording a maintainer would regret publishing. Any finding
   means `SAFE TO PUBLISH: NO`.
4. Publish only after the verdict is exactly `SAFE TO PUBLISH: YES`. On
   `NO`, fix every finding and review the exact final content again. Never
   edit-and-publish without re-review.

Never publish unreviewed content. Only the user may skip this gate,
explicitly; record the skip in your summary.
Done when: a `SAFE TO PUBLISH: YES` verdict exists for the exact content
being sent.

In this skill the gate reviews the assembled release before create — tag
name, release name, `NOTES.md`, and the asset file/link list — and any
later notes edit. Reads and deletes carry no new text.

## Create a release

1. **Pick the version.** Follow the project's policy; mechanical bumps:
   `python3 scripts/next_version.py --bump patch` (or `minor`/`major`;
   `--pre rc` for a prerelease; `--latest vX.Y.Z` when local tags are not
   the source of truth). The output is `TAG` below.
2. **Write the notes** to `NOTES.md` per the decision table below.
3. **Run the gate** over tag name, release name, `NOTES.md`, and the
   asset list. GitLab publishes on create — there is no draft to fix up.
4. **Create** (the tag is created at `--ref` if it does not exist;
   `--tag-message` makes it an annotated tag):

       glab release create TAG -R G/P --name "NAME" \
         --notes-file NOTES.md [--ref BRANCH_OR_SHA] \
         [--tag-message "MSG"] [--milestone "M"] [--no-close-milestone] \
         [ASSET_FILES...]

5. Report the release URL from the output.

Done when: the URL is reported and `glab release view TAG -R G/P` shows
the expected notes and assets.

## Notes

| Situation | Path |
|---|---|
| `.gitlab/changelog_config.yml` exists and commits carry `Changelog:` trailers | `glab changelog generate --version X.Y.Z > NOTES.md`, then curate before the gate |
| Hand-written notes | Compose NOTES.md from `git log PREV_TAG..HEAD --oneline` grouped by kind, matching the prior notes style found above |

Read [references/changelog-generation.md](references/changelog-generation.md)
when generating notes (trailer semantics, category config, ranges, the
REST changelog endpoint that can also commit a CHANGELOG file).

## Assets

| Task | Command |
|---|---|
| Upload files to an existing release | `glab release upload TAG -R G/P FILE1 'FILE2#Display label'` |
| Link an external URL as an asset | `glab release upload TAG -R G/P -a '[{"name":"NAME","url":"https://...","link_type":"package"}]'` |
| Delete an asset link | `glab release delete-asset TAG ASSET_NAME -R G/P -y` |

`link_type` is one of `other`, `runbook`, `image`, `package`. The same
`-a`/`--assets-links` JSON works on `release create`.

## Read, list, edit, delete

| Task | Command |
|---|---|
| List releases | `glab release list -R G/P` |
| View one / latest | `glab release view TAG -R G/P` (omit `TAG` for the latest) |
| Edit name/notes | `glab api --method PUT projects/:fullpath/releases/TAG -f name="N" -F "description=@NOTES.md"` — glab has no release-edit subcommand; gate on text changes |
| Delete a release | `glab release delete TAG -R G/P -y` — the git tag survives; confirm with the user first |
| Delete the tag too | after the delete: `glab api --method DELETE projects/:fullpath/repository/tags/TAG` |

Read [references/release-recipes.md](references/release-recipes.md) for
the long tail (standalone tag creation, generic package registry uploads,
publishing to the CI/CD catalog, release evidence, released-at
scheduling).

## Gotchas

- `glab release create` on an existing release **updates** it instead of
  failing, unless `--no-update` — convenient for fixing notes, dangerous
  when the tag name was a typo. Check `glab release list` first.
- Associating a milestone **closes it by default** when the release is
  created — pass `--no-close-milestone` unless closing is intended.
- `glab changelog generate` includes only commits carrying the
  `Changelog:` trailer (or the trailer set in the config) — commits
  without it are silently excluded; an empty changelog usually means the
  trailer convention is not in use, not that nothing changed.
- `glab release delete` keeps the git tag; recreating the release later
  reuses that tag's commit. Delete the tag explicitly when the whole
  version was wrong.
- Without `--tag-message`, a tag created by `release create` is
  lightweight; projects requiring annotated/signed tags should pass
  `--tag-message` or create the tag with git first and push it.
- A 404 on release endpoints usually means insufficient role (Developer+
  required) or a private project without access — not a tier gate;
  releases are a Free feature.
- `--released-at` in the future creates an "Upcoming" release — it is
  not shown as the latest until the timestamp passes.
