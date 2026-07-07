# gitlab — Catalog Context

Rules, notes, and references that apply only to skills in this catalog.
(Repo-wide standards live in `.agents/knowledge/skill-quality.md`.)

This catalog holds **operational** skills: directly installable playbooks
for day-to-day GitLab work (issues, merge requests, planning structures,
wikis, releases, read-only research) on gitlab.com or any self-managed
host. Tooling setup and conventions authoring live in the `meta-gitlab`
catalog.

## Requirements

- **Design floor: a ~30B-parameter local model.** Every operation gets
  exactly one recommended path: the shared "Choose your path" procedure
  (authenticated glab first; the GitLab Duo MCP server only when glab is
  unavailable and the row names an MCP capability; else pair with
  `gitlab-tooling-setup`), then decision tables mapping task → exact glab
  command → MCP capability (or `—` when none exists). No unlabeled
  alternatives, no "you could also". Add a `Done when:` line where
  completion is ambiguous or a weak model may stop early or run past done;
  omit it for steps that are simple and cannot fail.
- **MCP tools are described by capability, never by name.** MCP tool names
  churn across server versions, and MCP servers self-describe each tool's
  purpose and parameters — the agent matches by purpose at runtime. Skill
  bodies, tables, and references write "the MCP tool that reads an issue",
  never a concrete tool name or a `mcp__...` prefix pattern. A capability
  cell may carry a minimum GitLab version in parentheses when one is
  known. Exact names are allowed only for glab commands, REST/GraphQL
  endpoints, and bundled scripts. Consequence: only glab/REST references
  need re-verification; MCP cells stay valid across server versions.
- **Host-agnosticism is load-bearing.** GitLab is routinely self-managed:
  never hardcode `gitlab.com`. Every command, endpoint, config example,
  and script is written against a `HOST` derived from the project's git
  remote or `GITLAB_HOST`/`GL_HOST`; the MCP endpoint is always written
  `https://<gitlab-host>/api/v4/mcp`. Cross-host targeting uses
  `--hostname HOST` on `glab api`/`glab auth`, and `GITLAB_HOST=HOST` for
  command groups without a hostname flag. Scripts take `--hostname`/
  `--host` and never silently default to gitlab.com when a remote is
  available.
- **Tier and version gating is marked inline.** The Duo MCP server
  requires GitLab ≥ 18.6, Premium/Ultimate with GitLab Duo enabled, and is
  Beta. Premium/Ultimate features (iterations, epics, group wikis,
  scoped-label enforcement) carry a tier badge in the section header or
  table row. A connected MCP server on an older self-managed instance
  legitimately lacks newer capabilities — absence means "use the glab
  column", not an error. GitLab returns **404, not 403**, for features
  above the instance's tier — say so wherever a user could hit it.
  Skills with no MCP coverage at all (`gitlab-planning`, `gitlab-wiki`,
  `gitlab-releases`) say so in their intro and ship single-path tables
  instead of embedding the MCP step.
- **Convention discovery is mandatory before any create.** Every skill
  that creates content embeds "Match the project's conventions" with its
  own discovery table (description templates, labels, milestones,
  iterations/epics where relevant, tag schemes, project convention skills
  / AGENTS.md). Inventing structure parallel to what the project already
  defines is a defect, not a style choice.
- Bodies stay well under 200 lines. Install matrices, recipe long-tails,
  GraphQL, log procedures, and the publish-review procedure live in
  `references/` behind precise load conditions. Deterministic multi-step
  logic (version bumping, log digestion) lives in `scripts/` (python3
  ≥3.9 stdlib only, invoked with plain `python3`, non-interactive, exit
  codes 0/1/2, data to stdout, diagnostics to stderr, idempotent).
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
  labels, board and list names, release notes and assets, commit
  messages, diffs, attachments, branch and tag names. On private or
  internal projects the content becomes visible to every member just as
  instantly as it becomes public on public projects. A line starting with
  `/` in any body or comment can execute as a GitLab **quick action**
  (`/close`, `/assign`, ...) — a hazard in drafted text and, deliberately
  used, the sanctioned way to do things glab lacks flags for. Every skill
  that publishes embeds the canonical pre-publish gate in its body and
  ships its own copy of `references/publish-review.md` — the review
  procedure is never delegated to a separate skill that might not be
  loaded. Tailoring is allowed only where the canonical text marks it.
