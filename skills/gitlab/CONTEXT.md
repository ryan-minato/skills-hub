# gitlab — Catalog Context

Rules, notes, and references that apply only to skills in this catalog.
(Repo-wide standards live in `.agents/knowledge/skill-quality.md`.)

## Requirements

- **Design floor: a ~30B-parameter local model.** Every operation gets
  exactly one recommended path: the shared "Choose your path" procedure
  (authenticated glab first; the GitLab Duo MCP server only when glab is
  unavailable and the operation has an MCP tool; else pair with
  `gitlab-tooling-setup`), then decision tables mapping
  task → exact glab command → MCP tool (or `—` when none exists). No
  unlabeled alternatives, no "you could also". Add a `Done when:` line
  where completion is ambiguous or a weak model may stop early or run past
  done; omit it for steps that are simple and cannot fail.
- **Host-agnosticism is load-bearing.** GitLab is routinely self-managed:
  never hardcode `gitlab.com`. Every command, endpoint, config example,
  and script is written against a `HOST` derived from the project's git
  remote or `GITLAB_HOST`/`GL_HOST`; the MCP endpoint is always written
  `https://<gitlab-host>/api/v4/mcp`. Cross-host targeting uses
  `--hostname HOST` on `glab api`/`glab auth`, and `GITLAB_HOST=HOST` for
  command groups without a hostname flag. Scripts take `--hostname`/
  `--host` and never silently default to gitlab.com when a remote is
  available.
- **Tier and version gating is marked inline.** The MCP server requires
  GitLab ≥ 18.6, Premium/Ultimate with GitLab Duo enabled, and is Beta;
  individual tools have their own minimums (18.3–19.2), carried in
  parentheses in every MCP table entry. Premium/Ultimate features
  (iterations, epics, group wikis, scoped-label enforcement, CODEOWNERS
  enforcement, required approvals) carry a tier badge in the section
  header or table row. A connected MCP server on an older self-managed
  instance legitimately lacks newer tools — absence means "use the glab
  column", not an error. GitLab returns **404, not 403**, for features
  above the instance's tier.
- Bodies stay well under 200 lines. Install matrices, recipe long-tails,
  GraphQL, log procedures, template schemas, and the publish-review
  procedure live in `references/` behind precise load conditions.
  Deterministic multi-step logic (probes, label sync, log digestion)
  lives in `scripts/` (python3 ≥3.9 stdlib only, invoked with plain
  `python3`, non-interactive, exit codes 0/1/2, data to stdout,
  diagnostics to stderr, idempotent).
- **Multi-line content is always sent via files.** glab has no
  `--body-file`: the catalog pattern is to write the content to a file,
  then pass it with `--description "$(cat BODY.md)"` or
  `-m "$(cat COMMENT.md)"` (command substitution does not re-expand file
  contents). Where a command lacks a text flag, `glab api` with
  `-F "field=@FILE"` is the fallback. Never retype reviewed content
  inline.
- **Non-interactive rule.** glab prompts and opens editors by default:
  always pass `--yes` on create and merge commands that support it,
  always supply `-t`/`-d` so no editor opens, and never use `--fill` — it
  publishes generated content that never went through the review gate.
- **Publishing safety.** Publishing = anything that becomes visible to
  others: issue/MR/epic/milestone/wiki titles and bodies, comments,
  labels, board and list names, commit messages, diffs, attachments, and
  branch names. On private or internal projects the content becomes
  visible to every member just as instantly as it becomes public on
  public projects. A line starting with `/` in any body or comment can
  execute as a GitLab **quick action** (`/close`, `/assign`, ...) — a
  hazard in drafted text and, deliberately used, the sanctioned way to do
  things glab lacks flags for. Every skill that publishes embeds the
  canonical pre-publish gate in its body and ships its own copy of
  `references/publish-review.md` — the review procedure is never
  delegated to a separate skill that might not be loaded. Tailoring is
  allowed only where the canonical text marks it.
- Cross-skill overlap is limited to the canonical blocks below and the
  disambiguation line, duplicated verbatim where needed; deep content
  lives only in the owning skill. Sibling skills are named, never
  path-linked (self-containment).
