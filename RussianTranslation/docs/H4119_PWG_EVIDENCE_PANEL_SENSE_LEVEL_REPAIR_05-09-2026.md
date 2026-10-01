# H4119 — PWG evidence panel: per-sense evidence, corpus sense lane, non-circular TM

_Created: 05-09-2026 · Last updated: 05-09-2026_

Repair of the three P0/P1 defects the H4058 review ranked. Model: Opus 4.8 (claude-opus-4-8).
Every number below is a measured read of the canonical store — the probe is read-only, made
no provider call, and promoted nothing.

Receipt: [`RussianTranslation/reports/H4119_evidence_probe.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/reports/H4119_evidence_probe.json) ·
probe: [`RussianTranslation/tools/h4119_evidence_probe.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/tools/h4119_evidence_probe.py)

```
python RussianTranslation/tools/h4119_evidence_probe.py --json RussianTranslation/reports/H4119_evidence_probe.json
```

## P0 — the lemma roll-up was rendered as sense support

[`annotate_evidence.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/annotate_evidence.py)
writes two fields and they are not interchangeable: `row['evidence']` is the SENSE's own
evidence array, while `row['evidence_summary']` is a LEMMA roll-up attached identically to
every row sharing a `key1` (D1 ruling 08-07-2026 — the flat store has no lemma object).
Consumers read `evidence_summary.supports_senses` and displayed it as this sense's support,
which credits a sense with a *sibling* sense's evidence.

| Measure (11,519 store rows, 221 distinct `key1`) | Count |
|---|---|
| rows with their own per-sense `evidence` | 2,218 (19.26 %) |
| rows with a non-empty lemma roll-up | 10,802 (93.78 %) |
| **rows credited by the roll-up alone** | **8,584** |
| roll-up / per-sense inflation | ×4.87 |

**Repaired in** [`build_h4056_evidence_packet.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_h4056_evidence_packet.py):

1. `screen()` now gates eligibility on `row['evidence']`. The roll-up keeps only its two
   genuinely lemma-level roles (`evidence_status`, `contradicts`); the rows it would have
   admitted are counted in a new funnel bucket `rollup_only_no_sense_evidence` rather than
   silently passing.
2. `verdict_panel()` renders the per-sense array under «Свидетельства ЭТОГО значения»
   (source, relation and the matched gloss snippet), and the roll-up under an explicitly
   lemma-scoped label — «Сводка по ЛЕММЕ (не по значению; общая для всех значений этого
   key1)». A sense with no evidence of its own now says so.

Pinned by four new checks in `build_h4056_evidence_packet.py --selftest`.

## P1 — the corpus is now a sense-support lane, not a presence bit

`corpus` was a NONRU presence-only lane: `corpus_gate.corpus_examples_with_status` answers
"does an aligned verse mentioning this lemma exist?", so a 1.09M-row resource supported
**0 senses**. But [`corpus_lexicon.jsonl`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_corpus_lexicon.py)
is SLP1-keyed Sanskrit→Russian word alignment — a Russian-glossing authority in exactly the
shape the other RU lanes take.

New module [`corpus_lexicon_lane.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/corpus_lexicon_lane.py)
makes it token-comparable, with two deliberate asymmetries: it can never reach `provides`
(a verse rendering is one translator's choice, not a lexicographic equivalent statement) and
it never emits `contradicts` (a differing verse rendering says nothing against a printed
sense).

| Measure | Value |
|---|---|
| lexicon rows read / usable Russian renderings | 1,093,391 / 1,093,391 (`translation` 992,265 · `commentary` 101,126) |
| store `key1` covered by the lane | 166 / 221 (75.11 %) |
| senses supported **before** | 0 (presence-only lane, by construction) |
| matched / missed / ambiguous / no_lane | 575 / 9,038 / 1,793 / 113 — denominator 11,519 rows |
| matched share of *judgeable* rows | 5.98 % |
| **rows NEWLY supported** (had no per-sense evidence at all) | **205** |

`ambiguous` is a first-class class, not a miss: those 1,793 rows are senses that assert no
comparable Russian meaning (bare cross-ref / citation senses), so the lane cannot judge them.

The lane is wired into `annotate_evidence.annotate_rows` behind `CORPUS_LEX_LANE`, **off by
default**: switching it on rewrites `evidence` on ~575 live rows, which is a store promotion
decision, not a code default. This handoff was read-only over the canonical store.

## P2 — TM evidence made non-circular

A TM built FROM the store and queried WITH that store's own addresses hits 100 % by
construction. That self-hit is excluded from the verdict here.

| Measure | Value |
|---|---|
| address unit | entry-level `ru:<provenance.input_raw_sha256>` — one address per sub-card |
| distinct addresses / addressable rows | 2,445 over 11,510 (mean 4.71 rows per address) |
| rows that cannot be content-addressed (defer) | 9 |
| circular self-hit rate | 100 % — **excluded** |
| hold-out replay: 60 addresses withheld (318 rows removed), TM rebuilt without them | hit 0 · miss 59 · defer 1 → **0.00 % hit rate** |

The reading: within this store there is **no cross-card reuse at all** — every sub-card's
masked source is unique, so a hold-out card has nothing to resolve against. The TM's real
value is therefore re-run idempotence (the same source arriving again costs no provider
call), not deduplication across distinct cards. Any panel claiming "TM demonstrates reuse"
on a self-hit is claiming something this measurement does not support.

## Selftests

```
python RussianTranslation/src/corpus_lexicon_lane.py --selftest
python RussianTranslation/tools/h4119_evidence_probe.py --selftest
python RussianTranslation/src/annotate_evidence.py --selftest
python RussianTranslation/src/build_h4056_evidence_packet.py --selftest
```

All four pass on this branch. The probe selftest runs on committed fixtures only and needs
no store; the two fixtures are
[`corpus_lexicon.fixture.jsonl`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/fixtures/corpus_lexicon.fixture.jsonl)
and the new `corpus_lexicon_kinds.fixture.jsonl` (pins that a non-Russian `kind` is censused
but contributes no gloss).

_Dr. Mārcis Gasūns_
