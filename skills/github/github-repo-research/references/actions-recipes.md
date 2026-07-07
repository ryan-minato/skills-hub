# Actions recipes beyond the core table

Same column discipline as SKILL.md: the MCP tool whose description matches
the capability if the GitHub MCP server is connected, else the gh command.
Substitute `O/R`, `RUN_ID`, and names.

## Artifacts

| Task | MCP capability | gh |
|---|---|---|
| List a run's artifacts | list a run's artifacts | `gh api repos/O/R/actions/runs/RUN_ID/artifacts` |
| Download one artifact | — (no MCP download; use gh) | `gh run download RUN_ID -R O/R -n ARTIFACT_NAME -D DIR` |

Download into a scratch directory and read only the files the task needs;
artifacts can be large.

## Run timing and usage

| Task | MCP capability | gh |
|---|---|---|
| Run timing/usage | read a run's timing/usage | `gh api repos/O/R/actions/runs/RUN_ID/timing` |

## Filtered run listings and workflows

| Task | MCP capability | gh |
|---|---|---|
| Filtered run listing | list workflow runs — check the tool's own description for where the workflow id and the branch/status/event/actor filters go; they are usually nested in a filter object rather than bare parameters | `gh run list -R O/R --workflow NAME --branch BR --status failure --limit 20 --json databaseId,displayTitle,headBranch,status,conclusion,createdAt` |
| List workflows | list workflows | `gh workflow list -R O/R` |

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
