# FINDINGS — cross-repo empirical registry

Non-obvious, **evidence-backed** facts about the Sanskrit-lexicon data, corpus, dictionary
structure, encoding, and tooling — the kind of thing that is expensive to re-discover and
easy to get wrong by assumption. Distinct from [`PILOT_LESSONS.md`](../PILOT_LESSONS.md)
(CI/CD process) and [`SHARED_CODE.md`](../SHARED_CODE.md) (who-owns-what code).

> **Living document — appended on a regular basis.** Every session that *measures* a
> non-obvious fact (a probe result, a count, a structural gotcha) adds it here, same pass as
> the work that found it. If you discovered it by running something, it belongs here.

**Schema per finding:** a one-line **claim** in bold, then `Evidence:` (the measurement, with
numbers / a file + line), `Implication:` (what to do or not do), and a **Source** link to the
exact statement and/or code, with a `— repo · date` tag. Keep them grounded (a number, a file,
a probe), never a hunch. When a finding is later refuted or superseded, strike it and say why.

---

## Corpus & parallel-text data

- **The parallel corpus rarely attests prefixed-verb surface forms.**
  Evidence: of √man's 15 prefixed forms, only **3** (`anuman`, `abhiman`, `avaman`) appear in
  the SamudraManthanam parallel corpus; the `pwg_preverb1.txt` sandhi-join produces the *same*
  surface strings as a naïve `upasarga+root` concat, so spelling is not the limiter — the
  corpus simply lemmatises prefixed verbs to the root or lacks them.
  Implication: prefix-specific Apresjan evidence is corpus-bound; for the ~80 % that miss,
  defer to the dictionary's own (German) gloss. Do **not** build a sandhi-join lookup
  expecting coverage gains — it's a no-op.
  **Source:** code [`subcard_portrait()`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/_pilot_gen_merged.py#L237)
  · statement [FREQ_TEST_RUNBOOK.md § Apresjan evidence](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/FREQ_TEST_RUNBOOK.md). — SanskritLexicography/RussianTranslation · 2026-06-24

- **No printed frequency dictionary of Sanskrit exists.**
  Evidence: absent from the prefaces and literature of PWG/PW/MW/GRA/AP90 and from Kochergina;
  only Hellwig's DCS corpus counts (≈2021) give per-lemma frequency.
  Implication: DCS-frequency headword ordering is a genuine innovation, not a digitisation of
  prior art.
  **Source:** [A33 note § 1 "The question"](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/A33_sense_ordering_note.md). — SanskritLexicography (A33) · 2026-06-24

- **DCS lemma data is keyed in two different transliterations.**
  Evidence: `VisualDCS/dcs_lemma_summary.json` (`lemmas`, freqBand 1–5) is **SLP1**-keyed
  (joins PWG `key1` natively); `RussianTranslation/src/dcs_lemma_renou.json` (breadth `n_texts`,
  dates) is **IAST**-keyed.
  Implication: a freq join must transcode SLP1↔IAST for the second; don't assume one scheme.
  **Source:** [`freq_route.py` header (lines 7–8) + `iast()`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/freq_route.py#L7-L8). — VisualDCS / RussianTranslation · 2026-06-24

- **The unaccented DCS corpus cannot distinguish present class I from VI (or IV from passive).**
  Evidence: WhitneyRoots — the corpus carries no pitch accent, and the class distinction rests
  on it.
  Implication: never write a corpus-derived verb class into reviewed data without a grammar /
  Zaliznyak cross-check.
  **Source:** [WhitneyRoots `REVIEWER_GUIDE.md`](https://github.com/gasyoun/WhitneyRoots/blob/main/REVIEWER_GUIDE.md). — WhitneyRoots · 2026-06

## Dictionary structure & markup

- **PWG never uses `<div n="m">`; secondary stems are encoded inline.**
  Evidence: 0 occurrences of `<div n="m">` in `csl-orig/v02/pwg/pwg.txt`; causative/desiderative/
  intensive/participle/passive of the simple root appear as `<div n="p">— <ab>caus.</ab> {#…#}`
  (a `<div n="p">` whose first token is an `<ab>` label, not a `{#upasarga#}`).
  Implication: a secondary-stem segmenter keys on the inline `<ab>` label
  (`SEC_DIVP_RE` + a caus/desid/intens/partic/pass/insens label set), not on `<div n="m">`.
  **Source:** code [`SEC_DIVP_RE` + the comment](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/research/root_segment_proto.py#L28-L34)
  · measured by [`verify_root_glue.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/verify_root_glue.py) (570 split, 0 merged). — csl-orig (pwg) / RussianTranslation · 2026-06-24

- **A headword's giant verb root often sits at a non-zero homonym index.**
  Evidence: √i has its 114-prefix verb root at homonym **2** (homonym 0 is the particle);
  √mā at index 2, √As at index 1; 19 of the top-50 freq roots have a giant homonym at
  index > 0 or more than one giant homonym.
  Implication: any per-record split / processing must iterate **all** homonym records, not
  `bufs[0]`, or it silently misses the verb (or drops extra giant homonyms).
  **Source:** code [`gen_root_split()`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/_pilot_gen_merged.py#L258)
  · audited by [`audit_root_split.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/audit_root_split.py). — csl-orig (pwg) / RussianTranslation · 2026-06-24

- **PWG orders senses genetically (etymological core first), not historically.**
  Evidence: across 13,900 multi-sense entries, printed sense-1 is the oldest-attested only
  **73.5 %** of the time; Kendall τ(printed vs date) = **0.375**; citations *within* a sense run
  old→new in 76 % of adjacent pairs but are strictly sorted in only 26 %.
  Implication: don't auto-re-sort senses by date or frequency (it changes the lead sense for
  ~1 in 4 entries and fights the source); surface attestation era as per-sense metadata instead.
  **Source:** [`sense_order_metrics.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/research/sense_order_metrics.md)
  · [`analyze_sense_order.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/research/analyze_sense_order.py). — SanskritLexicography (A33) · 2026-06-24

- **Vedic-citation density cleanly separates the dictionary traditions.**
  Evidence: fraction of cited senses reaching a Vedic source — **PWG 23.4 % ≈ MW 24.8 % ≫
  AP90 2.3 % ≫ Kochergina 0 %**.
  Implication: PWG/MW are etymological-genetic with a real historical apparatus; Apte and
  Kochergina are logical-semantic / pedagogical — do not import their sense order into a PWG
  translation.
  **Source:** [`cross_dict_metrics.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/research/cross_dict_metrics.md)
  · [`analyze_cross_dict.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/research/analyze_cross_dict.py). — SanskritLexicography (A33 cross-dict) · 2026-06-24

- **SKD and VCP carry essentially zero Western markup.**
  Evidence: ~0 `<ab>`/`<div>`/`<s>`/`<ls>` tags; citations appear via `iti`/quotes, verbs via
  `dhātuḥ`/`preraṇe`/`bhvādi`.
  Implication: any marker-based detector scores SKD/VCP at 0 *by construction* — never read 0
  as "no content"; use the indigenous cues. (Miscalled ≥4×.)
  **Source:** data [`v02/skd/skd.txt`](https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/skd/skd.txt)
  · [`v02/vcp/vcp.txt`](https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/vcp/vcp.txt) (grep: no `<ab>`/`<div>`). — SKD / VCP (csl-orig) · 2026-06

- **`ls_source_map.json` recognises 72.4 % of PWG's `<ls>` citations.**
  Evidence: 559,243 of 772,567 `<ls>` keys map to one of 45 dated primary sources
  (range −1125 → 1830); the unrecognised 27.6 % is catalogues / secondary literature
  (Aufrecht's Oxford catalogue, *Indische Studien*, *Indische Sprüche*), which skews *late*.
  Implication: dated-citation analyses see the most-cited primary corpus and are conservative
  about the oldest stratum, not biased toward it.
  **Source:** [`sense_order_metrics.md` § "Foundations check"](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/research/sense_order_metrics.md)
  · [`analyze_sense_order.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/research/analyze_sense_order.py). — RussianTranslation · 2026-06-24

## Encoding & normalization

- **IAST Unicode collides and lossily normalises if you're naïve.**
  Evidence: `ś` = `s` + U+0301 (combining acute), which collides with a pitch-accent mark;
  NFD-decompose-then-strip-Mn destroys vowel length (`ā`→`a`) and retroflex dots (`ṣ`→`s`).
  Implication: use a length-preserving `form_key`, not a blanket NFD+strip-combining.
  **Source:** [`form_key` in sanskrit_util](https://github.com/sanskrit-lexicon/sanskrit-util/blob/main/py/sanskrit_util/__init__.py). — sanskrit-util / shared · 2026-06

- **`csl-orig` files never carry a BOM; many exported HeadwordLists do.**
  Evidence: `csl-orig` dict `.txt` are BOM-free; e.g. `MW-unique-key1-…txt` **has** `EF BB BF`
  while its `key2` sibling does not.
  Implication: check `head -c 3` before transforming; preserve the file's existing BOM state on
  write; never silently add/strip one.
  **Source:** [SanskritLexicography `CLAUDE.md` § "Encoding — BOM is inconsistent"](https://github.com/gasyoun/SanskritLexicography/blob/master/CLAUDE.md). — csl-orig / SanskritLexicography · 2026-06

- **`devanagari_to_slp1` mis-routes ळ (ḷa).**
  Evidence: a pre-existing `sanskrit-util` master bug routes ळ via IAST→`x` instead of `L`.
  Implication: low-severity (affects `ocr_verify`), but don't trust ḷa round-trips until fixed
  (fix in progress on branch `feat/deva-to-slp1`).
  **Source:** [`devanagari_to_slp1` in sanskrit_util](https://github.com/sanskrit-lexicon/sanskrit-util/blob/main/py/sanskrit_util/__init__.py). — sanskrit-util · 2026-06

## Tooling & infra

- **CodeQL has no PHP analyzer.**
  Evidence: an `Analyze (php)` matrix job is a permanent red across the org; PHP is absent from
  CodeQL's supported languages.
  Implication: scan PHP with Semgrep instead; keep `php` out of any CodeQL language matrix.
  **Source:** [GitHub CodeQL — supported languages](https://codeql.github.com/docs/codeql-overview/supported-languages-and-frameworks/) (PHP not listed). — org-wide · 2026-06

- **The indigenous Sanskrit dictionaries agree on a head-word's derivation 90–100 %; Wilson 1832 is the systematic outlier (23–61 %).**
  Evidence: across 10 Cologne dicts whose etymology was extracted to `<dict>_etymology.tsv`, affix
  agreement on shared head-words (proportion, 95 % Wilson CI) is SKD↔VCP 93.8 % [85.2–97.6], Apte↔AP
  100 % [97.9–100], VCP↔SHS 98.5 % [95.8–99.5], but WIL↔SKD only **22.9 % [14.6–34.0]** and WIL↔VCP
  **61.2 % [58.7–63.7]** — the Wilson interval (≤34 %) is **disjoint** from every Sanskrit-side pair
  (≥83 %), so the divergence is statistically clear, not sampling noise. Cross-tradition root
  attribution: MW↔PWG (English √ vs German "Wurzel") 65 %, PWG↔PW 93 %.
  Implication: the Pāṇinian analysis is a stable cross-source signal usable as a consensus/QA oracle;
  Wilson's divergence is a distinct stratum, not noise.
  **Source:** [`cross_dict_agreement.csv`](https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/etymology_stats/cross_dict_agreement.csv)
  + [PAPER_DRAFT.md](https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/etymology_stats/PAPER_DRAFT.md)
  · dashboard https://sanskrit-lexicon.github.io/csl-orig/ — csl-orig · 2026-06-26

- **The same `<ab>E.</ab>` tag means different things across dicts — count the meaning, not the marker.**
  Evidence: WIL `E.` = Etymology (39,713×); but CAE `E.` = "Epithet of" (`E. of Śiva/Viṣṇu/Indra`,
  584×) and MD `E.` = "Epic" (`āste (E. + I. Ā.)`). A tag-count survey wrongly flagged CAE/MD as
  etymology sources; reading the entry contexts corrected it.
  Implication: never infer content from a shared tag across dicts (generalises the SKD/VCP
  zero-markup trap); validate a marker's *sense* per dictionary before parsing it.
  **Source:** `csl-orig/v02/{cae,md}/` entry contexts — csl-orig · 2026-06-26

---

_Started 2026-06-26 (relocated from `Uprava/FINDINGS.md`, which now holds **non-Sanskrit**
findings). Appended on a regular basis — add findings as they're discovered; this is the
shared memory of "things we measured that aren't obvious from the code."_