- **Authoring defaults are canonical.** Every skill that authors prose
  embeds the fixed "Authoring defaults" block below, word-for-word
  identical to the github catalog's copy.
- Cross-skill overlap is limited to the canonical blocks below and the
  disambiguation line, duplicated verbatim where needed; deep content
  lives only in the owning skill. Sibling skills (including meta-gitlab
  skills) are named, never path-linked (self-containment).
- Exact glab subcommand and flag names — and REST/GraphQL endpoint
  shapes — must be re-verified before publishing a skill revision. glab's
  command surface churns across releases (`mr note` grew subcommands;
  output-format flags differ between command groups), `glab work-items`
  is experimental, and the Epics REST API is deprecated (removal in the
  unreleased API v5). Authoritative source: <https://docs.gitlab.com/cli/>
  per command group. MCP capabilities are deliberately name-free and carry
  no such duty.

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
2. Otherwise, look at the tools available in this session. If a connected
   MCP server provides GitLab tools for the work this skill covers (each
   tool's description states its purpose; names vary across server
   versions), use the **MCP** column, picking the tool whose description
   matches the row's capability — but only for rows that name one. Rows
   marked `—` have no MCP tool, and an older self-managed instance may
   lack a capability entirely: for those tasks, tell the user glab is
   required.
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

#### Single-path skills (gitlab-planning, gitlab-wiki, gitlab-releases)

Skills with no MCP coverage drop step 2, renumber, and open their intro
with one sentence stating that the Duo MCP server has no tools for this
domain and glab (with `glab api` for gaps) is the only path.

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
wherever the tables show `G/P` (glab: `-R G/P`; MCP: the project
identifier parameter). Inside the project's checkout, glab resolves the
host from the remote on its own; outside it, pass `--hostname HOST` to
`glab api`/`glab auth` and set `GITLAB_HOST=HOST` for other command
groups.
```

### Match the project's conventions

Only the table rows are tailorable per skill; the surrounding text is
fixed. Embedded by every skill that creates content.

```markdown
## Match the project's conventions (before any create)

Before creating anything, discover what the project already defines and
use it — never invent parallel structure:

| Artifact | How to check |
|---|---|
| <skill-specific rows> | <exact command or MCP capability> |

