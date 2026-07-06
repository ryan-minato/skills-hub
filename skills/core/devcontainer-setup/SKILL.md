---
name: devcontainer-setup
description: >
  Creates and edits dev container configurations
  (.devcontainer/devcontainer.json) under a trusted-sources policy: base
  images only from mcr.microsoft.com/devcontainers/* or NVIDIA NGC
  (nvcr.io), features only from ghcr.io/devcontainers/features and
  ghcr.io/stacit-ai/devcontainer-features, templates only from
  ghcr.io/devcontainers/templates — with a bundled script that lists what
  each trusted source offers. Covers GPU-capable containers (NVIDIA/CUDA
  via NGC images, AMD/ROCm via device passthrough). Use when creating or
  modifying a devcontainer — "create a devcontainer", "set up a dev
  container", "add .devcontainer to this project", "make this repo open in
  a container", "configure Codespaces", "containerized dev environment",
  "GPU dev environment", or "CUDA/PyTorch container for development".
license: Apache-2.0
compatibility: >
  scripts/list_sources.py requires uv and Python 3.11+ (stdlib only) plus
  network access to mcr.microsoft.com, ghcr.io, api.ngc.nvidia.com, and
  nvcr.io (--self-test checks these prerequisites). Verification is
  strongest with the devcontainer CLI and a container runtime; authoring
  alone needs neither.
---

# Devcontainer Setup

Create or modify a project's dev container configuration
(`.devcontainer/devcontainer.json`) using trusted sources only. The policy
exists because images and features execute arbitrary code on the
developer's machine at build time — an unvetted source is a supply-chain
decision, not a style choice.

## Trusted sources policy

| Asset | Allowed origins |
|---|---|
| Base images | `mcr.microsoft.com/devcontainers/*`; NVIDIA NGC (`nvcr.io/nvidia/*`) |
| Features | `ghcr.io/devcontainers/features/*`; `ghcr.io/stacit-ai/devcontainer-features/*` |
| Templates | `ghcr.io/devcontainers/templates/*` |

These are the only sources to use unless the user explicitly requests a
specific other image, feature, or registry. An explicit user request
overrides the policy; never widen it on your own initiative (a convenient
community feature is not a reason), and when the user does override it,
note the deviation in your summary so it stays visible. When editing an
existing configuration that already references untrusted sources, leave
them in place but point them out.

## Assess the repository first

Before writing anything, check what already exists — the three
configuration axes (`image`, `build.dockerfile`, `dockerComposeFile`) are
peer options chosen by repository reality, not a default-to-image ladder:

- `.devcontainer/` already present → modify it; do not rebuild from
  scratch.
- A `Dockerfile` exists → consider `build.dockerfile`, reusing or wrapping
  it (its base image must still be trusted).
- A `docker-compose.yml` exists or development needs sidecar services
  (database, queue) → consider `dockerComposeFile` attached to the
  existing services.
- Otherwise → `image` + `features`, with the image matched to the
  project's language/toolchain.

Templates are skipped by default; only for a brand-new, empty project
apply one from `ghcr.io/devcontainers/templates/*`. GPU/CUDA/ROCm work →
read [references/gpu.md](references/gpu.md). Dockerfile/compose recipes,
lifecycle hooks, mounts, ports, users, or `templates apply` → read
[references/config-recipes.md](references/config-recipes.md).

## Discover what the trusted sources offer

Enumerate the trusted sources with
[`scripts/list_sources.py`](scripts/list_sources.py) instead of guessing
names, options, or tags:

```bash
uv run scripts/list_sources.py --kind features --format json   # all features + options
uv run scripts/list_sources.py --kind images --source ngc --filter pytorch
uv run scripts/list_sources.py --tags mcr.microsoft.com/devcontainers/python
```

The script only reaches trusted registries; a ref outside them exits 2.
`--format json` output is designed to be consumed directly. If the script
errors, or the user asks to add a trusted source, read
[references/trust-domains.md](references/trust-domains.md).

## Compose the configuration

Prefer `.devcontainer/devcontainer.json` (over a root `.devcontainer.json`)
and keep it minimal:

```jsonc
{
  "name": "myproject",
  "image": "mcr.microsoft.com/devcontainers/python:3-bookworm",
  "features": {
    "ghcr.io/devcontainers/features/github-cli:1": {},
    "ghcr.io/stacit-ai/devcontainer-features/uv:1": {}
  },
  "postCreateCommand": "uv sync",
  "customizations": {
    "vscode": { "extensions": ["ms-python.python"] }
  }
}
```

- Reference features by full OCI ref pinned to the major version shown by
  the lister (`ghcr.io/devcontainers/features/python:1`); `{}` means
  default options. Take option names from the lister's JSON output, never
  from memory.
- Project dependency install belongs in `postCreateCommand`; every-start
  services in `postStartCommand`.
- Pin the image tag from `--tags` output rather than trusting `latest` to
  exist.

## Baseline features for non-prebuilt images

Only `mcr.microsoft.com/devcontainers/*` images (and images explicitly
prebuilt for dev containers with the needed features baked in) come with
the baseline a dev container expects. **Every other base image — NGC
images, plain language/distro images, the base under a custom Dockerfile —
must add:**

- `ghcr.io/devcontainers/features/common-utils:2` — non-root user, shell
  and core utilities baseline;
- `ghcr.io/devcontainers/features/git:1` — and most projects also want
  `ghcr.io/devcontainers/features/git-lfs:1`.

Skipping this breaks user creation, `remoteUser`, and other features in
ways that surface late. For GPU images the rule is mandatory in practice:
read [references/gpu.md](references/gpu.md) before writing any config
whose image comes from `nvcr.io` or that needs GPU access (NVIDIA and AMD
paths, `runArgs`, `hostRequirements.gpu`).

## Verify

1. Every image/feature/template ref in the config must resolve against the
   lister's output (or be an explicitly user-approved exception).
2. If the `devcontainer` CLI is available, build it:
   `npx -y @devcontainers/cli@0.87.0 build --workspace-folder .` (or
   `devcontainer up` when a runtime is available) and fix what it reports.
3. If no CLI/runtime is available, say so explicitly and tell the user how
   to test (reopen in container, or the command above). Never claim the
   container works without one of these.

## Gotchas

- `image`, `build`, and `dockerComposeFile` are mutually exclusive axes —
  setting two silently ignores one depending on the tool.
- A feature ref without a version tag floats to `latest`; always pin at
  least the major version.
- devcontainer.json is JSONC (comments and trailing commas allowed);
  strict JSON parsers reject valid files — do not "fix" comments away.
- NGC tags are date-based (`yy.mm`) and `latest` frequently does not
  exist; list tags before picking.
- Features are applied by devcontainer tooling at build time; plain
  `docker run` of the same base image gets none of them.

## Spec references

For exact property semantics, fetch the authoritative spec documents
rather than relying on paraphrase:

- devcontainer.json reference:
  <https://raw.githubusercontent.com/devcontainers/spec/main/docs/specs/devcontainerjson-reference.md>
- Overall spec:
  <https://raw.githubusercontent.com/devcontainers/spec/main/docs/specs/devcontainer-reference.md>
