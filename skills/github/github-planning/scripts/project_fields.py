#!/usr/bin/env python3
"""Resolve GitHub Projects v2 node IDs for gh project item-edit.

gh project item-edit takes GraphQL node IDs (--project-id, --field-id,
--single-select-option-id, --id), which the human-facing commands do not
surface directly. This script resolves them from the project number and
human-readable names via gh's JSON output.

Usage:
    python3 scripts/project_fields.py --owner OWNER --number N \\
        [--field "Status" [--option "In Progress"]] [--item-url URL]

Output: one JSON object on stdout —
    {"project_id": ..., "field_id": ..., "option_id": ..., "item_id": ...}
with null for anything not requested. Name matching is case-insensitive.

Exit codes: 0 = resolved; 1 = a name/url was not found (candidates are
listed on stderr) or gh failed; 2 = bad arguments or gh not installed.
Requires an authenticated gh CLI with the project token scope.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys


def run_gh(cli_args: list[str]) -> dict:
    try:
        proc = subprocess.run(
            ["gh", *cli_args], capture_output=True, text=True, check=False
        )
    except FileNotFoundError:
        print("gh is not installed or not on PATH", file=sys.stderr)
        sys.exit(2)
    if proc.returncode != 0:
        sys.stderr.write(proc.stderr)
        sys.exit(1)
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        print(f"unexpected non-JSON output from gh: {exc}", file=sys.stderr)
        sys.exit(1)


def fail_with_candidates(kind: str, wanted: str, names: list[str]) -> None:
    listing = ", ".join(sorted(n for n in names if n)) or "(none)"
    print(f"{kind} {wanted!r} not found; available: {listing}", file=sys.stderr)
    sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="project_fields.py",
        description=(
            "Resolve Projects v2 node IDs (project, field, option, item) "
            "for gh project item-edit"
        ),
    )
    parser.add_argument("--owner", required=True, help="user login, org, or @me")
    parser.add_argument("--number", type=int, required=True, help="project number")
    parser.add_argument("--field", help="field name, e.g. Status")
    parser.add_argument("--option", help="single-select option name; needs --field")
    parser.add_argument("--item-url", help="issue/PR URL to resolve to an item id")
    parser.add_argument(
        "--limit", type=int, default=500, help="items scanned for --item-url"
    )
    args = parser.parse_args()
    if args.option and not args.field:
        parser.error("--option requires --field")

    result = {
        "project_id": None,
        "field_id": None,
        "option_id": None,
        "item_id": None,
    }
    number = str(args.number)

    view = run_gh(["project", "view", number, "--owner", args.owner, "--format", "json"])
    result["project_id"] = view.get("id")

    if args.field:
        payload = run_gh(
            ["project", "field-list", number, "--owner", args.owner, "--format", "json"]
        )
        fields = payload.get("fields", [])
        field = next(
            (f for f in fields if f.get("name", "").lower() == args.field.lower()),
            None,
        )
        if field is None:
            fail_with_candidates("field", args.field, [f.get("name") for f in fields])
        result["field_id"] = field.get("id")
        if args.option:
            options = field.get("options") or []
            option = next(
                (
                    o
                    for o in options
                    if o.get("name", "").lower() == args.option.lower()
                ),
                None,
            )
            if option is None:
                fail_with_candidates(
                    "option", args.option, [o.get("name") for o in options]
                )
            result["option_id"] = option.get("id")

    if args.item_url:
        payload = run_gh(
            [
                "project",
                "item-list",
                number,
                "--owner",
                args.owner,
                "--limit",
                str(args.limit),
                "--format",
                "json",
            ]
        )
        items = payload.get("items", [])
        item = next(
            (
                i
                for i in items
                if (i.get("content") or {}).get("url") == args.item_url
            ),
            None,
        )
        if item is None:
            print(
                f"item with url {args.item_url} not found in the first "
                f"{args.limit} items",
                file=sys.stderr,
            )
            sys.exit(1)
        result["item_id"] = item.get("id")

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
