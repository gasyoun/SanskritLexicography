_Created: 19-07-2026 · Last updated: 19-07-2026_

# Metadoc — PLAN_SanskritLexicography_PWG_DATA_LAYERS_2026H2

**Purpose.** Companion record for the `/ask`-grade layered plan that turns PWG card anatomy into a formally specified, machine-validated, queryable object and routes enrichment additively onto the German original (never into csl-orig source text).

**Audience.** The unattended execution agent running [H1350](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1350-Sonnet_SanskritLexicography_pwg-data-layers-anatomy-schema-extract_19.07.26.md); MG for the Wave-2 upstream gate; any future session extending the PWG data layers.

**Provenance.** Authored 19-07-2026 by Opus 4.8 (`claude-opus-4-8`) via `/ask` (4 interview rounds, 16 rulings). Execution handoff minted as H1350 for Sonnet 5 (`claude-sonnet-5`). Audit basis: three Explore sweeps over SanskritLexicography, Uprava hubs, and csl-atlas parse-rules (19-07-2026).

**The five docs.**
- Cover — [PLAN_SanskritLexicography_PWG_DATA_LAYERS_2026H2.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/PLAN_SanskritLexicography_PWG_DATA_LAYERS_2026H2.md)
- [ROADMAP](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/ROADMAP_SanskritLexicography_PWG_DATA_LAYERS_2026H2.md) · [ARCHITECTURE](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/ARCHITECTURE_SanskritLexicography_PWG_DATA_LAYERS.md) · [IMPLEMENTATION](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/IMPLEMENTATION_SanskritLexicography_PWG_DATA_LAYERS.md) · [VERIFICATION](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/VERIFICATION_SanskritLexicography_PWG_DATA_LAYERS.md)

**Ranked improvement backlog.**
1. When Wave-1 lands, add measured numbers (contamination %, citation coverage delta, failure-bucket counts) back into this plan's §4 and the ARCHITECTURE risk register.
2. If the RNG spike (S1) forces the fallback (sense structure in JSON only), record it here and in ARCHITECTURE §2.
3. Cross-link the shipped anatomy reference from [EntryAnatomy/README.md](https://github.com/gasyoun/SanskritLexicography/blob/master/EntryAnatomy/README.md) and csl-atlas's MICROSTRUCTURE docs so the three originals point up to the crosswalk.
4. Feed the citation-coverage work into papers A27 (serialization standard) and A33 (sense ordering); feed the `〉` contamination number into A52 (failure taxonomy).

**Limitations.**
- The plan is deterministic-first; the single LLM step (W1.5) is a sanity check, not a decision-maker. Sense-segmentation *disagreements* (Wave 2) need a stronger evidence bar than this run applies.
- Wave 3 (requeue contaminated cards) is deliberately out of scope — it needs a generation budget the autonomy contract can't guarantee.
- The "agent-gated" upstream preference was reconciled to "csl-corrections staging only, MG merges" — a narrower reading than the raw interview answer, chosen to respect the standing csl-orig read-only rule.

**Related docs.** [PWG_LAYER_COMBINATIONS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/PWG_LAYER_COMBINATIONS.md) · [PWG_PLUS_GERMAN_ENRICHMENT.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/PWG_PLUS_GERMAN_ENRICHMENT.md) · [LOD_GRAPH.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/LOD_GRAPH.md) · [FINDINGS §447 / §20 / §71 / §9](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md).

**Revision history.**
- 19-07-2026 — created alongside the PLAN (H1350 minted). Opus 4.8 (`claude-opus-4-8`).

_Dr. Mārcis Gasūns_
