# meta-gitlab — Catalog Context

Rules, notes, and references that apply only to skills in this catalog.
(Repo-wide standards live in `.agents/knowledge/skill-quality.md`.)

## Scope

meta-gitlab holds **harness-authoring** skills: they set up the tooling a
coding agent needs for GitLab (`gitlab-tooling-setup`) and author a
project's conventions (the `*-conventions` skills). Their value lands in
what they leave behind — configured tooling, committed templates, CI jobs,
validators, and a generated project-level skill — not in the skill staying
installed. Day-to-day GitLab operations belong to the `gitlab` catalog.

## Requirements

- **Design floor: a ~30B-parameter local model.** Every step gets exactly
  one recommended path and a decision table where a choice exists. No
  unlabeled alternatives, no "you could also". Add a `Done when:` line where
  completion is ambiguous or a weak model may stop early or run past done.
- Bodies stay well under 200 lines. Schemas, per-framework matrices, and
  customization long-tails live in `references/` behind precise load
  conditions. Deterministic multi-step logic lives in `scripts/` (python3
  ≥3.9 stdlib only, invoked with plain `python3`, non-interactive, exit
  codes 0/1/2, data to stdout, diagnostics to stderr, idempotent).
- **Host-agnosticism is load-bearing.** GitLab is routinely self-managed:
  never hardcode `gitlab.com` in a skill body, template, CI snippet, or
  script. Scripts take `--hostname`/`--host`; CI snippets use predefined
  variables (`$CI_SERVER_HOST`, `$CI_API_V4_URL`) instead of literal hosts;
  the MCP endpoint is always written `https://<gitlab-host>/api/v4/mcp`.
- **Free-tier default, tier badges everywhere else.** Every shipped
  mechanism works on the Free tier unless the section or table row carries
  a Premium/Ultimate badge (push rules, CODEOWNERS enforcement, required
  approvals, scoped-label enforcement). GitLab returns **404, not 403**,
  for features above the instance's tier — say so wherever a user could
  hit it.
- **Tokenless CI.** Shipped CI snippets run without job tokens or secrets:
  checklist/format validation in merge request pipelines
  (`$CI_PIPELINE_SOURCE == "merge_request_event"`), tag checks in tag
  pipelines (`$CI_COMMIT_TAG`). Anything needing a token appears only
  behind an explicit user opt-in, marked as such. Shipped CI validators are
  dependency-free python3 scripts committed into the target project.
- **Local-files doctrine (conventions skills).** Conventions skills write
  local files only; nothing they do publishes directly. The project's
  normal git flow publishes the outputs, and that flow carries its own
  review gates — so conventions skills embed no full pre-publish gate. Any
  **generated** project skill that publishes content embeds the condensed
  gate below. `gitlab-tooling-setup` is the exception to the conventions
  shape: it configures the agent's environment (glab auth, optional Duo
  MCP) and follows its own assess → install → verify structure.
- **Quick actions are a feature and a hazard.** Templates may embed quick
  actions (`/label`, `/assign`, ...) deliberately — document every quick
  action a shipped template embeds, in the template itself and in the
  skill body. Generated skills warn that any body line starting with `/`
  can execute as a quick action.
- **Generated project skills are products.** They must meet the same bar as
  a published skill: the ~30B floor, one recommended path per operation,
  `Done when:` lines, frontmatter `name` equal to the directory name, the
  condensed pre-publish gate when they publish, and **zero leftover
  `{{...}}` placeholders**. Template placeholders use `{{UPPER_SNAKE}}`; the
  Done-when of every generate step is placeholder-free output.
- **MCP tools are described by capability, never by name.** MCP tool names
  churn across server versions, and MCP servers self-describe each tool's
  purpose — write "the MCP tool that reads an issue", not a concrete tool
  name, in skill bodies, tables, and references. Exact names are allowed
  only for CLI commands (glab), REST/GraphQL endpoints, and bundled
  scripts.
