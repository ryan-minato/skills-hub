# writing

[中文](README.zh.md)

Skills for **writing aimed at human readers** — genre skills (academic,
blog/opinion, promotional copy) and medium skills (LaTeX, Typst, Markdown
source). They share one foundation: define the piece's type, author, reader,
and intended effect before writing; keep a specific author present in the
text; verify every citation; and edit with restraint. The general baseline
skill `human-writing` lives in the `core` catalog.

```bash
npx skills add ryan-minato/skills --skill <skill-name>
```

## Skills

| Skill | Description |
|---|---|
| [academic-writing](academic-writing/) | Write and revise academic prose (papers, theses, reports) in English, Chinese, or Japanese: editor/researcher/reviewer role switching, argument-spine planning, a source-credibility hierarchy with script-verified citations, strict register rules, and restraint-first editing. |
| [blog-writing](blog-writing/) | Write and improve stance-carrying blog posts, columns, and commentary in English, Chinese, or Japanese: confirm audience and persona first, plan on the reader's arc with unequal budgets, keep the stance sharp and the rhythm ahead of defensive narration, verify or drop citations. |
| [copywriting](copywriting/) | Write promotional copy (social posts, ad and landing text, slogans) in English, Chinese, or Japanese: define the client brief first, center emotion and shareability, front-load one message with maximum density, and let structure yield to spread when the medium rewards it. |
| [latex-authoring](latex-authoring/) | Write, edit, and reflow LaTeX source: resolve syntax from class docs, texdoc/CTAN, and Overleaf Learn instead of guessing; break long lines at logical points (semantic linefeeds) since single newlines don't render; core gotchas for macros, dashes, labels, and package order. |
| [markdown-authoring](markdown-authoring/) | Write Markdown for a specific rendering engine: identify the dialect first (GFM, GLFM, mkdocs, Docusaurus/MDX, Obsidian, chat), then apply its newline/blank-line semantics and its forms for math, mermaid, footnotes, admonitions, and HTML — with a defensive CommonMark fallback when the engine is unknown. |
| [typst-authoring](typst-authoring/) | Write and edit Typst source with an in-body primer (markup/code/math modes, set/show rules, include vs import, template pattern) plus a cheat sheet for figures, tables, math, and bibliography — Typst is niche enough that guessed syntax is usually LaTeX in disguise. |
