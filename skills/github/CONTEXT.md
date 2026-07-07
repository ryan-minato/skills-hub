# github — Catalog Context

Rules, notes, and references that apply only to skills in this catalog.
(Repo-wide standards live in `.agents/knowledge/skill-quality.md`.)

This catalog holds **operational** skills: directly installable playbooks
for day-to-day GitHub work (issues, pull requests, planning structures,
releases, read-only research). Tooling setup and conventions authoring live
in the `meta-github` catalog.

## Requirements

- **Design floor: a ~30B-parameter local model.** Every operation gets
  exactly one recommended path: the shared "Choose your path" procedure
  (GitHub MCP if a connected server provides the needed capabilities, else
  authenticated gh, else pair with `github-tooling-setup`), then decision
  tables mapping task → MCP capability → exact gh command. No unlabeled
  alternatives, no "you could also". Add a `Done when:` line where
  completion is ambiguous or a weak model may stop early or run past done;
  omit it for steps that are simple and cannot fail.
- **MCP tools are described by capability, never by name.** MCP tool names
  churn across server versions, and MCP servers self-describe each tool's
  purpose and parameters — the agent matches by purpose at runtime. Skill
  bodies, tables, and references write "the MCP tool that reads an issue",
  never a concrete tool name or a `mcp__...` prefix pattern. Exact names
  are allowed only for gh commands, REST/GraphQL endpoints, and bundled
  scripts. Consequence: MCP table cells stay valid across server versions;
  only gh/REST references need re-verification.
