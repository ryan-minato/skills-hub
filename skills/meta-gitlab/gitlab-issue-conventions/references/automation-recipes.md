# Issue automation beyond template quick actions

The templates' embedded quick actions are the primary automation: zero
infrastructure, Free tier, any host. GitLab has **no issue-event
pipelines** — CI runs on code events only — so event-driven issue
automation would need webhooks or a bot service, which is out of this
skill's scope. What fits inside the project itself is scheduled
sweeps.

## Token reality (read first)

`CI_JOB_TOKEN` cannot call the issues REST endpoints. A sweep job needs
a real token in a **masked** CI/CD variable (Settings > CI/CD >
Variables), named `TRIAGE_TOKEN` below:

- Self-managed (any tier) and gitlab.com Premium: a **project access
  token** with the `api` scope — smallest blast radius.
- gitlab.com Free: project access tokens are unavailable — use a PAT
  from a dedicated bot user instead of a personal account.

All recipes use `${CI_API_V4_URL}` and `${CI_PROJECT_ID}` so they are
host-agnostic — never hardcode an instance URL.

## Scheduled triage sweep

Labels every unlabeled issue `status::needs-triage` so nothing escapes
the triage queue. Add to `.gitlab-ci.yml`, then create a schedule
(Build > Pipeline schedules, e.g. daily):

```yaml
triage-sweep:
  rules:
    - if: $CI_PIPELINE_SOURCE == "schedule"
  script:
    - |
      ids=$(curl -sS --header "PRIVATE-TOKEN: $TRIAGE_TOKEN" \
        "${CI_API_V4_URL}/projects/${CI_PROJECT_ID}/issues?labels=None&state=opened&per_page=100" \
        | python3 -c 'import json,sys; print("\n".join(str(i["iid"]) for i in json.load(sys.stdin)))')
    - |
      for iid in $ids; do
        curl -sS --request PUT --header "PRIVATE-TOKEN: $TRIAGE_TOKEN" \
          "${CI_API_V4_URL}/projects/${CI_PROJECT_ID}/issues/${iid}?add_labels=status::needs-triage" > /dev/null
        echo "labeled #$iid"
      done
```

Uses the runner's default image; needs only `curl` and `python3` (swap
the JSON extraction for `jq` if the image has it).

## Stale sweep (variant)

Same skeleton, different query and action: list issues with
`updated_before=<ISO date>` and `state=opened`, then either comment a
nudge (`POST .../issues/:iid/notes`) or apply a `status::stale` label.
Keep destructive actions (auto-close) out unless the user explicitly
asks; closing other people's issues by cron is a policy decision.

## Supply-chain rule

GitLab has no third-party actions marketplace; every recipe here is
plain CI YAML calling the instance's own API. Keep it that way: no
external container images or remote scripts in shipped automation — the
runner-default image plus `curl`/`python3` covers these jobs.
