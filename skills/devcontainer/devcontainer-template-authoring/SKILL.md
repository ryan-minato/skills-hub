---
name: devcontainer-template-authoring
description: >
  Dev Container Template authoring — create, test, and publish parameterized
  .devcontainer starters applied once into a project. Use when building, changing, or
  publishing a devcontainer Template; when an existing .devcontainer should become a
  reusable starter or teams keep copy-pasting devcontainer configs; when designing
  options users pick at apply time; when an applied template misbehaves — option
  substitution mangles files, applying fails, or pickers don't surface it; or when
  src/*/devcontainer-template.json is the material at hand. Not for setting up a
  devcontainer in one project (devcontainer-setup), tool installers
  (devcontainer-feature-authoring), or prebuilt images (devcontainer-image-prebuild).
license: Apache-2.0
compatibility: >
  Smoke-testing and publishing require the Dev Container CLI (pinned via
  npx -y @devcontainers/cli@0.87.0 or npm install -g) and a running
  Docker-compatible engine; publishing also needs push access to an OCI
  registry (e.g. ghcr.io). Authoring guidance applies without them.
---

# Devcontainer Template Authoring

A Template is a starting configuration copied **once** into the user's
project, which they then own and edit freely. The three dev container
artifacts divide cleanly: a **Template** is an applied-once starter; a
**Feature** installs tooling on every container build; a **prebuilt
image** bakes results ahead of time. If the payload you are packaging is
really a tool installer, build a Feature instead — this skill pairs with
`devcontainer-feature-authoring`; if it is not installed:
`npx skills add ryan-minato/skills --skill devcontainer-feature-authoring`.

## Prerequisites

A Docker-compatible engine and the Dev Container CLI:

```bash
npm install -g @devcontainers/cli@0.87.0   # or npx -y @devcontainers/cli@0.87.0
```

Do not scaffold from `devcontainers/template-starter` — it hardcodes its
template list in CI, masks test failures with `continue-on-error`, tests
with an unpinned CLI, and has no agent harness. This skill ships a
modern scaffold instead.

## Repository scaffold

Copy [`assets/scaffold/`](assets/scaffold/) into the new repository root
and adapt owner/repo placeholders:

- `src/<id>/devcontainer-template.json` + `.devcontainer/` payload
  (+ `NOTES.md`, appended to the auto-generated README) — `id` must
  equal the directory name; `test/<id>/test.sh` runs inside the applied
  container.
- `AGENTS.md` — harness so coding agents work correctly in the repo.
- `.github/actions/smoke-test/` — **the shared action + `smoke.sh`**:
  pinned CLI install, default-option substitution, `devcontainer up`,
  in-container test run, labeled-container cleanup. Test-mechanics
  changes happen there once.
- `.github/actions/detect-changed-templates/` — auto path filters; PRs
  test only changed templates, new `src/<id>/` dirs need no workflow
  edits.
- `.github/workflows/` — `test.yaml` (changed-template smoke tests),
  `release.yaml` (least-privilege publish + docs-PR jobs).
- `justfile` — local mirror (`just smoke <id>`, `just validate`,
  `just lint`).
- `src/hello-template/` + `test/hello-template/` — a working example;
  replace with the real template.

## devcontainer-template.json and substitution

```jsonc
{
  "id": "my-stack",            // = directory name
  "version": "1.0.0",          // semver; bumping it is what publishes
  "name": "My Stack",
  "platforms": ["Python"],     // declare honestly; pickers filter on it
  "options": {
    "imageVariant": {
      "type": "string",
      "proposals": ["3.12-bookworm", "3.13-bookworm"],
      "default": "3.12-bookworm",
      "description": "Python image variant."
    }
  }
}
```

Any text file in the payload may contain `${templateOption:imageVariant}`;
applying replaces it with the chosen value. It is plain text substitution
— no conditionals, no defaults-at-use-site, no binary files. Read
[references/template-json-reference.md](references/template-json-reference.md)
for the full field list (`optionalPaths`, `publisher`, `keywords`, ...)
or when reviewing an existing manifest.

## Designing a good template

- **Minimal payload**: ship only files the user should own after apply —
  a `.devcontainer/` and, when genuinely needed, seed project files.
  Reusable install logic belongs in a Feature (referenced by full public
  OCI address); heavyweight toolchains belong in a prebuilt image the
  template references.
- **Options only for real variation points**, each with a working
  default: applying with zero input must produce a working container.
  Prefer `proposals` over `enum` unless other values cannot work.
- **Prefer `image` + `features`** in the payload's devcontainer.json
  over baking a Dockerfile; a Dockerfile in a template becomes the
  user's maintenance burden forever.
- **`optionalPaths`** for genuinely removable extras (sample CI, example
  code) — never for files the container needs.
- **Honest `platforms`** so pickers surface it to the right users.

## Testing

The smoke-test loop mirrors what `templates apply` does, without needing
the template published: substitute every option's **default** into a
temp copy of `src/<id>`, run `devcontainer up` on it, then execute
`test/<id>/test.sh` inside the container and assert the template's
promises (tools present, user correct, service reachable). Locally:

```bash
just smoke my-stack        # wraps .github/actions/smoke-test/smoke.sh
```

Test non-default option values by temporarily editing the defaults or
extending `smoke.sh` — and keep assertions on behavior, not file
contents.

## Publishing

```bash
npx -y @devcontainers/cli@0.87.0 templates publish \
  -r ghcr.io -n <owner>/<repo> ./src
```

Consumers run `devcontainer templates apply -t ghcr.io/<ns>/<id> -a
'{...}'` or use their editor's template picker. Read
[references/publishing-and-ci.md](references/publishing-and-ci.md) when
publishing, adjusting the release pipeline, or registering the
collection on containers.dev.

## Gotchas

- `${templateOption:...}` is dumb text replacement — an option value
  containing sed-special characters or used inside a binary file breaks
  silently; keep values simple strings.
- Option types are `string` and `boolean` only; booleans substitute as
  the strings `true`/`false`.
- A template must work with zero option input — a missing `default` is
  an authoring bug (the scaffold's smoke test fails on it).
- Editing files without bumping `version` publishes nothing.
- `src/<id>/README.md` is auto-generated at release — hand edits are
  overwritten; put prose in `NOTES.md`.
- GHCR packages default to private; flip visibility after first publish
  or applying fails with auth errors.

## Spec references

- Templates: <https://raw.githubusercontent.com/devcontainers/spec/main/docs/specs/devcontainer-templates.md>
- Distribution: <https://raw.githubusercontent.com/devcontainers/spec/main/docs/specs/devcontainer-templates-distribution.md>
