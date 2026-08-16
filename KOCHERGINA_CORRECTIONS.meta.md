# KOCHERGINA_CORRECTIONS.md — metadoc

_Created: 15-08-2026 · Last updated: 16-08-2026_

## Purpose

The tracked home for corrections to Kochergina 1987 and the learnsanskrit.ru dictionary
derived from it — a dictionary the org **consumes but does not publish**, and which
therefore has no slot in the project's real correction store.

## Audience

Sessions annotating or scoring against Kochergina glosses (BLI gold, RussianTranslation
equivalence work), and whoever eventually reports these findings upstream to
learnsanskrit.ru.

## Provenance

Created 15-08-2026 by Opus 5 (`claude-opus-5`) under
[H798](https://github.com/gasyoun/Uprava/blob/main/handoffs/H798-Sonnet_SanskritLexicography_h779-apply-okas-guda-sphic-decisions_12.07.26.md),
whose prerequisite 1 ("locate the owning store") had blocked four approved votes since
12-07-2026. The store did not exist; that absence is recorded as
[FINDINGS §539](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md).
Votes come from sheet `uprava-nagari2013-okas-guda-sphic_4lemmas` (4/4 approve, decided
2026-07-12, re-decided with notes 2026-07-17); attestation evidence from
[Uprava/history/NAGARI_LIST_2013_ATTESTATION_VS_GLOSS_OKAS_GUDA.md](https://github.com/gasyoun/Uprava/blob/main/history/NAGARI_LIST_2013_ATTESTATION_VS_GLOSS_OKAS_GUDA.md).

## Design decisions

- **Not a row in [CORRECTIONS](https://github.com/sanskrit-lexicon/CORRECTIONS).** That
  repo is the project's correction audit trail but is keyed by CDSL dictionary codes
  (`ACC … SKD`). Kochergina is not a Cologne dictionary — no code, no `dictionaries/`
  slot, zero `cfr.tsv` rows. Filing there would have required inventing a code for a
  dictionary the project does not host.
- **Lives in the consuming repo.** SanskritLexicography owns the BLI gold set and the
  RussianTranslation work that reads Kochergina glosses, so the correction record sits
  next to its consumer rather than next to Cologne's.
- **Corrects nothing automatically.** Kochergina is third-party; these are findings
  *about* its entries, not edits to it. The "Consumer action" column, not a patch, is how
  the correction takes effect.
- **Refuted claims are kept, not deleted** (`guda` gender). A removed refutation gets
  re-raised as if new; H779 already had to disprove that one once.
- **Wording-open rows are marked as such** rather than silently finalised — two of the
  four need a reading session (Elizarenkova, Druzhinin) that no agent pass can shortcut.

## Improvement backlog (ranked)

1. ~~Close the two open cross-checks — Elizarenkova on `okas`, Druzhinin on `guda`.~~
   **Done 16-08-2026 under H2863**; both rows are `recorded`. The residual is narrower:
   locate **Druzhinin's own Aṣṭāṅgahṛdaya translation**, which is in no repo under
   `GitHub/` and would be a better source than the anonymous course transcripts the
   closure had to fall back on.
2. Decide whether these findings get reported upstream to learnsanskrit.ru, and if so
   record the report link per row.
3. If a second batch of Kochergina corrections ever arrives, consider whether the table
   should carry the sheet_id per row rather than once in the section header.
4. Cross-link from the BLI gold set's own documentation, so an annotator meets the
   corrections before annotating rather than after.
5. Re-check row 1's wording once [H2850](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2850-Opus_SanskritLexicography_rv-citation-pada-alignment-elizarenkova-rvlinks_15.08.26.md)
   builds its pāda-level alignment: the 12 `okas` loci were aligned by hand here and are a
   ready-made regression case for it.

## Limitations

- Covers exactly the four H798 lemmas; it is **not** a survey of Kochergina's defects.
- Records no page/edition numbers for the 1987 print — the votes were adjudicated against
  attestation evidence and secondary sources, not against a scan.
- Whether learnsanskrit.ru's derived dictionary reproduces each defect is untested.
- The `guda` closure rests on the DCS **Aṣṭāṅgahṛdaya** annotation plus one anonymous
  Ayurveda course corpus. It is not a survey of the Ayurvedic register at large —
  Caraka and Suśruta were not read, and Druzhinin's own translation was never found.
- RV 9.86.45 carries no Russian in the rvlinks build, so the `okas` closure rests on 11
  of 12 attestations, not 12.

## Revision history

| Date | Change | Model |
|---|---|---|
| 15-08-2026 | Created alongside the store under H798 | Opus 5 (`claude-opus-5`) |
| 16-08-2026 | Both cross-checks closed under H2863; backlog item 1 retired and replaced with the narrower "find Druzhinin's own translation" residual; two new limitations recorded | Opus 5 (`claude-opus-5`) |

_Dr. Mārcis Gasūns_
