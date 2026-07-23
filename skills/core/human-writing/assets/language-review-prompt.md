# Language-and-wording review prompt template

Structure-only template: build the specifics fresh each time you use it —
never send it unfilled and never reuse a previously filled copy.

1. Fill {{language}} and {{reader profile and register}} from the piece
   definition, and fill the cautions slot from the `references/` file matching
   the text's language (`english.md`, `chinese.md`, or `japanese.md`).
2. Send to a subagent with a separate, clean context. Provide the text and the
   filled slots only — no drafting history and no list of edits already made.
   Without clean-context subagents, review the text yourself against the same
   questions instead.

---

You are a careful native reader of {{language}}, reviewing a text written for
the following audience: {{reader profile and register — who the readers are and
how formally the piece should speak to them}}.

Judge only the language: fluency, grammar, and word choice. Content, structure,
and argument are other reviewers' jobs.

The text:

{{full text}}

Language-specific cautions to watch for:

{{wording and grammar cautions for this language, drawn from the matching
reference file: unnatural constructions, register pitfalls, punctuation
conventions}}

Assess:

1. Fluency — sentences that stumble, tangle, or read as translated from
   another language; rhythm that no native writer would produce. Quote each.
2. Word choice — every word or phrase these readers would not actually use:
   obscure, archaic, or literary picks where a common word exists; register
   mismatches (too stiff or too casual for the audience); terms the audience
   does not share, used without need. For each, say what kind of word belongs
   there instead — name the common alternative, not a rarer synonym.
3. Grammar and usage — errors and questionable usage per this language's
   norms, including punctuation conventions.
4. What already reads well — name the passages that are fluent and natural as
   they stand, so they are not edited without cause.

For every finding: the quoted passage, why it fails for these readers, and the
kind of fix. Do not rewrite the piece; report findings only.
