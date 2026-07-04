# Translation Memory Decisions

_Created: 04-07-2026_

This file records settled user decisions for the PWG translation-memory approach.
Do not re-ask these as open planning questions unless the user explicitly reopens
the topic.

## Settled Decisions

1. **Auto-reuse policy for draft windows**

   Machine-gated exact reuse is acceptable for draft windows. Human-reviewed
   material remains the higher-trust tier, but draft production may auto-serve
   exact content-addressed TM hits that have passed the machine gates.

2. **Fuzzy translation memory**

   Fuzzy TM should suggest wording to the model. It must remain advisory prompt
   context and must not pre-resolve cards, remove cards from agent work lanes,
   or count as exact reuse.

3. **Optimization priority**

   The immediate priority is speed. When speed, print-grade consistency, and
   scholarly provenance conflict during draft-window engineering, prefer the
   fastest path that preserves the existing deterministic safety gates and keeps
   provenance sufficient for later review.

4. **MW English influence on Russian**

   MW English material should not influence RU translation directly. It may
   influence RU only through a curated Sanskrit-to-Russian terminology layer.

5. **Publication-grade TM schema**

   The translation memory is part of the scholarly publication apparatus, not
   only a draft-speed cache. Harden the TM schema now for eventual publication:
   explicit provenance, review state, source evidence, versioning, and
   reproducibility metadata outrank short-term implementation convenience.

6. **Interoperability priority**

   Digital-humanities and audit interoperability outrank CAT-tool
   interoperability. TMX export may be useful later, but the primary contract is
   a reviewable, citable, source-grounded TM record with enough metadata for
   independent audit and reuse.

7. **Fuzzy-match evidence channels**

   Fuzzy TM should compute and preserve separate scores for German source
   fragments, Sanskrit headwords, and normalized semantic tags. Do not collapse
   these into one opaque score; the model and reviewer should be able to see
   which evidence channel produced each suggestion.

8. **Human review precedence**

   Human-reviewed exact TM entries outrank machine exact entries automatically,
   even when the machine entry is newer. Recency may break ties within the same
   trust tier, but reviewed evidence is the higher-trust tier.

9. **MW-derived RU path**

   MW-derived English evidence may be used only in a hidden build step that
   produces curated Sanskrit-to-Russian terminology with attached provenance.
   The RU prompt must see the curated Sanskrit-to-Russian terminology decision,
   not raw MW English glosses.

10. **Publication-grade TM artifact timing**

    Make the publication-grade translation memory a tracked artifact now. Do
    not wait for higher human-review coverage before creating the reviewable
    scholarly artifact layer.

11. **Fuzzy scoring experiment**

    Test all three fuzzy evidence channels rather than choosing a single winner
    by assumption. The working hypothesis is that semantic-tag/register
    similarity should dominate for PWG, but German-fragment similarity and
    Sanskrit-headword similarity must be evaluated as separate arms.

12. **Fuzzy TM evaluation priority**

    Evaluate fuzzy TM by speed first. Reviewer acceptance and false-positive
    rates remain important follow-up metrics, but the immediate optimization
    target is draft throughput.

13. **Curated Sanskrit-to-Russian terminology publication**

    Curated Sanskrit-to-Russian terminology should be a separate dataset with
    its own DOI path, not merely a subsection of the PWG translation-memory
    apparatus.

14. **ACL Anthology monitoring**

    Create a recurring monthly ACL Anthology / NLP-for-DH monitoring workflow
    across the Sanskrit repos. Each pass should produce a small annotated
    bibliography and an "Actionable for us?" verdict per paper.

## Implementation Consequences

- Keep exact TM and fuzzy/suggestion TM separate.
- Keep machine-gated exact TM eligible for draft auto-serve, while preserving
  trust levels so reviewed exact entries can outrank machine exact entries.
- Route fuzzy candidates into generated prompts as evidence, not as completed
  output.
- Build any MW-derived RU benefit as curated terminology, with source/provenance
  attached to the Sanskrit-to-Russian term decision.
- Treat TM entries as publication-grade scholarly records: include source
  identifiers, source hashes, gate/review state, model/script versions,
  evidence-channel scores, and supersession links.
- Preserve separate fuzzy evidence channels for German-fragment similarity,
  Sanskrit-headword similarity, and semantic-tag similarity.
