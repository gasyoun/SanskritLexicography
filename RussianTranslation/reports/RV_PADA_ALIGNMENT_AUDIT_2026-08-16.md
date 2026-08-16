# Ṛgveda citations aligned to Elizarenkova at pāda granularity — audit, 16-08-2026

_Created: 16-08-2026 · Last updated: 16-08-2026_

Deliverable of [H2850](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2850-Opus_SanskritLexicography_rv-citation-pada-alignment-elizarenkova-rvlinks_15.08.26.md)
(Opus 5 — align RV citations to Elizarenkova's published Russian at pāda level instead of
re-translating), which carries point **P8** of MG's crosswalk review
([H2843](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H2843-Opus_Uprava_mg-crosswalk-review-8-point-vote-contour-umbrella_15.08.26.md)).
Run by Opus 5 (`claude-opus-5`).

The instruction, in MG's words: *«You do not need to translate where a good translation is
already available in Russian. You need to align it.»* What follows is the alignment, the
numbers it produced, and — stated first because it is the part most easily overclaimed — what
it still gets wrong.

## What was built

| Piece | Where |
|---|---|
| The pāda-granular join + agreement verdict + build-time refusal | [`RussianTranslation/src/rv_pada_align.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/rv_pada_align.py) |
| Selftest, 49 checks incl. the gate's negative control | [`RussianTranslation/src/rv_pada_align_selftest.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/rv_pada_align_selftest.py) |
| Per-citation results, 2 964 rows | [`RussianTranslation/reports/rv_pada_alignment.jsonl`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/reports/rv_pada_alignment.jsonl) |
| Frozen 50-citation audit sample | [`RussianTranslation/reports/rv_pada_alignment_sample50_2026-08-16.txt`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/reports/rv_pada_alignment_sample50_2026-08-16.txt) |
| CI wiring | [`.github/workflows/ci.yml`](https://github.com/gasyoun/SanskritLexicography/blob/master/.github/workflows/ci.yml), "RussianTranslation gates" job |

Substrate is [rvlinks](https://github.com/sanskrit-lexicon/rvlinks), already cloned as a
sibling: `rvhymns/rv<MM>.<HHH>.html` carries Elizarenkova, Geldner and Griffith for all 1 028
hymns, with the Russian broken one printed line per pāda. Nothing was scraped and no parser was
written for a source the org did not already hold — the prior-art check
([FINDINGS §544](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md))
established that rvlinks is the substrate and that the SamudraManthanam `no_tags` extract
covers only Mandalas I–II.

## The specimen MG raised

```
parigā  (gA · g_a~~h0_30_pari)
PWG gloss   : прийти, достигнуть, настигнуть кого-либо
Citation    : ṚV. 7,84,1.  ->  rv07.084.01
Quoted      : pra vāṃ ghṛtācī bāhvordaghānā pari tmanā viṣurūpā jigāti
Pādas       : cd   (coverage [0.5, 0.357, 0.962, 1.0], quote 0.98, high confidence)
  c) Полная жира (жертвенная ложка,) которую держат в руках,
  d) (Принимая) разные формы, кружит около вас.
Verdict     : diverges — PWG «прийти, достигнуть, настигнуть кого-либо» ↮ pāda(s) cd
```

Reproduce with `python src/rv_pada_align.py card --locus 7,84,1`. Pādas c+d, not the verse;
`jigāti` read by Elizarenkova as circum-motion — «кружит около» — against PWG's arrival sense.
The divergence is recorded, not smoothed over.

## Extent — the handoff's numbers do not reproduce

The handoff states **1 526 RV citations across 62 entries**. Re-measured on the same store
(`RussianTranslation/src/pwg_ru_translated.jsonl`, 11 603 sense rows, 16-08-2026):

| Counting rule | Citations | Entries |
|---|---|---|
| Any `ṚV.`-sigla `<ls>` in the German column | 3 760 | 52 |
| … distinct `(n=, text)` pairs | 3 486 | 52 |
| **Saṃhitā verse references** (hymn-level and Prātiśākhya / Anukramaṇī / Vālakhilya excluded) | **2 964** | **52** |
| … distinct loci | 2 482 | — |

No counting rule tried lands on 1 526 or on 62. The measured pair is what the code operates on
and what this document reports; the handoff's line should be read as an estimate, not a target.

## Results over the whole surface

`python src/rv_pada_align.py report --out reports/rv_pada_alignment.jsonl`

| Measure | Value |
|---|---|
| RV Saṃhitā citations | 2 964 |
| Joined to specific pāda(s) | 1 856 (62.6 %) |
| … of which span more than one pāda | 333 (17.9 %) |
| Quote no Sanskrit — verse-scope only | 775 |
| No published Russian for the locus | 171 |
| Verdicts | 1 221 `diverges` · 520 `agrees` · 1 223 `undecidable` |
| Join confidence | 1 456 high · 281 medium · 119 low · 775 verse-scope · 333 none |

**17.9 % is the number that answers MG's objection directly.** One pāda-scoped citation in five
quotes across a pāda boundary, so a verse-granular join would have shown the wrong Russian lines
for roughly 333 citations before any question of sense arises.

`diverges` being the majority decidable verdict is expected, not alarming: the verdict is a
**lexical-support screen**, and PWG glosses a lemma across its whole range while Elizarenkova
renders one occurrence in context. It ranks the corpus so a human reads the disagreements first.
It is not a defect list and must not be published as one.

## The build-time refusal

Two layers, because the API-level refusal alone is unfalsifiable at scale.

1. `emit_citation_ru()` raises `PublishedTranslationExists` when a caller offers a machine
   translation for a locus that has published Russian. Selftested in both directions: refused
   for RV 7.84.1, allowed for a locus rvlinks has no Russian for.
2. `python src/rv_pada_align.py gate` scans the live store for the invariant that makes the rule
   checkable: **a Ṛgvedic locus with published Russian must carry its quoted Sanskrit through to
   the RU column byte-identically**, rather than having it rendered away as Russian prose. Exit
   3 on any violation.

```
gate: 2964 RV citations checked · 2793 with published Russian · 2018 of those quote Sanskrit
      · 2018 carried the quote through · 0 violations
```

The gate ships with a **negative control** (`test_gate_detects_a_violation`): a two-row fixture
store, one clean and one violating, asserting exit 0 and exit 3 respectively. The first
implementation of this gate called `emit_citation_ru(..., machine_ru=None)`, which cannot raise —
it reported "0 violations" over any input whatsoever, including a store that broke the rule on
every row. A gate with no failing input is a decoration; the control is what makes the 0 above
mean something.

## Pāda-selection accuracy — 50-citation audit

Drawn with `python src/rv_pada_align.py sample --n 50 --seed 20260816` from the 1 856
pāda-scoped joins, frozen at
[`reports/rv_pada_alignment_sample50_2026-08-16.txt`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/reports/rv_pada_alignment_sample50_2026-08-16.txt).
Every row prints the **whole verse** — the pādas that were not chosen, with their Russian — so
the selection can be judged against the alternatives rather than confirmed against itself.

| Outcome | n |
|---|---|
| Correct pāda(s), correct published Russian returned | 47 |
| Wrong | 2 |
| Correctly declined (low confidence → `undecidable`) | 1 |

**47 / 49 asserted joins = 95.9 %** (94 % of the drawn 50).

The two failures, named:

| Row | Locus | What went wrong |
|---|---|---|
| 18 | `rv07.033.10` | Elizarenkova's **printed line order is inverted** against the Sanskrit: her first line renders pāda b, her second renders pāda a. The pāda chosen is right; the Russian returned is the neighbour's. Undetectable from the Russian alone. |
| 33 | `rv08.006.09` | Under-selection. `pra tam indra naśīmahi rayim` runs one word (`rayim`) into pāda b; only pāda a was returned, so «Богатства из коров (и) из коней» is missing. |

**This adjudication was made by the same model that wrote the matcher** (Opus 5,
`claude-opus-5`), against the printed verse. It is a machine self-audit, not an independent
human review; treat 95.9 % as the author's own estimate until a human re-scores the frozen
sample.

## Corrections made during the audit, and what they cost

The first implementation scored 44/50. Four defects were found by adjudicating and fixed:

1. **Fragment matching summed scattered blocks.** `(ā)gamyās` at RV 1.163.13 scored 1.00 against
   pāda a on two-character coincidences while the word it quotes, `gamyā`, sits in pāda c. Now
   the single **longest contiguous** block decides, since a quoted word is contiguous by
   construction.
2. **Fragments below 4 folded characters** (a bare `ā`, `su`) were being placed at medium
   confidence. They locate nothing; they are now declined outright — 42 citations.
3. **Span selection unioned independent per-pāda hits**, which silently dropped the pāda a
   quotation only reaches into (RV 1.141.1, RV 1.116.8). It now picks the minimal contiguous
   run: start from the whole verse, trim an end while the remainder still carries the quotation
   or while the quotation barely touches that end pāda. Multi-pāda joins rose from 14.1 % to
   17.9 % as a result.
4. **Speaker attributions were counted as pāda lines.** Elizarenkova prints «Индра:», «Сарама:»,
   «Р е к и:» on their own line in the dialogue hymns — 163 such lines across the 1 028 hymns —
   and each one shifted every later line off its pāda. RV 3.33.9 and RV 10.108.5 were both
   returning the following pāda's Russian; both are correct now. The filter is deliberately
   narrow (a capitalised stub of at most two words, or letters spaced for emphasis, ending in a
   colon), so a real pāda line ending in a colon — «Царям, достойным жертв:» — is untouched.

## Limitations a consumer must know

- **Pāda boundaries are derived, not given.** rvlinks prints the romanised verse as hemistichs;
  pādas are recovered by splitting each hemistich at word boundaries to balance syllables
  against the number of published Russian lines. A sandhi-fused word straddling the caesura
  (`rathenāriṣṭā` at RV 2.27.16) lands wholly on one side and can carry the join with it. Each
  row reports `regularity` — the largest deviation of any pāda from the mean, in syllables — and
  anything above 3.5 is refused rather than joined.
- **Line order is not guaranteed to be pāda order** (RV 7.33.10 above). This is the residual
  error class and is not mechanically detectable from the Russian.
- **PWG cites the lemma, the verse carries the inflected form.** A citation quoting `yuvan`
  against a verse reading `yuvā` can land on a spurious substring elsewhere in the verse.
- **775 citations quote no Sanskrit at all**, so nothing narrows them below the whole verse.
  That is a property of PWG's citation practice, not of the join, and no method fixes it.
- **`agrees`/`diverges` is a screen, not a semantic ruling.** `verdict_basis` is `screen` (or
  `screen-verse`); a hand-adjudicated row would carry `hand`. None does yet.
- **Coverage of the substrate is near-total, not total:** 124 verses in scope have no Russian in
  rvlinks (some print `-ru-`), and two hymn references point past the end of their hymn
  (`rv08.082` verse 15 of 9; `rv08.049` verse 20 of 10) — PWG numbering the Vālakhilya inline.

## Rights, recorded once

The Russian is Elizarenkova's published translation, **reproduced** in rvlinks, not
org-produced; that repository asserts no redistribution licence and credits only the
compilation. Per the org's standing policy
([rights uncertainty is not a stop](https://github.com/gasyoun/Uprava/blob/main/docs/STANDING_POLICY_RIGHTS_UNCERTAINTY_IS_NOT_A_STOP_2026.md))
the facts are recorded here and work proceeds.

Marginal exposure from this deliverable is nil: the full Elizarenkova Ṛgveda is **already
committed to this same public repository** at
[`RussianTranslation/pwg_ru/rv_stanza_translations.jsonl`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/rv_stanza_translations.jsonl)
(10 552 stanzas, all five translators). The report published here quotes pāda-level lines for
2 964 citations drawn from that same corpus. Note the tension with
[`src/citation_tm.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/citation_tm.py),
whose `rights_flag='metadata-only'` forbids writing a translation of record to a committed
artifact — that rule governs the SamudraManthanam corpus DB, which is *not* committed, and the
RV corpus was committed under a separate earlier decision. A human should decide whether the two
policies are reconciled or whether the committed RV corpus is itself to be revisited; the
alignment work does not depend on the answer.

## How to re-run

```
cd RussianTranslation
python src/rv_pada_align.py --selftest
python src/rv_pada_align.py card --locus 7,84,1
python src/rv_pada_align.py report --out reports/rv_pada_alignment.jsonl
python src/rv_pada_align.py sample --n 50 --seed 20260816 --out reports/rv_pada_alignment_sample50_2026-08-16.txt
python src/rv_pada_align.py gate
```

The store is gitignored and lives only in the main checkout; `default_store()` resolves it
through [`store_path.canonical_store`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/store_path.py),
so the commands work unchanged from inside a linked worktree.

_Dr. Mārcis Gasūns_
