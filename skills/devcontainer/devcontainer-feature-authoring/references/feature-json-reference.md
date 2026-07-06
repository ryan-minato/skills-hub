# devcontainer-feature.json property reference

Read this when you need a property not covered in SKILL.md, or when
reviewing an existing feature manifest. Authoritative source (fetch when
exact semantics matter):
<https://raw.githubusercontent.com/devcontainers/spec/main/docs/specs/devcontainer-features.md>

## Identity (required)

| Property | Rules |
|---|---|
| `id` | Must equal the `src/<id>/` directory name; becomes the last segment of the OCI ref. |
| `version` | Semver. Publishing only happens when this changes; registries tag `:MAJOR`, `:MAJOR.MINOR`, `:MAJOR.MINOR.PATCH`, `:latest`. |
| `name` | Human-readable display name. |

## Descriptive

| Property | Notes |
|---|---|
| `description` | Shown in pickers and generated README. |
| `documentationURL` | Link users land on; point at real docs. |
| `licenseURL` | License link. |
| `keywords` | Array of search terms. |

## Options

```jsonc
"options": {
  "version": {
    "type": "string",          // "string" or "boolean" only
    "proposals": ["latest", "1.8"], // suggestions; free-form input allowed
    "default": "latest",
    "description": "Version to install."
  },
  "flavor": {
    "type": "string",
    "enum": ["minimal", "full"],   // closed set; free-form input rejected
    "default": "minimal",
    "description": "Install profile."
  }
}
```

- `proposals` vs `enum`: `enum` validates and rejects other values — use it
  only when other values genuinely cannot work; otherwise `proposals`.
- Every option needs a working `default`; a feature must install cleanly
  with `{}`.
- Option values reach `install.sh` as environment variables: the option
  name uppercased with every non-alphanumeric character replaced by `_`
  (`version` → `VERSION`, `installTools` → `INSTALLTOOLS` — no underscore
  is inserted at case boundaries).

## Container effects

| Property | Effect |
|---|---|
| `containerEnv` | Env vars set for all container processes. |
| `mounts` | Mounts added to the container (same shape as devcontainer.json mounts). |
| `init` | `true` adds `--init`. |
| `privileged` | `true` adds `--privileged`; demand a strong reason. |
| `capAdd` | Added Linux capabilities (e.g. `SYS_PTRACE`). |
| `securityOpt` | Security options (e.g. `seccomp=unconfined`). |
| `entrypoint` | Script invoked at container start (for daemons the feature provides); must exec/forward to the original entrypoint semantics. |
| `customizations` | Tool-namespaced settings merged into the final config (e.g. `customizations.vscode.extensions`). |

## Ordering and dependencies

| Property | Semantics |
|---|---|
| `dependsOn` | **Hard** dependencies, resolved recursively, installed first; keys are FULL OCI refs with a pinned major (`"ghcr.io/<owner>/<repo>/<id>:1": {"option": "value"}`); may pass options. A missing dependency fails the build. |
| `installsAfter` | **Soft** ordering hints; affects only features the user already selected; not recursive; cannot carry options or install anything. |
| (user side) `overrideFeatureInstallOrder` | devcontainer.json escape hatch that raises priority; cannot violate the dependency graph. |

Both must reference features by full public OCI address even when the
target lives in the same source repository — consumers install each
feature individually from the registry, where sibling source directories
do not exist.

## Lifecycle metadata

| Property | Notes |
|---|---|
| `deprecated` | `true` hides the feature from pickers; keep publishing docs pointing at the replacement. |
| `legacyIds` | Former ids after a rename, so existing references keep resolving. |

## install.sh environment contract

- Runs as **root** at image build time; `$HOME` is root's home.
- Option env vars as described above, sourced from a generated
  `devcontainer-features.env`.
- Injected user variables: `_REMOTE_USER`, `_REMOTE_USER_HOME`,
  `_CONTAINER_USER`, `_CONTAINER_USER_HOME`. Install user-facing artifacts
  (shell rc entries, per-user tool state, PATH additions) for
  `_REMOTE_USER`, not root; `chown` what you create in the user's home.
- With no `remoteUser` configured, `_REMOTE_USER` equals `_CONTAINER_USER`.
