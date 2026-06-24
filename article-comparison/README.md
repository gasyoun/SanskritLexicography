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
| **PD minimal + Russian** | `<w>.pd-min.ru.md` | Bilingual EN/RU sense skeleton + key supporting Sanskrit quotes with Russian translations. *(agni done as the reference word; others on request.)* |
| **Full verbatim** | `<w>.verbatim.md` | Faithful raw `csl-orig` entries, every dictionary, full Cologne markup. The full PD is here. |
| **Full IAST** | `<w>.iast.md` | Same entries, SLP1→IAST transcoded, tags stripped. |

### agni — fire (non-samāsa)

[table](agni.table.md) · [pd-min](agni.pd-min.md) · [**pd-min + RU**](agni.pd-min.ru.md) · [verbatim](agni.verbatim.md) · [iast](agni.iast.md)

### anya — other (non-samāsa)

[table](anya.table.md) · [pd-min](anya.pd-min.md) · [verbatim](anya.verbatim.md) · [iast](anya.iast.md)

### akṣara — imperishable / syllable (a-samāsa)

[table](aksara.table.md) · [pd-min](aksara.pd-min.md) · [verbatim](aksara.verbatim.md) · [iast](aksara.iast.md)

### ananta — endless / Viṣṇu (a-samāsa)

[table](ananta.table.md) · [pd-min](ananta.pd-min.md) · [verbatim](ananta.verbatim.md) · [iast](ananta.iast.md)

## Method

- **PD** = Deccan College *Encyclopaedic Dictionary of Sanskrit on Historical Principles* (unfinished; "a" coverage stops ~`apaca-`). All candidates were filtered to fall inside PD's wordlist — that is the real constraint, since every other CDSL dictionary has a complete "a".
- Keys matched on both **stem** (MW/PW style: `agni`) and **nominative citation form** (Apte/SKD style: `agniH`) so no dictionary is missed.
- **PD minimal mode** keeps only the `{@…@}` sense outline; the full PD (often the largest entry by an order of magnitude — `anya` ≈ 278 KB) stays in the verbatim/IAST files.
- **Russian** translations are drafts (Indological terminology aligned to Kochergina/Smirnov via the SamudraManthanam corpus); they need expert review before any reuse.
