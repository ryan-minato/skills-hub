# meta-gitlab

[English](README.md)

GitLab **harness 创作类** skill。它们为项目及其编码 agent 搭建围绕
GitLab 的基础设施，而不是执行日常的 GitLab 操作：agent 工具链（glab
CLI，可选 GitLab Duo MCP server）与项目规范（描述模板、scoped 标签体系、
MR 规则、提交信息规则、版本与发布政策、CI 校验、生成的项目级 skill）。meta skill 的价值在于它留下的
产物——配置好的工具链和提交进仓库的文件——而不在于自身持续安装。同等
支持 gitlab.com 与自建实例，默认使用 Free 层机制。日常的 issue、merge
request、规划与发布操作属于 `gitlab` catalog。

```bash
npx skills add ryan-minato/skills --skill <skill-name>
```

## Skill 列表

| Skill | 说明 |
|---|---|
| [gitlab-release-conventions](gitlab-release-conventions/) | 为项目创作发布规范：映射到提交类型的 SemVer 政策、免 token 的 tag 检查 CI 任务、以 Changelog trailer 为键的 changelog_config.yml、一版本一里程碑政策，以及采用创建前审查流程的生成项目级 release skill——并以 AGENTS.md 章节作为 fallback 交付物。 |
| [gitlab-tooling-setup](gitlab-tooling-setup/) | 按操作系统安装 glab CLI 并对 gitlab.com 或任意自建实例完成认证，可选配置 GitLab Duo MCP server（Premium/Ultimate，18.6+），附带报告可用性与认证状态的探测脚本。 |
| [gitlab-commit-conventions](gitlab-commit-conventions/) | 为项目创作提交规范：基于历史分析的约定式提交规则（含驱动变更日志生成的 Changelog trailer）、提交进仓库的零依赖 Python 校验器、免 token 的 MR 流水线 CI 任务，以及生成的项目级 commit skill——并以 AGENTS.md 章节作为 fallback 交付物。 |
| [gitlab-issue-conventions](gitlab-issue-conventions/) | 为项目创作 issue 规范：内嵌 quick actions 的描述模板、由幂等同步脚本应用的 scoped 标签体系、定时清扫自动化配方，以及生成的项目级 issue skill——并以 AGENTS.md 章节作为 fallback 交付物。 |
| [gitlab-mr-conventions](gitlab-mr-conventions/) | 为项目创作 merge request 规范：Default.md MR 模板、贡献规则、在 merge request 流水线中运行的免 token CI 清单校验任务，以及生成的项目级 MR skill——并以 AGENTS.md 章节作为 fallback 交付物。 |
