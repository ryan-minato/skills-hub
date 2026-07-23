---
name: blog-writing
description: >
  Writes and improves blog posts, columns, and opinion or commentary pieces that
  carry an author's stance, in English, Chinese, or Japanese. Use when drafting a
  blog post, personal essay, or 专栏/评论/コラム piece; when turning notes, a work
  log, or a talk into a publishable post; when a draft needs stronger narrative
  rhythm, a clearer through-line, or a more present authorial voice; or when
  reviewing whether a post lands with its intended readers. Asks for the target
  audience and author persona when the user has not specified them. Not for
  academic manuscripts, promotional or ad copy, or reference documentation.
---

# Blog Writing

A blog or opinion piece exists to deliver a stance. Its center is the author's
opinion and the narrative rhythm that carries the reader to it; being correct is
a bonus, and being defensible is not the goal.

This skill builds on `human-writing` (the general human-audience baseline). When
`human-writing` is installed, load it alongside this skill before drafting or
editing — do not work from this skill alone. This skill leads: its rules override
the baseline where they conflict. If `human-writing` is not installed, install it
from https://github.com/ryan-minato/skills.git:

    npx skills add ryan-minato/skills --skill human-writing

## Audience and persona are inputs, not assumptions

Readers of this genre range from complete beginners to seasoned peers, depending
on the venue and the author; the image the author wants to project varies just
as widely. Take both from the user's request. When either is unspecified,
ask — or state the assumption explicitly and get it confirmed — before designing
the piece. A post aimed at nobody in particular reaches nobody in particular.

## Roles

- **Designing, drafting, improving** — work as a columnist: a professional with
  a voice, hired to say something, on deadline.
- **Reviewing** — work as the target reader, meeting the piece cold.

## Plan on the reader's arc

Outline along the reader's emotional and intellectual trajectory: where they
start (skeptical? curious? annoyed?), what they must feel or accept at each
step, and where they should land. For every section, name the role it plays in
that arc; a section with no role gets cut, however good the material. Assign
length budgets by importance — if everything gets equal space, the piece says
that nothing in it matters. Avoid flat chronology unless the timeline itself is
the point.

## Deliver the stance

- The author's opinion stays sharp. Never dilute it into on-the-one-hand
  neutrality, and never spend the reader's momentum on preemptive defenses
  against every possible objection. Address the one objection the target reader
  will actually raise, where it naturally comes up.
- Correctness supports the piece but never outranks its rhythm: cut the
  qualifying subclause, keep the claim honest instead.

## Citations and facts

If the piece cites sources — papers, cases, statistics, quotes — verify each
one. If a source cannot be found, do not use the claim. Judge whether the
source is credible enough for this piece and audience: a community thread can
anchor a hot take but not an investigative claim.

## Style

- Short paragraphs; one to three sentences is normal. A wall of text loses
  screen readers.
- Interleave images, diagrams, or code blocks with prose where they carry the
  point better than words; tell the user where a figure belongs if you cannot
  produce it.
- Explicit connectives only where the logic turns; otherwise let order carry
  the flow.
- An ordered list only for a genuine progression, an unordered list only for
  genuine parallelism; otherwise prose.

## Review pass

If the environment can run subagents with a separate, clean context, send the
draft through [assets/review-prompt.md](assets/review-prompt.md) filled in with
the audience and persona; otherwise re-read the piece yourself as the target
reader against the same questions. Fix what the review surfaces, then
re-review. If the input text is already natural and effective, say which parts
are good and change nothing.
