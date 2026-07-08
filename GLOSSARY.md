# GLOSSARY — canonical Sanskrit-data terminology

_Created: 08-07-2026 · Last updated: 08-07-2026_

**Epistemic sibling of [`FINDINGS.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md).** FINDINGS holds facts; this file holds the act it cannot: **defining** the terms those facts are stated in. **It aggregates, it does not supersede** (MG ruling, 08-07-2026): each entry gathers where a term is already used/defined and states the working definition, but existing in-context definitions stand — an entry's job is "here is what this means and everywhere it appears," not "this overrides all other definitions." One of the seven epistemic registries minted under [H356](https://github.com/gasyoun/Uprava/blob/main/handoffs/H356-Opus_csl-corrections_epistemic-sibling-registries_08.07.26.md). Its infra twin is [`Uprava/GLOSSARY.md`](https://github.com/gasyoun/Uprava/blob/main/GLOSSARY.md).

**How to read an entry.** Each opens with the shared **importance dot** (🔴 3 · 🟠 2 · 🟡 1) — here rating **how costly the term is to get wrong** (🔴 = a confusion that has actually poisoned data). Then `Means:`, `Not:` (the common confusion to avoid), and `Canonical in:` (where the term is authoritative). Auto-assist only: token-frequency across the hubs *surfaces* undefined jargon; humans write the definitions.

---

### form_key
🔴 **Means:** a length-preserving normalization key for Sanskrit strings, used to join across schemes without losing distinctions (`ā`≠`a`).
**Not:** blanket NFD-decompose + strip-combining-marks — that destroys vowel length (`ā`→`a`) and retroflex (`ṣ`→`s`), and collides `ś`'s acute with the pitch mark (see [FINDINGS §36](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md#36-iast-unicode-collides-and-normalises-lossily); the abandoned path is [DEAD_ENDS §5](https://github.com/gasyoun/SanskritLexicography/blob/master/DEAD_ENDS.md)).
**Canonical in:** [`form_key` in sanskrit_util](https://github.com/sanskrit-lexicon/sanskrit-util/blob/main/py/sanskrit_util/__init__.py).

### headword vs lemma
🔴 **Means:** a *headword* is a dictionary entry key (`<L>`/`<k1>` in a CDSL dict); a *lemma* is a corpus dictionary-form assigned by a lemmatizer (DCS `LemmaId`).
**Not:** interchangeable — 18.6% of DCS lemmas have no CDSL headword at all (FINDINGS §12); they are keyed and populated independently (see [ASSUMPTIONS §1](https://github.com/gasyoun/SanskritLexicography/blob/master/ASSUMPTIONS.md)).
**Canonical in:** [FINDINGS §12](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md#12-a-fifth-of-dcs-lemmas-have-no-cdsl-headword) · [union_headwords.tsv](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/union/union_headwords.tsv).

### homonym index
🔴 **Means:** the ordinal on repeated identical headwords (`1 √as`, `2 √as`); a dict's giant verb root frequently sits at a non-zero index.
**Not:** guaranteed to be 0 for the "main" sense — 19 of the top-50 freq roots have a giant homonym at index > 0 (FINDINGS §16); iterate all records, never `bufs[0]` ([ASSUMPTIONS §3](https://github.com/gasyoun/SanskritLexicography/blob/master/ASSUMPTIONS.md)).
**Canonical in:** [FINDINGS §16](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md#16-giant-verb-roots-sit-at-non-zero-homonym-indexes).

### ls source map
🟠 **Means:** `ls_source_map.json` / `ls_resolver.py` — the mapping from a PWG `<ls>` citation siglum to a dated primary source (and its scanned-edition page URL).
**Not:** complete — recognises 72.4% of PWG `<ls>` keys (45 dated sources); the unrecognised 27.6% is late catalogues/secondary literature (FINDINGS §20). Also not a fold-key: sigla families bundle several works (§45).
**Canonical in:** [FINDINGS §20](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md#20-the-ls-source-map-recognises-724-percent-of-pwg-citations) · tool `ls_resolver.py`.

### gaṇa
🟠 **Means:** a Pāṇinian verb present-class group (bhvādi = class 1, tudādi = class 6, …); the axis on which some homonym roots split.
**Not:** recoverable from an unaccented corpus — only 5 of 38 DCS-lumped homonym groups are gaṇa-splittable; class I vs VI needs pitch accent the corpus lacks (FINDINGS §2, §8).
**Canonical in:** [FINDINGS §2](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md#2-homonym-token-splitting-has-a-hard-morphological-ceiling) · vidyut dhātupāṭha.

### Renou period-state
🟠 **Means:** a diachronic era tag I–V (Vedic → late) assigned per entry from multi-signal evidence (`ls`/`dcs`/`bhs`/`wl`), covering 770k entries in 8 dicts.
**Not:** reliable on high-frequency closed-class words — DCS homograph collapse gives `ca`/`idam` the union of all their homographs' eras (spuriously broad); apply a min-support gate (FINDINGS §14).
**Canonical in:** [`RENOU.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/RENOU.md).

