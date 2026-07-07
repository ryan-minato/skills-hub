# Commit conventions

Commit messages in this repository follow
[Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/),
validated by `scripts/check_commits.py` locally and in CI.

## Format

```
type(scope)!: subject

body (why, not how)

Footer-Key: value
```

Title only is the default; add a body when the why is not obvious from
the diff. `!` marks a breaking change (also add a `BREAKING CHANGE:`
footer describing it).

## Types

| Type | Use for |
|---|---|
| feat | A user-visible feature or capability |
| fix | A bug fix |
| docs | Documentation only |
| refactor | Code change that neither fixes a bug nor adds a feature |
| perf | Performance improvement |
| test | Adding or correcting tests |
| build | Build system or dependency changes |
| ci | CI configuration changes |
| style | Formatting only; no code meaning change |
| chore | Maintenance that fits nothing above |
| revert | Reverts a previous commit |

{{TYPES_NOTE}}

## Scope

{{SCOPE_RULE}}

## Subject rules

- Imperative mood ("add", not "added" or "adds").
- At most {{SUBJECT_MAX}} characters for the whole title line.
- No trailing period.
- English.

## Body and footers

- Blank line between title and body; body lines wrap at
  {{BODY_LINE_MAX}} characters.
- The body explains why, not how.
- Footers each on their own line after a blank line (issue references,
  `BREAKING CHANGE:`).

## Changelog trailer

{{TRAILER_RULE}}

<!-- Default — keep and delete this comment:

Every user-facing commit carries a `Changelog:` Git trailer naming its
category (`added`, `fixed`, `changed`, `deprecated`, `removed`,
`security`, `performance`, `other`):

```
fix(api): reject expired tokens

Changelog: fixed
```

The trailer feeds `glab changelog generate` and the release notes —
commits without it are silently excluded from generated changelogs.
Internal-only commits (docs, chore, test) usually omit it.
-->

## Exemptions

Merge commits, `Revert "..."` commits created by tooling, and
`fixup!`/`squash!` commits are exempt from these rules.
