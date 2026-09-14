# EWA acquisition report — the index is absent, the shape is ready (H4726)

_Created: 15-09-2026 · Last updated: 15-09-2026_

Mission
[H4726](https://github.com/gasyoun/Uprava/blob/main/handoffs/H4726-OxAlpha_SanskritLexicography_xwalk-b7-ewa-pwg-acquisition_14.09.26.md)
(B7, sibling of the xwalk batch of 14-09-2026): acquire the EWA index,
normalize + join, keep `lane = modern-IE` separate from the traditional
Cologne lane. Shape contract:
[KEWA memo §7](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/KEWA_INDEX_NORMALIZATION_AND_PWG_JOIN_25-08-2026.md).

## 1. Acquisition census — EWA is not on disk, and cannot be agent-acquired

Probed 15-09-2026 (OxAlpha, `zai-coding-plan/glm-5.3-flash`):

| Surface | Probe | Verdict |
|---|---|---|
| [SamudraManthanam](https://github.com/gasyoun/SamudraManthanam) `Index/lib/x86_64-win64/Data/` | `ls` — `KEWA.txt` present, no `EWA.*` | **absent** |
| SamudraManthanam git history | `git log --all --grep EWA` | no commit ever touched EWA |
| samskrtam.ru | `curl` `/sanskrit-lexicon/KEWA/` → 200; `/sanskrit-lexicon/EWA/` → timeout/absent | **not served** |
| kosha registry | grep `datasets.json` for EWA/Altindoarischen | no row |
| Uprava `DATA_LAYERS_CENSUS.md` | grep | no row |
| Whole `~/Documents/GitHub` tree | `find -iname '*ewa*'` (noise-filtered) | no EWA dataset |
| Recorded owner intent | [memory](https://github.com/gasyoun/Uprava/blob/main/_memory_staging/claude_memory/C--Users-user-Documents-GitHub__reference_mayrhofer_kewa_ewa_permission.md), updated 29-08-2026 | "EWA: not yet on disk; **to come later (MG)**" |

The KEWA "acquisition precedent" is not an agent acquisition at all: the
KEWA heading index is **MG's own digitization** (his scanned copy, his OCR,
published in SamudraManthanam under his Mayrhofer permission). EWA has no
equivalent artifact, and a print-only 3-volume in-copyright dictionary cannot
be digitized by an agent. **The full EWA index arrives only when MG brings
it** — that is a human `@DO`, filed in the same pass.

## 2. The one EWA footprint that does exist — readiness, not rows

[dhatup_multisource_crosswalk.json](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/data/dhatup_multisource_crosswalk.json)
(H4478, from MG's own Dhātupāṭha Concordance) carries `ewa_volcol` ×841 and
`ewa_no` ×1,210 — **the only EWA data in the estate**. Their semantics are
UNCONFIRMED from the derived JSON alone: `ewa_volcol` is numeric-monotonic
(page/column-like, 2→1,299, no volume letter), `ewa_no` mixes entry numbers
with German glosses (`155`, `449`, but also `sehen`, `(an)treiben`), and
sibling columns (`whitney_root`, `verba_root`) demonstrably carry page
numbers, not roots. Deciding the semantics needs the source workbook / MG's
documentation — machine-guessing it is banned house practice (cf. the
four-tier enumeration ruling, FINDINGS §453/§617).

So **none of these rows enter the crosswalk**. What IS reported is a
readiness census
([`ewa_extension_report.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/data/etym/ewa_extension_report.json)):
1,026 pointer rows carry a Palsule root; after dropping the leading homonym
numeral, folding Palsule's print-ç to ś, and going through the canonical
sanskrit-util transcoder, **900 of 1,026 (87.7 %) land exact in PWG key1**;
126 are absent; 0 fail to transcode. When the real index lands, those ~900
roots give the EWA leg an immediately anchorable verbal core.

## 3. What was built — the §7 shape, implemented and verified

[`src/etym/ewa_extend.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/etym/ewa_extend.py)
extends the crosswalk **in shape**, never in source rows:

- [`data/etym/kewa_ewa_pwg_crosswalk_extended.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/data/etym/kewa_ewa_pwg_crosswalk_extended.tsv) —
  11,418 KEWA rows unchanged, plus `source = KEWA`, an empty `supersedes`
  relation (memo §7: an EWA row marks the KEWA row superseded and **both
  stay**), and reserved `ewa_volcol`/`ewa_no` slots. `vol` stays a string
  (EWA's three volumes number independently — §7 point 3).
- [`data/etym/ewa_extension_report.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/data/etym/ewa_extension_report.json) —
  machine report + the readiness census above.
- Original [`kewa_pwg_crosswalk.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/data/etym/kewa_pwg_crosswalk.tsv)
  is **not rewritten**; H4749's rung extension can land independently.

**Verify (ran green):** `python RussianTranslation/src/etym/ewa_extend.py --github-root <GitHub>`
— hard-fails on any row-count, `pwg_key1`-set, or coverage drift, and the
lane-coverage recount over both the original and the extended file
reproduces
[`etym_lane_coverage.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/data/etym/etym_lane_coverage.json)
exactly: 7,157 / 11,087 / 1,665 / 5,492 / 9,422 / 89,503 / 106,082.

## 4. What is deliberately not here

- **No EWA rows emitted.** Zero-source rows would be fabricated coverage;
  the honest `ewa_rows_emitted` is 0 and the file says so.
- **No interpretation of the Concordance EWA columns.** Readiness census
  only.
- **No merge of lanes.** The modern-IE lane stays one labelled lane whose
  `source` column will distinguish KEWA from EWA when both exist.

## 5. Residual — the human action that unblocks the real leg

**@DO (MG):** acquire the EWA heading index (same shape as
`SamudraManthanam/Index/lib/x86_64-win64/Data/KEWA.txt`: one line per
heading block, `vol: page`, Devanāgarī + IAST + machine key) and, ideally,
document the two EWA columns of the Concordance Final sheet. The moment the
index lands, the H3169 pipeline reuses unchanged: `kewa_normalize.py` →
`join_kewa_pwg.py` with `source=EWA` → `supersedes` population — the
extension file already carries the slots.

_Гасунс_
