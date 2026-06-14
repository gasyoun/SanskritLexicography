# HeadwordLists

Exported and derived **headword lists** for Cologne Digital Sanskrit Lexicon
(CDSL) dictionaries, plus cross-dictionary comparison files. Each list is one
headword per line, sorted, used for coverage analysis, deduplication, and
joining dictionaries against one another.

Encoding is **SLP1** in the `key1`/`key2` files (e.g. `aMSa`, `a/MSa`); the one
exception is [21562-huet-velthius.txt](21562-huet-velthius.txt), which is in
**Velthuis** transliteration (e.g. `a.mza` = aṃśa). All files are UTF-8.

## Naming scheme

```
{DICT}-unique-{key1|key2}-{N}.txt
```

- `{DICT}` — CDSL dictionary code (see table below).
- `key1` / `key2` — which headword key (see next section).
- `{N}` — **entry count**. Note: `wc -l` usually reports `N − 1` because the
  last line has no trailing newline; the filename count is the true number of
  entries.

Variant patterns:

| Pattern | Meaning |
|---|---|
| `{DICT}-fehlerhaft-{N}.txt` | German "erroneous" — entries flagged as problematic. **These hold full XML records, not bare headwords** (see [PWG-fehlerhaft-1661.txt](PWG-fehlerhaft-1661.txt), [PWK-fehlerhaft-2227.txt](PWK-fehlerhaft-2227.txt)). |
| `SCH-accents-IAST-{N}.txt` | Accented headwords in IAST rather than SLP1 ([SCH-accents-IAST-20247.txt](SCH-accents-IAST-20247.txt)). |
| `{N}-huet-velthius.txt` | Count as a **prefix**; Velthuis transliteration ([21562-huet-velthius.txt](21562-huet-velthius.txt)). |
| `mw-apte-mcdonell-hk.txt` | Aggregate cross-dictionary list in **Harvard-Kyoto**, MW ∪ Apte ∪ Macdonell (~202k lines) ([mw-apte-mcdonell-hk.txt](mw-apte-mcdonell-hk.txt)). |
| `sanhw1.xlsx` | 41 MB binary spreadsheet — **do not open in an editor**; load with a library. |

## key1 vs key2 — choose deliberately

- **key1** — normalized computational key. May not match any printed form; built
  for machine comparison. Use for **matching, dedup, joins**.
- **key2** — closer to the printed source; retains markers like `-`, `--`, `/`
  (accent), `°` (e.g. `a/MSa`, `a--kAra`, `aMSa°prakalpanA`). Use for
  **editorial review, citation, checking digitized text against the scan**.

Not every dictionary ships both: some have only `key2` here (e.g. BHS, BUR, CAE,
CCS, MD, SCH).

## Note on duplicates / versions

Two MW `key2` files are present — [MW-unique-key2-198220.txt](MW-unique-key2-198220.txt)
and [MW-unique-key2-198231.txt](MW-unique-key2-198231.txt) — differing by 11
entries (198220 vs 198231). They are two snapshots; confirm which is current
before relying on one.

## Encoding caveat — BOM is inconsistent

Some files carry a UTF-8 BOM and some do not (e.g.
[MW-unique-key1-193978.txt](MW-unique-key1-193978.txt) and the
huet-velthius file **have** a BOM; [MW-unique-key2-198220.txt](MW-unique-key2-198220.txt)
does **not**). Check `head -c 3 file | xxd` before transforming, and preserve the
file's existing BOM state on write. The org-level "no BOM" rule does **not** hold
in this directory.

## Dictionary codes present

Codes follow the **CDSL abbreviation scheme**; the canonical, authoritative
code→dictionary mapping is on the
[CDSL site](https://www.sanskrit-lexicon.uni-koeln.de/). Titles below were
cross-checked against that site and the org-level
[../../CLAUDE.md](../../CLAUDE.md) table.

| Code | Dictionary | Keys present here |
|---|---|---|
| AP  | Apte, Practical Sanskrit-English Dictionary (revised edition) | key1, key2 |
| BHS | Edgerton, Buddhist Hybrid Sanskrit Dictionary | key2 |
| BUR | Burnouf, Dictionnaire classique sanscrit-français | key2 |
| CAE | Cappeller, Sanskrit-English Dictionary | key2 |
| CCS | Cappeller, Sanskrit-Wörterbuch (Sanskrit→German; companion to CAE) | key2 |
| GRA | Grassmann, Wörterbuch zum Rig-Veda | key1, key2 |
| INM | Sörensen, An Index to the Names in the Mahābhārata | key2 |
| MD  | Macdonell, Sanskrit-English Dictionary | key2 |
| MW  | Monier-Williams, A Sanskrit-English Dictionary (1899) | key1, key2 (×2) |
| PD  | An Encyclopedic Dictionary of Sanskrit on Historical Principles (Deccan College, Poona) | key1, key2 |
| PWG | Böhtlingk & Roth, *Großes* Petersburger Wörterbuch | key1, key2, fehlerhaft |
| PWK | Böhtlingk, Sanskrit-Wörterbuch in kürzerer Fassung | key1, key2, fehlerhaft |
| SCH | Schmidt, Nachträge zum Sanskrit-Wörterbuch | key2, accents-IAST |
| SKD | Rādhākānta Deva, Śabdakalpadruma | key1, key2 |
| VCP | Tārānātha Tarkavācaspati, Vācaspatyam | key1, key2 |
| VEI | Macdonell & Keith, Vedic Index of Names and Subjects | key1, key2 |

## Entry points

1. `*-unique-key1-*.txt` — normalized matching, dedup, joins.
2. `*-unique-key2-*.txt` — print-form display, citation, scan checking.
3. [mw-apte-mcdonell-hk.txt](mw-apte-mcdonell-hk.txt) — ready-made comparison
   across three major dictionary traditions.
