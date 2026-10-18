# ACC `<HI1>` flattening — work records with attribution (H6993 / H6989 S2)

_Created: 18-10-2026 · Executor: DeepSeek v4.1 Flash (`deepseek/deepseek-flash`) · Source: `csl-orig/v02/acc/acc.txt` (8,168,907 B, read-only) + committed `acc.jsonl`_

## What this is

`acc_works_flat.tsv` promotes the ACC `<HI1>` work layer to first-class work
records. One row is a **(work, ACC filing)** pair; a filing that lists the same
work twice (or a work plus its commentary notes) is one row with
`hi1_count > 1`. The parent ACC record is the source locator
(`acc_record_id` + `source_line_span`), and the parent filing supplies the
author/school attribution.

The script `flatten_acc_hi1.py` is stdlib-only and deterministic. It reuses
the committed `parse_acc.py` record model (`acc_L`, `pc_scan`, `k1`, `k2`) and
reads `acc.txt` only for the `<HI1>` line structure that `acc.jsonl` strips.

## Reconciliation (both sides printed)

| Measure | Measured | Quoted baseline | Delta |
|---|---:|---:|---:|
| ACC filings with `<HI1>` | **11,436** | 11,433 (C3 / grill Q12) | **+3** |
| `<HI1>` lines | **26,982** | 26,982 | 0 |
| `sum(hi1_count)` over work rows | **26,982** | 26,982 | 0 |
| `unattributed_hi1.tsv` rows | **0** | — | — |
| `sum(hi1_count) + unattributed` | **26,982** | 26,982 | **PASS** |
| `distinct(acc_record_id)` in `acc_works_flat.tsv` | **11,436** | 11,433 | +3 |
| Work rows | **23,509** | — | — |
| Distinct work keys | **20,634** | — | — |

**The +3 is a counting delta, not dropped data.** A raw parse of the pinned
source finds 11,436 filings with at least one line-initial `<HI1>` (no
malformed headers, no duplicate `L` ids, 26,982 lines exactly). The C3 sweep's
prose says 11,433. Every one of the 11,436 filings has at least one work row
and all 26,982 lines are counted exactly once; no line is silently dropped.
The verifier should treat 11,436 as the measured figure and reconcile the
prose 11,433 before quoting it again.

## Records-per-work distribution

Number of ACC filings that carry the same normalized work title:

| filings per work | works |
|---:|---:|
| 1 | 18,885 |
| 2 | 1,195 |
| 3 | 358 |
| 4 | 103 |
| 5 | 42 |
| 6 | 20 |
| 7 | 10 |
| 8 | 8 |
| 9 | 3 |
| 10 | 1 |
| 11 | 1 |
| 12 | 2 |
| 13 | 1 |
| 18 | 1 |
| 26 | 2 |
| 29 | 1 |
| 100 | 1 |

The long tail is the homograph problem C3 §1 named: e.g. `Dīpikā by
Nārāyaṇa` (100 filings), `Śrautasūtra` (29), `Dīpikā` (28), `Gṛhyasūtra`
(26). Short titles are disambiguated by the filing authority in the work key
(`len(title_norm.split()) <= 2`), so two schools' `Śrautasūtra` do not
silently merge; longer titles are keyed on the title alone.

## Author / school attribution coverage (counts, not adjectives)

Provenance is a column value, never a guessed string: `printed` = an explicit
relation/subject phrase in the filing, `inferred` = the filing headword's
person suffix with no prose, `blank` = no basis.

| Basis | Work rows | Share |
|---|---:|---:|
| printed | **14,941** | 63.6 % |
| inferred | **2,313** | 9.8 % |
| blank | **6,255** | 26.6 % |
| **total** | **23,509** | 100 % |

| Column | Rows populated | Coverage |
|---|---:|---:|
| `author` | 13,333 | 56.7 % |
| `school` | 7,933 | 33.7 % |
| author **or** school | 15,402 | 65.5 % |

Blank rows are mostly work-title filings whose `<HI1>` children are
commentaries or sub-works; the parent headword is a title, not a person, and
no author is printed in the filing. They are left blank on purpose.

## 164 top-title / 774 check — delta against the pre-flatten surface

The check reuses the C3 two-sided fold (parentheticals stripped; diacritics,
vowel length, aspirates and retroflexes flattened). It reproduces the C3
baseline exactly: **122 of 164** PD hand-adjudicated primary titles match an
ACC `<k1>` headword.

| Surface | PD titles matched (of 164) |
|---|---:|
| Pre-flatten ACC `<k1>` record surface | **122** |
| Flattened `<HI1>` work surface | **94** |
| Union (record headword **or** `<HI1>` work) | **127** |
| **Recovered by flattening** | **+5** |

The five titles that were invisible on the record surface and became joinable
only after flattening: `Bṛhadāraṇyakopaniṣadbhāṣya (Śaṅkara)`,
`Chāndogyopaniṣadbhāṣya (Śaṅkara)`, `Yogasūtrabhāṣya`,
`Sāṃkhyatattvakaumudī`, `Sāṃkhyakārikābhāṣya`.

**On the 774.** The grill quotes 774 as the pre-flatten top-title list size.
Re-measuring the committed P2 verdicts (`p2_agent_verdicts.jsonl.gz`, 920
approved rows) gives **796 distinct ACC filings**, not 774. The 774 figure is
kept as the quoted baseline and flagged **interim, AOB denominator**; it is
not silently overwritten by 796. The flatten delta above is measured on the
164 titles, which is the stable side of the check.

## Reproducibility

```
python flatten_acc_hi1.py --acc-txt acc.txt --acc-jsonl acc.jsonl --out-dir .
python top_title_check.py
```

Two consecutive runs diff clean (byte-identical `acc_works_flat.tsv`,
`unattributed_hi1.tsv`, `flatten_stats.json`, `top_title_check.json`).

## Risks / unknowns

- **Commentary attachment.** A `<HI1>` line with no independent title (e.g.
  `C. by X`, `C. Oppert 2759`) is attached to the preceding work in the same
  filing; if there is no preceding work, the filing headword becomes the base
  work. This is the only way to satisfy "no line dropped" without inventing a
  title, but it means a commentary can raise its base work's `hi1_count`.
- **Author-vs-title ambiguity.** ACC files works under authors and authors
  under works; `printed`/`inferred`/`blank` records the evidence, not a
  disambiguation verdict.
- **Short-title disambiguation is title+author only.** It does not use
  chronology or manuscript witnesses.
- **774 is stale.** The committed P2 artifact supports 796; the grill number
  is retained as a flagged interim quote, not a census.
- `acc.jsonl` was not edited; `acc.txt` is never committed (csl-orig fence).

## Files

- `flatten_acc_hi1.py` — deterministic flattener (stdlib).
- `acc_works_flat.tsv` — 23,509 work rows / 20,634 work keys.
- `unattributed_hi1.tsv` — header only (0 rows; every line is counted).
- `flatten_stats.json` — machine-readable counts used above.
- `top_title_check.py` + `top_title_check.json` — 164/774 re-run.
- this report.

_Dr. Mārcis Gasūns_
