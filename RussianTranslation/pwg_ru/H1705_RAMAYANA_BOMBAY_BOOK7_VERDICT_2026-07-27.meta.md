# Metadoc — H1705 R. (Bomb.) book-7 verdict

_Created: 27-07-2026 · Last updated: 27-07-2026_

Companion record for
[`H1705_RAMAYANA_BOMBAY_BOOK7_VERDICT_2026-07-27.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/H1705_RAMAYANA_BOMBAY_BOOK7_VERDICT_2026-07-27.md).

## Purpose

To be the document a future session reads **instead of re-running the probe**. Its subject
is a negative result — why PWG's `R.` book-7 citations were left as typed misses and why an
authorised OCR budget was deliberately not spent — and negative results decay fastest,
because the reasoning behind a *non*-action leaves no artifact unless someone writes it down.
Everything a re-attempt would otherwise rediscover (the scan-index location, the page→PDF
offset, the layout hazards, the numbering deltas) is in there.

## Audience

1. Whoever picks the lane back up when a Russian Uttarakāṇḍa appears —
   [GAPS §13](https://github.com/gasyoun/SanskritLexicography/blob/master/GAPS.md) is the trigger.
2. Any session about to OCR a Cologne scan-viewer edition — the trap list generalises past
   this book ([FINDINGS §480](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md)).
3. Whoever rules on the corpus kāṇḍa-6/7 provenance question
   ([CONTRADICTIONS §9](https://github.com/gasyoun/SanskritLexicography/blob/master/CONTRADICTIONS.md),
   [integrity #822](https://github.com/gasyoun/SanskritLexicography/issues/822)).

## Provenance

| | |
|---|---|
| Handoff | [H1705](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H1705-Opus_SanskritLexicography_ramayana-bombay-book7-etext_26.07.26.md) |
| Model | Opus 5 1M (`claude-opus-5[1m]`) |
| PRs | [#823](https://github.com/gasyoun/SanskritLexicography/pull/823) (work) · [#824](https://github.com/gasyoun/SanskritLexicography/pull/824) (v1.89.0) · [#825](https://github.com/gasyoun/SanskritLexicography/pull/825) (count correction, v1.89.1) |
| Inputs | [sanskrit-lexicon-scans/ramayanabom](https://github.com/sanskrit-lexicon-scans/ramayanabom) `app1/pywork/indexv{1,2,3}.txt` @ `841764ad` · SamudraManthanam `corpus_builder/jsonl` · csl-orig `v02/pwg/pwg.txt` · [RussianRamayana](https://github.com/gasyoun/RussianRamayana) `data/project-status.json` |
| Re-derivable by | `build_ramayana_concordance.py build-bombay` + `selftest`; `citation_tm.py selftest` |

## Limitations — read these before citing it

- **The OCR was never run**, so nothing here is a claim about how well the Bombay pages
  *would* OCR. The zone-segmentation difficulty is measured (14 whole-page vs 3 mūla-band
  `॥N॥` markers on p. 600; 22 vs 1 on p. 700) but the mūla band is itself under-recalled —
  those numbers bound the problem, they do not size the solution.
- **Only kāṇḍa 7 was studied against the corpus.** The inventory covers all 7 kāṇḍas, but
  the ≈1:1 test was run for book 7 alone. Kāṇḍa 6's index rows carry a known anomaly
  (reaches sarga 130 with 70/122/123 absent) that was **observed and not repaired** — anyone
  keying book-6 work off the inventory must resolve it first.
- **The `n_verses` column is the highest printed verse number**, not a count of verses
  present; the scan comments file records unreadable/missing ślokas that this does not model.
- **The sarga-111 repair is an inference**, however well-supported (page-810 colophon
  `… दशाधिकशततमः सर्गः ॥ ११० ॥` + a mūla restarting at `॥१॥` + a disjoint page span from the
  real sarga 11). It is flagged `index_typo_111` in the TSV precisely so it can be revisited.
- The published counts were **corrected once, same day** (1,781 → 1,765; 39,845 → 39,222) —
  see the correction note in the doc. Cite the corrected figures.

## Improvement backlog (ranked)

1. **Rule the corpus kāṇḍa-6/7 provenance** (#822). Until then, every "Southern vs critical"
   agreement figure that includes those two kāṇḍas is misleading, here and elsewhere.
2. **File the two upstream ramayanabom index defects** — `index.txt` is Śatapatha template
   residue; the last uttarakāṇḍa sarga is typed `11` for `111`. Both are documented here and
   in the builder; neither is reported upstream. Needs a human's go-ahead (outward-facing).
3. **Extend the ≈1:1 study to books 1–6** using the same command. Cheap now that the
   inventory exists, and it would test the Schlegel (books 1–2) assumption `citation_tm`
   currently relies on — that Schlegel ≈ vulgate ≈ the corpus keying — which has one
   human-validated fixture behind it and no census.
4. **Model `R. ed. Bomb.` explicitly.** PWG carries 319 such citations across all books, only
   14 in book 7; the resolver treats plain `R.` book-7 as Bombay but has no branch for the
   explicit form outside it.

## Revision history

| date | what changed | by |
|---|---|---|
| 27-07-2026 | created with the doc (H1705) | Opus 5 1M (`claude-opus-5[1m]`) |
| 27-07-2026 | count correction 1,781 → 1,765 folded into the doc (v1.89.1) | Opus 5 1M (`claude-opus-5[1m]`) |

_Dr. Mārcis Gasūns_
