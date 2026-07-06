# Skills

[中文](README.zh.md)

A curated library of [Agent Skills](https://agentskills.io) — self-contained
instruction packages that teach coding agents (Claude Code, Codex, Copilot,
and other compatible clients) how to perform specific tasks well.

## Catalogs

| Catalog | Contents | Install scope |
|---|---|---|
| [`core`](skills/core/) | Skills recommended for every environment | Global (user-level) |
| [`devcontainer`](skills/devcontainer/) | Dev Container authoring skills: Features, Templates, and prebuilt images | Per project, as needed |
| [`engineering`](skills/engineering/) | General programming methodology skills, not tied to a language or framework | Per project, as needed |
| [`github`](skills/github/) | GitHub collaboration workflows: MCP-first issue/PR/Discussions/Actions operations and conventions authoring | Per project, as needed |
| [`ops`](skills/ops/) | General workflow operations, not invoked directly | Per project, as needed |

Each catalog's README lists its skills.

## Installation

Install individual skills with the [skills CLI](https://github.com/vercel-labs/skills):

```bash
# Pick skills interactively (project-level)
npx skills add ryan-minato/skills

# Install a specific skill
npx skills add ryan-minato/skills --skill <skill-name>

# Install globally (recommended for core skills)
npx skills add ryan-minato/skills --skill <skill-name> -g
```

`core` skills are recommended for global installation so they are available
in every project; install other catalogs' skills into the projects that need
them.

## Contributing

Conventions, quality standards, and repository mechanics are documented for
both humans and agents: start at [AGENTS.md](AGENTS.md), then
[ARCHITECTURE.md](ARCHITECTURE.md). Run `just setup` once after cloning and
`just check` before committing.

## License

[Apache-2.0](LICENSE)
