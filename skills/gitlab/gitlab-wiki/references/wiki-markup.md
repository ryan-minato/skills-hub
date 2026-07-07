# Wiki markup specifics

For markdown-format pages (the default). Other formats have their own
link syntaxes; these rules are the GitLab-wiki-specific parts.

## Links between pages

Standard markdown links whose targets are wiki slugs. Two target forms:

| Target form | Resolves |
|---|---|
| `/docs/setup` (leading slash) | absolute — from the wiki root |
| `sibling-slug` or `child/page` | relative — from the current page's directory |

Link targets are slugs, not titles — spaces become hyphens. A link to a
nonexistent slug renders as a "new page" link rather than erroring,
which silently hides typos: verify slugs against the page list.

## Attachment links

The upload response from `POST .../wikis/attachments` contains the exact
markdown to embed:

```json
{ "link": { "url": "uploads/....png", "markdown": "![file](uploads/....png)" } }
```

Use `link.markdown` verbatim; hand-built `uploads/...` paths break when
the page moves directories.

## Sidebar

A page named `_sidebar` (file `_sidebar.md` at the wiki root) replaces
the auto-generated navigation. It is an ordinary page — edit it through
the same create/update rows, slug `_sidebar`. Keep it a short list of
links; the auto sidebar returns if the page is deleted.

## Front matter

Pages may start with a YAML front matter block; `title:` overrides the
display title without changing the slug or filename:

```markdown
---
title: Display Title With Punctuation!
---
```

Useful when the desired title contains characters that slugs cannot
carry.
