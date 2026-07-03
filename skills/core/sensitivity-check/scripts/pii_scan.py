#!/usr/bin/env -S uv run
# /// script
# dependencies = [
#   "click>=8,<9",
#   "presidio-analyzer>=2.2,<3",
#   "spacy>=3.8,<3.9",
# ]
# requires-python = ">=3.11"
# ///
"""Model-based PII detector built on Microsoft Presidio (preferred engine).

This script assumes it runs under ``uv run``; if uv is unavailable, use
the stdlib fallback ``python3 scripts/pii_scan_lite.py`` instead.

Supported languages map to spaCy models (en -> en_core_web_sm,
zh -> zh_core_web_sm, ja -> ja_core_news_sm). Models arrive as ordinary
dependencies: when one is missing, the error prints the exact
``uv run --with "<model> @ <wheel-url>"`` invocation to use. The script
never installs anything itself — that would mutate the surrounding
environment. click stays a direct dependency because Presidio's import
chain needs it but may not pull it transitively in an isolated uv
environment.

Exit codes: 0 scan completed, 1 dependency/model/self-test failure,
2 invalid arguments.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

CONTEXT_CHARS = 40
DEFAULT_THRESHOLD = 0.5

MODEL_MAP = {
    "en": "en_core_web_sm",
    "zh": "zh_core_web_sm",
    "ja": "ja_core_news_sm",
}

_MODEL_RELEASES = "https://github.com/explosion/spacy-models/releases/download"
MODEL_VERSION = "3.8.0"  # matches the spacy>=3.8,<3.9 pin above


def _model_wheel_url(model: str) -> str:
    return (
        f"{_MODEL_RELEASES}/{model}-{MODEL_VERSION}/"
        f"{model}-{MODEL_VERSION}-py3-none-any.whl"
    )


def _with_requirement(model: str) -> str:
    return f'--with "{model.replace("_", "-")} @ {_model_wheel_url(model)}"'


def _build_analyzer(language: str):
    try:
        import spacy
        from presidio_analyzer import AnalyzerEngine
        from presidio_analyzer.nlp_engine import NlpEngineProvider
    except ImportError as exc:
        print(
            f"error: dependency missing ({exc}). Run this script with "
            f"'uv run' so PEP 723 dependencies resolve, or fall back to "
            f"'python3 scripts/pii_scan_lite.py' (stdlib only).",
            file=sys.stderr,
        )
        raise SystemExit(1) from exc

    model = MODEL_MAP[language]
    if not spacy.util.is_package(model):
        print(
            f"error: spaCy model '{model}' is not installed. Re-run adding "
            f"{_with_requirement(model)} to the uv run command (needs the "
            f"network once; uv caches it afterwards). This script installs "
            f"nothing itself to avoid mutating the environment.",
            file=sys.stderr,
        )
        raise SystemExit(1)

    provider = NlpEngineProvider(
        nlp_configuration={
            "nlp_engine_name": "spacy",
            "models": [{"lang_code": language, "model_name": model}],
        }
    )
    return AnalyzerEngine(
        nlp_engine=provider.create_engine(), supported_languages=[language]
    )


def _excerpt(text: str, beg: int, end: int) -> str:
    left = max(0, beg - CONTEXT_CHARS)
    right = min(len(text), end + CONTEXT_CHARS)
    prefix = "..." if left > 0 else ""
    suffix = "..." if right < len(text) else ""
    return (
        f"{prefix}{text[left:beg]}[{text[beg:end]}]{text[end:right]}{suffix}"
        .replace("\n", "\\n")
    )


def scan_text(analyzer, text: str, source: str, language: str, threshold: float) -> list:
    results = analyzer.analyze(text=text, language=language, score_threshold=threshold)
    return [
        {
            "entity_type": result.entity_type,
            "start": result.start,
            "end": result.end,
            "score": round(result.score, 4),
            "excerpt": _excerpt(text, result.start, result.end),
            "source": source,
        }
        for result in sorted(results, key=lambda r: r.start)
    ]


# --- self-test -------------------------------------------------------------


def run_self_test() -> int:
    """Smoke test: prove the analyzer builds and a scan runs.

    Exits 1 with instructions if dependencies or the spaCy model are
    unavailable; a pass means this engine is usable in this environment.
    """
    analyzer = _build_analyzer("en")
    # Needs a real TLD: Presidio's email recognizer validates the domain
    # against the public suffix list, so a reserved .example TLD never
    # matches; example.com carries the real .com suffix and does.
    text = "Contact Alice Smith at alice.smith@example.com."
    findings = scan_text(analyzer, text, "<self-test>", "en", DEFAULT_THRESHOLD)
    ok = any(finding["entity_type"] == "EMAIL_ADDRESS" for finding in findings)
    print(
        "PASS: analyzer built and detected the sample"
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
            "PII scanner backed by Microsoft Presidio and spaCy (preferred "
            "engine). Detects named entities (persons, locations) as well "
            "as structured PII (emails, phones, cards, IPs)."
        ),
        epilog=(
            "Examples:\n"
            "  uv run pii_scan.py --file export.csv --language en\n"
            '  uv run --with "en-core-web-sm @ <wheel-url>" pii_scan.py ...\n'
            "A missing spaCy model is an error; the message prints the "
            "exact --with flag to add. The script never installs anything "
            "itself.\n"
            "Exit codes: 0 scan completed, 1 dependency/model/self-test "
            "failure, 2 invalid arguments."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--file", nargs="+", default=[], help="files to scan")
    parser.add_argument("--text", help="inline text to scan")
    parser.add_argument(
        "--language",
        default="en",
        choices=sorted(MODEL_MAP),
        help="content language; selects the spaCy model (default: %(default)s)",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=DEFAULT_THRESHOLD,
        help="minimum confidence score, 0-1 (default: %(default)s)",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help=(
            "verify the engine can run in this environment (English model), "
            "then exit; fails with instructions if the model is missing"
        ),
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if not args.file and args.text is None:
        parser.error("provide --file and/or --text (or --self-test)")

    analyzer = _build_analyzer(args.language)

    sources = []
    findings = []
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
        findings.extend(
            scan_text(analyzer, text, path_str, args.language, args.threshold)
        )
    if args.text is not None:
        sources.append("<inline-text>")
        findings.extend(
            scan_text(
                analyzer, args.text, "<inline-text>", args.language, args.threshold
            )
        )

    print(
        json.dumps(
            {
                "engine": "presidio",
                "sources": sources,
                "language": args.language,
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
