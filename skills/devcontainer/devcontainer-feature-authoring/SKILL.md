---
name: devcontainer-feature-authoring
description: >
  Dev Container Feature authoring — develop, test, and publish reusable install units.
  Use when creating, modifying, or releasing a devcontainer Feature or its options;
  when a tool install or setup script should be reusable across projects' dev
  containers; when a feature misbehaves — breaks on another base image, fails when
  applied twice, or a release publishes nothing; when questions arise about Feature
  mechanics — dependsOn vs installsAfter, option variables, versioning; or when
  src/*/devcontainer-feature.json, its install.sh, or test/*/scenarios.json is the
  material at hand. Not for consuming features in a project's devcontainer.json
  (devcontainer-setup), project starters (devcontainer-template-authoring), or
  prebuilt images (devcontainer-image-prebuild).
license: Apache-2.0
compatibility: >
  Testing and publishing require the Dev Container CLI (pinned via
  npx -y @devcontainers/cli@0.87.0 or npm install -g) and a running
  Docker-compatible engine; publishing also needs push access to an OCI
  registry (e.g. ghcr.io). Authoring guidance applies without them.
---

# Devcontainer Feature Authoring

A Feature is a self-contained, versioned install unit that consumers
reference by OCI address and that runs during every container build. The
three dev container artifacts divide cleanly: a **Feature** installs
tooling on each build; a **Template** is a starting configuration copied
once into a project; a **prebuilt image** bakes the results ahead of
time. Build a Feature when a tool install should be reusable across
projects; one-off project setup belongs in `postCreateCommand` or the
project's Dockerfile instead.

## Prerequisites

A Docker-compatible engine and the Dev Container CLI:

```bash
npm install -g @devcontainers/cli@0.87.0   # or npx -y @devcontainers/cli@0.87.0
```

Do not scaffold from `devcontainers/feature-starter` — it hardcodes its
feature/image matrix, tests unpinned tool versions, and has no agent
harness. This skill ships a modern scaffold instead.

## Repository scaffold

Copy [`assets/scaffold/`](assets/scaffold/) into the new repository root
and adapt owner/repo placeholders. Its layout:

- `src/<id>/devcontainer-feature.json` + `install.sh` (+ `NOTES.md`,
  appended to the auto-generated README) — `id` must equal the directory
  name; `test/<id>/` mirrors every `src/<id>/`.
- `AGENTS.md` — harness so coding agents work correctly in the repo
  (structure, conventions, commands, CI map).
- `.github/actions/run-feature-test/` — **the shared composite action**:
  pinned CLI install + every `devcontainer features test` invocation
  mode. All test workflows call it; test logic changes happen there once.
- `.github/actions/detect-changed-features/` — auto-generated path
  filters; PRs test only changed features, and new `src/<id>/` dirs are
  picked up with zero workflow edits.
- `.github/actions/build-test-matrix/` — expands features into a
  `{feature, baseImage}` matrix from each `test/<id>/compatibility.txt`,
  so every feature declares its own supported images.
- `.github/workflows/` — `test.yaml` (fast changed-only loop),
  `test-multios.yaml` (full compatibility sweep on main/dispatch),
  `validate.yaml` (manifest schema + shellcheck), `release.yaml`
  (least-privilege publish + docs-PR jobs).
- `justfile` — local mirror of the CI commands (`just test <id>`, etc.).
- `src/hello-tool/` + `test/hello-tool/` — a working example feature
  demonstrating the conventions; replace it with the real feature.

## devcontainer-feature.json essentials

```jsonc
{
  "id": "mytool",              // = directory name, = last OCI ref segment
  "version": "1.0.0",          // semver; bumping it is what publishes
  "name": "My Tool",
  "options": {
    "version": {
      "type": "string",              // "string" or "boolean"
      "proposals": ["latest", "2.1"], // suggestions (open); enum = closed
      "default": "latest",           // every option needs a working default
      "description": "Tool version to install."
    }
  }
}
```

Read [references/feature-json-reference.md](references/feature-json-reference.md)
when you need any property beyond these (containerEnv, mounts,
entrypoint, customizations, privileged, deprecated/legacyIds, or the full
dependsOn/installsAfter fine print), or when reviewing an existing
manifest.

## The install.sh contract

Runs as **root** at image build time. Option values arrive as environment
variables — the option name uppercased with non-alphanumerics replaced by
`_` (`version` → `VERSION`, `installTools` → `INSTALLTOOLS`). The CLI
also injects `_REMOTE_USER`, `_REMOTE_USER_HOME`, `_CONTAINER_USER`,
`_CONTAINER_USER_HOME`. Skeleton:

