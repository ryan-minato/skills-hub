# github

[中文](README.zh.md)

GitHub **collaboration workflow** skills — operating issues, pull requests,
Discussions, and Actions through the GitHub MCP server first, with exact
`gh` CLI fallbacks. Designed so small local models can execute them: one
recommended path per operation, decision tables, and a mandatory
pre-publish security review embedded in every skill that publishes content.
Tooling setup and repository conventions authoring live in the
`meta-github` catalog.

```bash
npx skills add ryan-minato/skills --skill <skill-name>
```

## Skills

| Skill | Description |
|---|---|
| [github-issues](github-issues/) | Issue operations through MCP-first/gh-fallback decision tables — create, comment, close/reopen, read, labels, assignees, milestone — discovering the repository's issue templates, labels, and milestones before any create, behind a mandatory pre-publish review gate. |
| [github-pull-requests](github-pull-requests/) | Pull-request operations through MCP-first/gh-fallback decision tables — create, comment, merge, labels/milestone, CI check results, failed-job logs, Copilot review threads — discovering the repository's PR template and contributing rules before any create, behind a mandatory pre-publish review gate. |
| [github-repo-research](github-repo-research/) | Read-only investigation of any repository — issues, PRs, Actions runs and failed-job logs, Discussions, releases, tags — via MCP, gh, or a bundled REST script that works unauthenticated on public repos, with digest tooling that keeps huge logs out of context. |
