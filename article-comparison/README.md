# "a-" article comparison across CDSL dictionaries

Single-headword comparison of one **non-samāsa** and one **a-samāsa (nañ-privative)** word, each present in the unfinished Deccan **PD** dictionary (the binding constraint) and near-universally across the CDSL corpus.

Frequency ranking from **DCS 2026** (`dcs_full.sqlite`, 5.69 M tokens); article sizes from `csl-orig/v02`.

## Finalists

| Headword | Class | Gloss | Dicts | Senses (PD) |
|----------|-------|-------|------:|------:|
| **agni** | non-samāsa | fire | 20 | 130 |
| **anya** | non-samāsa | other | 19 | 77 |
| **akṣara** | a-samāsa (nañ) | imperishable / syllable | 19 | 55 |
| **ananta** | a-samāsa (nañ) | endless / Viṣṇu, Śeṣa | 18 | 102 |

## Files per word

| View | Pattern | What it is |
|------|---------|------------|
| **Side-by-side table** | `<w>.table.md` | All dictionaries in one table, condensed (citations stripped, SLP1→IAST). PD shown as its sense skeleton. The comparison overview. |
| **PD minimal mode** | `<w>.pd-min.md` | PD definition outline only — `{@…@}` sense markers, no etymology/citation bulk. |
| **PD minimal + Russian** | `<w>.pd-min.ru.md` | Bilingual EN/RU sense skeleton **+ corpus-grounded Russian**: attested-rendering distribution from the DeepSeek word-alignment lexicon, and real verse pairs (Sanskrit + published Russian). Done for all four. |
| **Corpus RU fragment** | `<w>.corpus-ru.md` | Standalone corpus section (the per-word attested-RU table + verse pairs) embedded into `pd-min.ru.md`. |
| **Per-sense corpus RU** | `<w>.persense-ru.md` | The deepened view: each attested Russian rendering hung under the **specific PD sense** it supports (Russian-lemma ↔ Russian-gloss match + synonym/phrase/name rules). Coverage 88–99% of aligned occurrences. |
| **Full verbatim** | `<w>.verbatim.md` | Faithful raw `csl-orig` entries, every dictionary, full Cologne markup. The full PD is here. |
| **Full IAST** | `<w>.iast.md` | Same entries, SLP1→IAST transcoded, tags stripped. |

### agni — fire (non-samāsa)

[table](agni.table.md) · [pd-min](agni.pd-min.md) · [**pd-min + RU**](agni.pd-min.ru.md) · [corpus-ru](agni.corpus-ru.md) · [**per-sense**](agni.persense-ru.md) · [verbatim](agni.verbatim.md) · [iast](agni.iast.md)

### anya — other (non-samāsa)

[table](anya.table.md) · [pd-min](anya.pd-min.md) · [**pd-min + RU**](anya.pd-min.ru.md) · [corpus-ru](anya.corpus-ru.md) · [**per-sense**](anya.persense-ru.md) · [verbatim](anya.verbatim.md) · [iast](anya.iast.md)

### akṣara — imperishable / syllable (a-samāsa)

[table](aksara.table.md) · [pd-min](aksara.pd-min.md) · [**pd-min + RU**](aksara.pd-min.ru.md) · [corpus-ru](aksara.corpus-ru.md) · [**per-sense**](aksara.persense-ru.md) · [verbatim](aksara.verbatim.md) · [iast](aksara.iast.md)

### ananta — endless / Viṣṇu (a-samāsa)

[table](ananta.table.md) · [pd-min](ananta.pd-min.md) · [**pd-min + RU**](ananta.pd-min.ru.md) · [corpus-ru](ananta.corpus-ru.md) · [**per-sense**](ananta.persense-ru.md) · [verbatim](ananta.verbatim.md) · [iast](ananta.iast.md)

## Method

- **PD** = Deccan College *Encyclopaedic Dictionary of Sanskrit on Historical Principles* (unfinished; "a" coverage stops ~`apaca-`). All candidates were filtered to fall inside PD's wordlist — that is the real constraint, since every other CDSL dictionary has a complete "a".
- Keys matched on both **stem** (MW/PW style: `agni`) and **nominative citation form** (Apte/SKD style: `agniH`) so no dictionary is missed.
- **PD minimal mode** keeps only the `{@…@}` sense outline; the full PD (often the largest entry by an order of magnitude — `anya` ≈ 278 KB) stays in the verbatim/IAST files.
- **Russian, two layers.** (1) **Sense-skeleton glosses** — hand-authored drafts (Indological terminology aligned to Kochergina/Smirnov), need expert review. (2) **Corpus-grounded** — *not re-translated*: attested Russian renderings come from the **DeepSeek Sanskrit→Russian word-alignment lexicon** (`RussianTranslation/src/corpus_lexicon.jsonl`, 1.09 M aligned rows, built June 2026), and the verse pairs quote **published** academic translations (Elizarenkova RV/AV, academic Mahābhārata, Russian Gītās incl. the 1788 first edition) from the SamudraManthanam parallel corpus.
- The attested-rendering distributions are themselves a finding: `agni` splits Агни (theonym) vs огонь (common noun); `akṣara` splits слог (syllable) vs Непреходящее (Brahman); `ananta` splits бесконечный (adj.) vs Ананта (Śeṣa).
- **Per-sense attribution** (`*.persense-ru.md`) hangs each attested rendering under the PD sense it supports. Because the sense-skeleton already carries a Russian gloss, the match is **Russian-lemma ↔ Russian-gloss** (lemmatized with `pymorphy3`, reusing `corpus_harvest.lemma_key`), plus three rules: synonym normalization (нетленный/неразрушимый → непреходящий), phrase matching (multi-word renderings), and name-routing (theonyms → the deity sense). This maps **88–99%** of aligned occurrences; the unmapped residual (function-word/context leakage) is listed honestly per word. The harder synonym/paraphrase tail is the natural target for a Max-subscription LLM assignment pass.
