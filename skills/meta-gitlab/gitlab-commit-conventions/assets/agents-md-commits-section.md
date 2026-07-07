## Commit messages

This section is the fallback deliverable for projects whose harness does
not load agent skills; it carries the same rules as the generated skill.

Commits follow Conventional Commits, enforced by
`scripts/check_commits.py` (documented in {{CONVENTION_DOC_PATH}}):

- Format: `type(scope)!: subject` — types: {{TYPES_LIST}};
  scope: {{SCOPE_RULE}}.
- Subject: imperative mood, whole title ≤ {{SUBJECT_MAX}} characters, no
  trailing period, English. Body (when the why is not obvious): blank
  line after the title, wrapped at {{BODY_LINE_MAX}} characters, explains
  why not how. Breaking changes: `!` plus a `BREAKING CHANGE:` footer.
- Changelog trailer: {{TRAILER_RULE}}
- **Always validate before committing**: write the message to a file,
  run `python3 scripts/check_commits.py --file COMMIT_MSG.txt`, fix
  every finding until it prints `OK`, then
  `git commit -F COMMIT_MSG.txt`. The same validator runs in CI over
  the MR range.
- Merge, revert, and `fixup!`/`squash!` commits are exempt.
