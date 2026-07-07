# meta-gitlab

[中文](README.zh.md)

GitLab **harness-authoring** skills. They set up what a project and its
coding agents need *around* GitLab instead of operating GitLab day to day:
agent tooling (the glab CLI, optionally the GitLab Duo MCP server) and a
project's conventions (description templates, scoped-label taxonomy, MR
rules, CI validation, generated project-level skills). A meta skill's value
lands in what it leaves behind — configured tooling and committed files —
not in staying installed. Works on gitlab.com and self-managed instances
alike, defaulting to Free-tier mechanisms. Day-to-day issue, merge-request,
planning, and release operations belong to the `gitlab` catalog.

```bash
npx skills add ryan-minato/skills --skill <skill-name>
```

## Skills

| Skill | Description |
|---|---|
| [gitlab-tooling-setup](gitlab-tooling-setup/) | Install and authenticate the glab CLI per OS against gitlab.com or any self-managed host, optionally configure the GitLab Duo MCP server (Premium/Ultimate, 18.6+), with a probe script reporting what is available and authenticated. |
| [gitlab-commit-conventions](gitlab-commit-conventions/) | Author a project's commit conventions: history-informed Conventional Commits rules including the Changelog trailer that powers changelog generation, a dependency-free Python validator committed into the repo, a tokenless MR-pipeline CI job, and a generated project-level commit skill — with an AGENTS.md section as the fallback deliverable. |
| [gitlab-issue-conventions](gitlab-issue-conventions/) | Author a project's issue conventions: description templates with embedded quick actions, a scoped-label taxonomy applied by an idempotent sync script, scheduled-sweep automation recipes, and a generated project-level issue skill — with an AGENTS.md section as the fallback deliverable. |
| [gitlab-mr-conventions](gitlab-mr-conventions/) | Author a project's merge-request conventions: a Default.md MR template, contributing rules, a tokenless CI checklist-validation job for merge request pipelines, and a generated project-level MR skill — with an AGENTS.md section as the fallback deliverable. |
