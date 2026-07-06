# Issue recipes — long-tail operations

Operations that are not rows in the SKILL.md table. The same rules apply:
use the column chosen in "Choose your path", except where an entry is
marked gh only or MCP only — then use that column regardless of the
session's default. The pre-publish gate in SKILL.md covers every recipe
here that changes public text or metadata (milestones; a transfer moves
public content between repositories).

## Pin / unpin

Keep an important issue at the top of the repository's issue list (GitHub
allows up to three pinned issues per repository). No MCP tool — gh only.

```bash
gh issue pin N -R O/R
gh issue unpin N -R O/R
```

## Lock / unlock

Restrict further commenting on a resolved or heated conversation. No MCP
tool — gh only. The optional reason is one of `off_topic`, `resolved`,
`spam`, `too_heated`.

```bash
gh issue lock N -R O/R --reason resolved
gh issue unlock N -R O/R
```

## Transfer

Move an issue to another repository under the same owner or organization.
No MCP tool — gh only. `-R O/R` names the source repository.

```bash
gh issue transfer N OWNER/TARGET-REPO -R O/R
```

## Sub-issues

Attach, detach, or reorder sub-issues under a parent issue. MCP only: use
`sub_issue_write` with method `add`, `remove`, or `reprioritize`, passing
the parent's `issue_number` and the child's `sub_issue_id`; `reprioritize`
additionally takes `after_id` or `before_id` to set the position. gh has
no first-class sub-issue command, and the GraphQL route via `gh api` is
out of scope here — without MCP, tell the user sub-issue management needs
the GitHub MCP server or the web UI.

## Milestone

Assign an issue to an existing milestone (the milestone must already exist
in the repository).

| MCP tool | gh command |
|---|---|
| `issue_write` method=`update`, `milestone` | `gh issue edit N -R O/R --milestone "NAME"` |

## Search

Find issues by text and qualifiers instead of listing everything.

| MCP tool | gh command |
|---|---|
| `search_issues` with query `repo:O/R is:open label:bug TEXT` | `gh issue list -R O/R --search "TEXT label:bug"` |

Both columns use the same GitHub search qualifier syntax (`is:`, `label:`,
`author:`, `in:title`). With `gh issue list --search` the `repo:` qualifier
is unnecessary because `-R O/R` already scopes the search.
