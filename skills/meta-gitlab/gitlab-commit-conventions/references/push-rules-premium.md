# Push rules: server-side enforcement (Premium/Ultimate)

Load condition: the user wants hard enforcement — rejecting
non-compliant commits at push time — and the instance is
Premium/Ultimate. On Free, CI validation plus "Pipelines must succeed"
is the strongest available gate.

Push rules run server-side on every push, before CI: a rejected push
never lands, which also means contributors see the error in their git
client, not in a pipeline.

## Set the commit-message rule

Project Settings > Repository > Push rules ("Require expression in
commit messages"), or via the API:

```bash
glab api --method PUT projects/:fullpath/push_rule \
  -f commit_message_regex='^(build|chore|ci|docs|feat|fix|perf|refactor|revert|style|test)(\([^)]+\))?!?: .{1,72}$'
```

(`POST projects/:id/push_rule` creates it when none exists; GitLab
returns 404 for push-rule endpoints on unlicensed tiers.)

## Limits of the regex

- One expression, applied to the **first line** of every commit — it
  can enforce shape and types, but not scope sets per path, body
  wrapping, or trailer presence per type. Keep the committed validator
  and CI job as the complete check; the push rule is a coarse outer
  wall.
- Merge commits GitLab itself creates are exempted automatically;
  revert/fixup flows are not — mirror the validator's exemptions in the
  regex (`^(Merge |Revert |fixup!|squash!)|...`) or contributors cannot
  push them.
- Test the expression on recent history before enabling:
  `git log --format=%s -n 50 | grep -Ev 'REGEX'` lists the titles the
  rule would reject.
