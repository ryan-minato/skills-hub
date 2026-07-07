# CI checks and failed-job logs

Goal: get from a failing PR to the relevant error lines without flooding
the context window. Use the column (MCP or gh) chosen in "Choose your
path"; `O/R` and `N` come from "Identify the repository".

## 1. Identify the failing checks

- MCP: the capability that reads a PR's check runs.
- gh: `gh pr checks N -R O/R --json name,state,bucket,link,workflow` —
  the failing checks are the rows with `bucket` = `fail`.

## 2. Map each failing check to its Actions run

- Preferred: the check's `link` URL contains the ids directly, in the form
  `https://github.com/O/R/actions/runs/RUN_ID/job/JOB_ID`. Extract
  `RUN_ID` and `JOB_ID` from it.
- If the link is missing or is not an Actions URL, list recent runs on the
  PR's branch:
  `gh run list -R O/R --branch BRANCH --limit 10 --json databaseId,workflowName,conclusion`
  and pick the run whose `workflowName` matches the failing check's
  `workflow` and whose `conclusion` is `failure`; its `databaseId` is
  `RUN_ID`.

## 3. Fetch failed logs only

- MCP: the job-log capability, in one of two shapes — all failed jobs in
  the run (run id + failed-only + a tail limit of about 100 lines), or a
  single job (job id + the same tail limit). Never combine a single-job id
  with the failed-only switch.
- gh: `gh run view RUN_ID -R O/R --log-failed | tail -n 100` for all
  failed jobs in the run, or
  `gh run view -R O/R --job JOB_ID --log-failed | tail -n 100` for one
  job. gh prefixes each log line with the job and step name, so
  attribution can be read straight off the tail.

## Hard rule

Never fetch a full run log: full logs can be megabytes and will drown the
context window. Always request failed-only output and tail it — start
with 100 lines and raise the tail (for example to 300) only when the
actual error is not within it.

Done when: the failing step's error lines are quoted and attributed to
their job and step.
