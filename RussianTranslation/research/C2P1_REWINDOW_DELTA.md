# C2 — re-window delta report on the corrected work dates

_Created: 15-09-2026 · Handoff [H4728](https://github.com/gasyoun/Uprava/blob/main/handoffs/H4728-OxAlpha_SanskritLexicography_xwalk-b9-work-dating-rewindow_14.09.26.md) · Table [C2P2_WORK_DATING_TABLE.md](C2P2_WORK_DATING_TABLE.md) · Phase 1 [C2P1_ATTESTATION_WINDOW.md](C2P1_ATTESTATION_WINDOW.md)_

_Dr. Mārcis Gasūns_

**What this is.** H3790 curated 45 sourced date ranges and measured what a re-window would move — without performing it. This report performs it on a DERIVED artifact: [ls_source_map_rewindowed.json](../src/ls_source_map_rewindowed.json) carries the corrected datings beside the untouched phase-1 entries, and every committed window in [pwg_sense_attestation_window.jsonl](../src/pwg_sense_attestation_window.jsonl) is recounted under the curated ranges below. The phase-1 map and window store are read-only inputs; nothing is rewritten.

**Method.** Window bounds under the curated table = `min(earliest)` / `max(latest)` over the sense's cited works with `dating_valid: true` (`c2p2_dating_table.py::rewindow`, selftest-proven). Dating-invalid sigla (`Spr`, `ŚKDR`) are dropped, not clamped — the curated table's own committed semantics. The store-wide drop convention is the open human decision **C2P2-D10**: nothing here closes it, and no window store is rewritten.

## The seven corrections

| Siglum | Work | Phase-1 point | Curated range | Confidence | Effect |
| --- | --- | --- | --- | --- | --- |
| `AMAR` | Amaru-śataka | 450 CE | 650 CE – 800 CE | consensus | repointed into the sourced range |
| `KATHĀS` | Kathāsaritsāgara | 1050 CE | 1063 CE – 1081 CE | anchored | repointed into the sourced range |
| `GĪT. GOV` | Gītagovinda | 1048 CE | 1170 CE – 1200 CE | consensus | repointed into the sourced range |
| `VOP` | Vopadeva, Mugdhabodha | 1250 CE | 1260 CE – 1300 CE | consensus | repointed into the sourced range |
| `SĀH. D` | Sāhityadarpaṇa | 1400 CE | 1300 CE – 1384 CE | consensus | repointed into the sourced range |
| `RĀJAN` | Rājanighaṇṭu | 1300 CE | 1375 CE – 1500 CE | consensus | repointed into the sourced range |
| `Spr` | Indische Sprüche (Böhtlingk anthology) | 600 CE | 1863 CE – 1873 CE | invalid | dropped (dating-invalid) |

## Date-range recount (43,990 windows with ≥1 dated work)

| Measure | Windows |
| --- | --- |
| windows recounted | 43,990 |
| bounds unchanged | 56 |
| any bound moved | 41,061 |
| `earliest` moved | 39,027 (earlier 36,395 · later 2,632) |
| `latest` moved | 39,823 (later 32,619 · earlier 7,204) |
| any bound widened | 39,260 |
| any bound tightened | 8,329 |
| window VANISHED (only dated works were dating-invalid) | 2,873 |

Most movement is the point→range change itself (a work that was one number is now a bracket, so bounds widen by construction) plus the seven real corrections; `Spr`'s drop also TIGHTENS bounds it had falsely set and vanishes windows whose only dated works were invalid. A window may count as widened AND tightened when different cited works pull its two ends opposite ways.

## Per-siglum attribution (windows citing each corrected siglum)

Co-citation overlaps allowed — one window can move for two corrections.

| Siglum | windows citing | `earliest` moved | `latest` moved | vanished |
| --- | --- | --- | --- | --- |
| `AMAR` | 298 | 279 | 281 | 0 |
| `KATHĀS` | 5,332 | 5,093 | 4,895 | 0 |
| `GĪT. GOV` | 0 | 0 | 0 | 0 |
| `VOP` | 1,560 | 1,461 | 1,560 | 0 |
| `SĀH. D` | 1,672 | 1,595 | 1,672 | 0 |
| `RĀJAN` | 2,553 | 2,509 | 2,553 | 0 |
| `Spr` | 4,653 | 3,890 | 3,691 | 551 |

## Carried, unchanged

- **C7 residue:** 115,354 citation instances across 2,607 distinct sigla still resolve to no work in the map; every window remains a conservative lower bound. This re-window widens nothing about C7.
- **Open decisions:** C2P2-D1…D11 (eleven contested datings) remain open; the vote sheet [pwg_c2p2_work_dating_11.html](https://gasyoun.github.io/vote/sheets/pwg_c2p2_work_dating_11.html) is unvoted. This artifact changes no vote.
- **Phase-1 store:** [pwg_sense_attestation_window.jsonl](../src/pwg_sense_attestation_window.jsonl) and [ls_source_map.json](../src/ls_source_map.json) are byte-identical to phase 1. A re-windowed window store is deliberately NOT written until the D-decisions settle the convention.

## Reproduce

```sh
cd RussianTranslation/research
python c2p1_rewindow.py --selftest   # fixture tests
python c2p1_rewindow.py --check      # gate: recompute + invariants
python c2p1_rewindow.py              # regenerate both artifacts
```

