# core

[English](README.md)

推荐**全局（用户级）安装**的 skill——无论在什么项目中都有用。

```bash
npx skills add ryan-minato/skills --skill <skill-name> -g
```

## Skill 列表

| Skill | 说明 |
|---|---|
| [conventional-commits](conventional-commits/) | 起草符合 Conventional Commits 1.0.0 规范的 git 提交信息：规则优先级（文档 > commitlint 配置 > 历史 > 默认值）、首个匹配即停的 type 决策列表、scope 与破坏性变更策略，以及交付前校验清单。 |
| [devcontainer-setup](devcontainer-setup/) | 在可信来源策略下创建与修改 dev container 配置（mcr.microsoft.com/devcontainers、NVIDIA NGC、ghcr.io/devcontainers、ghcr.io/stacit-ai），内置来源枚举脚本、非预构建镜像的基线 feature 规则，以及 NVIDIA/AMD GPU 指引。 |
| [git-commit](git-commit/) | 以有序门禁执行完整的 git 提交工作流：按明确优先级发现项目约定、检查变更原子性、扫描暂存 diff 中的机密与 PII、核对提交者身份、运行 hooks 与本地检查，并在提交前用内置脚本校验提交信息。 |
| [great-skill-writer](great-skill-writer/) | 编写并改进行为可预测的 Agent Skill：符合规范的 frontmatter、触发准确的 description、可检验的完成标准、渐进式披露，并内置校验脚本。 |
| [meta-harness](meta-harness/) | 设计、审计并改进 agent harness：调查项目与团队事实，选择成熟度等级（L0–L4），校准九个 harness 层的厚度，并让每条规则都能被未来的 agent 从 AGENTS.md 发现。 |
| [programming-guidelines](programming-guidelines/) | 应用通用编程工作标准：编码前先思考，优先选择简单方案，保持改动精确，并用清晰的成功标准验证结果。 |
| [sensitivity-check](sensitivity-check/) | 检测文本或文件中的 PII 与泄露的机密信息，并生成结构化报告。首选引擎（经 uv 运行的 Presidio、detect-secrets）配合纯标准库回退脚本，覆盖通用及美/英/中/日实体。 |
