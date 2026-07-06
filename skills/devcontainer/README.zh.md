# devcontainer

[English](README.md)

Dev Container **创作**类 skill——为 [Dev Container 生态](https://containers.dev)
开发 Feature、创建 Template、预构建镜像。如需*使用* dev container
（为项目创建开发环境），请使用 `core` catalog 中的 `devcontainer-setup` skill。

```bash
npx skills add ryan-minato/skills --skill <skill-name>
```

## Skill 列表

| Skill | 说明 |
|---|---|
| [devcontainer-feature-authoring](devcontainer-feature-authoring/) | 开发、测试并发布 Dev Container Feature：manifest schema 与 install.sh 契约、质量标准（幂等性、基础镜像容忍度、非 root 正确性、确定性安装）、feature 独立性规则，以及带共享 action CI 的现代仓库脚手架。 |
