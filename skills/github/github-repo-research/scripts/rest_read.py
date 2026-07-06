#!/usr/bin/env python3
"""Read-only GitHub reader for the REST fallback tier of github-repo-research.

Works without any authentication against public repositories. If GH_TOKEN
or GITHUB_TOKEN is set it is used automatically (higher rate limits, and
Discussions upgrade from best-effort Atom/HTML extraction to full-fidelity
GraphQL). Output is a compact field projection by default so responses stay
small in agent context; --raw returns the unprojected payload.

Usage:
    python3 scripts/rest_read.py SUBCOMMAND --repo OWNER/REPO [options]

Subcommands:
    issues        List issues (--state open|closed|all, --limit N).
    issue         One issue (--number N; --comments appends the thread).
    labels        List labels.
    prs           List pull requests (--state, --limit).
    pr            One pull request (--number N; or add one of --diff,
                  --files, --reviews, --comments, --checks).
    runs          List workflow runs (--limit).
    run           One workflow run (--run-id ID).
    jobs          A run's jobs (--run-id ID).
    run-failures  Failed jobs, failed steps, and log tails (--run-id ID,
                  --tail N).
    search        Search issues and PRs (--query "is:issue repo:O/R text").
    discussions   List discussions (GraphQL with token; Atom feed without).
    discussion    One discussion (--number N; GraphQL with token,
                  best-effort HTML extraction without).

Exit codes: 0 = read succeeded, 1 = network/HTTP failure (rate-limit
exhaustion is reported with its reset time), 2 = bad arguments.
JSON to stdout; diagnostics to stderr. Token values are never printed.
"""

from __future__ import annotations

import argparse
import datetime
import html.parser
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

API = "https://api.github.com"
WEB = "https://github.com"
ACCEPT_JSON = "application/vnd.github+json"
ACCEPT_DIFF = "application/vnd.github.diff"
API_VERSION = "2022-11-28"
TIMEOUT = 30
ATOM_NS = {"a": "http://www.w3.org/2005/Atom"}


def die(message: str, code: int = 1) -> None:
    print(f"error: {message}", file=sys.stderr)
    sys.exit(code)


def _token() -> str | None:
    for name in ("GH_TOKEN", "GITHUB_TOKEN"):
        value = os.environ.get(name)
        if value:
            return value
    return None


def _headers(accept: str, auth: bool) -> dict:
    headers = {
        "Accept": accept,
        "X-GitHub-Api-Version": API_VERSION,
        "User-Agent": "github-repo-research-rest-read",
    }
    token = _token() if auth else None
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def _rate_limit_message(err: urllib.error.HTTPError) -> str | None:
    if err.code not in (403, 429):
        return None
    if err.headers.get("X-RateLimit-Remaining") != "0":
        return None
    reset = err.headers.get("X-RateLimit-Reset")
    when = "unknown"
    if reset and reset.isdigit():
        when = datetime.datetime.fromtimestamp(
            int(reset), datetime.timezone.utc
        ).strftime("%H:%M:%S UTC")
    return (
        f"GitHub rate limit exhausted; it resets at {when}. "
        "Unauthenticated clients get 60 requests/hour (search: 10/minute); "
        "set GH_TOKEN or GITHUB_TOKEN to raise the limit, or wait."
    )


def _request(
    url: str,
    accept: str = ACCEPT_JSON,
    data: bytes | None = None,
    auth: bool = True,
    follow_redirects: bool = True,
) -> bytes:
    req = urllib.request.Request(url, data=data, headers=_headers(accept, auth))
    if data is not None:
        req.add_header("Content-Type", "application/json")
    opener = (
        urllib.request.build_opener()
        if follow_redirects
        else urllib.request.build_opener(_NoRedirect())
    )
    try:
        with opener.open(req, timeout=TIMEOUT) as resp:
            return resp.read()
    except urllib.error.HTTPError as err:
        if not follow_redirects and err.code in (301, 302, 307, 308):
            raise
        limited = _rate_limit_message(err)
        if limited:
            die(limited)
        die(f"HTTP {err.code} {err.reason} for {url}")
    except urllib.error.URLError as err:
        die(f"network failure for {url}: {err.reason}")
    raise AssertionError("unreachable")


def _api_json(path: str, params: dict | None = None):
    url = f"{API}{path}"
    if params:
        url += "?" + urllib.parse.urlencode(params)
    return json.loads(_request(url))


def _graphql(query: str, variables: dict):
    payload = json.dumps({"query": query, "variables": variables}).encode()
    body = json.loads(_request(f"{API}/graphql", data=payload))
    if body.get("errors"):
        die(f"GraphQL error: {body['errors'][0].get('message', 'unknown')}")
    return body["data"]


