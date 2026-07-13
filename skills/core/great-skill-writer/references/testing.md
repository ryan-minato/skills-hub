# Behavioral test-driven skill authoring

Load this only after the subagent-support gate in SKILL.md passes. Use the
authoring worktree for intended edits and disposable detached git worktrees for
every test run. Never let a test edit the authoring worktree.

## 1. Design the red tests

Before editing, write:

1. At least three realistic prompts that should trigger the description and
   three near-misses that share vocabulary but should not. Include direct and
   indirect phrasing, with the expected load decision for each.
2. Two or three representative outcome tasks and a rubric of observable
   requirements. Mark failures that count as critical regressions.

Keep task text, inputs, model capability, tools, and limits equal across every
solver that will run them.

Append the same neutral instrumentation to every solver prompt, without naming
the target skill in the instrumentation:

```text
End your answer with SKILLS_LOADED: <comma-separated skill names or none>.
List only skills whose bodies you actually loaded; do not load a skill merely
to report it.
```

## 2. Isolate every test run

Create worktrees only immediately before a test run, with outputs outside
version control:

- **Candidate:** detach at the current `HEAD`, then transfer a complete
  temporary snapshot of intended tracked staged and unstaged changes plus
  intended untracked files. Expose the target through the agent's normal skill
  discovery.
- **No skill:** create it from the same candidate snapshot and make the target
  skill unavailable before that solver starts.

Give every writing solver its own worktree and output directory. Never let
concurrent writers share a worktree. If isolation, skill exposure, or the
candidate snapshot is incomplete, skip the behavioral tests and report the
specific blocker instead of falling back to the authoring worktree.
Never explicitly tell a trigger-test solver to use the target skill. If normal
discovery cannot expose the candidate and hide it from the no-skill baseline,
skip the trigger tests rather than replacing them with explicit invocation.

## 3. Establish the no-skill baseline

Before editing, run the no-skill solver in its test worktree. The baseline
must expose a meaningful gap. If it already satisfies every
requirement, revise the cases or stop: the proposed change has not shown value.

Remove the no-skill worktrees after recording their outputs. Recreate fresh
ones for the candidate comparison; do not reuse a solver context.

## 4. Make the tests green

Apply the smallest general skill change that should close the observed gap,
then test the candidate:

- **Trigger accuracy:** use a fresh clean-context subagent for every prompt and
  read its final `SKILLS_LOADED` line. The target name present means loaded;
  absent means not loaded. A missing or malformed line, or a reported skill
  unavailable in that solver's worktree, invalidates the attempt. Retry an
  invalid or unexpected result up to three total attempts. A valid case passes
  only when at least two attempts match the expectation; if three attempts
  yield no valid report, skip that case and report inadequate observability.
- **Outcome quality:** run candidate and no-skill solvers in parallel. Retain
  every output, including failures. A candidate output is valid only when its
  report includes the target; a no-skill output reporting the unavailable
  target is invalid. Apply the same three-attempt limit, then skip and report
  if a valid output cannot be obtained.
- **Independent grading:** anonymize solver identities and give the outputs,
  rubric, and critical requirements to a clean-context subagent that produced
  none of the answers. Require a score and concrete evidence for every item.
  Accept the candidate only when it has no critical regression and its
  aggregate score is strictly higher than the no-skill baseline.

A tie is not improvement. On failure, fix the underlying instruction rather
than patching one prompt, then rerun the complete affected comparison.

## 5. Clean up and report

Record prompts, rubric, results, scores, evidence, and any skipped test with
its reason. Remove every candidate and no-skill test worktree, snapshot,
fixture, harness, and evaluation output. Confirm the authoring worktree contains
only intended changes before continuing.
