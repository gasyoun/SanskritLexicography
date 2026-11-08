# PD — *An Encyclopaedic Dictionary of Sanskrit on Historical Principles*

_Created: 24-06-2026 · Last updated: 11-07-2026_

**PD** (CDSL code) = the **Deccan College** *Encyclopaedic Dictionary of Sanskrit on
Historical Principles* — not a bilingual gloss dictionary but a large historical
thesaurus that arranges each word's senses **in chronological order of attestation**
(Ṛgveda → *Hāsyārṇava*, 1850 CE), citing the references for each.

- Conceived by **S. M. Katre (1948)**; first fascicle **1976** (opening «a»), first bound volume
  **1978** (gen. ed. **A. M. Ghatage**) — the sourced form per
  [PD_KNOWLEDGE_INDEX.md §2](https://github.com/gasyoun/Uprava/blob/main/papers/A68/PD_KNOWLEDGE_INDEX.md)
  (H7493, 30-10-2026; reconciles the «1976–2009» fascicle span in
  `corrections_draft/PD/readme.md` and the «PD 1976» chronology row in `.ai_state.md`).
- **~35 volumes** published so far, **~125,000 vocables**, built on a primary corpus of
  **1,469 Sanskrit treatises**. Still in progress — published volumes cover only the
  early part of the alphabet, so PD is **incomplete by design** (a multi-decade project).

## Digital editions / sources (two, per user 2026-06-24)

| | **CDSL — PDScan/2020** | **Digital KoshaSHRI** (2nd source, to add) |
|---|---|---|
| URL | [sanskrit-lexicon.uni-koeln.de … PDScan/2020](https://sanskrit-lexicon.uni-koeln.de/scans/PDScan/2020/web/index.php) | [koshashri-dc.ac.in](https://koshashri-dc.ac.in/) ([about](https://koshashri-dc.ac.in/about)) |
| Who | **Cologne (CDSL)** third-party scholarly digitization (Th. Malten et al.) | **Deccan College's own** portal (DST-funded, C-DAC Pune) — the **publisher/authority** |
| Format / openness | standard CDSL `<L>/<k1>/<k2>/<ls>` markup; **downloadable XML**, web app, APIs, cross-dict links — **plugs straight into the csl pipeline** | bespoke portal, **sign-in gated**, no bulk download; authoritative but not (yet) open data |
| Coverage *now* | the digitized published volumes — **currently more matter online** than KoshaSHRI | newer portal; **less matter exposed so far** (per observation 2026-06-24) |
| Growth | fixed snapshot of what was digitized | the **live editorial project** — grows as new volumes/edits land |

## Local copy — staging is per machine; re-stage with one command

**Staging state (30-10-2026, this machine): NOT STAGED.** `external_src/` is gitignored,
so machine migrations never carry it — the 30-10 PD estate audit found the sole local
copy gone with the old estate. Never let this file's «already on disk» outrun reality:
check the file before relying on it.

Re-stage from the canonical Cologne PDScan-2020 download (one command, in the
SanskritSpellCheck clone):

    python detectors/get_external_source.py PD

→ `SanskritSpellCheck/external_src/pd/pd.txt` — 55 MB, **107,630 `<L>` records**, 879,172
lines, standard csl `<L>/<k1>/<k2>/<h>` markup (header: *DFG-Sanskrit-Projekt 2010,
PD1-8_FINAL, 2011-10-14*); the script self-verifies the `<L>` count. License
CC BY-NC-SA 3.0 © The Sanskrit Library / Thomas Malten — never commit the file, and
never re-derive it from any source other than the canonical Cologne `pdtxt.zip`.
(The `SanskritSpellCheck/o_vs_O/output*/PD.txt` files are detector outputs, not the source.)

## Differences that matter for our use

- **Same source dictionary, two digitizations.** They are not different works; they are
  two digital editions of the *same* Deccan-College PD. Divergence is about
  **format, openness, completeness, and authority**, not content scope.
- **CDSL = the usable feed today.** Standard `<L>` markup + downloadable XML means PDScan
  drops into the existing csl tooling (same as PWG/MW). If PD is ever wanted as a
  Sanskrit-side sense/chronology cross-check (its historical-principles sense ordering
  is directly relevant to our [sense-ordering study](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/research/HANDOFF_sense_ordering.md)),
  **start from PDScan/2020**.
- **KoshaSHRI = the authority + recency check.** As the publisher's own edition it is the
  reference for resolving a doubtful PDScan reading and for picking up volumes digitized
  after the 2020 Cologne scan — but it currently has *less* online and is not bulk-
  downloadable, so it is a **verification source, not a bulk import**, until that changes.
- **Both are incomplete** (only the early alphabet is published), so PD can only ever be a
  **partial** cross-reference, never a full-coverage layer.

_Sources: [KoshaSHRI About](https://koshashri-dc.ac.in/about) · Deccan College Sanskrit &
Lexicography dept · CDSL [PDScan/2020](https://sanskrit-lexicon.uni-koeln.de/scans/PDScan/2020/web/index.php).
PD is **not** part of the Petersburg supplement chain ([DICTIONARY_CHAIN.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/DICTIONARY_CHAIN.md));
it is an independent Sanskrit historical dictionary tracked here for its sense-ordering
evidence and as a future Sanskrit-side cross-check._

_Dr. Mārcis Gasūns_
