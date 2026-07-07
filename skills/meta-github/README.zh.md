# meta-github

[English](README.md)

GitHub **harness 创作类** skill。它们为项目及其编码 agent 搭建围绕
GitHub 的基础设施，而不是执行日常的 GitHub 操作：agent 工具链（GitHub
MCP server、gh CLI）与仓库规范（issue 表单、标签体系、PR 规则、自动化、
生成的项目级 skill）。meta skill 的价值在于它留下的产物——配置好的工具
链和提交进仓库的文件——而不在于自身持续安装。日常的 issue、pull
request、规划与发布操作属于 `github` catalog。

```bash
npx skills add ryan-minato/skills --skill <skill-name>
```

## Skill 列表

| Skill | 说明 |
|---|---|
| [github-tooling-setup](github-tooling-setup/) | 通过各框架官方安装指南安装并配置 GitHub MCP server（远程 HTTP 或本地 stdio），以及各操作系统下 gh CLI 的安装与认证（涵盖操作类技能所需的 token scope：repo、project），并附带报告可用性与认证状态的探测脚本。 |
| [github-issue-conventions](github-issue-conventions/) | 为仓库创作 issue 规范：issue 表单、由幂等同步脚本应用的标签体系、第一方 issue 自动化，以及生成的项目级 issue skill。 |
| [github-pr-conventions](github-pr-conventions/) | 为仓库创作 pull request 规范：PR 模板、贡献规则、自动打标与清单校验工作流，以及生成的项目级 PR skill。 |
