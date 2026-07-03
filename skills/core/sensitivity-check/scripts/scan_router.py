#!/usr/bin/env -S uv run
# /// script
# dependencies = [
#   "tiktoken>=0.7,<1",
# ]
# requires-python = ">=3.11"
# ///
"""Route scan targets by size before any sensitive-data scan.

Classifies each item so the caller never reads a huge file into its
context window by accident:

- "deep"   — at or under the token threshold; read the content directly.
- "script" — over the threshold; hand it to the scan scripts.
- "binary" — not valid UTF-8 in the first 8 KB; record it, do not scan.

Under ``uv run`` the PEP 723 block above provides tiktoken and counts are
exact (cl100k_base). Plain ``python3`` ignores the inline metadata — the
code itself is stdlib-only — and falls back to a characters/4 estimate
marked with "estimated": true.

Exit codes: 0 success, 1 unreadable input or self-test failure,
2 invalid arguments.
"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

DEFAULT_THRESHOLD = 4000
BINARY_PROBE_BYTES = 8192
CHARS_PER_TOKEN_ESTIMATE = 4


def _load_encoder():
    try:
        import tiktoken
    except ImportError:
        return None
    try:
        return tiktoken.get_encoding("cl100k_base")
    except Exception as exc:  # network/cache failures degrade to estimate
        print(f"note: tiktoken unavailable ({exc}); estimating", file=sys.stderr)
        return None


def _count_tokens(text: str, encoder) -> "tuple[int, bool]":
    """Return (token_count, estimated)."""
    if encoder is not None:
        return len(encoder.encode(text)), False
    return max(1, len(text) // CHARS_PER_TOKEN_ESTIMATE), True


def _is_binary(path: Path) -> bool:
    with path.open("rb") as handle:
        probe = handle.read(BINARY_PROBE_BYTES)
    try:
        probe.decode("utf-8")
    except UnicodeDecodeError as exc:
        # A multi-byte sequence cut off at the probe boundary is not
        # evidence of binary content.
        if exc.start < len(probe) - 4:
            return True
        try:
            probe[: exc.start].decode("utf-8")
        except UnicodeDecodeError:
            return True
    return False


def _route_text(item: str, text: str, threshold: int, encoder) -> dict:
    count, estimated = _count_tokens(text, encoder)
    entry = {
        "item": item,
        "token_count": count,
        "estimated": estimated,
        "method": "deep" if count <= threshold else "script",
    }
    if estimated:
        entry["note"] = (
            "token count estimated from characters/4; flag this in the report"
        )
    return entry


def _route_file(path_str: str, threshold: int, encoder) -> dict:
    path = Path(path_str)
    if not path.is_file():
        return {
            "item": path_str,
            "error": "file not found; fix the path and re-run",
        }
    try:
        if _is_binary(path):
            return {
                "item": path_str,
                "token_count": None,
                "estimated": False,
                "method": "binary",
                "note": "not valid UTF-8; record as unscanned in the report",
            }
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        return {"item": path_str, "error": f"could not read file: {exc}"}
    return _route_text(path_str, text, threshold, encoder)


# --- self-test -------------------------------------------------------------


def run_self_test() -> int:
    """Smoke test: prove routing runs in this environment.

    Routing correctness is covered by design-time tests maintained with
    the skill's development; this only verifies the script executes.
    """
    encoder = _load_encoder()
    if encoder is None:
        print("note: tiktoken not installed; counts are estimates", file=sys.stderr)
    try:
        text_entry = _route_text("<t>", "short text", DEFAULT_THRESHOLD, encoder)
        with tempfile.TemporaryDirectory(prefix="scan_router_selftest_") as tmp:
            binary_path = Path(tmp) / "blob.bin"
            binary_path.write_bytes(b"\x00\xff\xfe\x01" * 64)
            binary_entry = _route_file(str(binary_path), DEFAULT_THRESHOLD, encoder)
    except Exception as exc:  # any crash means routing is unusable
        print(f"FAIL: routing raised {exc!r}", file=sys.stderr)
        print(json.dumps({"self_test": "fail"}))
        return 1
    ok = text_entry["method"] == "deep" and binary_entry["method"] == "binary"
    print(
        "PASS: routing ran for text and binary inputs"
        if ok
        else f"FAIL: unexpected routing: {text_entry} / {binary_entry}",
        file=sys.stderr,
    )
    print(json.dumps({"self_test": "pass" if ok else "fail"}))
    return 0 if ok else 1


# --- CLI --------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Classify scan targets as deep (read directly), script (run "
            "scan scripts), or binary (record, do not scan) by token count. "
            "Run before any sensitive-data scan."
        ),
        epilog=(
            "Examples:\n"
            "  uv run scan_router.py --files a.txt b.log   # exact counts\n"
            "  python3 scan_router.py --files a.txt        # chars/4 estimate\n"
            "Exit codes: 0 success, 1 unreadable input or self-test failure, "
            "2 invalid arguments."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--files", nargs="+", default=[], help="files to route")
    parser.add_argument("--text", help="inline text to route")
    parser.add_argument(
        "--threshold",
        type=int,
        default=DEFAULT_THRESHOLD,
        help="max tokens for the deep method (default: %(default)s)",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="verify the script can run in this environment, then exit",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if not args.files and args.text is None:
        parser.error("provide --files and/or --text (or --self-test)")

    encoder = _load_encoder()
    items = [_route_file(path, args.threshold, encoder) for path in args.files]
    if args.text is not None:
        items.append(
            _route_text("<inline-text>", args.text, args.threshold, encoder)
        )

    had_error = any("error" in item for item in items)
    for item in items:
        if "error" in item:
            print(f"error: {item['item']}: {item['error']}", file=sys.stderr)
    print(
        json.dumps(
            {
                "engine": "router",
                "threshold": args.threshold,
                "items": items,
            },
            indent=2,
        )
    )
    return 1 if had_error else 0


if __name__ == "__main__":
    sys.exit(main())
