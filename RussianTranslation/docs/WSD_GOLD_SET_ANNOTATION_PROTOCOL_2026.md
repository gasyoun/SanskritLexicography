# WSD gold-set design and annotation protocol (token-in-context, ceiling C1)

_Created: 25-08-2026 · Last updated: 25-08-2026_

Design of record for the **token-in-context word-sense-disambiguation gold set** that
[ROADMAP_CEILING_2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/research/ROADMAP_CEILING_2026.md)
item **C1** needs, and that
[RESEARCH_CAPABILITY_ROADMAP_2026-07-09.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/RESEARCH_CAPABILITY_ROADMAP_2026-07-09.md)
cards **4** (token-in-context WSD) and **5** (MFS baseline *accuracy*) terminate at.
Produced by [H3172](https://github.com/gasyoun/Uprava/blob/main/handoffs/H3172-Opus_SanskritLexicography_pwgru-shared-gold-wsd-bli_19.08.26.md)
(**Opus 5**, `claude-opus-5`). Ready for **MG pass-1** annotation.

Sibling design of record for the BLI set:
[BLI_GOLD_SET_ANNOTATION_PROTOCOL_2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/BLI_GOLD_SET_ANNOTATION_PROTOCOL_2026.md).
This document deliberately mirrors its structure, and §5 below carries the
**shared annotator-2 freeze record** that both sets — and the A/B/C translation-quality
set — are measured under.

Scope: this document fixes **what counts as a sense**, size, strata, sampling, and the
two-pass annotation protocol, and ships the frame plus the scripts that build and verify
it. It does **not** produce gold labels — those are the annotation passes' output, and a
script inventing them is the rule-based-arm trap that invalidates a dual-annotation design
([/gold-adjudicate](https://github.com/gasyoun/claude-config/blob/main/commands/gold-adjudicate.md)
Phase 0).

## 1. What blocks on this

Three documents name a sense-labelled sample as their prerequisite and none of them owns
building it, so all three stall on the same missing artifact:

| Doc | Item | What it needs the gold for |
|---|---|---|
| [ROADMAP_CEILING_2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/research/ROADMAP_CEILING_2026.md) | C1 in-context WSD | ~200 hand-checkable tokens, P@1 harness |
| [RESEARCH_CAPABILITY_ROADMAP_2026-07-09.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/RESEARCH_CAPABILITY_ROADMAP_2026-07-09.md) | card 4 | WSD accuracy against the card-5 MFS baseline |
| same | card 5 | the *accuracy number* for the MFS emitter shipped in H775 |

The emitter itself already exists —
[`src/mfs_baseline.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/mfs_baseline.py)
says so in its own docstring: *"The score this baseline is measured against needs a frozen,
sense-labelled gold slice, which does not exist yet."* This frame is that slice's
annotation input.

## 2. What counts as a sense — the measurement this design turns on

**A store row is a subcard, not a sense**, and the naive count (distinct `sense_tag` over
all of a lemma's rows in
[`pwg_ru_translated.jsonl`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/mfs_baseline.py))
is wrong in three compounding ways.

**The store spans five dictionary layers.** Measured over 11,603 rows: `pwg` 5,594,
`pw` 5,205, `nws` 432, `sch` 210, `pwkvn` 162 — and **97 of 254 lemmas straddle more than
one**. Counting senses across layers asks an annotator to choose between *dictionaries*
("sense 2 as printed in PWG" vs "as printed in PW"), which is not a semantic judgment at all.

**Many tags are not senses.** Inside the `pwg` layer alone the tag vocabulary mixes real
numbered senses with structural apparatus (`main`, `intro`, `head`, `tail`, `header`,
`note`, `addendum`, `cross-ref`, `Nachtrag`) and derived-stem slots (`caus`, `desid`,
`caus-1`, `*_verb`).

**Tags are not normalized.** `1` and `1)` are stored as distinct tags, inflating 23
lemmas' inventories by pure punctuation.

Correcting all three collapses the picture, and the correction is the reason this design
looks the way it does:

| lemma | rows | all-layer tags | `pwg` tags | **`pwg` numeric senses** |
|---|---:|---:|---:|---:|
| `han` | 597 | 430 | 90 | **11** |
| `gam` | 673 | 410 | 69 | **8** |
| `viś` | 537 | 397 | 96 | **14** |
| `dhā` | 803 | 368 | 65 | **14** |
| store maximum | | 430 | 96 | **16** (`vah`) |

Read naively, PWG inventories look **bimodal** — a nominal mass of 2–12-sense lemmas plus
a tail of 300–430-sense verb roots that no human could pick among. A first cut of this
design accepted that reading and routed the tail to a separate free-gloss tier, because a
"top-K senses" shortlist for a 430-option lemma would have to be built from the only
ordering available (PWG dictionary order) — which is precisely the MFS baseline's own
prediction, so the shortlist would put the baseline's answer in front of the annotator on
every row.

**That tail does not exist.** Under the corrected definition the largest inventory in the
entire store is **16**, every lemma is hand-checkable, and one uniform pick-one frame
covers the whole pool. The shortlist-bias problem is not solved, it is dissolved.

So, for this gold set:

> **A sense is a pure-numeric `sense_tag` within a single dictionary layer (`pwg`), after
> tag normalization.**

Derived-stem slots are excluded deliberately, not by oversight: DCS already annotates each
token's morphology, so "is this the causative?" is *read off the analysis* rather than
judged from context — a different task from sense disambiguation. Sub-senses (`1a`, `1b`)
are excluded to keep the rule crisp. Every exclusion is counted in the frame header rather
than dropped silently.

## 3. Degenerate menus are excluded, not pooled

Two senses whose glosses are textually identical are not a choice. The live store really
does contain them — before the layer filter, the frame drew rows such as:

```
[1] раздувание, вздутие ‖ [PW] раздувание, вздутие          (dhmāna)
[1] двухсотый           ‖ [PW] двухсотый                    (dviśatatama)
```

Two annotators pick between those at random, and the κ that results measures coin-flips,
not agreement. A first cut of the frame carried **4 such rows outright and 16 more with
partially duplicated options** out of 200. The layer + numeric-tag rule removes the whole
class at source; `distinct_glosses()` in
[`probe_wsd_strata.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/eval/probe_wsd_strata.py)
and a dedicated check in
[`check_wsd_frame.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/eval/check_wsd_frame.py)
keep it out if a regenerated frame ever reintroduces it. This is the WSD twin of the BLI
protocol's homograph exclusion (its §3).

## 4. Frame construction, strata and allocation

| Stage | Count | Note |
|---|---:|---|
| store lemmas | 254 | `pwg_ru_translated.jsonl`, 11,603 subcard rows |
| with ≥ 2 numeric `pwg` senses and ≥ 2 distinguishable glosses | **48** | 206 excluded, ledger in the frame header |
| DCS-attested (≥ 20 tokens) | **48** | none of the 48 is absent from DCS |
| candidate token pool | **370,688** | tokens under those lemmas |
| **sampled frame** | **200** | 3 bands × 67/67/66 |

**Axis: PWG inventory size**, the difficulty axis — it sets the chance floor and decides how
much room the MFS baseline has to be right by default. Bands are cut so the three carry
comparable numbers of *lemmas* rather than comparable-looking edges:

| band | senses | lemmas | candidate tokens | frame rows |
|---|---|---:|---:|---:|
| `I2-5` | 2–5 | 18 | 123,918 | 67 |
| `I6-9` | 6–9 | 16 | 174,004 | 67 |
| `I10+` | 10–16 | 14 | 72,766 | 66 |

**Equal allocation per band, not proportional.** The research question is *does
disambiguation get harder as the inventory grows*; a proportional draw would spend the
budget on `I6-9` and leave `I10+` too thin to report.

**Per-lemma cap of 6** (5 actually binds), so no single frequent lemma becomes its band.
**One token per sentence**, so no two rows share a context — rows sharing a context are not
independent judgments, and an annotator who has already read the sentence is primed.

**Corpus context** is the DCS sentence (`text_sandhied`), gated to 5–60 tokens: below that
there is nothing to disambiguate *from*, above it the row is a reading task rather than a
judgment. Each row carries its citation (`chapter.ref` + sentence counter, e.g.
`MBh, 13, 70, 3`).

## 5. Annotation protocol, and the shared annotator-2 freeze record

**Pass 1 — MG (human).** For each row, pick **one** sense tag from `sense_menu` for the
token `form` as used in `sentence`, or `NONE` if no listed sense fits, or `SKIP` with a
reason (the token is a proper name, the sentence is corrupt, the lemma assignment is wrong).
The **`NONE` rate is a reported number, not an annotator error** — it measures how much of
real corpus usage the PWG numbered senses fail to cover, which is itself a C1 finding.

**Pass 2 — model as annotator 2.** A frozen, documented model annotates the same frame
independently, from the same instructions, with no access to pass 1. Standing constraint
(MG, 08-07-2026): human second-annotator recruiting is parked for 2026 — **do not resurface
it**; the honest label for the resulting statistic is **human–model agreement**, never
"inter-annotator agreement".

**Order matters:** pass 2 must not run before pass 1 is frozen, and neither annotator sees
the WSD system's or the MFS baseline's predictions. Annotating with the system's output
visible converts the gold set into a rubber stamp.

**Adjudication.**
[/gold-adjudicate](https://github.com/gasyoun/claude-config/blob/main/commands/gold-adjudicate.md)
computes raw agreement + Cohen's κ, MG rules every disagreement from the PWG record, and the
~10% agreement spot-check runs (two passes agreeing on a wrong label is the failure mode
agreement stats cannot see).

### The annotator-2 freeze record — required for all three gold sets

An undocumented annotator 2 makes every κ downstream unreproducible. Whichever set is being
annotated (WSD here, BLI, or the A/B/C translation-quality slice), pass 2 ships this record
alongside the labels:

| Field | Meaning |
|---|---|
| `model_tier` + `model_version` | e.g. `Sonnet 5` + `claude-sonnet-5` — tier alone is not a freeze |
| `prompt_sha256` | hash of the exact prompt text, with the prompt itself committed |
| `decoding` | temperature, top_p, max_tokens, and whether sampling was seeded |
| `run_date` | ISO date of the pass |
| `frame_sha256` | hash of the frame file annotated, so a re-cut frame cannot be confused with this one |
| `access_assertion` | explicit statement that pass 1 and system predictions were not in context |

**Why this table is here and not only in the BLI document.** All three sets in H3172 share
one annotator-2 discipline, and the existing A/B/C set is the cautionary case:
[`gold/GRADE_GOLD_MEMO.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/gold/GRADE_GOLD_MEMO.md)
reports κ = **−0.0044** over 320 rows, and that number is uninterpretable as agreement
because its "rater 2" was not a frozen model annotator at all but `tm_grade.qe_proxy()`, a
surface-shape heuristic — it scored 317/320 rows `A` because it only reads length and
Cyrillic coverage. The memo is candid that this reproduces
[FINDINGS §70](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md)
("proxy-QE is near-useless for adequacy") rather than impugning the labels, but a κ computed
against a heuristic is not the κ the roadmaps are asking for. **A frozen model pass 2 under
the record above is what makes the three sets comparable.**

## 6. Interaction with the MFS baseline (card 5)

The MFS baseline predicts the **lowest-numbered sense**
([`mfs_baseline.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/mfs_baseline.py),
`sense_sort_key`), so two contracts follow for whoever scores against this gold:

1. **Report per band, not one number.** Accuracy per inventory band plus the `NONE` rate per
   band. A single headline accuracy over 200 rows is **frame-weighted, not corpus-weighted**
   — the bands are equal-sized by design while the real corpus is not — and must not be
   quoted as "WSD accuracy on pwg_ru".
2. **`NONE` rows are excluded from accuracy and reported separately.** A token whose sense
   is genuinely absent from PWG's numbered inventory is a coverage fact, not a
   disambiguation failure; folding it in would make the baseline and any system look wrong
   for the same reason and hide which is which.

Because the frame preserves PWG's printed order, the MFS prediction for every row is
recoverable from `sense_menu` without re-reading the store: it is the first tag listed.

## 7. The frame as shipped

[`src/eval/wsd_frame_c1_200.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/eval/wsd_frame_c1_200.tsv)
— 200 rows,
`row_id · occ_id · sent_id · citation · lemma_key1 · lemma_iast · band · n_senses · form · upos · sentence · sense_menu`,
**no label column by design**. The header carries the seed (20260825), the per-band
allocation, the exclusion ledger and every input path; same inputs + same seed reproduce it
byte-identically.

Reproduce, end to end:

```sh
cd RussianTranslation/src/eval
python probe_wsd_strata.py --store ../pwg_ru_translated.jsonl \
    --db ../../../VisualDCS/src/DCS-data-2026/dcs_full.sqlite --json probe_wsd.json
python sample_wsd_frame.py --store ../pwg_ru_translated.jsonl \
    --db ../../../VisualDCS/src/DCS-data-2026/dcs_full.sqlite \
    --out wsd_frame_c1_200.tsv --total 200 --max-per-lemma 6 --seed 20260825
python check_wsd_frame.py wsd_frame_c1_200.tsv --max-per-lemma 6
```

Every script carries a fixture-based `selftest` subcommand and all three pass.
[`check_wsd_frame.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/eval/check_wsd_frame.py)
is the gate: label-column leakage, duplicate tokens, two rows sharing a sentence, a broken
per-lemma cap, menus that offer fewer than two distinguishable options, and POS dominance
over 80%.

**Note on the corpus asset.** `dcs_full.sqlite` (920 MB, 5,688,416 tokens / 754,726
sentences, from `gasyoun/dcs-conllu`) is local-only and not committed. `token.lemma` is
**not** indexed — only `lemma_id` is — so a per-lemma `WHERE lemma = ?` is a full-table scan
each time; the probe does one `GROUP BY` pass instead and caches the counts.

## 8. Limitations

- **This frame describes VERB-root disambiguation.** UPOS in the shipped frame is
  **VERB 82%**, NOUN 5%, the rest scattered — a direct consequence of what `pwg_ru` covers
  (749 DCS-attested verb roots), since verb roots are what carry ≥ 2 numbered PWG senses.
  The gate warns on this. Any headline number must say "verb roots", not "Sanskrit".
- **48 lemmas is a narrow base.** 200 tokens spread over 48 lemmas at up to 5 rows each
  means per-lemma idiosyncrasy is visible in every band; bands are ordered comparisons, not
  corpus-weighted rates.
- **Derived-stem senses are out of scope** (§2) — measuring those is a morphology-reading
  task, not disambiguation.
- **Sub-senses (`1a`/`1b`) are excluded**, so the frame slightly understates PWG's true
  granularity.
- **One layer only.** The set describes the `pwg` layer; `pw`, `nws`, `sch` and `pwkvn`
  senses are out of frame, and a token whose best sense lives only in those layers will
  correctly draw `NONE`.
- **DCS sandhied text is the context.** The annotator reads the sandhied sentence, not a
  segmented one; for a few rows the target `form` is fused with its neighbour.
- **Agreement is human–model** (§5), never inter-annotator.
- **Labels do not exist yet.** Everything above describes an annotation *input*. Until pass 1
  runs, C1, card 4 and card 5's accuracy stay blocked.

_Dr. Mārcis Gasūns_
