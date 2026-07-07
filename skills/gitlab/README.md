# gitlab

[中文](README.zh.md)

GitLab **collaboration workflow** skills — operating issues, merge requests,
pipelines, planning structures, and wikis through the authenticated `glab`
CLI first, with the GitLab Duo MCP server as an annotated alternative.
Works on gitlab.com and self-managed instances alike, with tier and version
gates marked. Designed so small local models can execute them: one
recommended path per operation, decision tables, and a mandatory
pre-publish security review embedded in every skill that publishes content.
Tooling setup and project conventions authoring live in the `meta-gitlab`
catalog.

```bash
npx skills add ryan-minato/skills --skill <skill-name>
```

## Skills

| Skill | Description |
|---|---|
| [gitlab-issues](gitlab-issues/) | Issue operations through glab-first decision tables with MCP annotations — create, comment, close/reopen, read, labels, assignees, milestone — discovering the project's description templates, labels, and milestones before any create, behind a mandatory pre-publish review gate. |
| [gitlab-merge-requests](gitlab-merge-requests/) | Merge-request operations through glab-first decision tables — create, comment, approve, merge with auto-merge/squash semantics, labels/milestone, pipeline status, failed-job log tails, discussion threads — discovering the project's MR template and contributing rules before any create, behind a mandatory pre-publish review gate. |
| [gitlab-repo-research](gitlab-repo-research/) | Read-only investigation of any GitLab project — issues, MRs, pipelines and failed-job log digests, releases, tags, search — via glab, MCP, or a bundled REST script that works unauthenticated on public projects, with tooling that keeps huge logs out of context. |
| [gitlab-planning](gitlab-planning/) | Lifecycle of GitLab planning structures with tier floors marked — milestones (Free), iterations (Premium, cadence-managed), issue boards and lists, epics (Premium/Ultimate via the stable REST path, work items as the experimental successor). |
| [gitlab-wiki](gitlab-wiki/) | Project and group wiki page operations via the wikis REST API — read, create, update, rename, delete, attachments — with the wiki-as-git-repository path for bulk restructures, behind a mandatory pre-publish review gate. |
