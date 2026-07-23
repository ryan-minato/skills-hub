---
name: human-writing
description: >
  Drafts, edits, and reviews text meant for human readers — articles, essays,
  announcements, documentation prose, newsletters — in English, Chinese, or Japanese.
  Use when writing or improving any piece a person will read; when a draft "sounds
  like AI", should be "more human", or needs polish without losing the author's
  voice; when reviewing whether a text lands with its intended audience; or before
  publishing prose produced as a side effect of other work. Also applies as the
  shared baseline when a genre-specific writing skill (academic, blog, copy) is
  active — the specialized skill's rules win on conflict. Not for code, commit
  messages, or agent-facing documents such as AGENTS.md, skill instructions, or
  knowledge-base entries.
---

# Human Writing

Text for human readers fails differently from text for machines: the most resented
AI writing is not wrong, it is authorless — smooth, correct, and empty. Everything
below exists to keep a specific author present in the text.

## Scope and precedence

This skill covers only text whose reader is a person. Code, commit messages, and
agent-facing documents (AGENTS.md, skill files, knowledge bases) follow their own
conventions — do not apply this skill to them. When a genre- or project-specific
writing skill is also loaded, apply both with the specialized skill leading: its
requirements override this baseline wherever they conflict.

## 1. Define the piece before touching it

Before writing or editing a single sentence, pin down four things — from the user's
request, the existing text, or by asking:

- **Type**: what kind of piece this is, and the conventions its venue implies.
- **Author**: who is speaking — their identity, stance, and how they want to appear.
- **Reader**: who receives it — background, expectations, what they already believe.
- **Effect**: what the author wants to change in the reader — what they should feel,
  think, or do afterward.

From these four, derive the piece's center (emotion, opinion, or logic), its voice
and register, and an explicit do/don't list. Human authors write from a concrete
identity and stance; erasing that presence is the core failure of AI writing.

## 2. Plan with budgets, then draft

Outline before drafting, top-down: order sections by importance to the intended
effect, and give each a length budget proportional to its value. A piece where every
point gets equal space says that nothing in it matters. Only start prose once the
structure and budgets stand.

## 3. Write as the author, not as an assistant

Reinforcement learning on user feedback rewards defensive, ingratiating, verbose,
convergent text. Step outside that pull by cycling roles: create as the author,
revise as an editor, judge as the reader. Concretely:

- Keep the author's explicit stance. Never rewrite it into mechanical neutrality or
  bury it under "balanced" both-sides padding the author did not ask for.
- Add no defensive qualifiers ("it's important to note", "of course, this depends")
  unless the uncertainty is real and the author would state it.
- Commit to claims. An author who believes something writes it plainly.

## 4. Failure modes to avoid

A digest of recognizable AI-writing patterns (fuller catalog: Wikipedia's
[Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing)).
Treat these as don'ts while drafting and as a checklist while reviewing:

- **Content**: inflated significance ("stands as a testament", "pivotal role in the
  evolving landscape"); superficial analysis bolted on with "-ing" clauses
  ("..., highlighting the importance of..."); promotional gloss on neutral subjects;
  opinions attributed to no one ("experts say", "widely regarded"); formulaic
  closing sections about challenges and future prospects.
- **Language**: high density of AI-flavored vocabulary (delve, underscore, pivotal,
  robust, landscape, tapestry, meticulous, showcase); avoiding "is/are" in favor of
  "serves as / represents / functions as"; negative parallelisms ("not just X, but
  Y") and rule-of-three chains as default rhythm; rotating synonyms to dodge honest
  repetition.
- **Style**: mechanical bold emphasis; headers-with-colons bullet lists standing in
  for paragraphs; em-dash overuse; emoji as structure; every section the same length
  and shape.
- **Citations**: sources that do not exist, do not say what is claimed, or carry
  broken links and tracking parameters.

These patterns surface differently per language. Read
[references/english.md](references/english.md),
[references/chinese.md](references/chinese.md), or
[references/japanese.md](references/japanese.md) — matching the language the piece
is written in — before drafting or reviewing in that language.

## 5. Citations

Every external source — book, paper, case, statistic — must exist and must meet the
credibility bar the piece's form demands. Verify before citing; if a source cannot
be verified, drop the claim rather than keep an unsourced or invented reference.
LLMs fabricate plausible citations to keep prose flowing; treat every reference you
did not verify as suspect.

## 6. Review loop

After drafting or editing, review from outside the author's seat:

- **Reader review**: if the environment can run subagents with a separate, clean
  context, send the piece with [assets/reader-review-prompt.md](assets/reader-review-prompt.md)
  filled in; otherwise re-read the piece yourself in the reader role, against the
  same questions. Did the piece achieve the intended effect? Does the structure
  carry it?
- **AI-writing detection**: if clean-context subagents are available, send the text
  (with no authorship context) using [assets/ai-detection-prompt.md](assets/ai-detection-prompt.md),
  filled in from the failure-mode digest and the matching language reference per
  the template's own instructions; otherwise skip this pass — the failure-mode
  digest above already served as your self-check.

Fix what the reviews surface, then re-review. Stop when a pass reports no
substantive findings.

## 7. Restraint

If the input text is already natural and idiomatic, say which parts are good and
change nothing — do not edit to justify the invocation. Before final output, ask:
did I change any fluent sentence only to leave a mark? If so, revert it. Fewer,
correct edits beat many defensible ones.
