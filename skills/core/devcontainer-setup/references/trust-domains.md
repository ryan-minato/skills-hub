# Trust domains: endpoint mechanics and extension

Read this when `scripts/list_sources.py` errors, when you must enumerate a
registry manually, or when the user asks to add a trusted source.

The script's `TRUST_DOMAINS` table is the single source of truth for what
is trusted. Each entry has a `kind` that maps to one fetcher; the three
kinds cover how the ecosystem distributes assets.

## docker-registry (images on a Docker Registry v2)

```bash
# Catalog (whole registry; filter client-side by repo prefix)
curl -s https://mcr.microsoft.com/v2/_catalog
# Tags for one repository (anonymous on MCR)
curl -s https://mcr.microsoft.com/v2/devcontainers/python/tags/list
```

Responses: `{"repositories": [...]}` and `{"name": ..., "tags": [...]}`.
MCR currently returns the full catalog in one response; the script still
follows `Link: <...>; rel="next"` headers defensively in case pagination
appears.

## oci-collection (Features/Templates as OCI artifacts)

Feature and Template collections publish an auto-generated
`devcontainer-collection.json` to the namespace itself, tagged `latest`.
This works for ANY namespace — including ones absent from the
containers.dev index (which is why `stacit-ai/devcontainer-features`
enumerates fine). Three steps:

```bash
NS=devcontainers/features
TOKEN=$(curl -s "https://ghcr.io/token?scope=repository:${NS}:pull&service=ghcr.io" | jq -r .token)
DIGEST=$(curl -s -H "Authorization: Bearer ${TOKEN}" \
  -H "Accept: application/vnd.oci.image.manifest.v1+json" \
  "https://ghcr.io/v2/${NS}/manifests/latest" \
  | jq -r '.layers[] | select(.mediaType == "application/vnd.devcontainers.collection.layer.v1+json") | .digest')
curl -sL -H "Authorization: Bearer ${TOKEN}" \
  "https://ghcr.io/v2/${NS}/blobs/${DIGEST}"
```

Gotchas encoded in the script:

- The blob GET answers with a 307 to pre-signed blob storage. The
  redirected request must NOT carry the `Authorization` header (the
  storage backend rejects it); `curl -L` happens to drop it cross-host,
  but naive HTTP clients resend it and fail.
- The collection body is `{"sourceInformation": ..., "features": [...]}`
  or `{..., "templates": [...]}` — id, version, name, and options per
  entry.
- Per-item tags: same token flow with
  `scope=repository:<namespace>/<id>:pull`, then
  `GET /v2/<namespace>/<id>/tags/list`.

There is also a registered-collections index at
<https://containers.dev/static/devcontainer-index.json> (the data behind
containers.dev/features). It only lists publishers who registered there —
do not treat absence from it as nonexistence; the OCI route above is
authoritative.

## ngc-catalog (NVIDIA NGC)

Catalog search (anonymous; undocumented, so treat failures as endpoint
drift, not user error):

```bash
curl -s "https://api.ngc.nvidia.com/v2/search/catalog/resources/CONTAINER?q=$(python3 -c 'import json,urllib.parse;print(urllib.parse.quote(json.dumps({"query":"pytorch","page":0,"pageSize":25})))')"
```

Response: `{"resultTotal": N, "results": [{"resources": [{"resourceId":
"nvidia/pytorch", "displayName": ...}]}]}`. Only the
`/v2/search/catalog/...` path works anonymously — `/v2/search/resources/...`
returns 401 and `/v2/repos` errors.

Tags go through the nvcr.io registry with an anonymous token from
`proxy_auth` (not `authn.nvidia.com`):

```bash
TOKEN=$(curl -s "https://nvcr.io/proxy_auth?scope=repository:nvidia/pytorch:pull" | jq -r .token)
curl -s -H "Authorization: Bearer ${TOKEN}" \
  https://nvcr.io/v2/nvidia/pytorch/tags/list
```

## Adding a trusted source

Only extend trust when the user explicitly asks for it; record the request
in your summary.

1. Existing mechanism: append one entry to `TRUST_DOMAINS` in the skill's
   `scripts/list_sources.py` with the same keys as its siblings (`name`,
   `kind`, `provides`, `ref_prefix`, plus the kind's endpoint fields). Feature/Template collections published per
   the dev container spec are always `oci-collection`; plain image
   registries are `docker-registry`.
2. New mechanism (a registry that is neither Docker Registry v2 nor an
   OCI collection): write one fetcher returning
   `[{"id", "ref", "name", ...}]` and register it in `FETCHERS`.
3. Update the policy table in `SKILL.md` so the policy and the script
   stay in sync, and re-run the script live to confirm the new source
   enumerates.
