# Nominal lexical-core translation queue (H179)

_Created: 05-07-2026 · Last updated: 05-07-2026_

The PWG→RU translation queue is ordered by **lexical priority**, not dictionary
letter order ([H179](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H179-Opus_RussianTranslation_pwg_ru_nominal_core_queue_reorder_05.07.26.md)).
The nominal tiers come from V.V. Leonchenko's DCS corpus lexical-core appendices,
which live in the sibling [VisualDCS](https://github.com/gasyoun/VisualDCS/tree/main/derived-data/Lexical-Cores)
repo as legacy Excel files. This directory holds the extracted, deduped SLP1
wordlists + PWG-coverage reports that feed the nominal drain.

## Files

| Tier | Core | SLP1 list | Coverage | Runnable nominals |
|---|---|---|---|---:|
| 2 (LEADS) | Приложение 10 — all-periods stable ultra-core | [`pril10.slp1.txt`](pril10.slp1.txt) | [`pril10.coverage.md`](pril10.coverage.md) | 286 |
| 3 | Приложение 5 — periodized cores | [`pril5.slp1.txt`](pril5.slp1.txt) | [`pril5.coverage.md`](pril5.coverage.md) | 4,292 |
| 4 | Сборное ядро — Consolidated Core | [`sbornoe.slp1.txt`](sbornoe.slp1.txt) | [`sbornoe.coverage.md`](sbornoe.coverage.md) | 4,798 |

Each core also has a `<core>.tsv` (`slp1`, `iast`, `pos`, `period_spread`) with full provenance.

## ⚠️ Count reconciliation — "Приложение 5 = 3,493" is the longest column, not the queue

H179 (following MG's sketch) labels Приложение 5 as **3,493 words**. On disk that is the
length of the single **longest** period column; the sheet is 7 periods × 2 cols,
blank-padded to that longest column. H179 Step 2.1 explicitly asks to **dedup across the 7
period columns** — that union is **6,337 lemmas** (2,247 appear in only one period; 474 in
all seven). After setting aside 1,298 verbs (POS=`v`, which belong to the standing verb
drain [H151](https://github.com/gasyoun/Uprava/blob/main/handoffs/H151-Sonnet_RussianTranslation_pwg_ru_verb_batch_drain_04.07.26.md),
not this nominal queue) and cumulative dedup, the runnable nominal queue is **4,292**, not
3,493. The "3,493" figure is not wrong — it's just the wrong axis to size the queue by. A
human should decide whether tier 3 means the full 7-period union (what Step 2 instructs,
used here) or only the single longest-period column.

## Regenerate

```sh
# 1. extract SLP1 wordlists from the VisualDCS xls (IAST -> SLP1 via build_src)
python src/pilot/extract_lexical_cores.py

# 2. build the coverage + ordered worklist for a tier
python src/pilot/nominals_worklist.py src/pilot/lexical_cores/pril10.slp1.txt \
    --report src/pilot/lexical_cores/pril10.coverage.md --top 30
```

`nominals_worklist.py` orders hits by DCS composite score (`scale_manifest.freq.json`)
desc, Leonchenko period-spread as tiebreak, and applies cumulative dedup against the live
store's `key1` set (never re-translate a lower tier's word). The ordered
`runnable_remaining` list is fed to the harness in nominal mode:

```sh
python src/_pilot_gen_merged.py <keys>                       # generate flat-nominal inputs
python src/pilot/gen_opt_harness2.py pril10 --nominal --keys=<ordered,list> --gen-model-version claude-sonnet-5
```

_Dr. Mārcis Gasūns_
