# Agent Skills spec — hard rules

The mechanical constraints a skill must satisfy. Authoritative source:
[agentskills.io/specification](https://agentskills.io/specification). Rules
tagged **error** fail validation; everything else is a recommendation.

## SKILL.md structure

YAML frontmatter delimited by `---` lines, followed by a Markdown body:

```
---
name: my-skill
description: ...
---

<Markdown body>
```

## Required frontmatter fields

### `name`

| Constraint | Rule |
|---|---|
| Characters | Lowercase `a-z`, digits `0-9`, hyphens `-` only (**error**) |
| Hyphens | No leading, trailing, or consecutive hyphens — `pdf--tools` is invalid (**error**) |
| Max length | 64 characters (**error**) |
| Directory match | Must exactly equal the parent directory name (**error**) |

Valid: `pdf-processing`, `data-analysis-v2`. Invalid: `PDF-Processing`
(uppercase), `-pdf` (leading hyphen), `pdf_processing` (underscore),
`pdf processing` (space).

### `description`

| Constraint | Rule |
|---|---|
| Required, non-empty | (**error**) |
| Max length | 1024 characters (**error**); aim far lower — every character is permanent context load |
| Person | Third person: first sentence = capability (action verbs + domain keywords), remaining sentences = triggers |

The description is the **only** text the agent reads before deciding to
activate the skill.

## Optional frontmatter fields

### `compatibility`

Max 500 characters (**error**). Include only when the skill has real
environment requirements (runtime version, system packages, network access).
Omit otherwise — its absence means "runs anywhere".

### `license`

Short license identifier (e.g. `Apache-2.0`) or a path to a bundled license
file. No length constraint.

### `metadata`

Flat key→value map, `string → string`. Use reasonably unique key names to
avoid conflicts across skills.

### `allowed-tools`

Space-separated string of pre-approved tool names. **Experimental** — support
varies by agent implementation; do not rely on it for safety.

## Portability — fields outside the spec

Some hosts read extra frontmatter fields the spec does not define. Using them
is fine when you target one host, but flag it: another host will silently
ignore them, and a validator may warn on unknown fields.

- `disable-model-invocation: true` — Claude Code extension. Hides the
  description from the agent, making the skill user-invoked (reachable only
  by the human typing its name). On hosts that don't support it, the skill
  behaves as model-invoked. If a skill must be user-only everywhere, keep it
  out of shared skill directories instead.
- Any other host-specific field: document in the skill body which host it
  targets.
- Skill-to-skill invocation — one skill reaching another through its
  description — requires the host to keep all skill descriptions in the
  running agent's context; not every host does. Flag the dependency when a
  skill's design relies on being reached by another skill.

## Directory structure

```
skill-name/            ← must equal the `name` field (error)
├── SKILL.md           ← required (error)
├── scripts/           ← optional: executable helpers
├── references/        ← optional: disclosed reference files
└── assets/            ← optional: templates and static material to copy
```

- Do not create an optional subdirectory until at least one file goes in it —
  an empty directory misleads agents into expecting files that don't exist.
- No `README.md` in the skill root — SKILL.md is the skill's one entry point.

## Body rules

- No mandatory format. Recommended limit: under **500 lines** and **~5,000
  tokens**.
- Self-containment: every file link must be a relative path inside the skill
  directory. A link starting with `../` or `/` breaks when the skill is
  installed by copying the directory elsewhere.
- Link every bundled file (`scripts/`, `references/`, `assets/`) from SKILL.md
  with a relative markdown link at its first mention — an unlinked path in a
  code block is ambiguous about what it is relative to.
- Prefer bundled files at most one directory level deep.

## Progressive disclosure stages

| Stage | Content | Loaded | Recommended size |
|---|---|---|---|
| Metadata | `name` + `description` | every turn | ~100 tokens |
| Instructions | full SKILL.md body | on activation | < 5,000 tokens |
| Resources | `scripts/`, `references/`, `assets/` | on demand | as needed |

Every reference file needs a load condition stated in SKILL.md ("Read X when
Y"). Instructing the agent to load files unconditionally collapses stage 3
into stage 2 and defeats the mechanism.

That "Read X when Y" condition is a *reference* mechanism: a reference is read
to inform the agent's work. An asset is *copied or emitted* rather than read,
so it is linked where it is used and takes no read condition — the shared
"Resources" row above says when a resource loads, not that an asset is read
like a reference.
