# AGENTS.md

Agent entrypoint for this Dev Container Features repository. Read this
before making changes.

## Purpose

This repository publishes Dev Container Features — self-contained,
versioned install units — to an OCI registry. Consumers install each
feature individually by its registry address; the repository itself never
ships to them.

## Structure

```
src/<id>/
  devcontainer-feature.json   Manifest; `id` MUST equal the directory name
  install.sh                  Installer; runs as root at image build time
  NOTES.md                    Optional; appended to the generated README
  README.md                   AUTO-GENERATED at release — never edit by hand
test/<id>/
  test.sh                     Default-options test (dev-container-features-test-lib)
  scenarios.json              Option-combination scenarios
  <scenario>.sh               One script per scenario key
  compatibility.txt           One supported base image per line (# comments)
test/_global/                 Cross-feature scenarios
.github/actions/              Shared composite actions used by all workflows
justfile                      Local mirror of the CI test commands
```

Every `src/<id>/` has a matching `test/<id>/`.

## Core conventions

- `install.sh`: bash with `set -euo pipefail`; runs as root; option values
  arrive as UPPERCASED env vars; install user-facing artifacts for
  `_REMOTE_USER`, not root. Idempotent — re-running must not fail.
- **Features are independent.** `dependsOn`/`installsAfter` must use full
  public OCI refs (`ghcr.io/<owner>/<repo>/<id>:1`) even for features in
  this same repository — consumers install from the registry, where
  sibling source directories do not exist.
- Bump `version` (semver) in `devcontainer-feature.json` for every change
  you want published; releasing an unchanged version is a no-op.
- Tests must `source dev-container-features-test-lib`, use
  `check "<label>" <cmd>`, and end with `reportResults`.
- `test/<id>/compatibility.txt` is the feature's supported-image claim;
  CI tests exactly what it declares. Only claim images the install
  actually handles.
- Commit messages: Conventional Commits, scope = feature id.

## Commands

| Task | Command |
|---|---|
| Test one feature (default options) | `just test <id>` |
| Test against a specific image | `just test <id> <image>` |
| Repeat-install (idempotency) test | `just test-duplicate <id>` |
| Scenario tests | `just test-scenarios <id>` |
| Global scenarios | `just test-global` |
| Full compatibility sweep | `just test-compat <id>` |
| Manifest + shell lint | `just validate && just lint` |

## CI/CD

| Workflow | Trigger | Purpose |
|---|---|---|
| `test.yaml` | push/PR | Changed features only, ubuntu base, all modes |
| `test-multios.yaml` | main, manual | All features x their compatibility.txt images |
| `validate.yaml` | PR | Manifest schema + shellcheck |
| `release.yaml` | manual | Publish to GHCR, then regenerate READMEs via PR |

All test workflows call the shared `.github/actions/run-feature-test`
action; change test invocation logic there, not in the workflows.

## Adding a feature

1. Create `src/<id>/` (manifest + install.sh) and `test/<id>/` (test.sh,
   compatibility.txt; scenarios for every non-default option worth
   supporting).
2. `just test <id>` and `just test-compat <id>` pass locally.
3. Open a PR; CI tests only your feature. After merge, run the release
   workflow to publish.
