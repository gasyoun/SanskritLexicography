# RECIPES — reproduction recipes for the Sanskrit-data findings & datasets

_Created: 08-07-2026 · Last updated: 08-07-2026_

**Epistemic sibling of [`FINDINGS.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md).** FINDINGS cites *a number*; this file holds the act it cannot: **reproducing** — the exact runnable path back to that number. One recipe per derived dataset or heavy FINDINGS row, so a fact can be re-checked rather than trusted. This is what [`STALENESS.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/STALENESS.md)'s "Re-check recipe" column points at. One of the seven epistemic registries minted under [H356](https://github.com/gasyoun/Uprava/blob/main/handoffs/H356-Opus_csl-corrections_epistemic-sibling-registries_08.07.26.md). Its infra twin is [`Uprava/RECIPES.md`](https://github.com/gasyoun/Uprava/blob/main/RECIPES.md).

**How to read a row.** Every row opens with two glyphs:

- **Importance dot** (identical scale to FINDINGS): 🔴 3 high · 🟠 2 medium · 🟡 1 minor — here the dot rates **reproduction weight** (🔴 = a canonical/expensive derived asset others consume, must be reproducible; 🟡 = a light one-liner check).
- **Origin marker:** ⚙️ auto (a stub emitted from the manifest builder / a FINDINGS script-citation) · ✍️ human (a session wrote the full recipe).

Then `Inputs:`, `Command:`, `Expected:` (ties back to the FINDINGS §N it reproduces), `Env/runtime:`, and a `> **Source:**` line.

