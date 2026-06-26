# Sanskrit–Catalan word list vs. the Cologne (CDSL) wordlists

**File analysed:** [`61267-Sanskrit-Catalan-Words-List.txt`](61267-Sanskrit-Catalan-Words-List.txt) (mirrored here from the `sanskrit-lexicon/CORRECTIONS` repo)
**Source work:** *Diccionari Sànscrit–Català* (Òscar Pujol, Enciclopèdia Catalana, 2005 — the first Sanskrit→Catalan dictionary)
**Date:** 2026-06-25 · analysis scripts: [`coverage_by_dict.py`](coverage_by_dict.py), [`match_rate.py`](match_rate.py), [`make_uncovered_lists.py`](make_uncovered_lists.py)

---

## 1. What the file is

A flat headword index — **one Sanskrit lemma per line, 61,266 lines, UTF-8 *with* BOM** (`EF BB BF`). It is *not* a correction/change file and does not follow the `updateByLine.py` paired-line format; it is a raw lemma list, presumably the headword spine of the Catalan dictionary exported for cross-linking into CDSL.

The lemmas are written in **accented IAST** with an editorial segmentation layer that is the list's signature:

| Convention | Example in file | Meaning |
|---|---|---|
| `√` prefix marks a verbal root | `√aṃś`, `√hve`, `√pic` | 4,950 entries contain `√` (1,561 are bare root headwords) |
| Vedic **udātta accent** kept on vowels | `áṃśa-`, `aṃśu-mát-`, `grāma-ṇī́-` | 3,947 entries carry a vowel accent |
| **Internal hyphens** segment compound members and prefix+root | `aṃśa-karaṇa-`, `vy-ava-√dhāv`, `saṃ-√yuj` | morphological analysis, ~50 % of entries |
| **Trailing hyphen** = nominal stem form | `aṃśa-`, `akampita-` | lemma cited in stem (not nominative) |
| Homograph numbering | `a-1`, `a2`, `a-3`, `áṃsa-1` | distinguishes homonyms |

The accent + stem-hyphen + `√` style is the **Petersburg / Monier-Williams** lexicographic convention; the internal-hyphen compound segmentation is **Pujol's own editorial layer** and is *not* present in any Cologne headword key.

## 2. How it relates to the Cologne wordlists

