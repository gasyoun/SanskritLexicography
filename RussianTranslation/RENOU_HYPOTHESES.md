# Renou tagging — hypothesis-testing programme (H1–H7)

_Created: 02-07-2026 · Last updated: 02-07-2026_

Executable specification for testing seven hypotheses on the Renou state/register
tagging system described in
[RENOU.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/RENOU.md).
Written so a fresh session (Sonnet-tier executor) can run any step without prior
context. Findings F1–F5 in
[RENOU_FINDINGS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/RENOU_FINDINGS.md)
are **already done** — do not redo them (bhāṣya syntactic register, BHS second
lexical world, perennial vs period-bound registers, kāvya/nāṭya coinage,
finite-verb recession).

## Locked decisions (MG, 02-07-2026)

1. **Destination:** infrastructure for `pwg_ru` + a dictionary-citation-bias
   study now; a quantitative findings paper (testing Renou 1956) later. Rigor
   bar accordingly: pilot validation, not full gold standard.
2. **Validation:** small pilot only — 60–80 entries targeting the *contested*
   cells (`dcs`-only states, `bhs`-only V, maximal I–V spans), via an
   interactive HTML review sheet (markdown checkboxes are banned).
3. **Visualizations:** all three forms, in this order — audit-report charts →
   static paper figures → GH-Pages dashboard (dashboard gated on a
   publish-safety check; the Pages site is public).
4. **Hypotheses:** all of them, one at a time, in the order below.

## Execution ground rules

- **Working dir:** `RussianTranslation/src`. Every Python script starts with
  `sys.stdout.reconfigure(encoding='utf-8')` and
  `sys.stderr.reconfigure(encoding='utf-8')`; write files with
  `encoding='utf-8'` (never `utf-8-sig` — no BOM).
- **Delivery:** branch + PR with auto-merge, never direct to `master`. One
  branch per hypothesis (`feat/renou-h4`, `feat/renou-pilot`, …). Update
  [.ai_state.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/.ai_state.md)
  and add a dated entry to
  [CHANGELOG.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/CHANGELOG.md)
  in the same PR.
