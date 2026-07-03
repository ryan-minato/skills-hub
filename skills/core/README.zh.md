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
| [sensitivity-check](sensitivity-check/) | 检测文本或文件中的 PII 与泄露的机密信息，并生成结构化报告。首选引擎（经 uv 运行的 Presidio、detect-secrets）配合纯标准库回退脚本，覆盖通用及美/英/中/日实体。 |
