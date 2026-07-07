# Milestone recipes

Long-tail milestone work beyond the SKILL.md table. Everything here is gh
(`gh api`) — there is no MCP capability for milestones.

## Resolve a milestone number by title

The REST rows in SKILL.md take the milestone `number`. When you only have
the title:

```bash
gh api "repos/O/R/milestones?state=all" \
  -q '.[] | select(.title == "TITLE") | .number'
```

An empty result means no such milestone — list all titles and re-check
before creating anything.

## List with sorting and paging

```bash
gh api "repos/O/R/milestones?state=open&sort=due_on&direction=asc&per_page=100" \
  -q '.[] | {number, title, due_on, open_issues, closed_issues}'
```

`sort` is `due_on` or `completeness`; `state` is `open`, `closed`, or
`all`. The `open_issues`/`closed_issues` counters show progress without
listing the issues.

## List a milestone's issues

Milestone filtering lives on the issues API, by **title**:

```bash
gh issue list -R O/R --milestone "TITLE" --state all \
  --json number,title,state
```

## Bulk-move issues between milestones

There is no bulk endpoint; loop over the source milestone's issues. This
changes issue metadata, so the pre-publish gate's metadata rule applies —
confirm the plan with the user, then:

```bash
gh issue list -R O/R --milestone "OLD" --state all --json number \
  -q '.[].number' \
| while read -r n; do gh issue edit "$n" -R O/R --milestone "NEW"; done
```

Re-run the list afterwards to confirm the source is empty.

## Due-date semantics

`due_on` is a full ISO timestamp; GitHub renders only the date part and
normalizes the time to 07:00/08:00 UTC on some paths — write
`YYYY-MM-DDT00:00:00Z` and treat the date as the contract, not the hour.
Clearing a due date is `-F due_on=null` (`-F`, not `-f`, so null stays a
JSON null instead of a string).
