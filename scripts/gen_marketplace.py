#!/usr/bin/env python3
"""Regenerate each plugin's `skills[]` in .claude-plugin/marketplace.json.

Every catalog plugin (its `name` equals a catalog directory under skills/)
gets its `skills` array rewritten to the sorted list of that catalog's skill
directories (`./skills/<catalog>/<skill>`). Those exact paths are what the
vercel `skills` CLI matches to group the picker by catalog, and what Claude
Code loads as the plugin's skills.

Human-owned fields (name, source, strict, description) and plugin order are
preserved; the generator never adds or removes plugin entries. A non-empty
catalog with no entry, or an entry whose catalog is empty/missing, is reported
to stderr (the validator turns those into hard errors).

Modes:
  (default)  Rewrite marketplace.json in place.
  --check    Do not write; exit 1 if any plugin's skills[] is out of sync.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = REPO_ROOT / "skills"
MARKETPLACE = REPO_ROOT / ".claude-plugin" / "marketplace.json"


def catalog_skill_paths(catalog: str) -> list[str]:
    """Sorted `./skills/<catalog>/<skill>` for every skill dir in the catalog."""
    cat_dir = SKILLS_DIR / catalog
    if not cat_dir.is_dir():
        return []
    return sorted(
        f"./skills/{catalog}/{d.name}"
        for d in cat_dir.iterdir()
        if d.is_dir() and (d / "SKILL.md").is_file()
    )


def coverage_warnings(listed: set[str]) -> list[str]:
    warnings: list[str] = []
    if not SKILLS_DIR.is_dir():
        return warnings
    for cat in sorted(p.name for p in SKILLS_DIR.iterdir() if p.is_dir()):
        if cat not in listed and catalog_skill_paths(cat):
            warnings.append(
                f"catalog `{cat}` has skills but no plugin entry; add one with "
                f"a name and description, then re-run."
            )
    return warnings


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="do not write; exit 1 if any plugin's skills[] is out of sync",
    )
    args = parser.parse_args(argv)

    manifest = json.loads(MARKETPLACE.read_text(encoding="utf-8"))
    plugins = manifest.get("plugins", [])

    mismatches: list[str] = []
    listed: set[str] = set()
    for entry in plugins:
        name = entry.get("name", "")
        listed.add(name)
        expected = catalog_skill_paths(name)
        if not expected:
            print(
                f"WARNING: plugin `{name}`: catalog skills/{name}/ is empty or "
                f"missing; remove the entry or add a skill.",
                file=sys.stderr,
            )
        if args.check:
            if entry.get("skills") != expected:
                mismatches.append(name)
        else:
            entry["skills"] = expected

    for warning in coverage_warnings(listed):
        print(f"WARNING: {warning}", file=sys.stderr)

    if args.check:
        if mismatches:
            print(
                "marketplace.json skills[] out of sync for: "
                f"{', '.join(sorted(mismatches))}. Fix: run `just gen-marketplace`.",
                file=sys.stderr,
            )
            return 1
        print("OK: marketplace.json skills[] are in sync.")
        return 0

    MARKETPLACE.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(f"Wrote {MARKETPLACE.relative_to(REPO_ROOT)}.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