def emit(obj) -> None:
    json.dump(obj, sys.stdout, indent=2, ensure_ascii=False)
    print()


class _TextExtractor(html.parser.HTMLParser):
    """Collect plain text, used to strip tags from HTML snippets."""

    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        self.parts.append(data)

    def text(self) -> str:
        return re.sub(r"\s+", " ", "".join(self.parts)).strip()


def _strip_html(fragment: str) -> str:
    extractor = _TextExtractor()
    extractor.feed(fragment)
    return extractor.text()


class _MarkdownBodyParser(html.parser.HTMLParser):
    """Collect the text of each markdown-body block on a discussion page."""

    def __init__(self) -> None:
        super().__init__()
        self.blocks: list[str] = []
        self._depth = 0
        self._parts: list[str] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        classes = dict(attrs).get("class", "")
        if self._depth:
            self._depth += 1
        elif "markdown-body" in classes:
            self._depth = 1
            self._parts = []

    def handle_endtag(self, tag: str) -> None:
        if not self._depth:
            return
        self._depth -= 1
        if self._depth == 0:
            text = re.sub(r"[ \t]+", " ", "".join(self._parts)).strip()
            if text:
                self.blocks.append(text)

    def handle_data(self, data: str) -> None:
        if self._depth:
            self._parts.append(data)


def _issue_item(raw: dict, with_body: bool) -> dict:
    item = {
        "number": raw.get("number"),
        "title": raw.get("title"),
        "state": raw.get("state"),
        "labels": [label["name"] for label in raw.get("labels", [])],
        "author": (raw.get("user") or {}).get("login"),
        "comments": raw.get("comments"),
        "created_at": raw.get("created_at"),
        "updated_at": raw.get("updated_at"),
        "url": raw.get("html_url"),
    }
    if with_body:
        item["body"] = raw.get("body")
    return item


def _comment_item(raw: dict) -> dict:
    return {
        "author": (raw.get("user") or {}).get("login"),
        "created_at": raw.get("created_at"),
        "body": raw.get("body"),
    }


def _pr_item(raw: dict, with_body: bool) -> dict:
    item = {
        "number": raw.get("number"),
        "title": raw.get("title"),
        "state": raw.get("state"),
        "draft": raw.get("draft"),
        "merged": raw.get("merged_at") is not None,
        "base": (raw.get("base") or {}).get("ref"),
        "head": (raw.get("head") or {}).get("ref"),
        "author": (raw.get("user") or {}).get("login"),
        "created_at": raw.get("created_at"),
        "updated_at": raw.get("updated_at"),
        "url": raw.get("html_url"),
    }
    if with_body:
        item["body"] = raw.get("body")
        item["head_sha"] = (raw.get("head") or {}).get("sha")
        item["changed_files"] = raw.get("changed_files")
    return item


def cmd_issues(args) -> None:
    raw = _api_json(
        f"/repos/{args.repo}/issues",
        {"state": args.state, "per_page": args.limit},
    )
    if args.raw:
        emit(raw)
        return
    emit(
        [
            _issue_item(entry, with_body=False)
            for entry in raw
            if "pull_request" not in entry
        ]
    )


def cmd_issue(args) -> None:
    raw = _api_json(f"/repos/{args.repo}/issues/{args.number}")
    if args.raw:
        emit(raw)
        return
    item = _issue_item(raw, with_body=True)
    if args.comments:
        thread = _api_json(
            f"/repos/{args.repo}/issues/{args.number}/comments",
            {"per_page": args.limit},
        )
        item["comment_thread"] = [_comment_item(entry) for entry in thread]
    emit(item)


def cmd_labels(args) -> None:
    raw = _api_json(f"/repos/{args.repo}/labels", {"per_page": 100})
    if args.raw:
        emit(raw)
        return
    emit([{"name": lb["name"], "description": lb.get("description")} for lb in raw])


def cmd_prs(args) -> None:
    raw = _api_json(
        f"/repos/{args.repo}/pulls",
        {"state": args.state, "per_page": args.limit},
    )
    if args.raw:
        emit(raw)
        return
    emit([_pr_item(entry, with_body=False) for entry in raw])


