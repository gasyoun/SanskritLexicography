# Handoff research — sense ordering across the core dictionaries (2026-06-23)

**Question.** In what order does each core Sanskrit dictionary arrange the senses
*within* an entry — **historical** (oldest/Vedic attestation first → later), **logical /
semantic** (grouped by meaning, common-first, pedagogical), **etymological** (derivation
order), or **frequency** (none known to exist in print)? This decides how `pwg_ru`
orders each card's senses — and we already carry the **Renou I–V** tag + `renou_oldest`
per sense, so *historical* ordering is essentially free if that's the target.

**Why it matters.** The sense order is an editorial stance, not a mechanical fact. A
printed Russian PWG should order senses the way scholarly users expect; if the source
dictionaries disagree, `pwg_ru` must choose deliberately and state it.

## Working hypothesis (user, to verify)
- **The 19th-c. European dictionaries are HISTORICAL.** PWG, PW, MW, GRA arrange senses
  by period of attestation (Vedic → Brāhmaṇa → epic → classical), the comparative-
  philology paradigm of their era. *Likely true — verify in each preface.*
- **No printed FREQUENCY dictionary of Sanskrit exists yet** (so frequency-order is a
  `pwg_ru` innovation if we want it — and DCS now makes it possible).
- **AP (Apte) is NON-historical** — but is its order best described as *logical/semantic
  grouping* (common/practical senses first, grouped by meaning, student-facing)?
  **Open — continue research.**

## Sources (read the PREFACES first — most are OCRed)
| Dict | Preface (OCR) — read for the explicit ordering statement | Entry file (verify against real entries) |
|---|---|---|
| PWG | [`PWG/prefaces/pwgpref_all.de.md`](https://github.com/sanskrit-lexicon/PWG/blob/master/prefaces/pwgpref_all.de.md) | `csl-orig/v02/pwg/pwg.txt` |
| PW | [`PWK/prefaces/pwpref_all.de.md`](https://github.com/sanskrit-lexicon/PWK/blob/master/prefaces/pwpref_all.de.md) | `csl-orig/v02/pw/pw.txt` |
| MW | [`MWS/prefaces/mwpref_all.en.md`](https://github.com/sanskrit-lexicon/MWS/blob/master/prefaces/mwpref_all.en.md) | `csl-orig/v02/mw/mw.txt` |
| GRA | [`GRA/prefaces/grapref_all.en.md`](https://github.com/sanskrit-lexicon/GRA/blob/master/prefaces/grapref_all.en.md) (also `.de`, `.ru`) | `csl-orig/v02/gra/gra.txt` |
| AP90 | *(no OCR preface — read the Apte 1890 print front-matter / "Scheme of the work")* | `csl-orig/v02/ap90/ap90.txt` |
| SCH | [`SCH/prefaces/schpref_all.de.md`](https://github.com/sanskrit-lexicon/SCH/blob/master/prefaces/schpref_all.de.md) | `csl-orig/v02/sch/sch.txt` |

**Method.** (1) In each preface, find the passage on *Anordnung der Bedeutungen* /
"arrangement of meanings" / "scheme of the work"; quote it. (2) Cross-check against a
shared polysemous probe word translated across all of them — e.g. `artha` (अर्थ: aim →
wealth → meaning → lawsuit) or `dharma` — does sense 1 in each correspond to the oldest
attested meaning, the commonest, or the etymological core? (3) Classify each dict +
quote the evidence.

**Output:** a table `dict × {historical / logical-semantic / etymological} × evidence
quote`, plus a recommendation for `pwg_ru`'s sense order (likely **historical via the
Renou tag**, since we already compute `renou_oldest` per sense — but confirm it matches
PWG's own order so we don't fight the source).

**Note for executor.** Distinguish *macro*structure (headword order = alphabetical for
all) from *micro*structure (sense order within an entry) — this handoff is only the
latter. Watch for dictionaries that mix axes (e.g. etymological *grouping* of homonyms
but historical order *within* a homonym).
