# H2679 — W1 TM-mine unmined SamudraManthanam delta

_Created: 14-08-2026 · Last updated: 14-08-2026_

Handoff: [H2679 (Grok 4.6) — W1 TM-mine unmined SamudraManthanam delta](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2679-Grok_SanskritLexicography_deepseek-w1-tm-mine-delta_13.08.26.md).
Method: [RUNNING_TEXT_MINING.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/RUNNING_TEXT_MINING.md)
(H186/H224). Miner: [`mine_running_text.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/mine_running_text.py).
Model: DeepSeek `deepseek-v4-flash` (Grok 4.6 `grok-4.6` orchestration).

## Fence

- Writes only `src/corpus_lexicon.mined.jsonl` (`tier: mined`).
- Never writes the clean 1.09M [`corpus_lexicon.jsonl`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_corpus_lexicon.py).
- Clean lexicon sha256 **before** (and after, same bytes):
  `9f3d852f1f1424c275af2cc1823dab1b561e649320e597d3cab013068ccc4072`
  (290 543 363 bytes, read-only from the main-tree copy).

## `--plan` (14-08-2026)

SamudraManthanam `web/corpus_builder/jsonl/` now has **269** `*.jsonl` (H224 saw 148).
Aligned works still **116** (frozen list matches live corpus). New selection rules
on top of H224:

1. Skip `*.raw` companions (byte-level / near-duplicates of the processed jsonl).
2. Skip the eight H224-scale works as already-mined (local `mined.jsonl` is
   gitignored and was absent). `--include` can force a remine. `kommentarii-k-makhabkharate`
   stays `MINE_LAST` if forced.

**28 sources selected, 8 823 term-bearing, 8 823 pending (`done_refs`-missing).**
H224 eight + 26 raw companions + 116 aligned + 18 denylist + 1 index + low-yield
= the SKIP set. `kommentarii` is **not** remine-queued (already-mined skip).

### MINE (delta, cheap-first)

| Source | Term-bearing | pending | done_refs |
|---|---:|---:|---:|
| `devibhagavata-purana-4` | 15 | 15 | 0 |
| `devibhagavata-purana-6` | 16 | 16 | 0 |
| `devibhagavata-purana-10` | 18 | 18 | 0 |
| `kama-samuha-literatura` | 18 | 18 | 0 |
| `shaktisangama-tantra` | 22 | 22 | 0 |
| `devibhagavata-purana-11` | 24 | 24 | 0 |
| `mahabhagavata-purana` | 24 | 24 | 0 |
| `mahabharata-mausalaparva-ignatiev` | 26 | 26 | 0 |
| `devibhagavata-purana-12` | 31 | 31 | 0 |
| `devibhagavata-purana-5` | 34 | 34 | 0 |
| `yogini-tantra` | 36 | 36 | 0 |
| `devibhagavata-purana-3` | 38 | 38 | 0 |
| `devibhagavata-purana-1` | 43 | 43 | 0 |
| `devibhagavata-purana-7` | 66 | 66 | 0 |
| `yajnavalkyasmriti_add` | 67 | 67 | 0 |
| `chinachara-tantra` | 86 | 86 | 0 |
| `kama-samuha` | 86 | 86 | 0 |
| `maya-tantra` | 104 | 104 | 0 |
| `nirvana-tantra` | 129 | 129 | 0 |
| `yoni-tantra` | 135 | 135 | 0 |
| `niruttara-tantra` | 231 | 231 | 0 |
| `devibhagavata-purana` | 298 | 298 | 0 |
| `guptasadhana-tantra` | 352 | 352 | 0 |
| `naradasmriti` | 874 | 874 | 0 |
| `yajnavalkyasmriti` | 1003 | 1003 | 0 |
| `brihannila-tantra` | 1058 | 1058 | 0 |
| `kularnava-tantra` | 1206 | 1206 | 0 |
| `vishnu-smriti` | 2783 | 2783 | 0 |
| **Total** | **8823** | **8823** | **0** |

### SKIP (reason counts)

| Reason | N |
|---|---:|
| verse-aligned (Track A domain) | 116 |
| low-yield: term-bearing below min-tb 15 | 72 |
| raw companion (duplicate of processed jsonl) | 26 |
| dictionary/glossary/non-Sanskrit (denylist) | 18 |
| already mined (H224 scale) | 8 |
| index file (skip-by-name) | 1 |
| **SKIP total** | **241** |

Full `--plan` stdout (no API calls) is the 273-line capture from
`python mine_running_text.py mineall --plan` on 14-08-2026. Headline lines:

```text
  SKIP  biruni                                               already mined (H224 scale; local mined.jsonl often absent — delta only)
  SKIP  kommentarii-k-makhabkharate                          already mined (H224 scale; local mined.jsonl often absent — delta only)
  SKIP  kularnava-tantra.raw                                 raw companion (duplicate of processed jsonl)
  SKIP  ukazateli-makhabkharaty                              index file (skip-by-name)
  === 28 sources selected, 8823 term-bearing, 8823 pending (done_refs-missing) ===
(--plan: no API calls made)
```

## Spend / JSONL

Every HTTP attempt is appended to gitignored
`src/mine_running_text.calls.jsonl` (model, served_model, tokens, UTC,
price_card, USD, finish_reason, error, work, passage). Key from
`ORS-FAQ/.env` `DEEPSEEK_API_KEY` copied into the worktree `.env` (never
committed).

## Precision gate (H224 method)

Target: correct-equivalence ≥95% on **new** sources. Same three verdicts as
[H224 scale sample](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/running_text_mining_precision_sample_scale.jsonl):
meaning-gloss / low-info ident / hard error.

### Mid-run gate (small sources, before the large smritis/tantras)

After the first seven new sources (~306 pairs), a deterministic 30-row
stratified sample (`sample-new --n 30`) was adjudicated against the source
passage. Sample:
[running_text_mining_precision_sample_h2679_small.jsonl](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/running_text_mining_precision_sample_h2679_small.jsonl).

| Verdict | Count | Rate |
|---|---:|---:|
| Correct meaning-gloss (`rājasūya`→рождение царя, `so 'ham`→Он есть я, `liṅga`→знак) | 25 | 83% |
| Correct but low-information (river / book-title / name: `sarayū`→совр. Гхагра, `Raghuvaṃśa`→Род Рагху, `heramba`→имя Ганеши) | 5 | 17% |
| Hard error | 0 | 0% |

**Correct-equivalence = 30/30 (100%); meaning-gloss = 25/30 (83%); hard-error = 0%.**
Clears ≥95%. Large remaining sources (`naradasmriti` … `vishnu-smriti`) therefore
proceed.

### Official close-out gate (22 new sources, 14-08-2026)

Deterministic stratified 30-row sample across **all** new-source rows present
when the gate ran (`sample-new --n 30`, 22 works). Each gloss checked as a
substring of its source passage (30/30 `IN`) and adjudicated against that
passage. Sample:
[running_text_mining_precision_sample_h2679.jsonl](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/running_text_mining_precision_sample_h2679.jsonl).

| Verdict | Count | Rate |
|---|---:|---:|
| Correct meaning-gloss (`pādya`→вода для омовения стоп, `ekārṇava`→единственный океан, `mukti`→освобождение) | 24 | 80% |
| Correct but low-information (person / varṇa loan / clan / title: `śaunaka`→мудрец, `śūdra`→шудра, `dānava`→данавы, `Raghuvaṃśa`→Род Рагху, `heramba`→имя Ганеши, `Yama`→бог смерти) | 6 | 20% |
| Hard error | 0 | 0% |

**Correct-equivalence = 30/30 (100%); meaning-gloss = 24/30 (80%); hard-error = 0%.**
Clears ≥95%. Verbatim-in-passage held (zero fabricated glosses in the sample).
Same noise as H224: proper-name / title / loanword transliterations are
low-information, not wrong.

## Mine progress (resume, 14-08-2026)

A previous isolated agent left `mineall --workers 12` running (PID 14668,
started 02:40 local). This resume **did not start a second miner**. Snapshot
after the official sample (still on `devibhagavata-purana`; large smṛti/tantra
tail not finished):

| Metric | Value |
|---|---|
| New-source mined pairs | ~2 700 (`tier: mined` only) |
| Distinct `(slp1, ru)` | ~1 800 |
| DeepSeek calls (JSONL) | ~1 610, all `deepseek-v4-flash` |
| Logged USD (pre-1608 Flash card) | ~$1.46 |
| API errors logged | ~192 (timeout / premature close / SSL) — retries, then remine |
| Clean lexicon sha256 after | `9f3d852f1f1424c275af2cc1823dab1b561e649320e597d3cab013068ccc4072` (unchanged) |
| Worktree `corpus_lexicon.jsonl` | absent (never written) |

### Still pending (cheap-first tail)

`guptasadhana-tantra` (352), `naradasmriti` (874), `yajnavalkyasmriti` (1003),
`brihannila-tantra` (1058), `kularnava-tantra` (1206), `vishnu-smriti` (2783),
plus mop-up of 0-pair leftovers on already-started sources. Miner is
resumable via `done_refs` + `corpus_lexicon.mined.done.jsonl` (empty successes).
`kommentarii-k-makhabkharate` stays skipped (H224 already-mined).

_Dr. Mārcis Gasūns_