def cmd_pr(args) -> None:
    base = f"/repos/{args.repo}/pulls/{args.number}"
    if args.diff:
        text = _request(f"{API}{base}", accept=ACCEPT_DIFF).decode(
            "utf-8", errors="replace"
        )
        print(text)
        return
    if args.files:
        raw = _api_json(f"{base}/files", {"per_page": args.limit})
        if args.raw:
            emit(raw)
            return
        emit(
            [
                {
                    "filename": f["filename"],
                    "status": f["status"],
                    "additions": f["additions"],
                    "deletions": f["deletions"],
                }
                for f in raw
            ]
        )
        return
    if args.reviews:
        raw = _api_json(f"{base}/reviews", {"per_page": args.limit})
        if args.raw:
            emit(raw)
            return
        emit(
            [
                {
                    "author": (r.get("user") or {}).get("login"),
                    "state": r.get("state"),
                    "submitted_at": r.get("submitted_at"),
                    "body": r.get("body"),
                }
                for r in raw
            ]
        )
        return
    if args.comments:
        raw = _api_json(f"{base}/comments", {"per_page": args.limit})
        if args.raw:
            emit(raw)
            return
        emit(
            [
                {
                    "id": c.get("id"),
                    "in_reply_to_id": c.get("in_reply_to_id"),
                    "author": (c.get("user") or {}).get("login"),
                    "path": c.get("path"),
                    "line": c.get("line") or c.get("original_line"),
                    "created_at": c.get("created_at"),
                    "body": c.get("body"),
                }
                for c in raw
            ]
        )
        return
    pr = _api_json(base)
    if args.checks:
        sha = (pr.get("head") or {}).get("sha")
        raw = _api_json(
            f"/repos/{args.repo}/commits/{sha}/check-runs",
            {"per_page": 100},
        )
        if args.raw:
            emit(raw)
            return
        emit(
            [
                {
                    "name": run["name"],
                    "status": run["status"],
                    "conclusion": run["conclusion"],
                }
                for run in raw.get("check_runs", [])
            ]
        )
        return
    emit(pr if args.raw else _pr_item(pr, with_body=True))


def _run_item(raw: dict) -> dict:
    return {
        "run_id": raw.get("id"),
        "workflow": raw.get("name"),
        "display_title": raw.get("display_title"),
        "branch": raw.get("head_branch"),
        "event": raw.get("event"),
        "status": raw.get("status"),
        "conclusion": raw.get("conclusion"),
        "created_at": raw.get("created_at"),
        "url": raw.get("html_url"),
    }


def _job_item(raw: dict) -> dict:
    return {
        "job_id": raw.get("id"),
        "name": raw.get("name"),
        "status": raw.get("status"),
        "conclusion": raw.get("conclusion"),
        "failed_steps": [
            step["name"]
            for step in raw.get("steps", [])
            if step.get("conclusion") == "failure"
        ],
    }


def cmd_runs(args) -> None:
    raw = _api_json(f"/repos/{args.repo}/actions/runs", {"per_page": args.limit})
    if args.raw:
        emit(raw)
        return
    emit([_run_item(entry) for entry in raw.get("workflow_runs", [])])


def cmd_run(args) -> None:
    raw = _api_json(f"/repos/{args.repo}/actions/runs/{args.run_id}")
    emit(raw if args.raw else _run_item(raw))


def cmd_jobs(args) -> None:
    raw = _api_json(
        f"/repos/{args.repo}/actions/runs/{args.run_id}/jobs",
        {"per_page": 100},
    )
    if args.raw:
        emit(raw)
        return
    emit([_job_item(entry) for entry in raw.get("jobs", [])])


def _job_log_tail(repo: str, job_id: int, tail: int) -> list[str] | None:
    """Return the last lines of a job log, or None when logs need a token.

    GitHub requires authentication for the Actions log endpoints even on
    public repositories ("Must have admin rights to Repository." without a
    token); everything else in this script works anonymously.
    """
    url = f"{API}/repos/{repo}/actions/jobs/{job_id}/logs"
    try:
        # The API answers with a redirect to a short-lived signed URL; fetch
        # it manually so the Authorization header is not forwarded off-host.
        _request(url, follow_redirects=False)
    except urllib.error.HTTPError as err:
        if err.code == 403 and not _token():
            return None
        if err.code not in (301, 302, 307, 308):
            die(f"HTTP {err.code} {err.reason} for {url}")
        signed = err.headers.get("Location")
        if not signed:
            die(f"redirect without Location for {url}")
        text = _request(signed, auth=False).decode("utf-8", errors="replace")
        return text.splitlines()[-tail:]
    die(f"expected a redirect for {url}")
    raise AssertionError("unreachable")


