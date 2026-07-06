# devcontainer

[中文](README.zh.md)

Dev Container **authoring** skills — developing Features, creating
Templates, and prebuilding images for the
[Dev Container ecosystem](https://containers.dev). For *using* dev
containers (creating a project's development environment), see the
`devcontainer-setup` skill in the `core` catalog.

```bash
npx skills add ryan-minato/skills --skill <skill-name>
```

## Skills

| Skill | Description |
|---|---|
| [devcontainer-feature-authoring](devcontainer-feature-authoring/) | Develop, test, and publish Dev Container Features: manifest schema and install.sh contract, quality bar (idempotency, base-image tolerance, non-root correctness, deterministic installs), the feature-independence rule, and a modern repo scaffold with shared-action CI. |
