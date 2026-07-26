# ACC×NCC P0 — measured row counts

_Created: 06-07-2026 · Last updated: 26-07-2026_

Produced by [`parse_acc.py`](parse_acc.py) / [`parse_ncc.py`](parse_ncc.py) against the
sources named in [`ROADMAP_ACC_NCC.md`](../../ROADMAP_ACC_NCC.md) §1. Re-run either script
to regenerate `acc.jsonl` / `ncc.jsonl` from the current source snapshot.

| | ACC | NCC |
|---|---:|---:|
| Rows parsed | 49,833 | 152,526 |
| Distinct `match_key` | 32,287 | 124,523 |
| Malformed/unparsed lines | 0 | 0 |

**Exact-key join** (`match_key` intersection): **22,775** shared keys.

## The 26-07-2026 NCC `match_key` repair (H1671 / issue #779)

The NCC figures above changed on 26-07-2026, and not because the source moved. Until then
`parse_ncc.match_key_for` transliterated the **capitalised** NCC headword, and
`sanskrit_util.to_slp1` is case-preserving with no uppercase IAST keys — so the initial
capital fell through unchanged into the SLP1 string, where `slp1_simplify` read it as a
*different phoneme* (`K`=kh, `R`=ṇ, `Y`=ñ, `E`=ai, `B`=bh; non-ASCII capitals like `Ś` were
not transliterated at all). `Rāmāyaṇa` keyed as `namayana`, `Yogasūtra` as `nogasutra`.

**91,548 of 152,526 keys (60.0%) were wrong.** Case-folding before transliteration:

| | before | after |
|---|---:|---:|
| Distinct NCC `match_key` | 124,801 | 124,523 |
| Keys containing non-ASCII | 20,571 | 643 |
| **Exact-key join with ACC** | **8,397** | **22,775** |

The join gains 14,379 keys and loses 1 — and the lost one was a collision the corruption
itself manufactured (NCC `Rāmamuktāvali` keyed as `namamuktavali`, colliding with ACC's
genuinely different `Nāmamuktāvalī`). Row-level consequences downstream:
[`NCC_KEY_REPAIR_MIGRATION_2026.md`](NCC_KEY_REPAIR_MIGRATION_2026.md).

The 643 residual non-ASCII keys are a **different and much smaller defect**, not introduced
by this bug and not fixed by it: they carry typographic characters through from the NCC
headword itself — the ordinal indicator `º` used as a repeat-the-headword mark
(`ajitabrahman,ºbrahmacari`, 331 keys), curly quotes (`‘aksobhyatathagatadhyayapujakalpa’`,
~251), and a residue of ellipses, double quotes, a soft hyphen and en-dashes. No ACC key can
ever match one. They are reported here as measured rather than silently stripped, because
stripping them is a headword-normalization decision (is `ajitabrahman,ºbrahmacari` one work
or two?) that belongs to P0's parsing rules, not to a key-derivation patch.

## Note on the roadmap's 03-07-2026 figures vs these measurements

`ROADMAP_ACC_NCC.md` §1 states 152,378 NCC entries / 124,651 distinct NCC keys / 8,413
shared exact keys, measured 03-07-2026 — the latter two on the *pre-repair* key derivation,
so only the row count is comparable to the table above. This run measures 152,526 rows
against the same source file — a difference of 148 rows, which is inside the range of a
normal snapshot drift (the roadmap's own text flags NCC as still subject to re-verification:
*"MG will re-verify the local NCC file is not merely stale before the build is frozen"*).
Reported here as measured, not adjusted to match the earlier figure — no attempt was made to
force agreement with the interview-time count.

ACC's counts (49,833 rows / 32,287 distinct keys) match the roadmap's figures exactly, and
are untouched by the repair: `parse_acc.py` reads Cologne SLP1 directly and never fed a
capitalised string to `to_slp1`.
