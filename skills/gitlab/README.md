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
