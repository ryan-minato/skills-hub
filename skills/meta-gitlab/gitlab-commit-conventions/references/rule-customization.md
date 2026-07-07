# Customizing the rules

Load condition: tailoring the convention beyond the shipped defaults, or
the project squash-merges.

Every enforced rule lives in the `CONFIG` block at the top of the
committed `scripts/check_commits.py`; the convention doc describes the
same rules for humans. Change both in the same commit.

## Scope rules

`CONFIG["allowed_scopes"]` has three shapes:

| Value | Meaning | Convention-doc wording |
|---|---|---|
| `None` | Scope optional, free-form | "Scope is optional; use the touched module's name." |
| `[]` | Scope forbidden | "This project does not use scopes." |
| `["api", "cli", ...]` | Scope required, from this set | List the set and what each covers |

Monorepos usually want the required-set shape with one scope per
component; keep the set short enough to memorize, or derive it from the
top-level directory names and say so in the doc.

## Custom types

Add project-specific types to `CONFIG["types"]` sparingly — every extra
type dilutes the signal. A type earns its place when the history
analyzer shows a recurring change kind the standard eleven cannot
express. Update the convention doc's table in the same commit.

## Requiring the Changelog trailer

The shipped default treats the `Changelog:` trailer as a convention, not
a validator rule (internal-only commits legitimately omit it). To make
it mandatory for specific types (for example every `feat` and `fix`),
add a check to `check_message` in the validator — match the title's
type, then require a `^Changelog: (added|fixed|changed|deprecated|`
`removed|security|performance|other)$` line in the body — and document
it. Keep the exemption patterns in mind: merge and revert commits will
not carry trailers.

## Squash-merge projects

When the project squash-merges (`squash_option` of `always` or
`default_on`), the **MR title** becomes the squash commit's subject on
the default branch, and branch commits disappear. Two adjustments:

1. Validate the MR title in the same CI job — add a second script line
   (the variable is expanded by the runner into a quoted argument; do
   not build the command by hand from it elsewhere):

   ```yaml
     script:
       - python3 scripts/check_commits.py --range "$CI_MERGE_REQUEST_DIFF_BASE_SHA..$CI_COMMIT_SHA"
       - python3 scripts/check_commits.py --message "$CI_MERGE_REQUEST_TITLE"
   ```

2. Relax the branch-commit rules in the convention doc when they are
   squashed away, and say which applies.

## Commit template

Ship a `.gitmessage` template so humans get the format as a scaffold:
put the title format, type list, and the `Changelog:` trailer hint in a
comment block, commit the file at the repo root, and document
`git config commit.template .gitmessage` as a one-time setup step (or
run it via the project's bootstrap script).
