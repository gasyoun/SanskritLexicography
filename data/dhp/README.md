# dhātu-pāṭha XML corpus layer — Westergaard + Scharf Mādhavīya

_Created: 11-09-2026 · Last updated: 11-09-2026_

Machine-readable dhātu-pāṭha corpus: **Westergaard's Dhātupāṭha** (Jim Funderburk's XML edition, 2009–2010) and the **Mādhavīya-Dhātupāṭha** (Scharf-camp XML), landed byte-exact from the emailed academic package (H4538).

## Provenance

| Fact | Value |
|---|---|
| Source | yadisk `Sanskrityatina/05_Sanskrit-Lexicon/Jim-Peter-emailed/` — subfolders `westwork/` (Westergaard) + `ScharfMDhP/` (Mādhavīya); fetched 11-09-2026 via `rclone` (auth H2303 WebDAV) |
| Lineage | `westwork/readme.txt`…`readme4.txt`: Jim Funderburk, Cologne `Lexical/Funderburk/Westergaard` work, Dec 2009 – Mar 2010 |
| Parity | every landed file SHA-256-verified against the fetched yadisk originals — [SHA256SUMS.txt](SHA256SUMS.txt) (`shasum -a 256 -c SHA256SUMS.txt`) |
| Canonical copies | the yadisk originals remain canonical; this layer is a byte-exact mirror, never hand-edited |

## Rights note (license-gated ingest discipline)

Emailed academic files (Jim Funderburk / Peter Scharf circle → MG, via the «Jim-Peter-emailed» yadisk folder); source recorded once, here. Redistribution beyond research use is **pending rights confirmation — UNRESOLVED, recorded, not blocking** (MG 30-07-2026 ruling: rights uncertainty is not a stop, but must be recorded). Derived measurements (counts, crosswalks, indexes) are free (MG 07-09-2026 derived-only rule; this raw landing is the H4538-sanctioned exception for the emailed dhP package).

## Validation receipts (xmllint, libxml 2.9.13, 11-09-2026)

| File | Verdict |
|---|---|
| `westwork/WestergaardDhP.xml` | **DTD-VALID** — 0 errors vs `WestergaardDhP.dtd` |
| `westwork/wdp-mw.xml` | **DTD-VALID** — MW-linked variant |
| `ScharfMDhP/MadhaviyaDhP4.xml` | **DTD-VALID** — vs `MadhaviyaDhP3.dtd` |
| `westwork/WestergaardDhP1.xml` | **DTD-INVALID** — 1 949 validity errors, all ONE class: `No declaration for attribute msid of element root` (the enriched MW-crossref variant; the shipped DTD was never extended for its `msid` attributes). Landed byte-exact, deliberately not repaired — parity beats prettiness. |

Reproduce: `cd westwork && xmllint --noout --valid WestergaardDhP.xml && xmllint --noout --valid wdp-mw.xml && cd ../ScharfMDhP && xmllint --noout --valid MadhaviyaDhP4.xml` (the `DhP1` run exits 4 by design; count: `xmllint --noout --valid WestergaardDhP1.xml 2>&1 | grep -c 'validity error'`).

## Census (11-09-2026)

| File | Root element | Counts |
|---|---|---|
| `westwork/WestergaardDhP.xml` | `<wdpsections>` | 35 sections · 1 491 sutras · 1 985 `<root>` elements (1 982 distinct `wsid`) · 1 474 senses · 15 `mdproot` |
| `westwork/WestergaardDhP1.xml` | `<wdpsections>` | identical skeleton (35 / 1 491 / 1 985 / 1 982 / 1 474) + per-root `msid` MW cross-refs |
| `westwork/wdp-mw.xml` | `<wdpsections>` | identical skeleton + 16 `mdproot` (MW links) |
| `westwork/sutras.txt` | plain text | 1 637-line sutra index (msid · gaṇa · root · sense), e.g. `01.0001   2 BU sattAyAm` |
| `ScharfMDhP/MadhaviyaDhP4.xml` | `<MadhaviyaDhP3>` | 2 276 entries · 2 247 roots · 2 246 `fullDAtu`/`lemma` · 1 640 sūtras · 1 700 senseterms · 1 615 senses |

## Variant relationships

- `WestergaardDhP.xml` (base, DTD-valid) ↔ `WestergaardDhP1.xml` (same skeleton + undeclared `msid` attrs — the DTD-drift file) ↔ `wdp-mw.xml` (MW-linked, DTD-valid). All three carry the same 1 982-root Westergaard corpus.
- The Mādhavīya layer (`MadhaviyaDhP4.xml` + `MadhaviyaDhP3.dtd`) is a single self-consistent DTD-valid document: 2 247 roots with lemma/fullDAtu pairing and sūtra/senseterm apparatus.

## Adjacency (cross-links, not duplicates)

- [`helpmorphids.html`](https://github.com/gasyoun/SanskritLexicography/blob/master/helpmorphids.html) — already at repo root; **NOT re-landed** (H4477 §6 overlap verdict).
- FEATURES_INDEX L18 / L19 dhātupāṭha crosswalks (Palsule-hubbed, H1333/H4478) — this layer supplies the source XMLs behind the Westergaard and Mādhavīya witnesses.
- [H4479](https://github.com/gasyoun/Uprava/blob/main/handoffs/H4479-OxAlpha_SanskritGrammar_gasuns-dissertation-corpus_09.09.26.md) (SanskritGrammar, MG PhD dhātu corpus) — adjacent lane, cross-linked not duplicated.

## Excluded (recorded, not landed)

- `__MACOSX/` Finder junk from the yadisk folder.
- `Archive/` (`roots.xml`, `roots-ids.xml`, `Whitney.txt` — an MW-roots archive: 1 022 roots / 4 070 groups / 19 333 forms, both XMLs well-formed) — outside the H4538 mission file list; left on yadisk, noted here for the next census.
- `mwverb/`, `whit-mw-html/` — Whitney/MW verb-coverage comparison residue, out of scope.

_Dr. Mārcis Gasūns_
