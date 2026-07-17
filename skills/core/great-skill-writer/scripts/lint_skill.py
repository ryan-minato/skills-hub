#!/usr/bin/env -S uv run
# /// script
# dependencies = [
#   "pyyaml>=6.0,<7",
# ]
# requires-python = ">=3.11"
# ///
"""Lint an Agent Skill: spec compliance plus quality heuristics.

Checks frontmatter fields, directory structure, body size, link integrity
(self-containment and broken targets), reachability of bundled files,
description quality, and script hygiene.

Usage:
  uv run scripts/lint_skill.py --skill PATH [--json]

PATH is a skill directory or its SKILL.md file.

Exit codes:
  0  no errors (warnings may be present)
  1  one or more errors found
  2  bad arguments
"""

import argparse
import json
import re
import sys
from pathlib import Path

import yaml

KNOWN_FIELDS = frozenset(
    {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
)
REQUIRED_FIELDS = frozenset({"name", "description"})
ALLOWED_ROOT = frozenset({"SKILL.md", "references", "assets", "scripts"})
BUNDLE_DIRS = ("scripts", "references", "assets")
ALLOWED_SCRIPT_EXTS = frozenset({".py", ".ts"})

NAME_RE = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
MD_LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
FENCE_RE = re.compile(r"^(```|~~~)", re.MULTILINE)
CONDITION_WORDS = ("when", "if", "before", "after", "unless", "only")
USE_WHEN_RE = re.compile(r"\buse\b(?:\s+\w+){0,2}\s+when\b")
FILLER_OPENERS = ("this ", "a ", "an ", "helps ", "allows ", "provides ")
INTERACTIVE_PY_RE = re.compile(r"(?<![\w.\"'])input\s*\(")
INTERACTIVE_TS_RE = re.compile(r"(?<![\w.\"'])(?:prompt|confirm)\s*\(")

DESCRIPTION_MAX = 1024
DESCRIPTION_WARN_MILD = 600
DESCRIPTION_WARN_STRONG = 900
COMPATIBILITY_MAX = 500
BODY_WARN_LINES = 500
BODY_WARN_LINES_STRONG = 1000
BODY_WARN_TOKENS = 5000


def issue(location: str, level: str, reason: str, suggestion: str) -> dict:
    return {"location": location, "level": level, "reason": reason, "suggestion": suggestion}


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(Path.cwd()))
    except ValueError:
        return str(path)


def parse_frontmatter(text: str) -> tuple[dict, str]:
    """Return (frontmatter, body). Raise ValueError on parse failure."""
    if not text.startswith("---"):
        raise ValueError("missing opening '---'")
    lines = text.splitlines(keepends=True)
    end = next((i for i, line in enumerate(lines[1:], 1) if line.strip() == "---"), None)
    if end is None:
        raise ValueError("missing closing '---' delimiter")
    try:
        fm = yaml.safe_load("".join(lines[1:end]))
    except yaml.YAMLError as exc:
        raise ValueError(f"YAML parse error: {exc}") from exc
    if fm is None:
        fm = {}
    if not isinstance(fm, dict):
        raise ValueError("frontmatter must be a YAML mapping")
    return fm, "".join(lines[end + 1 :])


def strip_fenced_code(text: str) -> str:
    """Blank out fenced code blocks so examples inside them are not linted."""
    out: list[str] = []
    in_fence = False
    for line in text.splitlines(keepends=True):
        if FENCE_RE.match(line):
            in_fence = not in_fence
            out.append("\n")
        else:
            out.append(line if not in_fence else "\n")
    return "".join(out)


LIST_ITEM_RE = re.compile(r"(?:[-*+]|\d+\.)\s")


def split_prose_units(text: str) -> list[str]:
    """Split into logical prose units: paragraphs, with each list item its own
    unit, joining soft-wrapped lines so sentence-level checks see whole
    sentences."""
    units: list[str] = []
    current: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            if current:
                units.append(" ".join(current))
                current = []
        elif LIST_ITEM_RE.match(stripped):
            if current:
                units.append(" ".join(current))
            current = [stripped]
        else:
            current.append(stripped)
    if current:
        units.append(" ".join(current))
    return units


