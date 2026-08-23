# Roadmap A — beyond the ceiling: what the PWG→RU dictionary cannot answer, and what we bolt on

_Created: 08-07-2026 · Last updated: 19-08-2026_

> **Truth-pass 19-08-2026** ([H3001 (Opus 5) — Stale-roadmap slice 3: full /ask replan of stale Tier-1 roadmaps](https://github.com/gasyoun/Uprava/blob/main/handoffs/H3001-Opus_multi_stale-roadmap-s3-tier1-ask-replan_17.08.26.md)).
> This roadmap said *"Handoffs for Wave 1 items are minted after H335 lands."*
> [H335](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H335-Fable_RussianTranslation_pipeline-capability-audit_08.07.26.md)
> closed ✅ on **08-07-2026** and no Wave 1 handoff was ever minted — a roadmap that
> delegates its own mint to a future moment has nothing watching for that moment.
> **Wave 0 is complete; Wave 1 is now minted** (see the phasing section). Residual
> programme:
> [docs/PLAN_SanskritLexicography_PWG_RU_CEILING_RESIDUAL_2026H2.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/PLAN_SanskritLexicography_PWG_RU_CEILING_RESIDUAL_2026H2.md).

The dictionary answers "what senses exist and where are they cited" superbly; it does **not** answer "which sense is live in this passage" or "how did the sense change over time" without an external model or dated corpus bolted on. This roadmap turns each honest ceiling item into either a build (with the bolt-on named), a partial (with the proxy named), or an explicit stays-out-of-scope. All eight forks were ruled by MG on 08-07-2026 (decision log at the bottom). Sequencing ruling: **[H335](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H335-Fable_RussianTranslation_pipeline-capability-audit_08.07.26.md) audit first → cheap derivables in parallel with translation → model/benchmark phases after ~50% translation coverage.**

## The ceiling, item by item

| # | Ceiling item | Verdict | The bolt-on |
|---|---|---|---|
| C1 | **In-context WSD** — tagging a running-text token to one PWG sense | BUILD (phased) | Embedding baseline first (LaBSE-class similarity: token's DCS sentence context × sense glosses+citations; P@1 on ~200 hand-checkable tokens — the harness). Then a DharmaMitra probe scored on the **same** gold set. Gold = MG pass 1 + frozen documented model pass 2, κ via `/gold-adjudicate` (human recruiting stays parked for 2026). |
| C2 | **Chronology of senses** | PHASE 1 BUILT → phase 2 open | Phase 1 (cheap) **shipped 23-08-2026 (H3168)**: per-sense attestation window in [pwg_sense_attestation_window.jsonl](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_sense_attestation_window.jsonl) + [C2P1_ATTESTATION_WINDOW.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/research/C2P1_ATTESTATION_WINDOW.md) — 43,990/53,003 numbered senses windowed over [ls_source_map.json](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/ls_source_map.json)'s 45 dated works, labeled "per Böhtlingk–Roth's citations", C7 residue carried (115,354 instances). Phase 2 (citable): curated per-work dating table with ranges + the scholarly source per date (Witzel, Olivelle, …); contested datings each get an `@DECIDE`. Never claim absolute sense-emergence. |
| C3 | **Frequency outside DCS** | STAYS PARTIAL | DCS is a sample; absence ≠ non-existence. Mitigations only: report DCS counts always WITH the corpus size and the genre skew; GRETIL ingestion ([H308](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H308-Sonnet_SamudraManthanam_gretil-tei-ingestion-scoping_07.07.26.md) track) widens the sample but never closes the inference gap. Zero counts are labeled `unattested-in-sample`, never `rare`. |
| C4 | **Modern etymology** | BUILD (rights unlocked) | **MG holds written permission from Mayrhofer for KEWA and EWA** (email; locate + quote its terms verbatim before publication-tier use — GTD @DO). KEWA headings index already OCRed: `SamudraManthanam/Index/lib/x86_64-win64/Data/KEWA.txt` (join gotcha: dhātus appear as finite forms, `bhavati`→`bhū` — see [LEARNER_APPARATUS_SPEC.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/LEARNER_APPARATUS_SPEC.md)). EWA to come later — document the crosswalk when it lands. PLUS the own cross-dictionary layer: reuse the Cologne etymology-extraction project (10-dict extractors, 90–100% tradition agreement) as the "what the 19th-c. tradition says" lane. Two lanes, labeled: *traditional* (Cologne dicts) vs *modern IE* (KEWA/EWA). |
| C5 | **Register/pragmatics** | STAYS PROXY | Genre stands in for register, no further. H335 W4's per-sense genre attribution is the ceiling of what's derivable; "coarse/poetic-only" claims are never emitted, only "attested only in kāvya" style statements. |
| C6 | **Consensus meaning where scholars disagree** | STAYS OUT | We publish one authoritative 19th-c. reading + the per-source evidence vector (H335 W2: Grintser/Kossovich/… supports/contradicts). The evidence vector *surfaces* disagreement; adjudicating the field's current verdict is scholarship, not pipeline. |
| C7 | **Unresolved citation residue** | MEASURE + SHRINK | ls_resolver's unmapped residue gets a standing census (count + top unmapped abbreviations) in the H335 W4 join; each mapped abbreviation shrinks it. Citation *correctness* (does the page really attest the sense) stays out — we point, we don't verify. |
| C8 | **Cross-lingual (Tib/Ch), post-1875 vocabulary** | PROBE (rights-gated) | DharmaMitra ([lexicon.dharmamitra.org](https://lexicon.dharmamitra.org)): `/license-gated-ingest` — what's downloadable, license quoted verbatim, composition parked `@DECIDE`, derived measurements only until ruled. Parallel `/outreach-draft` to the Berkeley team on formal data exchange (they're a prospective API partner per org memory). PWG stays a closed historical corpus; the bolt-on is federation, not extension. |

## Phasing (per the sequencing ruling)

- **Wave 0 — ✅ complete 08-07-2026.** The [H335](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H335-Fable_RussianTranslation_pipeline-capability-audit_08.07.26.md)
  audit closed; its W2 evidence-vector and W4 genre specs are C6/C5/C7's foundation.
- **Wave 1 (parallel with translation, cheap derivables) — 🟡 minted 19-08-2026:**

  | Item | Handoff |
  |---|---|
  | C2 phase 1 — dating join, deterministic | ✅ [H3168 — Ceiling C2 phase 1: per-sense attestation window](https://github.com/gasyoun/Uprava/blob/main/handoffs/H3168-OxAlpha_SanskritLexicography_ceiling-c2p1-sense-attestation-window_19.08.26.md) (shipped 23-08-2026) |
  | C4 — KEWA normalization + dhātu-aware join | [H3169 (Opus 5) — Ceiling C4: KEWA index normalization and join](https://github.com/gasyoun/Uprava/blob/main/handoffs/H3169-Opus_SanskritLexicography_ceiling-c4-kewa-normalize-join_19.08.26.md) |
  | C8 — license-gated probe + outreach draft | [H3170 (Sonnet 5) — Ceiling C8: DharmaMitra probe plus outreach draft](https://github.com/gasyoun/Uprava/blob/main/handoffs/H3170-Sonnet_SanskritLexicography_ceiling-c8-dharmamitra-probe-outreach_19.08.26.md) |

- **Wave 2 (after ~50% translation coverage):** C1 embedding WSD baseline, C2 phase 2 (curated dating table), C1 DharmaMitra probe. **Deliberately not minted** — minting coverage-gated work now would produce handoffs that sit blocked and rot. The **gold set** C1 needs is *not* coverage-gated and is minted separately as [H3172 (Opus 5) — Shared gold sets unblocking WSD and BLI](https://github.com/gasyoun/Uprava/blob/main/handoffs/H3172-Opus_SanskritLexicography_pwgru-shared-gold-wsd-bli_19.08.26.md): building the yardstick early is what makes the coverage checkpoint actionable when it arrives.
- **On mint timing (correction, 19-08-2026).** The original line here — *"handoffs for Wave 1 items are minted after H335 lands"* — is the defect this truth-pass found. A gate whose successor is only *promised* has no observer. Any future gate in this document names the observable that decides it, and queues its successor at the same time the gate is written.

## Decision log (MG rulings, 08-07-2026)

| Fork | Ruling |
|---|---|
| WSD approach | Both in sequence: embedding baseline first (becomes the eval harness), then DharmaMitra probe on the same gold set |
| DharmaMitra depth | License-gated ingest + outreach; not API-only, not skipped |
| Sense dating | BOTH: derive from existing maps now, curated scholarly table later (phased) |
| Etymology | Own cross-dict layer + KEWA/EWA under Mayrhofer's emailed permission (KEWA index on disk; EWA later; document) |
| Gold/κ under the no-second-annotator constraint | Model as annotator 2 (frozen, documented), `/gold-adjudicate` |
| Sequencing | Audit → quick wins → rest; model/benchmark phases wait for ~50% coverage |

_Dr. Mārcis Gasūns_
