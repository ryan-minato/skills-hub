# Epics: lifecycle and the work-items successor (Premium/Ultimate)

## Epic lifecycle (deprecated-but-stable REST)

The Epics REST API is deprecated since GitLab 17.0 (removal planned for
the unreleased API v5) but remains the stable, complete path on every
currently supported version. Epic descriptions go through files
(`-F description=@FILE`).

| Task | Command |
|---|---|
| List | `glab api "groups/GROUP/epics?state=opened"` |
| View | `glab api groups/GROUP/epics/IID` |
| Create | `glab api --method POST groups/GROUP/epics -f title="TITLE" -F description=@EPIC.md` |
| Edit | `glab api --method PUT groups/GROUP/epics/IID [-f title="T"] [-F description=@EPIC.md]` |
| Close / reopen | `glab api --method PUT groups/GROUP/epics/IID -f state_event=close` (or `reopen`) |
| Add / remove labels | `-f add_labels=a,b` / `-f remove_labels=c` on the PUT |
| Set parent epic | `glab api --method PUT groups/GROUP/epics/IID -F parent_id=EPIC_ID` |
| Delete | `glab api --method DELETE groups/GROUP/epics/IID` |

`parent_id` takes the parent's global epic `id`, not its `iid` (the view
row shows both). The pre-publish gate in SKILL.md applies to create and
edit.

## Epics as work items

GitLab is migrating epics onto the work-items model (epics became work
items in 17.2; the legacy epic surfaces are being retired gradually).
Use this path when the legacy epics REST endpoints return 404 on a
licensed instance, or when the user asks for work items, tasks,
objectives, or key results.

`glab work-items` is marked **experimental** — subcommands and flags may
change or vanish between glab releases; check `glab work-items --help`
first and prefer long flags (`--type`, `--title`: both have `-t`-style
shorthands that have collided in the past).

## Operations

```bash
glab work-items list --group GROUP -F json
glab work-items create --type epic --group GROUP --title "TITLE" --description "$(cat EPIC.md)"
glab work-items update IID --group GROUP --title "NEW TITLE"
glab work-items delete IID --group GROUP
```

Work-item types include `epic`, `issue`, `task`, `objective`,
`key_result`, `incident`, `requirement`, `test_case` (`--type` on
create). Epics remain group-scoped (`--group`); tasks and issues are
project-scoped (`-R G/P`).

## Closing a work item

Neither glab nor REST closes a work item — it is a GraphQL mutation:

```bash
glab api graphql -f query=@close.graphql
```

```graphql
mutation {
  workItemUpdate(input: {
    id: "gid://gitlab/WorkItem/GLOBAL_ID",
    stateEvent: CLOSE
  }) {
    workItem { id state }
    errors
  }
}
```

`REOPEN` reverses it. The global id comes from
`glab work-items list -F json` output.

## Choosing between the two epic paths

Default to the legacy epics REST rows in SKILL.md — complete, stable
parameter shapes, works on every currently supported GitLab. Flip to
work-items only on the 404 signal above or an explicit user request;
when you do, tell the user the surface is experimental.