def check_frontmatter(base: str, skill_dir: Path, fm: dict) -> list[dict]:
    issues: list[dict] = []

    for key in sorted(fm):
        if key not in KNOWN_FIELDS:
            issues.append(issue(
                f"{base}:frontmatter:{key}",
                "warning",
                f"Frontmatter field '{key}' is not in the Agent Skills spec.",
                f"Spec fields: {', '.join(sorted(KNOWN_FIELDS))}. If '{key}' is a "
                "host-specific extension, keep it but note the host it targets in the body.",
            ))

    for key in sorted(REQUIRED_FIELDS):
        if key not in fm:
            issues.append(issue(
                f"{base}:frontmatter",
                "error",
                f"Required field '{key}' is missing.",
                f"Add '{key}' to the frontmatter block.",
            ))

    name = fm.get("name")
    if name is not None:
        if not isinstance(name, str):
            issues.append(issue(
                f"{base}:frontmatter:name",
                "error",
                f"'name' must be a string, got {type(name).__name__}.",
                "Set 'name' to a lowercase hyphenated string matching the directory name.",
            ))
        else:
            if len(name) > 64:
                issues.append(issue(
                    f"{base}:frontmatter:name",
                    "error",
                    f"'name' is {len(name)} chars; maximum is 64.",
                    "Shorten the skill name to 64 characters or fewer.",
                ))
            if not NAME_RE.fullmatch(name):
                issues.append(issue(
                    f"{base}:frontmatter:name",
                    "error",
                    f"'name' value '{name}' has invalid characters or structure.",
                    "Use only lowercase a-z, digits 0-9, and single hyphens — no leading, "
                    "trailing, or consecutive hyphens ('my-skill', not 'My_Skill' or 'my--skill').",
                ))
            if name != skill_dir.name:
                issues.append(issue(
                    f"{base}:frontmatter:name",
                    "error",
                    f"'name' is '{name}' but the directory is '{skill_dir.name}'; they must match exactly.",
                    f"Rename the directory to '{name}' or change 'name' to '{skill_dir.name}'.",
                ))

    issues.extend(check_description(base, fm.get("description")))

    compat = fm.get("compatibility")
    if isinstance(compat, str) and len(compat) > COMPATIBILITY_MAX:
        issues.append(issue(
            f"{base}:frontmatter:compatibility",
            "error",
            f"'compatibility' is {len(compat)} chars; maximum is {COMPATIBILITY_MAX}.",
            "Trim to 500 chars or fewer; state only real environment requirements.",
        ))

    meta = fm.get("metadata")
    if meta is not None and not isinstance(meta, dict):
        issues.append(issue(
            f"{base}:frontmatter:metadata",
            "error",
            f"'metadata' must be a YAML mapping, got {type(meta).__name__}.",
            "Use a flat mapping, e.g.:\nmetadata:\n  author: my-org\n  version: '1.0'",
        ))

    return issues


def check_description(base: str, desc: object) -> list[dict]:
    issues: list[dict] = []
    loc = f"{base}:frontmatter:description"
    if desc is None:
        return issues
    if not isinstance(desc, str):
        issues.append(issue(
            loc,
            "error",
            f"'description' must be a string, got {type(desc).__name__}.",
            "Use a YAML string, optionally with '>' for a folded block scalar.",
        ))
        return issues

    length = len(desc)
    if length > DESCRIPTION_MAX:
        issues.append(issue(
            loc,
            "error",
            f"'description' is {length} chars; maximum is {DESCRIPTION_MAX}.",
            "Trim below 1024: keep the capability sentence and one trigger per branch.",
        ))
    elif length > DESCRIPTION_WARN_STRONG:
        issues.append(issue(
            loc,
            "warning",
            f"'description' is {length} chars (>{DESCRIPTION_WARN_STRONG}); it is loaded "
            "into context on every turn.",
            "Cut synonym triggers (keep one per branch) and identity already in the body.",
        ))
    elif length > DESCRIPTION_WARN_MILD:
        issues.append(issue(
            loc,
            "warning",
            f"'description' is {length} chars (>{DESCRIPTION_WARN_MILD}).",
            "Consider trimming: one trigger per branch, no body identity restated.",
        ))

    lowered = desc.lower()
    if not USE_WHEN_RE.search(lowered) and "use this" not in lowered:
        issues.append(issue(
            loc,
            "warning",
            "'description' has no 'Use when …' trigger clause.",
            "Add trigger conditions after the capability sentence — the description is "
            "the only text the agent reads before activating.",
        ))
    if lowered.startswith(FILLER_OPENERS):
        issues.append(issue(
            loc,
            "warning",
            f"'description' opens with filler ('{desc.split()[0]}').",
            "Front-load the skill's leading word: start with the action verb or the "
            "domain concept that should trigger it.",
        ))
    if re.search(r"^i\s|\si\s", desc.lower()) or " my " in lowered:
        issues.append(issue(
            loc,
            "warning",
            "'description' uses first person.",
            "Write in third person: capability first, then triggers.",
        ))
    return issues


