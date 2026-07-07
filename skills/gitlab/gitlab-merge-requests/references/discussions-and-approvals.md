# Discussion threads and approvals

Every write here is publishing — run the pre-publish gate in SKILL.md
first. Reply and comment bodies go through files
(`-m "$(cat REPLY.md)"`), never inline strings.

## Read threads

```bash
glab mr view N -R G/P --comments        # all comments and threads
glab mr view N -R G/P --unresolved      # only unresolved threads
glab mr view N -R G/P --resolved        # only resolved threads
```

Each thread's discussion id appears in the output; MCP:
`get_merge_request_notes` (19.2).

## Reply in a thread

```bash
glab mr note create N -R G/P --reply DISCUSSION_ID -m "$(cat REPLY.md)"
```

`--reply` accepts the full discussion id or a prefix of 8+ characters.
The `glab mr note` subcommands are experimental; if `create` is missing
in the installed glab, use the API directly:

```bash
glab api --method POST "projects/:fullpath/merge_requests/N/discussions/DISCUSSION_ID/notes" -F "body=@REPLY.md"
```

MCP: `create_merge_request_note` (19.2) with the discussion parameter.

## Comment on a diff line

```bash
glab mr note create N -R G/P --file path/to/file --line 42 -m "$(cat COMMENT.md)"
```

`--line` takes a single line or a `10:15` range in the new version;
`--old-line` (with `--file`) targets a removed line. Targets the latest
diff version. New discussions are resolvable by default
(`--resolvable=false` for a plain note).

## Resolve / reopen a thread

```bash
glab mr note resolve DISCUSSION_ID N -R G/P
glab mr note reopen DISCUSSION_ID N -R G/P
```

API fallback:

```bash
glab api --method PUT "projects/:fullpath/merge_requests/N/discussions/DISCUSSION_ID?resolved=true"
```

Resolving is metadata, not text — the gate does not apply; the reply that
usually accompanies it does.

## Approvals

```bash
glab mr approvers N -R G/P    # who approved / who is eligible
glab mr approve N -R G/P      # approve
glab mr revoke N -R G/P       # withdraw your approval
```

*Required* approval rules and CODEOWNERS enforcement are
Premium/Ultimate; on Free, approvals are informational. `glab mr merge`
fails while required approvals are missing — approve first or name the
missing approver to the user.

## Internal notes

Notes created with the API parameter `internal=true` are visible only to
members with at least the Reporter role. glab has no flag for them; use
`glab api --method POST "projects/:fullpath/merge_requests/N/notes" -F "body=@NOTE.md" -F internal=true`
when the user explicitly asks for an internal note. The gate still
applies — internal is not private.
