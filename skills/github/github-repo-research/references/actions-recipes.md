# Actions recipes beyond the core table

Same column discipline as SKILL.md: MCP tool if the GitHub MCP server is
connected, else the gh command. Substitute `O/R`, `RUN_ID`, and names.

## Artifacts

| Task | MCP tool | gh |
|---|---|---|
| List a run's artifacts | `actions_list` method=`list_workflow_run_artifacts` | `gh api repos/O/R/actions/runs/RUN_ID/artifacts` |
| Download one artifact | — (no MCP download; use gh) | `gh run download RUN_ID -R O/R -n ARTIFACT_NAME -D DIR` |

Download into a scratch directory and read only the files the task needs;
artifacts can be large.

## Run timing and usage

| Task | MCP tool | gh |
|---|---|---|
| Run timing/usage | `actions_get` method=`get_workflow_run_usage` | `gh api repos/O/R/actions/runs/RUN_ID/timing` |

## Filtered run listings and workflows

| Task | MCP tool | gh |
|---|---|---|
| Filtered run listing | `actions_list` method=`list_workflow_runs` — the workflow id or file name goes in `resource_id`; branch/status/event/actor filters go inside the `workflow_runs_filter` object (there are no bare `workflow_id`/`branch`/`status` parameters) | `gh run list -R O/R --workflow NAME --branch BR --status failure --limit 20 --json databaseId,displayTitle,headBranch,status,conclusion,createdAt` |
| List workflows | `actions_list` method=`list_workflows` | `gh workflow list -R O/R` |

`--workflow` accepts the workflow name, its file name (`ci.yml`), or its
id from `gh workflow list`.

## Watch a live run

Only when the user explicitly asks to wait for a run — this blocks until
the run finishes:

```bash
gh run watch RUN_ID -R O/R --exit-status
```

`--exit-status` makes the command exit non-zero if the run fails, so the
outcome is machine-readable.

## Rerun / cancel — out of scope

Rerunning or canceling a run is a write operation, outside this skill's
read-only scope. If asked, confirm with the user first and then use
`gh run rerun RUN_ID -R O/R` (add `--failed` to rerun only failed jobs)
or `gh run cancel RUN_ID -R O/R` explicitly at their direction.