def check_body_size(base: str, body: str) -> list[dict]:
    issues: list[dict] = []
    lines = len(body.splitlines())
    est_tokens = len(body) // 4
    if lines > BODY_WARN_LINES_STRONG:
        issues.append(issue(
            f"{base}:body",
            "warning",
            f"Body is {lines} lines (>{BODY_WARN_LINES_STRONG}); attention thins across the excess.",
            "This is sprawl: disclose branch-specific content into references/ behind "
            "conditional pointers, or split the skill by branch or sequence.",
        ))
    elif lines > BODY_WARN_LINES or est_tokens > BODY_WARN_TOKENS:
        issues.append(issue(
            f"{base}:body",
            "warning",
            f"Body is {lines} lines / ~{est_tokens} tokens "
            f"(recommended <{BODY_WARN_LINES} lines and <{BODY_WARN_TOKENS} tokens).",
            "Move content needed only on some branches to references/<file>.md with a "
            "conditional load instruction.",
        ))
    return issues


def check_structure(skill_dir: Path) -> list[dict]:
    issues: list[dict] = []
    base = rel(skill_dir)

    for entry in sorted(skill_dir.iterdir()):
        if entry.name in ALLOWED_ROOT:
            continue
        loc = f"{base}/{entry.name}"
        if entry.name == "README.md":
            issues.append(issue(
                loc,
                "error",
                "README.md found in the skill root.",
                "SKILL.md is the skill's one entry point; the description field covers "
                "discovery. Remove README.md.",
            ))
        elif entry.name.startswith("."):
            issues.append(issue(
                loc,
                "warning",
                f"Hidden entry '{entry.name}' in the skill root.",
                "Skill roots should hold only SKILL.md, scripts/, references/, assets/. "
                "Remove it unless required at runtime.",
            ))
        else:
            issues.append(issue(
                loc,
                "warning",
                f"Unexpected entry '{entry.name}' in the skill root.",
                "Move it into scripts/, references/, or assets/, or remove it.",
            ))

    for sub in BUNDLE_DIRS:
        sub_dir = skill_dir / sub
        if sub_dir.is_dir() and not any(sub_dir.iterdir()):
            issues.append(issue(
                f"{base}/{sub}/",
                "warning",
                f"'{sub}/' is empty.",
                "An empty directory misleads agents into expecting files. Delete it "
                "until a file goes in.",
            ))

    scripts_dir = skill_dir / "scripts"
    if scripts_dir.is_dir():
        for entry in sorted(scripts_dir.iterdir()):
            loc = f"{base}/scripts/{entry.name}"
            if entry.is_dir():
                issues.append(issue(
                    f"{loc}/",
                    "warning",
                    f"Subdirectory '{entry.name}' inside scripts/.",
                    "Keep scripts/ flat: inline shared logic into the scripts that use it.",
                ))
                continue
            ext = entry.suffix.lower()
            if ext == ".js":
                issues.append(issue(
                    loc,
                    "warning",
                    f"'{entry.name}' is plain JavaScript.",
                    "Use TypeScript (.ts): Deno and Bun run it natively with type safety at no cost.",
                ))
            elif ext in {".sh", ".ps1"}:
                issues.append(issue(
                    loc,
                    "warning",
                    f"'{entry.name}' runs only where its shell exists; not portable across agent environments.",
                    "Rewrite in Python (uv) or TypeScript (Deno/Bun), or document the "
                    "requirement in the 'compatibility' field.",
                ))
            elif ext not in ALLOWED_SCRIPT_EXTS:
                issues.append(issue(
                    loc,
                    "warning",
                    f"Unexpected file type '{ext}' in scripts/.",
                    "Use .py (uv) or .ts (Deno/Bun); remove or convert other files.",
                ))
    return issues


def check_links(skill_dir: Path) -> list[dict]:
    """Self-containment and broken-target checks over all markdown in the skill."""
    issues: list[dict] = []
    md_files = [skill_dir / "SKILL.md"] + sorted(skill_dir.glob("references/*.md"))
    for md in md_files:
        if not md.exists():
            continue
        text = strip_fenced_code(md.read_text(encoding="utf-8"))
        loc = rel(md)
        for match in MD_LINK_RE.finditer(text):
            target = match.group(1)
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            if target.startswith(("../", "/")):
                issues.append(issue(
                    f"{loc}:link:{target}",
                    "error",
                    f"Link '{target}' escapes the skill directory.",
                    "Skills are installed by copying the directory; outside links break. "
                    "Bundle the material inside the skill or link a URL.",
                ))
                continue
            resolved = (md.parent / target.split("#", 1)[0]).resolve()
            if not resolved.exists():
                issues.append(issue(
                    f"{loc}:link:{target}",
                    "error",
                    f"Link target '{target}' does not exist.",
                    "A broken pointer has zero reach. Fix the path or create the file.",
                ))
    return issues


