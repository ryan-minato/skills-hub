#!/usr/bin/env python3
"""Analyze a repository's commit-message history to ground a convention.

Reads recent commits from the git repository in --repo-dir (default: the
current directory) and reports, as one JSON object on stdout: how many
titles follow a Conventional-Commits-style `type:` prefix or a gitmoji
prefix, the type and scope frequencies, subject-length statistics, and
the trailer keys in use. Read-only; makes no network calls.

Usage:
    python3 scripts/analyze_history.py [--repo-dir PATH] [--max 500]

Exit codes: 0 = report printed; 1 = git failed (not a repository, or no
commits); 2 = bad arguments or git not installed.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys

CC_RE = re.compile(r"^(?P<type>[a-z]+)(?:\((?P<scope>[^)]*)\))?(?P<bang>!)?: \S")
GITMOJI_RE = re.compile(r"^(:\w+:|[\U0001F000-\U0001FAFF←-⯿])")
EXEMPT_RE = re.compile(r"^(Merge |Revert |fixup!|squash!)")
TRAILER_RE = re.compile(r"^([A-Za-z][A-Za-z-]*): \S")

RECORD_SEP = "\x00"
UNIT_SEP = "\x01"


def read_commits(repo_dir: str, limit: int) -> list[tuple[str, str]]:
    try:
        # %x01/%x00 are expanded by git itself — a literal NUL cannot be
        # passed inside a subprocess argument.
        proc = subprocess.run(
            [
                "git",
                "-C",
                repo_dir,
                "log",
                f"-n{limit}",
                "--format=%s%x01%B%x00",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        print("git is not installed or not on PATH", file=sys.stderr)
        sys.exit(2)
    if proc.returncode != 0:
        sys.stderr.write(proc.stderr)
        sys.exit(1)
    commits = []
    for record in proc.stdout.split(RECORD_SEP):
        record = record.strip("\n")
        if not record:
            continue
        subject, _, body = record.partition(UNIT_SEP)
        commits.append((subject, body))
    if not commits:
        print("no commits found", file=sys.stderr)
        sys.exit(1)
    return commits


def percentile(sorted_values: list[int], pct: float) -> int:
    if not sorted_values:
        return 0
    index = min(len(sorted_values) - 1, int(round(pct * (len(sorted_values) - 1))))
    return sorted_values[index]


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="analyze_history.py",
        description="Report commit-message style statistics as JSON",
    )
    parser.add_argument("--repo-dir", default=".", help="repository to analyze")
    parser.add_argument("--max", type=int, default=500, help="commits to scan")
    args = parser.parse_args()

    commits = read_commits(args.repo_dir, args.max)

    styles = {"conventional": 0, "gitmoji": 0, "exempt": 0, "other": 0}
    types: dict[str, int] = {}
    scopes: dict[str, int] = {}
    trailers: dict[str, int] = {}
    breaking = 0
    lengths: list[int] = []

    for subject, body in commits:
        if EXEMPT_RE.match(subject):
            styles["exempt"] += 1
            continue
        lengths.append(len(subject))
        cc = CC_RE.match(subject)
        if cc:
            styles["conventional"] += 1
            types[cc.group("type")] = types.get(cc.group("type"), 0) + 1
            if cc.group("scope"):
                for scope in cc.group("scope").split(","):
                    scope = scope.strip()
                    if scope:
                        scopes[scope] = scopes.get(scope, 0) + 1
            if cc.group("bang"):
                breaking += 1
        elif GITMOJI_RE.match(subject):
            styles["gitmoji"] += 1
        else:
            styles["other"] += 1
        for line in body.splitlines():
            trailer = TRAILER_RE.match(line)
            if trailer and line != subject:
                key = trailer.group(1)
                if key.lower() in {"http", "https", "note", "warning"}:
                    continue
                trailers[key] = trailers.get(key, 0) + 1
        if "BREAKING CHANGE:" in body:
            breaking += 1

    lengths.sort()
    report = {
        "commits_scanned": len(commits),
        "title_styles": styles,
        "type_frequencies": dict(
            sorted(types.items(), key=lambda kv: -kv[1])
        ),
        "scope_frequencies": dict(
            sorted(scopes.items(), key=lambda kv: -kv[1])[:20]
        ),
        "subject_length": {
            "p50": percentile(lengths, 0.50),
            "p95": percentile(lengths, 0.95),
            "max": lengths[-1] if lengths else 0,
        },
        "breaking_markers": breaking,
        "trailer_keys": dict(
            sorted(trailers.items(), key=lambda kv: -kv[1])[:15]
        ),
    }
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
