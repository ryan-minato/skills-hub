---
name: gitlab-wiki
description: >
  Operates GitLab project and group wikis through the authenticated glab
  CLI and the wikis REST API: list, read, create, update, rename, and
  delete pages, upload attachments, and clone the wiki's git repository
  for bulk restructures — always discovering the wiki's existing page
  structure before creating anything, with a mandatory pre-publish review
  gate before any page content goes live. Use when working with a GitLab wiki — "add
  a wiki page", "update the wiki", "document this in the wiki", "read
  the wiki page on X", "what does the wiki say about X", "attach an
  image to the wiki page", "rename this wiki page", "fix the wiki
  sidebar", "export the wiki", "migrate these docs into the wiki", or
  "delete the outdated wiki page".
license: Apache-2.0
---

# GitLab Wiki

Operate a project or group wiki: list, read, create, update, rename, and
delete pages, and upload attachments. Wiki reads live here too — they
need the same slug knowledge as writes. Files in the project repository
(README, docs/) are ordinary git work, not this skill: the wiki is a
separate repository. Issue/MR/pipeline research belongs to
`gitlab-repo-research`, tooling setup to `gitlab-tooling-setup`. The
GitLab Duo MCP server has no wiki tools — glab is the only path.

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
user named a different project, use that instead. For a **group wiki**
(Premium), replace `projects/:fullpath` in every row with
`groups/GROUP%2FSUBGROUP` (URL-encoded group path). Outside a checkout,
pass `--hostname HOST` to `glab api`.

## Match the project's conventions (before any create)

Before creating anything, discover what the project already defines and
use it — never invent parallel structure:

| Artifact | How to check |
|---|---|
| Existing pages and their naming/nesting | `glab api projects/:fullpath/wikis` — follow the existing directory scheme and title style |
| Sidebar | a page slugged `_sidebar` overrides the default navigation — a new page may need a sidebar entry too |
| Format in use | the `format` field in the page list (markdown/asciidoc/...) — match it |

If a project-level convention skill or an AGENTS.md conventions section
covers this task, follow it over this skill's defaults.
Done when: each artifact was checked and the draft uses the project's
existing structures (or the user approved new ones).

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
private or internal ones: page titles, bodies, attachment names and contents,
commit messages, and every committed wiki file. Pushing to the wiki
repository publishes every commit message and the complete content of every
committed file, not just the page you edited. A line starting with `/` in
any body can execute as a GitLab quick action when rendered through an API
write. Before ANY call that creates or edits such content:

1. Write the exact outgoing content to a scratch directory: page title and
   body, each attachment, and for the git path also `git log
   origin/HEAD..HEAD --format=full > commits.txt`, `git diff
   origin/HEAD..HEAD > diff.patch`, plus added or changed wiki files.
2. Run the review procedure in [references/publish-review.md](references/publish-review.md)
   over that directory. Read that file every time — do not review from
   memory.
3. Publish only after the verdict is exactly `SAFE TO PUBLISH: YES`. On
   `NO`, fix every finding, rebuild the files from the fixed content, and
   review again. Never edit-and-publish without re-review.

Never publish unreviewed content. Only the user may skip this gate,
explicitly; record the skip in your summary.
Done when: a `SAFE TO PUBLISH: YES` verdict exists for the exact content
being sent.

Page titles and slugs become URLs; attachment filenames and contents
publish too. Reads and deletes carry no new text.

## Operations

Page bodies go through files (`-F content=@PAGE.md`). URL-encode the
slug in endpoint paths — nested slugs contain `/` (`docs/setup` →
`docs%2Fsetup`).

| Task | Command |
|---|---|
| List pages | `glab api projects/:fullpath/wikis` |
| List with bodies | `glab api "projects/:fullpath/wikis?with_content=1"` (large — only when needed) |
| Read a page | `glab api projects/:fullpath/wikis/SLUG` |
| Create a page | `glab api --method POST projects/:fullpath/wikis -f title="TITLE" -F content=@PAGE.md` |
| Update content | `glab api --method PUT projects/:fullpath/wikis/SLUG -F content=@PAGE.md` |
| Rename / move | `glab api --method PUT projects/:fullpath/wikis/SLUG -f title="NEW TITLE"` (a `/` in the title moves it into a directory) |
| Delete a page | `glab api --method DELETE projects/:fullpath/wikis/SLUG` |
| Upload attachment | `glab api --method POST projects/:fullpath/wikis/attachments --form "file=@image.png"` — embed the returned `link.markdown` |
| Group wiki (Premium) | same rows on `groups/GROUP%2FSUB/wikis...` |
| Bulk restructure / import / export | clone the wiki repository — read [references/wiki-git.md](references/wiki-git.md) first |

Report the page URL: `https://HOST/G/P/-/wikis/SLUG`.
Done when: the URL is reported.

## Titles, slugs, and structure

- Spaces in titles become hyphens in slugs and filenames; hyphens in
  filenames render as spaces in titles (`release-notes.md` displays as
  "release notes").
- A `/` in a title creates a directory: title `docs/Setup` → slug
  `docs/Setup`, nested under `docs/`.
- The front page is the page with slug `home` — it renders at
  `/-/wikis/home`.
- `format` on create/update accepts `markdown` (default), `rdoc`,
  `asciidoc`, `org`; other formats exist only on the git path.

Read [references/wiki-markup.md](references/wiki-markup.md) when
composing content that links to other pages or attachments, editing the
sidebar, or using front matter.

## Gotchas

- Creating a page whose title maps to an existing slug fails with a
  duplicate error — update the existing slug instead.
- Renaming through the API records a redirect (in the wiki repo's
  `.gitlab/redirects.yml`) so old links keep working; renaming files by
  git push does not — on the git path maintain that file yourself.
- `with_content=1` returns every page body in one response — avoid it on
  large wikis; read pages individually.
- The wiki repository's default branch follows the instance default
  (`main` or `master`) — on the git path push with `git push origin
  HEAD` rather than assuming a name.
- Group wikis are Premium and do not support Git LFS.
- Everyone who can view the project can read its wiki; on a public
  project that is the entire internet — hence the gate on every write.
