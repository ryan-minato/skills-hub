# Release automation recipes

Load condition: the user wants automation beyond the tag check —
creating releases from tag pipelines or attaching build artifacts.

The hard constraint: **GitLab has no draft releases.** A release a
pipeline creates is public the moment the job runs, notes and all. So
CI-created releases are only appropriate when the notes are fully
mechanical (generated from Changelog trailers, accepted as-is by policy,
with the user's explicit sign-off on that policy); anything needing
curation stays with the generated release skill, whose gate runs before
create.

## Create a release from a tag pipeline

`release-cli` is GitLab's own tool, preinstalled in the
`registry.gitlab.com/gitlab-org/release-cli` image; the `release:`
keyword drives it. Appended after the tag-check job (`needs:` makes it
run only on validated tags):

```yaml
release-create:
  image: registry.gitlab.com/gitlab-org/release-cli:latest
  needs: ["tag-check"]
  rules:
    - if: $CI_COMMIT_TAG =~ /^v/
  script:
    - echo "Creating release for $CI_COMMIT_TAG"
  release:
    tag_name: $CI_COMMIT_TAG
    name: $CI_COMMIT_TAG
    description: "See the changelog for $CI_COMMIT_TAG."
```

The `description:` here is the published text — keep it mechanical (a
pointer or trailer-generated content), never a place CI composes prose.
`release:` runs with the job's own `CI_JOB_TOKEN`; no extra secret is
needed on the Free tier.

## Attach build artifacts

Build in earlier jobs, then link via `release:assets:links` (URLs to
job artifacts or the generic package registry):

```yaml
  release:
    tag_name: $CI_COMMIT_TAG
    name: $CI_COMMIT_TAG
    description: "See the changelog for $CI_COMMIT_TAG."
    assets:
      links:
        - name: "binary (linux amd64)"
          url: "${CI_PROJECT_URL}/-/jobs/artifacts/${CI_COMMIT_TAG}/raw/dist/app?job=build"
          link_type: package
```

Prefer the generic package registry for durable artifacts
(`gitlab-releases` covers the upload path); job-artifact URLs expire
with the artifacts.

## Why not third-party release bots

Semantic-release and similar toolchains auto-publish based on commit
analysis — on GitLab that means unreviewed public notes by design. They
are a choice a user may explicitly make (record the opt-in, pin
versions); they are not this skill's default, which keeps release
publication behind the generated skill's gate.
