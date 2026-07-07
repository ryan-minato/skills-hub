#!/usr/bin/env python3
"""Probe the local environment for GitLab tooling and print a JSON report.

Usage:
    python3 scripts/check_tooling.py [--hostname HOST] [--skip-network]

Probes (all read-only; nothing is installed or changed):
- host:      the GitLab host being probed and where it came from
             (--hostname flag, GITLAB_HOST, GL_HOST, or the gitlab.com
             default).
- glab:      whether the glab CLI is on PATH, its version (first line of
             `glab --version`), and whether `glab auth status --hostname
             HOST` exits 0 (authenticated true/false for that host).
- token_env: which of GITLAB_TOKEN, GITLAB_ACCESS_TOKEN, and OAUTH_TOKEN
             are set. Only names and set/unset booleans are reported;
             token values are never printed. GITLAB_HOST/GL_HOST values
             are reported (hostnames are not secrets).
- network:   HTTPS reachability of https://HOST/api/v4/projects (any HTTP
             response, including 401, counts as reachable) and the HTTP
             status of https://HOST/api/v4/mcp — a 404 there means the
             instance is older than GitLab 18.6 or the Duo MCP server is
             unavailable/disabled; any other response means the endpoint
             exists. Disabled by --skip-network.

This script cannot see MCP session state. Whether a GitLab MCP server is
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
    "GITLAB_TOKEN",
    "GITLAB_ACCESS_TOKEN",
    "OAUTH_TOKEN",
)

HOST_ENV_VARS = ("GITLAB_HOST", "GL_HOST")

DEFAULT_HOST = "gitlab.com"

SUBPROCESS_TIMEOUT = 30
NETWORK_TIMEOUT = 5


def _bare_host(value: str) -> str:
    """Strip a scheme prefix and trailing slashes so the host can be
    interpolated into an endpoint URL."""
    return value.removeprefix("https://").removeprefix("http://").strip("/")


def resolve_host(flag_value: str | None) -> dict:
    """Resolve the host to probe: flag > GITLAB_HOST > GL_HOST > default."""
    if flag_value:
        return {"host": _bare_host(flag_value), "source": "--hostname"}
    for name in HOST_ENV_VARS:
        value = os.environ.get(name)
        if value:
            return {"host": _bare_host(value), "source": name}
    return {"host": DEFAULT_HOST, "source": "default"}


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


def probe_glab(host: str) -> dict:
    result: dict = {"installed": False, "version": None, "authenticated": False}
    if shutil.which("glab") is None:
        return result
    result["installed"] = True
    _, version = run_command(["glab", "--version"])
    result["version"] = version or None
    exit_code, _ = run_command(["glab", "auth", "status", "--hostname", host])
    result["authenticated"] = exit_code == 0
    return result


def probe_token_env() -> dict:
    # Booleans only for tokens: never read token values into the report.
    report = {name: bool(os.environ.get(name)) for name in TOKEN_ENV_VARS}
    # Host variables are not secrets; their values matter for debugging.
    report.update({name: os.environ.get(name) for name in HOST_ENV_VARS})
    return report


def http_status(url: str) -> int | None:
    """Return the HTTP status of a GET, or None when unreachable.

    One retry absorbs transient timeouts so a single blip is not
    reported as a missing endpoint.
    """
    request = urllib.request.Request(url, headers={"User-Agent": "check-tooling-probe"})
    last_error: Exception | None = None
    for _ in range(2):
        try:
            with urllib.request.urlopen(request, timeout=NETWORK_TIMEOUT) as response:
                return response.status
        except urllib.error.HTTPError as exc:
            # An HTTP status (401, 404, ...) is still a response.
            return exc.code
        except (urllib.error.URLError, OSError) as exc:
            last_error = exc
    print(f"warning: {url} unreachable: {last_error}", file=sys.stderr)
    return None


def probe_network(host: str, skip: bool) -> dict:
    result: dict = {"skipped": skip}
    if skip:
        return result
    rest_status = http_status(f"https://{host}/api/v4/projects")
    mcp_status = http_status(f"https://{host}/api/v4/mcp")
    result["rest_reachable"] = rest_status is not None
    result["mcp_endpoint_status"] = mcp_status
    result["mcp_endpoint_present"] = mcp_status is not None and mcp_status != 404
    return result


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Probe glab, GitLab token environment variables, and the "
            "GitLab host's REST and MCP endpoints; print one JSON object "
            "to stdout. Host resolution: --hostname > GITLAB_HOST > "
            "GL_HOST > gitlab.com. Exit codes: 0 = probes ran (missing "
            "tooling is data, not failure), 1 = a probe crashed "
            "unexpectedly, 2 = bad arguments."
        ),
    )
    parser.add_argument(
        "--hostname",
        "-H",
        help="GitLab host to probe (e.g. gitlab.example.com)",
    )
    parser.add_argument(
        "--skip-network",
        action="store_true",
        help="skip the HTTPS reachability probes (for offline environments)",
    )
    args = parser.parse_args()

    host_info = resolve_host(args.hostname)
    host = host_info["host"]

    try:
        report = {
            "host": host_info,
            "glab": probe_glab(host),
            "token_env": probe_token_env(),
            "network": probe_network(host, args.skip_network),
        }
    except Exception as exc:  # any probe crash is exit 1, per the contract
        print(f"error: a probe crashed unexpectedly: {exc}", file=sys.stderr)
        return 1

    json.dump(report, sys.stdout, indent=2)
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
