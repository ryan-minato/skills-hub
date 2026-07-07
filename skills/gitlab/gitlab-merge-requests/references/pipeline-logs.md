# Reading a failing MR pipeline

Three steps; never fetch a full trace unbounded — job logs run to
megabytes and flood the context.

## 1. Identify the failing jobs

| glab | MCP (min GitLab) |
|---|---|
| `glab ci get --merge-request N -R G/P -s failed -d -F json` | `get_merge_request_pipelines` (18.4), then `get_pipeline_jobs` (18.4) |

`-s failed` limits the listing to failed jobs; `-d` adds job details.
Record each failing job's `id`, `name`, `stage`, and `failure_reason`.

## 2. Fetch only the tail of each failed log

The failure is almost always in the last lines. For a **finished** job:

```bash
glab ci trace JOB_ID -R G/P | tail -n 100
```

`glab ci trace` follows running jobs forever — check the job is finished
first (step 1 shows its status). Equivalent without trace:

```bash
glab api "projects/:fullpath/jobs/JOB_ID/trace" | tail -n 100
```

MCP alternative: `get_job_log` (19.1) — it has **no tail parameter** and
returns the whole trace; prefer the glab column for logs, and use the MCP
tool only when glab is unavailable and the log is known to be small.

## 3. Quote the error

Extract the failing command and its error lines from the tail; raise the
tail to 300 only when the error is not in the last 100 lines.

Done when: the failing job is named and its error lines are quoted.
