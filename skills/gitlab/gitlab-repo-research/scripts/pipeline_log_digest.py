#!/usr/bin/env python3
"""Digest a GitLab CI pipeline's failures into one compact JSON object.

Shells out to the glab CLI (must be installed and authenticated) and never
fetches full pipeline logs: it reads only the traces of failed jobs and
keeps the last N lines per job — cleaned of ANSI escape codes, GitLab
section markers, and carriage-return progress frames — so multi-megabyte
logs stay out of agent context.

Usage:
    python3 scripts/pipeline_log_digest.py --repo GROUP/PROJECT \\
        --pipeline-id ID [--tail N] [--hostname HOST]

    --repo         Project as its full path GROUP[/SUBGROUP]/NAME.
    --pipeline-id  Numeric pipeline id (from `glab ci list`).
    --tail         Log lines to keep per failed job (default 50).
    --hostname     Self-managed GitLab host, passed as `glab api --hostname`.

Output: a single JSON object on stdout:
    {"pipeline_id": ..., "status": ...,
     "failed_jobs": [{"job_id": ..., "name": ..., "stage": ...,
                      "failure_reason": ..., "log_tail": [...]}]}
A job whose trace could not be fetched (private project, expired trace)
carries an empty "log_tail" plus a "log_error" string, so a consumer can
tell a fetch failure apart from a job that produced no output.

Diagnostics go to stderr, never stdout.

Exit codes:
    0  digest produced (a successful pipeline digests to an empty
       failed_jobs list — that is data, not a failure)
    1  glab missing, glab errored, or pipeline not found
    2  bad arguments
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import urllib.parse

ANSI_ESCAPE_RE = re.compile(r"\x1b\[[0-9;?]*[ -/]*[@-~]|\x1b[@-Z\\^_]")
SECTION_MARKER_RE = re.compile(r"section_(?:start|end):\d+:[\w.-]+(?:\[[^\]]*\])?")


def log(message: str) -> None:
    """Print a diagnostic line to stderr."""
    print(message, file=sys.stderr)


def run_glab_api(endpoint: str, hostname: str | None) -> "subprocess.CompletedProcess":
    """Run `glab api ENDPOINT`, exiting 1 with guidance if glab is missing."""
    cmd = ["glab", "api"]
    if hostname:
        cmd += ["--hostname", hostname]
    cmd.append(endpoint)
    try:
        return subprocess.run(cmd, capture_output=True, text=True, check=False)
    except FileNotFoundError:
        log(
            "error: glab not found on PATH — install and authenticate the "
            "GitLab CLI (the gitlab-tooling-setup skill covers this; "
            "https://gitlab.com/gitlab-org/cli), then rerun."
        )
        sys.exit(1)


def clean_trace(text: str) -> list[str]:
    """Strip ANSI escapes, GitLab section markers, and CR progress frames."""
    text = ANSI_ESCAPE_RE.sub("", text)
    text = SECTION_MARKER_RE.sub("", text)
    lines = []
    for line in text.split("\n"):
        if "\r" in line:
            # Progress lines rewrite themselves with \r; keep the final state.
            line = line.rsplit("\r", 1)[-1]
        lines.append(line.rstrip())
    return lines


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Digest the failed jobs of a GitLab CI pipeline into one small "
            "JSON object (failed jobs, failure reasons, last N cleaned log "
            "lines each). Requires an installed and authenticated glab CLI."
        ),
        epilog=(
            "Exit codes: 0 digest produced (empty failed_jobs on a green "
            "pipeline), 1 glab missing/errored/pipeline not found, 2 bad "
            "arguments."
        ),
    )
    parser.add_argument(
        "--repo",
        required=True,
        help="project as its full path GROUP[/SUBGROUP]/NAME",
    )
    parser.add_argument(
        "--pipeline-id", required=True, type=int, help="numeric pipeline id"
    )
    parser.add_argument(
        "--tail",
        type=int,
        default=50,
        help="log lines to keep per failed job (default: 50)",
    )
    parser.add_argument(
        "--hostname",
        help="self-managed GitLab host, passed through as `glab api --hostname`",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    parts = args.repo.split("/")
    if len(parts) < 2 or not all(parts):
        parser.error(
            f"--repo must be the full GROUP[/SUBGROUP]/NAME path (got "
            f"{args.repo!r}), e.g. --repo gitlab-org/cli"
        )
    if args.pipeline_id <= 0:
        parser.error(
            f"--pipeline-id must be a positive integer (got {args.pipeline_id})"
        )
    if args.tail <= 0:
        parser.error(f"--tail must be a positive integer (got {args.tail})")

    project = urllib.parse.quote(args.repo, safe="")

    view = run_glab_api(
        f"projects/{project}/pipelines/{args.pipeline_id}", args.hostname
    )
    if view.returncode != 0:
        log(
            f"error: `glab api projects/{args.repo}/pipelines/"
            f"{args.pipeline_id}` failed (exit {view.returncode}): "
            f"{view.stderr.strip()}"
        )
        log(
            f"fix: check that pipeline {args.pipeline_id} exists in "
            f"{args.repo} (`glab ci list --repo {args.repo}`) and that glab "
            "is installed and authenticated (`glab auth status`); the "
            "gitlab-tooling-setup skill covers install and auth."
        )
        return 1

    try:
        pipeline = json.loads(view.stdout)
    except json.JSONDecodeError as exc:
        log(f"error: could not parse glab JSON output: {exc}")
        log("fix: rerun the command; if it persists, update glab.")
        return 1

    jobs_proc = run_glab_api(
        f"projects/{project}/pipelines/{args.pipeline_id}/jobs"
        "?scope[]=failed&per_page=100",
        args.hostname,
    )
    if jobs_proc.returncode != 0:
        log(
            f"error: listing failed jobs of pipeline {args.pipeline_id} "
            f"failed (exit {jobs_proc.returncode}): {jobs_proc.stderr.strip()}"
        )
        log(
            "fix: check glab authentication (`glab auth status`); the "
            "gitlab-tooling-setup skill covers install and auth."
        )
        return 1

    try:
        jobs = json.loads(jobs_proc.stdout)
    except json.JSONDecodeError as exc:
        log(f"error: could not parse glab JSON output: {exc}")
        log("fix: rerun the command; if it persists, update glab.")
        return 1

    failed_jobs = []
    for job in jobs:
        job_id = job.get("id")
        name = job.get("name", "")
        trace_proc = run_glab_api(
            f"projects/{project}/jobs/{job_id}/trace", args.hostname
        )
        entry = {
            "job_id": job_id,
            "name": name,
            "stage": job.get("stage"),
            "failure_reason": job.get("failure_reason"),
            "log_tail": [],
        }
        if trace_proc.returncode != 0:
            # Report the fetch failure as data so a consumer can tell it
            # apart from a job that simply produced no output. Common on
            # private projects or expired traces (token/permission).
            reason = trace_proc.stderr.strip() or "glab returned no trace"
            log(f"note: no trace for job {job_id} ({name}): {reason}")
            entry["log_error"] = reason
        else:
            entry["log_tail"] = clean_trace(trace_proc.stdout)[-args.tail :]
        failed_jobs.append(entry)

    digest = {
        "pipeline_id": pipeline.get("id", args.pipeline_id),
        "status": pipeline.get("status"),
        "failed_jobs": failed_jobs,
    }
    json.dump(digest, sys.stdout, indent=2)
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
