# Bundling TypeScript scripts (Deno, with Bun differences)

Mechanics for TypeScript scripts in a skill's `scripts/` directory. The
universal script rules in SKILL.md apply on top of everything here. Deno is
the default runtime; if only Bun is installed, apply the
[Bun differences](#bun-differences) at the end.

## Imports

Deno resolves dependencies directly from import specifiers — no install step,
no `package.json`:

```typescript
import * as cheerio from "npm:cheerio@1.0.0";
import { z } from "npm:zod@3.22.0";
import { assertEquals } from "jsr:@std/assert@0.226.0";
```

| Prefix | Registry |
|---|---|
| `npm:` | npm |
| `jsr:` | JSR (Deno-native packages) |

Pin exact versions. An unpinned import (`npm:cheerio`) resolves to latest at
runtime — a predictability bug in the skill's own tooling.

## Shebang and invocation

```typescript
#!/usr/bin/env -S deno run --allow-read
```

The `-S` flag splits the remainder into multiple arguments, so permission
flags can live in the shebang. Invocation (use `--` to separate Deno flags
from script flags):

```bash
deno run --allow-read scripts/lint.ts -- --fix .
```

## Permissions

Deno is deny-by-default: every external access needs an explicit flag.

| Flag | Grants |
|---|---|
| `--allow-read[=path]` | filesystem reads (optionally scoped) |
| `--allow-write[=path]` | filesystem writes |
| `--allow-net[=host]` | network (optionally scoped to hostname) |
| `--allow-env[=var]` | environment variables |
| `--allow-run[=cmd]` | subprocess execution |

Prefer scoped flags; never `--allow-all`. Document the required flags in
`--help` so the agent can construct the command.

## TypeScript-specific rules

- Read input from `Deno.args` only — `prompt()` and `confirm()` hang in
  non-interactive shells.
- `console.log` is stdout (data, JSON preferred); `console.error` is stderr
  (diagnostics).
- Exit: `Deno.exit(0)` success, `Deno.exit(1)` error, `Deno.exit(2)` bad
  arguments.

## Template

Start every script from this skeleton:

```typescript
#!/usr/bin/env -S deno run
// Add permission flags to the shebang as needed, e.g.:
// #!/usr/bin/env -S deno run --allow-read --allow-net

// Pin exact versions:
// import { z } from "npm:zod@3.22.0";

const args = parseArgs(Deno.args);

if (args.help) {
  console.log(`Usage: deno run --allow-... scripts/[name].ts [options]

Options:
  --help    Show this help message`);
  // Document every flag here, with a usage example.
  Deno.exit(0);
}

// --- implementation ---

// Data to stdout:      console.log(JSON.stringify(result, null, 2));
// Diagnostics:         console.error("note");
// Exit: Deno.exit(0) success, Deno.exit(1) error, Deno.exit(2) bad args.

// --- minimal arg parser ---
function parseArgs(raw: string[]): Record<string, string | boolean> {
  const out: Record<string, string | boolean> = {};
  for (let i = 0; i < raw.length; i++) {
    if (raw[i].startsWith("--")) {
      const key = raw[i].slice(2);
      const next = raw[i + 1];
      if (next && !next.startsWith("--")) {
        out[key] = next;
        i++;
      } else {
        out[key] = true;
      }
    }
  }
  return out;
}
```

## Bun differences

Everything above holds except:

- **Imports**: version-pinned bare specifiers, no prefix —
  `import { z } from "zod@3.22.0";`. Bun auto-installs at runtime, but only
  when **no `node_modules` directory exists** anywhere from the script's
  location up to the filesystem root; a stray `node_modules` silently
  switches to Node resolution. Keep `scripts/` free of `package.json` and
  `node_modules`.
- **Shebang**: `#!/usr/bin/env bun`; run with `bun run scripts/name.ts`.
- **No permission flags** — Bun has no sandbox; omit the permissions section
  from `--help`.
- **APIs**: `process.argv.slice(2)` for arguments, `process.exit(...)` for
  exit codes.
