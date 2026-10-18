# MW annexure provenance — uptake evolution, corroboration and the enrichment metrics (csl-corrections#119)

_Created: 15-09-2026 · Last updated: 15-09-2026_

Companion details to [`MW_PWK_NACHTRAEGE_MISSING_ENTRIES_TRIAL_14-09-2026.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/MW_PWK_NACHTRAEGE_MISSING_ENTRIES_TRIAL_14-09-2026.md) and [`MW_PWK_NACHTRAEGE_TRIAL_INDEPENDENT_RECHECK_14-09-2026.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/MW_PWK_NACHTRAEGE_TRIAL_INDEPENDENT_RECHECK_14-09-2026.md) (whose §7 carries the MW72 baseline). Question source: [csl-corrections#119, comment 4359094604](https://github.com/sanskrit-lexicon/csl-corrections/issues/119#issuecomment-4359094604) (Andhrabharati, 01-05-2026). Adjudication: [`MW-NACHTRAG-ADJUDICATION-14-09-2026.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/MW-NACHTRAG-ADJUDICATION-14-09-2026.tsv) (H4878, PRs [#2208](https://github.com/gasyoun/SanskritLexicography/pull/2208)/[#2210](https://github.com/gasyoun/SanskritLexicography/pull/2210)/[#2211](https://github.com/gasyoun/SanskritLexicography/pull/2211)). Builder: [`nachtrag_uptake_details.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/nachtrag_uptake_details.py).

## 1 · Sources with publication years — the timeline argument

The whole "MW99's annexure draws on the Nachträge" claim is a claim about **dates**, so every source is cited with its year from here on:

| source | per-volume publication years | role here |
|---|---|---|
| Böhtlingk–Roth, great Petersburg dictionary (Cologne `pwg`) | **Bd 1 1855 · Bd 2 1856 · Bd 3 1857 · Bd 4 1858 · Bd 5 1861 · Bd 6 1863 · Bd 7 1872–75 (issued in parts)** | the other Petersburg work — out of scope for the `sup` tags, see [CONTRADICTIONS §18](https://github.com/gasyoun/SanskritLexicography/blob/master/CONTRADICTIONS.md) |
| Böhtlingk, *kürzere Fassung* (Cologne **`pw`**, MG's «PWK») | **Pt 1 1879 · Pt 2 1880 · … · Pt 7 1889** (one year per part; pts 2–6 to be pinned from the part title pages) | **the `sup_1`…`sup_7` tags live here**; `sup_7` = part 7 (**1889**) — the kāritra locus (7-331-d) |
| *Nachträge und Verbesserungen* (standalone digitization, Cologne `pwkvn`) | same parts as the kürzere Fassung | 24,976 entries; `kāritra` L16013 |
| Monier-Williams **MW72** | **1872** | 51,162 unique `k1∪k2`; **no annexure** |
| Monier-Williams **MW99** | **1899** | 344,684 unique `k1∪k2`; annexure = 6,067 `k1` (`<info n="sup"/>`) |
| Edgerton, *Buddhist Hybrid Sanskrit Dictionary* (Cologne `bhs`) | **1953** | 17,839 entries; post-dates MW99 by 54 years |
| *Mahāvyutpatti* | 9th-century glossary (edition year to be pinned) | `kāritra` = MAHĀVY 245/844 |

**Standing convention (MG, 15-09-2026):** a span like "1855–1875" is a title-page span, **not** per-volume precision — each volume of a multi-volume work has its own single year, and it must always be kept in mind for **PW, PWG, EWA, KEWA** (EWA: Bd I 1992 · II 1996 · III 2001; KEWA: Bd I 1956 · II 1963 · III 1976 · IV 1980). The whole annexure-draws-on-Nachträge argument turns on **which parts were printed when** relative to 1872 and 1899.

**Sharpened by the per-volume reading:** the motivating locus `kāritra` sits in the **kürzere Fassung, part 7 (1889), p. 331 col d** — printed **10 years before MW99 and 17 years after MW72**. MW99 could have taken it; it did not. (MW72 could not have, on any ordering of the 1872 printings of the great PW's last parts — but that comparison belongs to the great-PW layer, where `kāritra` is absent anyway.)

**Why it matters:** every Nachträge layer (PW vol 7, 1872–75) and the whole kürzere Fassung (1879–89) post-date MW72 (1872) and pre-date MW99 (1899). So a Nachträge word present in MW99 but absent from MW72 is a word MW *could only have taken from the Nachträge* — the uptake numbers in §3 are therefore direct evidence of the annexure's dependence, not a coincidence of coverage.

## 2 · The enrichment metric family (the "~7.8×" finding)

Metric: for a headword set **S**, compare its share among MW99's annexure entries against its share among MW99's main entries. A ratio ≫1 means the annexure is disproportionately stocked from S. Convention: `k1`-only sets; MW99 annexure = 6,067 `k1`, main = 188,016 `k1` (`k1` total 194,083).

| source set S | n(S) | in annexure | in main | enrichment |
|---|--:|--:|--:|--:|
| kürzere-Fassung Nachträge `sup_7` (letzte Nachträge, pt 7 = 1889) | 13,094 | 1,798 (29.6 %) | 7,157 (3.8 %) | **7.79×** |
| kürzere-Fassung Nachträge `sup_1`…`sup_7` (all layers, 1879–1889) | 14,401 | 1,956 (32.2 %) | 7,659 (4.1 %) | **7.91×** |
| `pwkvn` standalone digitization of the same Nachträge | 14,995 | 1,971 (32.5 %) | 7,787 (4.1 %) | **7.84×** |
| Edgerton BHS (1953) | 17,777 | 413 (6.8 %) | 6,128 (3.3 %) | **2.09×** |

**Reading:** the MW99 annexure is **~7.8× enriched for PW-Nachträge words** and only **~2.1× enriched for Edgerton's BHS words** — i.e. the annexure is roughly **3.7× more "PW-flavoured" than "BHS-flavoured"**. Edgerton (1953) post-dates MW99 by half a century, so a low BHS enrichment is expected; the PW layers *pre-date* MW99 and the enrichment is high — the asymmetry is the quantitative form of Andhrabharati's postulate.

Caveat: these are set-overlap ratios, not citation counts — a word can be in the annexure for reasons other than its Nachträge entry. The metric ranks *provenance likelihood*, and the 30 % reverse share (trial §3) is the direct check.

## 3 · MW72 (1872) → MW99 (1899) uptake — evolution details

Per Nachträge layer (`mw72_uptake_evolution.tsv`):

| layer | unique | in MW72 | in MW99 | new in MW99 | … via annexure | … via main | skipped by both |
|---|--:|--:|--:|--:|--:|--:|--:|
| `sup_1` | 1,755 | 342 (19 %) | 991 (56 %) | 655 | 281 | 374 | 758 |
| `sup_2` | 1,464 | 259 (18 %) | 757 (52 %) | 502 | 192 | 310 | 703 |
| `sup_3` | 1,712 | 361 (21 %) | 1,136 (66 %) | 778 | 198 | 580 | 573 |
| `sup_4` | 1,016 | 180 (18 %) | 669 (66 %) | 489 | 94 | 395 | 347 |
| `sup_5` | 2,192 | 564 (26 %) | 1,568 (72 %) | 1,013 | 248 | 765 | 615 |
| `sup_6` | 1,229 | 264 (21 %) | 808 (66 %) | 545 | 117 | 428 | 420 |
| **`sup_7`** | **13,094** | **2,892 (22 %)** | **8,955 (68 %)** | **6,090** | **1,474** | **4,616** | **4,112** |

**Interpretation for the PW/PWG-influence question:** MW72 already contained ~20 % of every Nachträge layer (it was compiled from the earlier PW volumes); MW99 then took **~60 % of the remaining pool** — most of it through the **main body** (4,616) and a substantial block through the **annexure** (1,474). That two-channel uptake, with the annexure concentrated on the latest layer (`sup_7` = 1,474 of 1,474+…; the annexure share of new words rises in the later layers), is the pattern to read as *documented dependence* on the Nachträge rather than coincidence.

**Dropped between the two editions (27):** `AKAta, Card, Uhin, aSfRya, aYjanika, amanasvin, amfzya, aniNgya, anumAsa, anupadeSa, apragIta, aramaRIya, asaMsTiti, asevana, asvAmya, avaRqa, avasarpin, dAsIka, indindira, karmatas, lavaNga, pArizad, pacanika, qItara, taqAGAta, upajIka, var` — a separate, small correction class (MW99 deleted these), worth an adjudication pass of its own; note several look like parse artifacts (`Card`, `var`, `qItara`) and should be scan-checked before any filing.

## 4 · Homonym / sense-extension census — how many sup_7 entries are extensions?

| metric | value |
|---|--:|
| `sup_7` entries | 13,208 |
| unique `sup_7` headwords | 13,094 |
| with an explicit `<hom>N.</hom>` tag | 541 (4.1 %) |
| headword **already present in the PW main body** (extension of an existing word, not a new headword) | **4,790 (36 %)** |
| genuinely new headwords | 8,418 (64 %) |

**Why this matters for the "MW skipped intended entries" claim:** a third of the `sup_7` slice is not new vocabulary but **new homonyms/senses of words PW already had** — and MW99 often carries the word already (which is why 4,790 "extensions" mostly land in the covered tiers). The "skipped intended entries" question is therefore sharpest on the **8,418 genuinely new headwords**, not on all 13,094. Explicit `<hom>` tags per layer: `sup_1`=62, `sup_2`=40, `sup_3`=70, `sup_4`=45, `sup_5`=140, `sup_6`=70, `sup_7`=541.

## 5 · DCS-ranked 10-word samples for every big list

DCS bands (Hellwig DCS-2021): 5 = very common (1000+ occurrences), 4 = common (100–999), 3 = uncommon (10–99), 2 = rare (2–9), 1 = hapax. "Most frequent first" = highest band. Full table: [`nachtrag_dcs_samples.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/nachtrag_dcs_samples.tsv).

**1,751 confirmed-missing from MW** (1,750 unique after dedup): `aBinirhAra` (3), `apariRAyaka` (3), `asADaka` (3), `evaMvAdin` (3), `EraRqa` (2), `aBAvaka` (2), `aDAtu` (2), `aDOta` (2), `aSOcaka` (2), `aYjanaparvan` (2).

**572 confirmed-missing corroborated by ≥2 independent dictionaries:** `aBinirhAra` (3), `apariRAyaka` (3), `asADaka` (3), `evaMvAdin` (3), `aDOta` (2), `aYjanaparvan` (2), `acetita` (2), `adamBin` (2), `agaRya` (2), `akarAla` (2).

**149 confirmed-missing citing Mahāvyutpatti:** `cAturdvIpaka` (2), `evaMpramuKa` (2), `goSAlIputra` (2), `icCantika` (2), `kalandakanivApa` (2), `AdarSamuKa` (1), `KARu` (1), `tuRava` (1), `ADAraRamudra` (0), `ARipratyARInirhArayoga` (0).

**4,112 never-seen (absent from MW72 *and* MW99):** `SA` (4), `arTay` (4), `dUzay` (4), `guRay` (4), `lakzay` (4), `mahant` (4), `pyA` (4), `varRay` (4), `ArAgay` (3), `AwarUzaka` (3). ⚠️ the top of this list is dominated by **denominal `-aya` verb stems** (`arTay`, `dUzay`, `guRay`, `lakzay`, `varRay`, `ArAgay`) — a class MW handles under its root/verb apparatus rather than as separate headwords; treat them as a **named false-positive class** for the adjudicator, not as missing entries.

**95 confirmed-missing also attested in Edgerton's BHS:** `aBinirhAra` (3), `agaRya` (2), `cAturdvIpaka` (2), `icCantika` (2), `kalandakanivApa` (2), `kowanaka` (2), `AdarSamuKa` (1), `KARu` (1), `Kusta` (1), `kuwukuYcaka` (1).

**Extension headwords (already in the PW main body):** `A` (5), `AKyA` (5), `Adi` (5), `Aditya` (5), `Ananda` (5), `Ap` (5), `As` (5), `Atman` (5), `BAga` (5), `BAz` (5) — i.e. the extension class is dominated by very common words gaining a new sense, exactly as expected.

## 6 · Edgerton (1953) vs MW99 (1899) — how does BHS compare?

- BHS unique keys 21,146 (`k1`-only 17,777); **6,603 (31 %)** also in MW99 — MW99 covers a third of Edgerton's vocabulary, unsurprising for a Buddhist-hybrid lexicon 54 years older.
- BHS words in the MW99 annexure: 413/6,067 = 6.8 %; in MW99 main: 6,128/188,016 = 3.3 % → **enrichment 2.09×** (vs 7.79–7.91× for the PW Nachträge, §2).
- **95** of the 1,751 confirmed-missing candidates are attested in BHS — the Buddhist-Hybrid core of the missing-entry class (matches the trial's `kāritra` case, which cites MAHĀVY and is BHS-flavoured).
- Cross-read: the annexure's BHS component is real but modest — the annexure is predominantly a **PW-Nachträge** phenomenon, with a smaller Buddhist layer.

## 7 · Machine-usable proposal list (approved 15-09-2026)

[`MW-NACHTRAG-PROPOSALS-15-09-2026.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/MW-NACHTRAG-PROPOSALS-15-09-2026.tsv) — **572 rows**, one per candidate with `verdict = confirmed-missing` **and** `corr_n ≥ 2` (corroborated by at least two independent dictionaries):

`hw_slp1 · iast · pw_L · pw_pc · corr_n · corr_dicts · mahavy_refs · dcs_band · proposed_action · evidence · gloss`

`proposed_action` = `add-entry`. This is the file to feed the monthly [`/cologne-batch-pr`](https://github.com/gasyoun/claude-config/blob/main/commands/cologne-batch-pr.md) discipline: **every row still needs printed-scan verification** (the source is a digitization; `kāritra` itself is the canary: pw 7-331-d). The wider tiers (`corr_n = 1`, and the near-form pool) stay in the adjudication TSV for a second pass.

## 8 · Reproduction

```sh
python HeadwordLists/nachtrag_uptake_details.py   # ~90 s, stdlib only
# reads csl-orig/v02 (CSL_ORIG_V02) + VisualDCS/dcs_lemma_summary.json (DCS_LEMMA_JSON)
# + HeadwordLists/MW-NACHTRAG-ADJUDICATION-14-09-2026.tsv
```

Files: [`nachtrag_uptake_details.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/nachtrag_uptake_details.py) · [`mw72_uptake_evolution.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/mw72_uptake_evolution.tsv) · [`nachtrag_dcs_samples.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/nachtrag_dcs_samples.tsv) · [`MW-NACHTRAG-PROPOSALS-15-09-2026.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/MW-NACHTRAG-PROPOSALS-15-09-2026.tsv).

## 9 · Caveats

1. **Set overlaps, not citations** — the enrichment metric (§2) ranks provenance likelihood; only the reverse share (trial §3) directly measures dependence.
2. **DCS band ≠ frequency** — bands are log-order buckets (1–5) from the DCS-2021 snapshot; ties inside a band are alphabetical.
3. **Dedup**: 1,751 confirmed-missing rows = 1,750 unique headwords (one duplicate `k1`).
4. **Named false-positive classes**: the `-aya` denominal stems in the never-seen top-10 (§5), the `len(hw) < 3` short forms (trial §3 note), and the `kAritra`~`kArita` near-form pair (recheck §2).
5. The dropped-between-editions list (§3) includes apparent parse artifacts (`Card`, `var`, `qItara`) — scan-check before any use.

## 10 · H4884 — never-seen (4,112) + dropped (27) adjudicator

MG ruling 15-09-2026 «Оба параллельно»: the two classes named in §3/§5 (never-seen
absent from MW72 *and* MW99, dropped MW72-had-it-MW99-lost-it) now carry a
per-row verdict, reusing the corroboration/stem/fold-twin machinery of
[`mw_pwk_nachtraege_adjudicate.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/mw_pwk_nachtraege_adjudicate.py)
(H4878/H4883) rather than rebuilding it. Builder:
[`mw72_classes_adjudicate.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/mw72_classes_adjudicate.py).
Output:
[`MW72-CLASSES-ADJUDICATION-15-09-2026.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/MW72-CLASSES-ADJUDICATION-15-09-2026.tsv)
(4,139 rows = 4,112 + 27) +
[`MW72-CLASSES-TIERA-STUBS-15-09-2026.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/MW72-CLASSES-TIERA-STUBS-15-09-2026.md) +
[`MW72-CLASSES-SPOTCHECK-30-15-09-2026.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/MW72-CLASSES-SPOTCHECK-30-15-09-2026.tsv).

| verdict | rows | meaning |
|---|--:|---|
| `confirmed-missing` | 3,384 | no exact/stem/fold hit anywhere in MW99 — omission stands; 1,140 of these corroborate ≥2 of 36 Cologne dicts (Tier A) |
| `covered-by-MW-stem-form` | 460 | MW99 carries the same stemkey headword |
| `covered-by-fold-twin-flagged` | 264 | MW99 carries a case/vowel-length twin (Akalita/akalita trap) — needs eyes |
| `dropped-between-editions` | 27 | all 27 dropped rows, fixed editorial note (§3) |
| `anomaly-exact-hit-in-mw99` | 4 | baseline TSV said never-seen but the headword is exact-present in `mw.txt` — flagged for a baseline-extraction re-check, not filed |

**Canary — kAritra:** `confirmed-missing`, pointers `pw L620963` (`pw.txt` physical
line of its `<L>` tag `216013`, `7-331-d`) / `pwkvn L53131` (`pwkvn.txt`
physical line, tag `16013`) / `bhs L4759` (`bhs.txt` `<L>` tag value — `bhs`
physical line is 19108, a different numbering convention from `pw`/`pwkvn`,
both verified against the raw files) / `MAHĀVY 245. 844` (two citations in the
same PW body: an inline `MAHĀVY. 245` and a second sense via
`<ls n="MAHĀVY.">844</ls>` with no inline prefix — both regex patterns are
needed, an earlier pass caught only the first and mis-reported `245`).

**30-sample spot-check:** 0 false positives (every sampled `confirmed-missing`
row has `mw_exact_hit=0`, `mw_fold_hit=0`, `mw_stem_hit=0` against MW99) — under
the ≤1 bar.

**Caveat — `sch` dominance in corroboration:** `sch` (Schmidt's *Nachträge zum
Sanskrit-Wörterbuch*) appears in nearly every sampled `corr_dicts` cell; it is
one of the 36 corroboration dictionaries and, being itself a PW-Nachträge-era
supplement, is expected to overlap heavily with `sup_7` headwords. This
inflates `corr_n`/Tier-A membership toward `sch`-only corroboration — a
Tier-A row whose only corroborator is `sch` is weaker evidence than one
corroborated by two independent, later dictionaries; treat `corr_dicts` as a
ranked list, not a flat count, before any filing pass.

_Гасунс_
