# Sensitivity Scan Report

## Scan Summary

- **Scan Date:** {YYYY-MM-DD}
- **Check Types:** {PII / secrets / both}
- **Items Scanned:** {N files, inline text}
- **Scan Engines:** {deep read only / presidio + detect-secrets / lite fallback / mixed}
- **Binary Files Skipped:** {N}

## Items Scanned

| # | Item | Type | Token Count | Method |
|---|---|---|---|---|
| 1 | {path or <inline-text>} | {text/binary} | {count, mark "(estimated)" when applicable} | {deep/script/binary} |

## Findings

| # | Source | Severity | Type | Location | Excerpt | Status |
|---|---|---|---|---|---|---|
| 1 | {item} | {Critical/High/Medium/Low} | {entity or secret type} | {line or offset} | {short excerpt; mask secret values} | {Confirmed / False Positive} |

For each false positive, add one line below the table:
- Finding {#}: {reason it is not genuine sensitive data}

## Binary Files (Not Analyzed)

- {path} — flag for manual review if its origin is unclear

## Conclusion

{One paragraph: what was scanned, with which engines, what was found, and
what should happen next (rotation, redaction, safe to share). When the lite
engines performed the script scanning, state that personal names, street
addresses, and free-form birth dates were covered only by deep reading.}

**Contains sensitive information: {YES / NO}**
