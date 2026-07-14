# Roadmap A — beyond the ceiling: what the PWG→RU dictionary cannot answer, and what we bolt on

_Created: 08-07-2026 · Last updated: 08-07-2026_

The dictionary answers "what senses exist and where are they cited" superbly; it does **not** answer "which sense is live in this passage" or "how did the sense change over time" without an external model or dated corpus bolted on. This roadmap turns each honest ceiling item into either a build (with the bolt-on named), a partial (with the proxy named), or an explicit stays-out-of-scope. All eight forks were ruled by MG on 08-07-2026 (decision log at the bottom). Sequencing ruling: **[H335](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H335-Fable_RussianTranslation_pipeline-capability-audit_08.07.26.md) audit first → cheap derivables in parallel with translation → model/benchmark phases after ~50% translation coverage.**

## The ceiling, item by item

| # | Ceiling item | Verdict | The bolt-on |
|---|---|---|---|
| C1 | **In-context WSD** — tagging a running-text token to one PWG sense | BUILD (phased) | Embedding baseline first (LaBSE-class similarity: token's DCS sentence context × sense glosses+citations; P@1 on ~200 hand-checkable tokens — the harness). Then a DharmaMitra probe scored on the **same** gold set. Gold = MG pass 1 + frozen documented model pass 2, κ via `/gold-adjudicate` (human recruiting stays parked for 2026). |
| C2 | **Chronology of senses** | PARTIAL → BUILD (two phases) | Phase 1 (cheap): join each sense's `<ls>` citations to [ls_source_map.json](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/ls_source_map.json)'s `date`/`period`/`renou` per work (45 works) → per-sense **attestation window**, honestly labeled "per Böhtlingk–Roth's citations", layered on the existing `pwg_sense_stratum.jsonl` Renou proxy (23,461 senses). Phase 2 (citable): curated per-work dating table with ranges + the scholarly source per date (Witzel, Olivelle, …); contested datings each get an `@DECIDE`. Never claim absolute sense-emergence. |
| C3 | **Frequency outside DCS** | STAYS PARTIAL | DCS is a sample; absence ≠ non-existence. Mitigations only: report DCS counts always WITH the corpus size and the genre skew; GRETIL ingestion ([H308](https://github.com/gasyoun/Uprava/blob/main/handoffs/H308-Sonnet_SamudraManthanam_gretil-tei-ingestion-scoping_07.07.26.md) track) widens the sample but never closes the inference gap. Zero counts are labeled `unattested-in-sample`, never `rare`. |
| C4 | **Modern etymology** | BUILD (rights unlocked) | **MG holds written permission from Mayrhofer for KEWA and EWA** (email; locate + quote its terms verbatim before publication-tier use — GTD @DO). KEWA headings index already OCRed: `SamudraManthanam/Index/lib/x86_64-win64/Data/KEWA.txt` (join gotcha: dhātus appear as finite forms, `bhavati`→`bhū` — see [LEARNER_APPARATUS_SPEC.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/LEARNER_APPARATUS_SPEC.md)). EWA to come later — document the crosswalk when it lands. PLUS the own cross-dictionary layer: reuse the Cologne etymology-extraction project (10-dict extractors, 90–100% tradition agreement) as the "what the 19th-c. tradition says" lane. Two lanes, labeled: *traditional* (Cologne dicts) vs *modern IE* (KEWA/EWA). |
| C5 | **Register/pragmatics** | STAYS PROXY | Genre stands in for register, no further. H335 W4's per-sense genre attribution is the ceiling of what's derivable; "coarse/poetic-only" claims are never emitted, only "attested only in kāvya" style statements. |
| C6 | **Consensus meaning where scholars disagree** | STAYS OUT | We publish one authoritative 19th-c. reading + the per-source evidence vector (H335 W2: Grintser/Kossovich/… supports/contradicts). The evidence vector *surfaces* disagreement; adjudicating the field's current verdict is scholarship, not pipeline. |
| C7 | **Unresolved citation residue** | MEASURE + SHRINK | ls_resolver's unmapped residue gets a standing census (count + top unmapped abbreviations) in the H335 W4 join; each mapped abbreviation shrinks it. Citation *correctness* (does the page really attest the sense) stays out — we point, we don't verify. |
| C8 | **Cross-lingual (Tib/Ch), post-1875 vocabulary** | PROBE (rights-gated) | DharmaMitra ([lexicon.dharmamitra.org](https://lexicon.dharmamitra.org)): `/license-gated-ingest` — what's downloadable, license quoted verbatim, composition parked `@DECIDE`, derived measurements only until ruled. Parallel `/outreach-draft` to the Berkeley team on formal data exchange (they're a prospective API partner per org memory). PWG stays a closed historical corpus; the bolt-on is federation, not extension. |

## Phasing (per the sequencing ruling)

- **Wave 0 (now):** H335 audit (its W2 evidence-vector and W4 genre specs are C6/C5/C7's foundation).
- **Wave 1 (parallel with translation, cheap derivables):** C2 phase 1 (dating join — deterministic), C4 KEWA normalization + join (deterministic), C8 license-gated probe + outreach draft.
- **Wave 2 (after ~50% translation coverage):** C1 embedding WSD baseline + gold set, C2 phase 2 (curated dating table), C1 DharmaMitra probe.
- Handoffs for Wave 1 items are minted after H335 lands (its specs set their schemas); each will carry its own starter line in the registry.

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