### Method
Each Catalan lemma was normalised to a comparable key — strip `√`, trailing digits, parentheticals, Vedic accents and all hyphens (so compounds join the way CDSL stores them), then transcode IAST→SLP1 with [`sanskrit-util`](https://github.com/sanskrit-lexicon/sanskrit-util) and strip SLP1 accent marks. The same accent-stripped key was extracted from the `<k1>` field of each Cologne dictionary in [`csl-orig/v02`](https://github.com/sanskrit-lexicon/csl-orig/tree/master/v02). Comparison is therefore **accent- and compound-insensitive** — a pure lemma-identity match.

> ⚠️ Two transcoding traps were hit and fixed: (a) the file's apparent leading `1\t` numbers are added by the editor's line display — the real file has **no** numbers; (b) `ś` = `s`+U+0301 collides with the combining acute, so stripping accents *before* transcoding silently turned every `ś`→`s`. Both corrected → match rate rose 78 %→**89 %**.

### Result — the list is essentially a subset of Monier-Williams

Greedy marginal coverage of the 59,377 unique normalised Catalan keys:

| Dictionary | New lemmas it adds | Cumulative | Cum. % of Catalan list |
|---|---:|---:|---:|
| **MW** (Monier-Williams 1899) | 52,536 | 52,536 | **88.5 %** |
| PW (Petersburg, shorter) | 834 | 53,370 | 89.9 % |
| VCP (Vācaspatya) | 236 | 53,606 | 90.3 % |
| AP90 (Apte 1890) | 166 | 53,772 | 90.6 % |
| SHS, CAE, MW72, BUR, YAT, PWG, BEN, BOR, WIL, GRA | +193 total | 54,016 | **91.0 %** |
| *uncovered by any CDSL dictionary* | — | 5,361 | **9.0 %** |

Per-dictionary coverage of the Catalan list (independent, not marginal):

| Dict | `<k1>` keys | Catalan lemmas found | % of Catalan covered | % of that dict used |
|---|---:|---:|---:|---:|
| MW | 194,084 | ~52,700 | **88.8 %** | 13 % |
| PW | 151,346 | — | 76 % | — |
| PWG | 106,080 | — | 71 % | — |
| MW72 | 51,159 | — | 64 % | 31 % |

### Reading the numbers
- **Monier-Williams is the source.** MW alone accounts for 88.5 % of the headwords, and adding *every other* CDSL dictionary lifts coverage only to 91.0 %. No second dictionary makes a meaningful marginal contribution (PW adds <1.5 %). This is consistent with the *Diccionari Sànscrit–Català* being built on the MW headword spine — the standard practice for a new bilingual Sanskrit dictionary.
- **The list is MW shrunk by ~3×.** 61 k lemmas vs MW's 194 k `<k1>` keys (which include sub-entries): Pujol kept ~13 % of MW's key set — a curated, pedagogically-weighted selection rather than the full corpus.
- **The remaining ~8 % are *not* in any CDSL dictionary.** Against the full set of **43** CDSL dictionaries (not just the 15 above), **4,670 unique keys / 4,680 headwords (7.9 %)** stay unmatched. The complete categorised list is in [`Catalan-uncovered-by-CDSL.txt`](Catalan-uncovered-by-CDSL.txt); see §4 below for the breakdown.

## 3. Practical implications for CDSL

1. **Cross-linking is cheap and high-yield.** ~91 % of Catalan lemmas map 1:1 onto an existing CDSL `<k1>` (overwhelmingly MW), so a Sanskrit→Catalan gloss layer could be wired into the CDSL frontend keyed on the MW headword with almost no fuzzy matching.
2. **The 4,680 unmatched lemmas are a free QA list** — split them into (a) likely typos to feed back to the Catalan editors and (b) candidate *new* headwords / compound-segmentation cases worth surfacing to MW maintainers (see §4).
3. **The hyphen-segmentation layer is unique value.** Pujol's compound and prefix+root segmentation (`vy-ava-√dhāv`) is information CDSL's flat `<k1>` keys lack; if licensing permits, it is the one thing this list adds *back* to the Cologne data, not just consumes from it.
4. **Encoding caveat for any pipeline:** the file has a UTF-8 **BOM** (the CDSL `csl-orig` convention is BOM-free) and uses precomposed accented IAST where `ś` decomposes onto the accent codepoint — normalise length/retroflex *and* transcode before stripping accents.

## 4. The CDSL-uncovered words — what they are

Matching the 59,377 normalised keys against `<k1>` of **all 43** CDSL dictionaries leaves **4,680 headwords (7.9 %)** unaccounted for. The complete list lives **one file per category** under [`Catalan-uncovered/`](Catalan-uncovered/) (each a Markdown table of headword + normalised SLP1 key); a single combined dump is in [`Catalan-uncovered-by-CDSL.txt`](Catalan-uncovered-by-CDSL.txt). All generated by [`make_uncovered_lists.py`](make_uncovered_lists.py).

| Category | Count | Per-category file | What it is |
|---|---:|---|---|
| `compound(2)` | 2,397 | [`02-compound-2.md`](Catalan-uncovered/02-compound-2.md) | Two-member compounds written solid (sandhi-joined), MW lists only under a parent or not at all |
| `simple` | 1,421 | [`01-simple.md`](Catalan-uncovered/01-simple.md) | Single rare derivatives, variant spellings, and solid sandhi-forms |
| `long-compound(3+)` | 600 | [`03-long-compound-3plus.md`](Catalan-uncovered/03-long-compound-3plus.md) | Three-plus-member compounds — heavily **Vedānta / philosophical** vocabulary |
| `suspect-char` | 126 | [`00-suspect-char.md`](Catalan-uncovered/00-suspect-char.md) | File artifacts, **not real missing words** (see below) |
| `prefixed-root` | 107 | [`05-prefixed-root.md`](Catalan-uncovered/05-prefixed-root.md) | Preverb + root combinations (`abhi-saṃ-ā-√gam`) not headworded as roots in CDSL |
| `root` | 29 | [`04-root.md`](Catalan-uncovered/04-root.md) | **Denominative / causative roots** (`√nāthaya`, `√dolaya`, `√kuṇṭh`) Cologne/Whitney don't list as roots |

**The four real groups:**

1. **Compounds MW doesn't headword (≈64 %, the 2- + 3-member rows).** The bulk. Sanskrit compounds are productive, so any dictionary headwords only a selection; Pujol included solid compounds — especially **Advaita-Vedānta technical terms** — that MW buries under a parent lemma or omits: `ātmaikya-bodha-` (knowledge of Self-unity), `bhūtendriyātmaka-` (consisting of elements and senses), `ātmānātma-vivecana-` (discrimination of Self/non-Self), `pretya-saṃbhava-`, `viśuddha-vijñāna-ghana-`. These are *genuine lexical content*, not noise.

2. **Rare simple derivatives & variant spellings (≈30 %).** Confirmed genuinely absent from MW even though their neighbours are present: `āmraka-` (MW has 20+ `āmra-` compounds but not this *-ka* diminutive), `bhikṣāśana-` (MW has `bhikṣāśin-` but not the *-ana* noun), `ārṇa-` (MW has `ārṇava-`). Plus orthographic variants (`bhavaniya-` for *bhavanīya-*) and a few truncated stem fragments (`bhūty-`, `bhakty-`, `bhej-`).

3. **Denominative & prefixed roots (136).** Pujol headwords denominative/causative verbs *as roots* — `√nāthaya` (to seek aid), `√dolaya` (to swing), `√pīyūṣaya`, `√svargāya` — and lists preverb+root strings (`abhi-pari-√svañj`, `bhasma-sād-√bhū`) that CDSL keeps only inside MW entries, never as separate `<k1>` keys. A real difference in lemmatisation policy, not a gap.

4. **File artifacts (126 `suspect-char` — discard these).** Mojibake/markup that leaked into the export: stray leading symbols (`˜ pra-√kāṅkṣ`, `• pūrva-jāti-`, `.asac-chāstra-`, `§pratikṛti-`), a spurious leading **`U`** on a block of prefixed roots (`Upari-√pracch`, `Uprati-saṃ-√grah`), abbreviated cross-reference stubs ending in a bullet (`abhi-√p•`, `ati-√t•`), periphrastic notation kept inline (`bhasmāvaśeṣam + √kṛ`, `cūrṇa-śas + √kṛ`), and parenthetical residue (`apunar-āvṛtti-).`). These are the **first thing to feed back to the Catalan editors** as encoding clean-up.

**Bottom line:** of the ~4,680 uncovered, the large majority (groups 1–3, ~4,550) are *real* — unselected compounds, rare derivatives, and denominative roots that reflect Pujol's editorial choices, especially a strong Vedānta-philosophical layer. Only ~126 are genuine file noise.

## 5. Corpus reality check — vs the DCS

§2–4 ask *"is each lemma in a CDSL **dictionary**?"*. The orthogonal question is *"is it actually **attested in texts**?"* — answered against the **Digital Corpus of Sanskrit** lemma index ([`VisualDCS/dcs_lemma_summary.json`](https://github.com/gasyoun/VisualDCS), DCS-2021, 83,239 lemmas, frequency-banded 1–5), the same index the `pwg_ru` frequency pipeline uses. Script: [`coverage_vs_dcs.py`](coverage_vs_dcs.py); keys normalised identically to §2 so the three analyses line up.

| | share of the 59,377 Catalan keys |
|---|---:|
| Dictionary-covered (any of 15 CDSL dicts) | **91.0 %** |
| **DCS corpus-attested** | **46.4 %** |

So **less than half** the list is attested in the ~650-text DCS corpus, even though 91 % sits in a dictionary. By DCS frequency band: band 5 (most frequent) 671 · band 4 3,610 · band 3 8,944 · band 2 9,286 · band 1 5,020.

### Dictionary coverage × corpus attestation (the 2×2)

| | DCS-attested | not in DCS |
|---|---:|---:|
| **in a CDSL dict** | 27,354 (46.1 %) | **26,662 (44.9 %)** — *listed but unattested* |
| **in no CDSL dict** | **177 (0.3 %)** — *corpus-real CDSL gaps* | 5,184 (8.7 %) |

### Reading the numbers
- **Lexicographic "dark matter" dominates.** **44.9 %** of the list is in a CDSL dictionary yet never appears in the DCS corpus — the Catalan list inherits MW's long tail of rare/Vedic/grammarians' forms that the corpus doesn't sample. The dictionary spine is ~2× larger than corpus usage.
- **The 8.7 % "neither" corner** (in no dictionary *and* unattested) is where real noise + hapax compounds concentrate — the best-yield slice to send back to the Catalan editors (it subsumes most of §4's `suspect-char`).

### The 177 "corpus-attested but in no CDSL dictionary" — triaged

This corner is **not all convention** — it splits into convention/morphology vs genuine candidate gaps. The **complete categorised list of all 177** is in [`DCS-attested-no-CDSL.md`](DCS-attested-no-CDSL.md) (band-sorted, reproducible via [`coverage_vs_dcs.py`](coverage_vs_dcs.py)); summary triage:

| Type | n | Convention or gap? | Examples (Pujol form) |
|---|---:|---|---|
| Prefixed / denominative **verb roots** | 41 | **Convention** — DCS lemmatises preverb+root as a unit; CDSL stores under the simple root (§4 "prefixed-root" group, corpus-confirmed) | `namas-√kṛ`, `vy-ava-√sā`, `saṃ-pra-√dhāv`, `abhi-vi-√hā`, `√ilay`; desideratives `saṃjihīrṣā-`, `visisṛkṣā-` |
| Productive **-tā / -tva / -tara / -tama / -vat** | 9 | **Convention** — productive suffixes CDSL rarely headwords | `niścala-tā-`, `vaiśvātmya-`, `vikṛṣṭa-tara-`, `saṃpanna-tama-`, `aṅga-vat-` |
| **Bīja / mantra syllables** | 5 | **Convention** — CDSL doesn't headword bare seed-syllables | `laṃ`, `vaṃ`, `yaṃ`, `hiṃ`, `sauḥ` |
| Solid **compounds** | 29 | **Real, but expected** — MW systematically under-headwords compounds (= §4's bulk) | `gaja-vaktra-`, `amara-kāṣṭha-`, `ahaṃ-pratyaya-`, `arka-parṇī-`, `mahā-kadamba-` |
| **Simple lexemes / feminine-derivatives / variants** | ~93 | **Mixed** — many are productive feminines of a CDSL base (`ajitā-←ajita`, `vairiṇī-←vairin`, `vyāpinī-←vyāpin`); a genuine residue is corpus-attested **and absent from all 43 CDSL dictionaries** | gaps: `alasāndra-` (cowpea), `kustumburī-` (coriander), `kaṅkolī-`, `udumbarī-`, `kāṇḍekṣukā-`, `eḍikā-`, `pulkasī-`, `ṣiṅga-`, `alavaṇā-` |

- **So: ~55 (31 %) are pure lemmatisation/morphology convention** (verbs + productive suffixes + bīja). The remaining **~122 are nominal lexical content** — 29 unheadworded compounds plus the simple/feminine bucket — and within them a **genuine, corpus-confirmed residue of a few dozen rare lexemes (especially plant/animal/object names)** that no CDSL dictionary carries. *These* are the highest-value candidate additions: unlike §4's dictionary-only uncovered list, they are independently **attested in real texts**.

> ⚠️ DCS lemmatisation differs from CDSL headwording (it splits/joins preverbs and resolves sandhi its own way), so corpus *non-attestation* of a key is a soft signal, not proof a word is unused — a few percent is lemmatisation drift, not genuine absence. Conversely, the verb/bīja/suffix rows above are *not* CDSL gaps.

## 6. Pujol's headword conventions

The list is in **accented IAST with an explicit morphological-analysis layer** — its signature, and the reason ~9 % of keys don't match a flat CDSL `<k1>` even when the word is present. Conventions observed (the normalisation in §2 strips all of these to recover the bare lemma):

| # | Convention | Marker | Example | CDSL equivalent |
|---|---|---|---|---|
| 1 | **Verbal root** marked | leading `√` | `√aṃś`, `√hve`, `√ilay` (denominative) | root stored bare; 4,950 entries carry `√`, 1,561 are bare-root headwords |
| 2 | **Preverb + root** fully segmented, `√` on the final root | hyphen chain + `√` | `vy-ava-√sā`, `saṃ-pra-√dhāv`, `abhi-vi-√hā` | listed under the *simple* root only → these miss `<k1>` |
| 3 | **Sandhi / analysis resolved** in parentheses | `(…)` after the headword | `saṃ-pra-√ṇaś (√naś)`, `anu-vi-√ṣad (vi2+√sad1)`, `saṃprārth (pra+√arth)` | gives the underlying root CDSL keys on |
| 4 | **Vedic udātta accent** kept on vowels | acute over a vowel | `áṃśa-`, `viṣā́ṇā-`, `grāma-ṇī́-` | 3,947 accented; CDSL `<k1>` is accent-free → strip before matching |
| 5 | **Compound members segmented** | internal `-` | `aṃśa-karaṇa-`, `ahaṃ-pratyaya-`, `amara-kāṣṭha-` | CDSL stores compounds solid → join hyphens before matching |
| 6 | **Nominal stem citation** | trailing `-` | `āmraka-`, `akampita-` (not `āmrakaḥ`) | CDSL `<k1>` is also stem-form |
| 7 | **Productive suffixes shown as a final member** | `-tā`, `-tva`, `-tara`, `-tama`, `-vat`, `-ka` | `niścala-tā-`, `vikṛṣṭa-tara-`, `aṅga-vat-` | usually not separately headworded by CDSL |
| 8 | **Feminine / derivative stems** given their own line | `-ā`, `-ī`, `-inī` headwords | `ajitā-`, `vairiṇī-`, `vyāpinī-` | CDSL often subsumes these under the masculine base |
| 9 | **Homograph numbering** (style inconsistent) | trailing/medial digit | `a-1`, `a2`, `a-3`, `áṃsa-1`, `nirmūlya1 / nirmūlya-2` | CDSL uses its own homonym numbering |
| 10 | **Bīja / mantra syllables** headworded | bare syllable | `laṃ`, `vaṃ`, `yaṃ`, `hiṃ`, `sauḥ` | CDSL doesn't headword bare seed-syllables |
| 11 | **Encoding** | UTF-8 **with BOM**; precomposed accented IAST | `ś` = `s` + U+0301 (collides with the acute accent) | csl-orig is BOM-free; normalise length/retroflex *then* transcode *then* strip accents (see the §2 trap) |
| — | **File-export artifacts** (not a convention) | leading `˜ • § U`, trailing `•`, inline `+ √kṛ` | `§pratikṛti-`, `Upari-√pracch`, `abhi-√p•` | noise to clean up; see §4 group 4 |

**Practical upshot:** conventions 1–3, 5, 7–8 and 10 are exactly why a word present in CDSL can still miss the flat-key match, and why the §5 "corpus-attested, no-dict" corner is dominated by verb/suffix/bīja convention rather than true gaps. To match Pujol against any CDSL or corpus key set: drop `√`, parentheticals and trailing digits; join internal hyphens; transcode IAST→SLP1; then strip SLP1 accents (in that order).

## 7. Do Pujol's accents agree with Cologne's?

**The notation differs; the placement mostly agrees.** Pujol marks the udātta with a **combining acute on the vowel** in IAST (`áṃśa-`, `viṣā́ṇā-`); Cologne marks it with a **`/` after the accented vowel** in SLP1 `<k2>` (`a/MSa`). Comparing accent *position* as a vowel ordinal (1 = first vowel), on lemmas accented on both sides — matching against **any** accent-variant of a key so homographs like *bhara*/*bhárā* aren't falsely counted as conflicts (script: [`accent_compare.py`](accent_compare.py)):

| vs dict | both-accented shared lemmas | **same position** | differ | accented in Pujol only | accented in dict only |
|---|--:|--:|--:|--:|--:|
| **GRA** (Grassmann RV) | 1,023 | **991 = 96.9 %** | 32 | 46 | 242 |
| **MW** | 1,611 | **1,564 = 97.1 %** | 47 | 534 | 524 |

- **~97 % place the udātta on the same vowel** — Pujol's accentuation is essentially the standard Vedic/MW accent, just in a different notation.
- **Coverage is selective and asymmetric.** Pujol accents ~11,535 lemmas total (mostly the Vedic stratum); GRA accents 242 shared lemmas Pujol leaves bare, and against MW each side accents ~520 the other doesn't. So Pujol is *not* an exhaustive accent source — absence of a Pujol accent ≠ the word is unaccented.
- **~3 % genuine position disagreements** (32 vs GRA, 47 vs MW). Spot-checked, these are real notation/analysis differences, and where they conflict with the Rigveda the **Cologne/GRA reading is generally the canonical one** — e.g. `bhaga` Pujol vowel 2 vs GRA vowel 1 (RV *bhága*, first-syllable udātta), `amatra` Pujol 3 vs GRA/MW 1, `dvāra` Pujol 1 vs 2. A useful small QA list to send back to the Catalan editors (full set reproducible via the script).

> Method caveat: positions are computed in SLP1 vowel-ordinal space; diphthong/transcoding edge cases and the any-variant match mean the ~3 % is an *upper-ish* bound on real conflicts, not an exact error count.

---

*Counts: 61,266 lemmas → 59,377 unique normalised keys; 4,950 with `√`, 3,947 vowel-accented (≈11,535 carry an accent counting all variants). Matching is accent- and compound-insensitive lemma identity against `<k1>` of CDSL dictionaries in `csl-orig/v02` (15 for §2's greedy table, all 43 for §4's uncovered list) and against the DCS-2021 lemma index for §5; §7 compares accent position against the accented `<k2>` of GRA and MW.*