def cmd_run_failures(args) -> None:
    run = _api_json(f"/repos/{args.repo}/actions/runs/{args.run_id}")
    jobs = _api_json(
        f"/repos/{args.repo}/actions/runs/{args.run_id}/jobs",
        {"per_page": 100},
    ).get("jobs", [])
    failed = [job for job in jobs if job.get("conclusion") == "failure"]
    result = {
        "run_id": run.get("id"),
        "status": run.get("status"),
        "conclusion": run.get("conclusion"),
        "failed_jobs": [],
    }
    for job in failed:
        item = _job_item(job)
        item["log_tail"] = _job_log_tail(args.repo, job["id"], args.tail)
        if item["log_tail"] is None:
            item["log_note"] = (
                "log text requires a token (GH_TOKEN/GITHUB_TOKEN); the "
                "failed step names above come from the jobs API"
            )
        result["failed_jobs"].append(item)
    emit(result)


def cmd_search(args) -> None:
    raw = _api_json("/search/issues", {"q": args.query, "per_page": args.limit})
    if args.raw:
        emit(raw)
        return
    emit(
        {
            "total_count": raw.get("total_count"),
            "items": [
                {
                    "number": item.get("number"),
                    "title": item.get("title"),
                    "state": item.get("state"),
                    "is_pr": "pull_request" in item,
                    "url": item.get("html_url"),
                }
                for item in raw.get("items", [])
            ],
        }
    )


DISCUSSIONS_QUERY = """
query($owner: String!, $name: String!, $first: Int!) {
  repository(owner: $owner, name: $name) {
    discussions(first: $first,
                orderBy: {field: UPDATED_AT, direction: DESC}) {
      nodes {
        number title url createdAt updatedAt
        category { name }
        author { login }
      }
    }
  }
}
"""

DISCUSSION_QUERY = """
query($owner: String!, $name: String!, $number: Int!) {
  repository(owner: $owner, name: $name) {
    discussion(number: $number) {
      number title body url createdAt
      category { name }
      author { login }
      comments(first: 30) {
        nodes { author { login } createdAt body }
      }
    }
  }
}
"""


def cmd_discussions(args) -> None:
    owner, name = args.repo.split("/", 1)
    if _token():
        data = _graphql(
            DISCUSSIONS_QUERY,
            {"owner": owner, "name": name, "first": args.limit},
        )
        nodes = data["repository"]["discussions"]["nodes"]
        emit(
            {
                "engine": "graphql",
                "discussions": [
                    {
                        "number": node["number"],
                        "title": node["title"],
                        "category": (node.get("category") or {}).get("name"),
                        "author": (node.get("author") or {}).get("login"),
                        "created_at": node["createdAt"],
                        "updated_at": node["updatedAt"],
                        "url": node["url"],
                    }
                    for node in nodes
                ],
            }
        )
        return
    feed = _request(f"{WEB}/{args.repo}/discussions.atom", auth=False)
    entries = []
    for entry in ET.fromstring(feed).findall("a:entry", ATOM_NS):
        link = entry.find("a:link", ATOM_NS)
        url = link.get("href") if link is not None else ""
        match = re.search(r"/discussions/(\d+)", url or "")
        title = entry.find("a:title", ATOM_NS)
        author = entry.find("a:author/a:name", ATOM_NS)
        published = entry.find("a:published", ATOM_NS)
        updated = entry.find("a:updated", ATOM_NS)
        content = entry.find("a:content", ATOM_NS)
        snippet = _strip_html(content.text or "") if content is not None else ""
        entries.append(
            {
                "number": int(match.group(1)) if match else None,
                "title": (title.text or "").strip() if title is not None else "",
                "author": author.text if author is not None else None,
                "published": published.text if published is not None else None,
                "updated": updated.text if updated is not None else None,
                "url": url,
                "snippet": snippet[:200],
            }
        )
    emit(
        {
            "engine": "atom",
            "note": "tokenless feed covers only the latest ~25 discussions",
            "discussions": entries,
        }
    )


