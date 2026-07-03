# Lite Fallback Engines

Read this when scanning with `pii_scan_lite.py` or `secret_scan_lite.py`
(the stdlib-only engines used when uv is unavailable). It defines what the
lite engines can and cannot see, so the report states coverage honestly.

## pii_scan_lite.py coverage

| Locale | Entity type | Validation | Base score |
|---|---|---|---|
| generic | EMAIL_ADDRESS | plain form; obfuscated forms (" at ", "[at]", "(at)" with spelled or literal dots) | 0.85 / 0.65 |
| generic | URL | shape only | 0.6 |
| generic | CREDENTIAL_PAIR | username and password keywords adjacent | 0.85 |
| generic | CREDIT_CARD | brand prefix + Luhn checksum; separators allowed | 0.95 |
| generic | IP_ADDRESS | IPv4/IPv6 parsed with `ipaddress` | 0.6 |
| generic | PHONE_NUMBER | 8–15 digits with `+` or separators (plus the exact US dotted 3.3.4 shape); date/version/SSN shapes rejected | 0.65 |
| us | US_SSN | area/group/serial range check (no 000/666/9xx area) | 0.7 |
| gb | GB_NINO | invalid prefix pairs excluded | 0.85 |
| gb | GB_POSTCODE | uppercase-only structure | 0.6 |
| gb | GB_DRIVERS_LICENCE | month/day ranges encoded in the pattern | 0.85 |
| cn | CN_RESIDENT_ID | ISO 7064 MOD 11-2 check digit | 0.95 |
| cn | CN_MOBILE | `1[3-9]` + 9 digits, optional +86 | 0.7 |
| cn | CN_USCC | GB 32100-2015 mod-31 check character | 0.95 |
| jp | JP_MY_NUMBER | official check-digit algorithm | 0.9 |
| jp | JP_PHONE | separators (or +81) required for landlines | 0.7 |
| jp | JP_POSTAL_CODE | only with the 〒 mark | 0.9 |

Score semantics: 0.95 checksum-validated, ~0.85 anchored or strongly
structured, 0.6–0.7 shape-only. These are heuristics, not model
probabilities; the `--threshold` flag filters on them all the same.

## Known limitations (state these in the report)

- **No NER.** Personal names, street addresses, and free-form birth dates
  are not detected. Cover them with the Presidio engine or by deep-reading
  the flagged items. Conversely, Presidio's English pipeline does not
  detect CN/JP/GB national identifiers — the engines complement each
  other; neither is a superset.
- Bare digit runs without `+` or separators are never reported as phone
  numbers (too ambiguous); CN mobile numbers have their own detector.
- Bare 9-digit SSNs without separators are not detected — only the
  separated 3-2-4 form is.
- JP postal codes require the `〒` mark; a bare `123-4567` is deliberately
  ignored. Mention unanchored postal codes during deep reads instead.
- GB vehicle registration plates are deliberately excluded — the `AB12
  CDE` shape collides with ordinary identifiers.
- Overlapping matches merge into one finding with entity types joined by
  `+` (e.g. `CN_MOBILE+PHONE_NUMBER`). Check whether a type is present in
  the list; do not compare for equality.
- Widely published test values that pass their checksums (4111 1111 1111
  1111, 078-05-1120, 13800138000, ...) are dropped automatically; the
  dropped count goes to stderr.

## secret_scan_lite.py coverage

Prefix detectors: private-key headers, AWS access key IDs (AKIA/ASIA),
GitHub (`ghp_`/`gho_`/... and `github_pat_`), GitLab (`glpat-`), Slack
(`xox?-`), Google (`AIza...`), Stripe (`sk_live_`), Anthropic
(`sk-ant-`), OpenAI (`sk-proj-`), JWTs, bearer tokens (value ≥ 20
chars), and credentialed connection strings.

Keyword + entropy detector: assignments to secret-suggestive names flag
when the value's Shannon entropy reaches 3.0 (hex charset), 4.5 (base64
charset), or 3.5 (mixed). Placeholder values (`YOUR_API_KEY`, `${VAR}`,
`<token>`, `changeme`, repeated characters) and bare URLs are skipped.

Behavioral notes:

- Lines carrying `pragma: allowlist secret`, `gitleaks:allow`,
  `detect-secrets:disable`, or a trailing `# nosec` are skipped entirely
  (count on stderr), matching the preferred engine.
- Expect small result differences versus detect-secrets: detect-secrets
  reports placeholder keywords (e.g. `YOUR_API_KEY` as "Secret Keyword")
  that the lite engine pre-filters, and their type labels differ. Both
  hash values with SHA-1, so identical findings correlate.
