#!/usr/bin/env python3
"""Lightweight PII detector using only the Python standard library.

Fallback engine for environments where uv (and therefore Presidio) is
unavailable. Detects structured PII with per-entity regexes plus checksum
or range validators, so short numeric patterns only fire when they survive
a stronger test than shape alone (Luhn for cards, ISO 7064 MOD 11-2 for CN
resident IDs, the official check digit for JP My Number, mod-31 for CN
USCC). It performs no NER: personal names, street addresses, and free-form
birth dates are NOT detected — cover those with a model-based engine or by
reading the content directly.

Exit codes: 0 scan completed, 1 self-test failure or read error,
2 invalid arguments.
"""

from __future__ import annotations

import argparse
import ipaddress
import json
import re
import string
import sys
from pathlib import Path
from typing import Callable, NamedTuple, Optional

CONTEXT_CHARS = 40
DEFAULT_THRESHOLD = 0.5

# Widely published example/test values that pass their checksums. They are
# documentation noise, not leaks, so they are dropped (counted on stderr).
# Comparison is against the match with spaces/hyphens removed, uppercased.
KNOWN_TEST_VALUES = {
    "4111111111111111",  # Visa test card
    "4242424242424242",  # Stripe test card
    "4012888888881881",  # Visa test card
    "5555555555554444",  # Mastercard test card
    "378282246310005",  # Amex test card
    "6011111111111117",  # Discover test card
    "078051120",  # famous misused SSN (Hilda Whitcher)
    "219099999",  # SSA advertising sample SSN
    "13800138000",  # China Mobile example number
    "123456789018",  # My Number check-digit example
    "11010519491231002X",  # GB 11643 documentation example ID
    "91350100M000100Y43",  # GB 32100-2015 documentation example USCC
}


def _digits(value: str) -> str:
    return re.sub(r"[ -]", "", value)


def _luhn_ok(digits: str) -> bool:
    total = 0
    for i, ch in enumerate(reversed(digits)):
        d = int(ch)
        if i % 2 == 1:
            d = d * 2 - 9 if d > 4 else d * 2
        total += d
    return total % 10 == 0


_CARD_PREFIX = re.compile(
    r"^(?:4|5[1-5]|2(?:22[1-9]|2[3-9]\d|[3-6]\d\d|7[01]\d|720)"
    r"|3[47]|3(?:0[0-5]|[68])|6(?:011|5)|35|2131|1800)"
)


def _valid_card(match: str) -> bool:
    digits = _digits(match)
    return (
        13 <= len(digits) <= 19
        and bool(_CARD_PREFIX.match(digits))
        and _luhn_ok(digits)
    )


def _valid_ipv4(match: str) -> bool:
    try:
        ipaddress.IPv4Address(match)
    except ValueError:
        return False
    return True


def _valid_ipv6(match: str) -> bool:
    if match.count(":") < 2:
        return False
    try:
        ipaddress.IPv6Address(match)
    except ValueError:
        return False
    return True


_DATE_SHAPES = (
    re.compile(r"\d{4}-\d{2}-\d{2}"),
    re.compile(r"\d{1,2}[-/]\d{1,2}[-/]\d{2,4}"),
)
_SSN_SHAPE = re.compile(r"\d{3}[-. ]\d{2}[-. ]\d{4}")


def _valid_phone(match: str) -> bool:
    digit_count = len(re.sub(r"\D", "", match))
    if not 8 <= digit_count <= 15:
        return False
    # Bare digit runs (order IDs, hashes) are too ambiguous: require an
    # international prefix or at least one separator.
    if not match.startswith("+") and re.fullmatch(r"\d+", match):
        return False
    if any(shape.fullmatch(match) for shape in _DATE_SHAPES):
        return False
    # Leave the 3-2-4 shape to the US_SSN detector.
    if _SSN_SHAPE.fullmatch(match):
        return False
    return True


def _valid_ssn(match: str) -> bool:
    area, group, serial = re.split(r"[-. ]", match)
    if area in {"000", "666"} or area.startswith("9"):
        return False
    return group != "00" and serial != "0000"


CN_ID_WEIGHTS = (7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2)
CN_ID_CHECK_MAP = "10X98765432"


def _valid_cn_resident_id(match: str) -> bool:
    value = match.upper()
    total = sum(int(d) * w for d, w in zip(value[:17], CN_ID_WEIGHTS))
    return CN_ID_CHECK_MAP[total % 11] == value[17]


# GB 32100-2015 alphabet: digits plus uppercase letters except I, O, S, V, Z.
USCC_CHARS = "".join(
    c for c in string.digits + string.ascii_uppercase if c not in "IOSVZ"
)
USCC_WEIGHTS = (1, 3, 9, 27, 19, 26, 16, 17, 20, 29, 25, 13, 8, 24, 10, 30, 28)


