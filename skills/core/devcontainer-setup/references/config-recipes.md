# Configuration recipes beyond image + features

Read this when using `build.dockerfile` or `dockerComposeFile`, when you
need lifecycle hooks beyond `postCreateCommand`, mounts, port forwarding,
user/env fine-tuning, or `devcontainer templates apply`.

Authoritative property definitions (fetch when exact semantics matter):
<https://raw.githubusercontent.com/devcontainers/spec/main/docs/specs/devcontainerjson-reference.md>

## Dockerfile-based configuration

Use when the project needs system packages no trusted feature provides, or
when a Dockerfile already exists. The `FROM` image must still come from a
trusted source (or be explicitly user-approved).

```jsonc
{
  "name": "myproject",
  "build": {
    "dockerfile": "Dockerfile",        // relative to this file's directory
    "context": "..",                    // default "."
    "args": { "VARIANT": "bookworm" }
  },
  "features": { "ghcr.io/devcontainers/features/git:1": {} }
}
```

- `image`, `build`, and `dockerComposeFile` are mutually exclusive axes.
- Features still apply on top of the built image, so prefer a minimal
  Dockerfile plus features over baking tools into the Dockerfile.
- Reusing an existing production Dockerfile is fine only if its base is
  trusted and it does not strip the tooling a dev environment needs;
  otherwise write a separate `.devcontainer/Dockerfile` that `FROM`s a
  trusted image.

## Docker Compose-based configuration

Use when development needs sidecar services (database, queue) or when the
repo already has a compose file to attach to.

```jsonc
{
  "name": "myproject",
  "dockerComposeFile": ["../docker-compose.yml", "docker-compose.dev.yml"],
  "service": "app",                    // the service agents attach to
  "workspaceFolder": "/workspace",
  "features": { "ghcr.io/devcontainers/features/git:1": {} },
  "shutdownAction": "stopCompose"
}
```

- `service` is required; other services start too (limit with
  `runServices`).
- Add a dev override file rather than editing the production compose file:
  mount the source into the service and neutralize its production
  `command` if it exits (`command: sleep infinity`), or set
  `overrideCommand: true`.
- The service's image is subject to the same trusted-sources policy.

## Lifecycle hooks

| Hook | Runs | Typical use |
|---|---|---|
| `initializeCommand` | on the **host**, before create and on starts | host-side prep (careful: runs outside the container) |
| `onCreateCommand` | in container, once at creation (prebuild-friendly) | system-level setup that can be baked into prebuilds |
| `updateContentCommand` | in container, on creation and when content updates | dependency install that must track the repo |
| `postCreateCommand` | in container, once after user setup | project dependency install, one-time tool config |
| `postStartCommand` | in container, every start | services, daemons |
| `postAttachCommand` | in container, every tool attach | personal shell niceties |

- Values: string (runs via `/bin/sh -c`), array (exec, no shell), or object
  (named commands run in parallel).
- A failing hook halts the remaining sequence — keep hooks idempotent.
- Default rule: dependency install goes in `postCreateCommand`;
  every-start services in `postStartCommand`.

## Users and environment

- `remoteUser`: the user tools and hooks-after-create run as (default:
  image's user, often `vscode` on devcontainers images).
  `containerUser`: the user the container itself runs as. Set `remoteUser`
  when in doubt.
- `updateRemoteUserUID` (default true on Linux) remaps the user's UID/GID
  to the local user, avoiding bind-mount permission pain.
- `containerEnv` sets env for every container process (static);
  `remoteEnv` only for tool-spawned processes and supports
  `${localEnv:VAR}` / `${containerEnv:VAR}` substitution.

## Mounts and ports

```jsonc
{
  "mounts": [
    {
      "source": "${localEnv:HOME}/.cache/huggingface",
      "target": "/home/vscode/.cache/huggingface",
      "type": "bind"
    }
  ],
  "forwardPorts": [8000],
  "portsAttributes": {
    "8000": { "label": "api", "onAutoForward": "notify" }
  }
}
```

- Named volumes (`"type": "volume"`) survive rebuilds — use them for
  caches (package managers, model downloads).
- `forwardPorts` is the declarative way; do not use `runArgs` `-p` unless
  the port must be host-published for non-tooling reasons.

## Applying a template

Only for a brand-new project with no existing container assets, and only
from `ghcr.io/devcontainers/templates/*`:

```bash
npx -y @devcontainers/cli@0.87.0 templates apply \
  -t ghcr.io/devcontainers/templates/python:3 \
  -a '{"imageVariant": "3.12-bookworm"}'
```

List available templates and their options first
(`uv run scripts/list_sources.py --kind templates --format json`). After
applying, review the generated files against the trusted-sources policy
and the baseline-features rule like any hand-written config.
