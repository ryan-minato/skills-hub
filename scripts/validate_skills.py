#!/usr/bin/env python3
"""Validate the repository's skill layout and harness consistency.

Per-skill SKILL.md checks (spec frontmatter rules, size limits, README
rule) live in check_skill.py; this validator runs them over every skill in
the repository and adds the repo-level checks:

  1. Self-containment: no markdown links escaping a public skill's
     directory (targets starting with `../` or `/`).
  2. Every public skill is symlinked into .agents/skills/ and no symlink
     there dangles.
  3. plugin.json skill paths exist.
  4. Every catalog has README.md, README.zh.md, and CONTEXT.md; the root
     README.zh.md exists.
  5. Catalog directories match the catalog list in AGENTS.md.

Errors exit 1; warnings from check_skill.py are reported but never fail.
Messages explain what failed, why it matters, and how to fix it.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import check_skill as skill_linter

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = REPO_ROOT / "skills"
AGENT_SKILLS_DIR = REPO_ROOT / ".agents" / "skills"
PLUGIN_MANIFEST = REPO_ROOT / ".claude-plugin" / "plugin.json"
AGENTS_MD = REPO_ROOT / "AGENTS.md"

ESCAPING_LINK = re.compile(r"\]\((?:\.\./|/)[^)]*\)")

errors: list[str] = []
warnings: list[str] = []


def fail(message: str) -> None:
    errors.append(message)


def check_all_skills() -> None:
    """Run the per-skill linter over public and project-only skills."""
    for severity, message in [
        finding
        for skill_dir in skill_linter.repo_skill_dirs()
        for finding in skill_linter.check_skill_dir(skill_dir)
    ]:
        if severity == skill_linter.ERROR:
            fail(message)
        else:
            warnings.append(message)


def public_skill_dirs() -> list[Path]:
    dirs: list[Path] = []
    if not SKILLS_DIR.is_dir():
        return dirs
    for catalog in sorted(p for p in SKILLS_DIR.iterdir() if p.is_dir()):
        dirs.extend(sorted(p for p in catalog.iterdir() if p.is_dir()))
    return dirs


def check_self_containment() -> None:
    """Public skills must not reference anything outside their own root;
    project-only workflow skills in .agents/skills/ are exempt."""
    for skill_dir in public_skill_dirs():
        for md_file in skill_dir.rglob("*.md"):
            for match in ESCAPING_LINK.finditer(md_file.read_text(encoding="utf-8")):
                fail(
                    f"{md_file.relative_to(REPO_ROOT)}: link "
                    f"{match.group(0)} escapes the skill directory. "
                    f"Installed skills lose access to everything outside "
                    f"their own root, so the link breaks. Fix: copy the "
                    f"content into the skill, or instruct installing the "
                    f"other skill via `npx skills add` (see "
                    f".agents/knowledge/skill-quality.md)."
                )


def check_catalogs() -> None:
    if not SKILLS_DIR.is_dir():
        return
    for catalog in sorted(p for p in SKILLS_DIR.iterdir() if p.is_dir()):
        rel = catalog.relative_to(REPO_ROOT)
        for required in ("README.md", "README.zh.md", "CONTEXT.md"):
            if not (catalog / required).is_file():
                fail(
                    f"{rel}: missing {required}. Every catalog needs "
                    f"README.md (English), README.zh.md (Chinese "
                    f"translation), and CONTEXT.md (catalog-specific rules). "
                    f"Fix: create {rel}/{required}."
                )


def check_agents_md_catalog_list() -> None:
    if not AGENTS_MD.is_file():
        fail(
            "AGENTS.md: missing. It is the harness entrypoint for all "
            "agents. Fix: restore it from git history."
        )
        return
    text = AGENTS_MD.read_text(encoding="utf-8")
    section = re.search(r"^## Catalogs$(.*?)(?=^## |\Z)", text, re.M | re.S)
    if not section:
        fail(
            "AGENTS.md: no `## Catalogs` section found. The validator (and "
            "agents) read the catalog list from that section. Fix: add a "
            "`## Catalogs` heading listing each catalog as `- `name` — ...`."
        )
        return
    listed = set(re.findall(r"^- `([\w-]+)`", section.group(1), re.M))
    actual = (
        {p.name for p in SKILLS_DIR.iterdir() if p.is_dir()}
        if SKILLS_DIR.is_dir()
        else set()
    )
    for missing in sorted(actual - listed):
        fail(
            f"AGENTS.md: catalog `{missing}` exists in skills/ but is not "
            f"listed in the Catalogs section. Agents rely on AGENTS.md to "
            f"know the catalogs. Fix: add `- \\`{missing}\\`` with a short "
            f"description to AGENTS.md."
        )
    for stale in sorted(listed - actual):
        fail(
            f"AGENTS.md: catalog `{stale}` is listed but skills/{stale}/ "
            f"does not exist. Stale harness misleads agents. Fix: remove "
            f"the entry or create the catalog."
        )


def check_symlinks() -> None:
    if not AGENT_SKILLS_DIR.is_dir():
        fail(
            ".agents/skills/: missing. Project agents discover skills "
            "there. Fix: recreate it and re-run this validator."
        )
        return

    for entry in sorted(AGENT_SKILLS_DIR.iterdir()):
        if entry.is_symlink() and not entry.resolve().is_dir():
            fail(
                f".agents/skills/{entry.name}: dangling symlink (target "
                f"missing). Agents fail to load the skill. Fix: remove the "
                f"link or restore the target skill directory."
            )

    for skill_dir in public_skill_dirs():
        link = AGENT_SKILLS_DIR / skill_dir.name
        rel = skill_dir.relative_to(REPO_ROOT)
        if not link.is_symlink():
            fail(
                f"{rel}: no symlink in .agents/skills/. Without it this "
                f"repo's agents cannot use the skill. Fix: "
                f"ln -s ../../{rel} .agents/skills/{skill_dir.name}"
            )
        elif link.resolve() != skill_dir.resolve():
            fail(
                f".agents/skills/{skill_dir.name}: points to "
                f"{link.resolve()} instead of {rel}. Fix: recreate it with "
                f"ln -sfn ../../{rel} .agents/skills/{skill_dir.name}"
            )


def check_plugin_manifest() -> None:
    if not PLUGIN_MANIFEST.is_file():
        fail(
            ".claude-plugin/plugin.json: missing. It publishes the public "
            "skill list for plugin installs. Fix: restore it from git "
            "history."
        )
        return
    try:
        manifest = json.loads(PLUGIN_MANIFEST.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(
            f".claude-plugin/plugin.json: invalid JSON ({exc}). Plugin "
            f"installs will fail. Fix: repair the syntax."
        )
        return
    paths = manifest.get("skills", [])
    if isinstance(paths, str):
        paths = [paths]
    for path in paths:
        if not (REPO_ROOT / path.lstrip("./")).is_dir():
            fail(
                f".claude-plugin/plugin.json: skills path `{path}` does not "
                f"exist. Plugin installs would silently miss skills. Fix: "
                f"update the path or create the directory."
            )


def check_root_files() -> None:
    if (REPO_ROOT / "README.md").is_file() and not (
        REPO_ROOT / "README.zh.md"
    ).is_file():
        fail(
            "README.zh.md: missing. The root README must have a "
            "content-identical Chinese translation. Fix: create README.zh.md."
        )


def main() -> int:
    check_all_skills()
    check_self_containment()
    check_catalogs()
    check_agents_md_catalog_list()
    check_symlinks()
    check_plugin_manifest()
    check_root_files()

    for warning in warnings:
        print(f"WARNING: {warning}\n", file=sys.stderr)

    if errors:
        print(f"FAIL: {len(errors)} problem(s) found\n", file=sys.stderr)
        for error in errors:
            print(f"  * {error}\n", file=sys.stderr)
        print(
            "Source of truth: AGENTS.md and .agents/knowledge/skill-quality.md. "
            "Re-run with `just validate` after fixing.",
            file=sys.stderr,
        )
        return 1
    suffix = f" ({len(warnings)} warning(s))" if warnings else ""
    print(f"OK: skill layout and harness consistency checks passed{suffix}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