- Exact glab subcommand and flag names — and MCP tool names, parameter
  shapes, and minimum versions — must be re-verified before publishing a
  skill revision. glab's command surface churns across releases (`mr
  note` grew subcommands; output-format flags differ between command
  groups), `glab work-items` is experimental, and the Epics REST API is
  deprecated (removal in the unreleased API v5). Authoritative sources:
  <https://docs.gitlab.com/cli/> per command group, and
  <https://docs.gitlab.com/user/gitlab_duo/model_context_protocol/mcp_server_tools/>
  for MCP tools and their minimum versions.

## Canonical blocks

The following texts are canonical. Skills copy them verbatim; when editing
one, update every copy in the same commit (`grep -rl "Choose your path"
skills/gitlab/` finds them).

### Choose your path

```markdown
## Choose your path (do this first, once per session)

1. Run `glab auth status`. If it exits 0 and lists the target host, use the
   **glab** column of every table below. For a self-managed host, check that
   host specifically: `glab auth status --hostname HOST`.
2. Otherwise, look at the tools available in this session. If any tool name
   contains `create_issue`, `get_merge_request`, or a `gitlab` MCP server
   prefix (for example `mcp__gitlab__...`), the GitLab MCP server is
   connected: use the **MCP** column — but only for rows that show an MCP
   tool. Rows marked `—` have no MCP tool, and a self-managed instance older
   than a tool's minimum version lacks that tool: for those tasks, tell the
   user glab is required.
3. Otherwise stop and tell the user GitLab tooling is not set up. This skill
   pairs with `gitlab-tooling-setup`. If it is not installed, install it from
   https://github.com/ryan-minato/skills.git:

       npx skills add ryan-minato/skills --skill gitlab-tooling-setup

4. Use one column for the whole task. Never mix glab and MCP in one
   operation.
```

#### Read-only variant (gitlab-repo-research only)

`gitlab-repo-research` inserts a REST-fallback step between steps 2 and 3
and renumbers accordingly; its closing step reads "Use one path for the
whole task. Never mix glab, MCP, and REST in one operation." The inserted
step is:

```markdown
3. Otherwise, if the target project is public, or a token is set in
   `GITLAB_TOKEN`/`GITLAB_ACCESS_TOKEN` even though glab is missing, use the
   REST fallback: read [references/rest-fallback.md](references/rest-fallback.md)
   and run [scripts/rest_read.py](scripts/rest_read.py) with `--host HOST`.
   Reads only.
```

### Identify the host and project

Self-managed support lives in this block; every operational skill embeds
it (skills that also work at group level append their group-derivation
sentence where the canonical text marks it).

```markdown
## Identify the host and project

Run `git remote get-url origin`. The host is the part right after
`https://` or the `@` (GitLab is often self-managed — never assume
`gitlab.com`). The project path is everything after the host, with any
trailing `.git` stripped; GitLab paths can nest (`group/subgroup/project`
is one project — keep the full path). If there is no origin remote, or the
user named a different project, use that instead. Substitute the full path
wherever the tables show `G/P` (glab: `-R G/P`; MCP: the project `id`
parameter). Inside the project's checkout, glab resolves the host from the
remote on its own; outside it, pass `--hostname HOST` to `glab api`/`glab
auth` and set `GITLAB_HOST=HOST` for other command groups.
```

### Pre-publish gate

The sentence in square brackets appears only in `gitlab-merge-requests`
and the generated MR project-skill template (brackets removed there);
`gitlab-wiki` and `gitlab-planning` replace it with their own tailored
sentence at the same position.

```markdown
## Pre-publish gate (mandatory)

Everything you send becomes visible the moment the call succeeds — to the
whole internet on public projects, and to every member just as instantly
on private or internal ones: title, body, every comment, labels, commit
messages, the full diff, attachment contents, and the branch name.
[Creating an MR publishes every commit message and the complete diff of
`TARGET...SOURCE`, not just the description.] A line starting with `/` in
any body or comment can execute as a GitLab quick action (for example
`/close`). Before ANY call that creates or edits such content:

1. Write the exact outgoing content to files in a scratch directory
   (title, body, each comment; for MRs also `git log TARGET..SOURCE
   --format=full > commits.txt` and `git diff TARGET...SOURCE >
   diff.patch`; copy attachments in).
2. Run the review procedure in references/publish-review.md over that
   directory. Read that file every time — do not review from memory.
3. Publish only after the verdict is exactly `SAFE TO PUBLISH: YES`. On
   `NO`, fix every finding, rebuild the files, review again. Never
   edit-and-publish without re-review.

