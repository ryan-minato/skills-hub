---
name: sensitivity-check
description: >
  Detects personally identifiable information (PII) and leaked secrets or
  credentials in text or files, then produces a structured scan report. Use
  when checking content for sensitive data before sharing, committing, or
  publishing — including requests like "find secrets in this code", "is
  there any PII here?", "check for leaked passwords or API keys", "run a
  privacy or compliance review", or "make sure nothing sensitive is in this
  file".
compatibility: >
  Scripts need Python 3.9+; the lite fallback engines and the router run
  with plain python3 (stdlib only). The preferred engines additionally need
  uv and Python 3.11+ (Presidio, spaCy, detect-secrets via PEP 723 inline
  dependencies) plus network access on first run to resolve dependencies
  and fetch a spaCy model wheel.
license: Apache-2.0
---

# Sensitivity Check

Scan text or files for PII and secrets, judge false positives, and finish
with a report whose conclusion is an explicit YES/NO. Two engine families
do the scanning: preferred engines (Presidio, detect-secrets — model-based
and battle-tested, need uv) and lite engines (single-file stdlib scripts —
run anywhere python3 exists).

## Step 1 — Clarify Scope

Confirm before scanning:

1. **Target**: inline text, one file, or many files?
2. **Check type**: PII only, secrets only, or both? Default to **both**.
3. **Locales**: note which languages or regions the content involves.
   Personal data from any region is in scope — deep reads judge all of it,
   and the note also selects the `--language`/`--locale` flags below where
   the scan scripts have locale-specific detectors.

## Step 2 — Route Content

Always route first with [`scripts/scan_router.py`](scripts/scan_router.py);
reading a huge file directly can consume the entire context window.

```bash
# Preferred (exact token counts via PEP 723 tiktoken):
uv run scripts/scan_router.py --files FILE [FILE ...]

# Without uv (counts become chars/4 estimates, flagged "estimated": true):
python3 scripts/scan_router.py --files FILE [FILE ...]

# Inline text: add --text "TEXT"; custom limit: --threshold N (default 4000)
```

| Method | Meaning | Action |
|---|---|---|
| `deep` | at or under the threshold | read the content directly (Step 3) |
| `script` | over the threshold | run scan scripts (Step 4) |
| `binary` | not UTF-8 in the first 8 KB | record the path; do not scan |

Carry any `"estimated": true` flags into the report.

## Step 3 — Deep Check (items routed to `deep`)

Read the full content and judge it directly — no scripts needed. Load
[references/pii_reference.md](references/pii_reference.md) when the check
type includes PII, and
[references/secret_reference.md](references/secret_reference.md) when it
includes secrets. For each finding record entity type, location, severity,
and a short excerpt, applying the false-positive criteria from Step 5 as
you read. Deep reading is also what covers personal names, addresses, and
birth dates when the lite engines do the script scanning.

## Step 4 — Script Check (items routed to `script`)

### 4a. Select engines (once per environment)

Run `uv --version`:

- **Succeeds** → use the preferred engines,
  [`scripts/pii_scan.py`](scripts/pii_scan.py) and
  [`scripts/secret_scan.py`](scripts/secret_scan.py).
- **Fails** → use the lite engines via `python3`,
  [`scripts/pii_scan_lite.py`](scripts/pii_scan_lite.py) and
  [`scripts/secret_scan_lite.py`](scripts/secret_scan_lite.py).

Late-failure rule: if `uv run` later fails with a *dependency-class* error
(package resolution, download, import failure — typical when offline),
treat uv as unusable and switch to the lite engine for that scan type. A
*scan-class* error (bad path, analysis exception) is not a reason to
switch.

**Verify once per environment**: run `--self-test` on each script you
selected before its first real scan. The self-test only proves the script
can run in this environment — correctness is established at design time.
If a preferred engine's self-test fails, fall back to its lite engine; if
a lite self-test fails, deep-read the affected items manually. Record any
degradation in the report.

### 4b. PII scan

```bash
# Preferred engine (add --language zh or ja for Chinese/Japanese content):
uv run scripts/pii_scan.py --file FILE [FILE ...] [--language en]

# Fallback engine (locales: generic, us, gb, cn, jp; default all):
python3 scripts/pii_scan_lite.py --file FILE [FILE ...] [--locale all]
```

If the preferred engine reports a missing spaCy model, its error message
prints the exact `--with "<model> @ <wheel-url>"` flag to append to the
`uv run` command — re-run with it (first run needs the network once).

Read [references/lite_engines.md](references/lite_engines.md) when using
the lite engine: it defines the exact entity coverage and the limitations
the report must state.

