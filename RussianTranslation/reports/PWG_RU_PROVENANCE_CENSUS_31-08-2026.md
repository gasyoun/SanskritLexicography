# PWG→RU provenance census — measured, asserted, absent

_Created: 31-08-2026 · Last updated: 31-08-2026_

Wave unit **W3** of the [CLAUDE hardening wave](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/PLAN_SanskritLexicography_CLAUDE_HARDENING_WAVE_2026H2.md),
the measurement half of [#1804](https://github.com/gasyoun/SanskritLexicography/issues/1804)
([H3750](https://github.com/gasyoun/Uprava/blob/main/handoffs/H3750-Opus_SanskritLexicography_pwg-provenance-census_30.08.26.md),
Opus 5 `claude-opus-5`). No store write of any kind: the classifier reads, counts and prints.

Reproduce every number below with
[`RussianTranslation/src/provenance_census.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/provenance_census.py):

```sh
python provenance_census.py --reconstruct --corroborate            # this report
python provenance_census.py --reconstruct --corroborate --json     # the evidence file beside it
```

Machine copy of this run: [PWG_RU_PROVENANCE_CENSUS_31-08-2026.json](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/reports/PWG_RU_PROVENANCE_CENSUS_31-08-2026.json).

## The three classes

A row's `provenance.pipeline` block either carries the three content hashes that
[`pipeline_version.stamp()`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pipeline_version.py)
computes from the actual component bytes at generation time, or it carries version
*strings* with nothing behind them.

| class | meaning | rows | share |
|---|---|---:|---:|
| **measured** | `prompt_sha` + `glossary_sha` + `script_sha` present — the row is tied to the bytes that produced it | 737 | 6.40 % |
| **asserted** | `backfilled: true` plus `*_version` strings only — a provenance stated, never measured | 10,773 | 93.52 % |
| **absent** | no `generated_at`, no `input_raw_sha256`, no `input_portrait_sha256` — no input identity at all | 9 | 0.08 % |
| | **store total** | **11,519** | 100 % |

**#1804 is confirmed, not revised.** The issue measured 10,792 of 11,603 (93.0 %) at
`af58b3b01836e7e888b066b1cd499c3ee53dc602`; the live store on 31-08-2026 gives 10,782
of 11,519 (93.6 %) once the 9 no-identity rows are counted with the asserted mass. The
ruling-14 halt condition (a census diverging ≥2× from the issue's claimed population)
is **not** met — ratio 1.01 — so the census stands as the wave's premise.

## Eras — a clean cutover, not a gradient

| era (generation month) | measured | asserted | absent |
|---|---:|---:|---:|
| 2026-06 | 0 | 8,556 | 0 |
| 2026-07 | 651 | 2,217 | 0 |
| 2026-08 | 86 | 0 | 0 |
| undated | 0 | 0 | 9 |

The two classes do not interleave. Every asserted row was generated between
**2026-06-29T11:40:48Z** and **2026-07-04T05:43:33Z**; every measured row from
**2026-07-04T20:36:49Z** onward. Stamping began inside one ~15-hour window on 4 July
2026 and never lapsed afterwards. The store therefore has exactly two eras plus a
9-row hole, and the boundary is a timestamp, not a judgement call.

| era | span | rows | what the row can prove about the tooling |
|---|---|---:|---|
| **A — asserted** | 2026-06-29 .. 2026-07-04T05:43Z | 10,773 | nothing: version strings only |
| **B — measured** | 2026-07-04T20:36Z .. 2026-08-29 | 737 | the exact prompt/glossary/script bytes |
| **C — absent** | undated | 9 | nothing, and not even the input |

Era C is the `L-6` class of #1804: nine `key1='vid'` rows from
`autosplit_requeue.topup` (store lines 10774–10782) with `generated_at`,
`input_raw_sha256` and `input_portrait_sha256` all null. Every other row in the store
has all three.

## The measured era's own stamps

Nine distinct stamp classes across 737 rows — the component bytes changed on average
every ~82 rows, twice within a single day (11 July, script `435a…` → `ef6b…`):

| prompt | glossary | script | rows | first | last |
|---|---|---|---:|---|---|
| 1.0.0/`e7059f46842e156d` | 1.0.0/`6d2a4293c7c81ccf` | 1.0.0/`435a596ac5ef77c5` | 331 | 2026-07-04T20:36:49Z | 2026-07-11T14:08:20Z |
| 1.0.0/`e7059f46842e156d` | 1.0.0/`6d2a4293c7c81ccf` | 1.0.0/`ef6b1686d36abdb8` | 122 | 2026-07-11T17:44:58Z | 2026-07-11T18:29:23Z |
| 1.0.0/`a12469490a9d4139` | 1.0.0/`90aeaabd28675878` | 1.1.0/`a4047e086ea0f9ae` | 100 | 2026-07-12T15:04:36Z | 2026-07-14T04:10:54Z |
| 1.0.0/`7d2e1e83f492eece` | 1.0.0/`ca1c632639627174` | 1.0.0/`435a596ac5ef77c5` | 61 | 2026-07-10T17:22:42Z | 2026-07-10T17:22:42Z |
| 1.1.0/`dc0e1e2b65ca9731` | 1.0.0/`6d2a4293c7c81ccf` | 1.1.0/`db1177db36f20d7d` | 44 | 2026-08-27T18:59:07Z | 2026-08-29T08:49:35Z |
| 1.0.0/`eb081209a5ea01a2` | 1.0.0/`ca1c632639627174` | 1.0.0/`7bf00f4f5be69b1e` | 23 | 2026-07-06T06:29:07Z | 2026-07-06T20:56:05Z |
| 1.1.0/`dc0e1e2b65ca9731` | 1.0.0/`6d2a4293c7c81ccf` | 1.1.0/`2e646e35de9931f6` | 22 | 2026-08-25T14:40:34Z | 2026-08-25T14:40:34Z |
| 1.1.0/`31656e0197b6c806` | 1.0.0/`bb4626344404b1c1` | 1.1.0/`db1177db36f20d7d` | 20 | 2026-08-28T15:21:25Z | 2026-08-28T15:21:25Z |
| 1.0.0/`cd082096fa24de73` | 1.0.0/`602841ea2c644659` | 1.0.0/`f3eeaccfbbc0868e` | 14 | 2026-07-09T18:56:38Z | 2026-07-09T18:58:36Z |

All 11,519 rows carry `prompt_version: "1.0.0"`-style strings and a single
`model_version: claude-sonnet-5`; the version strings alone cannot separate any of
these nine classes from each other, which is exactly why the hashes exist.

## Can the asserted era be reconstructed from git? Measured answer: no

The obvious backfill is "recompute each component's content hash from the repository
as it stood when the row was generated." That method is **testable**, because era B
carries the truth it would have to reproduce. `--reconstruct` recomputes
`component_sha` over the manifest's file sets at all 99 commits that touched a
component between 2026-06-01 and 2026-09-01, and compares:

| test | question | result |
|---|---|---|
| **loose** | does the recorded hash occur at *any* commit in the window? | **1 of 9** stamp classes match on all three components (5 of 9 on at least one) |
| **strict** | does it match the newest component commit at or before the row's `generated_at` — what a dated backfill would actually use? | **1 of 9** |

The one class that reproduces is the 20-row 2026-08-28 stamp. In rows: **20 of 737
measured rows (2.7 %) have a git-reproducible provenance**; 717 do not. The loose
test is deliberately generous — it accepts a hash from any commit in a three-month
window, including commits made *after* the row — and it still fails eight classes out
of nine, so no stricter dating scheme can rescue the method.

The cause is visible in the data: the prompt set hashes to `dc0e1e2b65ca9731` for 66
rows across 25–29 August, and that value exists at no commit at all. The pipeline was
routinely run against an **uncommitted working tree**. Git records what was
committed; the store records what was executed; for this pipeline those are usually
different objects.

Two further limits, both stated rather than assumed:

1. The local clone is **shallow** (grafted; earliest commit now 2026-06-12 after a
   `--shallow-since=2026-06-01` deepen). Upstream history reaches further back, and a
   deeper fetch would add candidate commits — but the failures above are not
   *missing* commits, they are hashes that no commit produces.
2. `pipeline_versions.json` records only the **current** frozen SHA per component
   (prompt `9983b21651493256`, glossary `ca1c632639627174`, script `144e83f802c72828`
   as of this run). It is a drift guard, not a history, and it keeps no past values.

## What the asserted era *does* have: input identity, corroborated

The tooling half is lost. The input half is not, and it is independently checkable —
each row names the workflow sidecar (`provenance.wf_file`) that recorded the input
hashes for its batch, and the pre-cutover sidecars survive in
[`RussianTranslation/archive/legacy_runtime_2026-07-04/`](https://github.com/gasyoun/SanskritLexicography/tree/master/RussianTranslation/archive).

| class | rows | named sidecar found | input hash confirmed | conflict |
|---|---:|---:|---:|---:|
| measured | 737 | 471 | 471 | 0 |
| asserted | 10,773 | 10,773 | 10,100 | 673 |
| absent | 9 | 0 | 0 | 0 |

**93.8 % of the asserted era's input identity is confirmed by a second file that the
promotion path did not write.** That is worth stating plainly: these rows do not know
what code translated them, but they do know — twice over — what text was translated.

The 673 conflicts are one defect, not 673. Every one of them belongs to rows
generated on 2026-07-03 whose `wf_file` is the generic **`wf_output.json`** — a
default output name with four physical copies on disk, overwritten by every later run
that did not pass an explicit name. 1,025 rows (673 conflicting, 352 matching by
overlap) point at that non-unique filename, so for those rows the sidecar layer is
not addressable evidence at all: the name resolves to whatever ran last. Every other
`wf_file` in the store (57 distinct names) is conflict-free.

## Conclusions

1. **93.5 % of the store carries an assertion where it claims a measurement**, and the
   claim is uniform (`prompt_version: 1.0.0` on every row, including all 737 that
   carry real hashes). A prompt defect found today cannot be scoped to the rows it
   touched.
2. **The asserted era's tooling identity is unrecoverable from any evidence now in
   hand** — proven, not assumed, by failing the reconstruction against 8 of 9 known
   stamps.
3. **The input identity of that same era survives and is corroborated** for 10,100 of
   10,773 rows.
4. **Nine rows have no identity at all** and can never be re-derived or checked
   against upstream drift.
5. The evidence layer has its own defect: an unnamed `wf_output.json` is not a
   pointer. Any future provenance record must be content-addressed, not name-addressed.

What follows from this is a design, not a backfill:
[SPEC_PWG_RU_PROVENANCE_BACKFILL_31-08-2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/SPEC_PWG_RU_PROVENANCE_BACKFILL_31-08-2026.md).
Executing any of it is explicitly out of scope for W3 and needs its own authorization.

Registered as [FINDINGS §621](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md)
(what is now known) and [GAPS §19](https://github.com/gasyoun/SanskritLexicography/blob/master/GAPS.md)
(what stays unknown).

_Dr. Mārcis Gasūns_
