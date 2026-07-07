#!/usr/bin/env python3
"""Sync a GitLab project's or group's labels to a JSON taxonomy file via glab.

Reads the desired labels from a JSON array of {"name", "color",
"description"} objects, compares them with the labels currently on the
target project or group, and prints the resulting plan as JSON to stdout.
Dry-run by default: nothing changes without --apply. Idempotent: re-running
after a successful apply yields an all-in-sync plan.

All GitLab access shells out to `glab api --hostname HOST`, so glab must be
on PATH and authenticated for the target host (the gitlab-tooling-setup
skill covers both). In project mode, labels inherited from ancestor groups
are reported under "group_managed" and never modified; --prune deletes only
labels defined on the project itself.

Exit codes: 0 plan printed or applied cleanly, 1 glab missing or a glab
command failed, 2 bad arguments or an invalid labels file.
"""

import argparse
import json
import os
import re
import subprocess
import sys
import urllib.parse

HEX_COLOR = re.compile(r"^[0-9a-f]{6}$")
PROJECT_PATH = re.compile(r"^[^/\s]+(?:/[^/\s]+)+$")
GROUP_PATH = re.compile(r"^[^/\s]+(?:/[^/\s]+)*$")
SCP_REMOTE = re.compile(r"^(?:[^@/\s]+@)?([^:/\s]+):")

TOOLING_HINT = (
    "install and authenticate glab for this host with the "
    "gitlab-tooling-setup skill (npx skills add ryan-minato/skills)"
)


def fail(code, message):
    print(f"sync_labels: error: {message}", file=sys.stderr)
    sys.exit(code)


def run_glab(argv, context, hint=None):
    """Run a glab command; return stdout, or exit 1 with glab's error."""
    try:
        proc = subprocess.run(
            ["glab"] + argv, capture_output=True, text=True, check=False
        )
    except FileNotFoundError:
        fail(1, f"glab CLI not found on PATH — {TOOLING_HINT}")
    if proc.returncode != 0:
        detail = proc.stderr.strip() or proc.stdout.strip() or "(no output)"
        message = f"{context}: 'glab {' '.join(argv)}' failed: {detail}"
        if hint:
            message = f"{message}\n  {hint}"
        fail(1, message)
    return proc.stdout


def normalize_color(raw, context):
    color = str(raw).strip().lstrip("#").lower()
    if not HEX_COLOR.match(color):
        fail(
            2,
            f"{context}: color {raw!r} is not a 6-digit hex value "
            '(use e.g. "#d73a4a" or "d73a4a")',
        )
    return f"#{color}"


def load_desired(path):
    try:
        with open(path, encoding="utf-8") as handle:
            data = json.load(handle)
    except OSError as exc:
        fail(2, f"cannot read {path}: {exc}")
    except json.JSONDecodeError as exc:
        fail(2, f"{path} is not valid JSON: {exc}")
    if not isinstance(data, list):
        fail(2, f"{path} must be a JSON array of label objects")
    labels = []
    seen = set()
    for index, item in enumerate(data):
        context = f"{path}[{index}]"
        if not isinstance(item, dict) or not str(item.get("name", "")).strip():
            fail(2, f"{context} must be an object with a non-empty 'name'")
        name = str(item["name"]).strip()
        key = name.lower()
        if key in seen:
            fail(2, f"{context}: duplicate label name {name!r} (case-insensitive)")
        seen.add(key)
        labels.append(
            {
                "name": name,
                "color": normalize_color(item.get("color", ""), context),
                "description": str(item.get("description") or "").strip(),
            }
        )
    if not labels:
        fail(2, f"{path} contains no labels")
    return labels


def host_from_remote_url(url):
    """Extract the host from an https://, ssh://, or scp-style git URL."""
    url = url.strip()
    if "://" in url:
        return urllib.parse.urlsplit(url).hostname
    match = SCP_REMOTE.match(url)
    if match:
        return match.group(1)
    return None


def clean_host(value):
    host = value.strip()
    if "://" in host:
        parsed = urllib.parse.urlsplit(host)
        host = parsed.netloc or parsed.path
    if "@" in host:
        host = host.rsplit("@", 1)[1]
    return host.strip("/")


