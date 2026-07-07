# .gitlab/changelog_config.yml schema

Load condition: editing the changelog configuration beyond the shipped
categories.

The file configures **changelog generation** — `glab changelog
generate` and the repository changelog REST endpoint. It affects nothing
else: not release descriptions, not tags, not milestones.

## Structure

```yaml
date_format: "%Y-%m-%d"        # heading date, strftime format
categories:                     # trailer value → section heading
  added: Features
  fixed: Bug fixes
template: |                     # optional: full custom template
  ...
tag_regex: '^v(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)$'
```

## Matching rules

- `categories:` keys are `Changelog:` trailer **values**, matched
  case-sensitively — GitLab has no default category, so `Changelog: Added`
  against an `added` key matches nothing and is dropped from the changelog
  entirely (the SKILL's gotcha and the config's own header say the same).
- Commits without the trailer are excluded entirely; an empty generated
  changelog almost always means the trailer habit is missing, not that
  nothing changed.
- Section order follows the key order in the file.
- `tag_regex` is how the generator finds "the previous version tag"
  when `--from` is not given — keep it consistent with the versioning
  policy's tag format.

## Testing a change

Both generators are read-as-data until told otherwise:

```bash
glab changelog generate --version X.Y.Z            # prints, changes nothing
glab api "projects/:fullpath/repository/changelog?version=X.Y.Z"
```

Edit the config, re-run, and diff the output until the sections look
right. (The REST endpoint's `POST` form **commits** a changelog file —
that is a publish; gate the generated text first.)