- Cross-skill overlap is limited to the canonical blocks below, duplicated
  verbatim; deep content lives only in the owning skill. Sibling skills
  (including operational counterparts in the `gitlab` catalog) are named
  with the install-pointer pattern, never path-linked (self-containment).
- Exact glab subcommand and flag names, CI keywords, and GitLab file
  conventions (template paths, `changelog_config.yml`) must be re-verified
  before publishing a skill revision, against <https://docs.gitlab.com/cli/>
  and <https://docs.gitlab.com/>.

## Canonical blocks

The following texts are canonical. Conventions skills copy them verbatim;
when editing one, update every copy in the same commit
(`grep -rl "Assess the project first" skills/meta-gitlab/` finds them).

### Assess the project first

Only the bracketed artifact list is tailorable per skill.

```markdown
## Assess the project first

Before authoring anything, inventory what the project already has:
[the `.gitlab/` artifacts this skill creates or replaces, and the existing
labels, milestones, or CI jobs it touches (via glab)], `AGENTS.md` /
`CLAUDE.md` for recorded conventions, and where project skills live — use
`.claude/skills/` if it exists, else `.agents/skills/` if it exists, else
plan to create `.agents/skills/`. Never invent structure parallel to what
the project already defines: build on what exists, or get the user's
explicit approval to replace it.
Done when: the inventory is written down and each deliverable below is
marked "new", "extends existing", or "replaces (approved)".
```

### Choose the deliverable

Fixed text.

```markdown
## Choose the deliverable

The default deliverable for workflow guidance is a **project-level agent
skill** in the skills directory found during assessment. When the project's
harness does not support skills, or the user prefers documentation, deliver
an `AGENTS.md` section (create the file if missing) or a standalone doc
instead. Ask the user once, before generating, and record the choice. All
other artifacts (templates, configs, CI jobs, validators) ship regardless
of this choice.
```

### Deliver

Fixed text; the closing section of every conventions skill.

```markdown
## Deliver

Everything this skill wrote is local files — nothing is published yet. Hand
the changes to the project's normal git flow (branch, commit, review); that
flow, not this skill, publishes them and carries its own review gates.
Done when: the user has the list of every file created or changed, one line
each on what it does, and any follow-up steps (label sync to run, CI job to
watch on the next MR, settings to enable).
```

### Condensed pre-publish gate

Embedded in every generated project skill that publishes content
(issues, MRs, releases, comments). The five numbered checks are fixed;
three slots are tailorable per template — the opening sentence(s) before
"review the exact final text" (the MR template adds the commit-log/diff
exposure, the release template the no-drafts-on-GitLab framing), a
parenthetical after it naming the artifacts under review, and, in the MR
template only, a "— or the branch, when the finding is in the diff —"
clause in the closing "fix the draft" sentence (its findings can live in
commits, not just the description). Everything else in the closing
paragraph is fixed. The AGENTS.md fallback sections carry the same
checks as prose, not verbatim. The full-procedure gate stays in the
`gitlab` catalog's operational skills; this condensed form exists
because generated skills must be self-contained.

```markdown
## Pre-publish gate (mandatory)

Everything you send becomes visible the moment the call succeeds — to the
whole internet on public projects, and to every member just as instantly on
private or internal ones. Before any call that creates or edits such
content, review the exact final text:

1. Prefer a clean-context subagent review when available; otherwise do the
   same deep review yourself against the final draft, not memory.
2. No secrets or credentials: tokens, keys, passwords, connection strings,
   internal URLs, cookies, or signing material.
3. No personal data beyond what the task needs: names, emails, phone
   numbers, addresses, account identifiers, screenshots.
4. No internal-only context: codenames, private hostnames, ticket links,
   unreleased plans, or private branch names.
5. No unintended quick actions: a body line starting with `/` can execute
   as one (for example `/close`).
6. No accidental unrelated content, and professional concise wording;
   English unless the project's conventions say otherwise.

If any check fails, fix the draft and re-check. Publish only after the full
text passes. Only the user may skip this gate, explicitly; note the skip in
your summary.
```

