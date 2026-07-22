# PLAN_RussianTranslation_pubgrade_tm_oral_2026H2 — metadoc

_Created: 22-07-2026 · Last updated: 22-07-2026_

Companion record for [PLAN_RussianTranslation_pubgrade_tm_oral_2026H2.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/PLAN_RussianTranslation_pubgrade_tm_oral_2026H2.md)
and its four layer docs (ROADMAP / ARCHITECTURE / IMPLEMENTATION / VERIFICATION).

## Purpose
The execution-ready `/ask` plan for **finishing** the Publication-Grade Sa→Ru Translation Memory
([H215](https://github.com/gasyoun/Uprava/blob/main/handoffs/H215-Opus_RussianTranslation_pwg_ru_publication_grade_tm_tmx_and_oral_06.07.26.md))
as three parallel tracks (technical hardening · oral formalization · release prep). It is the doc a wave-1
execution handoff points at.

## Audience
A fresh execution agent (Sonnet/Opus) running unattended, and MG for the human-gated forks (adjudication,
rights clearance, the final publish).

## Provenance
- Authored 22-07-2026 by Opus 4.8 (`claude-opus-4-8`) via the `/ask` skill.
- Interview: 5 rounds (goal · oral · publication · rights/tech · autonomy) — all rulings in the PLAN
  decisions table.
- Audit basis: three read-only recon passes (RussianTranslation TM state, SamudraManthanam corpus schema +
  oral material, cross-repo hub prior-art) + [`TRANSLATION_MEMORY_DECISIONS.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/TRANSLATION_MEMORY_DECISIONS.md)
  + [`ACL_TM_CROSSWALK_MEMO.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/ACL_TM_CROSSWALK_MEMO.md).
- ACL grounding partly via aclanthology.org web search (Vecalign/LaBSE, TM-as-baseline LREC-2022, LoResMT
  2025, SAHAAYAK/KanSan/MITRA Sanskrit corpora).

## Key decisions this plan rests on
Objective = technical-hardening-first; wave-1 = all three tracks parallel; quality bar = ACL-defensible
(COMET-QE + frozen gold + κ); oral = user-provides-transcripts, all-4-sources, all-3-granularities,
schema-extend SamudraManthanam; paper = fold TM into A42; rights = clearance-in-hand but hard human
GO/NO-GO, nothing auto-publishes; compute = external HF Inference API. Full table in the PLAN.

## Improvement backlog (ranked)
1. Once S1 resolves, pin the exact embedding + QE endpoints in ARCHITECTURE §Interfaces (currently a
   choose-first-that-serves list).
2. After A2, fold the measured COMET-QE ρ into FINDINGS (§70 currently says proxy-QE is near-useless).
3. When the first real transcript arrives, add its concrete format to the B2 converter contract.
4. If W2 engine-retrieval proceeds, split it into its own PLAN (kNN-MT is engine-side, out of this scope).

## Limitations
- The oral track's converter contract is specified against an expected transcript shape (raw RU + embedded
  Sanskrit + PDF); a materially different delivered format needs a converter-contract revision (backlog 3).
- COMET-QE transfer to Sa→Ru is unproven (a stated risk with a floor + a fallback).
- Release timing is coupled to A42's schedule (fold-in decision) and to per-source rights clearance (human).

## Revision history
- 22-07-2026 — created (Opus 4.8, `/ask`).

_Dr. Mārcis Gasūns_
