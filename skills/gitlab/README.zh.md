# gitlab

[English](README.md)

GitLab **协作工作流** skill——优先通过已认证的 `glab` CLI 操作 issue、merge
request、流水线、规划结构与 wiki，并以 GitLab Duo MCP server 作为带注释的
备选路径，另含项目规范创作类 skill。同等支持 gitlab.com 与自建实例，并
标注层级与版本门槛。面向小型本地模型设计：每个操作只有一条推荐路径、
决策表驱动，且所有发布内容的 skill 都内嵌强制的发布前安全审查。

```bash
npx skills add ryan-minato/skills --skill <skill-name>
```

## Skill 列表

| Skill | 说明 |
|---|---|
| [gitlab-tooling-setup](gitlab-tooling-setup/) | 按操作系统安装 glab CLI 并对 gitlab.com 或任意自建实例完成认证，可选配置 GitLab Duo MCP server（Premium/Ultimate，18.6+），附带报告可用性与认证状态的探测脚本。 |
| [gitlab-issues](gitlab-issues/) | 通过 glab 优先、附 MCP 注释的决策表执行 issue 操作——创建、评论、关闭/重开、读取、标签、指派——全部经过强制的发布前审查关卡。 |
| [gitlab-merge-requests](gitlab-merge-requests/) | 通过 glab 优先的决策表执行 merge request 操作——创建、评论、批准、含 auto-merge/squash 语义的合并、流水线状态、失败任务日志尾部、讨论线程——全部经过强制的发布前审查关卡。 |