- **Model provenance:** report tier + exact version for every step in the
  output doc (e.g. "computed by Sonnet 5 (`claude-sonnet-5`), judged by
  Opus 4.8 (`claude-opus-4-8`)"). This spec was authored by Fable 5
  (`claude-fable-5`). A bare tier is a defect.
- **Canonical sources are read-only.** Never edit `{code}.renou.jsonl` inputs
  by hand; all analysis is downstream. The audit convention holds: measure,
  don't mutate.
- **Outputs:** analysis write-ups are committed Markdown
  (`RENOU_H{n}_*.md`, dated header + byline, full blob URLs, no HTML);
  figures go to `research/figures/renou/` (SVG preferred, PNG fallback,
  committed); bulk derived data stays gitignored with the regeneration command
  documented.
- **Findings routing:** every confirmed result becomes a new numbered finding
  (F6, F7, …) appended to
  [RENOU_FINDINGS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/RENOU_FINDINGS.md)
  with its `[source]`/`[data]` evidence tag, in the same PR.

## Shared inputs

| Input | Where | Status |
|---|---|---|
| Per-dict Renou indices `{code}.renou.jsonl` (8 dicts, 770,292 entries) | `src/` | gitignored; **already built locally** (2026-06-25). Regenerate: `python renou_pipeline.py --all` |
| DCS lemma index `dcs_lemma_renou.json` (per-state `state_support`, per-register `register_support`) | `src/` | gitignored; built. Regenerate: `python build_dcs_renou.py` (~2–3 min) |
| `<ls>` source maps | [ls_source_map.json](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/ls_source_map.json), [ls_source_map_mw.json](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/ls_source_map_mw.json) | committed |
| Corpus register mapper + corpus-wide stats | [renou_corpus_map.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/renou_corpus_map.py) | committed; running it prints register shares over 1,091,528 aligned pairs |
| Aligned Sa→Ru corpus `corpus_lexicon.jsonl` (1.09 M pairs, SLP1) | `src/` | gitignored; present locally |
| Inter-signal audit | [renou_audit.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/renou_audit.py) → `renou_audit_report.md` | committed / gitignored |
| PWG∩MW headword crosswalk (94,753 rows, SLP1-keyed, `dicts` column) | [HeadwordLists/union/union_headwords.tsv](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/union/union_headwords.tsv) | committed — **reuse, do not rebuild** |
| Register glossaries (epig 709 / bhāṣya 14,498 / jaina 286 …) | [glossaries/](https://github.com/gasyoun/SanskritLexicography/tree/master/RussianTranslation/glossaries) | committed |

Record schema (per line of `{code}.renou.jsonl`): `key1` (join key to the
Russian cards), `iast`, `renou_enriched` (list of states I–V),
`renou_provenance` (`{state: [signal,…]}` over `ls`/`dcs`/`bhs`/`wl`),
`renou_register` (list over the 20-register lattice),
`renou_register_provenance`. Ten worked examples, simple → tough, are in
[RENOU.md §Provenance examples](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/RENOU.md#provenance-examples).

---

## Step 0 (first pass, runs alongside H4) — pilot human validation

**Question.** What is the actual precision of the contested signal cells? The
existing audit is *internal consistency only* (signals cross-checked against
each other, `<ls>` as anchor). Nothing yet distinguishes `dcs` over-tagging
from `ls` under-citation — only a human judgment can.

**Sample — 70 entries, five strata, fixed seed (42), sampler committed as
`src/renou_pilot_sample.py`:**

| Stratum | n | Definition (from `{code}.renou.jsonl`) |
|---|--:|---|
| A. `dcs`-only states | 20 | a state whose provenance is exactly `["dcs"]`; spread over states I–V and ≥4 dicts |
| B. `bhs`-only V | 15 | `V: ["bhs"]` and no other V signal |
| C. maximal-span suspects | 15 | `renou_enriched` = I–V while `ls` supports ≤2 states (the audit's `akāra` pattern) |
| D. single-era `dcs_adds` | 10 | entries with both `ls`+`dcs` where `dcs` adds exactly one era beyond `ls` |
| E. corroborated controls | 10 | ≥2 signals agreeing on every state (expected-good; calibrates the sheet) |

**Sheet.** One interactive single-file HTML review sheet (the `/review-sheet`
pattern: approve / reject / defer per item + free-text note → download
`decisions.json`). Each item must show: headword (IAST), dictionary, the
**contested state** being judged, the full provenance dict, the `ls` citations
(resolved siglum names), and the DCS evidence behind the contested state
(`state_support` detail: which texts, how many, what confidence). The judgment
question per item: *"Is state X justified for this headword — is the word
genuinely attested in that Sanskrit?"* Approve = justified; reject =
over-tag; defer = can't tell from the evidence shown.

**Analysis (after MG votes, via `/decisions-apply`).** Per-stratum precision
with Wilson 95 % intervals → `RENOU_VALIDATION.md`. Interpretation contract,
fixed in advance: stratum A precision bounds the `dcs` signal; C separates
homograph collapse (reject) from genuine era-neutrality (approve); D directly
splits "dcs over-tags" vs "ls under-cites"; if E is not ≈100 %, the sheet
itself is miscalibrated and results are void. The error bounds feed H1's
write-up and become finding F-next in RENOU_FINDINGS.md.

**Deliverables:** `src/renou_pilot_sample.py`, `review/renou_pilot_sheet.html`
(committed), sample JSONL (committed — it is small), then after votes
`RENOU_VALIDATION.md`.

---

## H4 — dictionary citation bias (run first; no validation gate needed)

**Hypothesis.** 19th-century dictionaries over-cite Vedic and kāvya relative
to actual usage, and under-cite the epic — a measurable imprint of
philological taste. Corpus baseline (attestation-level route): epic 61.0 %,
ṛgveda 14.4 %, atharva 5.6 %, kāvya 3.9 %, smṛti 3.6 %, upaniṣad 3.5 %,
kārikā 2.6 %, kathā 2.0 %, tantra 1.2 %, bhāṣya 1.2 %, bauddha 1.1 %.

**Why it needs no gold standard:** both sides are deterministic — the `<ls>`
register route (the lexicographer's own citations) vs the corpus genre route.
Neither depends on `dcs` state-tagging precision.

**Method.**
1. **Citation side.** Per dictionary, the register distribution of the `ls`
   route: count (entry, register) pairs where the register's provenance
   includes `"ls"`. If per-entry resolved citation *instances* are recoverable
   from the tagger (preferred unit — a dict may cite the same register many
   times per entry), use instance counts and report both units.
2. **Usage side.** `python renou_corpus_map.py` corpus-wide register counts
   (the baseline above).
3. **Compare shares, not raw counts** (the units differ: citations vs aligned
   word-pairs). Per register *r* and dict *d*: bias(d,r) =
   log2( citation-share(d,r) / usage-share(r) ). Bootstrap the citation side
   (resample entries, 1,000 reps) for a 95 % CI.
4. **Scope guard.** Only registers reachable by BOTH routes enter the ratio
   table. One-route registers (`jaina`, `epig` — `ls`-only; corpus-only
   genres) are listed separately, not force-compared. `hors_inde` is excluded
   (no source at all).

**Outputs.** `RENOU_H4_CITATION_BIAS.md` (per-dict bias table + interpretation);
dumbbell chart per dict (citation-share vs usage-share, one row per register)
→ `research/figures/renou/h4_citation_vs_usage_{dict}.svg`; findings F-next.

**Acceptance.** Sign of the bias (over/under) agrees between entry-level and
instance-level units for every register reported; epic and ṛgveda results
stated explicitly (they are the headline: 61 % of usage — what share of
citations?).

---

## H6 — agreement follows the Zipf curve (infrastructure payoff)

**Hypothesis.** `ls`–`dcs` exact agreement falls with lemma corpus frequency;
`dcs_adds` rises with it. If confirmed, `renou_low_info` gets a *principled
frequency threshold* instead of the current state-count heuristic
(`LOW_INFO_MIN_STATES`).

**Method.** Lemma frequency = aggregated pair counts from
`corpus_lexicon.jsonl` (in-repo; do NOT re-derive corpus frequency from
scratch — check
[SHARED_CODE.md §8](https://github.com/gasyoun/github-spine/blob/main/SHARED_CODE.md)
for the canonical VisualDCS frequency table first and prefer it if it joins
cleanly on lemma). Among entries carrying both `ls` and `dcs`: bin by log10
frequency, per bin compute exact-agreement / `dcs_adds` / `dcs_misses` rates
(the same trichotomy as
[renou_audit.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/renou_audit.py)).
Fit a logistic curve; report the frequency at which P(exact) drops below 50 %.

**Outputs.** Scatter + fitted curve →
`research/figures/renou/h6_zipf_agreement.svg`; `RENOU_H6_ZIPF.md` with a
concrete recommended threshold and a note on whether to wire it into
[renou_portrait.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/renou_portrait.py)
(recommendation only — no behavior change in this pass).

---

## H1 — Vedic lexical survival curves (after Step 0 votes land)

**Hypothesis.** A large fraction of I-attested (Vedic) vocabulary never
reappears in III/IV; survival is word-class-dependent (particles ≈ 100 %,
nominals lowest, verbal roots between).

**Method.** Universe = lemmas with state I under the `dcs` signal
(min-support applied). Survival into II/III/IV = presence of that state on
the same lemma. Stratify by word class via the MW grammar field joined by
headword where available; where not, report unstratified plus an
indeclinable-list subset. **Two mandatory robustness layers:** (1) sensitivity
at `--dcs-min-support 2 / 3 / 5` (the tunable in
[tag_dict_from_source.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/tag_dict_from_source.py));
(2) the homograph-collapse error bound from Step 0 stratum C applied as an
uncertainty band — survival is *inflated* by collapse, so the band is
one-sided. State this limitation in the write-up; do not present a single
unqualified number.

**Outputs.** Survival table + streamgraph (I → II/III/IV flow) →
`research/figures/renou/h1_survival.svg`; `RENOU_H1_SURVIVAL.md`; finding
F-next. This is the flagship diachronic figure for the later findings paper.

---

## H5 — MW inherits the Petersburg citation structure

**Hypothesis.** MW's citation profile is largely inherited from PWG/PW
(known philologically, never measured).

**Method.** Join MW↔PWG entries via
[HeadwordLists/union/union_headwords.tsv](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/union/union_headwords.tsv).
For each shared headword compare the `ls`-provenance state profiles:
(a) exact-match rate, (b) mean Jaccard, (c) **containment** —
P(MW ls-states ⊆ PWG ls-states) — the inheritance signature. Baseline/control:
the same statistics for MW↔AP (an independent lineage); inheritance is claimed
only if MW↔PWG containment clearly exceeds MW↔AP. If per-entry resolved sigla
are recoverable, repeat at siglum level (stronger: shared *citations*, not
just shared eras).

**Outputs.** `RENOU_H5_LINEAGE.md` + a containment-vs-baseline figure →
`research/figures/renou/h5_lineage.svg`; finding F-next (this is the core of
the dictionary-bias study together with H4).

---

## H2 — compound-length inflation (cross-repo; needs VisualDCS)

**Hypothesis.** Mean nominal-compound length grows Vedic → epic → kāvya →
bhāṣya (the nominal-style thesis F5 from the morphology side).

**Method.** Requires per-token compound segmentation — that lives in the
**VisualDCS** M1–M8 CoNLL-U→SQLite pipeline (`src/DCS-data-2026/`), not here.
Compute mean compound members per nominal token, grouped by the same
genre→register mapping as
[renou_corpus_map.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/renou_corpus_map.py).
Execute in the VisualDCS repo; commit the figure and write-up here
(`RENOU_H2_COMPOUNDS.md`). Known caveats from memory: DCS `OccId`/`sent_id`
are non-unique; UD `Tense=Past` conflates aorist/perfect (irrelevant here but
don't trust UD features blindly).

---

## H3 — register lexical disjointness

**Hypothesis.** Epigraphic and Buddhist Sanskrit are *lexically
self-contained worlds* (the epig glossary is 68 % corpus-absent; F2 showed it
for BHS); narrative/poetic registers share vocabulary heavily.

**Method.** From headword-level `renou_register` over all 8 dicts: pairwise
Jaccard between register vocabularies (restrict to registers with ≥200
member lemmas). Complement with corpus-absence rate per register (share of
the register's vocabulary absent from `corpus_lexicon.jsonl`). Expect `epig`,
`bauddha`, `jaina` as outliers on both measures.

**Outputs.** Register×register Jaccard heatmap →
`research/figures/renou/h3_register_jaccard.svg`; `RENOU_H3_DISJOINT.md`;
finding F-next.

---

## Visualization workplan (three tracks, in order)

1. **Audit-report charts (durable).** Extend
   [renou_audit.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/renou_audit.py)
   to save figures next to `renou_audit_report.md` and reference them from it,
   regenerated on every run: (a) **UpSet plot** of state-combination
   frequencies per dict (5 multi-label sets — an UpSet, never a Venn);
   (b) provenance-stacked bars per dict × state (`ls`/`dcs`/`bhs`/`wl` share —
   makes the trust ladder visible; PW/SCH state-V being all soft signal should
   leap out); (c) the agreement trichotomy per dict. Matplotlib; no seaborn
   dependency unless already installed; `upsetplot` package allowed.
2. **Static paper figures.** The per-hypothesis SVGs above, publication-grade
   (labeled axes, font ≥ 9 pt, no titles baked in — captions live in the MD).
3. **GH-Pages dashboard (last, gated).** An entry-portrait demo (search a
   headword → state badge + register sub-label + provenance drill-down,
   `renou_portrait`-driven) on the existing
   [gasyoun.github.io/SanskritLexicography](https://gasyoun.github.io/SanskritLexicography)
   site (built by `build_article_site.py` → `gh-pages`). **Mandatory
   `/publish-safety-check` before pushing anything to the public site** — the
   underlying stores are gitignored for a reason; the demo must embed only
   derived per-headword tags, never the Russian card texts wholesale.

## Execution order (one at a time)

| # | Step | Gate | Executor tier |
|--:|---|---|---|
| 1 | H4 citation bias + Step 0 sheet generation (same pass) | none | Sonnet 5 (`claude-sonnet-5`) |
| 2 | MG votes the pilot sheet → `RENOU_VALIDATION.md` | human votes | Sonnet 5 analysis; Opus 4.8 (`claude-opus-4-8`) if verdicts need adjudication |
| 3 | H6 Zipf agreement | none | Sonnet 5 |
| 4 | H1 survival curves | Step 0 error bounds | Sonnet 5 |
| 5 | H5 MW–PWG lineage | none | Sonnet 5 |
| 6 | H3 register disjointness | none | Sonnet 5 |
| 7 | H2 compound inflation | VisualDCS session | Sonnet 5 |
| 8 | Audit-report charts | can run any time after 1 | Sonnet 5 |
| 9 | GH-Pages dashboard | `/publish-safety-check` + MG go | Sonnet 5 |

Each step = its own branch + PR + changelog entry + findings append + model
provenance line. If a step's result contradicts this spec's expectations,
write the contradiction into the step's MD and into
[RENOU_FINDINGS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/RENOU_FINDINGS.md)
— a refuted hypothesis is a finding, not a failure.

_Dr. Mārcis Gasūns_