- **Mixed coverage rule.** Where the MCP server has no capability for some
  rows of a skill (planning's milestone rows, release writes), the table
  keeps both columns and marks the MCP cell `—`. A `—` means "use the gh
  column for this row even on the MCP path" — never an error, never a
  reason to stop. Skills with `—` cells use the mixed-coverage variant of
  "Choose your path".
- **Convention discovery is mandatory before any create.** Every skill
  that creates content embeds "Match the project's conventions" with its
  own discovery table (templates, labels, milestones, tag schemes, project
  convention skills / AGENTS.md). Inventing structure parallel to what the
  repository already defines is a defect, not a style choice.
- Bodies stay well under 200 lines. Per-framework matrices, GraphQL
  queries, log recipes, and the publish-review procedure live in
  `references/` behind precise load conditions. Deterministic multi-step
  logic (ID resolution, version bumping, log digestion) lives in `scripts/`
  (python3 ≥3.9 stdlib only, invoked with plain `python3`, non-interactive,
  exit codes 0/1/2, data to stdout, diagnostics to stderr, idempotent).
- Multi-line content is always sent via files (`--body-file`, or MCP body
  parameters filled from files), never inline shell strings.
- **Publishing safety.** Publishing = anything that becomes public: issue/
  PR/discussion titles and bodies, comments, labels, milestone and project
  names, release notes and assets, commit messages, diffs, attachments,
  branch and tag names. Every skill that publishes embeds the canonical
  pre-publish gate in its body and ships its own copy of
  `references/publish-review.md` — the review procedure is never delegated
  to a separate skill that might not be loaded. Tailoring is allowed only
  where the canonical text marks it.
- **Authoring defaults are canonical.** Every skill that authors prose
  embeds the fixed "Authoring defaults" block below, word-for-word
  identical to the gitlab catalog's copy.
- Cross-skill overlap is limited to the canonical blocks below and the
  disambiguation line, duplicated verbatim where needed; deep content
  lives only in the owning skill. Sibling skills (including meta-github
  skills) are named, never path-linked (self-containment).
- Exact gh command, subcommand, and flag names — and REST/GraphQL endpoint
  shapes — must be re-verified before publishing a skill revision, against
  <https://cli.github.com/manual/> and <https://docs.github.com/en/rest>.
  MCP capabilities are deliberately name-free and carry no such duty.

## Canonical blocks

The following texts are canonical. Skills copy them verbatim; when editing
one, update every copy in the same commit (`grep -rl "Choose your path"
skills/github/` finds them).

### Choose your path

```markdown
## Choose your path (do this first, once per session)

1. Look at the tools available in this session. If a connected MCP server
   provides GitHub tools for the work this skill covers (each tool's
   description states its purpose; names vary across server versions), use
   the **MCP** column of every table below, picking the tool whose
   description matches the row's capability.
2. Otherwise run `gh auth status`. If it exits 0, use the **gh** column.
3. Otherwise stop and tell the user GitHub tooling is not set up. This skill
   pairs with `github-tooling-setup`. If it is not installed, install it from
   https://github.com/ryan-minato/skills.git:

       npx skills add ryan-minato/skills --skill github-tooling-setup

4. Use one column for the whole task. Never mix MCP and gh in one operation.
```

#### Mixed-coverage variant (github-planning, github-releases)

Skills whose tables contain `—` MCP cells append this sentence to step 1:

```markdown
   The MCP column applies only to rows that name a capability; rows marked
   `—` have no MCP tool — use the gh column for those rows even on the MCP
   path.
```

#### Read-only variant (github-repo-research only)

`github-repo-research` inserts a REST-fallback step between steps 2 and 3
and renumbers accordingly; its closing step reads "Use one path for the
whole task. Never mix MCP, gh, and REST in one operation." The inserted
step is:

```markdown
3. Otherwise, if the target repository is public, or a token is set in
   `GH_TOKEN`/`GITHUB_TOKEN` even though gh is missing, use the REST
   fallback: read [references/rest-fallback.md](references/rest-fallback.md)
   and run [scripts/rest_read.py](scripts/rest_read.py). Reads only.
```

### Identify the repository

```markdown
## Identify the repository

Run `git remote get-url origin`. The owner/repo pair is the path right
after the host, with any trailing `.git` stripped. If there is no origin
remote, or the user named a different repository, use that instead.
Substitute the pair wherever the tables show `O/R` (gh: `-R O/R`; MCP: the
owner and repo parameters).
```

### Match the project's conventions

Only the table rows are tailorable per skill; the surrounding text is
fixed. Embedded by every skill that creates content.

```markdown
## Match the project's conventions (before any create)

Before creating anything, discover what the repository already defines and
use it — never invent parallel structure:

| Artifact | How to check |
|---|---|
| <skill-specific rows> | <exact command or MCP capability> |

If a project-level convention skill or an AGENTS.md conventions section
covers this task, follow it over this skill's defaults.
Done when: each artifact was checked and the draft uses the repository's
existing structures (or the user approved new ones).
```

### Authoring defaults

Fixed text; embedded by every skill that authors prose. Word-for-word
identical to the gitlab catalog's copy.

```markdown
## Authoring defaults

Write all published text — titles, bodies, comments, notes — as
professional, concise prose. Default to English unless the user or the
project's own conventions call for another language. State facts and
requests directly; no filler, and no emojis unless the project's existing
content uses them. The project's templates and conventions win over these
defaults.
```

### Pre-publish gate

The sentence in square brackets is a per-skill slot. Registry:
`github-issues` drops it; `github-pull-requests` uses the PR sentence
below (also embedded, condensed, in project skills generated by
meta-github); `github-planning` uses "Milestone titles and descriptions,
project names, and label names are visible to everyone who can see the
repository."; `github-releases` uses "Publishing a release publishes the
notes, the tag, and every asset, and notifies watchers — the draft step
exists so this gate always runs before the release goes live."

```markdown
## Pre-publish gate (mandatory)

Everything you send becomes public the moment the call succeeds: title, body,
every comment, labels, commit messages, the full diff, attachment contents,
and the branch name. [Creating a PR publishes every commit message and the
complete diff of `BASE...HEAD`, not just the description.] Before ANY call
that creates or edits public content:

1. Write the exact outgoing content to files in a scratch directory (title,
   body, each comment; for PRs also `git log BASE..HEAD --format=full >
   commits.txt` and `git diff BASE...HEAD > diff.patch`; copy attachments in).
2. Run the review procedure in references/publish-review.md over that
   directory. Read that file every time — do not review from memory.
3. Publish only after the verdict is exactly `SAFE TO PUBLISH: YES`. On `NO`,
   fix every finding, rebuild the files, review again. Never edit-and-publish
   without re-review.

Never publish unreviewed content. Only the user may skip this gate,
explicitly; record the skip in your summary.
Done when: a `SAFE TO PUBLISH: YES` verdict exists for the exact content
being sent.
```

### publish-review.md

The canonical copy of the full review procedure is
`github-issues/references/publish-review.md`; the copies in
`github-pull-requests`, `github-planning`, and `github-releases` must be
verbatim-identical. The condensed version embedded in generated project
skills is canonical in the meta-github catalog's CONTEXT.md.

## Disambiguation

Set up MCP/gh → `github-tooling-setup` (meta-github catalog) · issue
operations, including applying labels or a milestone to one issue →
`github-issues` · PR operations, including labels/milestone on one PR →
`github-pull-requests` · milestone lifecycle, label lifecycle (create/
rename/recolor/delete), and Projects v2 boards including adding items and
setting fields → `github-planning` · releases and tags (create, notes,
assets, publish, delete) → `github-releases` · read-only research on any
repository (issues, PRs, Actions, Discussions, releases — no write intent)
→ `github-repo-research` · authoring templates, label taxonomies, commit
and release policy → the meta-github catalog.

Tie-breaker: the skill that owns a write owns the read that immediately
precedes it (reading a release before editing it belongs to
`github-releases`); `github-repo-research` owns reads with no write intent.

## Tool inventory

Maintenance index: what the catalog's skills reference, so upstream
changes can be applied from here instead of re-reading every skill.
Whenever a skill adds, removes, or renames a reference, update this
inventory in the same commit.

### MCP capabilities (by capability — never by tool name)

| Capability | Used in |
|---|---|
| Connection/identity check (current login) | referenced by tooling verification |
| Read an issue, its comments, its labels | github-issues, github-repo-research |
| Create / update an issue (state, labels, assignees, milestone) | github-issues |
| List and search issues | github-issues, github-repo-research |
| Comment on an issue or PR | github-issues, github-pull-requests |
| Manage sub-issues | github-issues (references) |
| List repository labels | github-issues, github-planning |
| Create / update a label | github-planning |
| Create / update / merge a PR; update its branch | github-pull-requests |
| Read PR details, diff, status, checks, reviews | github-pull-requests, github-repo-research |
| List and search PRs | github-repo-research |
| Author PR reviews; reply in review threads; request Copilot review | github-pull-requests (references) |
| List/read Actions workflows, runs, jobs; job logs (failed-only, tail) | github-repo-research, github-pull-requests (references) |
| Read Discussions and their comments/categories | github-repo-research |
| Read releases (list, latest, by tag) | github-repo-research, github-releases (reads) |

### gh commands

| Command | Meaning | Used in |
|---|---|---|
| `gh auth status` | Path selection probe | all skills |
| `gh auth refresh -s project` | Add the `project` scope for Projects v2 | github-planning |
| `gh issue create/comment/close/reopen/view/list/edit` | Issue operations | github-issues |
| `gh issue pin/unpin/lock/unlock/transfer` | Long-tail issue operations | github-issues (references) |
| `gh label list` | List labels | github-issues, github-planning |
| `gh label create/edit/delete/clone` | Label lifecycle | github-planning |
| `gh api repos/{o}/{r}/milestones[/{n}]` | Milestone lifecycle (gh has no milestone command) | github-planning |
| `gh project list/view/create/edit/close/delete/link/unlink` | Projects v2 lifecycle | github-planning |
| `gh project item-add/item-list/item-edit/item-archive/field-list/field-create` | Projects v2 items and fields | github-planning |
| `gh pr create/comment/view/diff/checks/close/reopen/ready/merge/edit` | PR operations | github-pull-requests |
| `gh pr update-branch/revert/checkout` | Long-tail PR operations | github-pull-requests (references) |
| `gh api repos/{o}/{r}/pulls/{n}/reviews` and `.../comments` (+ `.../comments/{id}/replies`) | Review threads incl. Copilot bot | github-pull-requests (references) |
| `gh release create/view/list/edit/delete` (`--draft`, `--generate-notes`, `--notes-file`, `--cleanup-tag`) | Release lifecycle | github-releases |
| `gh release upload/delete-asset` | Release assets | github-releases |
| `gh release list/view` | Release reads on researched repos | github-repo-research |
| `gh run list/view` (`--log-failed`) | Actions runs and logs | github-repo-research, github-pull-requests (references) |
| `gh run download/watch/rerun/cancel`, `gh workflow list` | Artifacts, live runs, explicit rerun/cancel | github-repo-research (references) |
| `gh api repos/{o}/{r}/actions/runs/{id}/artifacts` and `.../timing` | Run artifacts and usage | github-repo-research (references) |
| `gh api graphql` | Discussions; Projects v2 long tail | github-repo-research, github-planning (references) |
| `gh api --paginate` | Cursor pagination | github-repo-research |

### REST/GraphQL/Atom endpoints (scripts/rest_read.py)

All consumed only by github-repo-research's REST fallback tier.

| Endpoint | Meaning |
|---|---|
| `GET /repos/{o}/{r}/issues`, `/issues/{n}`, `/issues/{n}/comments`, `/labels` | Issues (list mixes PRs; the script filters by the `pull_request` key) |
| `GET /repos/{o}/{r}/pulls`, `/pulls/{n}` (+`Accept: application/vnd.github.diff`), `/pulls/{n}/files`, `/pulls/{n}/reviews`, `/pulls/{n}/comments` | Pull requests, diff, files, reviews, review comments |
| `GET /repos/{o}/{r}/commits/{sha}/check-runs` | Check results for a PR head sha |
| `GET /repos/{o}/{r}/actions/runs`, `/actions/runs/{id}`, `/actions/runs/{id}/jobs`, `/actions/jobs/{id}/logs` | Actions runs, jobs, log text (logs require a token even on public repos) |
| `GET /repos/{o}/{r}/releases`, `/releases/latest`, `/releases/tags/{tag}`, `/tags` | Releases and tags (read) |
| `GET /search/issues` | Issue/PR search (10/min unauthenticated) |
| `POST /graphql` | Discussions with a token |
| `GET github.com/{o}/{r}/discussions.atom` and `/discussions/{n}` (HTML) | Tokenless Discussions: Atom list (~25), best-effort page extraction |

## References

- gh manual: <https://cli.github.com/manual/>
- REST API: <https://docs.github.com/en/rest>
- Projects v2 (concepts + GraphQL): <https://docs.github.com/en/issues/planning-and-tracking-with-projects>
- Milestones REST API: <https://docs.github.com/en/rest/issues/milestones>
- Releases: <https://docs.github.com/en/repositories/releasing-projects-on-github>
- Automatically generated release notes (`.github/release.yml`): <https://docs.github.com/en/repositories/releasing-projects-on-github/automatically-generated-release-notes>
- Discussions GraphQL guide: <https://docs.github.com/en/graphql/guides/using-the-graphql-api-for-discussions>
