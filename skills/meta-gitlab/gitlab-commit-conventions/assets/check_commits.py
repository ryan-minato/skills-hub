#!/usr/bin/env python3
"""Commit-message validator. Copy into the target repository at
scripts/check_commits.py and edit CONFIG to match the project's commit
convention document. Python 3.9+ stdlib only.

Usage:
    python3 scripts/check_commits.py --range BASE..HEAD   # validate commits in a git range
    python3 scripts/check_commits.py --file MSG_FILE      # validate one message from a file
    python3 scripts/check_commits.py --message "..."      # validate one message string

Findings go to stdout, one line each. Exit codes: 0 = all messages
compliant; 1 = findings; 2 = bad arguments or git failure.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys

# ---------------------------------------------------------------------------
# Edit this block to match the project's commit convention document.
CONFIG = {
    # Allowed Conventional Commits types.
    "types": [
        "build",
        "chore",
        "ci",
        "docs",
        "feat",
        "fix",
        "perf",
        "refactor",
        "revert",
        "style",
        "test",
    ],
    # None = scope optional and free-form; [] = scope forbidden;
    # a non-empty list = scope required and must be one of these.
    "allowed_scopes": None,
    # Maximum length of the title line.
    "subject_max": 72,
    # Maximum length of body lines (None disables the check).
    "body_line_max": 72,
    # Titles matching any of these regexes are exempt from all checks.
    "exempt_patterns": [r"^Merge ", r"^Revert ", r"^fixup!", r"^squash!"],
}
# ---------------------------------------------------------------------------

TITLE_RE = re.compile(r"^(?P<type>[a-z]+)(?:\((?P<scope>[^)]*)\))?(?P<bang>!)?: (?P<subject>.+)$")


def check_message(message: str, label: str) -> list[str]:
    findings = []
    lines = message.strip("\n").split("\n")
    title = lines[0]

    for pattern in CONFIG["exempt_patterns"]:
        if re.match(pattern, title):
            return []

    if len(title) > CONFIG["subject_max"]:
        findings.append(
            f"{label}: title is {len(title)} characters; max {CONFIG['subject_max']}"
        )

    match = TITLE_RE.match(title)
    if not match:
        findings.append(
            f"{label}: title does not match 'type(scope)!: subject' — got {title!r}"
        )
        return findings

    if match.group("type") not in CONFIG["types"]:
        allowed = ", ".join(CONFIG["types"])
        findings.append(
            f"{label}: unknown type {match.group('type')!r}; allowed: {allowed}"
        )

    scope = match.group("scope")
    allowed_scopes = CONFIG["allowed_scopes"]
    if allowed_scopes == [] and scope is not None:
        findings.append(f"{label}: scopes are not used in this project")
    elif isinstance(allowed_scopes, list) and allowed_scopes:
        if scope is None:
            findings.append(f"{label}: a scope is required")
        else:
            bad = [
                s.strip()
                for s in scope.split(",")
                if s.strip() and s.strip() not in allowed_scopes
            ]
            if bad:
                findings.append(
                    f"{label}: scope(s) {', '.join(bad)} not in the allowed set"
                )

    if match.group("subject").rstrip().endswith("."):
        findings.append(f"{label}: subject ends with a period")

    if len(lines) > 1 and lines[1].strip():
        findings.append(f"{label}: missing blank line between title and body")

    if CONFIG["body_line_max"]:
        for number, line in enumerate(lines[1:], start=2):
            if len(line) > CONFIG["body_line_max"] and " " in line.strip():
                findings.append(
                    f"{label}: body line {number} is {len(line)} characters; "
                    f"max {CONFIG['body_line_max']}"
                )

    return findings


def messages_from_range(git_range: str) -> list[tuple[str, str]]:
    # %x01/%x00 are expanded by git itself — a literal NUL cannot be
    # passed inside a subprocess argument.
    try:
        proc = subprocess.run(
            ["git", "log", "--format=%h%x01%B%x00", git_range],
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        print("git is not installed or not on PATH", file=sys.stderr)
        sys.exit(2)
    if proc.returncode != 0:
        sys.stderr.write(proc.stderr)
        sys.exit(2)
    out = []
    for record in proc.stdout.split("\x00"):
        record = record.strip("\n")
        if not record:
            continue
        sha, _, body = record.partition("\x01")
        out.append((sha, body))
    return out


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="check_commits.py", description="Validate commit messages"
    )
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--range", dest="git_range", help="git range BASE..HEAD")
    source.add_argument("--file", help="path to one commit message file")
    source.add_argument("--message", help="one commit message string")
    args = parser.parse_args()

    if args.git_range is not None:
        targets = messages_from_range(args.git_range)
    elif args.file is not None:
        try:
            with open(args.file, encoding="utf-8") as handle:
                targets = [("message", handle.read())]
        except OSError as exc:
            print(f"cannot read {args.file}: {exc}", file=sys.stderr)
            sys.exit(2)
    else:
        targets = [("message", args.message)]

    findings = []
    for label, message in targets:
        findings.extend(check_message(message, label))

    for finding in findings:
        print(finding)
    if findings:
        sys.exit(1)
    print(f"OK: {len(targets)} message(s) compliant")


if __name__ == "__main__":
    main()