### varga
🟠 **Means:** a consonant series (5 groups: guttural/palatal/cerebral/dental/labial) aggregating the 25 sparśa varṇas; the unit of the DCS diachrony analysis.
**Not:** a phonetically shifting distribution over time — series composition is near epoch-stable (Cramér's V = 0.037 across ~2 kyr); p-values carry no signal at DCS scale (FINDINGS §62).
**Canonical in:** [FINDINGS §62](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md#62-varga-distribution-is-almost-epoch-stable-cramérs-v--0037--and-the-gasūns-2014-dissertation-prose-read-its-own-χ²-table-backwards) · manifest `varga-series-diachrony`.

### SLP1 vs IAST
🔴 **Means:** two transliteration schemes — SLP1 (ASCII-safe, one char per phoneme, native PWG `key1` join key) and IAST (diacritic Unicode).
**Not:** interchangeable in DCS-derived files — `dcs_lemma_summary.json` is SLP1-keyed, `dcs_lemma_renou.json` is IAST-keyed; a join must transcode one side (FINDINGS §7; [ASSUMPTIONS §2](https://github.com/gasyoun/SanskritLexicography/blob/master/ASSUMPTIONS.md)).
**Canonical in:** [FINDINGS §7](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md#7-dcs-lemma-data-is-keyed-in-two-transliterations) · transcoder in [`sanskrit-util`](https://github.com/sanskrit-lexicon/sanskrit-util).

### key1 vs key2
🟠 **Means:** `key1` is a dictionary's computational/normalized headword key (join on this); `key2` is the printed form, carrying the udātta `/` accent mark in PWG (`agni/` = agní).
**Not:** cross-dict-joinable via `key2` — the same lemma keys differently between dicts (MW bare stem `agni` vs Apte nominative `agniH`); always join on `key1` (FINDINGS §23).
**Canonical in:** [FINDINGS §23](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md#23-apte-is-three-dictionaries-keys-differ-stem-vs-nominative).

### Zaliznyak index (a–f accent axis)
🟡 **Means:** a compact per-word grammar token scheme (335 tokens over 98,639 PWG headwords) plus a Vedic accent-mobility axis (a–f schemes) encoded from Whitney's declension rules.
**Not:** a proven translation aid — a blind A/B showed injecting the grammar token does NOT improve DE→RU translation, so it stays structured-data-only (FINDINGS §4); the accent axis is Vedic-only (Classical entries lack `/`).
**Canonical in:** [`ZALIZNYAK_INDEX.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/ZALIZNYAK_INDEX.md) · manifest `zaliznyak-grammar-index`.

### `<ls>` / iti register
🟠 **Means:** the two ways dictionaries cite sources — Western `<ls>` markup tags (PWG/MW) vs the indigenous `iti`/quotation register (SKD/VCP/KRM).
**Not:** comparable by a raw `<ls>` counter — SKD's ~80k citations, KRM's densest-in-corpus 6.00/entry all score zero under an `<ls>` detector; and a "space-preceded" `iti` counter hides `<s>iti` (~2/3 of KRM's citations). Control for register before ranking (FINDINGS §26).
**Canonical in:** [FINDINGS §26](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md#26-citation-density-is-register-bound-not-comparable-raw).

### dhātupāṭha citation form
🟠 **Means:** the canonical listing form of a verbal root in the Pāṇinian root-catalogue, used as the normalization target (CANON) for root-recovery joins.
**Not:** the same as vidyut's surface forms (which keep the thematic `-a` and must NOT seed CANON), nor a stem grab (`sada` for `sad`) — normalize to citation form before comparing; grep vidyut as `ancu`, not SLP1 `aYc`, and strip anubandha `~ \ ^` (§63).
**Canonical in:** [`mw_roots.tsv`](https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/mw/mw_roots.tsv) · [FINDINGS §35](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md#35-root-recovery-tiers-err-on-root-form-not-identity).

---

_Dr. Mārcis Gasūns_