## Disambiguation

Set up glab/MCP for an agent → `gitlab-tooling-setup` · description
templates, scoped-label taxonomy, issue automation →
`gitlab-issue-conventions` · MR template, CONTRIBUTING MR rules, checklist
CI → `gitlab-mr-conventions` · commit-message rules, the committed
validator, the `Changelog:` trailer definition, commit CI →
`gitlab-commit-conventions` · versioning and tag policy,
`changelog_config.yml` (consumes the trailer), milestone-per-release
policy, tag CI → `gitlab-release-conventions` · **using** the
conventions day to day (filing issues, opening MRs, committing, cutting
releases) → the `gitlab` catalog's operational skills or the generated
project skill.

Boundary rule: this catalog authors *policy and structure* (what labels
exist, what the template says); the `gitlab` catalog *operates within*
that structure (applies labels, files issues against templates).
Ordering: when several conventions skills run,
`gitlab-commit-conventions` goes before `gitlab-release-conventions`
(the changelog config consumes the trailer habit it establishes), and
`gitlab-issue-conventions` before anything keyed to its labels.

## Tool inventory

Maintenance index: every glab command and REST endpoint the catalog's
skills and scripts reference. MCP interactions are listed by capability,
not tool name (see Requirements). Whenever a skill adds, removes, or
renames a command reference, update this inventory in the same commit.

| Command / endpoint / capability | Meaning | Used in |
|---|---|---|
| `glab auth status` / `glab auth login` (`--hostname`) | Check / establish authentication per host | gitlab-tooling-setup, conventions assess steps |
| `glab api user` | Auth smoke test | gitlab-tooling-setup |
| MCP: connection/version check capability | Verify the Duo MCP server answers | gitlab-tooling-setup |
| `glab label list` | Inventory existing labels | gitlab-issue-conventions |
| `GET/POST/PUT/DELETE /projects/:id/labels[/:label_id]`, `GET /groups/:id/labels` | Label taxonomy sync (group-inheritance aware) | gitlab-issue-conventions (scripts/sync_labels.py) |
| `GET /projects/:fullpath` | Merge settings (merge_method, squash_option) | gitlab-mr-conventions, gitlab-commit-conventions (assess) |
| `glab release list` / `glab release view` | Inventory existing releases and notes style | gitlab-release-conventions (assess) |
| `glab milestone list` | Inventory milestone usage | gitlab-release-conventions (assess) |
| `glab changelog generate` / `GET /projects/:fullpath/repository/changelog` | Test changelog generation as data | gitlab-release-conventions (references) |
| `PUT /projects/:fullpath/push_rule` | Commit-message push rule (Premium) | gitlab-commit-conventions (references) |
| `git tag --sort=-v:refname` | Inventory the existing tag scheme | gitlab-release-conventions (assess) |
| `git log` (via scripts) | History analysis and range validation | gitlab-commit-conventions (scripts/analyze_history.py, assets/check_commits.py) |
| `glab ci lint` | Validate shipped CI snippets | gitlab-mr-conventions |

## References

- glab manual: <https://docs.gitlab.com/cli/>
- glab source and releases: <https://gitlab.com/gitlab-org/cli>
- GitLab Duo MCP server: <https://docs.gitlab.com/user/gitlab_duo/model_context_protocol/mcp_server/>
- Description templates: <https://docs.gitlab.com/user/project/description_templates/>
- Labels: <https://docs.gitlab.com/user/project/labels/>
- Quick actions: <https://docs.gitlab.com/user/project/quick_actions/>
- CI/CD YAML: <https://docs.gitlab.com/ci/yaml/> · Predefined CI variables: <https://docs.gitlab.com/ci/variables/predefined_variables/>
- Push rules (Premium): <https://docs.gitlab.com/user/project/repository/push_rules/>
- Personal access tokens: <https://docs.gitlab.com/user/profile/personal_access_tokens/>
