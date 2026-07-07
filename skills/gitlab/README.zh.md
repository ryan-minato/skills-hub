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
| [gitlab-repo-research](gitlab-repo-research/) | 对任意 GitLab 项目的只读调查——issue、MR、流水线与失败任务日志摘要、搜索——可经 glab、MCP 或内置 REST 脚本（公开项目无需认证），并附带避免大日志涌入上下文的工具。 |
| [gitlab-planning](gitlab-planning/) | GitLab 规划结构的生命周期管理并标注层级门槛——milestone（Free）、iteration（Premium，由 cadence 管理）、issue board 与列表、epic（Premium/Ultimate，走稳定 REST 路径，work items 为实验性后继）。 |
| [gitlab-wiki](gitlab-wiki/) | 通过 wikis REST API 操作项目与群组 wiki 页面——读取、创建、更新、重命名、删除、附件——批量重构走 wiki 即 git 仓库路径，全部经过强制的发布前审查关卡。 |
| [gitlab-issue-conventions](gitlab-issue-conventions/) | 为项目创作 issue 规范：内嵌 quick actions 的描述模板、由幂等同步脚本应用的 scoped 标签体系、定时清扫自动化配方，以及生成的项目级 issue skill。 |
| [gitlab-mr-conventions](gitlab-mr-conventions/) | 为项目创作 merge request 规范：Default.md MR 模板、贡献规则、在 merge request 流水线中运行的免 token CI 清单校验任务，以及生成的项目级 MR skill。 |
