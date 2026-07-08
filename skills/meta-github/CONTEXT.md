# meta-github — Catalog Context

Rules, notes, and references that apply only to skills in this catalog.
(Repo-wide standards live in `.agents/knowledge/skill-quality.md`.)

## Scope

meta-github holds **harness-authoring** skills: they set up the tooling a
coding agent needs for GitHub (`github-tooling-setup`) and author a
repository's conventions (the `*-conventions` skills). Their value lands in
what they leave behind — configured tooling, committed templates, workflows,
validators, and a generated project-level skill — not in the skill staying
installed. Day-to-day GitHub operations belong to the `github` catalog.

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
- **Local-files doctrine (conventions skills).** Conventions skills write
  local files only; nothing they do publishes directly. The project's normal
  git flow publishes the outputs, and that flow carries its own review
  gates — so conventions skills embed no full pre-publish gate. Any
  **generated** project skill that publishes content embeds the condensed
  gate below. `github-tooling-setup` is the exception to the conventions
  shape: it configures the agent's environment (MCP server, gh auth) and
  follows its own assess → install → verify structure.
- **Generated project skills are products.** They must meet the same bar as
  a published skill: the ~30B floor, one recommended path per operation,
  `Done when:` lines, frontmatter `name` equal to the directory name, the
  condensed pre-publish gate when they publish, and **zero leftover
  `{{...}}` placeholders**. Template placeholders use `{{UPPER_SNAKE}}`; the
  Done-when of every generate step is placeholder-free output.
- **First-party actions only.** Shipped workflow assets use only actions
  from the `actions/*` and `github/*` orgs. Third-party actions appear only
  behind an explicit user opt-in, marked as such. Shipped CI validators are
  dependency-free python3 scripts committed into the target repository.
- **MCP tools are described by capability, never by name.** MCP tool names
  churn across server versions, and MCP servers self-describe each tool's
  purpose — write "the MCP tool that reads an issue", not a concrete tool
  name, in skill bodies, tables, and references. Exact names are allowed
  only for CLI commands (gh), REST/GraphQL endpoints, and bundled scripts.
- Cross-skill overlap is limited to the canonical blocks below, duplicated
  verbatim; deep content lives only in the owning skill. Sibling skills
  (including operational counterparts in the `github` catalog) are named
  with the install-pointer pattern, never path-linked (self-containment).
- Exact gh command and flag names, workflow trigger/action schemas, and
  GitHub file conventions (template paths, `release.yml`) must be
  re-verified before publishing a skill revision, against
  <https://cli.github.com/manual/> and <https://docs.github.com/>.

## Canonical blocks

The following texts are canonical. Conventions skills copy them verbatim;
when editing one, update every copy in the same commit
(`grep -rl "Assess the project first" skills/meta-github/` finds them).

### Assess the project first

Only the bracketed artifact list is tailorable per skill.

```markdown
## Assess the project first

Before authoring anything, inventory what the repository already has:
[the `.github/` artifacts this skill creates or replaces, and the existing
labels, milestones, or workflows it touches (via gh)], `AGENTS.md` /
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
other artifacts (templates, configs, workflows, validators) ship regardless
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
each on what it does, and any follow-up steps (secrets to set, first sync
run, branch protection to enable).
```

### Condensed pre-publish gate

Embedded in every generated project skill that publishes content
(issues, PRs, releases, comments). The four numbered checks are fixed;
three slots are tailorable per template — the opening sentence(s) before
"review the exact final text" (the PR template adds the commit-log/diff
exposure, the release template the draft-first framing), a parenthetical
after it naming the artifacts under review, and, in the PR template
only, a "— or the branch, when the finding is in the diff —" clause in
the closing "fix the draft" sentence (its findings can live in commits,
not just the description). Everything else in the closing paragraph is
fixed. The AGENTS.md fallback sections carry the same checks as
prose, not verbatim. The full-procedure gate stays in the `github`
catalog's operational skills; this condensed form exists because
generated skills must be self-contained.