def _valid_cn_uscc(match: str) -> bool:
    total = sum(USCC_CHARS.index(c) * w for c, w in zip(match[:17], USCC_WEIGHTS))
    return USCC_CHARS[(31 - total % 31) % 31] == match[17]


def _valid_jp_my_number(match: str) -> bool:
    digits = _digits(match)
    total = 0
    for n in range(1, 12):  # n-th digit from the right of the 11 base digits
        p = int(digits[11 - n])
        q = n + 1 if n <= 6 else n - 5
        total += p * q
    remainder = total % 11
    check = 0 if remainder <= 1 else 11 - remainder
    return int(digits[11]) == check


def _valid_jp_phone(match: str) -> bool:
    return 10 <= len(re.sub(r"\D", "", match.replace("+81", "0", 1))) <= 11


class Detector(NamedTuple):
    entity_type: str
    pattern: re.Pattern
    validator: Optional[Callable[[str], bool]]
    score: float


# Score semantics: 0.95 checksum-validated, 0.85 anchored or strongly
# structured, 0.6-0.7 shape-only regex. Heuristic confidence, not a model
# probability.
DETECTORS = {
    "generic": [
        # Guards use explicit ASCII classes instead of \w/\b: Python's \w
        # matches CJK characters, which would wrongly suppress matches
        # embedded in Chinese/Japanese prose.
        Detector(
            "EMAIL_ADDRESS",
            re.compile(
                r"(?<![0-9a-z_.%+-])[a-z0-9][a-z0-9._%+-]{0,63}@"
                r"(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,63}"
                r"(?![0-9a-z-])",
                re.IGNORECASE,
            ),
            None,
            0.85,
        ),
        Detector(
            # Obfuscated form. The "at" must itself be obfuscated (spaced
            # or bracketed) so ordinary prose like "reach me at jane.doe"
            # cannot match; the "dot" may then be spelled out or literal.
            "EMAIL_ADDRESS",
            re.compile(
                r"(?<![0-9a-z_.%+-])[a-z0-9][a-z0-9._%+-]{0,63}"
                r"(?: at |\s?\[at\]\s?|\s?\(at\)\s?)"
                r"(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?"
                r"(?:\.| dot |\s?\[dot\]\s?|\s?\(dot\)\s?))+[a-z]{2,63}"
                r"(?![0-9a-z-])",
                re.IGNORECASE,
            ),
            None,
            0.65,
        ),
        Detector(
            "URL",
            re.compile(
                r"(?:https?://|www\.)[\w.-]+\.[a-z]{2,63}(?::\d{2,5})?"
                r"(?:/[\w\-./%?#&=~+@!$'()*,;:\[\]]*)?",
                re.IGNORECASE,
            ),
            None,
            0.6,
        ),
        Detector(
            "CREDENTIAL_PAIR",
            re.compile(
                r"(?:username|login|user)\s*[:=]?\s*(?P<username>[\w.@+-]{2,64})"
                r"\s+(?:password|passwd|pwd|pass)\s*[:=]?\s*(?P<password>\S+)",
                re.IGNORECASE,
            ),
            None,
            0.85,
        ),
        Detector(
            "CREDIT_CARD",
            re.compile(
                r"(?<![0-9A-Za-z_.+-])\d(?:[ -]?\d){12,18}(?![0-9A-Za-z_-])"
            ),
            _valid_card,
            0.95,
        ),
        Detector(
            "IP_ADDRESS",
            re.compile(r"(?<![\d.])(?:\d{1,3}\.){3}\d{1,3}(?![\d.])"),
            _valid_ipv4,
            0.6,
        ),
        Detector(
            "IP_ADDRESS",
            re.compile(
                r"(?<![0-9A-Za-z_:.-])(?=[0-9a-f]{0,4}:)[0-9a-f:]{2,45}"
                r"(?![0-9A-Za-z_:])",
                re.IGNORECASE,
            ),
            _valid_ipv6,
            0.6,
        ),
        Detector(
            "PHONE_NUMBER",
            # The extra digit-adjacency guards stop backtracking from
            # carving a "phone" out of a longer digit run (e.g. the first
            # 12 digits of a 16-digit card number).
            re.compile(
                r"(?<![0-9A-Za-z_.+-])(?<!\d )\+?\d(?:[ ()-]{0,2}\d){6,14}"
                r"(?![0-9A-Za-z_-])(?![ -]?\d)"
            ),
            _valid_phone,
            0.65,
        ),
        Detector(
            # US-style dotted phone (212.555.0187). Kept separate: dots as
            # general separators would collide with decimals and versions,
            # but the exact 3.3.4 shape is unambiguous.
            "PHONE_NUMBER",
            re.compile(r"(?<![\d.])\d{3}\.\d{3}\.\d{4}(?![\d.])"),
            None,
            0.65,
        ),
    ],
    "us": [
        Detector(
            "US_SSN",
            re.compile(r"(?<![\d.-])\d{3}([-. ])\d{2}\1\d{4}(?![\d-])"),
            _valid_ssn,
            0.7,
        ),
    ],
    "gb": [
        Detector(
            "GB_NINO",
            re.compile(
                r"(?<![A-Z0-9])(?!BG|GB|NK|KN|TN|NT|ZZ)"
                r"[A-CEGHJ-PR-TW-Z][A-CEGHJ-NPR-TW-Z](?: ?\d){6} ?[A-D]"
                r"(?![A-Z0-9])"
            ),
            None,
            0.85,
        ),
        Detector(
            "GB_POSTCODE",
            re.compile(
                r"(?<![A-Z0-9])(?:GIR ?0AA|"
                r"[A-PR-UWYZ][A-HK-Y]?\d[A-Z0-9]? ?\d[ABD-HJLNP-UW-Z]{2})"
                r"(?![A-Z0-9])"
            ),
            None,
            0.6,
        ),
        Detector(
            "GB_DRIVERS_LICENCE",
            re.compile(
                r"(?<![A-Z0-9])[A-Z9]{5}\d(?:[05][1-9]|[16][0-2])"
                r"(?:[0-2]\d|3[01])\d[A-Z9]{2}\d[A-Z]{2}(?![A-Z0-9])"
            ),
            None,
            0.85,
        ),
    ],
    "cn": [
        Detector(
            "CN_RESIDENT_ID",
            re.compile(
                r"(?<![0-9Xx])[1-9]\d{5}(?:18|19|20)\d{2}"
                r"(?:0[1-9]|1[0-2])(?:0[1-9]|[12]\d|3[01])\d{3}[0-9Xx](?![0-9Xx])"
            ),
            _valid_cn_resident_id,
            0.95,
        ),
        Detector(
            "CN_MOBILE",
            re.compile(
                r"(?<![0-9A-Za-z_.+-])(?:\+?86[ -]?)?1[3-9]\d{9}"
                r"(?![0-9A-Za-z_-])"
            ),
            None,
            0.7,
        ),
        Detector(
            "CN_USCC",
            re.compile(
                r"(?<![0-9A-Z])[0-9A-HJ-NPQRTUWXY]{2}\d{6}"
                r"[0-9A-HJ-NPQRTUWXY]{10}(?![0-9A-Z])"
            ),
            _valid_cn_uscc,
            0.95,
        ),
    ],
    "jp": [
        Detector(
            "JP_MY_NUMBER",
            # Digit-adjacency guards: 12 digits carved out of a longer
            # spaced digit run (a card number) must not match.
            re.compile(
                r"(?<![\d-])(?<!\d )\d{4}([ -]?)\d{4}\1\d{4}(?![\d-])(?! \d)"
            ),
            _valid_jp_my_number,
            0.9,
        ),
        Detector(
            "JP_PHONE",
            re.compile(
                r"(?<![\d-])(?:\+81[ -]?\d{1,4}[ -]\d{1,4}[ -]\d{3,4}"
                r"|0\d{1,4}[ -]\d{1,4}[ -]\d{4}"
                r"|0[789]0\d{8})(?!\d)"
            ),
            _valid_jp_phone,
            0.7,
        ),
        Detector(
            "JP_POSTAL_CODE",
            re.compile(r"〒\s*\d{3}-?\d{4}(?!\d)"),
            None,
            0.9,
        ),
    ],
}


