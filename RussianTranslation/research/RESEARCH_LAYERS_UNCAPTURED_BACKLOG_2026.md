# Research layers — the uncaptured backlog (residue of the July 2026 braindumps)

_Created: 11-07-2026 · Last updated: 11-07-2026_

This note captures the research-layer ideas from two root-level braindump files
(`pwg-layers.md`, `research-layers.txt`, removed 11-07-2026) that were **not**
already folded into a durable roadmap or handoff. Most of those dumps *were*
already captured — see the pointers under "Already homed" — so only the residue
lives here. Each item is a candidate layer derivable in parallel with the
PWG→RU translation; none is scheduled yet.

## Already homed (do not re-capture — these pointers are the whole point)

- **Ceiling items (WSD, chronology, etymology, register, consensus, citation residue, cross-lingual)** →
  [ROADMAP_CEILING_2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/research/ROADMAP_CEILING_2026.md) (C1–C8, MG rulings 08-07-2026).
- **ACL lessons (BLI evaluation, sense-attestation benchmark, Lexical Linked Data / OntoLex upgrade, IndoWordNet crosswalk, Leonchenko Sinonimy lane)** →
  [ROADMAP_ACL_LESSONS_2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/research/ROADMAP_ACL_LESSONS_2026.md) (B1–B3).
- **W1–W4 audit specs (3-account concurrency, per-source evidence vector, case-government backfill, sense→genre attribution)** →
  [PIPELINE_CAPABILITY_AUDIT_2026-07-08.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/PIPELINE_CAPABILITY_AUDIT_2026-07-08.md) and the H335 audit it launched.
- **Nominal-core queue reorder (Приложение 5/10, tier ordering, Сборное ядро = 7,532)** →
  [H179](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H179-Opus_RussianTranslation_pwg_ru_nominal_core_queue_reorder_05.07.26.md).
- **Addenda typology + content-aware glue + learner-retention layering** →
  [H180](https://github.com/gasyoun/Uprava/blob/main/handoffs/H180-Opus_RussianTranslation_pwg_ru_addenda_typology_glue_learner_05.07.26.md).
- **Zaliznyak IIL polemical article** → SanskritGrammar's `IIL_ZALIZNIAK_ALTERNATIONS_ARTICLE_2027.md` +
  `IIL_ZALIZNIAK_ALTERNATIONS_POLEMIC_PLAN_2027.md` (relocated `3.txt` braindump parked in that repo).

## Uncaptured residue — candidate layers

1. **Cross-layer completeness gate.** There is no union-across-the-five-layers
   completeness check anywhere — coverage is audited per-card only, and if
   `dict_merge.py` returns zero records for a layer (failed index lookup) it is
   silently skipped with no warning. No "expected-layers" registry exists.
   Flagged as cheap to close deterministically ("can we close it now?"). Distinct
   from the H180 glue work: this is a *gate*, not a re-ordering.

2. **Multi-recension Mahābhārata citation verification.** PWG/MW cite MBH by
   verse (e.g. `br_u~~h0_00_pwg00`: "MBH. 7,9283 ошибочно вместо abravīt, как
   имеет ed. Bomb."). Verify such citations against the critical edition on
   GRETIL and the recensions on [mahabharata.manipal.edu](https://mahabharata.manipal.edu)
   (BORI 73,797 · Kumbhakonam 96,635 · Sastri-Vavilla 95,286 · Tatparyanirnaya
   5,180 verses), then the wider web. Same forensic pattern as
   [csl-atlas HARIVAMSA_CITATION_RESOLUTION_CENSUS.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/HARIVAMSA_CITATION_RESOLUTION_CENSUS.md) —
   extend to MW/PWG's other cited works. Also: Böhtlingk's Indische Sprüche
   (Spr.) citations are digitized; track first- vs second-edition numbering
   (`Spr. II` = 2nd ed.).

3. **Page-adjacency layer.** Expose the IDs of all headwords that originally sat
   on the same printed dictionary page together (a derivable co-location layer
   over the source scans/line-map, addable to the German source too, not only the
   translation).

4. **Per-card grammar counts, stored not recomputed.** Case-government backfill
   (snih + loc.) is now in hand, but dictionaries carry much more grammar. Define
   what is countable in a card (government patterns, variance, absences), store
   the counts so they need not be recalculated later.

5. **Hapax enumeration.** "Как найти все гапаксы санскрита?" — a corpus/dictionary
   layer enumerating hapax legomena.

6. **Big / medium / small student-dictionary retention layering.** Beyond the
   scholarly abridgements (PW/MW/AP), track retention across student tiers —
   Medium: CAE, CCS (both PWG-derived, watch closely), MD, KCH; Small: LAN, KNA,
   FRI — as a data-driven per-sense learner-retention score. Correction to the
   naive framing: also compare headword-level change MW72→MW and AP90→AP (MW had
   more PWG + fully-published PW by then).

7. **TM enrichment from non-printed corpora.** Supply translation memory beyond
   the PWG translation itself: Russian lecture transcripts
   ([sgi/03](https://samskrtam.ru/l/sgi/03.html),
   [vvip/02](https://samskrtam.ru/l/vvip/02.html)), monographs (Syrkin, Mahābhārata
   articles, Pandey), smaller glossaries (Grintser Rāmāyaṇa 1–2 / Bāṇa Kādambarī,
   Potapova, Erman-Temkin, Toporov), reference works (Индуизм·Джайнизм·Сикхизм,
   Mify_759_ind), and the DSG mechanical RU rendering
   ([samskrtam.ru/sanskrit-lexicon/dsg](https://samskrtam.ru/sanskrit-lexicon/dsg/)).
   Compare against the KEWA word index (dhātus as finite forms; `bhavati`→`bhū`);
   add EWA later and document. Some Russian translations lack a known Sanskrit
   original (e.g. `devi-gita.no_tags`) — a find-the-source sub-task.

_Dr. Mārcis Gasūns_