```bash
#!/usr/bin/env bash
set -euo pipefail

VERSION="${VERSION:-latest}"

if [ "$(id -u)" -ne 0 ]; then
    echo "must run as root during the image build" >&2
    exit 1
fi

# ... resolve "latest" to a concrete version, download by pinned URL,
# verify checksum when the vendor publishes one, install ...

# User-facing artifacts (rc entries, per-user state) belong to the remote
# user, not root:
#   install -d -o "${_REMOTE_USER}" "${_REMOTE_USER_HOME}/.config/mytool"

# Debian-family: clean apt lists to keep layers small.
# rm -rf /var/lib/apt/lists/*
```

## What makes a Feature good

Correct is the floor; these are what make one worth publishing:

- **Idempotent**: re-installation must not fail — prebuilds and metadata
  merges can apply a feature more than once. "Create if absent" guards;
  prove it with the duplicate-install test mode.
- **Base-image tolerant**: branch on `/etc/os-release` for the distros
  you support, and fail fast with a message naming the supported set for
  the rest. A silent partial install is the worst outcome. Claim exactly
  what you test in `test/<id>/compatibility.txt`.
- **Non-root correct**: install user-facing pieces for `_REMOTE_USER`
  (PATH additions, shell rc, ownership via `chown`/`install -o`), and
  test both root and non-root scenarios when the install touches home
  directories.
- **Well-optioned**: the smallest option set covering real variation;
  zero-config (`{}`) must produce a sensible install; `enum` only when
  other values genuinely cannot work (otherwise `proposals`); a `version`
  option defaulting to `latest` that supports pinning.
- **Deterministic**: resolve `latest` to a concrete version at install
  time and log it; pin download URLs by version; verify checksums where
  available. Two builds a week apart should differ only when the user
  asked for `latest`.
- **Fast and lean**: prefer binary releases over compilation; clean
  package-manager caches; every consumer pays your install time on every
  full build.
- **Diagnosable and documented**: errors say what failed and how to fix
  it; `NOTES.md` documents supported bases and caveats (it becomes the
  published README's tail).
- **Semver-disciplined**: patch = fixes, minor = new options/behavior,
  major = breaking changes; never republish a used version.

## Features are independent — always

Every published feature is its own tarball, installed individually by
registry address; the repository it was developed in does not exist on
the consumer's machine. Therefore `dependsOn` and `installsAfter` must
use **full public OCI references, even for features in the same source
repository**:

```jsonc
"dependsOn": { "ghcr.io/<owner>/<repo>/other-tool:1": {} }
```

A bare or relative id resolves during local development and then breaks
for every registry consumer. Semantics: `dependsOn` = hard dependency,
recursive, may pass options, pin the major; `installsAfter` = soft
ordering hint among already-selected features, not recursive, installs
nothing. Design consequence: if two features cannot be used
independently, they are one feature.

## Testing

```bash
devcontainer features test --project-folder . -f mytool \
  -i mcr.microsoft.com/devcontainers/base:ubuntu
```

`test/<id>/test.sh` sources `dev-container-features-test-lib`, asserts
with `check "<label>" <cmd>`, and ends with `reportResults`. The scaffold
runs three modes per feature (default install, duplicate install,
scenarios) — locally via `just test|test-duplicate|test-scenarios <id>`.
Read [references/testing.md](references/testing.md) when writing
scenarios, the idempotency test, a base-image matrix, or when debugging
test failures.

## Publishing

```bash
npx -y @devcontainers/cli@0.87.0 features publish \
  -r ghcr.io -n <owner>/<repo> ./src
```

Each release fans out semver tags (`:1`, `:1.2`, `:1.2.3`, `:latest`) and
regenerates the namespace's `devcontainer-collection.json`. Prefer the
scaffold's `release.yaml` over manual publishes. Read
[references/publishing-and-release.md](references/publishing-and-release.md)
when publishing or adjusting the release pipeline (GHCR visibility,
docs generation, containers.dev registration).

## Gotchas

- Option-name mangling inserts no separators: `nodeVersion` →
  `NODEVERSION`, not `NODE_VERSION`.
- `installsAfter` installs nothing — it only orders features the user
  already selected; needing the other feature present means `dependsOn`.
- `version` in the manifest is the **feature's** version, not the tool's;
  tool versions belong in an option.
- Tests run against local `src/`, but `dependsOn` still resolves from the
  registry — publish dependencies before testing dependents.
- GHCR packages default to private; forgetting to flip visibility makes
  consumers see auth errors that look like a missing feature.
- Editing files without bumping `version` publishes nothing — releases
  are keyed on the manifest version.

## Spec references

Fetch the authoritative documents when exact behavior matters:

- Features: <https://raw.githubusercontent.com/devcontainers/spec/main/docs/specs/devcontainer-features.md>
- Distribution: <https://raw.githubusercontent.com/devcontainers/spec/main/docs/specs/devcontainer-features-distribution.md>
- Dependency resolution: <https://raw.githubusercontent.com/devcontainers/spec/main/docs/specs/feature-dependencies.md>
