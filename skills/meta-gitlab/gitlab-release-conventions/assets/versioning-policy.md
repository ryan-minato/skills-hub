# Versioning policy

This project versions releases with
[Semantic Versioning 2.0.0](https://semver.org/): `MAJOR.MINOR.PATCH`.

## Choosing the bump

{{BUMP_RULE}}

<!-- Default when gitlab-commit-conventions is in place — keep and
     delete this comment:

The bump is derived from the commits since the last release:

| Highest change present | Bump |
|---|---|
| A breaking change (`!` type marker or a `BREAKING CHANGE:` footer) | major |
| A `feat:` commit | minor |
| Anything else | patch |

Prereleases append `-rc.N` and count up until the final release.
-->

## Tag format

Release tags are `{{TAG_FORMAT}}` (regex: `{{TAG_REGEX}}`).
Tags are {{TAG_KIND}} <!-- "lightweight" or "annotated: created via
--tag-message on glab release create" or "signed: created locally with
git tag -s and pushed before the release" -->.
The tagged commit must be reachable from the default branch; CI (the
`tag-check` job in `.gitlab-ci.yml`) fails any release tag that breaks
either rule.

## Release notes

{{NOTES_RULE}}

<!-- Pick one and delete this comment:
- Generated: notes come from `glab changelog generate --version X.Y.Z`,
  categorized by Changelog trailer via `.gitlab/changelog_config.yml`;
  curate the generated text before the release is created.
- Manual: notes follow `docs/release-notes-template.md`.
-->

## Milestones

{{MILESTONE_RULE}} <!-- e.g. "Each release has a milestone titled
exactly like the version; release creation associates it and closes it
automatically." or "...and passes --no-close-milestone because the
milestone tracks post-release work too." -->

## Cadence and prereleases

{{CADENCE_RULE}} <!-- e.g. "Releases ship when meaningful changes
accumulate; release candidates (-rc.N) precede every minor and major
release." -->
