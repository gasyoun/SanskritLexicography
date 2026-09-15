# H4741 — Samsaadhanii Dhātupāṭha × WhitneyRoots mw_roots parity report

_Created: 15-09-2026 · tier: OxAlpha (opencode/z-ai/glm-5.3-flash) · VALIDATION-ONLY_

## Inputs (provenance)

| input | sha256 (first 12) | size |
|---|---|---|
| SCL `samsaadhanii/scl` `skt_gen/Sentence/data/dhatu_info_chart_wx.txt` (dhaatupaatha data CC BY-SA 3.0 per dhaatupaatha/README; N Shailaja & Amba Kulkarni) | `ad05ae736a82` | 7419 pada-rows |
| WhitneyRoots `crosswalk/mw_roots.json` (estate MW root canon) | `c12d8efbb0e8` | 750 roots |

Join key: SCL-WX root → estate SLP1 via SCL's own `converters/wx2slp.lex`
pair table composed with canonical `sanskrit_util` (never forked).
Anubandha markers (SCL-WX `z`/`Z`/trailing digits) stripped before join.

## Result — root-count parity

| metric | value |
|---|---|
| SCL distinct roots (anubandha/pada-deduped) | 1591 |
| WhitneyRoots mw_roots entries | 750 |
| **mw_roots matched by SCL (exact SLP1)** | **581 / 750 = 77.5 %** |
| SCL roots matched in mw_roots (tier1 exact) | 523 / 1591 = 32.9 % |
| SCL roots matching only under recall-only ASCII fold (tier2) | 36 |
| SCL roots unmatched | 1032 |
| join pairs (root × mw entry, tier1) | 562 |
| gaṇa-class agreement / disagreement on matched pairs | 447 / 104 |
| SCL-WX gaṇa tokens outside the 10 Adi series | 0 |

## Residue analysis (measured, not guessed)

- 169 mw_roots entries have no SCL chart root even under the
  recall-only fold; of these **14 are explicitly lexicographic**
  (MW gloss flags ", L." / "L." — late Sanskrit additions a Pāṇinian gaṇa-list
  does not attest).
- The rest diverge by **citation-grade convention**, not by key failure:
  MW cites guṇa/vṛddhi or nasal-infixed shapes where the Pāṇinian chart cites
  zero-grade (tier2 examples: bad↔bAD, bid↔Bid, cad↔Cad+Cad, das↔dAS, dav↔Dav+DAv+DAv, de↔De).
- Class agreement 447/551
  (81.1 %) on matched
  pairs with classes on both sides — informational only.

Parity verdict: mw_roots is a **Whitney/MW-derived canon** — the SCL Pāṇinian
Dhātupāṭha (generator inventory) covers 77.5 % of it exactly; the
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