- Rank reusable exact entries by trust tier first (`reviewed_exact` above
  `machine_exact`), then by recency only inside a tier.
- Future fix plans should cite this file instead of asking these four questions
  again.

## Decision Record Entries

### D10. Track Publication-Grade TM Now

**Context.** The current exact-card and fragment TM sidecars are local,
gitignored speed caches in
[`translation_memory.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/translation_memory.py),
while this file already defines the TM as a future scholarly publication
apparatus. Waiting would keep the draft cache and publication contract drifting.

**Options considered.** Track the publication-grade artifact now, accepting
schema hardening and review-state churn earlier; or track only the schema and
datasheet until human-review coverage is higher, reducing artifact noise but
delaying audit discipline.

**Ruling.** 04-07-2026, decider MG: "yes, make the publication-grade TM a tracked
artifact now".

**Consequences.** Add a tracked publication artifact lane distinct from the
gitignored draft cache. Future TM work should harden export/validation around a
reviewable JSONL artifact instead of treating all TM files as disposable local
sidecars.

### D11. Test All Fuzzy Evidence Channels

**Context.** Fuzzy TM currently preserves separate scores for German source
fragments, Sanskrit headwords, and semantic tags/registers, matching the
decision above and the advisory-in-prompt implementation in
[`gen_opt_harness2.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/gen_opt_harness2.py).

**Options considered.** Prefer semantic-tag/register similarity immediately;
prefer German-fragment similarity; prefer Sanskrit-headword similarity; or run
all three arms and compare them empirically.

**Ruling.** 04-07-2026, decider MG: "can we test all 3? I lean for
semantic-tag/register similarity, but might turn out ot be wrong".

**Consequences.** Build fuzzy TM as an A/B/C experiment. Semantic-tag/register
similarity is the prior, not the fixed policy. Reports must preserve per-channel
metrics so a wrong prior can be overturned without schema change.

### D12. Evaluate Fuzzy TM For Speed First

**Context.** The current draft-window priority is throughput, and exact TM has
already been justified as a zero-token acceleration layer. Fuzzy TM may improve
quality, but its first value in the current phase is reducing draft time.

**Options considered.** Optimize first for speed; optimize first for reviewer
acceptance / false-positive rate; or require both before adopting fuzzy
suggestions in prompt context.

**Ruling.** 04-07-2026, decider MG: "evaluated by speed first".

**Consequences.** The first fuzzy-TM evaluation should report wall-clock,
agent-call, and token deltas before deeper reviewer-acceptance metrics.
False-positive and reviewer-acceptance tracking remains a follow-up gate before
publication-grade claims.

### D13. Separate DOI Path For Curated Sanskrit-To-Russian Terminology

**Context.** MW English must not enter RU prompts directly; its benefit must be
mediated through curated Sanskrit-to-Russian terminology. That terminology has
its own source mix, curation state, and reuse audience beyond PWG TM.

**Options considered.** Publish curated terminology as a subsection of the PWG
TM apparatus; or publish it as a separate dataset with its own DOI path and
cross-link it from TM records.

**Ruling.** 04-07-2026, decider MG: "curated Sanskrit-to-Russian terminology be
a separate dataset with its own DOI path".

**Consequences.** Create a separate terminology dataset/release plan. TM
suggestion rows should cite terminology record ids / source hashes rather than
embedding the terminology dataset as an undifferentiated subtable.

### D14. Monthly ACL Anthology Monitor

**Context.** ACL Anthology and NLP-for-DH venues regularly publish work directly
relevant to translation memory, retrieval-augmented translation, terminology
constraints, data statements, normalization, OCR, corpus alignment, and cultural
heritage NLP. The Sanskrit repos need a lightweight way to notice reusable
methods without rebuilding literature searches ad hoc.

**Options considered.** Do not monitor; do one manual literature review; or
create a recurring monthly monitor with a small annotated bibliography and an
"Actionable for us?" verdict per paper.

**Ruling.** 04-07-2026, decider MG: "yes".

**Consequences.** A monthly Codex automation now runs as
`monthly-acl-anthology-sanskrit-nlp-monitor`. Its output should append dated
sections to an appropriate monitor file, deduplicate prior entries, and route
new measured findings to the correct `FINDINGS.md` when warranted.
