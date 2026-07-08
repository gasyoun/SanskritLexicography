# RECIPES — reproduction recipes for the Sanskrit-data findings & datasets

_Created: 08-07-2026 · Last updated: 08-07-2026_

**Epistemic sibling of [`FINDINGS.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md).** FINDINGS cites *a number*; this file holds the act it cannot: **reproducing** — the exact runnable path back to that number. One recipe per derived dataset or heavy FINDINGS row, so a fact can be re-checked rather than trusted. This is what [`STALENESS.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/STALENESS.md)'s "Re-check recipe" column points at. One of the seven epistemic registries minted under [H356](https://github.com/gasyoun/Uprava/blob/main/handoffs/H356-Opus_csl-corrections_epistemic-sibling-registries_08.07.26.md). Its infra twin is [`Uprava/RECIPES.md`](https://github.com/gasyoun/Uprava/blob/main/RECIPES.md).

**How to read a row.** Every row opens with two glyphs:

- **Importance dot** (identical scale to FINDINGS): 🔴 3 high · 🟠 2 medium · 🟡 1 minor — here the dot rates **reproduction weight** (🔴 = a canonical/expensive derived asset others consume, must be reproducible; 🟡 = a light one-liner check).
- **Origin marker:** ⚙️ auto (a stub emitted from the manifest builder / a FINDINGS script-citation) · ✍️ human (a session wrote the full recipe).

Then `Inputs:`, `Command:`, `Expected:` (ties back to the FINDINGS §N it reproduces), `Env/runtime:`, and a `> **Source:**` line.

