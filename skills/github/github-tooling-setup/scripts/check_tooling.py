#!/usr/bin/env python3
"""Probe the local environment for GitHub tooling and print a JSON report.

Usage:
    python3 scripts/check_tooling.py [--skip-network]

Probes (all read-only; nothing is installed or changed):
- gh:        whether the GitHub CLI is on PATH, its version (first line of
             `gh --version`), and whether `gh auth status` exits 0
             (authenticated true/false).
- docker:    whether docker is on PATH and its version.
- token_env: which of GH_TOKEN, GITHUB_TOKEN, GITHUB_PERSONAL_ACCESS_TOKEN,
             and GITHUB_PAT are set. Only names and set/unset booleans are
             reported; token values are never printed.
- network:   HTTPS reachability of https://api.github.com and
             https://api.githubcopilot.com/ (any HTTP response, including
             401, counts as reachable). Disabled by --skip-network.

This script cannot see MCP session state. Whether a GitHub MCP server is
connected can only be answered by inspecting the agent's own tool list.

Output: one JSON object on stdout; diagnostics on stderr. Idempotent —
safe to re-run any number of times.

Exit codes: 0 = all probes ran (missing tooling is data, not a failure),
1 = a probe crashed unexpectedly, 2 = bad arguments.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import urllib.error
import urllib.request

TOKEN_ENV_VARS = (
    "GH_TOKEN",
    "GITHUB_TOKEN",
    "GITHUB_PERSONAL_ACCESS_TOKEN",
    "GITHUB_PAT",
)

NETWORK_ENDPOINTS = (
    "https://api.github.com",
    "https://api.githubcopilot.com/",
)

SUBPROCESS_TIMEOUT = 30
NETWORK_TIMEOUT = 5


def run_command(argv: list[str]) -> tuple[int, str]:
    """Run a command; return (exit code, first line of stdout).

    Returns (-1, "") when the command cannot be run at all; that is
    recorded as data, with a diagnostic on stderr.
    """
    try:
        proc = subprocess.run(
            argv,
            capture_output=True,
            text=True,
            timeout=SUBPROCESS_TIMEOUT,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        print(f"warning: `{' '.join(argv)}` failed to run: {exc}", file=sys.stderr)
        return -1, ""
    stdout = proc.stdout.strip()
    return proc.returncode, stdout.splitlines()[0] if stdout else ""


def probe_gh() -> dict:
    result: dict = {"installed": False, "version": None, "authenticated": False}
    if shutil.which("gh") is None:
        return result
    result["installed"] = True
    _, version = run_command(["gh", "--version"])
    result["version"] = version or None
    exit_code, _ = run_command(["gh", "auth", "status"])
    result["authenticated"] = exit_code == 0
    return result


def probe_docker() -> dict:
    result: dict = {"installed": False, "version": None}
    if shutil.which("docker") is None:
        return result
    result["installed"] = True
    _, version = run_command(["docker", "--version"])
    result["version"] = version or None
    return result


def probe_token_env() -> dict:
    # Booleans only: never read token values into the report.
    return {name: bool(os.environ.get(name)) for name in TOKEN_ENV_VARS}


def probe_network(skip: bool) -> dict:
    result: dict = {"skipped": skip, "reachable": {}}
    if skip:
        return result
    for url in NETWORK_ENDPOINTS:
        request = urllib.request.Request(
            url, headers={"User-Agent": "check-tooling-probe"}
        )
        try:
            with urllib.request.urlopen(request, timeout=NETWORK_TIMEOUT):
                reachable = True
        except urllib.error.HTTPError:
            # An HTTP status (401, 403, ...) is still a response: reachable.
            reachable = True
        except (urllib.error.URLError, OSError) as exc:
            print(f"warning: {url} unreachable: {exc}", file=sys.stderr)
            reachable = False
        result["reachable"][url] = reachable
    return result


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Probe gh, docker, GitHub token environment variables, and "
            "GitHub endpoint reachability; print one JSON object to stdout. "
            "Exit codes: 0 = probes ran (missing tooling is data, not "
            "failure), 1 = a probe crashed unexpectedly, 2 = bad arguments."
        ),
    )
    parser.add_argument(
        "--skip-network",
        action="store_true",
        help="skip the HTTPS reachability probes (for offline environments)",
    )
    args = parser.parse_args()

    try:
        report = {
            "gh": probe_gh(),
            "docker": probe_docker(),
            "token_env": probe_token_env(),
            "network": probe_network(args.skip_network),
        }
    except Exception as exc:  # any probe crash is exit 1, per the contract
        print(f"error: a probe crashed unexpectedly: {exc}", file=sys.stderr)
        return 1

    json.dump(report, sys.stdout, indent=2)
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
