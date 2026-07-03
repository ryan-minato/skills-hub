# Knowledge And Reference Files

Documents that carry project knowledge to agents. They are the one harness
category with no self-announcement mechanism, so every file created here
needs a when-to-read pointer in the entrypoint or it is invisible.

## Two kinds of documents

- Documents with a public convention that humans also read — an architecture
  overview, contribution guide, security policy, and similar files at their
  conventional locations. Write these human-readable-first; agents handle
  human prose fine, and the conventional name is itself part of
  discoverability.
- Agent-facing documents: design documents intended for agents, and
  knowledge-library files. Write these agent-first — front-load the facts,
  state the load condition at the top, keep one concern per file, and skip
  narrative padding.

Prefer existing maintained documents when they are accurate and concise;
do not write an agent-facing duplicate of something the project already
records.

## The local knowledge library

The default home for agent-facing knowledge is a dedicated folder at the
project root (`.agents/knowledge/` is a common choice): a set of focused
files, not one catch-all document. Create only the files a current need
justifies — no placeholder documents, no empty folders. Give every file a
precise load condition and register it in the entrypoint's when-to-read
pointers.

Start a new file from the matching shape in
`assets/knowledge-skeletons.md` (path relative to this skill's root): goals,
plan, quality, workflow, or reference index.

## Remote knowledge backends

Knowledge does not have to live in the repository. A team may keep it in a
ticket system, wiki, or another service, reached through a skill or a
registered tool. Use a remote backend when the maintained truth already
lives there, when the team needs to edit it outside the repository, or when
access control matters; keep knowledge local when it is stable, when agents
need it offline or pinned, or when no external access has been granted.
When uncertain, keep it local and ask the user — never invent an external
source or assume access that was not granted.

When the source of truth is external:

- Add a project-visible pointer stating what the source represents, when to
  consult it, and whether it is the source of truth or supplementary.
- Record the access boundary: what agents may read, what they may write,
  and what needs approval. Never embed credentials in harness files, and do
  not depend on one person's personal tool configuration — state the
  capability the project expects instead.
- Pick exactly one source of truth per piece of knowledge. If a local
  summary exists beside an external source, the summary must name the
  external source as truth, state what it covers and omits, carry a date or
  milestone, and have an update trigger. Never bulk-copy external material
  into the repository; stale copies mislead agents with confidence.
