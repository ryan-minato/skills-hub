# github

[English](README.md)

GitHub **协作工作流** skill——优先通过 GitHub MCP server 操作 issue、pull
request、Discussions 与 Actions，并提供精确的 `gh` CLI 回退命令，另含仓库
规范创作类 skill。面向小型本地模型设计：每个操作只有一条推荐路径、决策表
驱动，且所有发布内容的 skill 都内嵌强制的发布前安全审查。

```bash
npx skills add ryan-minato/skills --skill <skill-name>
```

## Skill 列表

| Skill | 说明 |
|---|---|
| [github-tooling-setup](github-tooling-setup/) | 通过各框架官方安装指南安装并配置 GitHub MCP server（远程 HTTP 或本地 stdio），以及各操作系统下 gh CLI 的安装与认证，并附带报告可用性与认证状态的探测脚本。 |
| [github-issues](github-issues/) | 通过 MCP 优先 / gh 回退的决策表执行 issue 操作——创建、评论、关闭/重开、读取、标签、指派——全部经过强制的发布前审查关卡。 |
| [github-pull-requests](github-pull-requests/) | 通过 MCP 优先 / gh 回退的决策表执行 pull request 操作——创建、评论、合并、CI 检查结果、失败任务日志、Copilot 审查线程——全部经过强制的发布前审查关卡。 |
| [github-repo-research](github-repo-research/) | 对任意仓库的只读调查——issue、PR、Actions 运行与失败日志、Discussions——可经 MCP、gh 或内置 REST 脚本（公开仓库无需认证），并附带避免大日志涌入上下文的摘要工具。 |
| [github-issue-conventions](github-issue-conventions/) | 为仓库创作 issue 规范：issue 表单、由幂等同步脚本应用的标签体系、第一方 issue 自动化，以及生成的项目级 issue skill。 |
| [github-pr-conventions](github-pr-conventions/) | 为仓库创作 pull request 规范：PR 模板、贡献规则、自动打标与清单校验工作流，以及生成的项目级 PR skill。 |
