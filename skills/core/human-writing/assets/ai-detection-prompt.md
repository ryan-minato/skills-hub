# AI-writing detection prompt template

Structure-only template: build the specifics fresh each time you use it —
never send it unfilled and never reuse a previously filled copy.

1. Read the "Failure modes to avoid" digest in this skill's SKILL.md and the
   `references/` file matching the language the text is written in
   (`english.md`, `chinese.md`, or `japanese.md`).
2. Fill every {{slot}} below with concrete patterns and example phrases for
   that language only — the detector should not wade through other
   languages' tells.
3. Send to a subagent with a separate, clean context. Provide only the
   text — no authorship information, no drafting history, no hint of what
   answer is expected. Without clean-context subagents, skip this pass; the
   digest and the language reference already serve as the self-review
   checklist.

---

Assess whether the following text reads as AI-generated. Judge by the
accumulation of patterns and your own overall impression — a single match
means little; several stacking up in one passage means a lot. Polished or
formal writing is not, by itself, AI writing: do not flag text merely for
being correct and well organized.

The text:

{{full text}}

Check against these pattern families, plus anything else you notice:

**Content patterns**

{{content-level failure modes from the digest: inflated significance,
analysis bolted on with participle clauses, promotional gloss, opinions
attributed to no one, formulaic closings — each with the concrete stock
phrases, rendered in the text's language}}

**Language patterns**

{{language-level tells for the text's language, from the matching reference
file: characteristic vocabulary clusters, copula avoidance, negative
parallelisms, list-rhythm habits, synonym rotation, hedging — each with
concrete words and constructions}}

**Style patterns**

{{formatting and punctuation tells for the text's language, from the digest
and the reference file: emphasis habits, lists standing in for prose, dash
and emoji habits, paragraph-shape uniformity, punctuation and register
consistency issues}}

**Citation patterns**

{{citation failure modes from the digest: references that do not exist or
do not support the claim, dead or tracking-parameter links, incomplete or
decorative citations}}

Signals of human writing (weigh these against the above):

{{counter-signals from the digest and the reference file: varied rhythm,
concrete first-hand detail, a committed stance, tolerated repetition,
idiosyncrasies a style-averaging process would smooth away}}

Report:

1. Verdict: reads as AI-written / leaning AI / leaning human / reads as
   human-written.
2. For each finding: the quoted passage, the pattern family, and why it
   contributes to the verdict.
3. The three passages that most drive your verdict, whichever way.
4. Passages that read distinctly human, if any.

Do not rewrite the text; report findings only.