def resolve_host(cli_value):
    """Resolve the GitLab host: --host, then origin remote, then env vars."""
    if cli_value:
        return clean_host(cli_value)
    proc = subprocess.run(
        ["git", "remote", "get-url", "origin"],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode == 0:
        host = host_from_remote_url(proc.stdout)
        if host:
            return host
    for name in ("GITLAB_HOST", "GL_HOST"):
        value = os.environ.get(name)
        if value and value.strip():
            return clean_host(value)
    fail(
        2,
        "cannot determine the GitLab host: no 'origin' git remote here and "
        "neither GITLAB_HOST nor GL_HOST is set — pass --host HOST (never "
        "assumed to be gitlab.com)",
    )


def parse_paginated_json(text, context):
    """Parse `glab api --paginate` output: concatenated JSON arrays."""
    decoder = json.JSONDecoder()
    entries = []
    index = 0
    length = len(text)
    while index < length:
        while index < length and text[index].isspace():
            index += 1
        if index >= length:
            break
        try:
            document, index = decoder.raw_decode(text, index)
        except json.JSONDecodeError:
            fail(1, f"{context}: could not parse glab api output as JSON")
        if not isinstance(document, list):
            fail(1, f"{context}: expected a JSON array from glab api")
        entries.extend(document)
    return entries


def fetch_current(host, kind, encoded_path):
    """List labels; return (editable_by_key, inherited_by_key) dicts."""
    if kind == "project":
        endpoint = (
            f"projects/{encoded_path}/labels"
            "?with_counts=false&per_page=100&include_ancestor_groups=true"
        )
    else:
        endpoint = (
            f"groups/{encoded_path}/labels"
            "?with_counts=false&per_page=100&include_ancestor_groups=false"
        )
    context = f"listing labels on {kind} via {host}"
    stdout = run_glab(
        ["api", "--hostname", host, endpoint, "--paginate"],
        context,
        hint=TOOLING_HINT,
    )
    editable, inherited = {}, {}
    for entry in parse_paginated_json(stdout, context):
        record = {
            "id": entry.get("id"),
            "name": str(entry.get("name", "")),
            "color": str(entry.get("color", "")).strip().lower(),
            "description": str(entry.get("description") or "").strip(),
        }
        if record["color"] and not record["color"].startswith("#"):
            record["color"] = f"#{record['color']}"
        key = record["name"].lower()
        if kind == "group" or entry.get("is_project_label"):
            editable[key] = record
        else:
            inherited[key] = record
    return editable, inherited


def build_plan(desired, editable, inherited):
    create, update, in_sync, group_managed = [], [], [], []
    for label in desired:
        key = label["name"].lower()
        if key in editable:
            existing = editable[key]
            changes = []
            if existing["name"] != label["name"]:
                changes.append("name-case")
            if existing["color"] != label["color"]:
                changes.append("color")
            if existing["description"] != label["description"]:
                changes.append("description")
            if changes:
                entry = {
                    "id": existing["id"],
                    "name": existing["name"],
                    "color": label["color"],
                    "description": label["description"],
                    "changes": changes,
                }
                if "name-case" in changes:
                    entry["new_name"] = label["name"]
                update.append(entry)
            else:
                in_sync.append(label["name"])
        elif key in inherited:
            existing = inherited[key]
            entry = {"name": label["name"], "group_label": existing["name"]}
            if (
                existing["color"] != label["color"]
                or existing["description"] != label["description"]
            ):
                entry["warning"] = (
                    "color/description in the file differ from the inherited "
                    "group label; edit it on the ancestor group instead"
                )
            group_managed.append(entry)
        else:
            create.append(label)
    desired_keys = {label["name"].lower() for label in desired}
    prune = [
        {"id": entry["id"], "name": entry["name"]}
        for key, entry in sorted(editable.items())
        if key not in desired_keys
    ]
    return create, update, in_sync, group_managed, prune


def apply_plan(host, kind, encoded_path, create, update, prune, do_prune):
    base = f"{'projects' if kind == 'project' else 'groups'}/{encoded_path}/labels"
    hint = (
        "operations completed before this failure remain applied; fix the "
        "error and re-run the same command — the sync is idempotent"
    )
    applied = {"created": 0, "updated": 0, "deleted": 0}
    for label in create:
        print(f"create: {label['name']}", file=sys.stderr)
        run_glab(
            [
                "api",
                "--hostname",
                host,
                "-X",
                "POST",
                base,
                "-f",
                f"name={label['name']}",
                "-f",
                f"color={label['color']}",
                "-f",
                f"description={label['description']}",
            ],
            f"creating label {label['name']!r}",
            hint=hint,
        )
        applied["created"] += 1
    for entry in update:
        print(f"update: {entry['name']}", file=sys.stderr)
        argv = [
            "api",
            "--hostname",
            host,
            "-X",
            "PUT",
            f"{base}/{entry['id']}",
            "-f",
            f"color={entry['color']}",
            "-f",
            f"description={entry['description']}",
        ]
        if "new_name" in entry:
            argv += ["-f", f"new_name={entry['new_name']}"]
        run_glab(argv, f"updating label {entry['name']!r}", hint=hint)
        applied["updated"] += 1
    if do_prune:
        for entry in prune:
            print(f"delete: {entry['name']}", file=sys.stderr)
            run_glab(
                [
                    "api",
                    "--hostname",
                    host,
                    "-X",
                    "DELETE",
                    f"{base}/{entry['id']}",
                ],
                f"deleting label {entry['name']!r}",
                hint=hint,
            )
            applied["deleted"] += 1
    return applied


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Sync a GitLab project's or group's labels to a JSON taxonomy "
            "file through the glab CLI. Dry-run by default: prints the "
            "create/update/in_sync/group_managed/prune plan as JSON to "
            "stdout without changing anything; re-run with --apply to "
            "execute it. Labels inherited from ancestor groups are never "
            "modified."
        ),
        epilog=(
            "Host resolution without --host: the host of the 'origin' git "
            "remote of the current directory (used as-is, even if it is not "
            "a GitLab host — pass --host to override), then GITLAB_HOST or "
            "GL_HOST, then an error; gitlab.com is never assumed. Exit "
            "codes: 0 plan printed or applied cleanly, 1 glab missing or "
            "failed, 2 bad arguments or invalid labels file."
        ),
    )
    parser.add_argument(
        "--file",
        required=True,
        help=(
            "path to the labels JSON file: an array of "
            '{"name", "color", "description"} objects; color is 6-digit hex '
            "with or without the leading '#'"
        ),
    )
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument(
        "--project",
        help="target project as GROUP[/SUBGROUP]/NAME (full nested path)",
    )
    target.add_argument(
        "--group",
        help="target group as GROUP[/SUBGROUP] (labels managed on the group)",
    )
    parser.add_argument(
        "--host",
        help=(
            "GitLab host, e.g. gitlab.com or gitlab.example.com (overrides "
            "the origin-remote and GITLAB_HOST/GL_HOST defaults)"
        ),
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="execute the plan (default: dry-run, print the plan only)",
    )
    parser.add_argument(
        "--prune",
        action="store_true",
        help=(
            "with --apply, delete project- or group-defined labels absent "
            "from the file (inherited group labels are never deleted)"
        ),
    )
    args = parser.parse_args()

    if args.prune and not args.apply:
        fail(
            2,
            "--prune requires --apply; the dry-run plan already lists prune candidates",
        )
    if args.project is not None:
        kind, path = "project", args.project.strip().strip("/")
        if not PROJECT_PATH.match(path):
            fail(2, f"--project must be GROUP[/SUBGROUP]/NAME, got {args.project!r}")
    else:
        kind, path = "group", args.group.strip().strip("/")
        if not GROUP_PATH.match(path):
            fail(2, f"--group must be GROUP[/SUBGROUP], got {args.group!r}")

    host = resolve_host(args.host)
    encoded_path = urllib.parse.quote(path, safe="")
    desired = load_desired(args.file)
    editable, inherited = fetch_current(host, kind, encoded_path)
    create, update, in_sync, group_managed, prune = build_plan(
        desired, editable, inherited
    )

    plan = {
        "host": host,
        "target": {"kind": kind, "path": path},
        "mode": "apply" if args.apply else "plan",
        "create": create,
        "update": update,
        "in_sync": in_sync,
        "group_managed": group_managed,
        "prune": prune,
    }
    if args.apply:
        plan["applied"] = apply_plan(
            host, kind, encoded_path, create, update, prune, args.prune
        )
    json.dump(plan, sys.stdout, indent=2)
    print()


if __name__ == "__main__":
    main()
