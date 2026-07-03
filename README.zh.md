# Skills

[English](README.md)

一个精心维护的 [Agent Skills](https://agentskills.io) 库——自包含的指令包，
用于教会编码 agent（Claude Code、Codex、Copilot 及其他兼容客户端）
高质量地完成特定任务。

## 目录（Catalogs）

| Catalog | 内容 | 安装范围 |
|---|---|---|
| [`core`](skills/core/) | 推荐在所有环境安装的 skill | 全局（用户级） |
| [`engineering`](skills/engineering/) | 通用编程方法论类 skill，不绑定特定语言或框架 | 按需安装到项目 |
| [`ops`](skills/ops/) | 不直接调用的通用工作流操作 | 按需安装到项目 |

每个 catalog 的 README 列出了其包含的 skill。

## 安装

使用 [skills CLI](https://github.com/vercel-labs/skills) 安装单个 skill：

```bash
# 交互式选择 skill（项目级安装）
npx skills add ryan-minato/skills

# 安装指定 skill
npx skills add ryan-minato/skills --skill <skill-name>

# 全局安装（core 类 skill 推荐）
npx skills add ryan-minato/skills --skill <skill-name> -g
```

建议将 `core` 类 skill 全局安装，使其在所有项目中可用；
其他 catalog 的 skill 按需安装到需要的项目中。

## 参与贡献

约定、质量标准和仓库机制均已为人类和 agent 编写成文档：
从 [AGENTS.md](AGENTS.md) 开始，然后阅读
[ARCHITECTURE.md](ARCHITECTURE.md)。克隆后运行一次 `just setup`，
提交前运行 `just check`。

## 许可证

[Apache-2.0](LICENSE)
