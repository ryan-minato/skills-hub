# Publishing features and the release pipeline

Read this when publishing features or setting up/adjusting the CI release
workflow. Distribution spec:
<https://raw.githubusercontent.com/devcontainers/spec/main/docs/specs/devcontainer-features-distribution.md>

## What publishing produces

For each feature, a tarball `devcontainer-feature-<id>.tgz` (the whole
`src/<id>/` directory) is pushed as an OCI artifact to
`<registry>/<namespace>/<id>` with tags `:MAJOR`, `:MAJOR.MINOR`,
`:MAJOR.MINOR.PATCH`, and `:latest`. The namespace additionally receives
an auto-generated `devcontainer-collection.json` (tag `latest`) listing
every feature's metadata — that is what pickers and enumeration tools
read.

Publishing is driven by `version` in `devcontainer-feature.json`: a
version that already exists in the registry is skipped. Bump the version
or nothing happens — there is no force-republish.

## Manual publish

```bash
npx -y @devcontainers/cli@0.87.0 features publish \
  -r ghcr.io -n <owner>/<repo> ./src
```

Auth: a `GITHUB_TOKEN`/PAT with `packages:write` (the CLI reads standard
docker credentials or `GITHUB_TOKEN`). Prefer the CI workflow below over
manual publishes so releases stay reproducible and documented.

## GHCR visibility

Packages published to ghcr.io default to **private**; consumers then get
auth errors that look like the feature does not exist. After the first
publish of each feature (and the collection package), set the package's
visibility to public in the GitHub package settings, or pre-create the
packages public.

## The scaffold's release pipeline

`assets/scaffold/.github/workflows/release.yaml` (manual dispatch, main
only) runs two jobs:

1. `publish` — `devcontainers/action@v1` with `publish-features: "true"`
   and `base-path-to-features: ./src`; holds only `packages: write`.
2. `docs` — the same action with `generate-docs: "true"`, which
   regenerates each `src/<id>/README.md` from the manifest (appending
   `NOTES.md` when present), then opens a PR with the regenerated files;
   holds `contents: write` + `pull-requests: write`.

The split keeps each job at least privilege and makes a docs-only rerun
possible. Adaptation points: registry/namespace (non-GHCR registries need
a login step and CLI-based publish instead of `devcontainers/action`),
and action pinning — `@v1`/`@v4` are moving tags; pin to commit SHAs when
supply-chain policy requires immutability.

## Release procedure

1. Bump `version` in the changed feature's `devcontainer-feature.json`
   in the same PR as the change (semver: patch = fixes, minor = new
   options/behavior, major = breaking option or behavior changes; never
   reuse a published version).
2. Merge to main with green `test`/`validate` workflows.
3. Run the `release` workflow; verify the new tags exist
   (`docker manifest inspect ghcr.io/<ns>/<id>:<ver>` or the registry UI).
4. Merge the automated docs PR it opens.

## Optional: containers.dev discoverability

To surface the collection on containers.dev (and in the VS Code picker's
index), add it to the community index by PR-ing
`collection-index.yml` in <https://github.com/devcontainers/devcontainers.github.io>.
Enumeration via the OCI collection metadata works without registration.