**Auto-seed:** [`seed_recipes.py`](https://github.com/sanskrit-lexicon/sanskrit-util/blob/main/tools/epistemic/seed_recipes.py) emits a stub per [`kosha` manifest](https://github.com/gasyoun/kosha/blob/main/data/manifest/datasets.json) row (each names a builder) and per FINDINGS row whose Evidence cites a `*.py`/`*.sh`.

**Categories** (below) group the recipes by *what kind of fact they reproduce* — a grammar/accent validation, a corpus-to-dictionary linkage, or a cross-dictionary census — so a reader can find the reproduction path by concern rather than by discovery order.

---

## A. Grammar & accent validation reproductions
*Recipes that re-derive a phonological/grammatical validation number against attested forms — the accent axis GO/NO-GO.*

### §1. Whitney accent axis validation (17→18/19 GO) → reproduce
🟠 ✍️ (reproduces [FINDINGS §54](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md#54-whitney-accent-axis-validates-at-1719-matrix-cells-go-against-attested-rv-accents))
Inputs: [`crosswalk/accent_rules.json`](https://github.com/gasyoun/WhitneyRoots/blob/main/crosswalk/accent_rules.json) (18 rules, 19-cell matrix), attested accented RV forms from VedaWeb 2.0 + Casaretto et al. (2025), PWG `key2` udātta positions ([`headword_index.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/headword_index.tsv)).
Command: score per [`ACCENT_VALIDATION_SPEC.md`](https://github.com/gasyoun/WhitneyRoots/blob/main/docs/ACCENT_VALIDATION_SPEC.md); note the `per_case` override trap (9 of 19 cells define a `G.pl`/`N.A.du.n` override the generic strong/middle/weakest slot ignores).
Expected: 18/19 cells GO at ≥90% position accuracy, 0 NO-GO, 1 measurement-only (`T2/T4/T6·monosyllable`, n≤1) — ties back to FINDINGS §54.
Env/runtime: VedaWeb API (`vedaweb.uni-koeln.de/api`) — check liveness first (`curl -sI --max-time 15 …/api/openapi.json`); the host has an extended outage history (§48, [SERVER_OUTAGES](https://github.com/gasyoun/Uprava/blob/main/SERVER_OUTAGES.md)).
↔ Interlinks: [CONTRADICTIONS §1](https://github.com/gasyoun/SanskritLexicography/blob/master/CONTRADICTIONS.md) (Whitney gen.pl accent) is the accent disagreement this validation adjudicates · [GAPS §1](https://github.com/gasyoun/SanskritLexicography/blob/master/GAPS.md) (ī/ū split, n=2) is the thin-evidence frontier the same axis runs up against · [DEAD_ENDS §2](https://github.com/gasyoun/SanskritLexicography/blob/master/DEAD_ENDS.md) is the failed corpus-only route that lacked the accent signal this recipe supplies.
> **Source:** [FINDINGS §54](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md#54-whitney-accent-axis-validates-at-1719-matrix-cells-go-against-attested-rv-accents) · [WhitneyRoots](https://github.com/gasyoun/WhitneyRoots) v1.3.0 · [08-07-2026](https://github.com/gasyoun/SanskritLexicography/commits/master?since=2026-07-08&until=2026-07-09) · `claude-opus-4-8`

---

## B. Corpus-to-dictionary linkage reproductions
*Recipes that re-derive a corpus↔dictionary join or word-alignment coverage number — the layer every frequency/translation pipeline sits on.*

### §2. DCS↔CDSL crosswalk (81.4% linked) → reproduce
🔴 ✍️ (reproduces [FINDINGS §12](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md#12-a-fifth-of-dcs-lemmas-have-no-cdsl-headword))
Inputs: DCS-2026 IAST lemmas (15,902), CDSL normalized keys; transcoder from `wf1/build_wf_from_dcs.py`.
Command: `python build_xref.py` (csl-apidev `simple-search/dcs_xref/`) → `dcs_cdsl_xref.tsv`; frequency map `wf0/wf.txt` (50,474) → `wf1/wf.txt` (50,574).
Expected: 12,946 of 15,902 (81.4%) link; 2,956 corpus-only — ties back to FINDINGS §12 / manifest `dcs-cdsl-xref` (15,902 rows).
Env/runtime: Python, offline once DCS CoNLL-U + CDSL keys are local; it is a LOD linkset — consume, never re-derive.
↔ Interlinks: [ASSUMPTIONS §1](https://github.com/gasyoun/SanskritLexicography/blob/master/ASSUMPTIONS.md) (DCS lemma == CDSL headword) is the premise this recipe *bounds* at 81.4% · [GLOSSARY "headword vs lemma"](https://github.com/gasyoun/SanskritLexicography/blob/master/GLOSSARY.md) defines the two sides being joined · [GAPS §3](https://github.com/gasyoun/SanskritLexicography/blob/master/GAPS.md) (Heritage as a third witness) is where the unlinked 18.6% could be recovered.
> **Source:** [FINDINGS §12](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md#12-a-fifth-of-dcs-lemmas-have-no-cdsl-headword) + kosha [datasets.json](https://github.com/gasyoun/kosha/blob/main/data/manifest/datasets.json) · [csl-apidev](https://github.com/sanskrit-lexicon/csl-apidev) · [08-07-2026](https://github.com/gasyoun/SanskritLexicography/commits/master?since=2026-07-08&until=2026-07-09) · `claude-opus-4-8`

### §3. DeepSeek word-alignment grounding cross-check (6.6% ungrounded) → reproduce
🟠 ✍️ (reproduces [FINDINGS §65](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md#65-66--of-the-deepseek-corpus-word-alignments-ground-to-nothing-in-their-verse))
Inputs: `corpus_lexicon.jsonl` (1,091,528 word-pairs — GITIGNORED, single copy on MG disk), L0 verse units rebuilt by [`src/build_l0.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_l0.py) (99,733 units / 116 works) from SamudraManthanam.
Command: [`src/tm_align.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/tm_align.py) cross-checks each pair against its L0 verse; feed `alignment_confidence` into [`tm_grade.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/tm_grade.py).
Expected: mean grounding 0.684, 93.4% grounded, 6.6% score 0; grade A 5.7%→5.3%, C 0.3%→0.9% — ties back to FINDINGS §65.
Env/runtime: Python, offline; corpus_lexicon is restricted-tier (published-RU-translation rights), regenerable via `build_corpus_lexicon.py` but single-copy.
↔ Interlinks: [ASSUMPTIONS §2](https://github.com/gasyoun/SanskritLexicography/blob/master/ASSUMPTIONS.md) (one transliteration keys all DCS files) is the keying premise the alignment join depends on · [GAPS §10](https://github.com/gasyoun/SanskritLexicography/blob/master/GAPS.md) (routing κ) is the adjacent grade-confidence measurement · [DEAD_ENDS §6](https://github.com/gasyoun/SanskritLexicography/blob/master/DEAD_ENDS.md) (OccId/sent_id key) is the id trap a DCS-import alignment must avoid.
> **Source:** [FINDINGS §65](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md#65-66--of-the-deepseek-corpus-word-alignments-ground-to-nothing-in-their-verse) · [RussianTranslation](https://github.com/gasyoun/SanskritLexicography/tree/master/RussianTranslation) · [08-07-2026](https://github.com/gasyoun/SanskritLexicography/commits/master?since=2026-07-08&until=2026-07-09) · `claude-opus-4-8`

---

## C. Cross-dictionary census & diachrony reproductions
*Recipes that re-derive a whole-corpus or cross-dictionary count — varga shares over time, the union headword index, the correction-loci census.*

### §4. Varga diachrony + Cramér's V (0.037) → reproduce
🟠 ✍️ (reproduces [FINDINGS §62](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md#62-varga-distribution-is-almost-epoch-stable-cramérs-v--0037--and-the-gasūns-2014-dissertation-prose-read-its-own-χ²-table-backwards))
Inputs: [VisualDCS `derived-data/Fonetika/regen-2026/varna_freq.csv`](https://github.com/gasyoun/VisualDCS/blob/main/derived-data/Fonetika/regen-2026/varna_freq.csv) (DCS pin 2026-03-05, 9,940,591 stop/nasal varṇas across time-slots 1–5).
Command: [`varga_shares.py`](https://github.com/gasyoun/SanskritGrammar/blob/chore/errata-kochergina-waiting/GasunsDhatu_2014/revision-2026/varga_shares.py) / `aggregate_vargas.py` (deterministic).
Expected: dentals ≈47–52%, labials ≈24–27%, gutturals 8.9→14.9%; 5×5 varga×epoch Cramér's V = 0.0372 (χ² = 54,890) — ties back to FINDINGS §62 / manifest `varga-series-diachrony`.
Env/runtime: Python stdlib, offline, deterministic; outputs `slot_era_map.csv` alongside.
↔ Interlinks: [CONTRADICTIONS §2](https://github.com/gasyoun/SanskritLexicography/blob/master/CONTRADICTIONS.md) (varga prose vs χ²) is the dissertation-prose contradiction this recomputation exposes · [GLOSSARY "varga"](https://github.com/gasyoun/SanskritLexicography/blob/master/GLOSSARY.md) defines the phonetic class being counted · [GAPS §11](https://github.com/gasyoun/SanskritLexicography/blob/master/GAPS.md) (verb-form-freq prelim) is a neighbouring diachronic-frequency measurement.
> **Source:** [FINDINGS §62](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md#62-varga-distribution-is-almost-epoch-stable-cramérs-v--0037--and-the-gasūns-2014-dissertation-prose-read-its-own-χ²-table-backwards) · [SanskritGrammar](https://github.com/gasyoun/SanskritGrammar)/[VisualDCS](https://github.com/gasyoun/VisualDCS) · [08-07-2026](https://github.com/gasyoun/SanskritLexicography/commits/master?since=2026-07-08&until=2026-07-09) · `claude-opus-4-8`

### §5. Cross-dict union headword index (323,425 / PWG∩MW=94,753) → reproduce
🔴 ✍️ (reproduces [FINDINGS §29](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md#29-pwg-and-mw-share-94753-headwords-in-the-union-index))
Inputs: 15 dicts' `<L>` headwords from `csl-orig/v02/`, SLP1-keyed.
Command: the HeadwordLists union build → [`union_headwords.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/union/union_headwords.tsv) (per-dict membership + gender flags).
Expected: 323,425 union headwords; PWG-bearing 106,054, MW-bearing 193,852, both 94,753 — ties back to FINDINGS §29 / manifest `union-headwords` (323,425 rows, 12.4 MB). CONSUME, don't rebuild (a new pairwise-overlap script is reinvention).
Env/runtime: Python; the built asset is public-tier in `data-v0.1.0`.
↔ Interlinks: [ASSUMPTIONS §4](https://github.com/gasyoun/SanskritLexicography/blob/master/ASSUMPTIONS.md) (PWG worklist covers the universe) is the scope premise this index actually measures · [DEAD_ENDS §1](https://github.com/gasyoun/SanskritLexicography/blob/master/DEAD_ENDS.md) (body-text headword mining) is the failed shortcut this canonical asset replaces · [GLOSSARY "headword vs lemma"](https://github.com/gasyoun/SanskritLexicography/blob/master/GLOSSARY.md) frames the `<L>` headword unit being unioned.
> **Source:** [FINDINGS §29](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md#29-pwg-and-mw-share-94753-headwords-in-the-union-index) · [SanskritLexicography](https://github.com/gasyoun/SanskritLexicography) · [08-07-2026](https://github.com/gasyoun/SanskritLexicography/commits/master?since=2026-07-08&until=2026-07-09) · `claude-opus-4-8`

### §6. Correction loci census (39,540 records) → reproduce
🟠 ✍️ (reproduces the kosha `correction-loci` manifest row, H294)
Inputs: all `batch_*/batches/*` change files across csl-corrections.
Command: [`scripts/build_correction_loci.py --selftest`](https://github.com/sanskrit-lexicon/csl-corrections/pull/291) (census invariants frozen 2026-07-07) → `data/derived/correction_loci.tsv`.
Expected: 39,540 records = 39,536 old→new + 4 old→del; `process∈{bulk,human}` splits the two machine markup batches (BOR 21,990 + LRV/markhom 8,063 = 76%) from human correction — manifest `correction-loci` (9.6 MB, 39,540 rows).
Env/runtime: Python, offline; keyed on (dict, L, k1) — line numbers are batch-time only, never a join key. Corrector identity excluded (public tier).
↔ Interlinks: [ASSUMPTIONS §6](https://github.com/gasyoun/SanskritLexicography/blob/master/ASSUMPTIONS.md) (a correction queue stays valid) is the perishability premise this census feeds · [DEAD_ENDS §4](https://github.com/gasyoun/SanskritLexicography/blob/master/DEAD_ENDS.md) (bulk typo respell) is the failure mode a proper loci census guards against · [GAPS §5](https://github.com/gasyoun/SanskritLexicography/blob/master/GAPS.md) (Stopovye diff) is an adjacent correction-coverage gap.
> **Source:** [kosha](https://github.com/gasyoun/kosha) [datasets.json](https://github.com/gasyoun/kosha/blob/main/data/manifest/datasets.json) `correction-loci` (H294) · [csl-corrections](https://github.com/sanskrit-lexicon/csl-corrections) · [08-07-2026](https://github.com/gasyoun/SanskritLexicography/commits/master?since=2026-07-08&until=2026-07-09) · `claude-opus-4-8`

---

## Conclusions

- **Every recipe ties a *number* back to a *runnable path*** — 81.4% linked (§2), 6.6% ungrounded (§3), Cramér's V = 0.037 (§4), 323,425 union headwords (§5), 39,540 correction loci (§6). A FINDINGS row that cannot be re-run this way is trust without reproduction; this file is the antidote.
- **The 🔴 rows (§2, §5) are canonical assets others consume — reproduce, but do NOT rebuild.** Both carry an explicit "CONSUME, don't rebuild" / "consume, never re-derive" caveat: a fresh crosswalk or pairwise-overlap script is reinvention, not reproduction. The recipe exists to *verify* the shipped asset, not to justify recomputing it.
- **Determinism and offline-once-local are the norm, with two watch-outs.** §1 depends on the VedaWeb API (check liveness — extended outage history), and §3's `corpus_lexicon` is restricted-tier single-copy on MG disk; the rest run offline against local inputs. Note the recorded traps — the accent `per_case` override (§1), the DCS keying scheme (§2/§3), line-numbers-are-not-a-join-key (§6).
- **Where they point:** each recipe reproduces a [FINDINGS](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) row, checks an [ASSUMPTIONS](https://github.com/gasyoun/SanskritLexicography/blob/master/ASSUMPTIONS.md) premise, and steers clear of the matching [DEAD_ENDS](https://github.com/gasyoun/SanskritLexicography/blob/master/DEAD_ENDS.md) — and [STALENESS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/STALENESS.md)'s "Re-check recipe" column points straight here.

---

_Dr. Mārcis Gasūns_
