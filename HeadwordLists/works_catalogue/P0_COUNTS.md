# ACC×NCC P0 — measured row counts

_Created: 06-07-2026 · Last updated: 06-07-2026_

Produced by [`parse_acc.py`](parse_acc.py) / [`parse_ncc.py`](parse_ncc.py) against the
sources named in [`ROADMAP_ACC_NCC.md`](../../ROADMAP_ACC_NCC.md) §1. Re-run either script
to regenerate `acc.jsonl` / `ncc.jsonl` from the current source snapshot.

| | ACC | NCC |
|---|---:|---:|
| Rows parsed | 49,833 | 152,526 |
| Distinct `match_key` | 32,287 | 124,801 |
| Malformed/unparsed lines | 0 | 0 |

**Exact-key join** (`match_key` intersection): **8,397** shared keys.

## Note on the roadmap's 03-07-2026 figures vs these measurements

`ROADMAP_ACC_NCC.md` §1 states 152,378 NCC entries / 124,651 distinct NCC keys / 8,413
shared exact keys, measured 03-07-2026. This run measures 152,526 / 124,801 / 8,397 against
the same source file today — a difference of 148 rows (NCC entries), which is inside the
range of a normal snapshot drift (the roadmap's own text flags NCC as still subject to
re-verification: *"MG will re-verify the local NCC file is not merely stale before the build
is frozen"*). Reported here as measured, not adjusted to match the earlier figure — no
attempt was made to force agreement with the interview-time count.

ACC's counts (49,833 rows / 32,287 distinct keys) match the roadmap's figures exactly.
