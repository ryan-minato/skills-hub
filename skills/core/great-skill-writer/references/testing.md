# Behavioral test-driven skill authoring

Load this only when SKILL.md confirms clean-context subagents are available.
Use a disposable detached candidate worktree for each test run when possible.
Never let a test edit the authoring worktree.

## 1. Design acceptance tests before editing

Before editing, write:

1. At least three realistic prompts that should trigger the description and
   three near-misses that share vocabulary but should not. Include direct and
   indirect phrasing, with the expected load decision for each.
2. Two or three representative outcome tasks and a rubric of observable
   requirements. Mark critical failures and declare the aggregate score needed
   to pass before seeing candidate output.

Keep task text, inputs, model capability, tools, and limits equal across every
solver that will run them.

Use framework-native conversation history or skill-load telemetry to determine
whether a solver loaded the target. If neither is available, append this neutral
instrumentation to every solver prompt without naming the target skill:

```text
End your answer with SKILLS_LOADED: <comma-separated skill names or none>.
List only skills whose bodies you actually loaded; do not load a skill merely
to report it.
```

## 2. Isolate every test run when possible

Create worktrees only immediately before a test run, with outputs outside
version control:

- **Candidate:** detach at the current `HEAD`, then transfer a complete
  temporary snapshot of intended tracked staged and unstaged changes plus
  intended untracked files.

Give every writing solver its own worktree and output directory. Never let
concurrent writers share a worktree. If a worktree or complete candidate
snapshot is unavailable, use the best available environment, keep generated
material outside version control, and record the isolation degradation.
Never explicitly tell a trigger-test solver to use the target skill.

## 3. Evaluate the candidate

Apply the smallest general skill change that should close the observed gap,
then test the candidate:

- **Trigger accuracy:** use a fresh clean-context subagent for every prompt.
  Observe target loading through framework-native history or telemetry; when
  unavailable, read its final `SKILLS_LOADED` line. The target name present
  means loaded; absent means not loaded. A missing observation or malformed
  fallback report invalidates the attempt. Retry an invalid or unexpected
  result up to three total attempts. A valid case passes only when at least two
  attempts match the expectation; if three attempts yield no valid observation,
  skip that case and report inadequate observability.
- **Outcome quality:** run a candidate solver for every representative task in
  its own test worktree. Retain every output, including failures. An output is
  valid only when the selected observation mechanism shows the target loaded.
  Apply the same three-attempt limit, then skip and report if a valid output
  cannot be obtained.
- **Independent grading:** anonymize solver identities and give the outputs,
  rubric, and critical requirements to a clean-context subagent that produced
  none of the answers. Require a score and concrete evidence for every item.
  Accept the candidate only when it has no critical failure and its aggregate
  score meets the threshold declared before the run.

On failure, fix the underlying instruction rather than patching one prompt,
then rerun the complete affected evaluation.

## 4. Clean up and report

Record prompts, observation method, rubric, results, scores, evidence, every
isolation degradation, and any skipped test with its reason. Remove every
candidate test worktree, snapshot, fixture, harness, and evaluation output.
Confirm the authoring worktree contains only intended changes before continuing.
