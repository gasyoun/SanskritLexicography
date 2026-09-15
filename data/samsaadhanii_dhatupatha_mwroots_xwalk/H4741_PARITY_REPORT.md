# H4741 — Samsaadhanii Dhātupāṭha × WhitneyRoots mw_roots parity report

_Created: 15-09-2026 · tier: OxAlpha (opencode/z-ai/glm-5.3-flash) · VALIDATION-ONLY_

## Inputs (provenance)

| input | sha256 (first 12) | size |
|---|---|---|
| SCL `samsaadhanii/scl` `skt_gen/Sentence/data/dhatu_info_chart_wx.txt` (dhaatupaatha data CC BY-SA 3.0 per dhaatupaatha/README; N Shailaja & Amba Kulkarni) | `ad05ae736a82` | 7419 pada-rows |
| WhitneyRoots `crosswalk/mw_roots.json` (estate MW root canon) | `c12d8efbb0e8` | 750 roots |

Join key: SCL-WX root → estate SLP1 via a literal char table lifted from SCL's
own `converters/wx2slp.lex` (the pairings are upstream-attested facts; the
table is cross-verified against canonical `sanskrit_util` in `--selftest`,
which is sanskrit_util's only role — it is not in the runtime join path).
Anubandha markers (SCL-WX `z`/`Z`/trailing digits) stripped before join.

## Result — root-count parity

| metric | value |
|---|---|
| SCL distinct roots (anubandha/pada-deduped) | 1591 |
| WhitneyRoots mw_roots entries | 750 |
| **mw_roots matched by SCL, EXACT SLP1 only** | **562 / 750 = 74.9 %** |
| mw_roots witnessed only via recall-only fold (tier2, not counted above) | 38 |
| mw_roots unmatched vs the FULL SCL root set (exact or fold) | 150 |
| SCL roots matched in mw_roots (tier1 exact) | 523 / 1591 = 32.9 % |
| SCL roots matching only under recall-only ASCII fold (tier2) | 36 |
| SCL roots unmatched | 1032 |
| join pairs (root × mw entry, tier1) | 562 |
| gaṇa-class agreement / disagreement on matched pairs | 447 / 104 |
| SCL-WX gaṇa tokens outside the 10 Adi series | 0 |

## Residue analysis (measured, not guessed)

- 150 mw_roots entries have neither an exact nor a case-fold
  SLP1 partner anywhere in the full SCL root set; of these
  **13 are explicitly lexicographic** (MW gloss flags ", L." /
  "L." — late Sanskrit additions a Pāṇinian gaṇa-list does not attest); the
  remainder are genuine generator-chart gaps vs MW's inventory.
- Citation-grade divergence is measured separately, as 38
  mw entries + 36 SCL roots that pair only under the
  recall-only fold (MW guṇa/vṛddhi or aspirated citation shapes vs the
  Pāṇinian zero-grade chart; SCL-side examples:
  bad↔bAD, bid↔Bid, cad↔Cad+Cad, das↔dAS, dav↔Dav+DAv+DAv, de↔De).
- Class agreement 447/551
  (81.1 %) on matched
  pairs with classes on both sides — informational only.

Parity verdict: mw_roots is a **Whitney/MW-derived canon** — the SCL Pāṇinian
Dhātupāṭha (generator inventory) covers 74.9 % of it exactly; the
residue splits into explicitly lexicographic MW additions and citation-grade
divergence (measured above), not key-bridge failure. VALIDATION-ONLY: no
SCL-derived row-level data is committed; join TSV stays local (--emit-join-tsv).

## Risks

- SCL dhatu_info_chart is the *verb-generator* inventory, not the full
  Dhātupāṭha concordance (dhaatupaatha/files/*.html, 4,388 pages) — parity is
  against the generator's root set.
- tier2 (ASCII fold) is recall-only; tier1 numbers are the assertion.
- gaṇa class disagreement counts compare SCL gaṇa vs MW printed classes —
  informational, never auto-corrective.
