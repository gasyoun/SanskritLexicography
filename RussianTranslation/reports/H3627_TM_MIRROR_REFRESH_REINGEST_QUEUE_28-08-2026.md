# H3627 — TM mirror refreshed, the 61 re-ingest lemmas queued; the windows still need a live-gate GO

_Created: 28-08-2026 · Last updated: 28-08-2026_

Discharges the two debts [H2996](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/reports/H2996_WRONG_ENTRY_QUARANTINE_REINGEST_28-08-2026.md)
left open, and reports the third as blocked. Executed by Opus 5 (`claude-opus-5`).

| debt | state |
|---|---|
| 1. `pwg-ru-data` TM mirror still held the 159 quarantined rows (and, from H3593, 6 stale `dā` rows) | **done** — `only_mirror` 167 → 0 |
| 2. the 61 lemmas were in no production queue | **done** — 61/61 runnable, shared worklist untouched |
| 3. run the re-ingest windows | **blocked** — `probe_log.py gate` is NO-GO; needs a fresh paid warm-up a human must authorize |

## 1. The mirror

The mirror is a straight copy of the canonical store — that is the contract
[`restore_store_rows_from_mirror.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/restore_store_rows_from_mirror.py)
ends on (`shutil.copy2(src, mirror)`). H2996 removed 159 rows from the store and repaired
the `durg_a~~h0_zz_sch` `key1` in place, so the mirror was left serving rows the store no
longer has. A window run with `--tm=auto` would have re-served exactly the cards H2996 had
just quarantined.

New tool: [`src/refresh_tm_mirror.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/refresh_tm_mirror.py)
(selftest 17/17). It refuses to copy blind. Before the write, every mirror-only row must be
explained, and all 167 were:

| bucket | rows | what it is |
|---|---:|---|
| quarantined | 159 | matched by row id against [`reports/pwg_ru_wrong_entry_quarantine.jsonl`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/reports/pwg_ru_wrong_entry_quarantine.jsonl) |
| id churn | 2 | the `durg_a~~h0_zz_sch` old-key rows — the same `ru` survives verbatim under `key1: durgA` |
| superseded | 6 | `dā` rows adjudicated one by one, below |
| **unexplained** | **0** | — |

Three guards, any one of which stops the copy: **G1 human-touched** (a mirror-only row with
a `reviewer` or a non-machine `review_status` is a human verdict), **G2 content-loss** (a
mirror-only row whose `ru` appears nowhere in the store), **G3 shrink** (a store more than
`--max-drop` rows smaller than the mirror is a truncation, not a repair).

### G2 fired, and it was right to

The six `dā` rows are **not** byte-identical id churn — their `ru` is genuinely absent from
the store, so G2 blocked the copy. Reading them settled it: in every case the store carries
a **newer and better** translation of the same sense, and the mirror carries the older pass.

The record corroborates this independently. Changelog `1.144.102` (27-08-2026) is the
**H3593 `dA` requeue**, which retranslated `d_a~~h0_02_sec_2` and `d_a~~h0_05_anu`
`--no-tm` to repair two H3590 head-line-loss rows, took `audit_store_gates.py` hard-flagged
rows 5 → 3, and closes with: *"The `pwg-ru-data/tm/` mirror is now stale by these rows and
still needs its own refresh."* These six rows **are** that stale remainder. So the mirror
was owed a refresh on two counts — H2996's quarantine and H3593's requeue — and this pass
discharges both.

| mirror row | superseded by | what changed |
|---|---|---|
| `d_a~~h0_02_sec_2` `1` | same subcard, `1` | mirror `ru` drops the whole `<div n="p">— <ab>desid.</ab> {#di/tsati#} <ls>P. 7,4,54.</ls> … <ab>Sch.</ab>` preamble (LS-LOSS / MARKUP-LOSS class); the store row preserves it *and* translates the German prose |
| `d_a~~h0_05_anu` `1` | `header` + `1` | the mirror row fuses subcard header and sense 1 into one unwrapped row; the store splits them, both `<div>`-preserving |
| `d_a~~h0_05_anu` `2`, `3`, `4` | same tags | same senses and citations; mirror `ru` has no `<div n="1">` wrapper, the store's does |
| `d_a~~h0_05_anu` `comp.` | `etym` | same `Vgl. anAnuda, anudeyI` cross-reference, retagged, wrapper preserved |

Rather than waive the guard with `--force`, the verdict was recorded per row in
[`reports/H3627_tm_mirror_superseded_ack.jsonl`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/reports/H3627_tm_mirror_superseded_ack.jsonl)
and fed back through the new `--ack-superseded` flag. G2 still blocks on anything not named
in that file, so the guard stays live for the next refresh instead of being spent on this one.

### Result

| gate | before | after |
|---|---|---|
| `audit_store_gates.py` `only_src` | 9 | **0** |
| `audit_store_gates.py` `only_mirror` | 167 | **0** |
| `audit_store_gates.py` `changed_ru` | 0 | 0 |
| mirror rows | 11 620 | 11 462 |
| mirror sha256 | `9b910ee3a03b…` | `19fcf5258e5e…` |

The post-refresh mirror sha is byte-identical to the store sha H2996 recorded after its
write (`19fcf5258e5ea384baa6aa0883e5495edd83d1ec0cb9f0cbf70bfd912b69bb9c`), which is the
proof that mirror and store now agree exactly.

