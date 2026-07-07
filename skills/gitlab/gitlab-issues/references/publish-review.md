# Pre-publish review procedure

Independent review of content that is about to be published on GitLab.
Input: the scratch directory assembled by the Pre-publish gate (title,
body, comments, and for MRs `commits.txt` and `diff.patch`, plus any
attachments). Output: findings and a binding verdict line.

## 1. Choose the review mode

| Your environment | Mode |
|---|---|
| You can dispatch a subagent that starts with its own clean context (for example Claude Code's Task tool, opencode subagents) | **Clean-context review** — preferred |
| No subagent support (Codex CLI, Gemini CLI, Antigravity, and others) | **File-only fallback** |

## 2. Clean-context review

Dispatch one subagent whose entire prompt is the review prompt below with
`<DIR>` replaced by the scratch directory path. Add nothing else to the
prompt: extra context about what you "meant" defeats the independence of
the review. The subagent's last output line is the verdict.

## 3. File-only fallback

1. This procedure pairs with `sensitivity-check` for scanning. If it is
   not installed, install it from https://github.com/ryan-minato/skills.git:

       npx skills add ryan-minato/skills --skill sensitivity-check

   Run its scanners over every file in the directory. If it cannot be
   installed, continue — the checklist below still applies.
2. Re-read every file in the directory from disk, top to bottom, applying
   the reviewer checklist. Judge only what the files contain, never what
   you remember intending to write.
3. Produce findings and the verdict in the reviewer output format, adding
   the line `Review mode: file-only (not clean-context)` directly above
   the verdict.

## Review prompt

```
Review the files in <DIR> before they are published on GitLab. Everything
in them will become visible to everyone who can view the project — on a
public project, the entire internet. You have no other context; judge only
what the files contain.

1. List the files. If the directory is empty or any file is unreadable,
   end with SAFE TO PUBLISH: NO.
2. Check every file, line by line, for:
   - Secrets: tokens, API keys, private keys, passwords, connection
     strings — including inside diff context lines and commit messages.
   - PII: real personal names, emails, phone numbers, addresses.
     Placeholders such as name@example.com are acceptable.
   - Internal identifiers: hostnames, internal URLs, ticket-system links,
     project codenames — including any branch name recorded in the files.
   - Quick actions: any line beginning with `/` (such as /close, /assign,
     /label) executes as a command on GitLab — flag any that are not
     clearly intended.
   - Unintended content: files in the diff unrelated to the stated change,
     lockfile or editor-config churn, attachments or screenshots showing
     tokens, emails, or internal systems.
   - Tone: wording a maintainer would regret publishing.
3. Report one line per finding: file, short excerpt with secret values
   masked, category, required fix. If there are none, say "No findings."
4. Your last output line must be exactly `SAFE TO PUBLISH: YES` or
   `SAFE TO PUBLISH: NO`. Any finding of secrets, PII, or internal
   identifiers means NO.
```

## Verdict handling

- Treat any review whose last line is not exactly `SAFE TO PUBLISH: YES`
  as NO.
- On NO: fix every finding, rebuild the scratch directory from the fixed
  content, and review again. Published content must be byte-identical to
  the reviewed content.
- Record the verdict line verbatim in your session summary.
