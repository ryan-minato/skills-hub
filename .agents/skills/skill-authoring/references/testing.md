# Test-driven skill authoring

Load this only after the isolated-subagent gate in SKILL.md passes. It tests
the skill's invocation and effect before static validation; a clean lint result
alone does not prove the skill adds value.

## 1. Create test worktrees only when testing

The current issue worktree is the authoring worktree: design, edit, stage, and
commit there. Do not create a test worktree until immediately before a test
run.

At the start of each test run, create detached disposable worktrees and
separate output directories:

- **Candidate:** create it at the current `HEAD`, then transfer a complete
  temporary snapshot of the intended current changes. Include tracked staged
  and unstaged changes plus intended untracked files; keep the snapshot patch
  and file copies outside version control. Expose the target through normal
  skill discovery.
- **No skill:** create it from the same candidate snapshot, then make the
  target skill unavailable before the solver starts.

Give every writing subagent its own test worktree and output directory. Never
run tests, generated harnesses, or test-driven edits in the current issue
worktree, and never let concurrent writers share a test worktree. If the
required isolation or complete candidate snapshot cannot be created, skip the
behavioral tests and record the blocker in the Linear milestone comment and
handoff.
Never explicitly tell a trigger-test solver to use the target skill. If normal
discovery cannot expose the candidate and hide it from the no-skill baseline,
skip the trigger tests and record why.

## 2. Make the tests red

Append the same neutral instrumentation to every solver prompt, without naming
the target skill in the instrumentation:

```text
End your answer with SKILLS_LOADED: <comma-separated skill names or none>.
List only skills whose bodies you actually loaded; do not load a skill merely
to report it.
```

Before editing the skill, write:

1. At least three realistic prompts that should trigger the description and
   three near-misses that share vocabulary but should not trigger it. Include
   direct and indirect phrasing, with the expected load decision for each.
2. Two or three representative outcome tasks and a rubric of observable
   requirements. Mark failures that count as critical regressions.
3. The no-skill baseline outputs. Keep task text, inputs, model capability,
   tools, and limits equal across solvers.

The no-skill baseline must expose a meaningful gap. If it already satisfies
every requirement, revise the cases or stop: the proposed change has not shown
value.

## 3. Make the tests green

Apply the smallest general skill change that should close the observed gap,
then test the candidate:

- **Trigger accuracy:** use a fresh clean-context subagent for each prompt and
  read its final `SKILLS_LOADED` line. The target name present means loaded;
  absent means not loaded. A missing or malformed line, or a reported skill
  unavailable in that solver's worktree, invalidates the attempt. Retry an
  invalid or unexpected result up to three total attempts. A valid case passes
  only when at least two attempts match the expectation; if three attempts
  yield no valid report, skip that case and record inadequate observability.
- **Outcome quality:** run candidate and no-skill solvers in parallel in their
  test worktrees. Retain every output, including failures. A candidate output
  is valid only when its report includes the target; a no-skill output
  reporting the unavailable target is invalid. Apply the same three-attempt
  limit, then skip and record if a valid output cannot be obtained.
- **Independent grading:** anonymize solver identities and give the outputs,
  rubric, and critical requirements to a clean-context subagent that produced
  none of the answers. Require a score and concrete evidence for every item.
  Accept the candidate only when it has no critical regression and its
  aggregate score is strictly higher than the no-skill baseline.

A tie is not improvement. On failure, fix the underlying instruction rather
than patching one test prompt, then rerun the complete affected comparison.

## 4. Clean up and report

Record the cases, rubric, results, scores, evidence, and any skipped test with
its reason in the Linear milestone comment and handoff. Remove every detached
candidate and no-skill test worktree, snapshot, harness, fixture, and
evaluation output. Keep the current issue worktree for the remaining commit
and PR workflow, and confirm its `git status` shows only the intended repository
changes.