Landed as [pwg-ru-data `5346cba`](https://github.com/gasyoun/pwg-ru-data/commit/5346cba)
with a ledger row in `tm/mirror_refresh_ledger.jsonl`; `tm/*.bak` is now gitignored there
(the tracked mirror's own git history is the real backup).

**Unchanged and unrelated:** the store still carries 3 SAN-LOSS rows (`mA`, `pat`,
`asvatantra`), identical before and after, so `audit_store_gates.py` still exits 1. That is
a pre-existing store defect, not mirror drift.

## 2. The 61 lemmas

Built with [`src/pilot/nominals_worklist.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/nominals_worklist.py):

```
61 lemmas | verbs->H151: 0 | nominals: 61 (hits 61 / miss 0, 100.0% cov) | promoted: 0 | RUNNABLE: 61
```

This independently reproduces H2996's coverage claim: all 61 resolve to PWG `<k1>` headwords,
and none is already in the store, so the cumulative dedup will not drop them.

### Why the shared worklist was not overwritten

H2996 flagged that the adapter overwrites the shared
`src/pilot/output/nominal_batch_worklist.json`, whose on-disk copy (691 899 bytes,
14-07-2026) belongs to another lane. That caution was correct and understated. Two facts:

1. **Four consumers read that exact path** — [`progress_dashboard/build_progress_data.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/progress_dashboard/build_progress_data.py),
   [`progress_dashboard/kitchen_slices.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/progress_dashboard/kitchen_slices.py),
   [`progress_dashboard/kitchen_nominal_selftest.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/progress_dashboard/kitchen_nominal_selftest.py)
   and [`src/pilot/h963_c4_pilot_candidates.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h963_c4_pilot_candidates.py).
   Clobbering it would silently redefine the public progress kitchen's nominal counts as a
   61-row re-ingest list.
2. **It is not actually regenerable.** The script's own docstring called it "gitignored,
   regenerable", but the [H963 C4 call graph](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h963/H963_C4_PIPELINE_CALL_GRAPH_2026-07-16.md)
   row D7 already established that rebuilding it needs four external inputs (the gitignored
   store, `scale_manifest.freq.json`, out-of-repo `csl-orig/v02`, out-of-repo `VisualDCS`) —
   **in a clean worktree it is not regenerable at all.**
   [`CONCURRENCY_REAUDIT_2026-07-09.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/CONCURRENCY_REAUDIT_2026-07-09.md)
   still grades the same file "NOT-A-RISK — regenerable". The two disagree; D7 is the one
   with the receipts.

So the adapter gained `--out` (default unchanged, so the standing nominal drain is
untouched) and the H3627 run wrote to
`src/pilot/output/H3627_reingest_worklist.json`. The shared file was verified byte-unchanged
after the run (691 899 bytes, mtime 14-07-2026).

It also gained `--manifest`, because `scale_manifest.freq.json` is gitignored and therefore
absent from a linked worktree — without it the builder cannot be run under this repo's own
worktree-isolation rule at all.

`src/pilot/output/` is gitignored, so `H3627_reingest_worklist.json` is **not committed**.
By §592's own logic that path is only safe if the rebuild is written down, so here it is —
both absolute paths point at the main checkout, which is where the gitignored inputs live:

```
python src/pilot/nominals_worklist.py \
    pwg_ru/H2996_WRONG_ENTRY_REINGEST_ROOTS_2026-08-28.txt \
    --manifest <main-checkout>/RussianTranslation/src/pilot/output/scale_manifest.freq.json \
    --out src/pilot/output/H3627_reingest_worklist.json
```

It must print `hits 61 / miss 0, 100.0% cov | promoted: 0 | RUNNABLE: 61`. Anything else
means the store moved underneath the queue — re-read before running windows.

## 3. The windows — blocked on a paid warm-up

```
$ python src/pilot/probe_log.py gate
NO-GO: last warm-up 2026-07-25T03:27:46Z — representative schema payload did not validate
```

The gate reads the append-only probe log; it is not a live check. The blocking reading is
**over a month old** (25-07-2026). Flipping it to GO means recording a fresh warm-up under
`production_v3` (latency ceiling 80 000 ms, API ceiling 45 000 ms, connection errors 0,
payload at or above the representative floor, `schema_valid` true) — and a warm-up is a real
model call, so it is spend.

Per the standing pwg_ru credit position, an agent does not open that spend on its own. **A
human should decide** whether to authorize the warm-up; nothing else blocks the run.

Once the gate reads GO, the run is:

```
python src/pilot/probe_log.py prompt                       # emits the load-representative probe
python src/pilot/probe_log.py append --kind warmup --verdict GO \
    --latency-ms <measured> --conn-errors 0 --payload-bytes <measured> --schema-valid
python src/pilot/probe_log.py gate                         # must print GO
# then the windows, over src/pilot/output/H3627_reingest_worklist.json
```

**Every window in this batch must pass `--no-tm`.** The mirror is now clean, so `--tm=auto`
would no longer re-serve the quarantined cards — but these are defect requeues, and the
standing rule for a defect requeue is `--no-tm` regardless of mirror state: the point is to
re-fetch the *right* PWG article, not to reuse any memory of the wrong one.

## Not done, and why

- **The windows themselves** — blocked above. Until they run, the store has 159 fewer wrong
  rows but not yet the 61 right articles, and the wave-4 ([FINDINGS §559](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md))
  MW/AP verdicts for these ~60 lemmas stay invalid.
- **The 3 SAN-LOSS store rows** — pre-existing, out of this handoff's scope, untouched.
- **`durgA`** — still has no PWG record to re-ingest from (H2996's finding), so it is
  correctly absent from the 61.

_Dr. Mārcis Gasūns_