### 4c. Secrets scan

```bash
uv run scripts/secret_scan.py --file FILE [FILE ...]      # preferred
python3 scripts/secret_scan_lite.py --file FILE [FILE ...] # fallback
```

Both engines report `hashed_secret` (SHA-1) instead of raw values — read
the source at the reported line to see what was actually matched.

### 4d. Review script findings

For every finding, read at least ±10 lines (or ±200 characters) around the
flagged location and apply Step 5 before recording it as confirmed. Apply
extra scrutiny to lite-engine findings and to any keyword/entropy-based
type — shape-only detection has a higher false-positive rate than the
model-based engines.

### 4e. Binary files

List each binary path in the report; do not attempt to extract or scan.

## Step 5 — Evaluate False Positives

Mark a finding as a false positive when context shows it is not genuine
sensitive data. Common patterns — examples for judgment, not a whitelist:

- Reserved example domains (`example.com`, `.example`, `.test`,
  `.invalid`) and provider noreply addresses
  (`*@users.noreply.github.com`)
- Documentation IPs (`192.0.2.x`, `198.51.100.x`, `203.0.113.x`,
  `127.0.0.1`, `0.0.0.0`) and private ranges appearing as explanatory
  values in docs
- Placeholders: `YOUR_API_KEY`, `<your-token>`, `${VAR}`, `changeme`,
  `xxxx`, and CJK placeholder identities (张三, 李四, 山田太郎,
  `000-0000-0000`)
- Suppression annotations on or immediately above the line
  (`# pragma: allowlist secret`, `# gitleaks:allow`, `# nosec`) — treat as
  intentionally allowed and note the annotation in the report
- Conversely: a value that passes its checksum (card Luhn, CN resident ID,
  JP My Number) is a strong true-positive signal; the lite engine already
  auto-drops the widely published test values

A pattern above appearing in genuinely exported user data is still a real
finding — always judge from context.

## Step 6 — Generate Report

Load [assets/report_template.md](assets/report_template.md) and fill every
section, including which engines ran. The Conclusion must end with exactly
one of:

- **"Contains sensitive information: YES"** — confirmed findings remain
- **"Contains sensitive information: NO"** — nothing found, or everything
  was ruled a false positive

## Gotchas

- **Route before scanning or reading** — skipping Step 2 on large files
  consumes the entire context window.
- **Run lite scripts with plain `python3`** — they have no dependencies;
  wrapping them in `uv run` works but defeats their purpose as the no-uv
  fallback.
- **`pii_scan.py` never installs anything itself** — installing would
  mutate the surrounding environment (and uv-managed environments have no
  pip anyway). A missing spaCy model is an error whose message prints the
  exact `--with "<model> @ <wheel-url>"` flag to append to `uv run`; if uv
  itself is unavailable, that is the signal to use the lite engine.
- **Presidio never matches emails on reserved TLDs** (`.example`, `.test`)
  because it validates domains against the public suffix list — judge such
  addresses in deep reads instead of assuming the engine saw them.
- **Lite scores are heuristics**, not model confidences: 0.95
  checksum-validated, ~0.85 anchored, 0.6–0.7 shape-only. The
  `--threshold` flag applies but means less than with Presidio.
- **Lite entity types merge with `+` on overlapping spans**
  (`CN_MOBILE+PHONE_NUMBER`) — test membership, never string equality.
- **JP postal codes are detected only with the `〒` mark**; a bare
  `123-4567` is deliberately ignored as too ambiguous. Cover unanchored
  postal codes in deep reads.
- **Secret engines never print raw values** — findings carry SHA-1 hashes;
  the review in Step 4d is where the actual value gets read.
- **`secret_scan_lite.py` skips suppressed lines** (same annotations as
  Step 5) and reports the skip count on stderr — check it so suppressions
  are noted, not silently lost.
- **The binary probe reads only the first 8 KB** — a file that is UTF-8
  early but binary later is misrouted as text; verify suspicious files
  manually.
- **`--self-test` is an environment smoke test**, not a correctness suite;
  a pass means "this engine runs here", nothing more.

## References

- Load [references/pii_reference.md](references/pii_reference.md) when
  classifying PII findings in Step 3 or Step 6.
- Load [references/secret_reference.md](references/secret_reference.md)
  when classifying secret findings in Step 3 or Step 6.
- Load [references/lite_engines.md](references/lite_engines.md) when a
  lite fallback engine performs the scanning in Step 4.
- Load [assets/report_template.md](assets/report_template.md) when writing
  the final report in Step 6.
