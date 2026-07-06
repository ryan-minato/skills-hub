# github — Catalog Context

Rules, notes, and references that apply only to skills in this catalog.
(Repo-wide standards live in `.agents/knowledge/skill-quality.md`.)

## Requirements

- **Design floor: a ~30B-parameter local model.** Every operation gets
  exactly one recommended path: the shared "Choose your path" procedure
  (GitHub MCP if its tools are visible in-session, else authenticated gh,
  else pair with `github-tooling-setup`), then decision tables mapping
  task → MCP tool → exact gh command. No unlabeled alternatives, no
  "you could also". Add a `Done when:` line where completion is ambiguous
  or a weak model may stop early or run past done; omit it for steps that
  are simple and cannot fail.
- Bodies stay well under 200 lines. Per-framework matrices, GraphQL
  queries, log recipes, template schemas, and the publish-review procedure
  live in `references/` behind precise load conditions. Deterministic
  multi-step logic (probes, label sync, log digestion) lives in `scripts/`
  (python3 ≥3.9 stdlib only, invoked with plain `python3`, non-interactive,
  exit codes 0/1/2, data to stdout, diagnostics to stderr, idempotent).
- Multi-line content is always sent via files (`--body-file`, or MCP body
  parameters filled from files), never inline shell strings.
- **Publishing safety.** Publishing = anything that becomes public: issue/
  PR/discussion titles and bodies, comments, labels, commit messages,
  diffs, attachments, branch names. Every skill that publishes embeds the
  canonical pre-publish gate in its body and ships its own copy of
  `references/publish-review.md` — the review procedure is never delegated
  to a separate skill that might not be loaded. Tailoring is allowed only
  where the canonical text marks it.
- Cross-skill overlap is limited to the canonical blocks below and the
  disambiguation line, duplicated verbatim where needed; deep content
  lives only in the owning skill. Sibling skills are named, never
  path-linked (self-containment).
- Exact MCP tool and gh command names — **and their parameter names,
  method enums, and value forms** — must be re-verified before publishing
  a skill revision. GitHub MCP tool names have churned across server
  versions (the 2025 consolidation replaced `get_issue`-style names with
  `*_read`/`*_write` + `method`), and README prose lags behind: the
  authoritative source for parameter shapes is the machine-generated
  schema snapshots at
  <https://github.com/github/github-mcp-server/tree/main/pkg/github/__toolsnaps__>
  (e.g. the README still said `submit` after the schema had moved to
  `submit_pending`).

## Canonical blocks

The following texts are canonical. Skills copy them verbatim; when editing
one, update every copy in the same commit (`grep -rl "Choose your path"
skills/github/` finds them).

### Choose your path

```markdown
## Choose your path (do this first, once per session)

1. Look at the tools available in this session. If any tool name contains
   `issue_read`, `pull_request_read`, or a `github` MCP server prefix (for
   example `mcp__github__...`), the GitHub MCP server is connected: use the
   **MCP** column of every table below.
2. Otherwise run `gh auth status`. If it exits 0, use the **gh** column.
3. Otherwise stop and tell the user GitHub tooling is not set up. This skill
   pairs with `github-tooling-setup`. If it is not installed, install it from
   https://github.com/ryan-minato/skills.git:

       npx skills add ryan-minato/skills --skill github-tooling-setup

4. Use one column for the whole task. Never mix MCP and gh in one operation.
```

### Pre-publish gate

The sentence in square brackets appears only in `github-pull-requests` and
the generated PR project-skill template (brackets removed there).

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
`github-issues/references/publish-review.md`; the copy in
`github-pull-requests` must be verbatim-identical. The generated
project-skill templates in the conventions skills embed a condensed version
of the same procedure.

## Disambiguation

Set up MCP/gh → `github-tooling-setup` · issue operations → `github-issues`
· PR operations → `github-pull-requests` · read-only Discussions/Actions
research → `github-repo-research` · authoring templates, labels, automation
→ `github-issue-conventions` / `github-pr-conventions`.

## Tool inventory

Maintenance index: every GitHub MCP tool and gh command the catalog's
skills reference, so upstream renames can be applied from here instead of
re-reading every skill. Whenever a skill adds, removes, or renames a tool
or command reference, update this inventory in the same commit.

### GitHub MCP tools

