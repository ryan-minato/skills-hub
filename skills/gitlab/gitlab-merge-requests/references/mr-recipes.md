# MR recipes — long-tail operations

The same rules apply: use the column chosen in "Choose your path"; rows
here are glab-only unless noted. Metadata edits (milestone, reviewers,
labels) fall under the pre-publish gate in SKILL.md.

## Rebase onto the target branch

The update-branch equivalent; rewrites the source branch on the server.

```bash
glab mr rebase N -R G/P [--skip-ci]
```

## Check out the MR branch locally

```bash
glab mr checkout N -R G/P
```

## Change target branch, reviewers, milestone

```bash
glab mr update N -R G/P --target-branch main
glab mr update N -R G/P --reviewer +some-user      # + adds, !/- removes, bare replaces
glab mr update N -R G/P -m "MILESTONE TITLE"       # -m "" unassigns
```

## Labels

```bash
glab mr update N -R G/P -l new-label -u old-label
```

## Linked issues and auto-close

`Closes #12` (or `Fixes #12`) in the MR description closes the issue when
the MR merges into the default branch. List the issues an MR mentions:

```bash
glab mr issues N -R G/P
```

## Squash and source-branch removal toggles

Project settings supply the defaults; per-MR overrides:

```bash
glab mr update N -R G/P --squash-before-merge
glab mr update N -R G/P --remove-source-branch
```

At merge time, `glab mr merge` accepts `--squash-message "..."` and a
custom merge commit message via `-m "$(cat MERGE_MSG.md)"`.

## Guarded merge

Merge only if the source head still matches a reviewed SHA:

```bash
glab mr merge N -R G/P --sha REVIEWED_SHA --yes
```

## Revert a merged MR

glab has no `mr revert`. Revert through git on a branch and open a new
MR: `git revert -m 1 MERGE_COMMIT_SHA`, push, then the create row in
SKILL.md.