**Auto-seed:** [`seed_recipes.py`](https://github.com/sanskrit-lexicon/sanskrit-util/blob/main/tools/epistemic/seed_recipes.py) emits a stub per [`kosha` manifest](https://github.com/gasyoun/kosha/blob/main/data/manifest/datasets.json) row (each names a builder) and per FINDINGS row whose Evidence cites a `*.py`/`*.sh`.

---

### §1. Whitney accent axis validation (17→18/19 GO) → reproduce
🟠 ✍️ (reproduces [FINDINGS §54](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md#54-whitney-accent-axis-validates-at-1719-matrix-cells-go-against-attested-rv-accents))
Inputs: [`crosswalk/accent_rules.json`](https://github.com/gasyoun/WhitneyRoots/blob/main/crosswalk/accent_rules.json) (18 rules, 19-cell matrix), attested accented RV forms from VedaWeb 2.0 + Casaretto et al. (2025), PWG `key2` udātta positions ([`headword_index.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/headword_index.tsv)).
Command: score per [`ACCENT_VALIDATION_SPEC.md`](https://github.com/gasyoun/WhitneyRoots/blob/main/docs/ACCENT_VALIDATION_SPEC.md); note the `per_case` override trap (9 of 19 cells define a `G.pl`/`N.A.du.n` override the generic strong/middle/weakest slot ignores).
Expected: 18/19 cells GO at ≥90% position accuracy, 0 NO-GO, 1 measurement-only (`T2/T4/T6·monosyllable`, n≤1) — ties back to FINDINGS §54.
Env/runtime: VedaWeb API (`vedaweb.uni-koeln.de/api`) — check liveness first (`curl -sI --max-time 15 …/api/openapi.json`); the host has an extended outage history (§48, [SERVER_OUTAGES](https://github.com/gasyoun/Uprava/blob/main/SERVER_OUTAGES.md)).
> **Source:** [FINDINGS §54](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md#54-whitney-accent-axis-validates-at-1719-matrix-cells-go-against-attested-rv-accents) · WhitneyRoots v1.3.0 · 08-07-2026 · Opus 4.8 (`claude-opus-4-8`)

### §2. DCS↔CDSL crosswalk (81.4% linked) → reproduce
🔴 ✍️ (reproduces [FINDINGS §12](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md#12-a-fifth-of-dcs-lemmas-have-no-cdsl-headword))
Inputs: DCS-2026 IAST lemmas (15,902), CDSL normalized keys; transcoder from `wf1/build_wf_from_dcs.py`.
Command: `python build_xref.py` (csl-apidev `simple-search/dcs_xref/`) → `dcs_cdsl_xref.tsv`; frequency map `wf0/wf.txt` (50,474) → `wf1/wf.txt` (50,574).
Expected: 12,946 of 15,902 (81.4%) link; 2,956 corpus-only — ties back to FINDINGS §12 / manifest `dcs-cdsl-xref` (15,902 rows).
Env/runtime: Python, offline once DCS CoNLL-U + CDSL keys are local; it is a LOD linkset — consume, never re-derive.
> **Source:** [FINDINGS §12](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md#12-a-fifth-of-dcs-lemmas-have-no-cdsl-headword) + kosha [datasets.json](https://github.com/gasyoun/kosha/blob/main/data/manifest/datasets.json) · csl-apidev · 08-07-2026 · Opus 4.8 (`claude-opus-4-8`)

### §3. DeepSeek word-alignment grounding cross-check (6.6% ungrounded) → reproduce
🟠 ✍️ (reproduces [FINDINGS §65](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md#65-66--of-the-deepseek-corpus-word-alignments-ground-to-nothing-in-their-verse))
Inputs: `corpus_lexicon.jsonl` (1,091,528 word-pairs — GITIGNORED, single copy on MG disk), L0 verse units rebuilt by [`src/build_l0.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_l0.py) (99,733 units / 116 works) from SamudraManthanam.
Command: [`src/tm_align.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/tm_align.py) cross-checks each pair against its L0 verse; feed `alignment_confidence` into [`tm_grade.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/tm_grade.py).
Expected: mean grounding 0.684, 93.4% grounded, 6.6% score 0; grade A 5.7%→5.3%, C 0.3%→0.9% — ties back to FINDINGS §65.
Env/runtime: Python, offline; corpus_lexicon is restricted-tier (published-RU-translation rights), regenerable via `build_corpus_lexicon.py` but single-copy.
> **Source:** [FINDINGS §65](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md#65-66--of-the-deepseek-corpus-word-alignments-ground-to-nothing-in-their-verse) · RussianTranslation · 08-07-2026 · Opus 4.8 (`claude-opus-4-8`)

### §4. Varga diachrony + Cramér's V (0.037) → reproduce
🟠 ✍️ (reproduces [FINDINGS §62](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md#62-varga-distribution-is-almost-epoch-stable-cramérs-v--0037--and-the-gasūns-2014-dissertation-prose-read-its-own-χ²-table-backwards))
Inputs: [VisualDCS `derived-data/Fonetika/regen-2026/varna_freq.csv`](https://github.com/gasyoun/VisualDCS/blob/main/derived-data/Fonetika/regen-2026/varna_freq.csv) (DCS pin 2026-03-05, 9,940,591 stop/nasal varṇas across time-slots 1–5).
Command: [`varga_shares.py`](https://github.com/gasyoun/SanskritGrammar/blob/chore/errata-kochergina-waiting/GasunsDhatu_2014/revision-2026/varga_shares.py) / `aggregate_vargas.py` (deterministic).
Expected: dentals ≈47–52%, labials ≈24–27%, gutturals 8.9→14.9%; 5×5 varga×epoch Cramér's V = 0.0372 (χ² = 54,890) — ties back to FINDINGS §62 / manifest `varga-series-diachrony`.
Env/runtime: Python stdlib, offline, deterministic; outputs `slot_era_map.csv` alongside.
> **Source:** [FINDINGS §62](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md#62-varga-distribution-is-almost-epoch-stable-cramérs-v--0037--and-the-gasūns-2014-dissertation-prose-read-its-own-χ²-table-backwards) · SanskritGrammar/VisualDCS · 08-07-2026 · Opus 4.8 (`claude-opus-4-8`)

### §5. Cross-dict union headword index (323,425 / PWG∩MW=94,753) → reproduce
🔴 ✍️ (reproduces [FINDINGS §29](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md#29-pwg-and-mw-share-94753-headwords-in-the-union-index))
Inputs: 15 dicts' `<L>` headwords from `csl-orig/v02/`, SLP1-keyed.
Command: the HeadwordLists union build → [`union_headwords.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/union/union_headwords.tsv) (per-dict membership + gender flags).
Expected: 323,425 union headwords; PWG-bearing 106,054, MW-bearing 193,852, both 94,753 — ties back to FINDINGS §29 / manifest `union-headwords` (323,425 rows, 12.4 MB). CONSUME, don't rebuild (a new pairwise-overlap script is reinvention).
Env/runtime: Python; the built asset is public-tier in `data-v0.1.0`.
> **Source:** [FINDINGS §29](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md#29-pwg-and-mw-share-94753-headwords-in-the-union-index) · SanskritLexicography · 08-07-2026 · Opus 4.8 (`claude-opus-4-8`)

### §6. Correction loci census (39,540 records) → reproduce
🟠 ✍️ (reproduces the kosha `correction-loci` manifest row, H294)
Inputs: all `batch_*/batches/*` change files across csl-corrections.
Command: [`scripts/build_correction_loci.py --selftest`](https://github.com/sanskrit-lexicon/csl-corrections/pull/291) (census invariants frozen 2026-07-07) → `data/derived/correction_loci.tsv`.
Expected: 39,540 records = 39,536 old→new + 4 old→del; `process∈{bulk,human}` splits the two machine markup batches (BOR 21,990 + LRV/markhom 8,063 = 76%) from human correction — manifest `correction-loci` (9.6 MB, 39,540 rows).
Env/runtime: Python, offline; keyed on (dict, L, k1) — line numbers are batch-time only, never a join key. Corrector identity excluded (public tier).
> **Source:** kosha [datasets.json](https://github.com/gasyoun/kosha/blob/main/data/manifest/datasets.json) `correction-loci` (H294) · csl-corrections · 08-07-2026 · Opus 4.8 (`claude-opus-4-8`)

---

_Dr. Mārcis Gasūns_
