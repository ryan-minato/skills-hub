#!/usr/bin/env python3
"""Lightweight secrets detector using only the Python standard library.

Fallback engine for environments where uv (and therefore detect-secrets)
is unavailable. Combines well-known token-prefix patterns (cloud keys,
VCS tokens, private-key headers, JWTs) with keyword-plus-Shannon-entropy
detection for generic assignments. Output mirrors the detect-secrets
wrapper: findings carry the SHA-1 hash of the secret value, never the
value itself.

Lines carrying a scanner suppression comment (pragma: allowlist secret,
gitleaks:allow, detect-secrets:disable, trailing nosec) are skipped and
counted on stderr, matching how the preferred engine treats them.

Exit codes: 0 scan completed, 1 self-test failure or read error,
2 invalid arguments.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
from collections import Counter
from pathlib import Path
from typing import NamedTuple, Optional

DEFAULT_ENTROPY_BASE64 = 4.5
DEFAULT_ENTROPY_HEX = 3.0
DEFAULT_ENTROPY_MIXED = 3.5

_SUPPRESSION = re.compile(
    r"pragma: allowlist secret|gitleaks:allow|detect-secrets:disable|#\s*nosec\b"
)

_PLACEHOLDER_SHAPES = re.compile(
    r"^(?:\$\{[^}]*\}|\{\{[^}]*\}\}|<[^>]*>|%s|\*{3,}|[xX]{4,}|\.{3,})$"
)
_PLACEHOLDER_WORDS = (
    "your_",
    "replace",
    "change",
    "todo",
    "example",
    "dummy",
    "sample",
    "placeholder",
    "password",
    "secret",
    "insert",
    "xxxx",
)


def _is_placeholder(value: str) -> bool:
    lowered = value.lower()
    if any(word in lowered for word in _PLACEHOLDER_WORDS):
        return True
    if _PLACEHOLDER_SHAPES.fullmatch(value):
        return True
    return len(set(value)) <= 2


def _shannon_entropy(value: str) -> float:
    counts = Counter(value)
    length = len(value)
    return -sum(c / length * math.log2(c / length) for c in counts.values())


def _entropy_flagged(value: str, hex_limit: float, base64_limit: float) -> bool:
    entropy = _shannon_entropy(value)
    if re.fullmatch(r"[0-9a-fA-F]+", value):
        return entropy >= hex_limit
    if re.fullmatch(r"[A-Za-z0-9+/=_-]+", value):
        return entropy >= base64_limit
    return entropy >= DEFAULT_ENTROPY_MIXED


class SecretDetector(NamedTuple):
    type_label: str
    pattern: re.Pattern
    group: Optional[str]  # capture group holding the secret; None = whole match
    placeholder_check: bool


DETECTORS = [
    SecretDetector(
        "Private Key",
        re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY(?: BLOCK)?-----"),
        None,
        False,
    ),
    SecretDetector(
        "AWS Access Key",
        re.compile(r"(?<![A-Z0-9])(?:AKIA|ASIA)[0-9A-Z]{16}(?![A-Z0-9])"),
        None,
        False,
    ),
    SecretDetector(
        "GitHub Token",
        re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{36,255}|github_pat_[A-Za-z0-9_]{22,255})"),
        None,
        False,
    ),
    SecretDetector(
        "GitLab Token",
        re.compile(r"\bglpat-[A-Za-z0-9_-]{20,}"),
        None,
        False,
    ),
    SecretDetector(
        "Slack Token",
        re.compile(r"\bxox[abeprs]-[A-Za-z0-9-]{10,}"),
        None,
        False,
    ),
    SecretDetector(
        "Google API Key",
        re.compile(r"\bAIza[0-9A-Za-z_-]{35}"),
        None,
        False,
    ),
    SecretDetector(
        "API Key (prefixed)",
        re.compile(r"\b(?:sk_live_[A-Za-z0-9]{16,}|sk-ant-[A-Za-z0-9_-]{20,}|sk-proj-[A-Za-z0-9_-]{20,})"),
        None,
        False,
    ),
    SecretDetector(
        "JWT",
        re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{5,}"),
        None,
        False,
    ),
    SecretDetector(
        "Bearer Token",
        re.compile(r"\b[Bb]earer\s+(?P<secret>[A-Za-z0-9._~+/-]{20,}=*)"),
        "secret",
        True,
    ),
    SecretDetector(
        "Connection String Credential",
        re.compile(r"\b[a-z][a-z0-9+.-]*://[^/\s:@]+:(?P<secret>[^@\s]{4,})@"),
        "secret",
        True,
    ),
]

# No leading \b: keywords legitimately appear after prefixes joined by
# underscores (db_password, aws_access_key_id), which have no word boundary.
# The optional quote before the separator covers JSON keys ("secret": ...).
_KEYWORD_ASSIGNMENT = re.compile(
    r"(?i)(?:api[_-]?key|apikey|secret|token|passw(?:or)?d|passwd|credential"
    r"|auth[_-]?token|access[_-]?key|private[_-]?key)\w*"
    r"[\"']?\s*[:=]+\s*[\"']?(?P<value>[^\s\"']{8,})"
)

_URL_SHAPE = re.compile(r"^[a-z][a-z0-9+.-]*://", re.IGNORECASE)


def _hash(value: str) -> str:
    # Same hashing detect-secrets uses, so findings from both engines can
    # be correlated without ever printing the raw value.
    return hashlib.sha1(value.encode("utf-8")).hexdigest()


def scan_lines(
    lines: list, source: str, hex_limit: float, base64_limit: float
) -> "tuple[list, int]":
    findings = []
    suppressed = 0
    for lineno, line in enumerate(lines, 1):
        if _SUPPRESSION.search(line):
            suppressed += 1
            continue
        flagged_values = set()
        for detector in DETECTORS:
            for match in detector.pattern.finditer(line):
                value = match.group(detector.group) if detector.group else match.group(0)
                if detector.placeholder_check and _is_placeholder(value):
                    continue
                if value in flagged_values:
                    continue
                flagged_values.add(value)
                findings.append(
                    {
                        "file": source,
                        "line": lineno,
                        "type": detector.type_label,
                        "is_verified": False,
                        "hashed_secret": _hash(value),
                    }
                )
        for match in _KEYWORD_ASSIGNMENT.finditer(line):
            value = match.group("value")
            if value in flagged_values or _is_placeholder(value):
                continue
            # Bare URLs assigned to token_url-style fields are endpoints,
            # not secrets; credentialed URLs are caught above.
            if _URL_SHAPE.match(value):
                continue
            if not _entropy_flagged(value, hex_limit, base64_limit):
                continue
            flagged_values.add(value)
            findings.append(
                {
                    "file": source,
                    "line": lineno,
                    "type": "Keyword + High Entropy",
                    "is_verified": False,
                    "hashed_secret": _hash(value),
                }
            )
    return findings, suppressed


# --- self-test -------------------------------------------------------------


def run_self_test() -> int:
    """Smoke test: prove the full pipeline runs in this environment.

    Detector correctness is covered by design-time tests maintained with
    the skill's development; this only verifies the script executes. The
    sample key is assembled at runtime so this file never contains a
    contiguous secret-shaped literal.
    """
    aws_key = "AKIA" + "IOSFODNN7" + "EXAMPLE"
    lines = [f"aws_access_key_id = {aws_key}", 'api_key = "YOUR_API_KEY"']
    try:
        findings, _ = scan_lines(
            lines, "<self-test>", DEFAULT_ENTROPY_HEX, DEFAULT_ENTROPY_BASE64
        )
    except Exception as exc:  # any crash means the engine is unusable
        print(f"FAIL: pipeline raised {exc!r}", file=sys.stderr)
        print(json.dumps({"self_test": "fail"}))
        return 1
    ok = any(finding["type"] == "AWS Access Key" for finding in findings)
    print(
        "PASS: pipeline ran and detected the sample"
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
            "Stdlib-only secrets scanner (fallback engine). Detects private "
            "key headers, AWS/GitHub/GitLab/Slack/Stripe/Anthropic/OpenAI "
            "token prefixes, JWTs, bearer tokens, connection-string "
            "credentials, and keyword assignments with high-entropy values. "
            "Findings report a SHA-1 hash of the value, never the value."
        ),
        epilog=(
            "Examples:\n"
            "  python3 secret_scan_lite.py --file .env deploy.sh\n"
            "  python3 secret_scan_lite.py --text 'token = ...'\n"
            "Exit codes: 0 scan completed, 1 error or self-test failure, "
            "2 invalid arguments."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--file", nargs="+", default=[], help="files to scan")
    parser.add_argument("--text", help="inline text to scan")
    parser.add_argument(
        "--entropy-base64",
        type=float,
        default=DEFAULT_ENTROPY_BASE64,
        help="entropy threshold for base64-charset values (default: %(default)s)",
    )
    parser.add_argument(
        "--entropy-hex",
        type=float,
        default=DEFAULT_ENTROPY_HEX,
        help="entropy threshold for hex-charset values (default: %(default)s)",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="verify the script can run in this environment, then exit",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if not args.file and args.text is None:
        parser.error("provide --file and/or --text (or --self-test)")

    sources = []
    findings = []
    suppressed_total = 0
    had_error = False
    for path_str in args.file:
        path = Path(path_str)
        if not path.is_file():
            print(
                f"error: {path_str}: not a file. Findings would be "
                f"incomplete; fix the path and re-run.",
                file=sys.stderr,
            )
            had_error = True
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            print(
                f"warning: {path_str}: not valid UTF-8, skipped. Record it "
                f"as an unscanned binary in the report.",
                file=sys.stderr,
            )
            continue
        sources.append(path_str)
        file_findings, suppressed = scan_lines(
            text.splitlines(), path_str, args.entropy_hex, args.entropy_base64
        )
        findings.extend(file_findings)
        suppressed_total += suppressed
    if args.text is not None:
        sources.append("<inline-text>")
        text_findings, suppressed = scan_lines(
            args.text.splitlines(), "<inline-text>", args.entropy_hex, args.entropy_base64
        )
        findings.extend(text_findings)
        suppressed_total += suppressed

    if suppressed_total:
        print(
            f"note: skipped {suppressed_total} line(s) carrying scanner "
            f"suppression comments",
            file=sys.stderr,
        )
    print(
        json.dumps(
            {
                "engine": "lite",
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
