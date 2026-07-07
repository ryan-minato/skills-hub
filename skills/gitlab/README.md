# gitlab

[中文](README.zh.md)

GitLab **collaboration workflow** skills — operating issues, merge requests,
pipelines, planning structures, and wikis through the authenticated `glab`
CLI first, with the GitLab Duo MCP server as an annotated alternative, plus
conventions authoring for a project. Works on gitlab.com and self-managed
instances alike, with tier and version gates marked. Designed so small local
models can execute them: one recommended path per operation, decision
tables, and a mandatory pre-publish security review embedded in every skill
that publishes content.

```bash
npx skills add ryan-minato/skills --skill <skill-name>
```

## Skills

| Skill | Description |
|---|---|
| [gitlab-tooling-setup](gitlab-tooling-setup/) | Install and authenticate the glab CLI per OS against gitlab.com or any self-managed host, optionally configure the GitLab Duo MCP server (Premium/Ultimate, 18.6+), with a probe script reporting what is available and authenticated. |
| [gitlab-issues](gitlab-issues/) | Issue operations through glab-first decision tables with MCP annotations — create, comment, close/reopen, read, labels, assignees — behind a mandatory pre-publish review gate. |
| [gitlab-merge-requests](gitlab-merge-requests/) | Merge-request operations through glab-first decision tables — create, comment, approve, merge with auto-merge/squash semantics, pipeline status, failed-job log tails, discussion threads — behind a mandatory pre-publish review gate. |
| [gitlab-repo-research](gitlab-repo-research/) | Read-only investigation of any GitLab project — issues, MRs, pipelines and failed-job log digests, search — via glab, MCP, or a bundled REST script that works unauthenticated on public projects, with tooling that keeps huge logs out of context. |
| [gitlab-planning](gitlab-planning/) | Lifecycle of GitLab planning structures with tier floors marked — milestones (Free), iterations (Premium, cadence-managed), issue boards and lists, epics (Premium/Ultimate via the stable REST path, work items as the experimental successor). |
| [gitlab-wiki](gitlab-wiki/) | Project and group wiki page operations via the wikis REST API — read, create, update, rename, delete, attachments — with the wiki-as-git-repository path for bulk restructures, behind a mandatory pre-publish review gate. |
| [gitlab-issue-conventions](gitlab-issue-conventions/) | Author a project's issue conventions: description templates with embedded quick actions, a scoped-label taxonomy applied by an idempotent sync script, scheduled-sweep automation recipes, and a generated project-level issue skill. |
| [gitlab-mr-conventions](gitlab-mr-conventions/) | Author a project's merge-request conventions: a Default.md MR template, contributing rules, a tokenless CI checklist-validation job for merge request pipelines, and a generated project-level MR skill. |