class Span(NamedTuple):
    beg: int
    end: int
    entity_type: str
    score: float


def _detect(text: str, locales: list) -> "tuple[list, int]":
    """Return raw spans plus the count of dropped known test values."""
    spans = []
    dropped = 0
    for locale in locales:
        for detector in DETECTORS[locale]:
            for match in detector.pattern.finditer(text):
                value = match.group(0)
                if detector.validator and not detector.validator(value):
                    continue
                normalized = _digits(value).upper()
                if normalized in KNOWN_TEST_VALUES:
                    dropped += 1
                    continue
                spans.append(
                    Span(match.start(), match.end(), detector.entity_type, detector.score)
                )
    return spans, dropped


def _merge(spans: list) -> list:
    """Merge overlapping spans, joining entity types with '+'."""
    merged = []
    for span in sorted(spans, key=lambda s: (s.beg, -s.end)):
        if merged and span.beg < merged[-1].end:
            last = merged[-1]
            types = last.entity_type.split("+")
            if span.entity_type not in types:
                types.append(span.entity_type)
            merged[-1] = Span(
                last.beg,
                max(last.end, span.end),
                "+".join(types),
                max(last.score, span.score),
            )
        else:
            merged.append(span)
    return merged


def _excerpt(text: str, beg: int, end: int) -> str:
    left = max(0, beg - CONTEXT_CHARS)
    right = min(len(text), end + CONTEXT_CHARS)
    prefix = "..." if left > 0 else ""
    suffix = "..." if right < len(text) else ""
    return (
        f"{prefix}{text[left:beg]}[{text[beg:end]}]{text[end:right]}{suffix}"
        .replace("\n", "\\n")
    )


