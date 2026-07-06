# core

[中文](README.zh.md)

Skills recommended for **global (user-level) installation** — they are
useful in every environment regardless of the project.

```bash
npx skills add ryan-minato/skills --skill <skill-name> -g
```

## Skills

| Skill | Description |
|---|---|
| [conventional-commits](conventional-commits/) | Draft git commit messages that comply with Conventional Commits 1.0.0: rule precedence (docs > commitlint config > history > defaults), a first-match type decision list, scope and breaking-change policy, and a pre-handover validation checklist. |
| [devcontainer-setup](devcontainer-setup/) | Create and edit dev container configurations under a trusted-sources policy (mcr.microsoft.com/devcontainers, NVIDIA NGC, ghcr.io/devcontainers, ghcr.io/stacit-ai), with a bundled source-enumeration script, baseline-feature rules for non-prebuilt images, and NVIDIA/AMD GPU guidance. |
| [git-commit](git-commit/) | Execute the full git commit workflow as ordered gates: convention discovery with explicit rule precedence, atomicity check, secret/PII scan of the staged diff, committer identity check, hooks and local checks, and a bundled message validator before committing. |
| [great-skill-writer](great-skill-writer/) | Write and improve Agent Skills that behave predictably: spec-compliant frontmatter, trigger-accurate descriptions, checkable completion criteria, progressive disclosure, and a bundled linter. |
| [meta-harness](meta-harness/) | Design, audit, and improve agent harnesses: inspect project and team facts, choose a maturity level (L0–L4), calibrate nine harness layers, and make every rule discoverable to future agents from AGENTS.md. |
| [programming-guidelines](programming-guidelines/) | Apply universal coding standards for programming work: think before coding, prefer simple solutions, make surgical changes, and verify against clear success criteria. |
| [ryan-minato-skills-installing](ryan-minato-skills-installing/) | Install skills from the ryan-minato/skills library into a project or globally: prefer the vercel-labs skills CLI through a modern package runner (pnpm/bun/yarn) or npx, with a bundled stdlib clone-and-copy fallback when no Node runtime exists, plus a discovery listing of available skills. |
| [sensitivity-check](sensitivity-check/) | Detect PII and leaked secrets in text or files and produce a structured report. Preferred engines (Presidio, detect-secrets via uv) with stdlib-only fallback scripts covering generic + US/GB/CN/JP entities. |
