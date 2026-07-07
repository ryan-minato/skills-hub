# Pipeline recipes — explicit writes and long-tail reads

The only mutating operations in this skill; run them solely on the
user's explicit request, and report what was triggered. glab only — the
MCP pipeline-management capability (18.10) covers run/retry/cancel where
present, but the glab column stays the recommended path.

## Retry, cancel, run

```bash
glab ci retry JOB_ID -R G/P             # retry one job (or by job name with -p/-b)
glab ci cancel pipeline ID -R G/P       # cancel a pipeline
glab ci cancel job JOB_ID -R G/P        # cancel one job
glab ci run -R G/P -b BRANCH            # start a new pipeline for a branch
```

## Lint CI configuration

Validates `.gitlab-ci.yml` against the instance (catches include and
rule errors local YAML parsing cannot):

```bash
glab ci lint [PATH] -R G/P
```

## Artifacts

```bash
glab ci artifact REF JOB_NAME -R G/P    # download the last pipeline's artifacts for a ref
```

For a specific job id instead of a ref/name pair:

```bash
glab api "projects/:fullpath/jobs/JOB_ID/artifacts" > artifacts.zip
```

## Pipeline variables (Maintainer only)

```bash
glab ci get -R G/P -p ID --with-variables
```