If a project-level convention skill or an AGENTS.md conventions section
covers this task, follow it over this skill's defaults.
Done when: each artifact was checked and the draft uses the project's
existing structures (or the user approved new ones).
```

### Authoring defaults

Fixed text; embedded by every skill that authors prose. Word-for-word
identical to the github catalog's copy.

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
`gitlab-issues` drops it; `gitlab-merge-requests` uses the MR sentence
below (also embedded, condensed, in project skills generated by
meta-gitlab); `gitlab-planning` uses "Milestone, board, list, epic, and
label names and descriptions are visible to everyone who can see the
project."; `gitlab-wiki` uses "Pushing to the wiki repository publishes
every commit message and the complete content of every committed file,
not just the page you edited."; `gitlab-releases` uses "GitLab has no
draft releases — creating a release publishes the tag, name, notes, and
asset links the moment the call succeeds, so this gate runs on the
complete assembled release before create."

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
`gitlab-merge-requests`, `gitlab-planning`, `gitlab-wiki`, and
`gitlab-releases` must be verbatim-identical. It adapts the github
catalog's procedure with GitLab wording and adds a quick-actions checklist
bullet. The condensed version embedded in generated project skills is
canonical in the meta-gitlab catalog's CONTEXT.md.

## Disambiguation

Set up glab/MCP → `gitlab-tooling-setup` (meta-gitlab catalog) · issue
operations, including applying labels or assigning one issue to a
milestone, iteration, or epic → `gitlab-issues` · MR operations, including
labels/milestone on one MR → `gitlab-merge-requests` · milestone/
iteration/board/epic lifecycle and label lifecycle (create/rename/recolor/
delete) → `gitlab-planning` · releases and tags (create, notes, assets,
milestone association, delete) → `gitlab-releases` · wiki pages (including
reads) → `gitlab-wiki` · read-only research (issues, MRs, pipelines,
releases, search — no write intent) → `gitlab-repo-research` · authoring
templates, label taxonomies, commit and release policy → the meta-gitlab
catalog.

Boundary rules: moving an issue between label-backed board lists is
relabeling and belongs to `gitlab-issues`; attaching a milestone to a
release belongs to `gitlab-releases`. Tie-breaker: the skill that owns a
write owns the read that immediately precedes it (reading a release before
editing it belongs to `gitlab-releases`); `gitlab-repo-research` owns
reads with no write intent.

## Tool inventory

Maintenance index: what the catalog's skills reference, so upstream
changes and deprecations can be applied from here instead of re-reading
every skill. Whenever a skill adds, removes, or renames a reference,
update this inventory in the same commit.

### MCP capabilities (by capability — never by tool name)

Minimum GitLab versions in parentheses where known; an instance below the
minimum simply lacks the capability.

| Capability | Used in |
|---|---|
| Connection/version check (18.3) | referenced by tooling verification |
| Create an issue (18.4) / read an issue (18.4) | gitlab-issues, gitlab-repo-research |
| Comment on an issue or work item (18.7); read those comments (18.7) | gitlab-issues, gitlab-repo-research |
| Search labels (18.9) | gitlab-issues |
| Create an MR (18.5) / read MR details (18.4) | gitlab-merge-requests, gitlab-repo-research |
| Read MR commits, diffs, attached pipelines (18.4) | gitlab-merge-requests, gitlab-repo-research |
| Comment or reply on an MR (19.2); read MR comments and threads (19.2) | gitlab-merge-requests, gitlab-repo-research |
| Read a pipeline's jobs (18.4); read a job log — no tail parameter, flooding risk (19.1) | gitlab-repo-research, gitlab-merge-requests (references) |
| List/run/retry/cancel pipelines (18.10) | gitlab-repo-research |
| Instance/group/project search (18.4); semantic code search (Duo, Beta, 18.7) | gitlab-repo-research |
| No capabilities exist for milestones, iterations, boards, epics, wikis, labels lifecycle, or releases | gitlab-planning, gitlab-wiki, gitlab-releases are glab-only |

### glab commands

| Command | Meaning | Used in |
|---|---|---|
| `glab auth status` (`--hostname`) | Path selection probe per host | all skills |
| `glab api <endpoint>` | Direct REST/GraphQL calls (`--hostname`, `-f`/`-F`, `--paginate`) | gitlab-planning, gitlab-wiki, gitlab-releases, gitlab-repo-research |
| `glab api version` | Instance version probe | gitlab-planning |
| `glab issue create/note/close/reopen/view/list/update` | Issue operations | gitlab-issues |
| `glab label list` | List labels | gitlab-issues, gitlab-planning |
| `glab label create` | Create a label (update/delete go through `glab api`) | gitlab-planning |
| `glab mr create/note/view/diff/list/close/reopen/update/approve/revoke/merge` | MR operations | gitlab-merge-requests |
| `glab mr rebase/checkout/issues/approvers` | Long-tail MR operations, approval reads | gitlab-merge-requests (references), gitlab-repo-research |
| `glab ci list/get/trace` | Pipeline status and job logs | gitlab-merge-requests, gitlab-repo-research |
| `glab ci retry/cancel/run/artifact` | Explicit pipeline writes, artifact download | gitlab-repo-research (references) |
| `glab milestone list/get/create/edit/delete` | Milestone lifecycle (`--group`) | gitlab-planning |
| `glab iteration list` | List iterations (Premium) | gitlab-planning |
| `glab work-items create/list/update` | Experimental work-item path for epics | gitlab-planning (references) |
| `glab release create` (`--name`, `--notes-file`, `--ref`, `--tag-message`, `--milestone`, `--no-close-milestone`, `--no-update`, asset files) | Create/update a release (publishes immediately) | gitlab-releases |
| `glab release list/view/delete` (`-y`) | Release reads and deletion (tag survives delete) | gitlab-releases, gitlab-repo-research |
| `glab release upload/delete-asset` | Release assets (`path#label#type`) | gitlab-releases |
| `glab changelog generate` | Notes from `Changelog:` commit trailers | gitlab-releases |

