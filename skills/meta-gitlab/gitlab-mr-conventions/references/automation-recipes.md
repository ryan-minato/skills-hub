# MR automation beyond the shipped checklist job

GitLab has no third-party actions marketplace; every recipe here is
plain CI YAML plus the instance's own API. Keep shipped automation free
of external images and remote scripts — the runner-default image with
`sh`/`grep`/`curl`/`python3` covers all of it. Recipes that mutate the
MR need a token: a **project access token** with `api` scope in a masked
CI/CD variable (Free on self-managed, Premium on gitlab.com; a
dedicated bot user's PAT is the gitlab.com-Free alternative). All
recipes use `${CI_API_V4_URL}` and predefined variables — never a
hardcoded host.

## Extra checks inside the existing job (tokenless)

Append to the `mr-checklist` script; both read only predefined
variables.

Linked-issue enforcement:

```sh
if ! printf '%s\n' "$CI_MERGE_REQUEST_DESCRIPTION" | grep -Eq '(Closes|Fixes|Resolves) #[0-9]+'; then
  echo "MR description must link its issue (Closes #N)." >&2
  status=1
fi
```

Conventional-commit title check:

```sh
if ! printf '%s' "$CI_MERGE_REQUEST_TITLE" | grep -Eq '^(Draft: )?(feat|fix|docs|refactor|perf|test|build|ci|chore)(\([a-z0-9., -]+\))?!?: '; then
  echo "MR title must follow Conventional Commits." >&2
  status=1
fi
```

## Path-based auto-labeling (token required)

An MR-pipeline job that labels the MR from the changed paths:

```yaml
mr-autolabel:
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
  script:
    - |
      paths=$(curl -sS --header "PRIVATE-TOKEN: $AUTOMATION_TOKEN" \
        "${CI_API_V4_URL}/projects/${CI_PROJECT_ID}/merge_requests/${CI_MERGE_REQUEST_IID}/diffs?per_page=100" \
        | python3 -c 'import json,sys; print("\n".join(d["new_path"] for d in json.load(sys.stdin)))')
      labels=""
      case "$paths" in *docs/*) labels="type::docs" ;; esac
      # add more path → label cases here
      if [ -n "$labels" ]; then
        curl -sS --request PUT --header "PRIVATE-TOKEN: $AUTOMATION_TOKEN" \
          "${CI_API_V4_URL}/projects/${CI_PROJECT_ID}/merge_requests/${CI_MERGE_REQUEST_IID}?add_labels=${labels}" > /dev/null
        echo "applied: $labels"
      fi
```

Fork caveat: MR pipelines for fork MRs cannot see the parent project's
masked variables by default — the job silently no-ops there, which is
the safe behavior; do not weaken variable protection to "fix" it.

## Stale-MR sweep

Scheduled pipeline (`rules: - if: $CI_PIPELINE_SOURCE == "schedule"`)
listing `merge_requests?state=opened&updated_before=<ISO>` and posting a
nudge note per result. Keep auto-close out unless the user explicitly
asks.

## Avoiding duplicate pipelines (apply only with consent)

If the project runs classic branch pipelines (jobs without `rules:`),
adding MR-event rules makes every push spawn both a branch and an MR
pipeline. The documented switch-over — run MR pipelines when an MR is
open, branch pipelines otherwise — is a `workflow:rules` block at the
top level:

```yaml
workflow:
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    - if: $CI_COMMIT_BRANCH && $CI_OPEN_MERGE_REQUESTS
      when: never
    - if: $CI_COMMIT_BRANCH
```

This changes when EVERY job runs. Offer it, explain the effect, and add
it only when the user agrees — never apply it unasked.
