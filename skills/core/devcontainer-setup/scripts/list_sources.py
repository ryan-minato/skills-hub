#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# ///
"""List dev container assets available from this skill's trusted sources.

Trusted sources are defined in TRUST_DOMAINS, one entry per source. Three
source kinds are supported, matching how the ecosystem distributes assets:

  docker-registry  images in a Docker Registry v2 (_catalog + tags/list)
  oci-collection   Features/Templates published as OCI artifacts alongside
                   a devcontainer-collection.json metadata blob
  ngc-catalog      images in NVIDIA NGC (bespoke search API; tags via the
                   nvcr.io registry v2 API with an anonymous token)

Extending trust: a new source of an existing kind is one more TRUST_DOMAINS
entry; a new distribution mechanism needs one new fetcher in FETCHERS.

Output: data to stdout (tab-separated table by default, --format json for a
machine-readable document); diagnostics to stderr. A failing source never
aborts the run — it is reported on stderr and marked ok=false in JSON.

Exit codes: 0 all requested sources succeeded; 1 at least one source failed
(partial results are still printed to stdout); 2 bad arguments, including a
--tags ref that is outside every trusted domain.

--self-test only checks that the environment is usable (Python version and
endpoint reachability); it does not validate parsing correctness.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

TIMEOUT_SECONDS = 15
USER_AGENT = "devcontainer-setup/list_sources"
COLLECTION_MEDIA_TYPE = "application/vnd.devcontainers.collection.layer.v1+json"
OCI_MANIFEST_MEDIA_TYPE = "application/vnd.oci.image.manifest.v1+json"
NGC_PAGE_SIZE = 100
NGC_MAX_PAGES = 40

TRUST_DOMAINS: list[dict] = [
    {
        "name": "mcr-devcontainers",
        "kind": "docker-registry",
        "provides": "images",
        "registry": "https://mcr.microsoft.com",
        "repo_prefix": "devcontainers/",
        "ref_prefix": "mcr.microsoft.com/devcontainers/",
    },
    {
        "name": "ngc",
        "kind": "ngc-catalog",
        "provides": "images",
        "registry": "https://nvcr.io",
        "token_url": "https://nvcr.io/proxy_auth",
        "search_api": "https://api.ngc.nvidia.com/v2/search/catalog/resources/CONTAINER",
        "default_org": "nvidia",
        "ref_prefix": "nvcr.io/",
    },
    {
        "name": "devcontainers-features",
        "kind": "oci-collection",
        "provides": "features",
        "registry": "https://ghcr.io",
        "token_url": "https://ghcr.io/token",
        "token_service": "ghcr.io",
        "namespace": "devcontainers/features",
        "ref_prefix": "ghcr.io/devcontainers/features/",
    },
    {
        "name": "stacit-ai-features",
        "kind": "oci-collection",
        "provides": "features",
        "registry": "https://ghcr.io",
        "token_url": "https://ghcr.io/token",
        "token_service": "ghcr.io",
        "namespace": "stacit-ai/devcontainer-features",
        "ref_prefix": "ghcr.io/stacit-ai/devcontainer-features/",
    },
    {
        "name": "devcontainers-templates",
        "kind": "oci-collection",
        "provides": "templates",
        "registry": "https://ghcr.io",
        "token_url": "https://ghcr.io/token",
        "token_service": "ghcr.io",
        "namespace": "devcontainers/templates",
        "ref_prefix": "ghcr.io/devcontainers/templates/",
    },
]


class SourceError(Exception):
    """A source-level failure carrying an actionable message."""


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: D102
        return None


def _host(url: str) -> str:
    return urllib.parse.urlparse(url).netloc


def _http_get(
    url: str,
    headers: dict | None = None,
    follow_redirects: bool = True,
) -> tuple[bytes, dict]:
    """GET url, returning (body, response headers). Raises SourceError."""
    request = urllib.request.Request(
        url, headers={"User-Agent": USER_AGENT, **(headers or {})}
    )
    handlers = [] if follow_redirects else [_NoRedirect()]
    opener = urllib.request.build_opener(*handlers)
    try:
        with opener.open(request, timeout=TIMEOUT_SECONDS) as response:
            return response.read(), dict(response.headers)
    except urllib.error.HTTPError as exc:
        raise SourceError(
            f"HTTP {exc.code} from {url}. The endpoint may have changed or "
            f"the resource may not exist; see references/trust-domains.md "
            f"for the manual route."
        ) from exc
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise SourceError(
            f"cannot reach {_host(url)} ({exc}). Listing from this source "
            f"is unavailable; check network/proxy access and retry."
        ) from exc


def _get_json(url: str, headers: dict | None = None) -> dict:
    body, _ = _http_get(url, headers)
    try:
        return json.loads(body)
    except json.JSONDecodeError as exc:
        raise SourceError(
            f"non-JSON response from {url} ({exc}). The endpoint contract "
            f"may have changed; see references/trust-domains.md."
        ) from exc


def _get_blob(url: str, token: str) -> bytes:
    """Fetch a registry blob, following one redirect WITHOUT credentials.

    Registries answer blob GETs with a 307 to pre-signed blob storage; the
    storage backend rejects requests that still carry the Authorization
    header, so the redirect must be re-issued without it.
    """
    try:
        body, _ = _http_get(
            url,
            headers={"Authorization": f"Bearer {token}"},
            follow_redirects=False,
        )
        return body
    except SourceError as exc:
        cause = exc.__cause__
        if (
            isinstance(cause, urllib.error.HTTPError)
            and cause.code in (301, 302, 303, 307, 308)
            and cause.headers.get("Location")
        ):
            location = urllib.parse.urljoin(url, cause.headers["Location"])
            body, _ = _http_get(location)
            return body
        raise


def _registry_token(domain: dict, repository: str) -> str:
    query: dict = {"scope": f"repository:{repository}:pull"}
    if domain.get("token_service"):
        query["service"] = domain["token_service"]
    url = f"{domain['token_url']}?{urllib.parse.urlencode(query)}"
    token = _get_json(url).get("token")
    if not token:
        raise SourceError(
            f"no anonymous pull token from {url}. The repository may be "
            f"private or the token endpoint may have changed."
        )
    return token


def _major_tag(version: str | None) -> str:
    match = re.match(r"^(\d+)", version or "")
    return match.group(1) if match else "latest"


def _next_link(link_header: str | None, base_url: str) -> str | None:
    if not link_header:
        return None
    match = re.search(r"<([^>]+)>\s*;\s*rel=\"next\"", link_header)
    if not match:
        return None
    return urllib.parse.urljoin(base_url, match.group(1))


def fetch_docker_registry(domain: dict, args: argparse.Namespace) -> list[dict]:
    registry = domain["registry"]
    host = _host(registry)
    url: str | None = f"{registry}/v2/_catalog"
    repos: list[str] = []
    while url:
        body, headers = _http_get(url)
        try:
            data = json.loads(body)
        except json.JSONDecodeError as exc:
            raise SourceError(f"non-JSON catalog from {url} ({exc}).") from exc
        repos.extend(data.get("repositories") or [])
        url = _next_link(headers.get("Link"), registry)
    prefix = domain["repo_prefix"]
    return [
        {"id": repo, "ref": f"{host}/{repo}", "name": repo}
        for repo in repos
        if repo.startswith(prefix)
    ]


def fetch_oci_collection(domain: dict, args: argparse.Namespace) -> list[dict]:
    registry, namespace = domain["registry"], domain["namespace"]
    token = _registry_token(domain, namespace)
    manifest = _get_json(
        f"{registry}/v2/{namespace}/manifests/latest",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": OCI_MANIFEST_MEDIA_TYPE,
        },
    )
    layer = next(
        (
            entry
            for entry in manifest.get("layers") or []
            if entry.get("mediaType") == COLLECTION_MEDIA_TYPE
        ),
        None,
    )
    if layer is None:
        raise SourceError(
            f"no devcontainer-collection.json layer in "
            f"{registry}/v2/{namespace}/manifests/latest. The namespace may "
            f"not publish collection metadata; list its source repository "
            f"instead (see references/trust-domains.md)."
        )
    blob = _get_blob(f"{registry}/v2/{namespace}/blobs/{layer['digest']}", token)
    try:
        collection = json.loads(blob)
    except json.JSONDecodeError as exc:
        raise SourceError(
            f"collection blob from {namespace} is not JSON ({exc})."
        ) from exc
    entries = collection.get("features") or collection.get("templates") or []
    deprecated = sum(1 for entry in entries if entry.get("deprecated"))
    if deprecated:
        print(
            f"note [{domain['name']}]: skipped {deprecated} deprecated "
            f"entr{'y' if deprecated == 1 else 'ies'}",
            file=sys.stderr,
        )
    return [
        {
            "id": entry["id"],
            "ref": (
                f"{domain['ref_prefix']}{entry['id']}"
                f":{_major_tag(entry.get('version'))}"
            ),
            "name": entry.get("name") or entry["id"],
            "version": entry.get("version"),
            "options": sorted((entry.get("options") or {}).keys()),
        }
        for entry in entries
        if entry.get("id") and not entry.get("deprecated")
    ]


def fetch_ngc_catalog(domain: dict, args: argparse.Namespace) -> list[dict]:
    host = _host(domain["registry"])
    term = args.filter or "*"
    seen: set[str] = set()
    items: list[dict] = []
    total = 0
    for page in range(NGC_MAX_PAGES):
        query = json.dumps({"query": term, "page": page, "pageSize": NGC_PAGE_SIZE})
        url = f"{domain['search_api']}?{urllib.parse.urlencode({'q': query})}"
        data = _get_json(url)
        total = data.get("resultTotal") or 0
        resources = [
            resource
            for group in data.get("results") or []
            for resource in group.get("resources") or []
        ]
        if not resources:
            break
        for resource in resources:
            resource_id = resource.get("resourceId")
            if not resource_id or resource_id in seen:
                continue
            if not args.all_orgs and not resource_id.startswith(
                domain["default_org"] + "/"
            ):
                continue
            seen.add(resource_id)
            items.append(
                {
                    "id": resource_id,
                    "ref": f"{host}/{resource_id}",
                    "name": resource.get("displayName") or resource_id,
                }
            )
        if len(items) >= args.limit or (page + 1) * NGC_PAGE_SIZE >= total:
            break
    if len(items) > args.limit or total > len(items):
        org_note = "all orgs" if args.all_orgs else f"{domain['default_org']}/* only"
        print(
            f"note [ngc]: NGC reports {total} public containers; showing "
            f"{min(len(items), args.limit)} ({org_note}). Narrow with "
            f"--filter TERM, or broaden with --all-orgs / --limit N.",
            file=sys.stderr,
        )
    return items[: args.limit]


FETCHERS = {
    "docker-registry": fetch_docker_registry,
    "oci-collection": fetch_oci_collection,
    "ngc-catalog": fetch_ngc_catalog,
}


def _match_domain(ref: str) -> dict | None:
    matches = [
        domain for domain in TRUST_DOMAINS if ref.startswith(domain["ref_prefix"])
    ]
    return max(matches, key=lambda d: len(d["ref_prefix"])) if matches else None


def list_tags(args: argparse.Namespace) -> int:
    ref = args.tags.split(":", 1)[0]
    domain = _match_domain(ref)
    if domain is None:
        allowed = ", ".join(d["ref_prefix"] + "*" for d in TRUST_DOMAINS)
        print(
            f"error: `{ref}` is not under a trusted domain. This script "
            f"only enumerates trusted sources ({allowed}). If the user "
            f"explicitly requested this source, query it directly with "
            f"docker/oras/curl instead.",
            file=sys.stderr,
        )
        return 2
    registry = domain["registry"]
    repository = ref.removeprefix(_host(registry) + "/")
    try:
        if domain["kind"] == "docker-registry":
            data = _get_json(f"{registry}/v2/{repository}/tags/list")
        else:
            token = _registry_token(domain, repository)
            data = _get_json(
                f"{registry}/v2/{repository}/tags/list",
                headers={"Authorization": f"Bearer {token}"},
            )
    except SourceError as exc:
        print(f"error [{domain['name']}]: {exc}", file=sys.stderr)
        return 1
    tags = data.get("tags") or []
    truncated = len(tags) > args.limit
    shown = tags[: args.limit]
    if truncated:
        print(
            f"note: {len(tags)} tags; showing the first {args.limit} in "
            f"registry order. Raise --limit to see more.",
            file=sys.stderr,
        )
    if args.format == "json":
        document = {
            "ref": ref,
            "source": domain["name"],
            "tags": shown,
            "truncated": truncated,
        }
        print(json.dumps(document, indent=2))
    else:
        for tag in shown:
            print(tag)
    return 0


def list_sources(args: argparse.Namespace) -> int:
    domains = [
        domain
        for domain in TRUST_DOMAINS
        if (not args.kind or domain["provides"] == args.kind)
        and (not args.source or domain["name"] == args.source)
    ]
    if not domains:
        names = ", ".join(domain["name"] for domain in TRUST_DOMAINS)
        print(
            f"error: no trusted source matches --kind/--source. Known "
            f"sources: {names}.",
            file=sys.stderr,
        )
        return 2
    results = []
    for domain in domains:
        try:
            items = FETCHERS[domain["kind"]](domain, args)
            if args.filter and domain["kind"] != "ngc-catalog":
                needle = args.filter.lower()
                items = [
                    item
                    for item in items
                    if needle in item["id"].lower()
                    or needle in (item.get("name") or "").lower()
                ]
            if len(items) > args.limit:
                print(
                    f"note [{domain['name']}]: {len(items)} items; showing "
                    f"the first {args.limit}. Raise --limit or use --filter.",
                    file=sys.stderr,
                )
                items = items[: args.limit]
            results.append({**_source_meta(domain), "ok": True, "items": items})
        except SourceError as exc:
            print(f"error [{domain['name']}]: {exc}", file=sys.stderr)
            results.append(
                {**_source_meta(domain), "ok": False, "error": str(exc), "items": []}
            )
    if args.format == "json":
        print(json.dumps({"sources": results}, indent=2))
    else:
        for source in results:
            for item in source["items"]:
                columns = [source["provides"], item["ref"], item.get("name") or ""]
                if item.get("options"):
                    columns.append("options: " + ",".join(item["options"]))
                print("\t".join(columns))
    return 0 if all(source["ok"] for source in results) else 1


def _source_meta(domain: dict) -> dict:
    return {
        "name": domain["name"],
        "kind": domain["kind"],
        "provides": domain["provides"],
    }


def self_test() -> int:
    """Environment smoke check: Python version and endpoint reachability."""
    probes = {
        "mcr.microsoft.com": "https://mcr.microsoft.com/v2/_catalog?n=1",
        "ghcr.io": (
            "https://ghcr.io/token"
            "?scope=repository:devcontainers/features:pull&service=ghcr.io"
        ),
        "api.ngc.nvidia.com": (
            "https://api.ngc.nvidia.com/v2/search/catalog/resources/CONTAINER?"
            + urllib.parse.urlencode(
                {"q": json.dumps({"query": "cuda", "page": 0, "pageSize": 1})}
            )
        ),
        "nvcr.io": "https://nvcr.io/proxy_auth?scope=repository:nvidia/cuda:pull",
    }
    endpoints = {}
    for host, url in probes.items():
        try:
            _get_json(url)
            endpoints[host] = "ok"
        except SourceError as exc:
            endpoints[host] = f"error: {exc}"
    python_ok = sys.version_info >= (3, 11)
    passed = python_ok and all(status == "ok" for status in endpoints.values())
    print(
        json.dumps(
            {
                "self_test": "pass" if passed else "fail",
                "python": ".".join(map(str, sys.version_info[:3])),
                "endpoints": endpoints,
            },
            indent=2,
        )
    )
    return 0 if passed else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "List images, features, and templates available from the "
            "trusted dev container sources."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
Modes:
  default      list assets from every matching trusted source
  --tags REF   list tags/versions for one image or feature/template ref
  --self-test  environment smoke check (Python + endpoint reachability)

Exit codes: 0 success; 1 at least one source failed (stdout still holds
the partial results); 2 bad arguments or --tags ref outside every trusted
domain.

Examples:
  uv run scripts/list_sources.py
  uv run scripts/list_sources.py --kind features --format json
  uv run scripts/list_sources.py --kind images --source ngc --filter pytorch
  uv run scripts/list_sources.py --tags mcr.microsoft.com/devcontainers/python
  uv run scripts/list_sources.py --tags nvcr.io/nvidia/pytorch --limit 40
  uv run scripts/list_sources.py --self-test
""",
    )
    parser.add_argument(
        "--kind",
        choices=["images", "features", "templates"],
        help="limit listing to one asset kind",
    )
    parser.add_argument(
        "--source",
        help="limit listing to one trusted source by name (see --help epilog)",
    )
    parser.add_argument(
        "--filter",
        help=(
            "substring filter on id/name; for the NGC source it is passed "
            "to the server-side search instead"
        ),
    )
    parser.add_argument(
        "--tags",
        metavar="REF",
        help="list tags for one ref, e.g. nvcr.io/nvidia/pytorch",
    )
    parser.add_argument(
        "--all-orgs",
        action="store_true",
        help="NGC: include images outside the nvidia/ org",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=200,
        help="max items per source and max tags (default: 200)",
    )
    parser.add_argument(
        "--format",
        choices=["table", "json"],
        default="table",
        help="output format (default: table, tab-separated)",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="check Python version and endpoint reachability, then exit",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.limit < 1:
        print("error: --limit must be >= 1.", file=sys.stderr)
        return 2
    if args.self_test:
        return self_test()
    if args.tags:
        return list_tags(args)
    return list_sources(args)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except BrokenPipeError:
        # Downstream (e.g. `| head`) closed the pipe; not an error. Detach
        # stdout so the interpreter does not raise again on shutdown.
        import os

        os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())
        sys.exit(0)
