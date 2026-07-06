# github

[中文](README.zh.md)

GitHub **collaboration workflow** skills — operating issues, pull requests,
Discussions, and Actions through the GitHub MCP server first, with exact
`gh` CLI fallbacks, plus conventions authoring for a repository. Designed so
small local models can execute them: one recommended path per operation,
decision tables, and a mandatory pre-publish security review embedded in
every skill that publishes content.

```bash
npx skills add ryan-minato/skills --skill <skill-name>
```

## Skills

| Skill | Description |
|---|---|
| [github-tooling-setup](github-tooling-setup/) | Install and configure the GitHub MCP server (remote HTTP or local stdio) for any agent framework via the official per-host install guides, plus gh CLI install and authentication per OS, with a probe script reporting what is available and authenticated. |
| [github-issues](github-issues/) | Issue operations through MCP-first/gh-fallback decision tables — create, comment, close/reopen, read, labels, assignees — behind a mandatory pre-publish review gate. |
| [github-pull-requests](github-pull-requests/) | Pull-request operations through MCP-first/gh-fallback decision tables — create, comment, merge, CI check results, failed-job logs, Copilot review threads — behind a mandatory pre-publish review gate. |
| [github-repo-research](github-repo-research/) | Read-only investigation of any repository — issues, PRs, Actions runs and failed-job logs, Discussions — via MCP, gh, or a bundled REST script that works unauthenticated on public repos, with digest tooling that keeps huge logs out of context. |
| [github-issue-conventions](github-issue-conventions/) | Author a repository's issue conventions: issue forms, a label taxonomy applied by an idempotent sync script, first-party issue automation, and a generated project-level issue skill. |
| [github-pr-conventions](github-pr-conventions/) | Author a repository's pull-request conventions: PR template, contributing rules, auto-labeling and checklist-validation workflows, and a generated project-level PR skill. |
