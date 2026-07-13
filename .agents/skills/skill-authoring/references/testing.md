# Test-driven skill authoring

Load this only after the subagent gate in SKILL.md passes. It tests
the skill's invocation and effect; a clean lint result alone does not prove the
skill adds value.

## 1. Create test worktrees when possible

The current issue worktree is the authoring worktree: design, edit, stage, and
commit there. Do not create a test worktree until immediately before a test
run.

At the start of each test run, try to create detached disposable candidate
worktrees and separate output directories:

- **Candidate:** create it at the current `HEAD`, then transfer a complete
  temporary snapshot of the intended current changes. Include tracked staged
  and unstaged changes plus intended untracked files; keep the snapshot patch
  and file copies outside version control.

Give every writing subagent its own test worktree and output directory when
available. Never let concurrent writers share a worktree. If isolation or a
complete candidate snapshot is unavailable, use the best available environment,
keep generated material outside version control, and record the isolation
degradation. Never explicitly tell a trigger-test solver to use the target
skill.

## 2. Define acceptance tests before editing

Use framework-native conversation history or skill-load telemetry to determine
whether a solver loaded the target. If neither is available, append this neutral
instrumentation to every solver prompt without naming the target skill:

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
   requirements. Mark critical failures and declare the aggregate score needed
   to pass before seeing candidate output.

## 3. Make the tests green

Apply the smallest general skill change that should close the observed gap,
then test the candidate:

- **Trigger accuracy:** use a fresh clean-context subagent for each prompt.
  Observe target loading through framework-native history or telemetry; when
  unavailable, read its final `SKILLS_LOADED` line. The target name present
  means loaded; absent means not loaded. A missing observation or malformed
  fallback report invalidates the attempt. Retry an invalid or unexpected
  result up to three total attempts. A valid case passes only when at least two
  attempts match the expectation; if three attempts yield no valid observation,
  skip that case and record inadequate observability.
- **Outcome quality:** run a candidate solver for every representative task in
  its own test worktree when possible. Retain every output, including failures.
  An output is valid only when the selected observation mechanism shows the
  target loaded. Apply the same three-attempt limit, then skip and record if a
  valid output cannot be obtained.
- **Independent grading:** anonymize solver identities and give the outputs,
  rubric, and critical requirements to a clean-context subagent that produced
  none of the answers. Require a score and concrete evidence for every item.
  Accept the candidate only when it has no critical failure and its aggregate
  score meets the threshold declared before the run.

On failure, fix the underlying instruction rather than patching one test
prompt, then rerun the complete affected evaluation.

## 4. Clean up and report

Record the cases, observation method, rubric, results, scores, evidence, every
isolation degradation, and any skipped test with its reason in the Linear
milestone comment and handoff. Remove every detached candidate test worktree,
snapshot, harness, fixture, and evaluation output. Keep the current issue
worktree for the remaining commit and PR workflow, and confirm its `git status`
shows only the intended repository changes.
