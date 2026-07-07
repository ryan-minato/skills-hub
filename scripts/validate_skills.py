#!/usr/bin/env python3
"""Validate the repository's skill layout and harness consistency.

Per-skill SKILL.md checks (spec frontmatter rules, size limits, README
rule) live in check_skill.py; this validator runs them over every skill in
the repository and adds the repo-level checks:

  1. Self-containment: no markdown links escaping a public skill's
     directory (targets starting with `../` or `/`).
  2. Every public skill is symlinked into .agents/skills/ and no symlink
     there dangles.
  3. marketplace.json publishes one plugin per non-empty catalog.
  4. Every catalog has README.md, README.zh.md, and CONTEXT.md; the root
     README.zh.md exists.
  5. Catalog directories match the catalog list in ARCHITECTURE.md.

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
MARKETPLACE_MANIFEST = REPO_ROOT / ".claude-plugin" / "marketplace.json"
LEGACY_PLUGIN_MANIFEST = REPO_ROOT / ".claude-plugin" / "plugin.json"
ARCHITECTURE_MD = REPO_ROOT / "ARCHITECTURE.md"

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


def check_architecture_md_catalog_list() -> None:
    if not ARCHITECTURE_MD.is_file():
        fail(
            "ARCHITECTURE.md: missing. It documents the repo mechanisms "
            "and holds the catalog list. Fix: restore it from git history."
        )
        return
    text = ARCHITECTURE_MD.read_text(encoding="utf-8")
    section = re.search(r"^## Catalogs$(.*?)(?=^## |\Z)", text, re.M | re.S)
    if not section:
        fail(
            "ARCHITECTURE.md: no `## Catalogs` section found. The validator "
            "(and agents) read the catalog list from that section. Fix: add "
            "a `## Catalogs` heading listing each catalog as `- `name` — ...`."
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
            f"ARCHITECTURE.md: catalog `{missing}` exists in skills/ but is "
            f"not listed in the Catalogs section. Agents rely on "
            f"ARCHITECTURE.md to know the catalogs. Fix: add `- "
            f"\\`{missing}\\`` with a short description to ARCHITECTURE.md."
        )
    for stale in sorted(listed - actual):
        fail(
            f"ARCHITECTURE.md: catalog `{stale}` is listed but "
            f"skills/{stale}/ does not exist. Stale harness misleads "
            f"agents. Fix: remove the entry or create the catalog."
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


def catalog_skill_subdirs(catalog: Path) -> list[Path]:
    """Skill directories (each holding a SKILL.md) directly under a catalog."""
    if not catalog.is_dir():
        return []
    return [p for p in catalog.iterdir() if p.is_dir() and (p / "SKILL.md").is_file()]


def nonempty_catalog_names() -> set[str]:
    """Catalogs under skills/ that publish at least one skill."""
    if not SKILLS_DIR.is_dir():
        return set()
    return {c.name for c in SKILLS_DIR.iterdir() if catalog_skill_subdirs(c)}


def check_marketplace_manifest() -> None:
    """The repo publishes as a pure marketplace: one plugin per non-empty
    catalog, each entry using a marketplace-root `source` and a `skills`
    array that enumerates the catalog's skill directories
    (`./skills/<catalog>/<skill>`). Those exact paths are what the vercel
    `skills` CLI groups on and what Claude Code loads; the list must match
    the catalog on disk (kept in sync by scripts/gen_marketplace.py)."""
    if LEGACY_PLUGIN_MANIFEST.is_file():
        fail(
            ".claude-plugin/plugin.json: the repo now publishes as a "
            "marketplace (.claude-plugin/marketplace.json), not one plugin. "
            "A leftover plugin.json is merged into every marketplace-root "
            "plugin and cross-loads all catalogs. Fix: remove it "
            "(git rm .claude-plugin/plugin.json)."
        )

    if not MARKETPLACE_MANIFEST.is_file():
        fail(
            ".claude-plugin/marketplace.json: missing. It publishes each "
            "catalog as an installable plugin. Fix: create it with `name`, "
            "`owner`, and one `plugins` entry per non-empty catalog."
        )
        return
    try:
        manifest = json.loads(MARKETPLACE_MANIFEST.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(
            f".claude-plugin/marketplace.json: invalid JSON ({exc}). "
            f"Marketplace adds will fail. Fix: repair the syntax."
        )
        return

    if not manifest.get("name"):
        fail(
            ".claude-plugin/marketplace.json: missing top-level `name` (the "
            "marketplace id users type as `<plugin>@<name>`). Fix: add a "
            "kebab-case `name`."
        )
    owner = manifest.get("owner")
    if not isinstance(owner, dict) or not owner.get("name"):
        fail(
            ".claude-plugin/marketplace.json: missing `owner.name`. The "
            'schema requires an owner. Fix: add `"owner": {"name": "..."}`.'
        )
    plugins = manifest.get("plugins")
    if not isinstance(plugins, list) or not plugins:
        fail(
            ".claude-plugin/marketplace.json: `plugins` must be a non-empty "
            "list, one entry per non-empty catalog. Fix: add the entries."
        )
        return

    listed_catalogs: set[str] = set()
    for entry in plugins:
        if not isinstance(entry, dict):
            fail(
                ".claude-plugin/marketplace.json: every `plugins` entry must "
                "be an object with `name`, `source`, and `skills`."
            )
            continue
        name = entry.get("name", "")
        if not name or not skill_linter.NAME_RE.fullmatch(name):
            fail(
                f".claude-plugin/marketplace.json: plugin name `{name}` is "
                f"not kebab-case; claude.ai marketplace sync rejects "
                f"non-kebab names. Fix: rename to lowercase-hyphen."
            )
        if entry.get("source") != "./":
            fail(
                f".claude-plugin/marketplace.json: plugin `{name}` source must "
                f'be `"./"` (the marketplace root); that is what makes the '
                f"`skills` filter replace the default scan so the plugin loads "
                f'only its own catalog. Fix: set `"source": "./"`.'
            )
        skills = entry.get("skills", [])
        if isinstance(skills, str):
            skills = [skills]
        for path in skills:
            if not path.startswith("./"):
                fail(
                    f".claude-plugin/marketplace.json: plugin `{name}` skills "
                    f"path `{path}` must be a relative path starting with "
                    f"`./` (no `..` traversal). Fix: run `just gen-marketplace`."
                )

        # Each plugin must enumerate exactly its catalog's skill directories,
        # so the vercel picker groups them and Claude Code loads them. The
        # generator (scripts/gen_marketplace.py) keeps this list in sync.
        expected = [
            f"./skills/{name}/{d.name}"
            for d in catalog_skill_subdirs(SKILLS_DIR / name)
        ]
        if not expected:
            fail(
                f".claude-plugin/marketplace.json: plugin `{name}` has no "
                f"catalog skills/{name}/ with skills. An empty or missing "
                f"catalog must not be published. Fix: remove the entry."
            )
        elif sorted(skills) != sorted(expected):
            missing = sorted(set(expected) - set(skills))
            stale = sorted(set(skills) - set(expected))
            detail = ", ".join(
                part
                for part in (
                    f"missing {missing}" if missing else "",
                    f"stale {stale}" if stale else "",
                )
                if part
            )
            fail(
                f".claude-plugin/marketplace.json: plugin `{name}` skills[] is "
                f"out of sync with skills/{name}/ ({detail}). Fix: run "
                f"`just gen-marketplace`."
            )
        listed_catalogs.add(name)

    for missing in sorted(nonempty_catalog_names() - listed_catalogs):
        fail(
            f".claude-plugin/marketplace.json: catalog `{missing}` has skills "
            f"but no plugin entry, so it cannot be installed. Fix: add a "
            f'`plugins` entry with `"skills": ["./skills/{missing}"]`.'
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
    check_architecture_md_catalog_list()
    check_symlinks()
    check_marketplace_manifest()
    check_root_files()

    for warning in warnings:
        print(f"WARNING: {warning}\n", file=sys.stderr)

    if errors:
        print(f"FAIL: {len(errors)} problem(s) found\n", file=sys.stderr)
        for error in errors:
            print(f"  * {error}\n", file=sys.stderr)
        print(
            "Source of truth: AGENTS.md, ARCHITECTURE.md, and "
            ".agents/knowledge/skill-quality.md. "
            "Re-run with `just validate` after fixing.",
            file=sys.stderr,
        )
        return 1
    suffix = f" ({len(warnings)} warning(s))" if warnings else ""
    print(f"OK: skill layout and harness consistency checks passed{suffix}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