| Tool | Methods used | Meaning | Used in |
|---|---|---|---|
| `get_me` | — | Verify auth / current login | github-tooling-setup |
| `issue_read` | `get`, `get_comments`, `get_labels` | Read one issue, its comments, its labels | github-issues |
| `issue_write` | `create`, `update` | Create/edit issue incl. state, labels, assignees | github-issues |
| `list_issues` | — | List issues in a repo | github-issues |
| `search_issues` | — | Search issues | github-issues (references/issue-recipes.md) |
| `add_issue_comment` | — | Comment on an issue or PR | github-issues, github-pull-requests |
| `sub_issue_write` | `add`, `remove`, `reprioritize` | Manage sub-issues | github-issues (references/issue-recipes.md) |
| `list_label` | — | List repo labels | github-issues, github-issue-conventions |
| `label_write` | `create`, `update` | Create/edit a label | github-issue-conventions |
| `create_pull_request` | — | Open a PR (incl. draft, reviewers) | github-pull-requests |
| `update_pull_request` | — | Edit PR incl. state, draft, reviewers | github-pull-requests |
| `update_pull_request_branch` | — | Update PR branch with base | github-pull-requests (references/pr-recipes.md) |
| `merge_pull_request` | — | Merge a PR (`merge_method`) | github-pull-requests |
| `pull_request_read` | `get`, `get_diff`, `get_status`, `get_check_runs`, `get_reviews`, `get_review_comments` | Read PR details, diff, checks, reviews | github-pull-requests |
| `pull_request_review_write` | `create`, `submit_pending` | Author a PR review | github-pull-requests (references/reviews-and-copilot.md) |
| `add_comment_to_pending_review` | — | Inline comment on a pending review | github-pull-requests (references/reviews-and-copilot.md) |
| `add_reply_to_pull_request_comment` | — | Reply in a review thread | github-pull-requests (references/reviews-and-copilot.md) |
| `request_copilot_review` | — | Request a Copilot code review | github-pull-requests (references/reviews-and-copilot.md) |
| `actions_list` | `list_workflow_runs`, `list_workflow_jobs`, `list_workflows`, `list_workflow_run_artifacts` | List workflow runs / jobs / workflows / artifacts | github-repo-research |
| `actions_get` | `get_workflow_run`, `get_workflow_run_usage` | Read one workflow run / its timing | github-repo-research |
| `get_job_logs` | — | Job logs (`failed_only`, `tail_lines`) | github-repo-research, github-pull-requests (references/checks-and-logs.md) |
| `list_discussions` | — | List discussions | github-repo-research |
| `get_discussion` | — | Read one discussion | github-repo-research |
| `get_discussion_comments` | — | Read discussion comments | github-repo-research |
| `list_discussion_categories` | — | List discussion categories | github-repo-research |

### gh commands

| Command | Meaning | Used in |
|---|---|---|
| `gh auth status` / `gh auth login` | Check / establish authentication | all skills / github-tooling-setup |
| `gh api user -q .login` | Auth smoke test | github-tooling-setup |
| `gh issue create/comment/close/reopen/view/list/edit` | Issue operations | github-issues |
| `gh issue pin/unpin/lock/unlock/transfer` | Long-tail issue operations | github-issues (references/issue-recipes.md) |
| `gh label list` | List labels | github-issues, github-issue-conventions |
| `gh label create/edit/delete` | Apply label taxonomy | github-issue-conventions (scripts/sync_labels.py) |
| `gh pr create/comment/view/diff/checks/close/reopen/ready/merge/edit` | PR operations | github-pull-requests |
| `gh pr update-branch/revert/checkout` | Long-tail PR operations | github-pull-requests (references/pr-recipes.md) |
| `gh api repos/{o}/{r}/pulls/{n}/reviews` and `.../comments` (+ `.../comments/{id}/replies`) | Review threads incl. Copilot bot | github-pull-requests (references/reviews-and-copilot.md) |
| `gh run list/view` (`--log-failed`) | Actions runs and logs | github-repo-research, github-pull-requests (references/checks-and-logs.md) |
| `gh run download/watch/rerun/cancel`, `gh workflow list` | Artifacts, live runs, explicit rerun/cancel | github-repo-research (references/actions-recipes.md) |
| `gh api repos/{o}/{r}/actions/runs/{id}/artifacts` and `.../timing` | Run artifacts and usage | github-repo-research (references/actions-recipes.md) |
| `gh repo view --json` | Read default branch and merge settings | github-pr-conventions |
| `gh api graphql` | Discussions (no first-class gh command) | github-repo-research (references/discussions-gh.md) |
| `gh api --paginate` | Cursor pagination | github-repo-research |

## References

- GitHub MCP server: <https://github.com/github/github-mcp-server>
- Remote server + toolsets: <https://github.com/github/github-mcp-server/blob/main/docs/remote-server.md>
- Server configuration (local): <https://github.com/github/github-mcp-server/blob/main/docs/server-configuration.md>
- Per-host install guides index: <https://raw.githubusercontent.com/github/github-mcp-server/refs/heads/main/docs/installation-guides/README.md>
- gh manual: <https://cli.github.com/manual/>
- Issue forms schema: <https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/syntax-for-issue-forms>
- Discussions GraphQL guide: <https://docs.github.com/en/graphql/guides/using-the-graphql-api-for-discussions>
- actions/labeler: <https://github.com/actions/labeler>
