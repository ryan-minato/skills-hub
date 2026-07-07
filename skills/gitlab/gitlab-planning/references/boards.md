# Issue boards: operations, scoping, and group boards

No glab command group exists for boards — every row is `glab api`.
Multiple boards per **project** are Free; scoping, non-label lists, and
group boards are Premium.

## Board and list operations (Free)

| Task | Command |
|---|---|
| List boards | `glab api projects/:fullpath/boards` |
| View a board's lists | `glab api projects/:fullpath/boards/BID/lists` |
| Create board | `glab api --method POST projects/:fullpath/boards -f name="NAME"` |
| Rename board | `glab api --method PUT projects/:fullpath/boards/BID -f name="NAME"` |
| Delete board | `glab api --method DELETE projects/:fullpath/boards/BID` |
| Add a label list | `glab api --method POST projects/:fullpath/boards/BID/lists -F label_id=LABEL_ID` |
| Reorder a list | `glab api --method PUT projects/:fullpath/boards/BID/lists/LID -F position=N` |
| Delete a list | `glab api --method DELETE projects/:fullpath/boards/BID/lists/LID` |

A label list takes the numeric `label_id` from `glab label list -F json`.
The pre-publish gate in SKILL.md applies to board/list create and rename.

## Board scoping (Premium)

A scoped board pre-filters every list. The scope parameters are mutually
exclusive — send one per request:

```bash
glab api --method PUT projects/:fullpath/boards/BID -f milestone_id=MID
glab api --method PUT projects/:fullpath/boards/BID -f assignee_id=UID
glab api --method PUT projects/:fullpath/boards/BID -f weight=3
glab api --method PUT projects/:fullpath/boards/BID -f labels=frontend
```

Hide the built-in columns:

```bash
glab api --method PUT projects/:fullpath/boards/BID -F hide_backlog_list=true -F hide_closed_list=true
```

## Non-label lists (Premium)

Free boards only have label lists. Premium adds lists keyed to an
assignee, milestone, or iteration — pass exactly one key:

```bash
glab api --method POST projects/:fullpath/boards/BID/lists -F assignee_id=UID
glab api --method POST projects/:fullpath/boards/BID/lists -F milestone_id=MID
glab api --method POST projects/:fullpath/boards/BID/lists -F iteration_id=IID
```

## Group boards

Every project row works at group level by replacing
`projects/:fullpath/boards` with `groups/GROUP/boards` (URL-encode `/`
in nested group paths). One group board is Free; **creating or deleting
additional group boards is Premium** — a 404 on POST/DELETE there is the
tier gate.

## Epic boards (Premium; read-only over REST)

```bash
glab api groups/GROUP/epic_boards
glab api groups/GROUP/epic_boards/BID
glab api groups/GROUP/epic_boards/BID/lists
```

The epic-boards REST API is GET-only; creating or editing epic boards
happens in the UI (or GraphQL) — say so instead of trying POST/PUT.
