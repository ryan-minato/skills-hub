---
name: copywriting
description: >
  Writes promotional copy — social media posts, ad copy, landing page and launch
  text, campaign slogans — in English, Chinese, or Japanese. Use when writing 文案,
  a product launch tweet or thread, a 小红书/公众号 promotion, an App Store or
  landing page pitch, or a slogan or tagline; when asked to make an announcement
  "punchy", "catchy", or "shareable"; or when adapting one message into
  platform-sized variants. Not for stance-driven blog or opinion pieces, press
  articles, documentation, or academic text.
---

# Copywriting

Copy exists to move — its center is emotion, spread, and shareability. Content
density and how easily a line travels outrank completeness, and sometimes
outrank structure and grammar.

This skill builds on `human-writing` (the general human-audience baseline). When
`human-writing` is installed, load it alongside this skill before drafting or
editing — do not work from this skill alone. This skill leads: its rules override
the baseline where they conflict — in particular, well-formed prose gives way
where a fragment, repetition, or a broken rhythm spreads better. If
`human-writing` is not installed, install it from
https://github.com/ryan-minato/skills.git:

    npx skills add ryan-minato/skills --skill human-writing

## Roles

- **Defining the brief** — work as the client being promoted (which may be the
  writer themselves): what is being sold, to whom, what one impression must
  survive a half-second scroll, what action counts as success, and what the
  brand would never say. Confirm the brief with the user when any of it is
  unclear; there is no default reader for copy.
- **Drafting** — work as the copywriter: deliver the brief, not your taste.
- **Reviewing** — work as the scrolling reader who owes this text nothing.

## Write for the medium's physics

- One piece, one message. Copy that says two things says nothing; cut or split.
- Front-load: the first line decides whether the rest exists. Put the hook —
  concrete benefit, tension, or image — before any context.
- Density over completeness: every sentence earns its place by carrying the
  message, an emotion, or a reason to act. Delete connective tissue; copy
  tolerates jump cuts.
- Shareability is a design goal: a line worth quoting, a structure worth
  imitating, a claim worth arguing with. If nothing in the piece would survive
  being screenshotted alone, the piece is not done.
- Structure and grammar may yield when the medium rewards it — fragments,
  repetition, a dangling line — but only in service of the message, never from
  carelessness; and platform conventions (hashtags, emoji, line breaks) follow
  the venue's actual usage, not decoration habits.
- Stay in the language's natural cadence; per-language rhythm matters more in
  copy than anywhere else. Claims about the product must stay true — punchy is
  a register, not a license to invent.

## Review pass

If the environment can run subagents with a separate, clean context, send the
copy through [assets/review-prompt.md](assets/review-prompt.md) filled in with
the brief; otherwise re-read it yourself as the scrolling reader against the
same questions. Fix, then re-review. If the provided copy already lands, say
so and change nothing.
