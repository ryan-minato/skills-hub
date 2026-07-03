#!/usr/bin/env python3
"""Lint one or more skill directories against the Agent Skills spec.

Usage:
  python3 scripts/check_skill.py <skill-dir> [<skill-dir>...]
  python3 scripts/check_skill.py --all

ERROR   = spec hard-rule violation or repo rule; fails the check.
WARNING = spec recommendation or quality guidance; reported, never fails.

Token estimates use a chars/4 heuristic, which is reasonable for this
repository's English-only skills.

Exit codes: 0 = clean or warnings only, 1 = at least one error,
2 = bad arguments (e.g. path is not a skill directory).
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
NAME_MAX = 64
DESC_MAX = 1024
DESC_WARN = 900
COMPAT_MAX = 500
BODY_LINES_WARN = 500
BODY_TOKENS_WARN = 5000

ERROR = "ERROR"
WARNING = "WARNING"

Finding = tuple[str, str]  # (severity, message)


def parse_frontmatter(text: str) -> tuple[dict[str, str] | None, str]:
    """Return (frontmatter fields, body). Fields is None when frontmatter
    is missing or unterminated. Handles single-line values and YAML block
    scalars (| and >, with optional +/- chomping)."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None, text
    fields: dict[str, str] = {}
    i = 1
    while i < len(lines):
        line = lines[i]
        if line.strip() == "---":
            return fields, "\n".join(lines[i + 1 :])
        match = re.match(r"^([A-Za-z][\w-]*):\s*(.*)$", line)
        if match:
            key, value = match.group(1), match.group(2).strip()
            if value in ("|", ">", "|-", ">-", "|+", ">+"):
                block: list[str] = []
                i += 1
                while i < len(lines) and (
                    lines[i].startswith((" ", "\t")) or not lines[i].strip()
                ):
                    if lines[i].strip() == "---":
                        break
                    block.append(lines[i].strip())
                    i += 1
                fields[key] = " ".join(part for part in block if part)
                continue
            fields[key] = value.strip("\"'")
        i += 1
    return None, text  # no closing --- found


def check_skill_dir(skill_dir: Path) -> list[Finding]:
    """Lint a single skill directory. Paths in messages are repo-relative
    when possible so output is stable across machines."""
    findings: list[Finding] = []
    try:
        rel = skill_dir.relative_to(REPO_ROOT)
    except ValueError:
        rel = skill_dir

    def error(message: str) -> None:
        findings.append((ERROR, message))

    def warn(message: str) -> None:
        findings.append((WARNING, message))

    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        error(
            f"{rel}: missing SKILL.md. A skill is defined by its SKILL.md; "
            f"without it nothing can be discovered or loaded. Fix: create "
            f"{rel}/SKILL.md with `name` and `description` frontmatter."
        )
        return findings

    fields, body = parse_frontmatter(skill_md.read_text(encoding="utf-8"))
    if fields is None:
        error(
            f"{rel}/SKILL.md: frontmatter missing or unterminated. Agents "
            f"cannot read metadata without a `---` ... `---` block at the "
            f"top. Fix: add frontmatter with `name` and `description`."
        )
        return findings

    # --- name (spec hard rules) ---
    name = fields.get("name", "")
    if not name:
        error(
            f"{rel}/SKILL.md: missing `name` in frontmatter. The spec "
            f"requires it. Fix: add `name: {skill_dir.resolve().name}`."
        )
    else:
        if not NAME_RE.fullmatch(name):
            error(
                f"{rel}/SKILL.md: name `{name}` is invalid. The spec allows "
                f"lowercase a-z, digits, and single hyphens only (no "
                f"leading/trailing/consecutive hyphens, no uppercase, no "
                f"underscores or spaces). Fix: rename to kebab-case."
            )
        if len(name) > NAME_MAX:
            error(
                f"{rel}/SKILL.md: name is {len(name)} chars; the spec "
                f"maximum is {NAME_MAX}. Fix: shorten the name."
            )
        dir_name = skill_dir.resolve().name
        if name != dir_name:
            error(
                f"{rel}/SKILL.md: name `{name}` does not match the "
                f"directory name `{dir_name}`. The spec requires an exact "
                f"match; a mismatch breaks installation and discovery. "
                f"Fix: rename one of them."
            )

    # --- description (spec hard rules + quality guidance) ---
    description = fields.get("description", "")
    if not description:
        error(
            f"{rel}/SKILL.md: missing or empty `description`. It is the "
            f"only text an agent reads before deciding to activate the "
            f"skill, so without it the skill never triggers. Fix: add a "
            f"third-person capability sentence plus 'Use when...' triggers."
        )
    else:
        if len(description) > DESC_MAX:
            error(
                f"{rel}/SKILL.md: description is {len(description)} chars; "
                f"the spec maximum is {DESC_MAX}. Fix: trim it below the "
                f"limit, keeping the trigger phrases."
            )
        elif len(description) > DESC_WARN:
            warn(
                f"{rel}/SKILL.md: description is {len(description)} chars, "
                f"approaching the {DESC_MAX}-char spec limit. Consider "
                f"trimming before it becomes a hard failure."
            )

    # --- compatibility (spec hard rule, optional field) ---
    compatibility = fields.get("compatibility", "")
    if len(compatibility) > COMPAT_MAX:
        error(
            f"{rel}/SKILL.md: compatibility is {len(compatibility)} chars; "
            f"the spec maximum is {COMPAT_MAX}. Fix: state only the "
            f"specific environment requirements, or omit the field."
        )

    # --- body size (spec recommendation) ---
    body_lines = len(body.splitlines())
    body_tokens = len(body) // 4
    if body_lines > BODY_LINES_WARN or body_tokens > BODY_TOKENS_WARN:
        warn(
            f"{rel}/SKILL.md: body is {body_lines} lines / ~{body_tokens} "
            f"tokens (chars/4 heuristic); the spec recommends under "
            f"{BODY_LINES_WARN} lines / ~{BODY_TOKENS_WARN} tokens. Move "
            f"branch-specific material to references/ with precise load "
            f"conditions (progressive disclosure)."
        )

    # --- repo rule: no README.md in a skill root ---
    if (skill_dir / "README.md").exists():
        error(
            f"{rel}: contains README.md. Skill roots must not have a "
            f"README; the catalog README describes skills. Fix: move the "
            f"content into SKILL.md or the catalog README and delete it."
        )

    # --- empty optional subdirectories (quality guidance) ---
    for sub in ("scripts", "references", "assets"):
        sub_dir = skill_dir / sub
        if sub_dir.is_dir() and not any(sub_dir.iterdir()):
            warn(
                f"{rel}/{sub}/: empty directory. It misleads agents into "
                f"expecting files that don't exist. Fix: delete it until "
                f"there is a file to put in it."
            )

    return findings