def scan_text(text: str, source: str, locales: list, threshold: float) -> "tuple[list, int]":
    spans, dropped = _detect(text, locales)
    findings = [
        {
            "entity_type": span.entity_type,
            "start": span.beg,
            "end": span.end,
            "score": span.score,
            "excerpt": _excerpt(text, span.beg, span.end),
            "source": source,
        }
        for span in _merge(spans)
        if span.score >= threshold
    ]
    return findings, dropped


# --- self-test -------------------------------------------------------------


def run_self_test() -> int:
    """Smoke test: prove the full pipeline runs in this environment.

    Detector correctness is covered by design-time tests maintained with
    the skill's development; this only verifies the script executes.
    """
    sample = (
        "Reach jane.doe@example.com or +1 (212) 555-0187, "
        "id 110101199003071233, 〒100-0001."
    )
    try:
        findings, _ = scan_text(
            sample, "<self-test>", sorted(DETECTORS), DEFAULT_THRESHOLD
        )
    except Exception as exc:  # any crash means the engine is unusable
        print(f"FAIL: pipeline raised {exc!r}", file=sys.stderr)
        print(json.dumps({"self_test": "fail"}))
        return 1
    ok = any(
        "EMAIL_ADDRESS" in finding["entity_type"].split("+") for finding in findings
    )
    print(
        "PASS: pipeline ran across all locales and detected the sample"
        if ok
        else f"FAIL: expected an EMAIL_ADDRESS finding, got {findings}",
        file=sys.stderr,
    )
    print(json.dumps({"self_test": "pass" if ok else "fail"}))
    return 0 if ok else 1


# --- CLI --------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Stdlib-only PII scanner (fallback engine). Locales and entities: "
            "generic (email, URL, credential pair, credit card w/ Luhn, "
            "IPv4/IPv6, phone), us (SSN), gb (NINO, postcode, drivers "
            "licence), cn (resident ID w/ checksum, mobile, USCC w/ "
            "checksum), jp (My Number w/ check digit, phone, 〒-anchored "
            "postal code). No NER: names, addresses, and birth dates are "
            "not detected."
        ),
        epilog=(
            "Examples:\n"
            "  python3 pii_scan_lite.py --file dump.txt --locale cn,generic\n"
            "  python3 pii_scan_lite.py --text 'call 03-1234-5678' --locale jp\n"
            "Exit codes: 0 scan completed, 1 error or self-test failure, "
            "2 invalid arguments."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--file", nargs="+", default=[], help="files to scan")
    parser.add_argument("--text", help="inline text to scan")
    parser.add_argument(
        "--locale",
        action="append",
        help=(
            "comma-separated locales to enable: all, generic, us, gb, cn, jp "
            "(default: all; repeatable)"
        ),
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=DEFAULT_THRESHOLD,
        help=(
            "minimum heuristic score, 0-1 (default: %(default)s; scores are "
            "0.95 checksum-validated, ~0.85 anchored, ~0.6-0.7 shape-only)"
        ),
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

    raw_locales = []
    for chunk in args.locale or ["all"]:
        raw_locales.extend(part.strip().lower() for part in chunk.split(","))
    if "all" in raw_locales:
        locales = sorted(DETECTORS)
    else:
        unknown = sorted(set(raw_locales) - set(DETECTORS))
        if unknown:
            parser.error(
                f"unknown locale(s): {', '.join(unknown)}. "
                f"Choose from: all, {', '.join(sorted(DETECTORS))}"
            )
        locales = sorted(set(raw_locales))

    sources = []
    findings = []
    dropped_total = 0
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
        file_findings, dropped = scan_text(text, path_str, locales, args.threshold)
        findings.extend(file_findings)
        dropped_total += dropped
    if args.text is not None:
        sources.append("<inline-text>")
        text_findings, dropped = scan_text(
            args.text, "<inline-text>", locales, args.threshold
        )
        findings.extend(text_findings)
        dropped_total += dropped

    if dropped_total:
        print(
            f"note: dropped {dropped_total} match(es) of widely published "
            f"test/example values",
            file=sys.stderr,
        )
    print(
        json.dumps(
            {
                "engine": "lite",
                "sources": sources,
                "locales": locales,
                "score_threshold": args.threshold,
                "finding_count": len(findings),
                "findings": findings,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 1 if had_error else 0


if __name__ == "__main__":
    sys.exit(main())