def check_reachability(skill_dir: Path, skill_body: str) -> list[dict]:
    """Every bundled file must be reachable from SKILL.md, with a condition on references."""
    issues: list[dict] = []
    base = rel(skill_dir)
    body_no_code = strip_fenced_code(skill_body)

    for sub in BUNDLE_DIRS:
        sub_dir = skill_dir / sub
        if not sub_dir.is_dir():
            continue
        for entry in sorted(sub_dir.iterdir()):
            if not entry.is_file():
                continue
            ref = f"{sub}/{entry.name}"
            if ref not in skill_body:
                issues.append(issue(
                    f"{base}/{ref}",
                    "warning",
                    f"'{ref}' is never mentioned in SKILL.md.",
                    "Orphaned files are unreachable sediment. Link it with a relative "
                    "markdown link at first mention, or delete it.",
                ))

    for unit in split_prose_units(body_no_code):
        if "references/" not in unit or not MD_LINK_RE.search(unit):
            continue
        if not any(word in unit.lower() for word in CONDITION_WORDS):
            snippet = unit if len(unit) <= 100 else unit[:97] + "..."
            issues.append(issue(
                f"{rel(skill_dir / 'SKILL.md')}:pointer",
                "warning",
                f"Reference pointer without a load condition: {snippet!r}.",
                "Pointer wording decides reach. State the condition: "
                "'Read references/<file>.md when <condition>.'",
            ))
    return issues


def check_script_hygiene(skill_dir: Path) -> list[dict]:
    issues: list[dict] = []
    scripts_dir = skill_dir / "scripts"
    if not scripts_dir.is_dir():
        return issues
    for entry in sorted(scripts_dir.iterdir()):
        if not entry.is_file():
            continue
        loc = f"{rel(skill_dir)}/scripts/{entry.name}"
        text = entry.read_text(encoding="utf-8", errors="replace")
        pattern = None
        if entry.suffix == ".py":
            pattern = INTERACTIVE_PY_RE
        elif entry.suffix == ".ts":
            pattern = INTERACTIVE_TS_RE
        if pattern and pattern.search(text):
            issues.append(issue(
                loc,
                "warning",
                "Script appears to call an interactive prompt builtin.",
                "Agents run in non-interactive shells where prompts hang forever. "
                "Accept all input via CLI flags.",
            ))
    return issues


def lint(skill_md: Path) -> list[dict]:
    skill_dir = skill_md.parent
    base = rel(skill_md)
    text = skill_md.read_text(encoding="utf-8")
    try:
        fm, body = parse_frontmatter(text)
    except ValueError as exc:
        return [issue(
            f"{base}:frontmatter",
            "error",
            f"Cannot parse frontmatter: {exc}.",
            "SKILL.md must begin with '---', contain valid YAML, and close the block "
            "with '---' on its own line.",
        )]

    issues: list[dict] = []
    issues += check_frontmatter(base, skill_dir, fm)
    issues += check_body_size(base, body)
    issues += check_structure(skill_dir)
    issues += check_links(skill_dir)
    issues += check_reachability(skill_dir, body)
    issues += check_script_hygiene(skill_dir)
    return issues


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Lint an Agent Skill: spec compliance plus quality heuristics.",
        epilog="Example: uv run scripts/lint_skill.py --skill path/to/my-skill",
    )
    parser.add_argument(
        "--skill",
        required=True,
        metavar="PATH",
        help="Path to a skill directory or its SKILL.md file.",
    )
    parser.add_argument(
        "--json",
        dest="json_output",
        action="store_true",
        help="Output findings as JSON instead of human-readable text.",
    )
    args = parser.parse_args()

    path = Path(args.skill).resolve()
    if path.is_dir():
        skill_md = path / "SKILL.md"
    elif path.name == "SKILL.md":
        skill_md = path
    else:
        parser.error(f"--skill must be a skill directory or a SKILL.md file. Got: {args.skill!r}")

    if not skill_md.exists():
        print(f"Error: '{skill_md}' does not exist.", file=sys.stderr)
        sys.exit(1)

    issues = lint(skill_md)
    errors = [i for i in issues if i["level"] == "error"]

    if args.json_output:
        print(json.dumps(issues, indent=2))
    else:
        if not issues:
            print(f"OK  {rel(skill_md.parent)}: all checks passed.")
        for item in issues:
            label = "ERROR  " if item["level"] == "error" else "WARNING"
            print(f"{label}  [{item['location']}]")
            print(f"           Reason:     {item['reason']}")
            print(f"           Suggestion: {item['suggestion']}")
            print()

    if errors:
        print(f"{len(errors)} error(s) found.", file=sys.stderr)
        sys.exit(1)
    if issues:
        print(f"{len(issues)} warning(s).", file=sys.stderr)
    sys.exit(0)


if __name__ == "__main__":
    main()
