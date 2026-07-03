# Bundling Python scripts (uv)

Mechanics for Python scripts in a skill's `scripts/` directory. The universal
script rules in SKILL.md apply on top of everything here.

## Inline dependencies (PEP 723)

Declare dependencies in the script itself, before imports, so the script is
self-contained — no `requirements.txt`, no pre-installed environment:

```python
# /// script
# dependencies = [
#   "httpx>=0.27,<1",
#   "beautifulsoup4>=4.12",
# ]
# requires-python = ">=3.11"
# ///
```

Pin every dependency: `>=X.Y,<X+1` for libraries, exact `==X.Y.Z` for tools.
An unpinned dependency resolves differently over time — a predictability bug
in the skill's own tooling.

## Shebang and invocation

```python
#!/usr/bin/env -S uv run
```

```bash
uv run scripts/extract.py --flag VALUE
```

`uv run` creates an isolated environment, installs the declared dependencies,
and runs the script; later runs reuse the cached environment.

## Python-specific rules

- Use `argparse`: it generates `--help` from `add_argument` calls and exits 2
  on bad arguments automatically. Put a usage example in `epilog`.
- Never call `input()` — it hangs in a non-interactive shell.
- Error messages state what is wrong, why, and what to do:

  ```python
  # Bad
  raise ValueError("invalid input")

  # Good
  parser.error(f"--format must be one of: json, csv, table. Got: {args.format!r}")
  ```

## Template

Start every script from this skeleton:

```python
#!/usr/bin/env -S uv run
# /// script
# dependencies = [
#   # "package>=X.Y,<X+1",
# ]
# requires-python = ">=3.11"
# ///

import argparse
import json
import sys


def main() -> None:
    parser = argparse.ArgumentParser(
        description="[One-line description.]",
        epilog="Example: uv run scripts/[name].py --flag VALUE",
    )
    # parser.add_argument("--flag", required=True, help="[description]")
    args = parser.parse_args()

    # --- implementation ---

    # Data to stdout (JSON preferred):
    # print(json.dumps(result, indent=2))
    # Diagnostics to stderr:
    # print("note", file=sys.stderr)
    # Exit: sys.exit(0) success, sys.exit(1) error, sys.exit(2) bad args.


if __name__ == "__main__":
    main()
```
