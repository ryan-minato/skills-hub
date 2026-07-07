# Issue recipes — long-tail operations

Operations that are not rows in the SKILL.md table. The same rules apply:
use the column chosen in "Choose your path", except where an entry is
marked glab only or quick-action only — then use that mechanism regardless
of the session's default. The pre-publish gate in SKILL.md covers every
recipe here that changes public text or metadata; a comment whose only
content is a quick action is still a publish (the action executes with
your permissions and is recorded publicly).

## Confidential issues

Visible to project members with at least the Reporter role. glab only.

```bash
glab issue create -R G/P -t "TITLE" -d "$(cat BODY.md)" -c -y   # create confidential
glab issue update N -R G/P -c                                   # make confidential
glab issue update N -R G/P -p                                   # make public again
```

## Due date, weight

Weight requires Premium. (Milestone assignment is a main-table row in
SKILL.md; create milestones with `gitlab-planning`.)

```bash
glab issue update N -R G/P --due-date 2026-08-31
glab issue update N -R G/P -w 3
```

## Iteration and epic assignment (Premium)

`glab issue update` has no iteration or epic flag. At create time,
`--epic <id>` attaches the issue to an epic. After creation, use quick
actions in a comment (gate first — the comment publishes):

```bash
glab issue note N -R G/P -m "/iteration [cadence:\"CADENCE\"] --current"
glab issue note N -R G/P -m "/epic GROUP&EPIC_IID"
```

`/epic` takes an epic reference (`&IID` inside the same group). Unknown
targets are silently ignored — verify the epic/iteration exists first.

## Lock / unlock discussion

Restrict further commenting on a resolved or heated conversation. glab
only.

```bash
glab issue update N -R G/P --lock-discussion
glab issue update N -R G/P --unlock-discussion
```

## Linked issues

At create time:

```bash
glab issue create -R G/P -t "TITLE" -d "$(cat BODY.md)" --linked-issues 12,34 --link-type relates_to -y
```

After creation, link with a quick action comment: `/relate #12`;
`/blocks #12` and `/blocked_by #12` need Premium.

## Move to another project

Quick-action only — glab has no move command. Post a comment whose body
is exactly:

```
/move full/path/to/target-project
```

The mover needs sufficient permissions in both projects; the issue is
closed here and recreated there.

## Search and filters

```bash
glab issue list -R G/P --search "TEXT" --in title,description
glab issue list -R G/P -l bug -a some-user --author other-user
glab issue list -R G/P -t incident            # issue types: issue, incident, test_case
glab issue list -R G/P -O json                # machine-readable output
```

The MCP search capability (18.4) covers cross-project search; per-project
filtering is glab's `issue list` flags as above.
