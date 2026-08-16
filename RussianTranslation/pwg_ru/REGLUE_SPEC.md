# Content-aware re-glue spec

_Created: 06-07-2026 · Last updated: 16-08-2026_

**Deliverable 3 of
[H180](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H180-Opus_RussianTranslation_pwg_ru_addenda_typology_glue_learner_05.07.26.md)**
(canonical after-translation track). The five layers are today glued **mechanically**
(fixed order PWG → PW → SCH → PWKVN → NWS, no sense-aware placement). This spec designs
a **content-aware remix** that interleaves the *already-translated* sub-cards so each
supplement sits at its relevant PWG sense — proving the re-glue is **free** (zero
re-translation).

## 1. Canonical design ruling (MG 05-07-2026)

- The **layered, provenance-preserving store stays canonical.** Synthesis is a *derived
  presentation*, built after translation, never replacing the per-sub-card store.
- Sub-cards stay individually translated + auditable (free re-glue preserved).
- The remix step **never calls the translate workflow** — it consumes
  [`src/pwg_ru_translated.jsonl`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_ru_translated.jsonl)
  only. This is the proof that re-glue is free.

## 2. Inputs (all already on disk)

Per sub-card, keyed by `key1` + `subcard`:
- `layer` (H179 Step 1): `pwg` | `pw` | `sch` | `pwkvn` | `nws`.
- `sense_tag`: PWG sense number (`6`) or supplement tag (`NWS-1`, `anu_desid`, `ava_caus`).
- `provenance.relationship.insertion_point` (from
  [`ADDENDA_TYPOLOGY.md`](ADDENDA_TYPOLOGY.md) §2/§4): `{homonym, target_sense, anchor}`.
- `ru` (translated body) + `de` (source) + the markup (`{%…%}`, `<ls>`, `<lex>`).

## 3. Algorithm (deterministic + light LLM assist)

For each `key1`:

