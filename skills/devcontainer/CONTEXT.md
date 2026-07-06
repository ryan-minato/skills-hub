# devcontainer — Catalog Context

Rules, notes, and references that apply only to skills in this catalog.
(Repo-wide standards live in `.agents/knowledge/skill-quality.md`.)

## Requirements

- Skills here are **authoring** skills for the Dev Container ecosystem:
  they teach how to build, test, and publish devcontainer artifacts
  (Features, Templates, prebuilt images). Skills for *consuming* dev
  containers (setting up a project's environment) belong in `core`.
- One skill covers one artifact kind end to end (design, implement, test,
  publish). Cross-artifact overlap stays limited to a short shared
  disambiguation block; deep content lives only in the owning skill.
- Spec accuracy: use exact property and CLI names from the Dev Container
  spec, and include raw spec document links (see References) so agents can
  verify interfaces on demand instead of trusting paraphrases.

## References

- Dev Container spec (rendered): <https://containers.dev/implementors/spec/>
- devcontainer.json reference: <https://containers.dev/implementors/json_reference/>
- Features: <https://containers.dev/implementors/features/>
- Features distribution: <https://containers.dev/implementors/features-distribution/>
- Templates: <https://containers.dev/implementors/templates/>
- Templates distribution: <https://containers.dev/implementors/templates-distribution/>
- Spec source (raw markdown): <https://github.com/devcontainers/spec/tree/main/docs/specs>
- Dev Container CLI: <https://github.com/devcontainers/cli>
- Official images: <https://github.com/devcontainers/images>
- CI action: <https://github.com/devcontainers/ci>
- Starters (prior art; superseded by the scaffolds bundled in this
  catalog's skills): <https://github.com/devcontainers/feature-starter>,
  <https://github.com/devcontainers/template-starter>
- Third-party feature collection prior art:
  <https://github.com/stacit-ai/devcontainer-features>
