#!/usr/bin/env -S uv run
# /// script
# dependencies = [
#   "detect-secrets>=1.4,<2",
# ]
# requires-python = ">=3.11"
# ///
"""Secrets detector built on detect-secrets (preferred engine).

Drives detect-secrets through its Python API (not a subprocess), so
results do not depend on a console entry point being on PATH. Inline
text is written to a temporary file because detect-secrets scans file
paths only. Findings carry the SHA-1 hash of the secret value, never
the value itself; re-read the source at the reported line to review it.

If uv or detect-secrets is unavailable, use the stdlib fallback
``python3 scripts/secret_scan_lite.py`` instead.

Exit codes: 0 scan completed, 1 dependency/self-test failure,
2 invalid arguments.
"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path


def _scan_files(paths: list) -> list:
    try:
        from detect_secrets import SecretsCollection
        from detect_secrets.settings import default_settings
    except ImportError as exc:
        print(
            f"error: dependency missing ({exc}). Run this script with "
            f"'uv run' so PEP 723 dependencies resolve, or fall back to "
            f"'python3 scripts/secret_scan_lite.py' (stdlib only).",
            file=sys.stderr,
        )
        raise SystemExit(1) from exc

    collection = SecretsCollection()
    with default_settings():
        for path in paths:
            collection.scan_file(path)

    findings = []
    for filename, secret in collection:
        findings.append(
            {
                "file": filename,
                "line": secret.line_number,
                "type": secret.type,
                "is_verified": bool(secret.is_verified),
                "hashed_secret": secret.secret_hash,
            }
        )
    findings.sort(key=lambda f: (f["file"], f["line"], f["type"]))
    return findings


def _run_scan(file_paths: list, inline_text: "str | None") -> "tuple[list, list, bool]":
    """Return (sources, findings, had_error) with inline text mapped back."""
    sources = []
    paths = []
    had_error = False
    for path_str in file_paths:
        if not Path(path_str).is_file():
            print(
                f"error: {path_str}: not a file. Findings would be "
                f"incomplete; fix the path and re-run.",
                file=sys.stderr,
            )
            had_error = True
            continue
        sources.append(path_str)
        paths.append(path_str)

    temp_path = None
    label_map = {}
    try:
        if inline_text is not None:
            with tempfile.NamedTemporaryFile(
                "w",
                prefix="sensitivity_check_",
                suffix=".txt",
                delete=False,
                encoding="utf-8",
            ) as handle:
                handle.write(inline_text)
                temp_path = handle.name
            label_map[temp_path] = "<inline-text>"
            sources.append("<inline-text>")
            paths.append(temp_path)
        findings = _scan_files(paths)
    finally:
        if temp_path is not None:
            Path(temp_path).unlink(missing_ok=True)

    for finding in findings:
        finding["file"] = label_map.get(finding["file"], finding["file"])
    return sources, findings, had_error


# --- self-test -------------------------------------------------------------


def run_self_test() -> int:
    """Smoke test: prove detect-secrets is importable and a scan runs."""
    aws_key = "AKIA" + "IOSFODNN7" + "EXAMPLE"  # assembled; not a real key
    _, findings, _ = _run_scan([], f"aws_access_key_id = {aws_key}\n")
    ok = any(finding["type"] == "AWS Access Key" for finding in findings)
    print(
        "PASS: detect-secrets scanned the sample"
        if ok
        else f"FAIL: expected an AWS Access Key finding, got {findings}",
        file=sys.stderr,
    )
    print(json.dumps({"self_test": "pass" if ok else "fail"}))
    return 0 if ok else 1


# --- CLI --------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Secrets scanner backed by detect-secrets (preferred engine). "
            "Findings report a SHA-1 hash of the value, never the value."
        ),
        epilog=(
            "Examples:\n"
            "  uv run secret_scan.py --file .env deploy.sh\n"
            "  uv run secret_scan.py --text 'token = ...'\n"
            "Exit codes: 0 scan completed, 1 dependency/self-test failure, "
            "2 invalid arguments."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--file", nargs="+", default=[], help="files to scan")
    parser.add_argument("--text", help="inline text to scan")
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="verify the engine can run in this environment, then exit",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if not args.file and args.text is None:
        parser.error("provide --file and/or --text (or --self-test)")

    sources, findings, had_error = _run_scan(args.file, args.text)
    print(
        json.dumps(
            {
                "engine": "detect-secrets",
                "sources": sources,
                "finding_count": len(findings),
                "findings": findings,
            },
            indent=2,
        )
    )
    return 1 if had_error else 0


if __name__ == "__main__":
    sys.exit(main())