Never publish unreviewed content. Only the user may skip this gate,
explicitly; record the skip in your summary.
Done when: a `SAFE TO PUBLISH: YES` verdict exists for the exact content
being sent.
```

### publish-review.md

The canonical copy of the full review procedure is
`gitlab-issues/references/publish-review.md`; the copies in
`gitlab-merge-requests`, `gitlab-planning`, and `gitlab-wiki` must be
verbatim-identical. It adapts the github catalog's procedure with GitLab
wording and adds a quick-actions checklist bullet. The generated
project-skill templates in the conventions skills embed a condensed
version of the same procedure.

## Disambiguation

Set up glab/MCP → `gitlab-tooling-setup` · issue operations →
`gitlab-issues` · MR operations → `gitlab-merge-requests` · read-only
research (issues, MRs, pipelines, search — including projects without
write access) → `gitlab-repo-research` · milestone/iteration/board/epic
lifecycle → `gitlab-planning` · wiki pages (including reads) →
`gitlab-wiki` · authoring templates, labels, automation →
`gitlab-issue-conventions` / `gitlab-mr-conventions`.

Boundary rules: assigning one issue to a milestone, iteration, or epic
(issue edit / quick actions) belongs to `gitlab-issues`; setting a
milestone on an MR belongs to `gitlab-merge-requests`; reading boards,
milestones, epics, or wiki pages belongs to `gitlab-planning`/
`gitlab-wiki`, not `gitlab-repo-research`.

## Tool inventory

Maintenance index: every GitLab MCP tool, glab command, and REST/GraphQL
endpoint the catalog's skills reference, so upstream renames and
deprecations can be applied from here instead of re-reading every skill.
Whenever a skill adds, removes, or renames a tool or command reference,
update this inventory in the same commit.

### GitLab MCP tools

| Tool | Min GitLab | Meaning | Used in |
|---|---|---|---|
| `get_mcp_server_version` | 18.3 | Verify MCP connectivity / server version | gitlab-tooling-setup |
| `create_issue` | 18.4 | Create an issue | gitlab-issues |
| `get_issue` | 18.4 | Read one issue | gitlab-issues, gitlab-repo-research |
| `create_workitem_note` | 18.7 | Comment on an issue/work item | gitlab-issues |
| `get_workitem_notes` | 18.7 | Read issue/work-item comments | gitlab-issues, gitlab-repo-research |
| `create_merge_request` | 18.5 | Open an MR | gitlab-merge-requests |
| `get_merge_request` | 18.4 | Read MR details | gitlab-merge-requests, gitlab-repo-research |
| `get_merge_request_commits` | 18.4 | MR commit list | gitlab-repo-research |
| `get_merge_request_diffs` | 18.4 | MR diffs | gitlab-merge-requests, gitlab-repo-research |
| `get_merge_request_pipelines` | 18.4 | Pipelines attached to an MR | gitlab-merge-requests, gitlab-repo-research |
| `create_merge_request_note` | 19.2 | Comment / reply on an MR | gitlab-merge-requests |
| `get_merge_request_notes` | 19.2 | Read MR comments and threads | gitlab-merge-requests, gitlab-repo-research |
| `get_pipeline_jobs` | 18.4 | Jobs of one pipeline | gitlab-repo-research, gitlab-merge-requests (references/pipeline-logs.md) |
| `get_job_log` | 19.1 | Job trace — no tail parameter (flooding risk) | gitlab-repo-research, gitlab-merge-requests (references/pipeline-logs.md) |
| `manage_pipeline` | 18.10 | List/run/retry/cancel pipelines | gitlab-repo-research |
| `search` | 18.4 | Instance/group/project search | gitlab-repo-research |
| `search_labels` | 18.9 | Search labels | gitlab-issues |
| `semantic_code_search` | 18.7 | Semantic code search (Duo, Beta) | gitlab-repo-research (references/search-recipes.md) |

### glab commands

| Command | Meaning | Used in |
|---|---|---|
| `glab auth status` / `glab auth login` | Check / establish authentication (`--hostname`) | all skills / gitlab-tooling-setup |
| `glab api user` | Auth smoke test | gitlab-tooling-setup |
| `glab api <endpoint>` | Direct REST/GraphQL calls (`--hostname`, `-f`/`-F`, `--paginate`) | gitlab-planning, gitlab-wiki, gitlab-repo-research, conventions scripts |
| `glab api version` | Instance version probe | gitlab-planning |
| `glab issue create/note/close/reopen/view/list/update` | Issue operations | gitlab-issues |
| `glab label list` | List labels | gitlab-issues, gitlab-issue-conventions |
| `glab mr create/note/view/diff/list/close/reopen/update/approve/revoke/merge` | MR operations | gitlab-merge-requests |
| `glab mr rebase/checkout/issues/approvers` | Long-tail MR operations, approval reads | gitlab-merge-requests (references/mr-recipes.md), gitlab-repo-research |
| `glab ci list/get/trace` | Pipeline status and job logs | gitlab-merge-requests, gitlab-repo-research |
| `glab ci retry/cancel/run/lint/artifact` | Explicit pipeline writes, config lint, artifact download | gitlab-repo-research (references/pipeline-recipes.md), gitlab-mr-conventions (lint) |
| `glab milestone list/get/create/edit/delete` | Milestone lifecycle (`--group`) | gitlab-planning |
| `glab iteration list` | List iterations (Premium) | gitlab-planning |
| `glab work-items create/list/update` | Experimental work-item path for epics | gitlab-planning (references/epics-work-items.md) |

### REST/GraphQL endpoints (via `glab api` or scripts/rest_read.py)

| Endpoint | Meaning | Used in |
|---|---|---|
| `GET /projects/:id/issues[/:iid]`, `/issues/:iid/notes`, `/labels` | Issues, notes, labels (read) | gitlab-repo-research (scripts/rest_read.py) |
| `GET /projects/:id/merge_requests[/:iid]` + `/diffs`, `/commits`, `/notes`, `/approvals`, `/pipelines` | MR reads | gitlab-repo-research (scripts/rest_read.py) |
| `GET /projects/:id/pipelines[/:id]`, `/pipelines/:id/jobs`, `/jobs/:id/trace` | Pipelines, jobs, traces | gitlab-repo-research (both scripts) |
| `GET /search?scope=...`, `GET /groups/:id/search` | Instance/group search | gitlab-repo-research (references/search-recipes.md) |
| `GET/POST/PUT/DELETE /projects/:id/labels[/:label_id]`, `GET /groups/:id/labels` | Label taxonomy sync | gitlab-issue-conventions (scripts/sync_labels.py) |
| `GET /projects/:fullpath` | Merge settings (merge_method, squash_option) | gitlab-mr-conventions |
| `GET/POST/PUT/DELETE /projects/:id/boards[/:bid]` + `/lists[/:lid]` | Project boards and lists | gitlab-planning |
| `GET/POST/PUT/DELETE /groups/:id/boards...`, `GET /groups/:id/epic_boards` | Group boards (Premium), epic boards (read-only) | gitlab-planning (references/boards-premium.md) |
| `GET /groups/:id/iterations`, `GET /projects/:id/iterations` | Iteration listing (Premium) | gitlab-planning |
| `GET/POST/PUT/DELETE /groups/:id/epics[/:iid]` | Epic lifecycle (deprecated-but-stable REST) | gitlab-planning |
| `GET/POST/PUT/DELETE /projects/:id/wikis[/:slug]`, `POST .../wikis/attachments` | Wiki page CRUD + attachments | gitlab-wiki |
| `GET/POST/PUT/DELETE /groups/:id/wikis...` | Group wikis (Premium) | gitlab-wiki |
| `POST /graphql` (`iterationCreate`, `iterationCadenceCreate`, `workItemUpdate`) | Cadence management; work-item close | gitlab-planning (references) |
| `https://HOST/NAMESPACE/PROJECT.wiki.git` | Wiki-as-git clone URL | gitlab-wiki (references/wiki-git.md) |

## References

- glab manual: <https://docs.gitlab.com/cli/>
- glab source and releases: <https://gitlab.com/gitlab-org/cli>
- GitLab Duo MCP server: <https://docs.gitlab.com/user/gitlab_duo/model_context_protocol/mcp_server/>
- MCP tools and minimum versions: <https://docs.gitlab.com/user/gitlab_duo/model_context_protocol/mcp_server_tools/>
- REST API v4: <https://docs.gitlab.com/api/rest/>
- Search API: <https://docs.gitlab.com/api/search/>
- Quick actions: <https://docs.gitlab.com/user/project/quick_actions/>
- Description templates: <https://docs.gitlab.com/user/project/description_templates/>
- Labels: <https://docs.gitlab.com/user/project/labels/>
- Wikis API: <https://docs.gitlab.com/api/wikis/> · Boards API: <https://docs.gitlab.com/api/boards/> · Epics API: <https://docs.gitlab.com/api/epics/>
- CI/CD YAML: <https://docs.gitlab.com/ci/yaml/> · Predefined CI variables: <https://docs.gitlab.com/ci/variables/predefined_variables/>
- Personal access tokens: <https://docs.gitlab.com/user/profile/personal_access_tokens/>
