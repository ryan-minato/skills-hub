# The wiki as a git repository — bulk work

Every GitLab wiki is a git repository. Use this path when the task
touches many pages at once (restructures, imports, exports), when a
rename must keep redirects consistent, or when the content format is one
the API does not accept (`.rst`, `.textile`). Single-page operations stay
on the REST rows in SKILL.md.

## Clone

The project wiki's clone URL is the project clone URL with `.git`
replaced by `.wiki.git`:

```bash
git clone https://HOST/GROUP/PROJECT.wiki.git
```

Authenticate over HTTPS with the same token glab uses (username is the
account name, password is the PAT; the token needs `write_repository`
scope to push). For a **group wiki** the URL pattern is not documented —
copy it from the wiki's UI (Wiki actions → Clone repository) instead of
constructing it.

## File ↔ page mapping

- Filename (minus extension) is the slug; hyphens display as spaces in
  titles.
- Directories nest pages: `docs/setup.md` is the page `docs/setup`.
- The front page is `home.<ext>` at the repository root.
- Extension selects the markup: `.md`, `.rdoc`, `.asciidoc`/`.adoc`,
  `.org`, plus git-path-only formats like `.rst` and `.textile`.
- Keep filenames under 245 bytes; git can create longer ones, but the
  wiki UI cannot edit those pages.
- A `templates/` directory at the root holds wiki templates, and
  `_sidebar.<ext>` customizes navigation (see wiki-markup.md).

## Renames and redirects

The UI/API write a redirect entry into `.gitlab/redirects.yml` (inside
the wiki repository) when a page moves, so old URLs keep resolving. A
plain `git mv` does not. When renaming via git, append the mapping
yourself:

```yaml
# .gitlab/redirects.yml — old slug: new slug
old-page: new-section/new-page
```

## Push flow (gate first)

1. Make the edits on a local clone.
2. Assemble the scratch directory for the pre-publish gate in SKILL.md:
   `git log origin/HEAD..HEAD --format=full > commits.txt`,
   `git diff origin/HEAD..HEAD > diff.patch`, plus any added files.
3. Only after `SAFE TO PUBLISH: YES`:

   ```bash
   git push origin HEAD
   ```

   `HEAD` sidesteps the main/master naming difference across instances.
   The push publishes every commit message and the full content of every
   committed file at once.
