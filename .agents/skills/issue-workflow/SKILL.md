---
name: issue-workflow
description: Issue-driven development workflow for this repository — create the Linear issue before any proactive change, work on the issue's branch, comment at milestones, keep every commit atomic and hook-clean, open a draft PR, and mark it ready after final validation. Use when starting any proactive creation or modification of tracked files, when picking up an existing Linear issue, when creating a work branch, or when preparing a push or pull request in this repo.
metadata:
  internal: true
---

# Issue Workflow

Project-only workflow skill for this repository. Follow it for every change
to tracked files, from first intent to PR readiness. It layers the
issue/branch/PR flow on top of the commit gates defined by the `git-commit`
skill.

Requires: git remote `origin` reachable, Linear MCP server connected
(configured in `.mcp.json`).

## When this applies

- **Proactive changes** (work not driven by a pre-existing Linear issue):
  create the issue(s) below **before touching any file**.
- **Work started from an existing Linear issue**: skip issue creation, but
  follow every other step (branch, milestone comments, commits, handoff).
- Answering questions, read-only analysis, and scratchpad-only files need no
  issue.

## 1. Create the issue(s)

Resolve the team at runtime with `list_teams` (do not hardcode or assume
team ids), and target the project named in `AGENTS.md`'s task-management
convention.

- One coherent change → one standalone issue.
- A group of related changes → one **parent issue** plus one **sub-issue**
  per independently completable unit (`save_issue` with `parentId`).
- Read `references/issue-templates.md` when composing any issue description
  or milestone comment; it holds the required templates and the label
  mapping.
- Label every issue via that mapping (aligned with conventional-commit
  types). Write all issue content in English.
- Set the issue you are starting on to **In Progress**.

## 2. Branch

Work happens on the issue's branch, never directly on `main`:

1. Take the branch name from Linear: `get_issue` returns `gitBranchName`.
   Use it verbatim — do not invent branch names.
2. For a parent/sub-issue structure, use the **parent** issue's branch; all
   sub-issue work lands there (one PR per parent). Sub-issues never get
   their own branches. A standalone issue acts as its own parent.
3. Create the branch from up-to-date `origin/main`:

   ```bash
   git fetch origin
   git switch -c <gitBranchName> origin/main
   ```

## 3. Work and milestone comments

After completing a todo milestone — a sub-issue's scope, a meaningful
checkpoint, a commit, or a change of direction — post a comment
(`save_comment`) on the issue that scope belongs to, using the
milestone-comment template: what was done, what remains, any deviations.
Keep comments status-oriented; do not manually paste commit hashes or PR
links just for traceability, because Linear links conforming branches and
PRs automatically. Also post one before ending a session with work still in
flight, so the issue reflects reality when no agent is running.

## 4. Commits

Commits are **atomic**: one logical change per commit, and every commit must
independently satisfy the full quality bar — do not stage unrelated work
together, and do not leave the tree broken between commits.

- For **every** commit, run `just commit-gate`, then make a best-effort
  pass with the `sensitivity-check` skill against the staged commit content
  (`git diff --cached --no-ext-diff` and, when useful, the staged files).
  Check both secrets and PII. Use the preferred engines when available, fall
  back to lite engines or deep reading when they are not, and record any
  degradation. A confirmed finding blocks the commit until fixed or
  explicitly cleared by the user.
- Then run the complete `git-commit` skill gates (convention discovery,
  atomicity, secret/PII scan, hooks and local checks, message validation).
  The sensitivity check is mandatory before each commit, not once per
  session.
- Never bypass hooks: `--no-verify`, `SKIP=...`, or disabling hook managers
  is forbidden. A failing hook or check stops the flow until fixed.
- No `Co-Authored-By` or tool-attribution trailers in commit messages.
- Commit authorship must use a GitHub or GitLab anonymous email address
  unless the user explicitly approves using a private email for that
  commit/session.

## 5. Complete sub-issues

When a sub-issue's scope is implemented and committed: post a closing
milestone comment, then set the sub-issue to **Done**.

**Never manually close or cancel the parent issue** — even when every
sub-issue is Done. The parent's final state follows the PR's acceptance
(merge → Done, rejection → Canceled) and is handled outside the agent.

## 6. Push and open a draft PR

After a coherent first implementation pass exists and the branch is useful
to review remotely:

1. Run `just check` and fix everything it reports.
2. Push the branch: `git push -u origin <branch>`. Do not force-push a
   branch others may have fetched.
3. Create a **draft PR** with a conventional-commit-style title matching
   the parent issue and a body following `.github/PULL_REQUEST_TEMPLATE.md`.
   Include `Closes <parent-id>` so Linear resolves the parent when the PR
   merges. Link sub-issues as plain references (no closing keywords; they
   are already Done).
4. Keep working on the PR branch. Continue posting milestone comments on
   the owning Linear issue after each commit or meaningful checkpoint.

## 7. Mark the PR ready

When all sub-issues are Done and the branch is ready for human review:

1. Run `just check` and fix everything it reports.
2. Push the final branch state.
3. Mark the draft PR **Ready for review**.
4. Set the parent issue to **In Review** and post a final status comment.

## Gotchas

- `Closes <id>` in the PR body must name the **parent** issue only. Putting
  closing keywords on sub-issue ids fights step 5 and confuses the
  automation.
- Linear branch names embed the issue identifier; if the issue title changes
  after branching, keep the existing branch — do not rename it mid-work.
- If unrelated work is discovered mid-task, file it as a new issue instead
  of widening the current branch's scope.
