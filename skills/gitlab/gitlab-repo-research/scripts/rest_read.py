#!/usr/bin/env python3
"""Read-only GitLab reader for the REST fallback tier of gitlab-repo-research.

Works without any authentication against public projects (subject to the
host's unauthenticated rate limits). If GITLAB_TOKEN or GITLAB_ACCESS_TOKEN
is set it is sent automatically as the PRIVATE-TOKEN header, which makes
private projects readable and raises the rate limits. Self-managed hosts are
first-class: pass --host, or set GITLAB_HOST or GL_HOST. Output is a compact
field projection by default so responses stay small in agent context; --raw
returns the unprojected payload.

Usage:
    python3 scripts/rest_read.py SUBCOMMAND --project GROUP/NAME [options]

--project takes the full nested path (GROUP[/SUBGROUP]/NAME); it is
URL-encoded internally. Issues and merge requests are addressed by IID (the
!N / #N number shown in the UI), pipelines and jobs by their global id.

Subcommands:
    issues             List issues (--state, --labels, --search, --limit).
    issue              One issue (--number IID; --comments appends the
                       non-system notes).
    labels             List labels (paginates through all pages).
    mrs                List merge requests (--state, --target-branch).
    mr                 One merge request (--number IID; or add one of
                       --diff, --commits, --notes, --approvals,
                       --pipelines).
    pipelines          List pipelines (--status, --ref, --limit).
    pipeline           One pipeline (--pipeline-id ID).
    jobs               A pipeline's jobs (--pipeline-id ID; --scope failed).
    pipeline-failures  Failed jobs with cleaned log tails (--pipeline-id ID,
                       --tail N). Per-job trace errors are reported as data
                       (job traces can require a token even on public
                       projects).
    search             Instance-level search, or group-level with --group
                       (--scope issues|merge_requests|projects|milestones|
                       users, --query TEXT).
    releases           List releases (--limit), or one release (--tag TAG
                       or --latest).
    tags               List repository tags (--limit).

Exit codes: 0 = read succeeded, 1 = network/HTTP failure (a 429 reports the
Retry-After delay instead of sleeping), 2 = bad arguments.
JSON to stdout; diagnostics to stderr. Token values are never printed.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

TIMEOUT = 30

# Overwritten in main() from --host / GITLAB_HOST / GL_HOST.
API_BASE = "https://gitlab.com/api/v4"

ANSI_ESCAPE_RE = re.compile(r"\x1b\[[0-9;?]*[ -/]*[@-~]|\x1b[@-Z\\^_]")
SECTION_MARKER_RE = re.compile(r"section_(?:start|end):\d+:[\w.-]+(?:\[[^\]]*\])?")


def die(message: str, code: int = 1) -> None:
    print(f"error: {message}", file=sys.stderr)
    sys.exit(code)


class ApiError(Exception):
    """An HTTP or network failure kept catchable for error-as-data paths."""


def _token() -> str | None:
    for name in ("GITLAB_TOKEN", "GITLAB_ACCESS_TOKEN"):
        value = os.environ.get(name)
        if value:
            return value
    return None


def _headers() -> dict:
    headers = {
        "Accept": "application/json",
        "User-Agent": "gitlab-repo-research-rest-read",
    }
    token = _token()
    if token:
        headers["PRIVATE-TOKEN"] = token
    return headers


def _resolve_host(value: str | None) -> str:
    host = (
        value
        or os.environ.get("GITLAB_HOST")
        or os.environ.get("GL_HOST")
        or "gitlab.com"
    ).strip()
    if "://" in host:
        parsed = urllib.parse.urlsplit(host)
        host = parsed.netloc or parsed.path
    return host.strip("/")


def _http_error_message(err: urllib.error.HTTPError, url: str) -> str:
    if err.code == 429:
        retry_after = err.headers.get("Retry-After", "unknown")
        return (
            f"rate limited (HTTP 429) for {url}; retry after {retry_after}s; "
            "set GITLAB_TOKEN to raise limits"
        )
    if err.code == 401:
        return (
            f"HTTP 401 for {url}: authentication required or token rejected — "
            "set GITLAB_TOKEN (or GITLAB_ACCESS_TOKEN) to a personal access "
            "token with read_api scope"
        )
    if err.code == 403:
        return (
            f"HTTP 403 for {url}: access forbidden — the endpoint needs more "
            "permission than you have (job traces and some features require "
            "membership or a token even on public projects); set GITLAB_TOKEN "
            "with read_api scope"
        )
    if err.code == 404:
        return (
            f"HTTP 404 for {url}: not found — on GitLab this can mean the "
            "project is private and no token is set (set GITLAB_TOKEN), the "
            "feature is tier-gated or disabled for the project, or the "
            "path/IID/id is genuinely wrong"
        )
    return f"HTTP {err.code} {err.reason} for {url}"


def _request(url: str, raise_errors: bool = False) -> tuple[bytes, object]:
    """GET url; return (body, response headers). Dies (or raises) on failure."""
    req = urllib.request.Request(url, headers=_headers())
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            return resp.read(), resp.headers
    except urllib.error.HTTPError as err:
        message = _http_error_message(err, url)
        if raise_errors:
            raise ApiError(message) from err
        die(message)
    except TimeoutError as err:
        message = f"timeout after {TIMEOUT}s for {url}"
        if raise_errors:
            raise ApiError(message) from err
        die(message)
    except urllib.error.URLError as err:
        message = f"network failure for {url}: {err.reason}"
        if raise_errors:
            raise ApiError(message) from err
        die(message)
    raise AssertionError("unreachable")


def _api_json(path: str, params: dict | None = None):
    url = f"{API_BASE}{path}"
    if params:
        url += "?" + urllib.parse.urlencode(params)
    body, _ = _request(url)
    return json.loads(body)


def _api_json_all_pages(path: str, params: dict | None = None) -> list:
    """Collect a list endpoint across pages by following x-next-page."""
    items: list = []
    page = "1"
    while page:
        query = dict(params or {}, per_page=100, page=page)
        url = f"{API_BASE}{path}?" + urllib.parse.urlencode(query)
        body, headers = _request(url)
        items.extend(json.loads(body))
        page = headers.get("x-next-page") or ""
    return items


def _project_path(project: str) -> str:
    return "/projects/" + urllib.parse.quote(project, safe="")


def emit(obj) -> None:
    json.dump(obj, sys.stdout, indent=2, ensure_ascii=False)
    print()


def _clean_trace(text: str) -> list[str]:
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


def _issue_item(raw: dict, with_body: bool) -> dict:
    item = {
        "iid": raw.get("iid"),
        "title": raw.get("title"),
        "state": raw.get("state"),
        "labels": raw.get("labels", []),
        "author": (raw.get("author") or {}).get("username"),
        "updated_at": raw.get("updated_at"),
        "web_url": raw.get("web_url"),
    }
    if with_body:
        item["created_at"] = raw.get("created_at")
        item["description"] = raw.get("description")
    return item


def _note_item(raw: dict) -> dict:
    return {
        "author": (raw.get("author") or {}).get("username"),
        "created_at": raw.get("created_at"),
        "body": raw.get("body"),
    }


def _mr_item(raw: dict, with_body: bool) -> dict:
    item = {
        "iid": raw.get("iid"),
        "title": raw.get("title"),
        "state": raw.get("state"),
        "source_branch": raw.get("source_branch"),
        "target_branch": raw.get("target_branch"),
        "author": (raw.get("author") or {}).get("username"),
        "updated_at": raw.get("updated_at"),
        "web_url": raw.get("web_url"),
    }
    if raw.get("detailed_merge_status") is not None:
        item["detailed_merge_status"] = raw["detailed_merge_status"]
    if with_body:
        item["draft"] = raw.get("draft")
        item["labels"] = raw.get("labels", [])
        item["created_at"] = raw.get("created_at")
        item["merged_at"] = raw.get("merged_at")
        item["sha"] = raw.get("sha")
        item["description"] = raw.get("description")
    return item


def _pipeline_item(raw: dict) -> dict:
    return {
        "id": raw.get("id"),
        "status": raw.get("status"),
        "source": raw.get("source"),
        "ref": raw.get("ref"),
        "sha": (raw.get("sha") or "")[:8],
        "updated_at": raw.get("updated_at"),
        "web_url": raw.get("web_url"),
    }


def _job_item(raw: dict) -> dict:
    return {
        "id": raw.get("id"),
        "name": raw.get("name"),
        "stage": raw.get("stage"),
        "status": raw.get("status"),
        "failure_reason": raw.get("failure_reason"),
        "web_url": raw.get("web_url"),
    }


def cmd_issues(args) -> None:
    params = {"per_page": args.limit}
    if args.state != "all":
        params["state"] = args.state
    if args.labels:
        params["labels"] = args.labels
    if args.search:
        params["search"] = args.search
    raw = _api_json(f"{_project_path(args.project)}/issues", params)
    emit(raw if args.raw else [_issue_item(e, with_body=False) for e in raw])


def cmd_issue(args) -> None:
    base = f"{_project_path(args.project)}/issues/{args.number}"
    raw = _api_json(base)
    if args.raw:
        emit(raw)
        return
    item = _issue_item(raw, with_body=True)
    if args.comments:
        notes = _api_json(f"{base}/notes", {"sort": "asc", "per_page": args.limit})
        item["comment_thread"] = [
            _note_item(note) for note in notes if not note.get("system")
        ]
    emit(item)


def cmd_labels(args) -> None:
    raw = _api_json_all_pages(f"{_project_path(args.project)}/labels")
    if args.raw:
        emit(raw)
        return
    emit(
        [
            {
                "name": lb.get("name"),
                "color": lb.get("color"),
                "description": lb.get("description"),
            }
            for lb in raw
        ]
    )


def _release_item(raw: dict, *, with_body: bool) -> dict:
    item = {
        "tag": raw.get("tag_name"),
        "name": raw.get("name"),
        "upcoming": raw.get("upcoming_release"),
        "released_at": raw.get("released_at"),
        "web_url": (raw.get("_links") or {}).get("self"),
    }
    if with_body:
        item["description"] = raw.get("description")
        item["assets"] = [
            {"name": link.get("name"), "type": link.get("link_type")}
            for link in ((raw.get("assets") or {}).get("links") or [])
        ]
        item["milestones"] = [
            m.get("title") for m in raw.get("milestones") or []
        ]
    return item


def cmd_releases(args) -> None:
    base = f"{_project_path(args.project)}/releases"
    if args.latest or args.tag:
        path = (
            f"{base}/permalink/latest"
            if args.latest
            else f"{base}/{urllib.parse.quote(args.tag, safe='')}"
        )
        raw = _api_json(path)
        emit(raw if args.raw else _release_item(raw, with_body=True))
        return
    raw = _api_json(base, {"per_page": args.limit})
    emit(raw if args.raw else [_release_item(e, with_body=False) for e in raw])


def cmd_tags(args) -> None:
    raw = _api_json(
        f"{_project_path(args.project)}/repository/tags", {"per_page": args.limit}
    )
    if args.raw:
        emit(raw)
        return
    emit(
        [
            {
                "name": tag.get("name"),
                "commit_sha": ((tag.get("commit") or {}).get("id") or "")[:8],
                "message": tag.get("message"),
            }
            for tag in raw
        ]
    )


def cmd_mrs(args) -> None:
    params = {"per_page": args.limit}
    if args.state != "all":
        params["state"] = args.state
    if args.target_branch:
        params["target_branch"] = args.target_branch
    raw = _api_json(f"{_project_path(args.project)}/merge_requests", params)
    emit(raw if args.raw else [_mr_item(e, with_body=False) for e in raw])


def cmd_mr(args) -> None:
    base = f"{_project_path(args.project)}/merge_requests/{args.number}"
    if args.diff:
        raw = _api_json(f"{base}/diffs", {"per_page": args.limit})
        if args.raw:
            emit(raw)
            return
        emit(
            [
                {
                    "old_path": d.get("old_path"),
                    "new_path": d.get("new_path"),
                    "diff": d.get("diff"),
                }
                for d in raw
            ]
        )
        return
    if args.commits:
        raw = _api_json(f"{base}/commits", {"per_page": args.limit})
        if args.raw:
            emit(raw)
            return
        emit(
            [
                {
                    "short_id": c.get("short_id"),
                    "title": c.get("title"),
                    "author_name": c.get("author_name"),
                    "created_at": c.get("created_at"),
                }
                for c in raw
            ]
        )
        return
    if args.notes:
        raw = _api_json(f"{base}/notes", {"sort": "asc", "per_page": args.limit})
        if args.raw:
            emit(raw)
            return
        emit([_note_item(note) for note in raw if not note.get("system")])
        return
    if args.approvals:
        raw = _api_json(f"{base}/approvals")
        if args.raw:
            emit(raw)
            return
        item = {"approved": raw.get("approved")}
        for field in ("approvals_required", "approvals_left"):
            if raw.get(field) is not None:
                item[field] = raw[field]
        item["approved_by"] = [
            (entry.get("user") or {}).get("username")
            for entry in raw.get("approved_by") or []
        ]
        emit(item)
        return
    if args.pipelines:
        raw = _api_json(f"{base}/pipelines", {"per_page": args.limit})
        if args.raw:
            emit(raw)
            return
        emit([_pipeline_item(entry) for entry in raw])
        return
    raw = _api_json(base)
    emit(raw if args.raw else _mr_item(raw, with_body=True))


def cmd_pipelines(args) -> None:
    params = {"per_page": args.limit}
    if args.status:
        params["status"] = args.status
    if args.ref:
        params["ref"] = args.ref
    raw = _api_json(f"{_project_path(args.project)}/pipelines", params)
    emit(raw if args.raw else [_pipeline_item(entry) for entry in raw])


def cmd_pipeline(args) -> None:
    raw = _api_json(f"{_project_path(args.project)}/pipelines/{args.pipeline_id}")
    if args.raw:
        emit(raw)
        return
    emit(
        {
            "id": raw.get("id"),
            "status": raw.get("status"),
            "source": raw.get("source"),
            "ref": raw.get("ref"),
            "sha": raw.get("sha"),
            "user": (raw.get("user") or {}).get("username"),
            "created_at": raw.get("created_at"),
            "updated_at": raw.get("updated_at"),
            "duration": raw.get("duration"),
            "queued_duration": raw.get("queued_duration"),
            "web_url": raw.get("web_url"),
        }
    )


def cmd_jobs(args) -> None:
    params = {"per_page": 100}
    if args.scope:
        params["scope[]"] = args.scope
    raw = _api_json(
        f"{_project_path(args.project)}/pipelines/{args.pipeline_id}/jobs", params
    )
    emit(raw if args.raw else [_job_item(entry) for entry in raw])


def cmd_pipeline_failures(args) -> None:
    project = _project_path(args.project)
    pipeline = _api_json(f"{project}/pipelines/{args.pipeline_id}")
    jobs = _api_json(
        f"{project}/pipelines/{args.pipeline_id}/jobs",
        {"scope[]": "failed", "per_page": 100},
    )
    result = {
        "pipeline_id": pipeline.get("id"),
        "status": pipeline.get("status"),
        "failed_jobs": [],
    }
    for job in jobs:
        item = {
            "job_id": job.get("id"),
            "name": job.get("name"),
            "stage": job.get("stage"),
            "failure_reason": job.get("failure_reason"),
        }
        trace_url = f"{API_BASE}{project}/jobs/{job['id']}/trace"
        try:
            body, _ = _request(trace_url, raise_errors=True)
        except ApiError as err:
            # Traces can be token-gated even on public projects; report the
            # failure per job instead of aborting the whole digest.
            item["log_error"] = str(err)
        else:
            text = body.decode("utf-8", errors="replace")
            item["log_tail"] = _clean_trace(text)[-args.tail :]
        result["failed_jobs"].append(item)
    emit(result)


def _search_item(scope: str, raw: dict) -> dict:
    if scope == "projects":
        return {
            "id": raw.get("id"),
            "path_with_namespace": raw.get("path_with_namespace"),
            "description": raw.get("description"),
            "web_url": raw.get("web_url"),
        }
    if scope == "users":
        return {
            "id": raw.get("id"),
            "username": raw.get("username"),
            "name": raw.get("name"),
            "web_url": raw.get("web_url"),
        }
    if scope == "milestones":
        return {
            "id": raw.get("id"),
            "iid": raw.get("iid"),
            "project_id": raw.get("project_id"),
            "title": raw.get("title"),
            "state": raw.get("state"),
            "due_date": raw.get("due_date"),
        }
    # issues and merge_requests
    return {
        "project_id": raw.get("project_id"),
        "iid": raw.get("iid"),
        "title": raw.get("title"),
        "state": raw.get("state"),
        "web_url": raw.get("web_url"),
    }


def cmd_search(args) -> None:
    if args.group:
        path = "/groups/" + urllib.parse.quote(args.group, safe="") + "/search"
    else:
        path = "/search"
    raw = _api_json(
        path,
        {"scope": args.scope, "search": args.query, "per_page": args.limit},
    )
    if args.raw:
        emit(raw)
        return
    emit([_search_item(args.scope, item) for item in raw])


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="rest_read.py",
        description=(
            "Read-only GitLab REST v4 reader for public-project research; "
            "exit codes 0/1/2 per module docstring"
        ),
    )
    sub = parser.add_subparsers(dest="command", required=True)

    def common(p: argparse.ArgumentParser, project=True, limit=True) -> None:
        if project:
            p.add_argument(
                "--project",
                required=True,
                help="full project path GROUP[/SUBGROUP]/NAME",
            )
        p.add_argument(
            "--host",
            help="GitLab host (default: GITLAB_HOST, GL_HOST, then gitlab.com)",
        )
        if limit:
            p.add_argument("--limit", type=int, default=30, help="page size")
        p.add_argument("--raw", action="store_true", help="unprojected API payload")

    p_issues = sub.add_parser("issues", help="list issues")
    common(p_issues)
    p_issues.add_argument(
        "--state", default="opened", choices=["opened", "closed", "all"]
    )
    p_issues.add_argument("--labels", help="comma-separated label names")
    p_issues.add_argument("--search", help="filter by text in title/description")
    p_issues.set_defaults(func=cmd_issues)

    p_issue = sub.add_parser("issue", help="one issue")
    common(p_issue)
    p_issue.add_argument("--number", type=int, required=True, help="issue IID")
    p_issue.add_argument("--comments", action="store_true")
    p_issue.set_defaults(func=cmd_issue)

    p_labels = sub.add_parser("labels", help="list labels (all pages)")
    common(p_labels, limit=False)
    p_labels.set_defaults(func=cmd_labels)

    p_mrs = sub.add_parser("mrs", help="list merge requests")
    common(p_mrs)
    p_mrs.add_argument(
        "--state", default="opened", choices=["opened", "closed", "merged", "all"]
    )
    p_mrs.add_argument("--target-branch")
    p_mrs.set_defaults(func=cmd_mrs)

    p_mr = sub.add_parser("mr", help="one merge request")
    common(p_mr)
    p_mr.add_argument("--number", type=int, required=True, help="merge request IID")
    view = p_mr.add_mutually_exclusive_group()
    for flag in ("diff", "commits", "notes", "approvals", "pipelines"):
        view.add_argument(f"--{flag}", action="store_true")
    p_mr.set_defaults(func=cmd_mr)

    p_pipelines = sub.add_parser("pipelines", help="list pipelines")
    common(p_pipelines)
    p_pipelines.add_argument(
        "--status",
        choices=[
            "created",
            "waiting_for_resource",
            "preparing",
            "pending",
            "running",
            "success",
            "failed",
            "canceled",
            "skipped",
            "manual",
            "scheduled",
        ],
    )
    p_pipelines.add_argument("--ref")
    p_pipelines.set_defaults(func=cmd_pipelines)

    p_pipeline = sub.add_parser("pipeline", help="one pipeline")
    common(p_pipeline, limit=False)
    p_pipeline.add_argument("--pipeline-id", type=int, required=True)
    p_pipeline.set_defaults(func=cmd_pipeline)

    p_jobs = sub.add_parser("jobs", help="a pipeline's jobs")
    common(p_jobs, limit=False)
    p_jobs.add_argument("--pipeline-id", type=int, required=True)
    p_jobs.add_argument(
        "--scope",
        choices=[
            "created",
            "pending",
            "running",
            "failed",
            "success",
            "canceled",
            "skipped",
            "waiting_for_resource",
            "manual",
        ],
    )
    p_jobs.set_defaults(func=cmd_jobs)

    p_fail = sub.add_parser(
        "pipeline-failures", help="failed jobs with cleaned log tails"
    )
    common(p_fail, limit=False)
    p_fail.add_argument("--pipeline-id", type=int, required=True)
    p_fail.add_argument("--tail", type=int, default=50, help="log lines per job")
    p_fail.set_defaults(func=cmd_pipeline_failures)

    p_search = sub.add_parser("search", help="instance- or group-level search")
    common(p_search, project=False)
    p_search.add_argument(
        "--scope",
        required=True,
        choices=["issues", "merge_requests", "projects", "milestones", "users"],
    )
    p_search.add_argument("--query", required=True)
    p_search.add_argument("--group", help="full group path for group-level search")
    p_search.set_defaults(func=cmd_search)

    p_rels = sub.add_parser("releases", help="list releases or read one")
    common(p_rels)
    which = p_rels.add_mutually_exclusive_group()
    which.add_argument("--tag", help="one release by tag name")
    which.add_argument("--latest", action="store_true", help="the latest release")
    p_rels.set_defaults(func=cmd_releases)

    p_tags = sub.add_parser("tags", help="list repository tags")
    common(p_tags)
    p_tags.set_defaults(func=cmd_tags)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    global API_BASE
    API_BASE = f"https://{_resolve_host(args.host)}/api/v4"
    project = getattr(args, "project", None)
    if project is not None and not re.fullmatch(r"[^/\s]+(?:/[^/\s]+)+", project):
        parser.error(
            f"--project must be the full GROUP[/SUBGROUP]/NAME path, got {project!r}"
        )
    if getattr(args, "limit", 1) <= 0:
        parser.error("--limit must be a positive integer")
    if getattr(args, "tail", 1) <= 0:
        parser.error("--tail must be a positive integer")
    args.func(args)


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:
        # The consumer (e.g. `| head`) closed the pipe; that is not an error.
        os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())
        sys.exit(0)