### REST/GraphQL endpoints (via `glab api` or scripts/rest_read.py)

| Endpoint | Meaning | Used in |
|---|---|---|
| `GET /projects/:id/issues[/:iid]`, `/issues/:iid/notes`, `/labels` | Issues, notes, labels (read) | gitlab-repo-research (scripts/rest_read.py) |
| `GET /projects/:id/merge_requests[/:iid]` + `/diffs`, `/commits`, `/notes`, `/approvals`, `/pipelines` | MR reads | gitlab-repo-research (scripts/rest_read.py) |
| `GET /projects/:id/pipelines[/:id]`, `/pipelines/:id/jobs`, `/jobs/:id/trace` | Pipelines, jobs, traces | gitlab-repo-research (both scripts) |
| `GET /projects/:id/releases[/:tag]`, `/repository/tags` | Release and tag reads | gitlab-repo-research (scripts/rest_read.py) |
| `PUT /projects/:id/releases/:tag` | Edit a release (glab has no release-edit subcommand) | gitlab-releases |
| `POST/DELETE /projects/:id/releases/:tag/assets/links[/:id]` | Link-only release assets | gitlab-releases |
| `POST/DELETE /projects/:id/repository/tags` | Tag create (annotated via `message`) and delete | gitlab-releases |
| `GET /projects/:id/repository/changelog` | Changelog generation via API | gitlab-releases (references) |
| `GET /search?scope=...`, `GET /groups/:id/search` | Instance/group search | gitlab-repo-research (references) |
| `PUT/DELETE /projects/:id/labels/:label_id` | Label update/delete (no glab subcommand) | gitlab-planning |
| `GET/POST/PUT/DELETE /projects/:id/boards[/:bid]` + `/lists[/:lid]` | Project boards and lists | gitlab-planning |
| `GET/POST/PUT/DELETE /groups/:id/boards...`, `GET /groups/:id/epic_boards` | Group boards (Premium), epic boards (read-only) | gitlab-planning (references) |
| `GET /groups/:id/iterations`, `GET /projects/:id/iterations` | Iteration listing (Premium) | gitlab-planning |
| `GET/POST/PUT/DELETE /groups/:id/epics[/:iid]` | Epic lifecycle (deprecated-but-stable REST) | gitlab-planning |
| `GET/POST/PUT/DELETE /projects/:id/wikis[/:slug]`, `POST .../wikis/attachments` | Wiki page CRUD + attachments | gitlab-wiki |
| `GET/POST/PUT/DELETE /groups/:id/wikis...` | Group wikis (Premium) | gitlab-wiki |
| `POST /graphql` (`iterationCreate`, `iterationCadenceCreate`, `workItemUpdate`) | Cadence management; work-item close | gitlab-planning (references) |
| `https://HOST/NAMESPACE/PROJECT.wiki.git` | Wiki-as-git clone URL | gitlab-wiki (references) |

## References

- glab manual: <https://docs.gitlab.com/cli/>
- glab source and releases: <https://gitlab.com/gitlab-org/cli>
- GitLab Duo MCP server: <https://docs.gitlab.com/user/gitlab_duo/model_context_protocol/mcp_server/>
- REST API v4: <https://docs.gitlab.com/api/rest/>
- Releases API: <https://docs.gitlab.com/api/releases/> · Tags API: <https://docs.gitlab.com/api/tags/>
- Changelogs: <https://docs.gitlab.com/user/project/changelogs/>
- Search API: <https://docs.gitlab.com/api/search/>
- Quick actions: <https://docs.gitlab.com/user/project/quick_actions/>
- Labels: <https://docs.gitlab.com/user/project/labels/>
- Wikis API: <https://docs.gitlab.com/api/wikis/> · Boards API: <https://docs.gitlab.com/api/boards/> · Epics API: <https://docs.gitlab.com/api/epics/>
- CI/CD YAML: <https://docs.gitlab.com/ci/yaml/> · Predefined CI variables: <https://docs.gitlab.com/ci/variables/predefined_variables/>
