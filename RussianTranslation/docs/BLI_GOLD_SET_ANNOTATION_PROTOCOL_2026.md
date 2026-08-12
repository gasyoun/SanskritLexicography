# BLI gold-set design and annotation protocol (Sa→Ru, ACL roadmap B1)

_Created: 10-08-2026 · Last updated: 12-08-2026_

Design of record for the **human-annotated, stratified Sa→Ru gold set** that ACL roadmap
[B1](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/research/ROADMAP_ACL_LESSONS_2026.md)
needs to evaluate [`corpus_lexicon.jsonl`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_corpus_lexicon.py)
as bilingual lexicon induction. Produced by [H2401](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2401-Fable_SanskritLexicography_bli-b1-gold-set-design_07.08.26.md)
(**Fable 5**, `claude-fable-5`). Ready for **MG pass-1** annotation.

Scope: this document fixes **size, strata, sampling, and the two-pass annotation
protocol**, and ships the frame + the scripts that build and verify it. It does **not**
produce gold labels — those are the annotation passes' output, and a script inventing them
is the rule-based-arm trap that invalidates a dual-annotation design
([/gold-adjudicate](https://github.com/gasyoun/claude-config/blob/main/commands/gold-adjudicate.md) Phase 0).

## 1. Why a second gold set exists at all

[H1521](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H1521-Sonnet_RussianTranslation_bli-eval-corpus-lexicon-p1-mrr_23.07.26.md)
already shipped a **fully automatic** 400-lemma gold set
([`gold_sa_ru_koch_400.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/eval/gold_sa_ru_koch_400.tsv))
and the first numbers: **P@1 = 0.402 · MRR = 0.539 · coverage = 0.995**
([FINDINGS §467](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md)).
That set is not superseded — it stays as the reproducible automatic baseline. B1 needs a
different instrument for three measured reasons.

**Coverage 0.995 was an artifact of the frame, not a property of the lexicon.** H1521
selected the top-400 lemmas by DCS frequency band, i.e. only the highest band. Presence in
`corpus_lexicon.jsonl` across the full frequency range is nothing like uniform:

| DCS band | presence in `corpus_lexicon.jsonl` |
|---|---|
| 5 (highest) | 0.96–1.00 |
| 4 | 0.77–0.91 |
| 3 | 0.37–0.77 |
| 2 | 0.15–0.46 |
| 1 (lowest) | **0.04–0.32** |

Measured over 12,939 candidates with
[`probe_gold_strata.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/eval/probe_gold_strata.py)
(full per-cell table in §7). A single-band gold set cannot see this and therefore cannot
answer B1's actual question — *where* does the induced lexicon fail.

**The gold labels are token-bags from a dictionary gloss, not translations.** H1521's
`ru_gold_tokens` column is every Russian content word in the Kochergina entry, so `A` (the
letter *a*) carries 26 "gold" tokens including `напр`, `нареч`, `прил`. A match is then
declared on any token overlap. That is a deliberately lenient proxy — appropriate for a
first automatic number, not for a citable gold standard.

**Verb behaviour is invisible in a top-band frame.** Presence collapses fastest for VERB
(band 3: 0.37, band 2: 0.15, band 1: 0.04) — the sharpest signal in the whole probe, and
structurally the most interesting, since verbs are where Sanskrit morphology puts the most
distance between a corpus surface form and a dictionary headword.

## 2. Frame construction (measured, reproducible)

| Stage | Count | Note |
|---|---|---|
| Kochergina standalone entries | 29,006 | bound compound members (`-kAra`) excluded |
| joined to an independent DCS frequency signal | 15,075 | see the key-scheme trap below |
| with ≥ 1 extractable Russian content token | 12,939 | notation filler (`напр`, `знач`) stripped |
| homograph SLP1 keys excluded | 595 keys | see §3 |
| **sampled frame** | **500** | 25 cells × 20 |

**Gold content and gold selection are both independent of the asset under test** — the
constraint H1521 established and this inherits. Content comes from **Kochergina**
(`src/koch.jsonl`, an independently authored dictionary); frequency ranking comes from
**VisualDCS** `dcs_lemma_summary.json` (Hellwig DCS whole-corpus counts). Neither is
derived from `corpus_lexicon.jsonl`, so measured coverage is a real property rather than a
tautology. The corpus's own 3-layer `surface_glossary.jsonl` remains **banned as gold** — it
is a group-by aggregation *of* the file under test and would score it against itself.

> **Key-scheme trap, measured here — costs ~75% of the join if missed.** The two DCS assets
> are keyed in *different schemes*: `dcs_lemma_summary.json` is **SLP1**-keyed (`aSva`) and
> `dcs_freq_dims.json` is **IAST**-keyed (`aśva`). Joining Kochergina's SLP1 headwords
> against the IAST file directly returns **3,534** hits; transcoding first returns
> **14,296** (+10,762). Diagnosis:
> [`probe_key_scheme.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/eval/probe_key_scheme.py).
> The transcode uses the canonical `sanskrit-util.to_slp1`
> ([SHARED_CODE §1](https://github.com/gasyoun/github-spine/blob/main/SHARED_CODE.md)) and
> the loader **hard-fails** rather than falling back to a private SLP1 table.

## 3. Homographs are excluded, not pooled

711 Kochergina SLP1 keys (2.52%) carry more than one entry — `vas` I *shine* vs `vas` II
*wear clothes*; `vas` has six. `corpus_lexicon.jsonl` is keyed by bare surface SLP1 with no
homograph index, so **"the gold Russian gloss for `vas`" is ill-posed**.

Pooling every homograph's glosses into one gold bag would make the match accept *any*
homograph's translation — inflating P@1 by construction, in exactly the direction the whole
design is trying to avoid. So homograph keys are excluded from the frame (595 of the 711
fall inside the glossable candidate pool), the count is written into the frame header, and
the exclusion is reported as a **known limitation**: the resulting metric describes the
lexicon's behaviour on *monosemous-headword* lemmas. Measuring homograph disambiguation is a
sense-level task (roadmap B2 / WSD), not BLI.

## 4. Strata and allocation

**Axes: DCS frequency band (5→1) × dominant POS.** The four POS clearing 20 glossable
candidates in *every* band are NOUN, VERB, ADJ, ADV. The seven rarer POS (PART, PRON, NUM,
INTJ, CONJ, SCONJ, ADP — 23 cells, 108 lemmas total) cannot support a per-cell rate and are
pooled into a single reported `OTHER` cell rather than silently dropped.

**5 bands × 5 POS groups = 25 cells × 20 lemmas = 500.** Equal allocation per cell, not
proportional: the research question is per-stratum behaviour, and a proportional draw would
spend most of the budget on band-2/3 NOUNs while leaving band-5 VERB too thin to report.

**Consequence, stated rather than buried:** cell-level rates are read as *ordered
comparisons across strata*, not as a corpus-weighted aggregate. A single headline P@1 over
these 500 rows would be **frame-weighted, not corpus-weighted**, and must not be quoted as
"the lexicon's P@1" — for that, re-weight per cell by the true stratum population (§7
carries the pool sizes needed to do it).

**Polysemy is observed, not controlled.** The frame's Kochergina sense counts land at
1 sense 52% · 2–3 34% · 4–6 13% · 7+ 2%. The `7+` bucket (8 rows) is below a reportable
threshold — report it pooled with `4–6`, never as its own rate. Polysemy is a third axis B1
would like; at 500 rows it cannot be a *third stratum* without collapsing cells to ~7 rows.
Documented as a limitation, revisitable if the budget grows.

## 5. Annotation protocol

**Pass 1 — MG (human).** Annotate the frame's 500 rows. Per row, the label is the set of
**acceptable Russian translation equivalents** of the Sanskrit headword — canonical lemma
forms, not the free-text definition. Also mark rows that are unannotatable
(`SKIP` + reason: gloss is a cross-reference only, headword is a proper name, gloss is
grammatical apparatus). The Kochergina gloss ships in the frame so no lookup is needed.

**Pass 2 — model as annotator 2.** A **frozen, documented** model annotates the same frame
independently, from the same instructions, with no access to pass 1. Freeze and record:
exact model version, the full prompt, temperature, and the run date. Standing constraint
(MG, 08-07-2026): human second-annotator recruiting is parked for 2026 — **do not resurface
it**; the honest label for the resulting statistic is **human–model agreement**, never
"inter-annotator agreement".

**Adjudication.** [/gold-adjudicate](https://github.com/gasyoun/claude-config/blob/main/commands/gold-adjudicate.md)
computes raw agreement + Cohen's κ, MG rules every disagreement from the Kochergina record,
and the ~10% agreement spot-check runs (two passes agreeing on a wrong label is the failure
mode agreement stats cannot see). Output: the adjudicated gold + `ruling`/`ruling_reason`,
per-pass P/R, and a provenance memo naming tier + exact version for pass 1, pass 2, and the
adjudicator.

**Order matters:** pass 2 must not run before pass 1 is frozen, and neither annotator sees
`corpus_lexicon.jsonl` output. Annotating with the system's predictions visible converts the
gold set into a rubber stamp.

**Vehicle.** 500 homogeneous repeated judgments is squarely sheet territory
([/review-sheet](https://github.com/gasyoun/claude-config/blob/main/commands/review-sheet.md)
Phase 0: ≥5 items, repeated identical judgments) — Russian-language interface, `title_href`
to the entry, one card per lemma, and the screening gate declared. Note the inversion:
here the human label **is** the deliverable, so every row is a class-(d) card by
construction; that must be stated explicitly in `screening=` rather than passed as a
formality. **Shipped 12-08-2026** by [H2551](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H2551-Sonnet_SanskritLexicography_bli-b1-gold-annotation-sheet-500_10.08.26.md)
(**Sonnet 5**) — [`build_bli_gold_b1_500_sheet.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/eval/build_bli_gold_b1_500_sheet.py)
([PR #1660](https://github.com/gasyoun/SanskritLexicography/pull/1660)); label = free-text
note (acceptable Russian equivalents), SKIP = reject path with a reason picker. Awaiting
MG's vote.

## 6. Interaction with the scorer (H2402)

[H2402](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2402-Sonnet_SanskritLexicography_bli-b1-p1-mrr-scorer_07.08.26.md)
(**Sonnet 5**) builds the P@1/P@5/MRR scorer. Two contracts it must honour, both consequences
of §4 and §5:

1. **Report per stratum, not one number.** P@1/P@5/MRR per (band × POS) cell, plus coverage
   per cell. Any aggregate is labelled frame-weighted, or re-weighted by the §7 pool sizes.
2. **Absent lemmas are a separate number.** A lemma missing from the lexicon has no rank;
   it counts against coverage and is excluded from P@k/MRR — never folded in as rank-∞.
   With per-stratum presence from 1.00 down to 0.00 (§7), silently mixing the two would make
   the low bands look like retrieval failures when they are absence.

Cells whose presence is under 25% (band 1 ADV/NOUN/VERB in the current frame) yield
**coverage evidence but no usable P@1** — 20 annotated rows with 0–4 lexicon hits cannot
support a rate. Annotate them anyway (they are the coverage story), and report them
separately rather than pretending to a rate.

## 7. The frame as shipped

[`src/eval/gold_frame_b1_stratified_500.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/eval/gold_frame_b1_stratified_500.tsv)
— 500 rows, `slp1 · band · pos · polysemy · n_senses · koch_gloss`, **no gold column by
design**. Header carries the seed (20260810), per-cell target, homograph-exclusion count and
every input path; same inputs + same seed reproduce it byte-identically.

Per-cell presence in `corpus_lexicon.jsonl`, i.e. the P@1 signal each cell can yield:

| band | ADJ | ADV | NOUN | OTHER | VERB |
|---|---|---|---|---|---|
| 5 | 0.90 | 1.00 | 0.90 | 1.00 | 0.90 |
| 4 | 0.90 | 0.85 | 0.90 | 0.80 | 0.60 |
| 3 | 0.85 | 0.65 | 0.80 | 0.95 | 0.45 |
| 2 | 0.60 | 0.45 | 0.60 | 0.65 | 0.25 |
| 1 | 0.35 | 0.20 | 0.20 | 0.30 | **0.00** |

Frame-wide: **321/500 (64.2%)** present — against H1521's 99.5%, the difference is entirely
the frame. Candidate-pool sizes per cell (for corpus re-weighting) come from
`probe_gold_strata.py --dcs … --dims …`; the largest pools are band-3 NOUN (2,970 glossable)
and band-2 NOUN (1,805), the smallest band-5 PART (27).

Reproduce, end to end:

```sh
cd RussianTranslation/src/eval
python probe_gold_strata.py --koch ../koch.jsonl \
    --dcs ../../../VisualDCS/dcs_lemma_summary.json \
    --dims ../dcs_freq_dims.json --lexicon ../corpus_lexicon.jsonl > probe.json
python summarize_gold_probe.py probe.json
python sample_gold_frame.py --koch ../koch.jsonl \
    --dcs ../../../VisualDCS/dcs_lemma_summary.json --dims ../dcs_freq_dims.json \
    --out gold_frame_b1_stratified_500.tsv --per-cell 20 --seed 20260810
python check_gold_frame.py gold_frame_b1_stratified_500.tsv --per-cell 20
python frame_presence_report.py --frame gold_frame_b1_stratified_500.tsv \
    --lexicon ../corpus_lexicon.jsonl
```

Every script carries a `selftest` subcommand (fixture-based, no large assets) except the two
read-only probes.
[`check_gold_frame.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/eval/check_gold_frame.py)
is the gate: it caught the homograph duplicates in the first draft of this frame, which is
why §3 exists.

## 8. Limitations

- **Homograph-free by construction** (§3) — the metric describes monosemous-headword lemmas.
- **Frame-weighted, not corpus-weighted** (§4) — equal cells buy per-stratum resolution at
  the cost of a directly quotable global P@1.
- **Polysemy uncontrolled** (§4) — observed and reported, not balanced; `7+` is unreportable
  at this size.
- **Sense count is a proxy** — explicit sense list where present, else the highest numbered
  sense marker in the gloss, else 1.
- **Kochergina is one dictionary.** Its Russian is a specific lexicographic register; a
  lexicon rendering a headword in defensible but non-Kochergina Russian scores as wrong
  unless MG's pass-1 labels admit the variant. This is the main reason pass 1 is human.
- **Agreement is human–model** (§5), never inter-annotator.
- **DCS frequency is a different corpus** than the translated subset the lexicon was induced
  from — that independence is the point, but it means band ≠ frequency in *our* corpus.

_Dr. Mārcis Gasūns_
