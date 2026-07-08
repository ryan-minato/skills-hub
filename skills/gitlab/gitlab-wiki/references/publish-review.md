# Pre-publish review procedure

Independent review of a GitLab wiki publishing surface. Input: the scratch
directory assembled by the Pre-publish gate: page titles and bodies,
attachments, changed wiki files, `commits.txt` from `git log
origin/HEAD..HEAD --format=full`, and `diff.patch` from `git diff
origin/HEAD..HEAD` when using the git path. Output: findings and a binding
verdict line.

## 1. Choose the review mode

| Your environment | Mode |
|---|---|
| You can dispatch a subagent that starts with its own clean context (for example Claude Code's Task tool, opencode subagents) | **Clean-context review** — preferred |
| No subagent support (Codex CLI, Gemini CLI, Antigravity, and others) | **File-only fallback** |

## 2. Clean-context review

Dispatch one subagent whose entire prompt is the review prompt below with
`<DIR>` replaced by the scratch directory path. Add nothing else to the
prompt: extra context about what you meant defeats the independence of the
review. The subagent's last output line is the verdict.

## 3. File-only fallback

Re-read every file in the directory from disk, top to bottom, applying the
reviewer checklist. Judge only what the files contain, never what you
remember intending to publish. Produce findings and the verdict in the
reviewer output format, adding the line `Review mode: file-only (not
clean-context)` directly above the verdict.

## Review prompt

```
Review the files in <DIR> before they are published to a GitLab wiki.
Everything in them will become visible to everyone who can view the wiki —
on a public project, the entire internet. Wiki git pushes also publish every
commit message and every committed file. You have no other context; judge
only what the files contain.

1. List the files. If the directory is empty, expected wiki content is
   missing, or any file is unreadable, end with SAFE TO PUBLISH: NO. For a
   wiki git push, `commits.txt` and `diff.patch` must both be present.
2. Check every file, line by line, for:
   - Secrets and credentials: tokens, API keys, private keys, passwords,
     connection strings, signing material, cookies, session IDs.
   - Personal data: real personal names, emails, phone numbers, addresses,
     account identifiers, screenshots or attachments exposing people.
     Placeholders such as name@example.com are acceptable.
   - Internal-only context: hostnames, internal URLs, ticket-system links,
     project codenames, unreleased plans, private branch names.
   - Quick actions: any line beginning with `/` (such as /close, /assign,
     /label) can execute as a command when sent through the API — flag any
     that are not clearly intended.
   - Unintended content: unrelated pages, generated output, local notes,
     lockfiles, attachments, or screenshots that should not be published.
   - Quality: confusing, hostile, speculative, stale, or regret-worthy
     wording in page content, commit messages, or visible diff text.
3. Report one line per finding: file, short excerpt with secret values
   masked, category, required fix. If there are none, say "No findings."
4. Your last output line must be exactly `SAFE TO PUBLISH: YES` or
   `SAFE TO PUBLISH: NO`. Any finding of secrets, credentials, personal
   data, or internal-only context means NO.
```

## Verdict handling

- Treat any review whose last line is not exactly `SAFE TO PUBLISH: YES`
  as NO.
- On NO: fix every finding, rebuild the scratch directory from the fixed
  content, and review again. Published content must be byte-identical to
  the reviewed content.
- Record the verdict line verbatim in your session summary.
