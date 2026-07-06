#!/usr/bin/env python3
"""Install Agent Skills from the ryan-minato/skills library without Node.

This is the no-Node fallback for the ryan-minato-skills-installing skill.
It clones the library to a temp directory and copies the requested skill
folder(s) into the scope-appropriate location as real files (never a
symlink), so a project-scope install commits with the project.

Modes:
  install (default)  Copy one or more named skills to the destination.
  --list             Discovery: print every available skill (name, catalog,
                     description) instead of installing.
  --self-test        Check prerequisites (git present, temp dir writable).

Scope:
  project (default)  Copy into <cwd>/<agent-dir>/skills/<name>/.
  --global / -g      Copy into <home>/<agent-dir>/skills/<name>/.

Output (stdout):
  install : JSON {"scope","agent_dir","installed":[{name,catalog,dest}],
                  "skipped":[{name,dest,reason}]}
  --list  : a human table, or a JSON array with --json.
Diagnostics go to stderr.

Exit codes:
  0  success
  1  runtime failure (git missing, skill not found/ambiguous, copy error)
  2  invalid arguments
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

DEFAULT_REPO = "https://github.com/ryan-minato/skills.git"
DEFAULT_REF = "main"
DEFAULT_AGENT_DIR = ".claude"


def eprint(*args: object) -> None:
    print(*args, file=sys.stderr)


def parse_frontmatter(text: str) -> dict[str, str]:
    """Extract top-level scalar keys from a SKILL.md YAML frontmatter block.

    Handles single-line ``key: value`` and folded/literal block scalars
    (``key: >`` / ``key: |``) by joining their indented continuation lines.
    Only the keys needed for listing (name, description) are relied upon.
    """
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    # Collect the frontmatter body up to the closing fence.
    body: list[str] = []
    for line in lines[1:]:
        if line.strip() == "---":
            break
        body.append(line)

    result: dict[str, str] = {}
    i = 0
    while i < len(body):
        line = body[i]
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or ":" not in line:
            i += 1
            continue
        # Only treat unindented lines as top-level keys.
        if line[:1].isspace():
            i += 1
            continue
        key, _, rest = line.partition(":")
        key = key.strip()
        rest = rest.strip()
        if rest in (">", "|", ">-", "|-", ">+", "|+"):
            # Block scalar: gather the more-indented following lines.
            collected: list[str] = []
            i += 1
            while i < len(body) and (body[i].strip() == "" or body[i][:1].isspace()):
                collected.append(body[i].strip())
                i += 1
            result[key] = " ".join(p for p in collected if p).strip()
        else:
            result[key] = rest.strip().strip('"').strip("'")
            i += 1
    return result


def run_git_clone(repo: str, ref: str, dest: Path) -> None:
    try:
        subprocess.run(
            ["git", "clone", "--depth", "1", "--branch", ref, repo, str(dest)],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True,
        )
    except FileNotFoundError as exc:  # git not installed
        raise RuntimeError(
            "git is required for this fallback but was not found on PATH. "
            "Install git, or use the skills CLI via pnpm/npx instead."
        ) from exc
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(
            f"git clone of {repo} (ref {ref}) failed:\n{exc.stderr.strip()}"
        ) from exc


def discover_skills(clone: Path) -> list[dict[str, str]]:
    """Return {name, catalog, description} for every skill in the clone."""
    skills_root = clone / "skills"
    found: list[dict[str, str]] = []
    if not skills_root.is_dir():
        return found
    for skill_md in sorted(skills_root.glob("*/*/SKILL.md")):
        skill_dir = skill_md.parent
        meta = parse_frontmatter(skill_md.read_text(encoding="utf-8"))
        found.append(
            {
                "name": meta.get("name", skill_dir.name),
                "catalog": skill_dir.parent.name,
                "description": meta.get("description", ""),
            }
        )
    return found


def find_skill_dir(clone: Path, name: str) -> Path:
    """Locate skills/<catalog>/<name>/; error if missing or ambiguous."""
    matches = [p for p in clone.glob(f"skills/*/{name}") if (p / "SKILL.md").is_file()]
    if not matches:
        raise RuntimeError(
            f"skill '{name}' not found in the library. "
            f"Run with --list to see available skills."
        )
    if len(matches) > 1:
        catalogs = ", ".join(sorted(p.parent.name for p in matches))
        raise RuntimeError(
            f"skill '{name}' is ambiguous (found in catalogs: {catalogs})."
        )
    return matches[0]


def dest_root(agent_dir: str, is_global: bool) -> Path:
    base = Path.home() if is_global else Path.cwd()
    return base / agent_dir / "skills"


def cmd_list(args: argparse.Namespace) -> int:
    tmp = Path(tempfile.mkdtemp(prefix="skills-list-"))
    try:
        run_git_clone(args.repo, args.ref, tmp)
        skills = discover_skills(tmp)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    if args.json:
        print(json.dumps(skills, indent=2, ensure_ascii=False))
        return 0

    if not skills:
        eprint("No skills found in the library.")
        return 1
    name_w = max(len(s["name"]) for s in skills)
    cat_w = max(len(s["catalog"]) for s in skills)
    for s in skills:
        desc = " ".join(s["description"].split())
        if len(desc) > 100:
            desc = desc[:97] + "..."
        print(f"{s['name']:<{name_w}}  {s['catalog']:<{cat_w}}  {desc}")
    return 0


def cmd_install(args: argparse.Namespace) -> int:
    names: list[str] = list(dict.fromkeys(args.names + args.skill))
    if not names:
        eprint("No skill name given. Pass one or more names, or use --list.")
        return 2

    root = dest_root(args.agent_dir, args.is_global)
    tmp = Path(tempfile.mkdtemp(prefix="skills-install-"))
    installed: list[dict[str, str]] = []
    skipped: list[dict[str, str]] = []
    try:
        run_git_clone(args.repo, args.ref, tmp)
        # Resolve every name up front so a bad name fails before any copy.
        resolved = {name: find_skill_dir(tmp, name) for name in names}

        root.mkdir(parents=True, exist_ok=True)
        for name, src in resolved.items():
            dest = root / name
            if dest.exists():
                if not args.force:
                    skipped.append(
                        {
                            "name": name,
                            "dest": str(dest),
                            "reason": "already installed; pass --force to replace",
                        }
                    )
                    continue
                shutil.rmtree(dest)
            shutil.copytree(src, dest)
            installed.append(
                {"name": name, "catalog": src.parent.name, "dest": str(dest)}
            )
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print(
        json.dumps(
            {
                "scope": "global" if args.is_global else "project",
                "agent_dir": args.agent_dir,
                "installed": installed,
                "skipped": skipped,
            },
            indent=2,
            ensure_ascii=False,
        )
    )
    return 0


def cmd_self_test(args: argparse.Namespace) -> int:
    ok = True
    if shutil.which("git") is None:
        eprint("FAIL: git not found on PATH")
        ok = False
    else:
        print("OK: git present")
    try:
        probe = Path(tempfile.mkdtemp(prefix="skills-selftest-"))
        (probe / "probe").write_text("ok", encoding="utf-8")
        shutil.rmtree(probe, ignore_errors=True)
        print("OK: temp dir writable")
    except OSError as exc:
        eprint(f"FAIL: cannot write temp dir: {exc}")
        ok = False
    return 0 if ok else 1


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="install_skill.py",
        description="Install skills from the ryan-minato/skills library (no-Node fallback).",
    )
    p.add_argument("names", nargs="*", help="skill name(s) to install")
    p.add_argument(
        "-s",
        "--skill",
        action="append",
        default=[],
        metavar="NAME",
        help="additional skill name to install (repeatable)",
    )
    p.add_argument(
        "-g",
        "--global",
        dest="is_global",
        action="store_true",
        help="install into the user home agent dir instead of the project",
    )
    p.add_argument(
        "--agent-dir",
        default=DEFAULT_AGENT_DIR,
        help=f"per-agent skills root (default: {DEFAULT_AGENT_DIR}; e.g. .codex)",
    )
    p.add_argument(
        "--repo",
        default=DEFAULT_REPO,
        help="source repo; only for a fork/mirror of this same library",
    )
    p.add_argument(
        "--ref", default=DEFAULT_REF, help=f"git ref (default: {DEFAULT_REF})"
    )
    p.add_argument(
        "--force", action="store_true", help="replace an already-installed skill"
    )
    p.add_argument(
        "--list", action="store_true", help="list available skills; do not install"
    )
    p.add_argument(
        "--json", action="store_true", help="machine-readable output for --list"
    )
    p.add_argument(
        "--self-test", action="store_true", help="check prerequisites and exit"
    )
    return p


def main(argv: list[str]) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.self_test:
            return cmd_self_test(args)
        if args.list:
            return cmd_list(args)
        return cmd_install(args)
    except RuntimeError as exc:
        eprint(f"error: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