def cmd_discussion(args) -> None:
    owner, name = args.repo.split("/", 1)
    if _token():
        data = _graphql(
            DISCUSSION_QUERY,
            {"owner": owner, "name": name, "number": args.number},
        )
        node = data["repository"]["discussion"]
        if node is None:
            die(f"discussion #{args.number} not found in {args.repo}")
        emit(
            {
                "engine": "graphql",
                "number": node["number"],
                "title": node["title"],
                "category": (node.get("category") or {}).get("name"),
                "author": (node.get("author") or {}).get("login"),
                "created_at": node["createdAt"],
                "url": node["url"],
                "body": node["body"],
                "comments": [
                    {
                        "author": (c.get("author") or {}).get("login"),
                        "created_at": c["createdAt"],
                        "body": c["body"],
                    }
                    for c in node["comments"]["nodes"]
                ],
            }
        )
        return
    page = _request(f"{WEB}/{args.repo}/discussions/{args.number}", auth=False).decode(
        "utf-8", errors="replace"
    )
    title_match = re.search(r"<title>(.*?)</title>", page, re.S)
    title = title_match.group(1).split(" · ")[0].strip() if title_match else ""
    parser = _MarkdownBodyParser()
    parser.feed(page)
    if not parser.blocks:
        die(
            "could not extract the discussion from the HTML page (GitHub "
            "may have changed its markup). Alternatives: set GH_TOKEN or "
            "GITHUB_TOKEN (GraphQL), or use the MCP / gh tiers."
        )
    emit(
        {
            "engine": "html-besteffort",
            "note": (
                "tokenless extraction from the public HTML page; text only, "
                "authorship and threading are not preserved"
            ),
            "number": args.number,
            "title": title,
            "texts": parser.blocks,
        }
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="rest_read.py",
        description=(
            "Read-only GitHub reader (REST/GraphQL/Atom) for public-repo "
            "research; exit codes 0/1/2 per module docstring"
        ),
    )
    sub = parser.add_subparsers(dest="command", required=True)

    def common(p: argparse.ArgumentParser) -> None:
        p.add_argument("--repo", required=True, help="OWNER/REPO")
        p.add_argument("--limit", type=int, default=20, help="page size")
        p.add_argument("--raw", action="store_true", help="unprojected API payload")

    p_issues = sub.add_parser("issues", help="list issues")
    common(p_issues)
    p_issues.add_argument("--state", default="open", choices=["open", "closed", "all"])
    p_issues.set_defaults(func=cmd_issues)

    p_issue = sub.add_parser("issue", help="one issue")
    common(p_issue)
    p_issue.add_argument("--number", type=int, required=True)
    p_issue.add_argument("--comments", action="store_true")
    p_issue.set_defaults(func=cmd_issue)

    p_labels = sub.add_parser("labels", help="list labels")
    common(p_labels)
    p_labels.set_defaults(func=cmd_labels)

    p_prs = sub.add_parser("prs", help="list pull requests")
    common(p_prs)
    p_prs.add_argument("--state", default="open", choices=["open", "closed", "all"])
    p_prs.set_defaults(func=cmd_prs)

    p_pr = sub.add_parser("pr", help="one pull request")
    common(p_pr)
    p_pr.add_argument("--number", type=int, required=True)
    view = p_pr.add_mutually_exclusive_group()
    for flag in ("diff", "files", "reviews", "comments", "checks"):
        view.add_argument(f"--{flag}", action="store_true")
    p_pr.set_defaults(func=cmd_pr)

    p_runs = sub.add_parser("runs", help="list workflow runs")
    common(p_runs)
    p_runs.set_defaults(func=cmd_runs)

    p_run = sub.add_parser("run", help="one workflow run")
    common(p_run)
    p_run.add_argument("--run-id", type=int, required=True)
    p_run.set_defaults(func=cmd_run)

    p_jobs = sub.add_parser("jobs", help="a run's jobs")
    common(p_jobs)
    p_jobs.add_argument("--run-id", type=int, required=True)
    p_jobs.set_defaults(func=cmd_jobs)

    p_fail = sub.add_parser("run-failures", help="failed jobs with log tails")
    common(p_fail)
    p_fail.add_argument("--run-id", type=int, required=True)
    p_fail.add_argument("--tail", type=int, default=50)
    p_fail.set_defaults(func=cmd_run_failures)

    p_search = sub.add_parser("search", help="search issues and PRs")
    common(p_search)
    p_search.add_argument("--query", required=True)
    p_search.set_defaults(func=cmd_search)

    p_discs = sub.add_parser("discussions", help="list discussions")
    common(p_discs)
    p_discs.set_defaults(func=cmd_discussions)

    p_disc = sub.add_parser("discussion", help="one discussion")
    common(p_disc)
    p_disc.add_argument("--number", type=int, required=True)
    p_disc.set_defaults(func=cmd_discussion)

    return parser


def main() -> None:
    args = build_parser().parse_args()
    if not re.fullmatch(r"[^/\s]+/[^/\s]+", args.repo):
        build_parser().error(f"--repo must be OWNER/REPO, got {args.repo!r}")
    args.func(args)


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:
        # The consumer (e.g. `| head`) closed the pipe; that is not an error.
        os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())
        sys.exit(0)
