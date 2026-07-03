# core

[English](README.md)

推荐**全局（用户级）安装**的 skill——无论在什么项目中都有用。

```bash
npx skills add ryan-minato/skills --skill <skill-name> -g
```

## Skill 列表

| Skill | 说明 |
|---|---|
| [great-skill-writer](great-skill-writer/) | 编写并改进行为可预测的 Agent Skill：符合规范的 frontmatter、触发准确的 description、可检验的完成标准、渐进式披露，并内置校验脚本。 |
| [meta-harness](meta-harness/) | 设计、审计并改进 agent harness：调查项目与团队事实，选择成熟度等级（L0–L4），校准九个 harness 层的厚度，并让每条规则都能被未来的 agent 从 AGENTS.md 发现。 |
| [sensitivity-check](sensitivity-check/) | 检测文本或文件中的 PII 与泄露的机密信息，并生成结构化报告。首选引擎（经 uv 运行的 Presidio、detect-secrets）配合纯标准库回退脚本，覆盖通用及美/英/中/日实体。 |
