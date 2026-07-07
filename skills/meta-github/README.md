# meta-github

[中文](README.zh.md)

GitHub **harness-authoring** skills. They set up what a project and its
coding agents need *around* GitHub instead of operating GitHub day to day:
agent tooling (the GitHub MCP server, the gh CLI) and a repository's
conventions (issue forms, label taxonomy, PR rules, automation, generated
project-level skills). A meta skill's value lands in what it leaves behind —
configured tooling and committed files — not in staying installed. Day-to-day
issue, pull-request, planning, and release operations belong to the `github`
catalog.

```bash
npx skills add ryan-minato/skills --skill <skill-name>
```

## Skills

| Skill | Description |
|---|---|
| [github-tooling-setup](github-tooling-setup/) | Install and configure the GitHub MCP server (remote HTTP or local stdio) for any agent framework via the official per-host install guides, plus gh CLI install and authentication per OS with the token scopes the operational skills need (repo, project), with a probe script reporting what is available and authenticated. |
| [github-issue-conventions](github-issue-conventions/) | Author a repository's issue conventions: issue forms, a label taxonomy applied by an idempotent sync script, first-party issue automation, and a generated project-level issue skill. |
| [github-pr-conventions](github-pr-conventions/) | Author a repository's pull-request conventions: PR template, contributing rules, auto-labeling and checklist-validation workflows, and a generated project-level PR skill. |