1. **Skeleton.** Take all `layer=pwg` sub-cards, ordered by homonym then `sense_tag`
   numeric — this is the frame. Everything else hangs off it (MG: "PWG remains the
   skeleton").
2. **Attach.** For each non-`pwg` sub-card, read `insertion_point.target_sense`:
   - a PWG sense number → splice **inside** that sense block as a marked supplement
     (`— [SCH] …`, `— [NWS] …`), carrying its layer badge + source citations.
   - `*new` → append as a new, badged sense at the end of the homonym, flagged *addition*.
   - `*whole` → attach at entry head (applies to the whole headword).
3. **Cancellations.** A `pw_cancel` / `pw_correct` instance (op=`delete`/`correct`)
   renders the PWG value **struck / annotated** in place (`PWG n. → PW m.`), never
   silently dropped — provenance is visible.
4. **Foreign fragments.** `foreign_fragment` sub-cards (NWS in FR/LA/**EN**) render the
   Russian translation as the body with the original-language source shown beneath
   (badge `‹fr›`/`‹la›`/`‹en›`).
5. **Deterministic first, LLM only for prose smoothing.** Steps 1–4 are pure data
   placement. An **optional** LLM pass only *smooths connective prose* between spliced
   blocks (never invents content, never re-translates) and is marked
   `reglue_smoothed: llm` so it is auditable and skippable.

Output per entry = a **print-oriented card**: PWG skeleton with SCH/NWS/PW/PWKVN
additions inline at their sense, cancellations struck/annotated, foreign-origin bits
shown with their RU translation.

## 4. Output artifact

`pwg_ru/reglue/<key1>.json` (+ a rendered `.md`/`.html` for eyeballing), schema:

```json
{"key1":"gA","homonyms":[
  {"h":"h0","senses":[
    {"sense":"1","pwg_ru":"…","supplements":[
      {"layer":"sch","subtype":"sch_star","ru":"…","source":"…","confidence":"llm"}]},
    {"sense":"*new","added_by":"nws","ru":"…","source":"Sūryas iv,26","lang":"en"}
  ]}]}
```

No field here requires a new translation — every `ru` is copied from the sub-card store.

## 5. Pilot (15 rich multi-layer headwords, zero re-translation)

Chosen from the translated set (measured 06-07-2026; the corpus is verb-root-first per
H179/H201, so the pilot is roots):

- **5 layers** (pwg+pw+sch+pwkvn+nws): `gA` (319 sub-cards), `Cid` (154 — includes the
  NWS English foreign-fragment case), `Sam` (172), `jIv` (78), `rakz` (67), `vraj`
  (128), `yat`.
- **4 layers**: `DA` (803 — the stress test), `Ap` (152), `Bid` (205), `Buj` (104),
  `banD` (137), `Sru` (80).
- **3 layers** (handoff-named family): `viS` (537, pwg+pw+pwkvn), `siD` (187).

`DA` (803 sub-cards) is the load/coherence stress case; `Cid` exercises the
foreign-fragment path; `gA` exercises all five layers at once.

**Success criteria:** (a) byte-identical `ru` bodies vs the sub-card store (proves zero
re-translation); (b) every supplement lands at a real PWG sense or a flagged `*new`;
(c) no cancellation silently dropped; (d) human spot-check of the 15 rendered cards on
an interactive HTML sheet.

Builder to write: `src/build_reglue.py` (consumes `pwg_ru_translated.jsonl` +
relationship sidecar; emits `pwg_ru/reglue/`). Depends on
[`ADDENDA_TYPOLOGY.md`](ADDENDA_TYPOLOGY.md)'s `build_relationships.py` having populated
`insertion_point`.

## 5a. Pilot run results (06-07-2026, Arm A — zero re-translation proven)

[`src/build_reglue.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_reglue.py)
built all **15/15** pilot headwords →
[`pwg_ru/reglue/`](https://github.com/gasyoun/SanskritLexicography/tree/master/RussianTranslation/pwg_ru/reglue)
(`<key1>.json` + rendered `.md` + [`PILOT_SUMMARY.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/reglue/PILOT_SUMMARY.tsv)).

**Success criteria met:**
- **(a) byte-identity** — every emitted `ru` (skeleton *and* supplement) is asserted
  present verbatim in the store; all 15 pass `byte_ok=True`. **Re-glue is free.**
- **(b) nothing lost** — every supplement lands at a real PWG sense (`placed`) or is
  flagged `*new`; none dropped.
- **(c) cancellations visible** — the 1 `DA` `pw_correct` renders annotated, not dropped.
- **(d) human spot-check** — deferred to an interactive HTML voting sheet (not checkboxes).

**Key finding — descendant sense-numbering diverges from PWG, so most supplements fall
to `*new` rather than `placed`** (e.g. `Sam` 0 placed / 130 new; `DA` 36 / 412). Two
causes, both measured:
1. **PW renumbers.** A PW sense `5` is *PW's own* numbering, **not** a pointer to PWG
   sense 5 — so naive leading-integer attachment misfires. True alignment needs *content*
   matching (gloss-to-sense), which is exactly the deferred gold pass, not a first-pass
   heuristic.
2. **The store is verb-root-first** — PWG senses live on *per-preverb* sub-cards each with
   their own `1,2,3…`, so a flat "sense N" key is ambiguous until more of PWG is
   translated.

The mechanism is proven and lossless; higher placement is a *content-alignment* task for
the gold pass, not a re-glue-engine fix. This divergence is itself evidence for the
Deliverable-5 paper ("how the tradition renumbered itself when it abridged").

## 6. Guardrails

- Never blocks the H179 run; consumes its output.
- **No re-translation** — assert byte-identity of every `ru` against the store in CI.
- The layered store remains canonical; `reglue/` is derived and regenerable.
- LLM smoothing is optional, marked, and content-neutral.

See [`SYNTHESIS_PILOT_10.md`](SYNTHESIS_PILOT_10.md) for the bake-off that tests whether
*synthesize-German-first* ever beats this after-translation remix.

## 7. N14 pilot — edition-diff reading surface (H1631, 26-07-2026, PARTIAL CLOSE)

A lighter-weight sibling of the full re-glue engine: a **read-only diff/badge view**
(not a print-oriented merged card) over the same `edition_rel` classification
(H1624 G4), for browsing rather than final presentation.
[`src/pilot/build_edition_diff_site.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/build_edition_diff_site.py)
renders the PWG skeleton with PW/SCH/PWKVN/NWS supplements attached at their
`insertion_point.target_sense`, each badged with its subtype — no DE rewrite, no
re-translation, no new typology. Pilot coverage: the same 7 five-layer roots as
Section 5 (`gA`, `Cid`, `Sam`, `jIv`, `rakz`, `vraj`, `yat`); counts in
[RESULTS_LOG.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/RESULTS_LOG.md)
26-07-2026. **Not yet done:** scaling past the 7-root pilot, per-sense visual
polish, and this view does not replace the Section 4/5 print-oriented re-glue
output — the two are complementary (diff/browse vs. merged/print).

## 8. The presentation layer — what a reviewer must SEE (H2827, 15-08-2026)

Sections 1–5 fix what the re-glue *is*; this section fixes what it *shows*. Three
defects of the v1 spot-check sheet, each with its ruling:

### 8.1 Citations are links, not prose

Every `<ls>` in a rendered card goes through
[`ls_links.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/ls_links.py),
a rendering layer over the repo's existing
[`ls_resolver.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/ls_resolver.py).
**83.6 %** of the store's 41,115 citations resolve to a Cologne scan/text target.
Never write a second resolver: Cologne's own precomputed csl-lslink table reaches
only 79.3 % and wins zero citations the resolver misses — full measurement in
[FINDINGS §536](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md).

The unresolved remainder is rendered as **two distinct marks**, because it is two
distinct things:

| mark | meaning | is it work? |
|---|---|---|
| ⚑ | a real locus no pattern covers | **yes** — the mintable gap |
| ∅ | a bare abbreviation (`GORR.`, `ed. Bomb.`) with no locus | **no** — nothing to point at, ever |

Collapsing them into one "unresolved" count overstates the backlog by about a
fifth. Per-card totals sit in a coverage strip above the card.

### 8.2 The glue typology is a first-class visual, keyed to ONE question

[`ADDENDA_TYPOLOGY.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/ADDENDA_TYPOLOGY.md)
already defines three axes and eight subtypes. For *reading a card* only one
question matters — **did this supplement add meaning, or not?** — so the eight
subtypes collapse to three colour-coded classes:

| class | subtypes | what the reader concludes |
|---|---|---|
| **＋ added meaning** (green) | `nws_at_sense` · `sch_star` · `derived_sense` · `foreign_fragment` · `a2a` | a later layer knows something PWG did not |
| **≈ restatement** (amber) | `restate` | PW says the same thing more briefly — **no new meaning** |
| **✕ cancels / corrects** (red) | `pw_correct` · `pw_cancels` | PWG's value is overridden; never silently dropped |

This is not decoration — it is the finding. Across the 15 pilot cards: **1,534
restatements vs 250 additions vs 1 correction**. Roughly **86 %** of everything
glued onto PWG is PW abridging what PWG already said. A reviewer who cannot see
that at a glance will read a card as far richer than it is.

**Ordering ruling (answers "are the glued-in entries ABOVE all old?"):** no. PWG
remains the skeleton (§1) and supplements are rendered *beneath* the PWG sense
they attach to, in layer order. A supplement is visually subordinate to the sense
it supplements; only a `*new` sense — one with no PWG sense to attach to — is
promoted to its own block at the end of the homonym. Position encodes attachment,
the chip encodes relationship; neither encodes precedence.

### 8.3 Gloss chains are split for reading, never in the store

NWS and SCH separate sense clusters with a **full stop** carried over verbatim
from the German (`gehen, kommen, wandern. weggehen.` → `идти, приходить,
странствовать. уходить.`). That is faithful to the source and unnatural in
Russian. The ruling: **split at render time, never in the store.** The card shows
numbered clusters; the raw store string stays one panel away, unchanged and
byte-identical (§6 guardrail intact).

The splitter is deliberately timid — it refuses to split inside a `{#…#}` Sanskrit
span, inside an unclosed bracket, after a known abbreviation (`нар.`, `т. е.`),
after a Russian clitic (`кому-л.`), or anywhere in a citation-bearing body, and it
falls back to plain rendering unless it finds ≥2 clusters. A missed split is
invisible; a wrong split silently rewrites a definition.

**Sheet:** [h180_reglue_v2.html](https://gasyoun.github.io/vote/sheets/h180_reglue_v2.html)
(generator
[`build_reglue_sheet_v2.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_reglue_sheet_v2.py)).
v1 stays published for comparison but is not the vote.

## 9. The vote had no evidence on it — and 90 % of it was unaskable (H2859, 16-08-2026)

§8 made the sheet legible. Asked for **more data in the voting**, the check found
the problem was not thin presentation but an unanswerable question.

### 9.1 The ≈ chip claims a relation to a sense that is not there

`restate` is assigned by **layer default** — `layer=pw` and no gender conflict —
*independently of whether an insertion target was found*. Measured over the
sidecar: **5,054 of 5,603 supplements (90.2 %) carry
`target_sense='*new'`**, the pipeline's own marker for "no PWG sense to attach
to", **and are still labelled `restate` ("PW abridging restatement")**. The chip
asserts a relationship to PWG while the insertion point simultaneously says there
is nothing to relate to. Asking a human "does this restatement sit at the right
PWG sense?" when the sidecar already says there is no such sense is not a
question, and no amount of extra display fixes it.

This is the same divergence §5a measured from the other side (PW renumbers, so
naive leading-integer attachment misfires) — but §5a read it as *placement falls
back to `*new`, nothing lost*. The label did not fall back with it.

### 9.2 What is actually checkable: 4.4 %

| bucket | supplements | share |
|---|---:|---:|
| no PWG target (`*new`) | 4,690 | 83.7 % |
| target exists, German too thin to compare | 303 | 5.4 % |
| **genuinely checkable** | **246** | **4.4 %** |

`nws/foreign_fragment` (62) and `pw/pw_correct` (1) have **zero** checkable pairs —
every one lands in `*new`. So the single `pw_correct`, the one cancellation the
whole corpus contains, cannot be verified against a PWG sense at all.

### 9.3 An evidence axis that was tried and rejected

Gloss-word overlap (Jaccard over German content words) was the obvious candidate
for making ≈-vs-＋ checkable. It does **not** discriminate — median 0.000 for both
classes — and the cause is the data, not the metric: a PWG sense body has a
**median of 3 content words** (39 chars) and 16 % have none, so two short German
synonym lists share no surface forms even when one restates the other. Kept in
[`reglue_overlap.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/reglue_overlap.py)
so the negative result stays reproducible, and deliberately **not** shown on a
card as a signal — a number that looks like evidence and isn't is worse than none.

Citation overlap survives as objective evidence and is displayed.

> A self-inflicted trap worth keeping: the first cut of that measurement stripped
> `{%…%}` along with `{#…#}`. `{#…#}` is Sanskrit; **`{%…%}` is the German meaning
> gloss** — the very text being compared. Deleting it drove 95 % of pairs to a
> spurious 0.000 that *looked* like a finding. Caught only by reading actual pairs
> instead of trusting the aggregate.

### 9.4 What the vote now is

[`build_reglue_evidence_sheet.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_reglue_evidence_sheet.py)
→ **one supplement per card**, 47 cards drawn only from the 246 checkable pairs,
stratified across every `(layer, subtype)` that has any. Each card carries the
**German original of both sides** (anatomy-coloured) — because the relation holds
between the sources, not between their translations — the Russian beneath it, and
the machine's full claim: subtype, op, direction, anchor, sidecar evidence string,
confidence, shared `<ls>` citations, and gloss-word counts. Reject reveals a
required reason (`wrong_place` / `wrong_label` / `both` / `not_a_supplement`).

The 90.2 % is reported in the footer as a finding, not put to a vote.

## 10. Two axes, not one: `placement` (H2879, 16-08-2026)

§9 diagnosed the defect; this is the fix. `subtype` was carrying two unrelated
claims at once — a property of the **layer** ("PW abridges PWG", true whether or
not anything was located) and a claim about the **pair** ("this supplement
restates *that* sense", true only when a target was actually found). They are now
separate fields, and `subtype` must be read together with `placement`.

| claim | field | true when |
|---|---|---|
| the PW layer abridges PWG | `direction: "abridging"` (pre-existing) | always; needs no target |
| this supplement relates to **that** sense | `placement: bool` (**new**) | only when the target is found in the PWG skeleton |
| what kind of relation it is | `subtype` (unchanged) | read **only together with** `placement` |

`subtype` is deliberately **not** renamed on unplaced rows: duplicating one fact
across two fields guarantees they drift apart.

### 10.1 `placement_reason` — three phenomena the old `*new` bucket merged

`placement=false` is not one thing. Measured over all 6,009 sidecar rows:

| `placement_reason` | rows | share | what it means |
|---|---:|---:|---|
| `found` | 595 | 9.9 % | target located in the PWG skeleton |
| `no_target_marker` | 4,901 | 81.6 % | the supplement's own tag has no leading number — no target exists *by construction*, not a lookup that failed |
| `out_of_range` | 383 | 6.4 % | the target number is above PWG's highest sense here — the later edition genuinely has more senses; **evidence about renumbering, not a data defect** |
| `not_found` | 130 | 2.2 % | inside the range, but no such sense — the only bucket that looks like a defect |

Separating `out_of_range` from `not_found` is the substantive gain: 383 rows that
read as broken links are in fact the renumbering phenomenon this project is
documenting, and only 130 rows are genuinely unexplained.

### 10.2 Tag normalisation — deliberately conservative

`normalize_sense_tag` strips trailing whitespace, `.`, `,` and an **unmatched**
trailing `)`, and nothing else, applied **symmetrically** to the PWG skeleton and
to the target. It does not merge `1-sub-…` (a sub-sense), `1 (PW)` (foreign
provenance), `Nachtrag` (an edit *to* a sense) or `caus-1` (another grammatical
branch) — each is pinned by a negative selftest. A false merge would produce a
silent `placement=true` on the wrong sense, which is worse than the defect being
repaired.

### 10.3 Measured effect — and what it is not

On an identical store and sidecar, switching the old raw-equality rule for the
`placement` flag:

| | old rule | new rule | delta |
|---|---:|---:|---:|
| checkable | 250 | **257** | +7 |
| no PWG target | 5,426 | 5,414 | −12 |
| too thin | 333 | 338 | +5 |

12 rows became placed; 7 of them have enough German to be compared. **This is a
correctness fix, not a coverage win** — the honest attribution is +7 checkable
pairs. The larger apparent jump from the previously published 246/4,690/303 is
mostly unrelated: that baseline was measured against a sidecar built 06-07-2026
while the store had moved on to 02-08-2026, so this pass also refreshed a stale
sidecar (5,603 → 6,009 rows). Wave 1's own effect is the +7.

`out_of_range` moved 381 → 383. VERIFICATION A4 expected it not to move at all;
the two extra rows are `vA h0` targets 8 and 9, in an article whose skeleton is
written `3)`–`7)` with no bare integer at all. Before normalisation that article
had no computable maximum, so both rows fell to `not_found`; they are genuinely
out of range and are now filed as such. The reclassification follows from S3's own
instruction to compute the maximum over normalised tags — A4's premise was
slightly wrong, not the implementation.

`placement_hypothesis` is implemented, guarded and selftested, but fires on **0**
real rows: no `not_found` row matched even under the looser key. The field earns
its place as the designed home for future named methods, not as a current result.

### 10.4 Acceptance is re-runnable

[`placement_axis_check.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/placement_axis_check.py)
proves A1–A5 and A9 against the artifacts on disk, including the two stop
conditions — that no row which had no target became placed (A3), and that the
canonical store is byte-identical (A5). Run it after any change to the classifier.

_Dr. Mārcis Gasūns_