def repo_skill_dirs() -> list[Path]:
    """All skill directories in this repository: public skills under
    skills/<catalog>/, plus project-only skills in .agents/skills/
    (symlinks excluded — their targets are already covered)."""
    dirs: list[Path] = []
    skills_root = REPO_ROOT / "skills"
    if skills_root.is_dir():
        for catalog in sorted(p for p in skills_root.iterdir() if p.is_dir()):
            dirs.extend(sorted(p for p in catalog.iterdir() if p.is_dir()))
    agents_root = REPO_ROOT / ".agents" / "skills"
    if agents_root.is_dir():
        dirs.extend(
            sorted(
                p for p in agents_root.iterdir() if p.is_dir() and not p.is_symlink()
            )
        )
    return dirs


def report(findings: list[Finding]) -> int:
    errors = [m for sev, m in findings if sev == ERROR]
    warnings = [m for sev, m in findings if sev == WARNING]
    for severity, message in findings:
        print(f"{severity}: {message}\n", file=sys.stderr)
    if errors:
        print(
            f"FAIL: {len(errors)} error(s), {len(warnings)} warning(s). "
            f"Standards: .agents/knowledge/skill-quality.md. Re-run with "
            f"`just check-skill <dir>` after fixing.",
            file=sys.stderr,
        )
        return 1
    if warnings:
        print(f"OK with {len(warnings)} warning(s).")
    else:
        print("OK: all skill checks passed.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("paths", nargs="*", help="skill directories to check")
    parser.add_argument(
        "--all",
        action="store_true",
        help="check every skill in skills/*/* and .agents/skills/*",
    )
    args = parser.parse_args()

    if args.all:
        targets = repo_skill_dirs()
    elif args.paths:
        targets = []
        for raw in args.paths:
            path = Path(raw)
            if not path.is_dir():
                print(f"ERROR: {raw} is not a directory.", file=sys.stderr)
                return 2
            targets.append(path)
    else:
        parser.print_usage(sys.stderr)
        print(
            "ERROR: pass one or more skill directories, or --all.",
            file=sys.stderr,
        )
        return 2

    findings: list[Finding] = []
    for target in targets:
        findings.extend(check_skill_dir(target))
    return report(findings)


if __name__ == "__main__":
    sys.exit(main())