```markdown
## Pre-publish gate (mandatory)

Everything you send becomes public the moment the call succeeds. Before any
call that creates or edits public content, review the exact final text:

1. Prefer a clean-context subagent review when available; otherwise do the
   same deep review yourself against the final draft, not memory.
2. No secrets or credentials: tokens, keys, passwords, connection strings,
   internal URLs, cookies, or signing material.
3. No personal data beyond what the task needs: names, emails, phone
   numbers, addresses, account identifiers, screenshots.
4. No internal-only context: codenames, private hostnames, ticket links,
   unreleased plans, or private branch names.
5. No accidental unrelated content, and professional concise wording;
   English unless the project's conventions say otherwise.

If any check fails, fix the draft and re-check. Publish only after the full
text passes. Only the user may skip this gate, explicitly; note the skip in
your summary.
```

## Disambiguation

Set up MCP/gh for an agent → `github-tooling-setup` · issue forms, label
taxonomy, issue automation → `github-issue-conventions` · PR template,
CONTRIBUTING PR rules, PR automation → `github-pr-conventions` ·
commit-message rules, the committed validator, commit CI →
`github-commit-conventions` · versioning and tag policy, release.yml,
tag CI → `github-release-conventions` · **using** the conventions day to
day (filing issues, opening PRs, committing, cutting releases) → the
`github` catalog's operational skills or the generated project skill.

Boundary rule: this catalog authors *policy and structure* (what labels
exist, what the template says); the `github` catalog *operates within*
that structure (applies labels, files issues against templates).
Ordering: when several conventions skills run, `github-issue-conventions`
goes before `github-release-conventions` (release.yml keys on the label
taxonomy), and `github-commit-conventions` before it when the bump rule
is type-mapped.

## Tool inventory

Maintenance index: every gh command the catalog's skills and scripts
reference. MCP interactions are listed by capability, not tool name (see
Requirements). Whenever a skill adds, removes, or renames a command
reference, update this inventory in the same commit.

| Command / capability | Meaning | Used in |
|---|---|---|
| `gh auth status` / `gh auth login` | Check / establish authentication | github-tooling-setup, conventions assess steps |
| `gh api user -q .login` | Auth smoke test | github-tooling-setup |
| MCP: connection/identity check capability | Verify the MCP server answers with the current login | github-tooling-setup |
| `gh label list` | Inventory existing labels | github-issue-conventions |
| `gh label create/edit/delete` | Apply the label taxonomy | github-issue-conventions (scripts/sync_labels.py) |
| `gh api repos/{o}/{r}/labels` | Label sync fallback fields | github-issue-conventions (scripts/sync_labels.py) |
| `gh repo view --json` | Read default branch and merge settings | github-pr-conventions, github-commit-conventions, github-release-conventions (assess) |
| `gh workflow list` | Inventory existing automation | conventions assess steps |
| `gh release list` / `gh release view` | Inventory existing releases and notes style | github-release-conventions (assess) |
| `gh api repos/{o}/{r}/releases/generate-notes` | Preview generated notes while editing release.yml | github-release-conventions (references) |
| `git tag --sort=-v:refname` | Inventory the existing tag scheme | github-release-conventions (assess) |
| `git log` (via scripts) | History analysis and range validation | github-commit-conventions (scripts/analyze_history.py, assets/check_commits.py) |

## References

- GitHub MCP server: <https://github.com/github/github-mcp-server>
- Remote server + toolsets: <https://github.com/github/github-mcp-server/blob/main/docs/remote-server.md>
- Server configuration (local): <https://github.com/github/github-mcp-server/blob/main/docs/server-configuration.md>
- Per-host install guides index: <https://raw.githubusercontent.com/github/github-mcp-server/refs/heads/main/docs/installation-guides/README.md>
- gh manual: <https://cli.github.com/manual/>
- Issue forms schema: <https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/syntax-for-issue-forms>
- PR templates: <https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/creating-a-pull-request-template-for-your-repository>
- actions/labeler: <https://github.com/actions/labeler>
- Workflow syntax: <https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions>
