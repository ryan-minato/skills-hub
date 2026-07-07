# github

[English](README.md)

GitHub **协作工作流** skill——优先通过 GitHub MCP server 操作 issue、pull
request、Discussions 与 Actions，并提供精确的 `gh` CLI 回退命令。面向小型
本地模型设计：每个操作只有一条推荐路径、决策表驱动，且所有发布内容的
skill 都内嵌强制的发布前安全审查。工具链配置与仓库规范创作类 skill 位于
`meta-github` catalog。

```bash
npx skills add ryan-minato/skills --skill <skill-name>
```

## Skill 列表

| Skill | 说明 |
|---|---|
| [github-issues](github-issues/) | 通过 MCP 优先 / gh 回退的决策表执行 issue 操作——创建、评论、关闭/重开、读取、标签、指派、milestone——创建前先发现仓库既有的 issue 模板、标签与 milestone，全部经过强制的发布前审查关卡。 |
| [github-pull-requests](github-pull-requests/) | 通过 MCP 优先 / gh 回退的决策表执行 pull request 操作——创建、评论、合并、CI 检查结果、失败任务日志、Copilot 审查线程——全部经过强制的发布前审查关卡。 |
| [github-repo-research](github-repo-research/) | 对任意仓库的只读调查——issue、PR、Actions 运行与失败日志、Discussions——可经 MCP、gh 或内置 REST 脚本（公开仓库无需认证），并附带避免大日志涌入上下文的摘要工具。 |
