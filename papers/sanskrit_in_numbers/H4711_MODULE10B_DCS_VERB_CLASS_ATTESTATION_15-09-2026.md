# Module 10b — DCS corpus attestation of verb classes + prefixed forms

_Created: 15-09-2026 · Last updated: 15-09-2026_

> H4711 (census A5 wiring): the «Санскрит в цифрах» verb-class+voice module
> gains its **corpus leg**, consuming two already-registered kosha datasets —
> [dcs-verb-roots-by-class](https://github.com/gasyoun/kosha/blob/main/data/manifest/datasets.json)
> (463 rows) and [dcs-verb-class-prefix-frequency](https://github.com/gasyoun/kosha/blob/main/data/manifest/datasets.json)
> (8454 rows) — instead of re-deriving class inventories. Generator:
> [module10b_dcs_verb_class_attestation.py](module10b_dcs_verb_class_attestation.py) →
> [module10b_dcs_verb_class_attestation.json](module10b_dcs_verb_class_attestation.json).

## The module section

Module 10 ([module10_verb_class_voice.json](module10_verb_class_voice.json), H813) is the
*lexical* view: Whitney's 938-root gaṇa inventory + vidyut pada paradigms. Module 10b is
the *corpus* view: what DCS actually attests per present class, and how much of that mass
is carried by prefixed formations.

### Per-class corpus mass (bare roots vs prefixed-inclusive entries)

| Class | Bare roots | Bare occ. | Prefixed-incl. entries | Incl. occ. |
|---|---|---|---|---|
| 1 (bhvādi) | 276 | 109,469 | 2,631 | 239,087 |
| 2 (adādi) | 47 | 111,051 | 527 | 158,096 |
| 3 (juhotyādi) | 12 | 2,046 | 266 | 21,954 |
| 4 (divādi) | 48 | 25,727 | 745 | 100,545 |
| 5 (svādi) | 12 | 1,425 | 175 | 14,178 |
| 6 (tudādi) | 44 | 19,566 | 788 | 112,575 |
| 7 (rudhādi) | 6 | 164 | 187 | 9,046 |
| 8 (tanādi) | 4 | 4,710 | 493 | 12,500 |
| 9 (kryādi) | 13 | 7,333 | 303 | 18,549 |
| 10 (curādi) | 0 | 0 | 2,339 | 94,958 |
| **Σ** | **462 rows / 442 distinct** | **281,491** | **8,454** | **781,488** |

(Sum row corrected 15-09-2026 after independent DeepSeek verifier re-sum: bare occ was mis-typed
391,991, entries Σ now the 8,454 parity constant itself; 442 distinct = 462 rows minus 20 roots
attested in more than one class; 7,890 of the 8,454 prefixed-inclusive entries are prefixed-only.)

Headline facts the portrait can quote:

1. **Class 10 has zero bare-roots attestation** in the bare inventory, yet 2,339
   prefixed-inclusive entries with ~95k occurrences — the curādi class lives almost
   entirely through derived stems (kathay-, pūjay-, kāray-…).
2. **7,890 of 8,454 prefixed-dataset entries** are absent from the bare-roots inventory:
   either prefixed stems listed as own entries (āgam, prāp…) or roots whose corpus mass is
   prefixed-only (gam 15,939 occ, dṛś 14,292, śru 9,422 — the bare inventory never sees them).
3. **Prefixed share of mass** for roots in both datasets: dā 99.9% prefixed (9,884 of its
   occurrences), hṛ 99.6%, jṛ 98.3% — the high-frequency verb system is heavily compounded.

## Trust block

- **Source:** kosha-registered VisualDCS derived-data, consumed read-only from the sibling
  checkout (pin `d515475da6e227598fed7c64e9cbef62951a9c69`), same
  resolution pattern as the SanskritGrammar H4178 consumer of the first dataset.
- **Manifest parity (the verification):** counted 463/463 and 8454/8454 rows vs kosha
  `datasets.json` — **match**; any drift fails the generator with exit 1.
- **Denominators:** 462 bare-root rows → 442 distinct roots (20 roots attested in more than one
  class; the 463rd parity row is the junk `0` line in 10.csv) — NOT merged with module 10's
  938-root Whitney denominator; the two legs are reported side by side, never summed.

## Honesty notes (carried in the JSON too)

1. **R2606-01 (Uprava DEAD_ENDS):** both datasets are UNACCENTED counts — they cannot
   separate present class I from VI (only accent does). **No I/VI verdict is drawn here.**
2. The prefixed-forms dataset lists mostly roots but also prefixed stems as own entries,
   and assigns classes more widely than the bare inventory (dā sits in its class-1 frq file
   though grammatically class 3). Entries are consumed as-is; re-classification is out of
   scope by the census contract.
3. "Prefixed-only" is an inventory fact (absent from the bare inventory), not a claim that
   the entry itself contains a prefix.

## Provenance

- Handoff: H4711 (OxAlpha tier label, executed per H3688 dual-run override) · 15-09-2026.
- Edges registered: Uprava `interlinks_edges.tsv` VisualDCS→SanskritLexicography (both kosha ids).
- kosha manifest `consumers` updated for both datasets in the same pass.

_Гасунс_
