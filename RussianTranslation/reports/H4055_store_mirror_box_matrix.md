# H4055 — src/mirror/box evidence matrix

_Generated: 2026-09-05T00:12:47Z · executor: glm-5.3-flash (opencode/z-ai (OxAlpha pool)) · zero provider calls · live state read-only_

| surface | box | timestamp | sha256 | rows | producing commit | availability |
|---|---|---|---|---|---|---|
| src store (canonical pwg_ru_translated.jsonl) | MacBook-Air.local | — | `—` | — | — | MISSING on this box |
| mirror working tree (hydrated bytes) | MacBook-Air.local | 2026-09-03T17:32:53Z | `79d72dbcb4b3…` | 11519 | — | present |
| mirror git blob (LFS pointer — never equated with bytes) | MacBook-Air.local @ /Users/mac/Documents/GitHub/pwg-ru-data | 2026-09-03T20:32:07+03:00 | `79d72dbcb4b3…` | — | 2c4f770642bd… | present |
| mirror_refresh_ledger.jsonl (last entry) | MacBook-Air.local | 20260902T202344Z | `79d72dbcb4b3…` | 11519 | 2c4f770642bd… | present |
| src store (canonical) | Windows build box | — | `—` | — | — | UNAVAILABLE — this box cannot observe it; any equality claim would be fabricated |
| mirror working tree | Windows build box | — | `—` | — | — | UNAVAILABLE — this box cannot observe it |

## Lineage (hash-based — row counts alone are never lineage)

- mirror hydrated sha256 `79d72dbcb4b33fc88d9e907dec9ecaa0e56ebfb72495a5115ce951a623f8ca65`
- ledger last `mirror_sha_after` `79d72dbcb4b33fc88d9e907dec9ecaa0e56ebfb72495a5115ce951a623f8ca65`
- LFS pointer oid `79d72dbcb4b33fc88d9e907dec9ecaa0e56ebfb72495a5115ce951a623f8ca65` (pointer ≠ bytes; oid recorded beside the sha)
- all three agree: **yes**
- origin: {"ref": "origin/main", "head": "2c4f770642bd1c9f766d6bb63de5636ca855fdbf", "availability": "fetch ok"}

## Cross-box equality

NOT ASSERTED — each unobserved box stays unavailable; row counts (11,462 quarantine-era / 11,519 current-ledger) are historical sizes, never lineage
